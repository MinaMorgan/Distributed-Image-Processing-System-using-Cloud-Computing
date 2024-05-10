import requests
import customtkinter as ctk
from tkinter import Canvas, filedialog, messagebox
from PIL import Image, ImageTk
import os
import matplotlib.pyplot as plt
import numpy as np
import time
import uuid

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# def plot_image(data):
#     image_array = np.array(data)
#     plt.figure()
#     plt.imshow(image_array, cmap='gray', interpolation='nearest')
#     plt.title("Result")
#     plt.axis('off')
#     plt.show()

def save_image(data, filename_prefix="image"):
    # Generate a unique filename based on current timestamp
    timestamp = int(time.time())
    filename = f"{filename_prefix}_{timestamp}.jpg"
    # Convert the data array to unsigned integer 8-bit
    image_array = np.array(data, dtype=np.uint8)
    # Create PIL Image object
    image = Image.fromarray(image_array)
    # Save the image to file
    image.save(filename)
    messagebox.showinfo("Save Successful", f"Image saved as {filename}")
    return filename  # Return the filename for reference

def open_image(filename):
    # Open the image using the default image viewer
    image = Image.open(filename)
    image.show()

def plot_image(data):
    # Generate a unique filename using UUID
    unique_filename = str(uuid.uuid4()) + ".jpg"
    
    # Check if the filename already exists
    while os.path.exists(unique_filename):
        unique_filename = str(uuid.uuid4()) + ".jpg"
    
    # Save the image with the unique filename
    filename = save_image(data, unique_filename)
    #open_image(filename)


class ImageProcessor(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Image Processing Application")
        self.geometry("640x480")
        self.resizable(False, False)

        self.load_background()

        self.create_widgets()

    def load_background(self):
        # Load the background image
        image_path = "images/Background.jpg"
        original_image = Image.open(image_path)
        self.background_image = ImageTk.PhotoImage(original_image)

        self.canvas = Canvas(self, width=640, height=480)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.background_image, anchor="nw")

    def create_widgets(self):
        # Button for selecting an image
        self.select_image_button = ctk.CTkButton(self, text="Select Image", width=200, command=self.select_image)
        self.select_image_button.place(x=220, y=40)

        # Label for the text entry
        self.text_label = ctk.CTkLabel(self, text="Text:")
        self.text_label.place(x=220, y=80)
        
        # Text entry
        self.text_entry = ctk.CTkEntry(self, width=170)
        self.text_entry.place(x=250, y=80)
        
        # Label for the text entry
        self.text_label = ctk.CTkLabel(self, text="Operation:")
        self.text_label.place(x=220, y=120)

        # Combobox for selecting operations
        self.operation_combobox = ctk.CTkComboBox(self, width=140, values=["edge_detection", "color_inversion", "grayscale", "threshold", "blur", "dilate", "erode", "resize", "equalize_histogram", "find_contours", "read_qr_code"])
        self.operation_combobox.set("")  # Set the empty string as the default selected value
        self.operation_combobox.place(x=280, y=120)

        # Button for sending requests
        self.send_request_button = ctk.CTkButton(self, text="Send Request", width=200, command=self.send_request)
        self.send_request_button.place(x=220, y=160)
        
        # File label to show the name of the selected file
        self.image_path = ctk.StringVar()
        self.image_path.trace_add("write", self.update_file_label)
        self.file_label = ctk.CTkLabel(self, text="")
        self.file_label.place(x=450, y=40)

    def select_image(self):
        file_types = [
            ('Image files', '*.jpg *.jpeg *.png *.gif *.bmp'),
            ('JPEG', '*.jpg;*.jpeg'),
            ('PNG', '*.png'),
            ('GIF', '*.gif'),
            ('BMP', '*.bmp'),
        ]
        
        filenames = filedialog.askopenfilenames(filetypes=file_types)
        
        if filenames:
            print("Selected files:", filenames)
            # Convert tuple of filenames to a single string separated by semicolons
            self.image_path.set(";".join(filenames))
        else:
            self.image_path.set("")    
    

    def send_request(self):
        url = 'http://16.170.213.68:5000/process'
        
        image_paths = self.image_path.get().split(";")
        for image_path in image_paths:
            try:
                files = {'images': open(image_path, 'rb')}
                data = {
                    'text': self.text_entry.get(),
                    'operation': self.operation_combobox.get()
                }
                #print("Sending files:", files) 
                #print("Sending data:", data) 
                response = requests.post(url, files=files, data=data)
                #print("Received response:", response.json()) 
                json_response = response.json()
                if 'results' in json_response:
                    results = json_response['results']
                    for result in results:
                        plot_image(result)
                else:
                    messagebox.showerror("Error", "No 'results' found in the response.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send request: {e}")



    
    def update_file_label(self, *args):
        self.file_label.configure(text=os.path.basename(self.image_path.get()))

if __name__ == "__main__":
    app = ImageProcessor()
    app.mainloop()
