import subprocess
import sys
import time
import threading
from config import config

def run_api():
    """Run FastAPI server"""
    subprocess.run([
        sys.executable, "api.py"
    ])

def run_streamlit():
    """Run Streamlit app"""
    time.sleep(3)  # Wait for API to start
    subprocess.run([
        "streamlit", "run", "streamlit_app.py",
        "--server.port", str(config.STREAMLIT_PORT),
        "--server.address", config.STREAMLIT_HOST
    ])

if __name__ == "__main__":
    print("Starting AI Calendar Booking Assistant...")
    print(f"API will run on: http://{config.API_HOST}:{config.API_PORT}")
    print(f"Streamlit will run on: http://{config.STREAMLIT_HOST}:{config.STREAMLIT_PORT}")
    
    # Start API server in a separate thread
    api_thread = threading.Thread(target=run_api)
    api_thread.daemon = True
    api_thread.start()
    
    # Start Streamlit app
    run_streamlit()