from typing import Optional, Union

from fastapi import APIRouter
from fastapi import status, Depends
from fastapi.responses import JSONResponse, HTMLResponse

from iac_scan_runner.enums.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.enums.scan_response_type import ScanResponseType
from iac_scan_runner.model.ConfigureCheck import CheckConfigurationModel
from iac_scan_runner.model.Scan import ScanModel
from iac_scan_runner.object_store import scan_runner

router = APIRouter(tags=["Checks"])


@router.get("/default/checks", summary="Retrieve and filter checks", responses={200: {}, 400: {"model": str}})
async def get_checks(keyword: Optional[str] = None, enabled: Optional[bool] = None, configured: Optional[bool] = None,
                     target_entity_type: Optional[CheckTargetEntityType] = None) -> JSONResponse:
    """
    Retrieve and filter checks
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


@router.put("/default/checks/{check_name}/enable", summary="Enable check for running", responses={200: {}, 400: {"model": str}})
async def put_enable_checks(check_name: str) -> JSONResponse:
    """
    Enable check for running
    \f
    :param check_name: Unique name of check to be enabled
    :param project_id: Identifier of a project
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        return JSONResponse(status_code=status.HTTP_200_OK, content=scan_runner.enable_check(check_name, ""))
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.put("/default/checks/{check_name}/disable", summary="Disable check for running",
            responses={200: {}, 400: {"model": str}})
async def put_disable_checks(check_name: str) -> JSONResponse:
    """
    Disable check for running
    \f
    :param check_name: Unique name of check to be disabled
    :param project_id: Identifier of a project
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        return JSONResponse(status_code=status.HTTP_200_OK, content=scan_runner.disable_check(check_name, ""))
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.put("/default/checks/{check_name}/configure", summary="Configure check for running",
            responses={200: {}, 400: {"model": str}})
async def put_configure_check(check_name: str,
                              form_data: CheckConfigurationModel = Depends(
                                  CheckConfigurationModel.as_form)) -> JSONResponse:
    """
    Configure check for running
    \f
    :param check_name: Unique name of check to be configured
    :param form_data: Form data model
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content=scan_runner.configure_check(check_name, form_data.config_file, form_data.secret))
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post("/default/scan", summary="Initiate IaC scan", responses={200: {}, 400: {"model": str}})
async def post_scan(form_data: ScanModel = Depends(ScanModel.as_form),
                    scan_response_type: ScanResponseType = ScanResponseType.json) -> Union[JSONResponse, HTMLResponse]:
    """
    Run IaC scan
    \f
    :param form_data: Form data model
    :param scan_response_type: Scan response type (JSON or HTML)
    :return: JSONResponse or HTMLResponse object (with status code 200 or 400)
    """
    try:
        if not form_data.checks or form_data.checks == ['']:
            checks = []
        else:
            checks = list(set(form_data.checks[0].split(",")))

        scan_output = scan_runner.scan_iac(form_data.iac, "", checks, scan_response_type)
        if scan_response_type == ScanResponseType.html:
            return HTMLResponse(status_code=status.HTTP_200_OK, content=scan_output)
        return JSONResponse(status_code=status.HTTP_200_OK, content=scan_output)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))
