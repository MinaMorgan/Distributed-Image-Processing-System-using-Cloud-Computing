import requests
import customtkinter as ctk
from tkinter import Canvas, filedialog, messagebox
from PIL import Image, ImageTk
import os
import numpy as np
import time
import uuid
import threading


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


def show_decoded_data(title, message):
    # Create a top-level window
    window = ctk.CTkToplevel()
    window.title(title)

    # Create a text widget to display the message
    text_widget = ctk.CTkTextbox(window, wrap='word', height=10, width=40)
    text_widget.insert('1.0', message)
    text_widget.pack(expand=True, fill='both')

    # Resize the window to fit the content
    window.update_idletasks()  # Update the window to calculate its size
    width = window.winfo_reqwidth() + 20  # Add some padding
    height = window.winfo_reqheight() + 20  # Add some padding
    window.geometry(f"{width}x{height}")


# def plot_image(data):
#     image_array = np.array(data)
#     plt.figure()
#     plt.imshow(image_array, cmap='gray', interpolation='nearest')
#     plt.title("Result")
#     plt.axis('off')
#     plt.show()
def save_image(data, filename_prefix="image"):
    timestamp = int(time.time())
    filename = f"{filename_prefix}_{timestamp}.jpg"
    image_array = np.array(data, dtype=np.uint8)
    image = Image.fromarray(image_array)
    image.save(filename)
    return filename

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
        self.text_label = ctk.CTkLabel(self, text="Parameter:")
        self.text_label.place(x=220, y=80)
        
        # Text entry
        self.text_entry = ctk.CTkEntry(self, width=135)
        self.text_entry.place(x=285, y=80)
            
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
            self.total_images = len(filenames)  # Set the total number of images selected
            self.show_progress_bar()
        else:
            self.image_path.set("")    
    

    
    def send_request(self):
        def request_thread():
            url = 'http://127.0.0.1:5000/process'  # PUT PUBLIC IP <-------------------
            
            image_paths = self.image_path.get().split(";")
            self.label.configure(text="Processing")
            for idx, image_path in enumerate(image_paths):
                try:
                    with open(image_path, 'rb') as image_file:
                        files = {'images': image_file}
                        data = {
                            'text': self.text_entry.get(),
                            'operation': self.operation_combobox.get()
                        }
                        response = requests.post(url, files=files, data=data)
                        if response.status_code == 200:
                            self.update_progress(idx+1)
                            json_response = response.json()
                        if 'results' in json_response:
                            results = json_response['results']
                            for result in results:
                                if data['operation'] == 'read_qr_code':
                                    plot_image(result[0])
                                    decoded_data = result[1]
                                    show_decoded_data("Decoded Data", decoded_data)
                                else:
                                    plot_image(result)
                        else:
                            messagebox.showerror("Error", "No 'results' found in the response.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to send request: {e}")

        # Start the request in a new thread
        thread = threading.Thread(target=request_thread)
        thread.start()

    def show_progress_bar(self):
        # Create a new top-level window
        self.progress_window = ctk.CTkToplevel()
        self.progress_window.title("Progress")
        self.progress_window.geometry("300x100")  # Adjust size as needed

        # Add a label to display the message above the progress bar
        self.label = ctk.CTkLabel(self.progress_window, text="Ready to Process")
        self.label.pack(pady=10)  # Add some padding vertically

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self.progress_window, width=200)
        self.progress_bar.pack(pady=10)  # Add some padding vertically

        # Initially set progress bar to 0
        self.progress_bar.set(0)

    def update_progress(self, current_index):
        self.progress_value = current_index / self.total_images # Calculate progress as a percentage
        self.progress_bar.set(self.progress_value)  # Update the progress bar
        if current_index >= self.total_images:
            self.label.configure(text="Task Done")
    
    def update_file_label(self, *args):
        self.file_label.configure(text=os.path.basename(self.image_path.get()))

if __name__ == "__main__":
    app = ImageProcessor()
    app.mainloop()
