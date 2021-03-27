# CS326 MQTT Lab
import os
import paho.mqtt.client as mqtt
from picamera import PiCamera
import time
import pigpio
import cv2 as cv

# Constants
BROKER = 'iot.cs.calvin.edu' # CS MQTT broker
PORT = 1883
QOS = 0
USERNAME = 'cs326' # broker username (if required)
PASSWORD = 'piot' # broker password (if required)
MAIN_TOPIC = 'RPC'
SERVOX = 12
SERVOY = 13

pi = pigpio.pi()
if not pi.connected:
    exit(0)

pi.set_PWM_frequency(SERVOX, 50)
pi.set_PWM_frequency(SERVOY, 50)

current_angle_x = 0
current_angle_y = 0

pi.set_servo_pulsewidth(SERVOX, (400/72)*(current_angle_x) + 1500)
pi.set_servo_pulsewidth(SERVOY, (400/72)*(current_angle_y) + 1500)

# ... receive delta x and y

def set_x(current_angle_x, delta_x):
    if current_angle_x + delta_x > 80:
        current_angle_x = 80
    elif current_angle_x + delta_x < -80:
        current_angle_x = -80
    else:
        current_angle_x += delta_x
    pi.set_servo_pulsewidth(SERVOX, int((400/72)*(current_angle_x) + 1500))
    return current_angle_x

def set_y(current_angle_y, delta_y):
    if current_angle_y + delta_y > 80:
        current_angle_y = 80
    elif current_angle_y + delta_y < -80:
        current_angle_y = -80
    else:
        current_angle_y += delta_y
    pi.set_servo_pulsewidth(SERVOY, int((400/72)*(current_angle_y) + 1500))
    return current_angle_y

# MQTT connection callback
def on_connect(client, userdata, flags, rc):
    if rc==0:
        print('Connected to',BROKER)
    else:
        print('Connection to {} failed. Return code={}'.format(BROKER,rc))
        os._exit(1)

def on_message(client, data, msg):
    global current_angle_x
    global current_angle_y
    if msg.topic == "RPC/position":
        stringtuple = msg.payload.decode().split(',')
        current_angle_x = set_x(current_angle_x, float(stringtuple[0]))
        current_angle_y = set_y(current_angle_y, float(stringtuple[1]))
        print(current_angle_x, ',', current_angle_y)

# Setup MQTT client and callbacks
client = mqtt.Client()
client.username_pw_set(USERNAME,password=PASSWORD) # remove for anonymous access
client.on_connect=on_connect
client.on_message=on_message
client.connect(BROKER, PORT, 60)
client.subscribe("RPC/position", qos = QOS)

# Connect to camera
camera = PiCamera()


# Main Loop
try:
    camera.start_preview()
    while True:
        client.loop(timeout=1.0)
        camera.capture('image.jpg')
        time.sleep(1)   
        original_image = cv.imread('image.jpg')
        grayscale_image = cv.cvtColor(original_image, cv.COLOR_BGR2GRAY)
        face_cascade = cv.CascadeClassifier(cv.data.haarcascades + "haarcascade_frontalface_default.xml")
        detected_faces = face_cascade.detectMultiScale(grayscale_image)
        
        if len(detected_faces) > 0:
            payload = str(detected_faces[0][0]) + ',' + str(detected_faces[0][1]) + ',' + str(detected_faces[0][2]) + ',' + str(detected_faces[0][3])
            print(payload)
            client.publish("RPC/face", payload, qos=QOS)

except KeyboardInterrupt:
    client.disconnect()
    print("Done")
