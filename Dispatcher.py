import uvicorn
import threading
import queue
import cv2
from mpi4py import MPI
from fastapi import FastAPI, UploadFile, Form
import tempfile
import numpy as np
import time
import ImageProcessingFunctions

app = FastAPI()
task_queue = queue.Queue()
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# List to keep track of worker node status (0: available, 1: unavailable)
worker_status = [0] * (size - 1)

def check_worker_status():
    while True:
        for i in range(1, size):
            try:
                # Send a test message to worker node
                comm.send("PING", dest=i)
                # Wait for response within a timeout period
                response = comm.recv(source=i, tag=1, status=MPI.Status())
                if response == "PONG":
                    worker_status[i - 1] = 0  # Node is available
            except Exception as e:
                worker_status[i - 1] = 1  # Node is unavailable
        time.sleep(5)  # Check node status every 5 seconds

# Thread for checking worker node status
status_thread = threading.Thread(target=check_worker_status)
status_thread.start()

class WorkerThread(threading.Thread):
    def __init__(self, task_queue):
        threading.Thread.__init__(self)
        self.task_queue = task_queue

    def run(self):
        while True:
            task = self.task_queue.get()
            if task is None:
                break
            image_chunk, operation = task
            result = self.process_image(image_chunk, operation)
            self.send_result(result)

    def process_image(self, image_chunk, operation):
        img = cv2.imdecode(np.frombuffer(image_chunk, np.uint8), cv2.IMREAD_COLOR)
        print("Processing")
        if operation == 'edge_detection':
            result = ImageProcessingFunctions.edge_detection(img)
        elif operation == 'color_inversion':
            result = ImageProcessingFunctions.color_inversion(img)
        elif operation == 'grayscale':
            result = ImageProcessingFunctions.grayscale(img)
        elif operation == 'threshold':
            result = ImageProcessingFunctions.threshold(img)
        elif operation == 'blur':
            result = ImageProcessingFunctions.blur(img)
        elif operation == 'dilate':
            result = ImageProcessingFunctions.dilate(img)
        elif operation == 'erode':
            result = ImageProcessingFunctions.erode(img)
        elif operation == 'resize':
            result = ImageProcessingFunctions.resize(img)
        elif operation == 'equalize_histogram':
            result = ImageProcessingFunctions.equalize_histogram(img)
        elif operation == 'find_contours':
            result = ImageProcessingFunctions.find_contours(img)
        elif operation == 'read_qr_code':
            result = ImageProcessingFunctions.read_qr_code(img)
        else:
            result = None  # Operation not supported

        return result

    def send_result(self, result):
        comm.send(result, dest=0)

@app.post('/process')
async def process_image(image: UploadFile = Form(...), operation: str = Form(...)):
    if rank == 0:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(await image.read())
            image_path = temp_file.name

        # Read the image and split it into chunks
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        height, width = img.shape[:2]
        chunk_size = (height + size - 1) // size

        # Send image chunks to worker nodes
        for i in range(1, size):
            start_row = chunk_size * (i - 1)
            end_row = min(chunk_size * i, height)
            chunk = img[start_row:end_row, :, :]
            encoded_chunk = cv2.imencode(".jpg", chunk)[1].tobytes()
            task_queue.put((encoded_chunk, operation))

        # Process the last chunk on the dispatcher node
        last_chunk = img[chunk_size * (size - 1):, :, :]
        last_encoded_chunk = cv2.imencode(".jpg", last_chunk)[1].tobytes()
        processed_last_chunk = WorkerThread.process_image(last_encoded_chunk, operation)

        # Gather processed chunks from worker nodes
        processed_chunks = [processed_last_chunk] + [comm.recv(source=i) for i in range(1, size)]

        # Stitch the processed chunks
        processed_image = np.vstack(processed_chunks)

        return {'result': processed_image.tolist()}
    else:
        return {'message': 'This endpoint is for the master node only.'}

def redistribute_tasks():
    while True:
        time.sleep(10)  # Check node status every 10 seconds
        for i in range(1, size):
            if worker_status[i - 1] == 1:  # If node is unavailable
                # Redistribute tasks assigned to the failed node
                while not task_queue.empty():
                    task_queue.get()  # Clear the task queue
                print(f"Worker node {i} is unavailable. Redistributing tasks...")
                # Resend tasks to other available nodes
                for j in range(1, size):
                    if j != i and worker_status[j - 1] == 0:  # If node is available
                        while not task_queue.empty():
                            task_queue.put(task_queue.get())  # Resend tasks to available nodes
                        break
                break

# Thread for redistributing tasks
redistribute_thread = threading.Thread(target=redistribute_tasks)
redistribute_thread.start()


if __name__ == '__main__':
    for i in range(size - 1):
        WorkerThread(task_queue).start()

    if rank == 0:
        uvicorn.run(app, host='0.0.0.0', port=5000)
