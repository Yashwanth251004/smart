import sys

# Add your project directory to the Python path
path = '/home/yourusername/smart-attendance-system'
if path not in sys.path:
    sys.path.append(path)

# Import your Flask application
from app import app as application

# Configure the application
application.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
application.config['DEBUG'] = False  # Set to False in production 