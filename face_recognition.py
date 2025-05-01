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

script_dir = os.path.dirname(os.path.abspath(__file__))
image = os.path.join(script_dir, 'rahul.png')
image2 = os.path.join(script_dir, 'sneha.png')

# Initialize face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize face recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()

# File to store face data
face_data_file = os.path.join(script_dir, 'face_data.pkl')

# Excel file for registered faces
registered_faces_file = 'registered_faces.xls'

class ClassManager:
    def __init__(self):
        self.classes_file = 'class_details.xls'
        self.ensure_class_file_exists()
    
    def ensure_class_file_exists(self):
        try:
            if not os.path.exists(self.classes_file):
                wb = Workbook()
                sheet = wb.add_sheet('Classes')
                sheet.write(0, 0, 'Class Name')
                sheet.write(0, 1, 'Total Students')
                sheet.write(0, 2, 'Created Date')
                wb.save(self.classes_file)
                print(f"Created new class details file: {self.classes_file}")
        except Exception as e:
            print(f"Error creating class file: {e}")
            return False
        return True
    
    def add_new_class(self, class_name):
        try:
            rb = xlrd.open_workbook(self.classes_file)
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
            
            # Add the new class
            sheet.write(row, 0, class_name)
            sheet.write(row, 1, 0)  # Initial total students
            sheet.write(row, 2, str(date.today()))
            wb.save(self.classes_file)
            
            # Create class-specific Excel file for students
            class_students_file = f'students_{class_name}.xls'
            wb = Workbook()
            sheet = wb.add_sheet('Students')
            sheet.write(0, 0, 'USN')
            sheet.write(0, 1, 'Name')
            sheet.write(0, 2, 'Registration Date')
            wb.save(class_students_file)
            
            print(f"Added new class: {class_name}")
            return True
        except Exception as e:
            print(f"Error adding new class: {e}")
            return False
    
    def get_all_classes(self):
        try:
            rb = xlrd.open_workbook(self.classes_file)
            sheet = rb.sheet_by_index(0)
            classes = []
            for row in range(1, sheet.nrows):
                if sheet.cell_value(row, 0):
                    classes.append(sheet.cell_value(row, 0))
            return classes
        except Exception as e:
            print(f"Error getting classes: {e}")
            return []
    
    def add_student_to_class(self, class_name, usn, name):
        try:
            class_students_file = f'students_{class_name}.xls'
            if not os.path.exists(class_students_file):
                print(f"Class file not found: {class_students_file}")
                return False
            
            rb = xlrd.open_workbook(class_students_file)
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
            
            # Add the student
            sheet.write(row, 0, usn)
            sheet.write(row, 1, name)
            sheet.write(row, 2, str(date.today()))
            wb.save(class_students_file)
            
            # Update total students count in class details
            self.update_total_students(class_name)
            
            print(f"Added student {name} to class {class_name}")
            return True
        except Exception as e:
            print(f"Error adding student to class: {e}")
            return False
    
    def update_total_students(self, class_name):
        try:
            # Update in class details file
            rb = xlrd.open_workbook(self.classes_file)
            wb = xl_copy(rb)
            sheet = wb.get_sheet(0)
            
            # Find the class row
            for row in range(1, sheet.nrows):
                if sheet.cell_value(row, 0) == class_name:
                    # Count students in class file
                    class_students_file = f'students_{class_name}.xls'
                    if os.path.exists(class_students_file):
                        student_rb = xlrd.open_workbook(class_students_file)
                        student_sheet = student_rb.sheet_by_index(0)
                        total_students = student_sheet.nrows - 1  # Subtract header row
                        sheet.write(row, 1, total_students)
                        wb.save(self.classes_file)
                    break
        except Exception as e:
            print(f"Error updating total students: {e}")
    
    def get_class_students(self, class_name):
        try:
            class_students_file = f'students_{class_name}.xls'
            if not os.path.exists(class_students_file):
                return []
            
            rb = xlrd.open_workbook(class_students_file)
            sheet = rb.sheet_by_index(0)
            students = []
            for row in range(1, sheet.nrows):
                if sheet.cell_value(row, 0):
                    students.append({
                        'usn': sheet.cell_value(row, 0),
                        'name': sheet.cell_value(row, 1)
                    })
            return students
        except Exception as e:
            print(f"Error getting class students: {e}")
            return []

