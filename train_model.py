#! /usr/bin/python

import numpy as np
import face_recognition
import pickle
import cv2
import sqlite3
import base64

conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

c.execute("SELECT * FROM liste_enseignants")
data = c.fetchall()

# initialize the list of known encodings and known names
knownEncodings = []
knownNames = []

# loop over the fetched data
for i, row in enumerate(data):
    print("[INFO] processing row {}/{}".format(i + 1, len(data)))
    firstname = row[1]
    lastname = row[2]
    # Iterate over image columns starting from the third column
    for j in range(3, len(row)):
        image_data = row[j]

        # Convert image data to numpy array
        image_np = np.frombuffer(image_data, np.uint8)
        
        # Decode image
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        
        # Detect faces in the image
        boxes = face_recognition.face_locations(image, model="hog")

        # Compute encodings for each face detected
        encodings = face_recognition.face_encodings(image, boxes)

        # Add encodings and associated names to lists
        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(f"{firstname} {lastname}")


# close the database connection
conn.close()

# dump the facial encodings + names to disk
print("[INFO] serializing encodings...")
data = {"encodings": knownEncodings, "names": knownNames}
f = open("encodings.pickle", "wb")
f.write(pickle.dumps(data))
f.close()

