import functools
import io
import os
from typing import Optional, List

import yaml
from content_size_limit_asgi import ContentSizeLimitMiddleware
from fastapi import FastAPI, File, Form, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi.responses import Response
from iac_scan_runner.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.scan_runner import ScanRunner
from pydantic import SecretStr

app = FastAPI(
    docs_url="/swagger",
    title="IaC Scan Runner REST API",
    description="Service that checks your IaC for issues and vulnerabilities",
    version="0.1.1",
    root_path=os.getenv('ROOT_PATH', "/")
)

# limit maximum size for file uploads to 50 MB
app.add_middleware(ContentSizeLimitMiddleware, max_content_size=52428800)
# instantiate runner for scanning IaC
scan_runner = ScanRunner()
scan_runner.init_checks()


def openapi_yaml() -> str:
    openapi_json = app.openapi()
    yaml_str = io.StringIO()
    yaml.dump(openapi_json, yaml_str)
    return yaml_str.getvalue()


@app.get('/openapi.yml', include_in_schema=False)
@functools.lru_cache()
def get_openapi_yml() -> Response:
    return Response(openapi_yaml(), media_type='text/yml')


@app.get('/openapi.yaml', include_in_schema=False)
@functools.lru_cache()
def get_openapi_yaml() -> Response:
    return Response(openapi_yaml(), media_type='text/yaml')


@app.get("/checks", summary="Retrieve and filter checks", responses={200: {}, 400: {"model": str}})
async def get_checks(keyword: Optional[str] = None, enabled: Optional[bool] = None, configured: Optional[bool] = None,
                     target_entity_type: Optional[CheckTargetEntityType] = None):
    try:
        filtered_checks = scan_runner.iac_checks.values()
        if keyword is not None:
            filtered_checks = filter(
                lambda check: keyword.lower() in check.name.lower() or keyword.lower() in check.description.lower(),
                filtered_checks)
        if enabled is not None:
            filtered_checks = filter(lambda check: check.enabled == enabled, filtered_checks)
        if configured is not None:
            filtered_checks = filter(lambda check: check.configured == configured, filtered_checks)
        if target_entity_type is not None:
            filtered_checks = filter(lambda check: check.target_entity_type == target_entity_type, filtered_checks)
        checks = map(lambda check: {"name": check.name, "description": check.description, "enabled": check.enabled,
                                    "configured": check.configured, "target_entity_type": check.target_entity_type},
                     filtered_checks)
        return JSONResponse(status_code=status.HTTP_200_OK, content=list(checks))
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@app.patch("/checks/{check_name}/enable", summary="Enable check for running", responses={200: {}, 400: {"model": str}})
async def patch_enable_checks(check_name: str):
    try:
        return JSONResponse(status_code=status.HTTP_200_OK, content=scan_runner.enable_check(check_name))
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@app.patch("/checks/{check_name}/disable", summary="Disable check for running",
           responses={200: {}, 400: {"model": str}})
async def patch_disable_checks(check_name: str):
    try:
        return JSONResponse(status_code=status.HTTP_200_OK, content=scan_runner.disable_check(check_name))
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@app.patch("/checks/{check_name}/configure", summary="Configure check",
           responses={200: {}, 400: {"model": str}})
async def patch_configure_check(check_name: str,
                                config_file: Optional[UploadFile] = File(None, description='Check configuration file'),
                                secret: Optional[SecretStr] = Form(None,
                                                                   description='Secret needed for configuration '
                                                                               '(e.g. API key, token, password etc.)')):
    try:
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content=scan_runner.configure_check(check_name, config_file, secret))
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@app.post("/scan", summary="Initiate IaC scan", responses={200: {}, 400: {"model": str}})
async def post_scan(iac: UploadFile = File(..., description='IaC file (zip or tar compressed) that will be scanned'),
                    checks: Optional[List[str]] = Form(None,
                                                       description='List of selected checks to be executed on IaC')):
    try:
        if not checks or checks == ['']:
            checks = []
        else:
            checks = list(set(checks[0].split(",")))
        check_output = scan_runner.scan_iac(iac, checks)
        return JSONResponse(status_code=status.HTTP_200_OK, content=check_output)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))
