import time
import paho.mqtt.client as paho
import ssl
import json
import sh
import random

def cust():
    return sh.cat("/run/payload-runtime/cust.cfg").strip()
def site():
    return sh.cat("/run/payload-runtime/site.cfg").strip()
def serial():
    return sh.cat("/run/payload-runtime/serial.cfg").strip()
def reboots():
    return sh.cat("/home/iot/firmware-reboots.cfg").strip()
def settings_version():
    return sh.cat("/run/settings/version.cfg").strip()
def payload_version():
    return sh.cat("/home/iot/payload/version.cfg").strip()


def on_message(client, userdata, message):
  print("incoming: ",str(message.payload.decode("utf-8")))

def on_log(client, userdata, level, buf):
  print("log: ",buf)

def on_connect(client, userdata, flags, rc):
  print("Connection attempt ...")

client=paho.Client() 
client.on_message=on_message
client.on_log=on_log
client.on_connect=on_connect
print("connecting to broker")
client.tls_set("mqtt.crt")
client.tls_insecure_set(True)
client.connect("mqtt.iot-training.net", 8883, 60)

##start loop to process received messages
client.loop_start()

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
    client.publish(
        f"iot/{cust()}/{site()}/{serial()}/health",
        json.dumps(
            {
                "settings_version" : int(settings_version()),
                "payload_version" : int(payload_version()),
                "reboots" : int(reboots()),
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
            client.publish(
                f"iot/{cust()}/{site()}/{serial()}/{i+1}",
                json.dumps(
                    {
                        "state" : v["state"]
                    }
                )
            )

    time.sleep(10)
