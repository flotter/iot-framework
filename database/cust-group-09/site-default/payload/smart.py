# Smart Home controller
#

# Python imports
import time
import json
import random
import atexit

# Threading
from threading import Thread, Lock

# MQTT
import paho.mqtt.client as paho

# GPIO
import RPi.GPIO as GPIO

# Payload imports
from libs import utils

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
# Threading - Flasher
#################################################

class Flasher(Thread):
    """Flash something."""

    def __init__(self, state_function, lock, delay = 0.5, timeout = 0):
        """Initialize."""

        Thread.__init__(self)

        # The callback
        self.state_function = state_function
        # How long to wait on a state on/off
        self.delay = delay
        # How long to flash before we return
        self.timeout = timeout
        # Allow manual termination
        self.running = True
        # Make sure only one pin instance is flashed at a time
        self.lock = lock

        self.start()

    def run(self):
        """Do work."""

        if self.lock.acquire(blocking=False):

            state = True
            time_spent = 0
            while self.running and (time_spent <= self.timeout):
                # Set state
                self.state_function(state)
    
                # Toggle state
                if state:
                    state = False
                else:
                    state = True
    
                # Wait a bit
                time.sleep(self.delay)
    
                # Time is disabled if zero
                if self.timeout:
                    time_spent += self.delay

            # Release
            self.lock.release()

    def stop(self):
        """Stop the flasher."""

        self.running = False
        self.join()
        self.state_function(False)

#################################################
# Threading - MQTT Event
#################################################

class MQTTEvent(Thread):
    """Flash something."""

    def __init__(self, state_get, state_function, lock, delay = 1):
        """Initialize."""

        Thread.__init__(self)

	# Get current state
        self.state_get = state_get
        # The callback
        self.state_function = state_function
        # How long to raise the event
        self.delay = delay
        # Make sure only one event type at a time
        self.lock = lock

        self.start()

    def run(self):
        """Do work."""

        if self.lock.acquire(blocking=False):

            # Set state
            self.state_function(True)

            # Wait a bit
            time.sleep(self.delay)
       
            while self.state_get():
                # Set state
                self.state_function(True)

                # Wait a bit
                time.sleep(self.delay)

            # Set state
            self.state_function(True)
           
            # Set state
            self.state_function(False)
            
            # Release
            self.lock.release()
    

#################################################
# GPIO Support
#################################################

BCM_BUZZER = 5
BCM_ON     = 6
BCM_TRIG   = 13
BCM_PANIC  = 19
BCM_DOOR   = 26

def gpio_setup():
    """Configure the pins."""

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BCM_BUZZER , GPIO.OUT)
    GPIO.setup(BCM_ON , GPIO.OUT)
    GPIO.setup(BCM_TRIG , GPIO.OUT)
    GPIO.setup(BCM_PANIC , GPIO.IN, GPIO.PUD_DOWN)
    GPIO.setup(BCM_DOOR , GPIO.IN, GPIO.PUD_DOWN)
    
    # Panic always on
    GPIO.add_event_detect(BCM_PANIC, GPIO.RISING, callback=panic_callback)

def arm_inputs():
    """Enable the input callbacks."""

    GPIO.add_event_detect(BCM_DOOR, GPIO.RISING, callback=door_callback)


def disarm_inputs():
    """Disable the input callbacks."""

    GPIO.remove_event_detect(BCM_DOOR)

def panic_get():
    """Get panic state."""

    return bool(GPIO.input(BCM_PANIC))

panic_debounce = Lock()

def panic_callback(ch):
    """Handle the panic press."""

    # Enter if no callback is running already
    if panic_debounce.acquire(blocking=False):

        print("Panic pressed!")

        MQTTEvent(panic_get, mqtt_send_panic, mqtt_send_panic_lock)

        Flasher(buzzer_set, buzzer_set_lock, 1, 5)
        Flasher(trigger_set, trigger_set_lock, 1, 5)

        # Soft debounce
        time.sleep(2)

        # Release Lock
        panic_debounce.release()

def door_get():
    """Get door state."""

    return bool(GPIO.input(BCM_DOOR))

door_debounce = Lock()

def door_callback(ch):
    """Handle the door press."""

    # Enter if no callback is running already
    if door_debounce.acquire(blocking=False):

        print("Door opened!")
    
        MQTTEvent(door_get, mqtt_send_door, mqtt_send_door_lock)
        
        Flasher(buzzer_set, buzzer_set_lock, 1, 5)
        Flasher(trigger_set, trigger_set_lock, 1, 5)

        # Soft debounce
        time.sleep(2)

        # Release Lock
        door_debounce.release()

# Used by the Flasher
buzzer_set_lock = Lock()

def buzzer_set(state):
    """Set the buzzer on or off."""

    if bool(state) == True:
        GPIO.output(BCM_BUZZER, GPIO.HIGH)
    else:
        GPIO.output(BCM_BUZZER, GPIO.LOW)

# Used by the Flasher
trigger_set_lock = Lock()

def trigger_set(state):
    """Set the Triggered Red LED on or off."""

    if bool(state) == True:
        GPIO.output(BCM_TRIG, GPIO.HIGH)
    else:
        GPIO.output(BCM_TRIG, GPIO.LOW)

# Used by the Flasher
on_set_lock = Lock()

def on_set(state):
    """Set the On Green LED on or off."""

    if bool(state) == True:
        GPIO.output(BCM_ON, GPIO.HIGH)
    else:
        GPIO.output(BCM_ON, GPIO.LOW)


#################################################
# Cleanup
#################################################

def exit_handler():
    print("Exit handler called")
    GPIO.cleanup()

atexit.register(exit_handler)

#################################################
# Application Logic
#################################################

# Setup the pins
gpio_setup()

# System is On
on_set(True)

# Arm the inputs
arm_inputs()

# Setup the MQTT client
mqtt = mqtt_start()

# Health heartbeat
while True:

    mqtt_send_health()

    time.sleep(10)
