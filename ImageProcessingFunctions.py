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

def blur(image):
    kernel_size=(5, 5)
    return cv2.GaussianBlur(image, kernel_size, 0)

def dilate(image):
    kernel = np.ones((10, 10), np.uint8)
    iterations=5
    return cv2.dilate(image, kernel, iterations=iterations)

def erode(image):
    kernel = np.ones((10, 10), np.uint8)
    iterations=5
    return cv2.erode(image, kernel, iterations=iterations)

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

def find_contours(image):
    # Convert the image to grayscale if it's not already
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

    edges = cv2.Canny(gray, 30, 100)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contour_image = image.copy()

    cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 1)

    return contour_image


def read_qr_code(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    qr_codes = decode(gray)
    decoded_data = []

    for qr_code in qr_codes:
        x, y, w, h = qr_code.rect
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        data = qr_code.data.decode("utf-8")
        decoded_data.append(data)
        cv2.putText(image, data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    return image, decoded_data

def PrintTest(l):
    l = "Hello"
    return l
