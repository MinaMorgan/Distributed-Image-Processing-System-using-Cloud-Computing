import numpy as np
import subprocess
from fastapi import FastAPI, HTTPException
import tempfile
import httpx
import asyncio
import signal
import threading
import uvicorn
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

async def send_ping_to_dispatcher(vm_id: str):
    dispatcher_url = "http://172.31.9.48:5000/ping" #<---------------- Dispatcher IP
    payload = {'vm_id': vm_id}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(dispatcher_url, json=payload)
            if response.status_code == 200:
                pass
            else:
                pass
    except Exception:
        print(f"Error sending ping")


async def run_ping_thread():
    while running:
        print("Sending ping...")
        await send_ping_to_dispatcher("172.31.46.231")#<---------------- Private IP
        await asyncio.sleep(5)

@app.post('/receive_result')
async def receive_result_handler(image: dict):
    received_image = np.array(image.get("image"), dtype=np.uint8)
    operation = image.get("operation")
    text = image.get("text")
    if text is not None:
        if text.isdigit():
            pass
        else:
            text = None
    try:
        print("Before executing MPI process")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.npy') as temp_file:
            np.save(temp_file, received_image)
            temp_file_path = temp_file.name
        if text is None:
            subprocess.run(['mpirun', '--hostfile', 'my_hostfile.txt', '-np', '2', 'python3', 'WorkerV3.py', temp_file_path, operation])
        else:
            subprocess.run(['mpirun', '--hostfile', 'my_hostfile.txt', '-np', '2', 'python3', 'WorkerV3.py', temp_file_path, operation, text])
        print("MPI process completed")
    except Exception as e:
        print("Error executing MPI process:", e)
    finally:
        print("MPI Finish")
        try:
            processed_result = np.load('processed_result.npy')
            processed_result_list = processed_result.tolist()
            if operation == "read_qr_code":
                with open("decoded_data.txt", "r") as file:
                    decoded_data = [line.strip() for line in file.readlines()]
                return processed_result_list, decoded_data
            return processed_result_list
        except Exception as e:
            print("Error loading processed result:", e)
            return []

def run_worker():
    uvicorn.run(app, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    # Register signal handler for SIGINT (CTRL+C)
    signal.signal(signal.SIGINT, signal_handler)
    ping_thread = threading.Thread(target=asyncio.run, args=(run_ping_thread(),))
    ping_thread.start()
    run_worker()
    ping_thread.join()
