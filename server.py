import numpy as np
import subprocess
from fastapi import FastAPI
from queue import Queue
import tempfile

app = FastAPI()
result_queue = Queue()

@app.post('/receive_result')
async def receive_image_and_operation(image: dict):
    received_image = np.array(image.get("image"), dtype=np.uint8)  # Convert image list back to NumPy array
    operation = image.get("operation")
    try:
        print("Before executing MPI process")
        # Write the image data to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.npy') as temp_file:
            np.save(temp_file, received_image)
            temp_file_path = temp_file.name
        subprocess.run(['mpirun', '--hostfile', 'my_hostfile.txt', '-np', '2', 'python3', 'WorkerV3.py', temp_file_path, operation]) ##If Local: Make it mpiexec :RAFIK
        print("MPI process completed")
    except Exception as e:
        print("Error:", e)

    print("MPI Finish")
    # Read the processed result from the file
    processed_result = np.load('processed_result.npy')
    
    # Convert NumPy array to list before returning
    processed_result_list = processed_result.tolist()
    return processed_result_list


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=5001)
