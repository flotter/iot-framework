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

# Task C.1:
#
# Include the Raspberry Pi processor temperature in the MQTT health
# message sent to the dashboard.
#
# The JSON data payload is made up of key-value pairs in the form:
#
# "key" : value
#
# Make the key "bcm_temp" and the value utils.bcm_temp(). The temperature
# is provided by a helper function you will find in the payload directory
# under libs/utils.py. The temperature is of type string, so do NOT try
# to convert it to int().


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

# Task C.2:
#
# Take a look at the mqtt_send_panic() function above and
# make this function send an MQTT message to report that
# the door was opened.
#
# MQTT messages consist of a message "topic" string, and the
# message body. The topic has to be a very specific format to
# allow the server to route the message to the correct domain.
#
# Topic format: "iot/<customer-id>/<site-id>/<endpoint-serial>/<event>"
#
# Note: Make sure that you change the event type to be "door".
#
# Message Body: The body takes a JSON object with a single key-value
# pair. The key should be "state" and the value an integer value
# reflecting if the door is open (1) or closed (0).
#
# Use the function mqtt.publish(topic, body)


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

# Task B.1:
#
# Setup the remaining 4 GPIO pins as follows:

# BCM_BUZZER as output (GPIO.OUT)
# BCM_TRIG as output (GPIO.OUT)
# BCM_PANIC as input (GPIO.IN) with pull-down (GPIO.PUD_DOWN)
# BCM_DOOR as input (GPIO.IN) with pull-down (GPIO.PUD_DOWN)
# 
# Use the function GPIO.setup(pin, direction, option)


# Task B.2:
#
# Register a callback function, panic_callback(), for the
# panic pin (BCM_PANIC) on a rising edge (GPIO.RISING) event
# (pin goes from 0v to 3.3v)
#
# Use the function GPIO.add_event_detect(pin, edge, callback=<function>)
    

# Task B.3:
#
# Register a callback function, door_callback(), for the
# panic pin (BCM_DOOR) on a rising edge (GPIO.RISING) event
# (pin goes from 0v to 3.3v)
#
# Use the function GPIO.add_event_detect(pin, edge, callback=<function>)


################################################

# Make sure only one Flasher can use this function at a time
on_set_lock = Lock()

def on_set(state):
    """Set the On Green LED on or off."""

    if bool(state) == True:
        GPIO.output(BCM_ON, GPIO.HIGH)
    else:
        GPIO.output(BCM_ON, GPIO.LOW)

################################################

def panic_get():
    """Get panic state."""

# Task B.4:
#
# Read the state of the panic pin (BCM_PANIC).
#
# Use function GPIO.input(pin)


################################################

def door_get():
    """Get door state."""

# Task B.5:
#
# Read the state of the panic pin (BCM_DOOR).
#
# Use function GPIO.input(pin)


################################################

# Make sure only one Flasher can use this function at a time
buzzer_set_lock = Lock()

def buzzer_set(state):
    """Set the buzzer on or off."""

# Task B.6:
#
# Set the state of the buzzer pin (BCM_BUZZER).
# If state is True, set the pin to GPIO.HIGH, else
# if the state request is False, set the pin to
# GPIO.LOW.
#
# Use the function GPIO.output(pin, state)


################################################

# Make sure only one Flasher can use this function at a time
trigger_set_lock = Lock()

def trigger_set(state):
    """Set the Triggered Red LED on or off."""

# Task B.7:
#
# Set the state of the trigger pin (BCM_TRIG).
# If state is True, set the pin to GPIO.HIGH, else
# if the state request is False, set the pin to
# GPIO.LOW.
#
# Use the function GPIO.output(pin, state)


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

# Task A.1:
#
# The command below controls the Green LED on your
# external circuit. The value of delay controls how
# long the green LED stays in one state before
# switching.
#
# Change the flash rate to use a delay of 0.1 (5Hz), instead
# of the current value of 1 (0.5 Hz).

background.Flasher(on_set, on_set_lock, delay = 1)

# Setup the MQTT client
mqtt = mqtt_start()

# Health heartbeat
while True:

    mqtt_send_health()

    time.sleep(10)
