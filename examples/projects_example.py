import requests
import sys

url = "http://127.0.0.1:8000/new_project"

par = {
    "creatorid": "penenadpi"
}

response = requests.post(url, params=par)
projectid = str(response.json())
print(projectid)

checkname="tfsec"

url = f"http://127.0.0.1:8000/checks/{checkname}/enable"

par = {
    "projectid": projectid
}

response = requests.put(url, params=par)
print(response.json())



checkname="tflint"

url = f"http://127.0.0.1:8000/checks/{checkname}/enable"

par = {
    "projectid": projectid
}

response = requests.put(url, params=par)
print(response.json())



checkname="tfsec"

url = f"http://127.0.0.1:8000/checks/{checkname}/disable"

par = {
    "projectid": projectid
}

response = requests.put(url, params=par)
print(response.json())

par = {
    "creatorid": "penenadpi"
}

url = "http://127.0.0.1:8000/projects"
response = requests.get(url, par)
print(response.json())

url = "http://127.0.0.1:8000/projects"
response = requests.get(url)
print(response.json())


