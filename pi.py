# CS326 MQTT Lab
import os
import paho.mqtt.client as mqtt
from picamera import PiCamera
import time

# Constants
BROKER = 'iot.cs.calvin.edu' # CS MQTT broker
PORT = 1883
QOS = 0
USERNAME = 'cs326' # broker username (if required)
PASSWORD = 'piot' # broker password (if required)
MAIN_TOPIC = 'RPC'

# MQTT connection callback
def on_connect(client, userdata, flags, rc):
    if rc==0:
        print('Connected to',BROKER)
    else:
        print('Connection to {} failed. Return code={}'.format(BROKER,rc))
        os._exit(1)


# Setup MQTT client and callbacks
client = mqtt.Client()
client.username_pw_set(USERNAME,password=PASSWORD) # remove for anonymous access
client.on_connect=on_connect
client.connect(BROKER, PORT, 60)

# Connect to camera
camera = PiCamera()

# Main Loop
try:
    camera.start_preview()
    while True:
        client.loop(timeout=5.0)
        camera.capture('image.jpg')
        time.sleep(5)
        f = open("image.jpg", "rb")
        fileContent = f.read()
        byteArr = bytearray(fileContent)
        client.publish("RPC/image", byteArr, qos=QOS)
except KeyboardInterrupt:
    client.disconnect()
    camera.stop_preview()
    print("Done")