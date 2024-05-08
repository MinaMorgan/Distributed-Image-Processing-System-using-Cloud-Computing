import uvicorn
import threading
import queue
import cv2
from mpi4py import MPI
from fastapi import FastAPI, UploadFile, Form
import requests
import numpy as np  # Added numpy import for array conversion

app = FastAPI()
task_queue = queue.Queue()
comm = MPI.COMM_WORLD
rank = comm.Get_rank()

class WorkerThread(threading.Thread):
    def __init__(self, task_queue):
        threading.Thread.__init__(self)
        self.task_queue = task_queue

    def run(self):
        while True:
            task = self.task_queue.get()
            if task is None:
                break
            image_path, operation = task
            result = self.process_image(image_path, operation)  # Pass image path instead of image array
            self.send_result(result)

    def process_image(self, image_path, operation):
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        vm2_url = "http://13.60.82.253:5000/receive_result"
        result = requests.post(vm2_url, json={"image": img.tolist(), "operation": operation})  # Convert img to list
        print("Finished and returning to User")
        return result

    def send_result(self, result):
        comm.send(result, dest=0)

@app.post('/process')
async def process(image: UploadFile = Form(...), text: str = Form(...), operation: str = Form(...)):
    if rank == 0:
        image_path = 'images/image.jpg'  # Set the path :RAFIK
        with open(image_path, 'wb') as f:
            f.write(await image.read())
        task_queue.put((image_path, operation))
        result = comm.recv(source=MPI.ANY_SOURCE)
        return {'result': result.json()}

    else:
        return {'message': 'This endpoint is for master node only.'}

if __name__ == '__main__':
    for i in range(MPI.COMM_WORLD.Get_size() - 1):
        WorkerThread(task_queue).start()

    if rank == 0:
        uvicorn.run(app, host='0.0.0.0', port=5000)
