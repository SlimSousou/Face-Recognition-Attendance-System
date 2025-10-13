from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
from datetime import datetime
import humanize
import base64 
import subprocess

app = Flask(__name__)
app.secret_key = 'recognition'

conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

# Path to your database folder containing images
database_folder = "dataset"

@app.route('/delete_row/<int:row_id>', methods=['DELETE'])
def delete_row(row_id):
    
    c.execute("DELETE FROM liste_enseignants WHERE id = ?", (row_id,))
    conn.commit()
    return jsonify({'message': 'Row deleted successfully'})


@app.route('/liste_enseignants', methods=['POST', 'GET'] )
def liste_enseignants():
    
    if request.method == "POST":
        
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        images = request.files.getlist('images[]')
        print(images)
        
        c.execute("INSERT INTO liste_enseignants (firstname, lastname, image1, image2) VALUES (?, ?, ?, ?)", (firstName, lastName, images[0].read(), images[1].read()))
        conn.commit()
            
        # Retrieve unique names and their BLOB data
        c.execute("SELECT * FROM liste_enseignants")
        data = c.fetchall()

        # Initialize lists to store data
        ids = []
        firstnames = []
        lastnames = []
        images1 = []
        images2 = []

        for row in data:
            ids.append(row[0])
            firstnames.append(row[1])
            lastnames.append(row[2])
            images1.append(base64.b64encode(row[3]).decode('utf-8'))
            images2.append(base64.b64encode(row[4]).decode('utf-8'))

        rows = zip(ids, firstnames, lastnames, images1, images2)

        # Pass the unique names and their BLOB images to the template
        return render_template('liste_enseignants.html', rows=rows)
    else:
        
        # Retrieve unique names and their BLOB data
        c.execute("SELECT * FROM liste_enseignants")
        data = c.fetchall()

        # Initialize lists to store data
        ids = []
        firstnames = []
        lastnames = []
        images1 = []
        images2 = []

        for row in data:
            ids.append(row[0])
            firstnames.append(row[1])
            lastnames.append(row[2])
            images1.append(base64.b64encode(row[3]).decode('utf-8'))
            images2.append(base64.b64encode(row[4]).decode('utf-8'))

        rows = zip(ids, firstnames, lastnames, images1, images2)

        # Pass the unique names and their BLOB images to the template
        return render_template('liste_enseignants.html', rows=rows)
    
@app.route('/list_requests', methods= ['POST', 'GET'])
def list_requests():
    if request.method == 'POST':
        # Extract data from the request
        data = request.json
        firstName = data['firstName']
        lastName = data['lastName']
        image1 = base64.b64decode(data['image1'].split(",")[1])
        image2 = base64.b64decode(data['image2'].split(",")[1])

        # Insert data into database
        c.execute("INSERT INTO liste_enseignants (firstname, lastname, image1, image2) VALUES (?, ?, ?, ?)",
                       (firstName, lastName, image1, image2))
        conn.commit()
        return jsonify({'message': 'Entry approved and added to database'})
    
    else:
        c.execute("SELECT * FROM requests")
        data = c.fetchall()

        # Initialize lists to store data
        ids = []
        firstnames = []
        lastnames = []
        images1 = []
        images2 = []

        for row in data:
            ids.append(row[0])
            firstnames.append(row[1])
            lastnames.append(row[2])
            images1.append(base64.b64encode(row[3]).decode('utf-8'))
            images2.append(base64.b64encode(row[4]).decode('utf-8'))

        rows = zip(ids, firstnames, lastnames, images1, images2)
        return render_template('list_requests.html', rows=rows)
    
@app.route('/delete_recognition/<int:row_id>', methods=['DELETE'])
def delete_recognition(row_id):
    
    c.execute("DELETE FROM enseignants WHERE id = ?", (row_id,))
    conn.commit()
    return jsonify({'message': 'Row deleted successfully'})

@app.route('/delete_request/<int:row_id>', methods=['DELETE'])
def delete_request(row_id):
    
    c.execute("DELETE FROM requests WHERE id = ?", (row_id,))
    conn.commit()
    return jsonify({'message': 'Request deleted successfully'})
    

@app.route('/', methods=['GET','POST'] )
def sign_in():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        c.execute("SELECT * FROM administrateurs WHERE email = ? AND password = ?", (email, password))
        admin = c.fetchone()
        
        if admin:
            # Store user data in session for authentication
            session['admin_id'] = admin[0]
            session['admin_name'] = admin[1]
            # Redirect to dashboard or another page
            return jsonify({'redirect_url': url_for('dashboard')})
        else:
            return jsonify({'message': 'Invalid user'})
    
    else:
        return render_template('sign-in.html')

