import numpy as np
import subprocess
from fastapi import FastAPI
import tempfile
import requests
import time
import threading
import uvicorn
import signal
import sys

app = FastAPI()

# Global flag to indicate whether the program should continue running
running = True

# Function to handle SIGINT signal (Ctrl+C)
def signal_handler(sig, frame):
    global running
    print("Exiting...")
    running = False
    sys.exit(0)

def send_ping_to_dispatcher(vm_id: str):
    dispatcher_url = "http://127.0.0.1:5000/ping"   #PUT PRIVATE IP <--------------------
    payload = {'vm_id': vm_id}
    try:
        response = requests.post(dispatcher_url, json=payload)
        if response.status_code == 200:
            #print(f"Ping: {vm_id}")
            pass
        else:
            pass
            #print(f"Failed to send ping and communicate: {vm_id}")
    except Exception:
        pass
        print(f"Error sending ping")


def run_ping_thread():
    while running:
        print("Sending ping...")
        send_ping_to_dispatcher("127.0.0.1:5001") #PUT VM's ID    <--------------------
        time.sleep(5)

@app.post('/receive_result')
async def receive_image_and_operation(image: dict):
    received_image = np.array(image.get("image"), dtype=np.uint8)  # Convert image list back to NumPy array
    operation = image.get("operation")
    text = image.get("text")
    if text is not None:
        if text.isdigit():
            pass
        else:
            text = None
    try:
        print("Before executing MPI process")
        # Write the image data to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.npy') as temp_file:
            np.save(temp_file, received_image)
            temp_file_path = temp_file.name
        if text is None:
            subprocess.run(['mpiexec','-np', '2', 'python', 'WorkerV3.py', temp_file_path, operation]) ##If Local: Make it mpiexec :RAFIK
        else:
            subprocess.run(['mpiexec','-np', '2', 'python', 'WorkerV3.py', temp_file_path, operation, text]) ##If Local: Make it mpiexec :RAFIK
        print("MPI process completed")
    except Exception as e:
        print("Error executing MPI process:", e)
    finally:
        print("MPI Finish")
        # Read the processed result from the file
        try:
            processed_result = np.load('processed_result.npy')
            processed_result_list = processed_result.tolist()
            if operation == "read_qr_code":
                with open("decoded_data.txt", "r") as file:
                    decoded_data = [line.strip() for line in file.readlines()]
                return processed_result_list,decoded_data
            # Convert NumPy array to list before returning
            return processed_result_list
        except Exception as e:
            print("Error loading processed result:", e)
            return []

def run_Worker():
    uvicorn.run(app, host='127.0.0.1', port=5001)

if __name__ == "__main__":
    # Register signal handler for SIGINT (CTRL+C)
    signal.signal(signal.SIGINT, signal_handler)
    ping_thread = threading.Thread(target=run_ping_thread)
    ping_thread.start()
    run_Worker()
    ping_thread.join()
