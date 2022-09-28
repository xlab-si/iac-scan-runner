import requests
import sys

url = "http://127.0.0.1:8000/new_project"

par = {
    "creatorid": "8357c950-78d3-4a15-94c6-f911116dcd10"
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
