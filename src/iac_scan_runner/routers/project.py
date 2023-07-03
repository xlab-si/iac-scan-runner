import json
import os
from typing import Optional, Union

from fastapi import APIRouter
from fastapi import status, Depends
from fastapi.responses import JSONResponse, HTMLResponse

from iac_scan_runner.enums.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.enums.scan_response_type import ScanResponseType

from iac_scan_runner.functionality.results_persistence import ResultsPersistence
from iac_scan_runner.functionality.scan_project import ScanProject
from iac_scan_runner.model.ConfigureCheck import CheckConfigurationModel
from iac_scan_runner.model.Scan import ScanModel
from iac_scan_runner.object_store import scan_runner

router = APIRouter(tags=["Projects"], prefix="/projects")


@router.post("", summary="Generate new scan project for given user as creator",
             responses={200: {}, 400: {"model": str}})
async def post_new_project(creator_id: str) -> JSONResponse:
    """
    Create a new project which might contain multiple scan runs.

    \f
    :param creator_id: Identifier of a user who created project
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        connection_string = os.environ["MONGODB_CONNECTION_STRING"]
        scan_project = ScanProject(connection_string)
        scan_runner.init_checks()
        scan_runner.init_checklist()
        pid = scan_project.new_project(creator_id, "", scan_runner.project_checklist)

        return JSONResponse(status_code=status.HTTP_200_OK, content=pid)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post("/{project_id}/scan", summary="Initiate IaC scan", responses={200: {}, 400: {"model": str}})
async def post_scan(project_id: str, form_data: ScanModel = Depends(ScanModel.as_form),
                    scan_response_type: ScanResponseType = ScanResponseType.JSON) -> Union[JSONResponse, HTMLResponse]:
    """
    Run IaC scan.

    \f
    :param form_data: Form data model
    :param project_id: Identifier of a project_id to which where scan run belongs
    :param scan_response_type: Scan response type (JSON or HTML)
    :return: JSONResponse or HTMLResponse object (with status code 200 or 400)
    """
    try:
        scan_output = scan_runner.scan_iac(form_data.iac, project_id, [], scan_response_type)
        if scan_response_type == ScanResponseType.HTML:
            return HTMLResponse(status_code=status.HTTP_200_OK, content=scan_output)
        return JSONResponse(status_code=status.HTTP_200_OK, content=scan_output)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("/{project_id}/results", summary="Retrieve particular scan result by given uuid",
            responses={200: {}, 400: {"model": str}})
async def get_scan_result(uuid: Optional[str], project_id: Optional[str]) -> JSONResponse:
    """
    Retrieve a particular scan result.

    \f
    :param uuid: Identifier of a saved scan record
    :param project_id: Identifier of a project
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        connection_string = os.environ["MONGODB_CONNECTION_STRING"]
        results_persistence = ResultsPersistence(connection_string)
        result = results_persistence.get_scan_result(project_id, uuid)
        return JSONResponse(status_code=status.HTTP_200_OK, content=json.dumps(result))
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.delete("/results/{uuid}", summary="Delete particular scan result by given uuid")
async def delete_scan_result(uuid: str) -> JSONResponse:
    """
    Delete a particular scan result.

    \f
    :param uuid: Identifier of a saved scan record
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        connection_string = os.environ["MONGODB_CONNECTION_STRING"]
        results_persistence = ResultsPersistence(connection_string)
        results_persistence.delete_result(uuid)
        return JSONResponse(status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("/{project_id}/checks", summary="Retrieve and filter checks", responses={200: {}, 400: {"model": str}})
async def get_checks(project_id: str, keyword: Optional[str] = None, enabled: Optional[bool] = None,
                     configured: Optional[bool] = None,
                     target_entity_type: Optional[CheckTargetEntityType] = None) -> JSONResponse:
    """
    Retrieve and filter checks.

    \f
    :param project_id: Identifier of a project
    :param keyword: substring for filtering
    :param enabled: bool saying whether check is enabled or disabled
    :param configured: bool saying whether check is configured or not
    :param target_entity_type: CheckTargetEntityType object - IaC, component or both
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        filtered_checks = scan_runner.iac_checks.values()
        check_list = scan_runner.scan_project.get_project_check_list(project_id)
        scan_runner.set_scan_runner_check(check_list)
        if keyword is not None:
            filtered_checks = [
                check for check in filtered_checks
                if keyword.lower() in check.name.lower() + check.description.lower()
            ]
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


@router.put("/{project_id}/checks/{check_name}/enable",
            summary="Enable execution of particular check for a specific project",
            responses={200: {}, 400: {"model": str}})
async def put_enable_checks(check_name: str, project_id: Optional[str]) -> JSONResponse:
    """
    Enable execution of particular check for a specific project.

    \f
    :param check_name: Unique name of check to be enabled
    :param project_id: Identifier of a project
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        return JSONResponse(status_code=status.HTTP_200_OK, content=scan_runner.enable_check(check_name, project_id))
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.put("/{project_id}/checks/{check_name}/disable",
            summary="Disable execution of particular check for a specific project",
            responses={200: {}, 400: {"model": str}})
async def put_disable_checks(project_id: str, check_name: str) -> JSONResponse:
    """
    Disable execution of particular check for a specific project.

    \f
    :param check_name: Unique name of check to be disabled
    :param project_id: Identifier of a project
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        return JSONResponse(status_code=status.HTTP_200_OK, content=scan_runner.disable_check(check_name, project_id))
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.put("/{project_id}/checks/{check_name}/configure",
            summary="Configure execution of particular check for a specific project",
            responses={200: {}, 400: {"model": str}})
async def put_configure_check(project_id: str, check_name: str,
                              form_data: CheckConfigurationModel = Depends(
                                  CheckConfigurationModel.as_form)) -> JSONResponse:
    """
    Configure execution of particular check for a specific project.

    \f
    :param project_id: Identifier of a project
    :param check_name: Unique name of check to be configured
    :param form_data: Form data model
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content=scan_runner.configure_check(project_id, check_name, form_data.config_file,
                                                                form_data.secret))
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))
