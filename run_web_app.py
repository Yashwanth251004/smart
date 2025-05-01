from app import app
import logging
import socket
import webbrowser
import time
import os
import sys

if __name__ == "__main__":
    # Set up detailed logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Get local IP address
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        logger.info(f"Local IP address: {local_ip}")
        
        port = 8080
        
        # Check if port is available
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', port))
            sock.close()
        except socket.error:
            logger.error(f"Port {port} is already in use. Please close any applications using this port.")
            sys.exit(1)
        
        # Start the Flask application
        logger.info(f"Starting Flask application on port {port}...")
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)  # Wait for Flask to start
            try:
                webbrowser.open(f'http://localhost:{port}')
                logger.info("Browser opened successfully")
            except Exception as e:
                logger.error(f"Failed to open browser: {e}")
        
        # Start browser in a separate thread
        import threading
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Run the Flask application
        app.run(
            host='0.0.0.0',  # Allow all connections
            port=port,
            debug=True,
            use_reloader=False
        )
    except Exception as e:
        logger.error(f"Failed to start Flask application: {e}")
        logger.info("Troubleshooting steps:")
        logger.info("1. Make sure no other application is using port 8080")
        logger.info("2. Check if the firewall is blocking the connection")
        logger.info("3. Try accessing the application using:")
        logger.info(f"   - http://localhost:{port}")
        logger.info(f"   - http://127.0.0.1:{port}")
        logger.info(f"   - http://{local_ip}:{port}")
        raise 