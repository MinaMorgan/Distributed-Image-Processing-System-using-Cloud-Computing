import requests

url = 'http://127.0.0.1:5000/test'
file = {'file': open('1234.pem', 'rb')}
resp = requests.post(url=url, files=file) 
print(resp.json())