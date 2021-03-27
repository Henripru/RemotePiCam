import paho.mqtt.client as mqtt
from PIL import Image
import cv2 as cv
import math  # for tan and atan

# Constants
BROKER = 'iot.cs.calvin.edu'
PORT = 1883
QOS = 0
USERNAME = 'cs326' # broker username (if required)
PASSWORD = 'piot' # broker password (if required)
MAIN_TOPIC = 'RPC' # topic to publish under                                              Not used
CAM_X = 1600   # pixels for x axis in images received
CAM_Y = 900    # pixels for y axis in images received

# Callback when a connection has been established with the MQTT broker
def on_connect(client, userdata, rc, *extra_params):
    print('Connected with result code={}'.format(rc))

# Callback when client receives a message from the broker
# Use button message to turn LED on/off
def on_message(client, data, msg):
    if msg.topic == "RPC/face":
        detected_faces = msg.payload.decode()
        # payload is string of x, y, width, length with ',' between each
        face_to_track = detected_faces.split(',')
        print("Tracking x,y,w,l:", face_to_track)
        # Extract the first x and y values
        x = int(face_to_track[0]) + int(face_to_track[2])/2
        y = int(face_to_track[1]) + int(face_to_track[3])/2
        # Must act like center of image is (0,0) instead of corner
        x -= CAM_X/2
        y -= CAM_Y/2
        print("x:", x, "y:", y)
        # Convert the x and y values to an angle
        delta_theta_x = math.atan(x * 2*math.tan(27*math.pi/180)/CAM_X) * (180/math.pi) # convert to degrees at the end
        delta_theta_y = math.atan(y * 2*math.tan(20.5*math.pi/180)/CAM_Y) * (180/math.pi) # convert to degrees at the end

        # publish x and y angles to RPC/position as a string with ',' between each element
        client.publish("RPC/position", str(-delta_theta_x) + ',' + str(-delta_theta_y), qos = QOS)

# Setup MQTT client and callbacks
client = mqtt.Client()
client.username_pw_set(USERNAME, password=PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker and subscribe to the button topic
client.connect(BROKER, PORT, 60)
client.subscribe("RPC/face", qos=QOS)

try:
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()
    print("Done")