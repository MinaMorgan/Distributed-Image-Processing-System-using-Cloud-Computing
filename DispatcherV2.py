import uvicorn
import threading
import queue
import cv2
from mpi4py import MPI
from fastapi import FastAPI, UploadFile, Form
import requests
import numpy as np  # Added numpy import for array conversion
from typing import List


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
        
        # Get image dimensions
        height, width, _ = img.shape
        
        # Split the image into two parts (vertical split)
        img1 = img[:, :width//2]
        img2 = img[:, width//2:]
        
        vm1_url = "http://127.0.0.1:5000/receive_result"
        vm2_url = "http://172.31.39.168:5000/receive_result"
        
        result_vm1 = requests.post(vm1_url, json={"image": img1.tolist(), "operation": operation})
        result_vm2 = requests.post(vm2_url, json={"image": img2.tolist(), "operation": operation})
        
        print("Finished and returning to User")
        return result_vm1, result_vm2

    def send_result(self, result):
        comm.send(result, dest=0)

@app.post('/process')
async def process(images: List[UploadFile] = Form(...), text: str = Form(...), operation: str = Form(...)):
    #print("Received images:", images)   # Print received images for debugging
    #print("Received text:", text)       # Print received text for debugging
    #print("Received operation:", operation)   # Print received operation for debugging

    if rank == 0:
        image_paths = []
        for image in images:
            image_path = f'images/{image.filename}'
            image_paths.append(image_path)
            with open(image_path, 'wb') as f:
                f.write(await image.read())
            task_queue.put((image_path, operation))
        
        results = []
        for _ in range(len(image_paths)):
            result = comm.recv(source=MPI.ANY_SOURCE)
            results.append(result.json())
        
        return {'results': results}
    else:
        return {'message': 'This endpoint is for master node only.'}



if __name__ == '__main__':
    for i in range(MPI.COMM_WORLD.Get_size() - 1):
        WorkerThread(task_queue).start()

    if rank == 0:
        uvicorn.run(app, host='0.0.0.0', port=5000)
