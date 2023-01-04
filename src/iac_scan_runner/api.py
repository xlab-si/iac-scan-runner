import os

from content_size_limit_asgi import ContentSizeLimitMiddleware
from fastapi import FastAPI

from iac_scan_runner.object_store import scan_runner
from iac_scan_runner.routers import scan, project, checks, openapi

# create an API instance
app = FastAPI(
    docs_url="/swagger",
    title="IaC Scan Runner REST API",
    description="Service that scans your Infrastructure as Code for common vulnerabilities",
    version="0.1.9",
    root_path=os.getenv('ROOT_PATH', "/")
)
# limit maximum size for file uploads to 50 MB
app.add_middleware(ContentSizeLimitMiddleware, max_content_size=52428800)

# initialize checks
scan_runner.init_checks()

# Include routes
app.include_router(openapi.router)
app.include_router(project.router)
app.include_router(scan.router)
app.include_router(checks.router)
