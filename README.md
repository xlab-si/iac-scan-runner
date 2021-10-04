# IaC Scan Runner
The IaC Scan Runner is a REST API service used to scan IaC (Infrastructure as Code) package and perform various code 
checks in order to find possible errors and improvements.

## Table of Contents
  - [Running](#running)
  - [Available checks](#available-checks)

## Running
To run locally from source:

```bash
# install prerequisites
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
./install-checks.sh
# run IaC Scan Runner REST API (add --reload flag to apply code changes on the way)
uvicorn src.iac_scan_runner.api:app
```

## Available checks
The scanner currently supports the following checks:

1. [Ansible Lint](https://github.com/willthames/ansible-lint/)
