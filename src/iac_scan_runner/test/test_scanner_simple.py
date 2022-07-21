import requests

URL = "http://127.0.0.1:8000/scan"
multipart_form_data = {
    "iac": ("hello-world.zip", open("hello-world.zip", "rb")),
    "checks": (None, "git-leaks,tfsec,tflint,shellcheck"),
}
response = requests.post(URL, files=multipart_form_data)
print(response.json())

scan_result = response.json()
print("First----------------")
print(scan_result["tfsec"]["output"])
print("Second---------------")
print(scan_result["git-leaks"]["output"])
print("Third----------------")
print(scan_result["tflint"]["output"])
print("Fourth---------------")
print(scan_result["shellcheck"]["output"])