# Initialize class manager
class_manager = ClassManager()

def ensure_excel_file_exists():
    try:
        if not os.path.exists(registered_faces_file):
            wb = Workbook()
            sheet = wb.add_sheet('Registered Faces')
            sheet.write(0, 0, 'Name')
            sheet.write(0, 1, 'Registration Date')
            sheet.write(0, 2, 'Registration Time')
            wb.save(registered_faces_file)
            print(f"Created new Excel file: {registered_faces_file}")
    except Exception as e:
        print(f"Error creating Excel file: {e}")
        return False
    return True

def add_to_registered_faces(name):
    if not ensure_excel_file_exists():
        return False
        
    try:
        rb = xlrd.open_workbook(registered_faces_file)
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
        
        # Add the new face
        sheet.write(row, 0, name)
        sheet.write(row, 1, str(date.today()))
        sheet.write(row, 2, datetime.now().strftime('%H:%M:%S'))
        wb.save(registered_faces_file)
        print(f"Added {name} to registered faces database")
        return True
    except Exception as e:
        print(f"Error adding to registered faces: {e}")
        return False

# Load known faces
def load_known_faces():
    known_faces = []
    known_names = []
    
    # Check if we have saved face data
    if os.path.exists(face_data_file):
        try:
            with open(face_data_file, 'rb') as f:
                saved_data = pickle.load(f)
                known_faces = saved_data['faces']
                known_names = saved_data['names']
                print(f"Loaded {len(known_names)} faces from saved data")
        except Exception as e:
            print(f"Error loading saved face data: {e}")
    
    # If no saved data or empty, load from image files
    if not known_faces:
        # Load first person
        if os.path.exists(image):
            img1 = cv2.imread(image)
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            faces1 = face_cascade.detectMultiScale(gray1, 1.3, 5)
            for (x, y, w, h) in faces1:
                known_faces.append(gray1[y:y+h, x:x+w])
                known_names.append("Rahul")
        
        # Load second person
        if os.path.exists(image2):
            img2 = cv2.imread(image2)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            faces2 = face_cascade.detectMultiScale(gray2, 1.3, 5)
            for (x, y, w, h) in faces2:
                known_faces.append(gray2[y:y+h, x:x+w])
                known_names.append("sneha")
    
    # Train recognizer if we have faces
    if known_faces:
        labels = np.arange(len(known_faces))
        recognizer.train(known_faces, labels)
    else:
        print("No faces found to train the recognizer")
    
    return known_faces, known_names

# Save face data
def save_face_data(faces, names):
    try:
        with open(face_data_file, 'wb') as f:
            pickle.dump({'faces': faces, 'names': names}, f)
        print(f"Saved {len(names)} faces to {face_data_file}")
    except Exception as e:
        print(f"Error saving face data: {e}")

