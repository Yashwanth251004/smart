import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def configure_firewall():
    if not is_admin():
        logger.error("This script needs to be run as administrator!")
        logger.info("Please right-click on the script and select 'Run as administrator'")
        return False

    try:
        # Get the Python executable path
        python_path = sys.executable
        
        # Create firewall rule for Python
        logger.info("Creating firewall rule for Python...")
        subprocess.run([
            'netsh', 'advfirewall', 'firewall', 'add', 'rule',
            'name=Flask Web Server',
            f'program={python_path}',
            'dir=in',
            'action=allow',
            'protocol=TCP',
            'localport=5000'
        ], check=True)
        
        logger.info("Firewall rule created successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to configure firewall: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting firewall configuration...")
    if configure_firewall():
        logger.info("Firewall has been configured successfully.")
        logger.info("You can now run the Flask application.")
    else:
        logger.error("Failed to configure firewall.")
        logger.info("Please try running the script as administrator.") 