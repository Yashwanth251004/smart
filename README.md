# Smart Attendance System

A modern face recognition-based attendance system built with Python, Flask, and OpenCV.

## Features

- Face recognition for attendance tracking
- Real-time attendance marking
- Student management system
- Excel-based attendance reports
- Web-based dashboard
- Secure login system

## Screenshots

![Dashboard](screenshots/dashboard.png)
![Student Management](screenshots/students.png)
![Attendance Report](screenshots/report.png)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/smart-attendance-system.git
cd smart-attendance-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python run_web_app.py
```

4. Access the application:
- Local: http://localhost:8080

## Usage

1. Login with default credentials:
   - Username: admin
   - Password: admin

2. Add students through the dashboard
3. Capture face data for each student
4. Start attendance tracking
5. View and export attendance reports

## Project Structure

```
smart-attendance-system/
├── app.py                  # Main Flask application
├── face_recognition.py     # Face recognition module
├── run_web_app.py          # Application runner
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates
│   ├── index.html          # Dashboard
│   ├── login.html          # Login page
│   └── students.html       # Student management
├── static/                 # Static assets
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   └── images/             # Images
└── certificates/           # SSL certificates (if using HTTPS)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenCV for face detection and recognition
- Flask for the web framework
- Bootstrap for the UI components 