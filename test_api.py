import requests

url = "http://127.0.0.1:8000/add_patient/"
params = {
    "name": "Rahul",
    "age": 22,
    "gender": "Male"
}

response = requests.post(url, params=params)
print(response.json())
