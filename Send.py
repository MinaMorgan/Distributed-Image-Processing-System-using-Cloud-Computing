import requests

url = 'http://13.50.240.154:5000/process'
image_path = "C:\\Users\\DELL\\Desktop\\Spring 24\\Distributed Computing\\Project\\Github\\Distributed-Image-Processing-System-using-Cloud-Computing\\image.jpg"  # Replace with the actual path of the image file

files = {'image': open(image_path, 'rb')}
data = {
    'text': 'HELLLOOOO',
    'operation': 'edge_detection'  # Specify the desired operation (edge_detection or color_inversion)
}

response = requests.post(url, files=files, data=data)
print(response.json())