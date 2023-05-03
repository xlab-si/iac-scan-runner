# instantiate runner for scanning IaC
import os

from fastapi import FastAPI

from iac_scan_runner.functionality.scan_runner import ScanRunner

scan_runner = ScanRunner()

tags_metadata = [
    {
        "name": "Checks",
        "description": "***Depricated***",
    },
    {
        "name": "Projects",
    },
]

app = FastAPI(
    docs_url="/swagger",
    title="IaC Scan Runner REST API",
    description="Service that scans your Infrastructure as Code for common vulnerabilities",
    version="0.4.0",
    root_path=os.getenv('ROOT_PATH', "/"),
    openapi_tags=tags_metadata
)
