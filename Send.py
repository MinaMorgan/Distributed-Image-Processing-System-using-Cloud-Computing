import requests
import customtkinter as ctk
from tkinter import Canvas, filedialog, messagebox
from PIL import Image, ImageTk
import os

ctk.set_appearance_mode("Dark")  # Set theme to Dark - Light or System are also options
ctk.set_default_color_theme("blue")  # Set color theme

class ImageProcessor(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Image Processing Application")
        self.geometry("640x480")
        self.resizable(False, False)

        # Load the background image
        self.load_background()

        # Initialize UI components
        self.create_widgets()

    def load_background(self):
        """Load and display a background image on a canvas."""
        # Load the background image using PIL and create a PhotoImage object
        image_path = "Background.jpg"  # Ensure this path is correct
        original_image = Image.open(image_path)
        self.background_image = ImageTk.PhotoImage(original_image)

        # Create a canvas and add the background image to it
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
        
        # Entry widget for text input
        self.text_entry = ctk.CTkEntry(self, width=170)
        self.text_entry.place(x=250, y=80)
        
        # Label for the text entry
        self.text_label = ctk.CTkLabel(self, text="Operation:")
        self.text_label.place(x=220, y=120)

        # Combobox for selecting operations
        self.operation_combobox = ctk.CTkComboBox(self, width=140, values=["edge_detection", "color_inversion"])
        self.operation_combobox.set("")  # Set the empty string as the default selected value
        self.operation_combobox.place(x=280, y=120)

        # Button for sending requests
        self.send_request_button = ctk.CTkButton(self, text="Send Request", width=200, command=self.send_request)
        self.send_request_button.place(x=220, y=160)
        
        # File label display to show the name of the selected file
        self.image_path = ctk.StringVar()
        self.image_path.trace_add("write", self.update_file_label)
        self.file_label = ctk.CTkLabel(self, text="")
        self.file_label.place(x=450, y=40)  # Placing it below the text entry

    def select_image(self):
        file_types = [
            ('Image files', '*.jpg *.jpeg *.png *.gif *.bmp'),  # Group common types
            ('JPEG', '*.jpg;*.jpeg'),  # JPEG format
            ('PNG', '*.png'),          # PNG format
            ('GIF', '*.gif'),          # GIF format
            ('BMP', '*.bmp'),          # BMP format
        ]
        
        # Open file dialog only showing the specified file types
        filename = filedialog.askopenfilename(filetypes=file_types)
        
        if filename:
            print("Selected file:", filename)  # Or handle the file path as needed
            self.image_path.set(filename)
        else:
            self.image_path.set("")  # Clear the path if the user cancels the dialog            

    def send_request(self):
        url = 'http://16.16.195.190:5000/process'
        
        image_path = self.image_path.get()
        text = self.text_entry.get()
        operation = self.operation_combobox.get()
        
        try:
            files = {'image': open(image_path, 'rb')}
            data = {
                'text': text,
                'operation': operation
            }
            response = requests.post(url, files=files, data=data)
            print(response.json())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send request: {e}")
    
    def update_file_label(self, *args):
        self.file_label.configure(text=os.path.basename(self.image_path.get()))

if __name__ == "__main__":
    app = ImageProcessor()
    app.mainloop()
