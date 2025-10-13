import sqlite3
import os
import cv2
import base64

# Path to your database folder containing images
database_folder = "dataset"

# Connect to SQLite database
conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

# Iterate over the folders in the database folder
for root, dirs, files in os.walk(database_folder):
    for name in dirs:
        # Get the path to the current directory
        directory_path = os.path.join(root, name)
        
        # Initialize variables to store image paths
        image_paths = []
        
        # Iterate over files in the current directory
        for filename in os.listdir(directory_path):
            # Get the path to the image file
            image_path = os.path.join(directory_path, filename)
            image_paths.append(image_path)
            
        # Ensure there are at least two images for each name
        if len(image_paths) >= 2:
            # Read the first two images
            image1 = cv2.imread(image_paths[0])
            image2 = cv2.imread(image_paths[1])
        
            # Encode images to base64
            encoded_image1 = cv2.imencode('.jpg', image1)[1].tobytes()
            encoded_image2 = cv2.imencode('.jpg', image2)[1].tobytes()
                
            # Insert data into the table
            c.execute("INSERT INTO liste_enseignants (name, image1, image2) VALUES (?, ?, ?)", (name, encoded_image1, encoded_image2))
            conn.commit()

# Close the database connection
conn.close()

print("Database created and populated successfully.")
