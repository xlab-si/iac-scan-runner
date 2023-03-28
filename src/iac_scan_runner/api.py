import uvicorn
from content_size_limit_asgi import ContentSizeLimitMiddleware

from iac_scan_runner.object_store import app
from iac_scan_runner.object_store import scan_runner
from iac_scan_runner.routers import project, checks, openapi

# limit maximum size for file uploads to 50 MB
app.add_middleware(ContentSizeLimitMiddleware, max_content_size=52428800)

# initialize checks
scan_runner.init_checks()
scan_runner.init_checklist()

# Include routes
app.include_router(openapi.router)
app.include_router(checks.router)
app.include_router(project.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
