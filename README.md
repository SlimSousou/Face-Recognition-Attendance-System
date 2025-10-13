# Face Recognition for Teacher Management

This project is a Flask-based web application for managing, recognizing, and tracking teachers using a SQLite database and a modern user interface.

## Features

- **Admin Authentication**: Secure registration and login.
- **Dashboard**: Overview of detections and registered teachers.
- **Add Teachers**: Manual addition or via requests with image management.
- **Real-Time Face Recognition**: Display of recent detections.
- **Model Update**: Retrain the recognition model via a Python script.
- **Request Management**: Validate or delete teacher addition requests.
- **Deletion**: Delete individual or all detections and teachers.
- **Image Management**: Store images as BLOBs in SQLite, display via base64.


- **facial_rec.py**: Main Flask server, routes, and business logic.
- **train_model.py**: Script for training the recognition model.
- **picam.py**: Video capture for real-time recognition.
- **static/**: Static files (CSS, JS, images).
- **templates/**: HTML templates for the user interface.

## Installation

1. **Clone the repository**  
   ```sh
   git clone <repo_url>
   cd face-recognition
   ```

2. **Install dependencies**  
   ```sh
   pip install flask humanize
   ```

3. **Create the database**  
   Run the `dataset_SQLite.py` script to initialize the database and required tables.

4. **Start the application**  
   ```sh
   python facial_rec.py
   ```
   Go to [http://localhost:5000](http://localhost:5000) in your browser.

## Usage

- **Login**: Go to `/` to log in as an administrator.
- **Dashboard**: View detections and teachers.
- **Add/Validate**: Add teachers or validate requests via dedicated forms.
- **Real-Time Recognition**: Go to `/realtime_recognition`.
- **Model Update**: Click "Update Model" in the dashboard.

## Useful Scripts

- `run_scripts.sh`: Shell script to automate required scripts for our project to be executed each time the Raspberry Pi starts.
- `train_model.py`: (Re)trains the face recognition model.

## Notes

- Images are stored as BLOBs in the SQLite database.
- The project requires Python 3.x.
- For use on Raspberry Pi, adapt paths and dependencies as needed for your environment.