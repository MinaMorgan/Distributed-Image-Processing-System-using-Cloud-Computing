import uvicorn
import threading
import queue
import cv2
from mpi4py import MPI
from fastapi import FastAPI, UploadFile, Form

app = FastAPI()
task_queue = queue.Queue()
comm = MPI.COMM_WORLD
rank = comm.Get_rank()

class WorkerThread(threading.Thread):
    def __init__(self, task_queue):
        threading.Thread.__init__(self)
        self.task_queue = task_queue
        print(rank)

    def run(self):
        while True:
            task = self.task_queue.get()
            if task is None:
                break
            image, operation = task
            print(operation)
            result = self.process_image(image, operation)
            self.send_result(result)

    def process_image(self, image, operation):
        print("in process")
        img = cv2.imread(image, cv2.IMREAD_COLOR)
        if operation == 'edge_detection':
            result = cv2.Canny(img, 100, 200)
        elif operation == 'color_inversion':
            result = cv2.bitwise_not(img)
        # Add more operations as needed...
        return result

    def send_result(self, result):
        comm.send(result, dest=0)

@app.post('/process')
async def process(image: UploadFile = Form(...), text: str = Form(...), operation: str = Form(...)):
    if rank == 0:
        image_path = '/home/ubuntu/Distributed-Image-Processing-System-using-Cloud-Computing/image.jpg'  # Set the appropriate path
        with open(image_path, 'wb') as f:
            f.write(await image.read())
        task_queue.put((image_path, operation))
        result = comm.recv(source=MPI.ANY_SOURCE)
        return {'result': result.tolist()}
    else:
        return {'message': 'This endpoint is for master node only.'}

if __name__ == '__main__':
    # Create worker threads
    for i in range(MPI.COMM_WORLD.Get_size() - 1):
        WorkerThread(task_queue).start()

    if rank == 0:
        uvicorn.run(app, host='0.0.0.0', port=5000)