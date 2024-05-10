import numpy as np
import cv2
from mpi4py import MPI
import Testing

# Initialization MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

img = cv2.imread("Image Test.jpg")
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
processed_chunk = Testing.equalize_histogram(chunk) #################### TODO:CHANGE FUNCTIONS

####################JUST FOR TESTING#################### Checking that each chunk is correct: Rafik
# if processed_chunk is not None:
#     cv2.imshow(f"Chunk {rank}", chunk)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

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

    cv2.imwrite("output_image.jpg", processed_image)

MPI.Finalize()
