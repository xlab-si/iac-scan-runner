from typing import Optional

from fastapi import APIRouter
from fastapi import File, Form, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import SecretStr

from iac_scan_runner.enum.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.scan_runner import ScanRunner

router = APIRouter(tags=["Checks"])

# instantiate runner for scanning IaC
scan_runner = ScanRunner()
scan_runner.init_checks()


@router.get("/checks", summary="Retrieve and filter checks", responses={200: {}, 400: {"model": str}})
async def get_checks(keyword: Optional[str] = None, enabled: Optional[bool] = None, configured: Optional[bool] = None,
                     target_entity_type: Optional[CheckTargetEntityType] = None) -> JSONResponse:
    """
    Retrieve and filter checks (GET method)
    \f
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


@router.put("/checks/{check_name}/enable", summary="Enable check for running", responses={200: {}, 400: {"model": str}})
async def put_enable_checks(check_name: str, project_id: Optional[str]) -> JSONResponse:
    """
    Enable check for running (PUT method)
    \f
    :param check_name: Unique name of check to be enabled
    :param project_id: Identifier of a project
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        return JSONResponse(status_code=status.HTTP_200_OK, content=scan_runner.enable_check(check_name, project_id))
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.put("/checks/{check_name}/disable", summary="Disable check for running",
            responses={200: {}, 400: {"model": str}})
async def put_disable_checks(check_name: str, project_id: Optional[str]) -> JSONResponse:
    """
    Disable check for running (PUT method)
    \f
    :param check_name: Unique name of check to be disabled
    :param project_id: Identifier of a project
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        return JSONResponse(status_code=status.HTTP_200_OK, content=scan_runner.disable_check(check_name, project_id))
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.put("/checks/{check_name}/configure", summary="Configure check for running",
            responses={200: {}, 400: {"model": str}})
async def put_configure_check(check_name: str,
                              config_file: Optional[UploadFile] = File(None, description='Check configuration file'),
                              secret: Optional[SecretStr] = Form(None, description='Secret needed for configuration '
                                                                                   '(e.g., ''API key, token, '
                                                                                   'password, cloud credentials, '
                                                                                   'etc.)')) -> JSONResponse:
    """
    Configure check for running (PUT method)
    \f
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
