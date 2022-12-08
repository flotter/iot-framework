# Smart Home controller
#

# Python imports
import time
import json
import random
import atexit

from threading import Lock

# MQTT sending and receiving
import paho.mqtt.client as paho

# GPIO access
import RPi.GPIO as GPIO

# Utils give us access to platform metrics
# such as temperature, customer and site.
from libs import utils

# Background provides the Flasher and Event
# helper classes that help us do things in the
# background.
from libs import background

#################################################
# MQTT Support
#################################################

def on_log(client, userdata, level, buf):
    """Print debug information."""

    print("MQTT Debug Log: ",buf)

def on_connect(client, userdata, flags, rc):
    """Subscribe to messages intended for this endpoint only."""

    print("MQTT Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(f"cmd/{utils.cust()}/{utils.site()}/{utils.serial()}/+")

def on_message(client, userdata, message):
    """Print incoming MQTT message."""

    print("MQTT Incoming:")
    print(str(message.topic.decode("utf-8")))
    print(str(message.payload.decode("utf-8")))

def mqtt_start():
    """Start the MQTT connection and listener."""

    client=paho.Client() 
    client.on_message=on_message
    client.on_log=on_log
    client.on_connect=on_connect
    client.tls_set("mqtt.crt")
    client.tls_insecure_set(True)
    client.connect("mqtt.iot-training.net", 8883, 60)

    # Start the MQTT event handler
    client.loop_start()

    return client
    
def mqtt_send_health():
    """Send health."""

    mqtt.publish(
        f"iot/{utils.cust()}/{utils.site()}/{utils.serial()}/health",
        json.dumps(
            {
                "settings_version" : int(utils.settings_version()),
                "payload_version"  : int(utils.payload_version()),
                "reboots"          : int(utils.reboots()),
                "bcm_temp"         : utils.bcm_temp(),
            }
        )
    )

# The lock makes sure we only send one panic at a time
mqtt_send_panic_lock = Lock()

def mqtt_send_panic(state):
    """Send panic."""

    mqtt.publish(
        f"iot/{utils.cust()}/{utils.site()}/{utils.serial()}/panic",
        json.dumps(
            {
                "state" : int(state),
            }
        )
    )

# The lock makes sure we only send one panic at a time
mqtt_send_door_lock = Lock()

def mqtt_send_door(state):
    """Send door state."""

    mqtt.publish(
        f"iot/{utils.cust()}/{utils.site()}/{utils.serial()}/door",
        json.dumps(
            {
                "state" : int(state),
            }
        )
    )


#################################################
# GPIO Support
#################################################

BCM_BUZZER = 5    # GPIO 05
BCM_ON     = 6    # GPIO 06
BCM_TRIG   = 13   # GPIO 13
BCM_PANIC  = 19   # GPIO 19
BCM_DOOR   = 26   # GPIO 26

################################################

def gpio_setup():
    """Configure the pins."""

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BCM_ON , GPIO.OUT)

    GPIO.setup(BCM_BUZZER , GPIO.OUT)
    GPIO.setup(BCM_TRIG , GPIO.OUT)
    GPIO.setup(BCM_PANIC , GPIO.IN, GPIO.PUD_DOWN)
    GPIO.setup(BCM_DOOR , GPIO.IN, GPIO.PUD_DOWN)
    
    # Call the function panic_callback if the panic pin goes to 3.3v
    GPIO.add_event_detect(BCM_PANIC, GPIO.RISING, callback=panic_callback)
    
    # Call the function door_callback if the door pin goes to 3.3v
    GPIO.add_event_detect(BCM_DOOR, GPIO.RISING, callback=door_callback)

################################################

def panic_get():
    """Get panic state."""

    return bool(GPIO.input(BCM_PANIC))

################################################

panic_debounce = Lock()

def panic_callback(ch):
    """Handle the panic press."""

    # Enter if no callback is running already
    if panic_debounce.acquire(blocking=False):

        print("Panic pressed!")

        # While the panic button is pressed, send one MQTT message every 1 second
        background.Event(panic_get, mqtt_send_panic, mqtt_send_panic_lock)

        # Make the buzzer go off for 5 seconds
        background.Flasher(buzzer_set, buzzer_set_lock, delay = 1, timeout = 5)
        
        # Make the trigger LED go off for 5 seconds
        background.Flasher(trigger_set, trigger_set_lock, delay = 1, timeout = 5)

        # Soft debounce
        time.sleep(2)

        # Release Lock
        panic_debounce.release()

################################################

def door_get():
    """Get door state."""

    return bool(GPIO.input(BCM_DOOR))

################################################

door_debounce = Lock()

def door_callback(ch):
    """Handle the door press."""

    # Enter if no callback is running already
    if door_debounce.acquire(blocking=False):

        print("Door opened!")

        # While the door is open, send one MQTT message every 1 second
        background.Event(door_get, mqtt_send_door, mqtt_send_door_lock)
        
        # Make the buzzer go off for 5 seconds
        background.Flasher(buzzer_set, buzzer_set_lock, delay = 1, timeout = 5)

        # Make the trigger LED go off for 5 seconds
        background.Flasher(trigger_set, trigger_set_lock, delay = 1, timeout = 5)

        # Soft debounce
        time.sleep(2)

        # Release Lock
        door_debounce.release()


################################################

# Make sure only one Flasher can use this function at a time
buzzer_set_lock = Lock()

def buzzer_set(state):
    """Set the buzzer on or off."""

    if bool(state) == True:
        GPIO.output(BCM_BUZZER, GPIO.HIGH)
    else:
        GPIO.output(BCM_BUZZER, GPIO.LOW)


################################################

# Make sure only one Flasher can use this function at a time
trigger_set_lock = Lock()

def trigger_set(state):
    """Set the Triggered Red LED on or off."""

    if bool(state) == True:
        GPIO.output(BCM_TRIG, GPIO.HIGH)
    else:
        GPIO.output(BCM_TRIG, GPIO.LOW)


################################################

# Make sure only one Flasher can use this function at a time
on_set_lock = Lock()

def on_set(state):
    """Set the On Green LED on or off."""

    if bool(state) == True:
        GPIO.output(BCM_ON, GPIO.HIGH)
    else:
        GPIO.output(BCM_ON, GPIO.LOW)

#################################################
# Application Logic
#################################################

# Setup the pins
gpio_setup()

# If the application exits, make sure we release
# the pins, otherwise we will get a warning.
def exit_handler():
    print("Exit handler called")
    GPIO.cleanup()

atexit.register(exit_handler)

# Start flasher
background.Flasher(on_set, on_set_lock, delay = 1)

# Setup the MQTT client
mqtt = mqtt_start()

# Health heartbeat
while True:

    mqtt_send_health()

    time.sleep(10)