# Route for dashboard page
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        image = request.files['profile_image']
        print(image)
        image_data = image.read()
        admin_id = session['admin_id']
        
        # Update the profile image in the database
        c.execute("UPDATE administrateurs SET profile_image = ? WHERE id = ?", (image_data, admin_id))
        conn.commit()
        return redirect(url_for('dashboard'))
    
    else:
        c.execute("SELECT COUNT(*) FROM enseignants")
        detections_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM liste_enseignants")
        professors_count = c.fetchone()[0]
        
        # Retrieve data from the SQLite database
        c.execute("SELECT ID, firstname, lastname, DateTime FROM enseignants ORDER BY DateTime DESC ")
        data = c.fetchall()

        # Initialize lists to store data
        ids = []
        firstnames = []
        lastnames = []
        datetimes = []
        for row in data:
            ids.append(row[0])
            firstnames.append(row[1])
            lastnames.append(row[2])
            datetimes.append(row[3])
        datetimes = [datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S') for dt_str in datetimes]
        elapsed_times = [humanize.naturaltime(datetime.now() - dt) for dt in datetimes]

        rows = zip(ids, firstnames, lastnames, elapsed_times)
        
        c.execute("SELECT ID, firstname, lastname, DateTime FROM requests ORDER BY DateTime DESC ")
        data1 = c.fetchall()

        # Initialize lists to store data
        ids1 = []
        firstnames1 = []
        lastnames1 = []
        datetimes1 = []
        for row in data1:
            ids1.append(row[0])
            firstnames1.append(row[1])
            lastnames1.append(row[2])
            datetimes1.append(row[3])
        datetimes1 = [datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S') for dt_str in datetimes1]
        elapsed_times1 = [humanize.naturaltime(datetime.now() - dt) for dt in datetimes1]

        rows1 = zip(ids1, firstnames1, lastnames1, elapsed_times1)
        
        # Retrieve user information including profile image from the database
        admin_id = session['admin_id']
        c.execute("SELECT name, profile_image FROM administrateurs WHERE id = ?", (admin_id,))
        admin_info = c.fetchone()
        if admin_info:
            admin_name = admin_info[0]
            # Convert the image data to a base64 string for displaying in HTML
            profile_image = admin_info[1]
            if profile_image:
                profile_image = base64.b64encode(profile_image).decode('utf-8')
            else:
                # Provide a default image if profile image not set
                profile_image = None
            return render_template('dashboard.html', admin_name=admin_name,
                profile_image=profile_image, rows=rows, rows1=rows1, detections_count=detections_count,
                professors_count=professors_count)

    
# Route to sign out
@app.route('/signout')
def signout():
    # Clear session data
    session.clear()
    return redirect(url_for('sign_in'))


@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        c.execute("INSERT INTO administrateurs (name, email, password) VALUES (?, ?, ?)" , (name, email, password) )
        conn.commit()
        
        return redirect(url_for('sign_in'))  # Redirect to the sign-in page
    
    else:
        return render_template('sign-up.html')

@app.route('/realtime_recognition')
def realtime_recognition():
    
    # Retrieve data from the SQLite database
    c.execute("SELECT * FROM enseignants ORDER BY DateTime DESC ")
    data = c.fetchall()

    # Initialize lists to store data
    ids = []
    firstnames = []
    lastnames = []
    images = []
    datetimes = []

    for row in data:
        ids.append(row[0])
        firstnames.append(row[1])
        lastnames.append(row[2])
        images.append(base64.b64encode(row[3]).decode('utf-8'))
        datetimes.append(row[4])

    rows = zip(ids, firstnames, lastnames, images, datetimes)

    return render_template('realtime_recognition.html', rows=rows)

@app.route('/delete_detections', methods=['POST'])
def delete_detections():
    c.execute("DELETE FROM enseignants")
    conn.commit()
    return jsonify({'message': 'deleted all detections successfully'})


@app.route('/update_model', methods=['GET'])
def update_model():
    try:
        # Execute the train_model.py script using subprocess
        subprocess.run(['python', 'train_model.py'])
        # Reboot picam.py script
        subprocess.run(['pkill', '-f', 'picam.py'])  # Kill existing picam.py instances
        subprocess.Popen(['python3', '/home/pi/Desktop/face-recognition/picam.py'])
          
        return jsonify({'success': True, 'message': 'Model updated successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
