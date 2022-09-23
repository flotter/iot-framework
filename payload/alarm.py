import time
import paho.mqtt.client as paho
import ssl
import json
import sh

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


#define callbacks
def on_message(client, userdata, message):
  print("received message =",str(message.payload.decode("utf-8")))

def on_log(client, userdata, level, buf):
  print("log: ",buf)

def on_connect(client, userdata, flags, rc):
  print("publishing ")


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


while True:
    print("Sending next message ...")
    client.publish(f"iot/{cust()}/{site()}/{serial()}",json.dumps(
        {
            "settings_version" : int(settings_version()),
            "payload_version" : int(payload_version()),
            "reboots" : int(reboots())
        }
    ))
    time.sleep(5)
