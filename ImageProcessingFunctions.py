import cv2
import numpy as np
from pyzbar.pyzbar import decode

def edge_detection(image):
    return cv2.Canny(image, 100, 200)

def color_inversion(image):
    return cv2.bitwise_not(image)

def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def threshold(image):
    threshold_value=128
    max_value=255
    threshold_type=cv2.THRESH_BINARY
    image = grayscale(image)
    _, binary_image = cv2.threshold(image, threshold_value, max_value, threshold_type)
    return binary_image

def blur(image, kernel_size=None):
    if kernel_size is None:
        kernel_size = (5, 5)
    elif isinstance(kernel_size, int):
        if kernel_size %2 == 0:
            kernel_size = kernel_size-1
        kernel_size = (kernel_size, kernel_size)
    return cv2.GaussianBlur(image, kernel_size, 0)

def dilate(image, kernel_size=None):
    if kernel_size is None:
        kernel_size = (5, 5)
    elif isinstance(kernel_size, int):
        if kernel_size %2 == 0:
            kernel_size = kernel_size-1
        kernel_size = (kernel_size, kernel_size)
    kernel = np.ones(kernel_size, np.uint8)
    iterations = 2
    return cv2.dilate(image, kernel, iterations=iterations)

def erode(image, kernel_size=None):
    if kernel_size is None:
        kernel_size = (5, 5)
    elif isinstance(kernel_size, int):
        if kernel_size %2 == 0:
            kernel_size = kernel_size-1
        kernel_size = (kernel_size, kernel_size)
    kernel = np.ones(kernel_size, np.uint8)
    iterations = 2
    return cv2.erode(image, kernel, iterations=iterations)

def find_contours(image):
    # Convert the image to grayscale if it's not already
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

    edges = cv2.Canny(gray, 30, 100)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contour_image = image.copy()

    cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 1)

    return contour_image
##########################################################
def resize(image, width=None, height=None):
    if width is None and height is None:
        return image
    elif width is None:
        r = height / image.shape[0]
        dim = (int(image.shape[1] * r), height)
    elif height is None:
        r = width / image.shape[1]
        dim = (width, int(image.shape[0] * r))
    else:
        dim = (width, height)
    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

def equalize_histogram(image):
    if len(image.shape) == 3:
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray_image = image
    img_equalized = cv2.equalizeHist(gray_image)
    return img_equalized


def read_qr_code(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    qr_codes = decode(gray)
    decoded_data = []

    for qr_code in qr_codes:
        x, y, w, h = qr_code.rect
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        data = qr_code.data.decode("utf-8")
        decoded_data.append(data)
        
        # Calculate the font scale based on the length of the decoded data
        font_scale = min(1, 1000 / len(data))  # Adjust 1000 as needed based on your image size
        
        # Calculate the thickness of the text
        thickness = max(1, int(font_scale))
        
        # Get the size of the text
        (text_width, text_height), _ = cv2.getTextSize(data, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        
        # Calculate the position to place the text
        text_x = max(x, 0)
        text_y = y + h + text_height + 10  # Adjust 10 as needed
        
        # Ensure text stays within image boundaries
        if text_x + text_width > image.shape[1]:
            text_x = image.shape[1] - text_width - 10  # Adjust 10 as needed
        
        # Draw the text on the image
        cv2.putText(image, data, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), thickness)

    return image, decoded_data


#############################################
def PrintTest(l):
    l = "Hello"
    return l
def Test(image):
    print("HEEEEEERE")
    return image
