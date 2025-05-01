import socket
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    # Test local socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', 5000))
        logger.info("Port 5000 is available")
        sock.close()
    except socket.error as e:
        logger.error(f"Port 5000 is not available: {e}")
    
    # Test HTTPS connection
    try:
        response = requests.get('https://192.168.31.128:5000', verify=False)
        logger.info(f"HTTPS connection successful. Status code: {response.status_code}")
    except requests.exceptions.SSLError as e:
        logger.error(f"SSL Error: {e}")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_connection() 