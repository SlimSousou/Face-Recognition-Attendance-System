from flask import Flask, render_template, jsonify, request
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'recognition'

conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()


@app.route('/', methods=['POST', 'GET'] )
def form():
    if request.method == "POST":
        
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        images = request.files.getlist('images[]')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        c.execute("INSERT INTO requests (firstname, lastname, image1, image2, DateTime) VALUES (?, ?, ?, ?, ?)",
                  (firstName, lastName, images[0].read(), images[1].read(), current_time))
        conn.commit()
        return render_template('formulaire.html')
    
    else:
        return render_template('formulaire.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001)