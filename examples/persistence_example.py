import requests
import sys



print("SHOW ALL RESULTS")

URL = "http://127.0.0.1:8000/results"

uuids = {
    "uuid": "8357c950-78d3-4a15-94c6-f911116dcd10"
}

response = requests.get(URL, uuids)
print(response.json())

scan_result = response.json()

print(scan_result)

uuid="8357c950-78d3-4a15-94c6-f911116dcd10"

print('SHOW SINGLE RESULT')

URL = "http://127.0.0.1:8000/results"

response = requests.get(URL, uuids)
scan_result = response.json()

print(scan_result)

print('DELETE SINGLE RESULT')

URL = f"http://127.0.0.1:8000/results/{uuid}"

response = requests.delete(URL)
scan_result = response.json()

print(scan_result)

