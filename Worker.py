from mpi4py import MPI
import cv2
import numpy as np
import ImageProcessingFunctions
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

# Function to process image chunk
def process_image_chunk(chunk, operation):
    img = cv2.imdecode(np.frombuffer(chunk, np.uint8), cv2.IMREAD_COLOR)
    print("Processing in Worker")
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

def worker():
    while True:
        try:
            task, status = comm.recv(source=0, tag=MPI.ANY_TAG, status=MPI.Status())

            if status.Get_tag() == 1:  # Health check message (Ping-Pong)
                comm.send("PONG", dest=0, tag=1)
                
            elif status.Get_tag() == 0:
                image_chunk, operation = task
                processed_chunk = process_image_chunk(image_chunk, operation)
                comm.send(processed_chunk, dest=0, tag=0)
        except Exception as e:
            print("Error:", e)

if __name__ == '__main__':
    worker()
