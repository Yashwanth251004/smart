from flask import Flask, render_template, Response, request, jsonify, redirect, url_for, session
import cv2
import numpy as np
import os
import xlwt
from xlwt import Workbook
from datetime import date, datetime
import xlrd, xlwt
from xlutils.copy import copy as xl_copy
import pickle
import re
import threading
import time
import json
from functools import wraps
import base64
import io
from PIL import Image

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'face_data')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize face recognition components
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()
face_data_file = os.path.join(app.config['UPLOAD_FOLDER'], 'face_data.json')

# Global variables for camera and attendance
camera = None
attendance_active = False
attendance_thread = None
capture_active = False
capture_thread = None
attendance_list = []
current_class = None
known_face_encodings = []
known_face_names = []
recent_activities = []

def initialize_camera():
    global camera
    if camera is None:
        try:
            camera = cv2.VideoCapture(0)
            if not camera.isOpened():
                raise Exception("Could not open camera")
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    return True

def load_known_faces():
    global known_face_encodings, known_face_names
    if os.path.exists(face_data_file):
        try:
            with open(face_data_file, 'r') as f:
                data = json.load(f)
                known_face_encodings = [np.array(encoding) for encoding in data['encodings']]
                known_face_names = data['names']
        except Exception as e:
            print(f"Error loading face data: {e}")
            known_face_encodings = []
            known_face_names = []
    return known_face_encodings, known_face_names

def save_face_data(encoding, name):
    global known_face_encodings, known_face_names
    try:
        known_face_encodings.append(encoding)
        known_face_names.append(name)
        
        data = {
            'encodings': [encoding.tolist() for encoding in known_face_encodings],
            'names': known_face_names
        }
        
        with open(face_data_file, 'w') as f:
            json.dump(data, f)
        return True
    except Exception as e:
        print(f"Error saving face data: {e}")
        return False

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_frames():
    global camera, attendance_active, capture_active, known_face_encodings, known_face_names
    
    while True:
        if not (attendance_active or capture_active):
            time.sleep(0.1)
            continue
            
        success, frame = camera.read()
        if not success:
            break
            
        # Process frame for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            face_roi = gray[y:y+h, x:x+w]
            
            try:
                label, confidence = recognizer.predict(face_roi)
                known_faces, known_names = load_known_faces()
                name = known_names[label] if confidence < 100 else "Unknown"
                
                if attendance_active and current_class:
                    # Check if the recognized person is in the selected class
                    class_students = class_manager.get_class_students(current_class)
                    student_in_class = any(student['name'] == name for student in class_students)
                    
                    if student_in_class and name not in attendance_list:
                        attendance_list.append(name)
                
                cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            except Exception as e:
                print(f"Error recognizing face: {e}")
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def attendance_worker():
    global attendance_active, attendance_list, current_class
    
    try:
        # Load known faces and train recognizer
        known_faces, known_names = load_known_faces()
        
        if not known_faces:
            print("No faces registered in the system. Please add faces first.")
            attendance_active = False
            return
        
        # Initialize Excel workbook for attendance
        attendance_file = f'attendance_{current_class}_{date.today()}.xls'
        try:
            wb = Workbook()
            sheet = wb.add_sheet('Attendance')
            sheet.write(0, 0, 'USN')
            sheet.write(0, 1, 'Name')
            sheet.write(0, 2, 'Time')
            sheet.write(0, 3, 'Status')
            wb.save(attendance_file)
        except Exception as e:
            print(f"Error creating attendance file: {e}")
            attendance_active = False
            return
        
        print(f"\nTaking attendance for class: {current_class}")
        
        # Dictionary to store attendance
        attendance_taken = {}
        
        while attendance_active:
            time.sleep(1)  # Check every second
            
            # Process attendance for new students
            for name in attendance_list:
                if name not in attendance_taken:
                    attendance_taken[name] = True
                    # Save attendance
                    try:
                        rb = xlrd.open_workbook(attendance_file)
                        wb = xl_copy(rb)
                        sheet = wb.get_sheet(0)
                        
                        # Get the next empty row
                        row = 1
                        while True:
                            try:
                                if sheet.cell_value(row, 0) == '':
                                    break
                                row += 1
                            except:
                                break
                        
                        # Find student's USN
                        class_students = class_manager.get_class_students(current_class)
                        student_usn = next(student['usn'] for student in class_students if student['name'] == name)
                        
                        # Add attendance record
                        sheet.write(row, 0, student_usn)
                        sheet.write(row, 1, name)
                        sheet.write(row, 2, datetime.now().strftime('%H:%M:%S'))
                        sheet.write(row, 3, 'Present')
                        wb.save(attendance_file)
                        
                        print(f"Marked attendance for {name}")
                    except Exception as e:
                        print(f"Error saving attendance: {e}")
    
    except Exception as e:
        print(f"An error occurred during attendance: {e}")
    finally:
        attendance_active = False

