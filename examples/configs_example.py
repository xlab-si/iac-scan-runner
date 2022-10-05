import requests
import sys

url = "http://127.0.0.1:8000/new_config"

par = {
    "creatorid": "8357c950-78d3-4a15-94c6-f911116dcd10"
}

response = requests.post(url, params=par)
configid = str(response.json())
print(configid)


url = "http://127.0.0.1:8000/set_config_params"

parameters = dict()

parameters["user"]="user"

print(parameters)

par1 = {
    "configid": configid,
    "parameters": str(parameters)
}

response = requests.post(url, params=par1)
configid = str(response.json())
print(configid)

