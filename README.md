# IaC Scan Runner

Service that scans your Infrastructure as Code for common vulnerabilities.

[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/xlab-si/iac-scan-runner/ci_cd.yml?branch=main)](https://github.com/xlab-si/iac-scan-runner/actions)
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
# Export env variables 
export MONGODB_CONNECTION_STRING=mongodb://localhost:27017
export SCAN_PERSISTENCE=enabled
export USER_MANAGEMENT=enabled

# Setup MongoDB
$ docker run --name mongodb -p 27017:27017 mongo

# install prerequisites
$ python3 -m venv .venv && . .venv/bin/activate
(.venv) $ pip install -r requirements.txt
(.venv) $ ./install-checks.sh
# run IaC Scan Runner REST API (add --reload flag to apply code changes on the way)
(.venv) $ cd src
(.venv) $ uvicorn iac_scan_runner.api:app
```

## Usage and examples

This part will show one of the possible deployments and short examples on how to use API calls.

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
  'http://0.0.0.0/project?creator_id=test' \
  -H 'accept: application/json' \
  -d ''
```

project id will be returned to us. For this example project id is 1e7b2a91-2896-40fd-8d53-83db56088026.


2. For example, let say we want to initiate all check expect ansible-lint. Let's disable it.

```console
curl -X 'PUT' \
  'http://0.0.0.0:8000/projects/1e7b2a91-2896-40fd-8d53-83db56088026/checks/ansible-lint/disable' \
  -H 'accept: application/json'
```

3. Now when project is configured, we can simply choose files that we want to scan and zip them. For IaC-Scan-Runner to
   work files are expected to be a compressed archives (usually zip files). In this case response type will be json
   , but it is possible to change it to html.Please change YOUR.zip to path of your file.

```console
curl -X 'POST' \
  'http://0.0.0.0:8000/projects/1e7b2a91-2896-40fd-8d53-83db56088026/scan?scan_response_type=json' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'iac=@YOUR.zip;type=application/zip'
```

That is it.

### Extending the scan workflow with new check tools

At certain point, it might be required to include new check tools within the scan workflow, with aim to provide wider coverage of IaC standards and project types. Therefore, in this subsection, a sequence of required steps for that purpose is identified and described. However, the steps have to be performed manually as it will be described, but it is planned to automatize this procedure in future via API and provide user-friendly interface that will aid the user while importing new tools that will become part of the available catalogue that makes the scan workflow.  Figure 16 depicts the required steps which have to be taken in order to extend the scan workflow with a new tool.

Step 1 – Adding tool-specific class to checks directory
First, it is required to add a new tool-specific Python class to the checks directory inside IaC Scan Runner’s source code:
iac-scan-runner/src/iac_scan_runner/checks/new_tool.py  
The class of a new tool inherits the existing Check class, which provides generalization of scan workflow tools. Moreover, it is necessary to provide implementation of the following methods:
   1) def configure(self, config_filename: Optional[str], secret: Optional[SecretStr])
   2) def run(self, directory: str)
While the first one aims to provide the necessary tool-specific parameters in order to set it up (such as passwords, client ids and tokens), another one specifies how the tool itself is invoked via API or CLI and its raw output returned.

Step 2 – Adding the check tool class instance within ScanRunner constructor
Once the new class derived from Check is added to the IaC Scan Runner’s source code, it is also required to modify the source code of its main class, called ScanRunner. When it comes to modifications of this class, it is required first to import the tool-specific class, create a new check tool-specific class instance and adding it to the dictionary of IaC checks inside def init_checks(self).
A.	Importing the check tool class
from iac_scan_runner.checks.tfsec import TfsecCheck
B.	Creating new instance of check tool object inside init_checks
"""Initiate predefined check objects"""
        new_tool = NewToolCheck() 
C.	Adding it to self.iac_checks dictionary inside init_checks
```console
    self.iac_checks = {
        new_tool.name: new_tool,
        …
    }
```

Step 3 – Adding the check tool to the compatibility matrix inside Compatibility class
On the other side, inside file src/iac_scan_runner/compatibility.py, the dictionary which represents compatibility matrix should be extended as well. There are two possible cases: a) new file type should be added as a key, together with list of relevant tools as value b) new tool should be added to the compatibility list for the existing file type.
```console
    compatibility_matrix = {
        "new_type": ["new_tool_1", "new_tool_2"],
        …
        "old_typeK": ["tool_1", …  "tool_N", "new_tool_3"]
    }
```

Step 4 – Providing the support for result summarization
Finally, the last step in sequence of required modifications for scan workflow extension is to modify class ResultsSummary (src/iac_scan_runner/results_summary.py). Precisely, it is required to append a part of the code to its method summarize_outcome that will look for specific strings which are tool-specific and can be used to identify whether the check passed or failed. Inside the loop that traverses the compatible checks, for each new tool the following structure of if-else should be included:
```console
        if check == "new_tool":
            if outcome.find("Check pass string") > -1:
                self.outcomes[check]["status"] = "Passed"
                return "Passed"
            else:
                self.outcomes[check]["status"] = "Problems"
                return "Problems"
``` 

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