def capture_worker(usn, name, class_name):
    global capture_active
    
    try:
        face_samples = []
        sample_count = 0
        max_samples = 20
        
        while capture_active and sample_count < max_samples:
            success, frame = camera.read()
            if not success:
                break
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                face_samples.append(gray[y:y+h, x:x+w])
                sample_count += 1
                print(f"Sample {sample_count}/{max_samples} captured")
                
                if sample_count >= max_samples:
                    break
            
            time.sleep(0.1)  # Small delay to avoid overwhelming the camera
        
        if face_samples:
            # Load existing faces and names
            known_faces, known_names = load_known_faces()
            
            # Add new face samples
            for face in face_samples:
                known_faces.append(face)
                known_names.append(name)
            
            # Save updated face data
            save_face_data(known_faces, known_names)
            
            # Add student to class
            if class_manager.add_student_to_class(class_name, usn, name):
                print(f"Successfully added {name} (USN: {usn}) to class {class_name}")
                return True
            else:
                print("Failed to add student to class")
                return False
        else:
            print("No face samples captured")
            return False
    
    except Exception as e:
        print(f"An error occurred during face capture: {e}")
        return False
    finally:
        capture_active = False

@app.route('/')
@login_required
def index():
    classes = class_manager.get_all_classes()
    return render_template('index.html', username=session['username'], classes=classes,
                         is_attendance_active=attendance_active,
                         is_capture_active=capture_active,
                         recent_activities=recent_activities)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple authentication - replace with proper authentication
        if username == 'admin' and password == 'admin':
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/video_feed')
@login_required
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_attendance', methods=['POST'])
@login_required
def start_attendance():
    global camera, attendance_active, attendance_thread, attendance_list, current_class
    
    if attendance_active:
        return jsonify({'error': 'Attendance is already active'})
    
    class_name = request.form.get('class')
    if not class_name:
        return jsonify({'error': 'Please select a class'})
    
    # Initialize camera if not already done
    if camera is None:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            return jsonify({'error': 'Could not open camera'})
    
    # Reset attendance list and set current class
    attendance_list = []
    current_class = class_name
    
    # Start attendance thread
    attendance_active = True
    attendance_thread = threading.Thread(target=attendance_worker)
    attendance_thread.daemon = True
    attendance_thread.start()
    
    return jsonify({'message': f'Started attendance for class {class_name}'})

@app.route('/stop_attendance', methods=['POST'])
@login_required
def stop_attendance():
    global attendance_active
    
    if not attendance_active:
        return jsonify({'error': 'Attendance is not active'})
    
    attendance_active = False
    return jsonify({'message': 'Attendance stopped'})

@app.route('/start_capture', methods=['POST'])
@login_required
def start_capture():
    global camera, capture_active, capture_thread
    
    if capture_active:
        return jsonify({'error': 'Capture is already active'})
    
    usn = request.form.get('usn')
    name = request.form.get('name')
    class_name = request.form.get('class')
    
    if not all([usn, name, class_name]):
        return jsonify({'error': 'Missing required information'})
    
    # Validate USN format
    usn_pattern = re.compile(r'^[A-Z][0-9]{2}[A-Z]{2}[0-9]{2}[A-Z][0-9]{4}$')
    if not usn_pattern.match(usn):
        return jsonify({'error': 'Invalid USN format. Please use format: A12BC23D1234'})
    
    # Initialize camera if not already done
    if camera is None:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            return jsonify({'error': 'Could not open camera'})
    
    # Start capture thread
    capture_active = True
    capture_thread = threading.Thread(target=capture_worker, args=(usn, name, class_name))
    capture_thread.daemon = True
    capture_thread.start()
    
    return jsonify({'message': 'Started face capture'})

@app.route('/stop_capture', methods=['POST'])
@login_required
def stop_capture():
    global capture_active
    
    if not capture_active:
        return jsonify({'error': 'Capture is not active'})
    
    capture_active = False
    return jsonify({'success': True})

@app.route('/get_attendance')
def get_attendance():
    return jsonify(attendance_list)

@app.route('/add_class', methods=['POST'])
def add_class():
    class_name = request.form.get('class')
    if not class_name:
        return jsonify({'error': 'Please enter a class name'})
    
    if class_manager.add_new_class(class_name):
        return jsonify({'message': f'Class {class_name} added successfully'})
    else:
        return jsonify({'error': 'Failed to add class'})

@app.route('/add_subject', methods=['POST'])
def add_subject():
    # This is now replaced by add_class
    return jsonify({'error': 'This endpoint is deprecated. Use add_class instead.'})

def add_activity(student_name, action):
    global recent_activities
    activity = {
        'student_name': student_name,
        'action': action,
        'time': datetime.now().strftime('%H:%M:%S')
    }
    recent_activities.insert(0, activity)
    if len(recent_activities) > 10:  # Keep only last 10 activities
        recent_activities.pop()

if __name__ == '__main__':
    load_known_faces()
    app.run(debug=True, host='0.0.0.0', port=5000) 