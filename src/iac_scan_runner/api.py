import functools
import io
import os
from typing import Optional, List, Union

import yaml
from content_size_limit_asgi import ContentSizeLimitMiddleware
from fastapi import FastAPI, File, Form, UploadFile, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.responses import Response
from iac_scan_runner.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.scan_response_type import ScanResponseType
from iac_scan_runner.scan_runner import ScanRunner
from pydantic import SecretStr

# create an API instance
app = FastAPI(
    docs_url="/swagger",
    title="IaC Scan Runner REST API",
    description="Service that scans your Infrastructure as Code for common vulnerabilities",
    version="0.1.6",
    root_path=os.getenv('ROOT_PATH', "/")
)

# limit maximum size for file uploads to 50 MB
app.add_middleware(ContentSizeLimitMiddleware, max_content_size=52428800)
# instantiate runner for scanning IaC
scan_runner = ScanRunner()
scan_runner.init_checks()


def openapi_yaml() -> str:
    """
    Return OpenAPI specification as YAML string
    :return: string with YAML
    """
    openapi_json = app.openapi()
    yaml_str = io.StringIO()
    yaml.dump(openapi_json, yaml_str)
    return yaml_str.getvalue()


@app.get('/openapi.yml', include_in_schema=False)
@functools.lru_cache()
def get_openapi_yml() -> Response:
    """
    GET OpenAPI specification in YAML format (.yml)
    :return: Response object
    """
    return Response(openapi_yaml(), media_type='text/yml')


@app.get('/openapi.yaml', include_in_schema=False)
@functools.lru_cache()
def get_openapi_yaml() -> Response:
    """
    GET OpenAPI specification in YAML format (.yaml)
    :return: Response object
    """
    return Response(openapi_yaml(), media_type='text/yaml')


@app.get("/checks", summary="Retrieve and filter checks", responses={200: {}, 400: {"model": str}})
async def get_checks(keyword: Optional[str] = None, enabled: Optional[bool] = None, configured: Optional[bool] = None,
                     target_entity_type: Optional[CheckTargetEntityType] = None) -> JSONResponse:
    """
    Retrieve and filter checks (GET method)
    :param keyword: substring for filtering
    :param enabled: bool saying whether check is enabled or disabled
    :param configured: bool saying whether check is configured or not
    :param target_entity_type: CheckTargetEntityType object - IaC, component or both
    :return: JSONResponse object (with status code 200 or 400)
    """
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


@app.put("/checks/{check_name}/enable", summary="Enable check for running", responses={200: {}, 400: {"model": str}})
async def put_enable_checks(check_name: str) -> JSONResponse:
    """
    Enable check for running (PUT method)
    :param check_name: Unique name of check to be enabled
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        return JSONResponse(status_code=status.HTTP_200_OK, content=scan_runner.enable_check(check_name))
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@app.put("/checks/{check_name}/disable", summary="Disable check for running",
         responses={200: {}, 400: {"model": str}})
async def put_disable_checks(check_name: str) -> JSONResponse:
    """
    Disable check for running (PUT method)
    :param check_name: Unique name of check to be disabled
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        return JSONResponse(status_code=status.HTTP_200_OK, content=scan_runner.disable_check(check_name))
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@app.put("/checks/{check_name}/configure", summary="Configure check for running",
         responses={200: {}, 400: {"model": str}})
async def put_configure_check(check_name: str,
                              config_file: Optional[UploadFile] = File(None, description='Check configuration file'),
                              secret: Optional[SecretStr] = Form(None, description='Secret needed for configuration '
                                                                                   '(e.g., ''API key, token, '
                                                                                   'password, cloud credentials, '
                                                                                   'etc.)')) -> JSONResponse:
    """
    Configure check for running (PUT method)
    :param check_name: Unique name of check to be configured
    :param config_file: Check configuration file
    :param secret: Secret needed for configuration (e.g., API key, token, password, cloud credentials, etc.)
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content=scan_runner.configure_check(check_name, config_file, secret))
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@app.post("/scan", summary="Initiate IaC scan", responses={200: {}, 400: {"model": str}})
async def post_scan(iac: UploadFile = File(..., description='IaC file (zip or tar compressed) that will be scanned'),
                    checks: Optional[List[str]] = Form(None,
                                                       description='List of selected checks (by their unique names) to '
                                                                   'be executed on IaC'),
                    scan_response_type: ScanResponseType = ScanResponseType.json) -> Union[JSONResponse, HTMLResponse]:
    """
    Run IaC scan (POST method)
    :param iac: IaC file (zip or tar compressed) that will be scanned'
    :param checks: List of selected checks to be executed on IaC
    :param scan_response_type: Scan response type (JSON or HTML)
    :return: JSONResponse or HTMLResponse object (with status code 200 or 400)
    """
    try:
        if not checks or checks == ['']:
            checks = []
        else:
            checks = list(set(checks[0].split(",")))
        scan_output = scan_runner.scan_iac(iac, checks, scan_response_type)
        if scan_response_type == ScanResponseType.html:
            return HTMLResponse(status_code=status.HTTP_200_OK, content=scan_output)
        return JSONResponse(status_code=status.HTTP_200_OK, content=scan_output)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))
