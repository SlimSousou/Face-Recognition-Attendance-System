import sqlite3
import RPi.GPIO as GPIO
import face_recognition
import numpy as np
import pickle
import time
import cv2
import os
import shutil
from picamera2 import Picamera2
from datetime import datetime
import base64
import sys
import signal 
import subprocess

conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

RELAY_PIN = 2
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

GPIO.output(RELAY_PIN, 1)
DELAY_BEFORE_LOCK = 5

encodingsP = "encodings.pickle"

print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read())

time.sleep(2.0)

camera = Picamera2()
camera.preview_configuration.main.size = (1280, 720)
camera.preview_configuration.main.format = "RGB888"
camera.preview_configuration.align()
camera.configure("preview")
camera.start()

while True:  # Check if video feed is active
    frame = camera.capture_array()
    boxes = face_recognition.face_locations(frame)
    encodings = face_recognition.face_encodings(frame, boxes)
    names = []

    for encoding in encodings:
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        name = "Unknown"
        counts = {}
        matchedIdxs = []

        if True in matches:
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                

            for i in matchedIdxs:
                full_name = data["names"][i]
                names_split = full_name.split()
                first_name = names_split[0]
                last_name = names_split[1]
                counts[full_name] = counts.get(full_name, 0) + 1

            name = max(counts, key=counts.get)

        names.append((name, counts.get(name, 0) / len(matchedIdxs) if matchedIdxs else 0))

    for ((top, right, bottom, left), (name, probability)) in zip(boxes, names):
        cv2.rectangle(frame, (left, top - 35), (right, top), (0, 102, 204), cv2.FILLED)           

        cv2.rectangle(frame, (left, top), (right, bottom), (102, 0, 0), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        name_with_probability = "{}: {:.2f}%".format(name, probability * 100)
        cv2.putText(frame, name_with_probability, (left, y), cv2.FONT_HERSHEY_SIMPLEX, .8, (102, 0, 0), 2)
            
        if name != "Unknown":
            GPIO.output(RELAY_PIN, 0)
            firstname, lastname = name.split()
            time.sleep(DELAY_BEFORE_LOCK)
            GPIO.output(RELAY_PIN, 1)
                
        else:
            GPIO.output(RELAY_PIN, 1)
            firstname = "Unknown"
            lastname = "Unknown"
            
        # Crop face region
        face_img = frame[top:bottom, left:right]
                
        # Save face image to database
        image = cv2.imencode('.jpg', face_img)[1].tobytes()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute("INSERT INTO enseignants (firstname, lastname, image, DateTime) VALUES (?, ?, ?, ?)", (firstname, lastname, image, current_time))
        conn.commit()
    
    cv2.imshow("Facial Recognition is Running", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

GPIO.cleanup()
cv2.destroyAllWindows()
camera.stop()


