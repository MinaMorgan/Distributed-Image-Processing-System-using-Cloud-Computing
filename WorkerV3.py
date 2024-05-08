from queue import Queue
import sys
import numpy as np
from mpi4py import MPI
import ImageProcessingFunctions
import json

# Initialization MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
result_queue = Queue()

def process_image(img, operation):
    height, width = img.shape[:2]
    # Broadcast image dimensions to all MPI Threads
    height, width = comm.bcast((height, width), root=0)
    # Define overlap size
    overlap_size = 0  # Adjust if needed (Make it zero for now !! :Rafik)
    # Calculate chunk height for each process including overlap
    chunk_height = (height + (size - 1) * overlap_size) // size
    # Calculate start and end rows for each process
    start_row = rank * (chunk_height - overlap_size)
    end_row = min((rank + 1) * chunk_height, height)
    # Adjust start and end rows for overlapping chunks
    if rank != 0:
        start_row += overlap_size
    if rank != size - 1:
        end_row += overlap_size
    # Ensure start_row and end_row are within image boundaries
    start_row = max(start_row, 0)
    end_row = min(end_row, height)
    # Calculate chunk height after adjusting for overlap
    chunk_height = end_row - start_row
    # Create the chunk with the correct dimensions
    chunk = np.zeros((chunk_height, width, 3), dtype=np.uint8)
    # Copy the corresponding part of the image to the chunk
    if chunk_height > 0:
        chunk[:chunk_height, :, :] = img[start_row:end_row, :, :]
    # Processing with overlap
    if operation == 'edge_detection':
        processed_chunk = ImageProcessingFunctions.edge_detection(chunk)
    elif operation == 'color_inversion':
        processed_chunk = ImageProcessingFunctions.color_inversion(chunk)
    elif operation == 'grayscale':
        processed_chunk = ImageProcessingFunctions.grayscale(chunk)
    elif operation == 'threshold':
        processed_chunk = ImageProcessingFunctions.threshold(chunk)
    elif operation == 'blur':
        processed_chunk = ImageProcessingFunctions.blur(chunk)
    elif operation == 'dilate':
        processed_chunk = ImageProcessingFunctions.dilate(chunk)
    elif operation == 'erode':
        processed_chunk = ImageProcessingFunctions.erode(chunk)
    elif operation == 'resize':
        processed_chunk = ImageProcessingFunctions.resize(chunk)
    elif operation == 'equalize_histogram':
        processed_chunk = ImageProcessingFunctions.equalize_histogram(chunk)
    elif operation == 'find_contours':
        processed_chunk = ImageProcessingFunctions.find_contours(chunk)
    elif operation == 'read_qr_code':
        processed_chunk = ImageProcessingFunctions.read_qr_code(chunk)
    else:
        processed_chunk = None  # Operation not supported
    # Send chunks to rank 0
    gathered_chunks = comm.gather(processed_chunk, root=0)

    # Stitching the image
    if rank == 0:
        # Concatenate gathered chunks into a single list
        concatenated_chunks = []
        for i, proc_chunk in enumerate(gathered_chunks):
            if i == 0:
                concatenated_chunks.append(proc_chunk)
            else:
                concatenated_chunks.append(proc_chunk[overlap_size:])

        # Concatenate gathered chunks into processed image
        processed_image = np.vstack(concatenated_chunks) # this is vertical stack
        return processed_image


if __name__ == "__main__":
    # Extract image and operation from command-line arguments
    received_image = np.load(sys.argv[1])
    operation = sys.argv[2]

    # Perform image processing using MPI
    print(f"Processing in workerV3 and my rank: {rank}")
    processed_result = process_image(received_image, operation)
    # Save the processed result into a file
    if rank ==0:
        np.save('processed_result.npy', processed_result)