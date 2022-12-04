# Smart Home controller
#

# Python imports
import time
import json
import random

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

#################################################
# GPIO Support
#################################################



#################################################
# Application Logic
#################################################

mqtt = mqtt_start()

channels = [
     {
         "state": 0,
         "prev" : 0
     },
     {
         "state": 0,
         "prev" : 0
     },
]

print("Hello!")

while True:
    mqtt.publish(
        f"iot/{utils.cust()}/{utils.site()}/{utils.serial()}/health",
        json.dumps(
            {
                "settings_version" : int(utils.settings_version()),
                "payload_version" : int(utils.payload_version()),
                "reboots" : int(utils.reboots()),
            }
        )
    )

    for i, v in enumerate(channels):
        if v["state"] != 0:
            # Reset of one iteration
            v["state"] = 0
        else:
            # Randomize the trigger
            v["state"] = random.choice([0, 1])

        if v["state"] != v["prev"]:
            v["prev"] = v["state"]
            mqtt.publish(
                f"iot/{utils.cust()}/{utils.site()}/{utils.serial()}/{i+1}",
                json.dumps(
                    {
                        "state" : v["state"]
                    }
                )
            )

    time.sleep(10)
