# IaC Scan Runner

Service that scans your Infrastructure as Code for common vulnerabilities.

[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/xlab-si/iac-scan-runner/Build%20and%20publish?label=ci%2Fcd)](https://github.com/xlab-si/iac-scan-runner/actions)
[![Docker Image Version (latest by date)](https://img.shields.io/docker/v/xscanner/runner?color=blue&label=docker)](https://hub.docker.com/r/xscanner/runner)
[![PyPI](https://img.shields.io/pypi/v/iac-scan-runner)](https://pypi.org/project/iac-scan-runner/)
[![Test PyPI](https://img.shields.io/badge/test%20pypi-dev%20version-blueviolet)](https://test.pypi.org/project/iac-scan-runner/)

| Aspect        |     Information     |
|---------------|:-------------------:|
| Tool name     | **IaC Scan Runner** |
| Docker image  |  [xscanner/runner]  |
| PyPI package  |  [iac-scan-runner]  |
| Documentation |       [docs]        |
| Contact us    |  [xopera@xlab.si]   |

## Table of Contents

- [Description](#purpose-and-description)
- [Running](#running)
    - [Run with Docker](#run-with-docker)
    - [Run from CLI](#run-from-cli)
    - [Run from source](#run-from-source)
- [License](#license)
- [Contact](#contact)
- [Acknowledgement](#acknowledgement)

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

## Usage and examples

This part will show one of the posible deployments and short examples on how to use API calls.

Firstly we will clone the [iac scan runner] repository and run the API.

```console
$ git clone https://github.com/xlab-si/iac-scan-runner.git
$ docker compose up
```

After this is done you can use different API endpoints by calling localhost:8000.
You can also navigate to localhost:8000/swagger or localhost:8000/redoc and test all the API endpoints there.
In this example, we will use curl for calling API endpoints.

1. Lets create a project named test.

```console
curl -X 'POST' \
  'http://127.0.0.1:8000/project?creator_id=test' \
  -H 'accept: application/json' \
  -d ''
```

2. Now check if project is created by listing all existing projects.

```console
curl -X 'GET' \
  'http://127.0.0.1:8000/project' \
  -H 'accept: application/json'
```

3. For example, lets say that we only want to check if file has any git leaks want to check for potential security
   leaks in our terraform files. We need to enable git-leaks and tfsec scans.

```console
curl -X 'PUT' \
  'http://127.0.0.1:8000/checks/git-leaks/enable?project_id=df833571-55d0-4396-8d21-a0fa08b44a06' \
  -H 'accept: application/json'
```

```console
curl -X 'PUT' \
  'http://127.0.0.1:8000/checks/tfsec/enable?project_id=df833571-55d0-4396-8d21-a0fa08b44a06' \
  -H 'accept: application/json'
```

4. Now when project is configured, we can simply choose files that we want to scan and zip them. For IaC-Scan-Runner to
   work files are expected to be a compressed archives (usually zip files). In this case response type will be json
   , but it is possible to change it to html.

```console
curl -X 'POST' \
  'http://127.0.0.1:8000/scan?project_id=df833571-55d0-4396-8d21-a0fa08b44a06&scan_response_type=json' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'checks=' \
  -F 'iac=@example.zip;type=application/zip'
```

Same can be achieved by calling /scan endpoint and define check list.

```console
curl -X 'POST' \
  'http://127.0.0.1:8000/scan?scan_response_type=json' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'checks=tfsec,git-leaks' \
  -F 'iac=@example.zip;type=application/zip'
```

That is it.

## License

This work is licensed under the [Apache License 2.0].

## Contact

You can contact the xOpera team by sending an email to [xopera@xlab.si].

## Acknowledgement

This project has received funding from the European Union’s Horizon 2020 research and innovation programme under Grant
Agreement No. 101000162 ([PIACERE]).

[xscanner/runner]: https://hub.docker.com/r/xscanner/runner

[iac-scan-runner]: https://pypi.org/project/iac-scan-runner/

[Documentation]: https://xlab-si.github.io/iac-scanner-docs/02-runner.html

[docs]: https://xlab-si.github.io/iac-scanner-docs/02-runner.html

[xopera@xlab.si]: mailto:xopera@xlab.si

[Apache License 2.0]: https://www.apache.org/licenses/LICENSE-2.0

[PIACERE]: https://www.piacere-project.eu/

[iac scan runner]: https://github.com/xlab-si/iac-scan-runner