# Add a new face
def add_new_face(name=None, face_samples=None):
    if name is None:
        name = input("Enter the name of the person: ")
    
    # Get USN
    usn = input("Enter the USN of the person: ")
    # Validate USN format
    usn_pattern = re.compile(r'^[A-Z][0-9]{2}[A-Z]{2}[0-9]{2}[A-Z][0-9]{4}$')
    if not usn_pattern.match(usn):
        print("Invalid USN format. Please use format: A12BC23D1234 (1 alphabet + 2 digits + 2 alphabets + 2 digits + 1 alphabet + 4 digits)")
        return False
    
    # Get class selection
    classes = class_manager.get_all_classes()
    if not classes:
        print("No classes found. Please add a class first.")
        return False
    
    print("\nAvailable Classes:")
    for i, class_name in enumerate(classes, 1):
        print(f"{i}. {class_name}")
    
    try:
        choice = int(input("\nSelect class number: "))
        if choice < 1 or choice > len(classes):
            print("Invalid class selection")
            return False
        class_name = classes[choice - 1]
    except ValueError:
        print("Invalid input")
        return False
    
    if face_samples is None:
        # Initialize camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera")
            return False
        
        face_samples = []
        sample_count = 0
        max_samples = 20
        
        print(f"Capturing {max_samples} samples of {name}'s face. Please look at the camera.")
        
        while sample_count < max_samples:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                face_samples.append(gray[y:y+h, x:x+w])
                sample_count += 1
                print(f"Sample {sample_count}/{max_samples} captured")
            
            cv2.imshow('Adding New Face', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
    
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

# Main menu
def main_menu():
    while True:
        print("\n===== Smart Attendance System =====")
        print("1. Take Attendance")
        print("2. Add New Face")
        print("3. Add New Class")
        print("4. View Class Details")
        print("5. Exit")
        try:
            choice = input("Enter your choice (1-5): ")
            
            if choice == '1':
                take_attendance()
            elif choice == '2':
                add_new_face()
            elif choice == '3':
                class_name = input("Enter the class name (e.g., CS-A, CS-B): ")
                if class_manager.add_new_class(class_name):
                    print(f"Class {class_name} added successfully")
                else:
                    print("Failed to add class")
            elif choice == '4':
                view_class_details()
            elif choice == '5':
                print("Exiting program")
                break
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please try again.")

def view_class_details():
    classes = class_manager.get_all_classes()
    if not classes:
        print("No classes found. Please add a class first.")
        return
    
    print("\n===== Class Details =====")
    for class_name in classes:
        students = class_manager.get_class_students(class_name)
        print(f"\nClass: {class_name}")
        print(f"Total Students: {len(students)}")
        print("Students:")
        for student in students:
            print(f"  - {student['name']} ({student['usn']})")

# Take attendance
def take_attendance():
    try:
        # Load known faces and train recognizer
        known_faces, known_names = load_known_faces()
        
        if not known_faces:
            print("No faces registered in the system. Please add faces first.")
            return
        
        # Get available classes
        classes = class_manager.get_all_classes()
        if not classes:
            print("No classes found. Please add a class first.")
            return
        
        print("\nAvailable Classes:")
        for i, class_name in enumerate(classes, 1):
            print(f"{i}. {class_name}")
        
        try:
            choice = int(input("\nSelect class number: "))
            if choice < 1 or choice > len(classes):
                print("Invalid class selection")
                return
            class_name = classes[choice - 1]
        except ValueError:
            print("Invalid input")
            return
        
        # Try multiple camera indices to find an available webcam
        video_capture = None
        for idx in range(3):
            temp_cap = cv2.VideoCapture(idx)
            if temp_cap.isOpened():
                print(f"Using camera index {idx}")
                video_capture = temp_cap
                break
            else:
                temp_cap.release()
        
        if video_capture is None:
            print("No available camera found. Please check your webcam connection and permissions.")
            return

        # Initialize Excel workbook for attendance
        attendance_file = f'attendance_{class_name}_{date.today()}.xls'
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
            return

        print(f"\nTaking attendance for class: {class_name}")
        print("Press 'q' to stop attendance")
        
        # Dictionary to store attendance
        attendance_taken = {}
        
        while True:
            ret, frame = video_capture.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                face_roi = gray[y:y+h, x:x+w]
                
                try:
                    label, confidence = recognizer.predict(face_roi)
                    name = known_names[label] if confidence < 100 else "Unknown"
                    
                    # Check if the recognized person is in the selected class
                    class_students = class_manager.get_class_students(class_name)
                    student_in_class = any(student['name'] == name for student in class_students)
                    
                    if student_in_class and name not in attendance_taken:
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
                    
                    cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                except Exception as e:
                    print(f"Error recognizing face: {e}")
            
            cv2.imshow('Video', frame)
            
            if cv2.waitKey(1) & 0xff == ord('q'):
                print("Attendance session ended")
                break

    except Exception as e:
        print(f"An error occurred during attendance: {e}")
    finally:
        if 'video_capture' in locals() and video_capture is not None:
            video_capture.release()
        cv2.destroyAllWindows()

# Run the main menu
if __name__ == "__main__":
    main_menu()
