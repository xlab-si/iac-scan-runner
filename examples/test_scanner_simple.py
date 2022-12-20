import requests
import sys

URL = "http://127.0.0.1:8000/scan"

print(sys.argv[0])
multipart_form_data = {
    "iac": (sys.argv[1], open(sys.argv[1], "rb")),
    "checks": (None, sys.argv[2])
}

par = { 
    "projectid" : (None, "074c9d59-02f1-4996-b919-a95bf497e9e1") 
}

response = requests.post(URL, files = multipart_form_data, params=par)
print(response.json())

scan_result = response.json()

print(scan_result)
