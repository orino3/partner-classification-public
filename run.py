import uvicorn
import psutil
import os
import signal
from time import sleep
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def kill_server_on_port(port):
    """Kill any process running on the specified port"""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                for conn in proc.connections('inet'):
                    if conn.laddr.port == port:
                        os.kill(proc.pid, signal.SIGTERM)
                        sleep(1)  # Give it time to shutdown gracefully
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.Error):
                continue
    except Exception as e:
        logger.error(f"Error killing process on port {port}: {e}")

def run_server(port):
    """Run the server with error handling"""
    while True:
        try:
            # Kill any existing process on our port
            kill_server_on_port(port)
            
            # Start the server
            config = uvicorn.Config(
                "app:app",
                host="127.0.0.1",
                port=port,
                reload=True,
                reload_dirs=["./"],
                log_level="info",
                workers=1
            )
            
            server = uvicorn.Server(config)
            server.run()
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Server error: {e}")
            logger.info("Restarting server in 5 seconds...")
            sleep(5)

if __name__ == "__main__":
    PORT = 8000
    logger.info(f"Starting server on port {PORT}")
    run_server(PORT) 