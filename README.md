# IaC Scan Runner
The IaC Scan Runner is a REST API service used to scan IaC (Infrastructure as Code) package and perform various code 
checks in order to find possible vulnerabilities and improvements.

## Table of Contents
  - [Running](#running)
      - [Run with Docker](#run-with-docker)
      - [Run from CLI](#run-from-cli)
      - [Run from source](#run-from-source)

## Running
This section explains how to run the REST API.

### Run with Docker
You can run the REST API using a public [Docker image] as follows:

```bash
# run IaC Scan Runner REST API in a Docker container and 
# navigate to localhost:8080/swagger or localhost:8080/redoc
docker run --name iac-scan-runner -p 8080:80 xscanner/runner
```

Or you can build the image locally and run it as follows:

```bash
# build Docker container (it will take some time) 
docker build -t iac-scan-runner .
# run IaC Scan Runner REST API in a Docker container and 
# navigate to localhost:8080/swagger or localhost:8080/redoc
docker run --name iac-scan-runner -p 8080:80 iac-scan-runner
```

### Run from CLI
To run using the IaC Scan Runner CLI:

```bash
# install the CLI
python3 -m venv .venv && . .venv/bin/activate
pip install iac-scan-runner
# print OpenAPI specification
iac-scan-runner openapi
# install prerequisites
iac-scan-runner install
# run IaC Scan Runner REST API
iac-scan-runner run
```

### Run from source
To run locally from source:

```bash
# install prerequisites
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
./install-checks.sh
# run IaC Scan Runner REST API (add --reload flag to apply code changes on the way)
uvicorn src.iac_scan_runner.api:app
```

[Docker image]: https://hub.docker.com/r/xscanner/runner
