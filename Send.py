import requests
import tkinter as tk
import os
from tkinter import filedialog, ttk
from PIL import Image, ImageTk

def send_request(image_path,text,operation):
    url = 'http://13.50.240.154:5000/process'
    files = {'image': open(image_path, 'rb')}
    data = {
        'text': text,
        'operation': operation
    }

    response = requests.post(url, files=files, data=data)
    print(response.json())

############################# GUI ##################################
def load_image(file_path):
    image = Image.open(file_path)
    return ImageTk.PhotoImage(image)

def select_image():
    filename = filedialog.askopenfilename()
    return filename


root = tk.Tk()
root.title("Image Processing")
root.geometry("639x360")

background_image = load_image("Background.jpg")
background_label = tk.Label(root, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Image selector
image_path = tk.StringVar()
image_button = tk.Button(root, text="Select Image", command=lambda: image_path.set(select_image()))
image_button.place(x=100,y=10)

# Label to display the name of the selected file
file_label = tk.Label(root, text="")
file_label.place(x=200,y=10)

# Update the file_label
def update_file_label(*args):
    file_label.config(text=os.path.basename(image_path.get()))
image_path.trace_add("write", update_file_label)

# Image Text
text_label = tk.Label(root, text="Text:")
text_label.place(x=100,y=50)
text_entry = tk.Entry(root)
text_entry.place(x=200,y=50)

# Combobox for operation
operation_label = tk.Label(root, text="Operation:")
operation_label.place(x=100,y=100)
operation_combobox = ttk.Combobox(root, values=["edge_detection", "color_inversion"])
operation_combobox.place(x=200,y=100)

# Send request
send_button = tk.Button(root, text="Send Request", command=lambda: send_request(image_path.get(), text_entry.get(), operation_combobox.get()))
send_button.place(x=100,y=150)

root.mainloop()
