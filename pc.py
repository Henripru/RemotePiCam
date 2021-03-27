import paho.mqtt.client as mqtt
from PIL import Image
import time
import cv2 as cv

# Constants
BROKER = 'iot.cs.calvin.edu'
PORT = 1883
QOS = 0
USERNAME = 'cs326' # broker username (if required)
PASSWORD = 'piot' # broker password (if required)
MAIN_TOPIC = 'RPC' # topic to publish under

# Callback when a connection has been established with the MQTT broker
def on_connect(client, userdata, rc, *extra_params):
    print('Connected with result code={}'.format(rc))

# Callback when client receives a message from the broker
# Use button message to turn LED on/off
def on_message(client, data, msg):
    if msg.topic == "RPC/image":
        # Create a file with write byte permission
        f = open('image.jpg', "wb")
        f.write(msg.payload)
        print("Image Received")
        f.close()
        original_image = cv.imread('image.jpg')
        grayscale_image = cv.cvtColor(original_image, cv.COLOR_BGR2GRAY)
        face_cascade = cv.CascadeClassifier(cv.data.haarcascades + "haarcascade_frontalface_default.xml")
        detected_faces = face_cascade.detectMultiScale(grayscale_image)
        if len(detected_faces) > 0:
            face_to_track = detected_faces[0]
            x = face_to_track[0] + face_to_track[2]/2
            y = face_to_track[1] + face_to_track[3]/2
            client.publish("RPC/position", str(x) + ',' + str(y), qos = QOS)

# Setup MQTT client and callbacks
client = mqtt.Client()
client.username_pw_set(USERNAME, password=PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker and subscribe to the button topic
client.connect(BROKER, PORT, 60)
client.subscribe("RPC/image", qos=QOS)

try:
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()
    print("Done")