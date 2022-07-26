import requests
import sys

URL = "http://127.0.0.1:8000/scan"

multipart_form_data = {
    "iac": (sys.argv[1], open(sys.argv[1], "rb")),
    "checks": (None, sys.argv[2]),
}
response = requests.post(URL, files=multipart_form_data)
print(response.json())

scan_result = response.json()

print(scan_result)
