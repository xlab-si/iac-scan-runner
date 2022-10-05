import requests
import sys

url = "http://127.0.0.1:8000/new_project"

par = {
    "creatorid": "penenadpi"
}

response = requests.post(url, params=par)
projectid = str(response.json())
print(projectid)

par = {
    "configid": "updated_config_value"
}

par["projectid"] = projectid

url = "http://127.0.0.1:8000/set_project_config"
response = requests.post(url, params=par)
print(response.json())

par = {
    "creatorid": "penenadpi"
}

url = "http://127.0.0.1:8000/projects"
response = requests.get(url, params=par)
print(response.json())
