import requests
import socket
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_server(host, port):
    # Test 1: Check if port is open
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    if result == 0:
        logger.info(f"Port {port} is open")
    else:
        logger.error(f"Port {port} is closed")
    sock.close()
    
    # Test 2: Try HTTP connection
    try:
        response = requests.get(f'http://{host}:{port}', timeout=5)
        logger.info(f"HTTP connection successful. Status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        logger.error("Connection refused. Server might not be running.")
    except requests.exceptions.Timeout:
        logger.error("Connection timed out. Server might be blocked by firewall.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    # Use command line arguments or default values
    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.31.128"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    
    logger.info(f"Testing connection to {host}:{port}")
    test_server(host, port) 