from fastapi import FastAPI, UploadFile, Form
from typing import List
from mpi4py import MPI
import numpy as np
import threading
import asyncio
import uvicorn
import httpx
import queue
import time
import json
import cv2
import VMs

app = FastAPI()
task_queue = queue.Queue()
ping_queue = queue.Queue()
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
vm_status = {vm_ip: 0 for vm_ip in VMs.ip}

def check_online():
    online_vms = [vm_ip for vm_ip, last_ping_time in vm_status.items() if last_ping_time != 0]
    online_vms.sort(key=lambda vm_ip: vm_status[vm_ip], reverse=True)  # Sort VMs by last ping time in descending order
    online_vms = online_vms[:2]  # Select the first two online VMs
    print("Online VMS: ", online_vms)
    return online_vms

class WorkerThread(threading.Thread):
    def __init__(self, task_queue):
        threading.Thread.__init__(self)
        self.task_queue = task_queue

    def run(self):
        while True:
            task = self.task_queue.get()
            if task is None:
                break
            image_path, text, operation = task
            result = asyncio.run(self.process_image(image_path, text, operation))  # Run process_image asynchronously
            self.send_result(result)

class WorkerThread(threading.Thread):
    def __init__(self, task_queue):
        threading.Thread.__init__(self)
        self.task_queue = task_queue

    def run(self):
        while True:
            task = self.task_queue.get()
            if task is None:
                break
            image_path, text, operation = task
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.process_image(image_path, text, operation))  # Run process_image asynchronously
            self.send_result(result)

    async def process_image(self, image_path, text, operation):
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        
        # Get image dimensions
        height, width, _ = img.shape
        
        # Split the image into two parts (vertical split)
        img1 = img[:, :width//2]
        img2 = img[:, width//2:]
        base_url = "http://{}:5000/receive_result"
        
        # Check the status of VMs and select the first two online VMs
        online_vms = check_online()

        # Store responses for the first two online VMs
        responses = []
        one_operation_response = None
        temp_img = None
        failed_ip = None
        
        # Create a list to hold tasks for async post_data calls
        tasks = []
        
        for i, vm_ip in enumerate(online_vms):
            if len(online_vms) == 1:
                img1 = img
            img_part = img1 if i == 0 else img2  # Assign image part to VM
            try:
                if operation in ['read_qr_code', 'resize', 'equalize_histogram']:
                    if i == 0:
                        one_operation_response = await post_data(base_url.format(vm_ip), img, text, operation)  # Await post_data asynchronously
                else:
                    task = post_data(base_url.format(vm_ip), img_part, text, operation)  # Create post_data task
                    response = await task  # Await the task individually
                    responses.append(response)  # Append response to list
            except Exception as e:
                temp_img = img_part
                failed_ip = vm_ip
                print("There is a VM Failed:", e)

        # Check if both responses are valid
        if one_operation_response is None:
            if not (all(response and response.status_code == 200 for response in responses) and (len(responses) == len(online_vms))):
                print("Failed to receive valid responses from one or both servers.")
                online_vms = check_online()
                # Reassign failed chunk to another VM
                for new_vm_ip in online_vms:
                    if new_vm_ip != failed_ip:
                        print("Reassigned the failed chunk to another VM:", new_vm_ip)
                        new_response = await post_data(base_url.format(new_vm_ip), temp_img, text, operation)  # Await post_data asynchronously
                        if new_response and new_response.status_code == 200:
                            responses.append(new_response)
        
        # Concatenate the results vertically using numpy
        if operation in ['read_qr_code', 'resize', 'equalize_histogram']:
            new_response = httpx.Response(httpx.codes.OK)
            new_response._content = json.dumps(one_operation_response.json()).encode('utf-8')
        else:
            json_responses = [response.json() for response in responses]
            concatenated_result = np.concatenate(json_responses, axis=1)
            concatenated_result_list = concatenated_result.tolist()

            new_response = httpx.Response(httpx.codes.OK)
            new_response._content = json.dumps(concatenated_result_list).encode('utf-8')

        print("Finished and returning to User")

        return new_response




    def send_result(self, result):
        comm.send(result, dest=0)

async def post_data(url, image, text, operation):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"image": image.tolist(), "text": text, "operation": operation})
        if response.status_code == 200:
            return response
        else:
            return None

@app.post('/process')
async def process(images: List[UploadFile] = Form(...), text: str = Form(None), operation: str = Form(...)):
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
            task_queue.put((image_path, text, operation))
        
        results = []
        for _ in range(len(image_paths)):
            result = comm.recv(source=MPI.ANY_SOURCE)
            results.append(result.json())
        
        return {'results': results}
    else:
        return {'message': 'This endpoint is for master node only.'}

@app.post('/ping')
async def ping(vm_id: dict):
    vm_ip = vm_id.get("vm_id")
    vm_status[vm_ip] = time.time()  # Update timestamp for the VM
    return {'response': 'pong'}

def handle_ping_from_vms():
    uvicorn.run(app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    worker_threads = []
    if rank == 0:
        threading.Thread(target=handle_ping_from_vms).start()
    for i in range(MPI.COMM_WORLD.Get_size() - 1):
        worker_thread = WorkerThread(task_queue)
        worker_thread.start()
        worker_threads.append(worker_thread)
    
    # Wait for all worker threads to finish
    for worker_thread in worker_threads:
        worker_thread.join()
