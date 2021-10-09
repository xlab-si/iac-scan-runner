# IaC Scan Runner
Service that checks your IaC for issues and vulnerabilities.

[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/xlab-si/iac-scan-runner/Build%20and%20publish?label=ci%2Fcd)](https://github.com/xlab-si/iac-scan-runner/actions)
[![Docker Image Version (latest by date)](https://img.shields.io/docker/v/xscanner/runner?color=blue&label=docker)](https://hub.docker.com/r/xscanner/runner)
[![PyPI](https://img.shields.io/pypi/v/iac-scan-runner)](https://pypi.org/project/iac-scan-runner/)
[![Test PyPI](https://img.shields.io/badge/test%20pypi-dev%20version-blueviolet)](https://test.pypi.org/project/iac-scan-runner/)

| Aspect            | Information          |
| ----------------- |:--------------------:|
| Tool name         | **IaC Scan Runner**  |
| Docker image      | [xscanner/runner]    |
| PyPI package      | [iac-scan-runner]    |
| Documentation     | [docs]               |

## Table of Contents
  - [Description](#purpose-and-description)
  - [Running](#running)
      - [Run with Docker](#run-with-docker)
      - [Run from CLI](#run-from-cli)
      - [Run from source](#run-from-source)

## Purpose and description
The **IaC Scan Runner** is a REST API service used to scan IaC (Infrastructure as Code) package and perform various 
code checks in order to find possible vulnerabilities and improvements.
Explore the [docs] for more info.

## Running
This section explains how to run the REST API.

### Run with Docker
You can run the REST API using a public [xscanner/runner] Docker image as follows:

```console
# run IaC Scan Runner REST API in a Docker container and 
# navigate to localhost:8080/swagger or localhost:8080/redoc
$ docker run --name iac-scan-runner -p 8080:80 xscanner/runner
```

Or you can build the image locally and run it as follows:

```console
# build Docker container (it will take some time) 
$ docker build -t iac-scan-runner .
# run IaC Scan Runner REST API in a Docker container and 
# navigate to localhost:8080/swagger or localhost:8080/redoc
$ docker run --name iac-scan-runner -p 8080:80 iac-scan-runner
```

### Run from CLI
To run using the IaC Scan Runner CLI:

```console
# install the CLI
$ python3 -m venv .venv && . .venv/bin/activate
(.venv) $ pip install iac-scan-runner
# print OpenAPI specification
(.venv) $ iac-scan-runner openapi
# install prerequisites
(.venv) $ iac-scan-runner install
# run IaC Scan Runner REST API
(.venv) $ iac-scan-runner run
```

### Run from source
To run locally from source:

```console
# install prerequisites
$ python3 -m venv .venv && . .venv/bin/activate
(.venv) $ pip install -r requirements.txt
(.venv) $ ./install-checks.sh
# run IaC Scan Runner REST API (add --reload flag to apply code changes on the way)
(.venv) $ uvicorn src.iac_scan_runner.api:app
```

[xscanner/runner]: https://hub.docker.com/r/xscanner/runner
[iac-scan-runner]: https://pypi.org/project/iac-scan-runner/
[Documentation]: https://xlab-si.github.io/iac-scanner-docs/02-runner.html
[docs]: https://xlab-si.github.io/iac-scanner-docs/02-runner.html
