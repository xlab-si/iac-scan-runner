from typing import Optional, Union

from fastapi import APIRouter
from fastapi import status, Depends
from fastapi.responses import JSONResponse, HTMLResponse

from iac_scan_runner.enums.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.enums.scan_response_type import ScanResponseType
from iac_scan_runner.functionality.project_config import ProjectConfig
from iac_scan_runner.functionality.results_persistence import ResultsPersistence
from iac_scan_runner.functionality.scan_project import ScanProject
from iac_scan_runner.model.ConfigureCheck import CheckConfigurationModel
from iac_scan_runner.model.Scan import ScanModel
from iac_scan_runner.object_store import scan_runner

router = APIRouter(tags=["Project"], prefix="/project")


@router.post("", summary="Generate new scan project for given user as creator",
             responses={200: {}, 400: {"model": str}})
async def post_new_project(creator_id: str) -> JSONResponse:
    """
    Create a new project which might contain multiple scan runs
    \f
    :param creator_id: Identifier of a user who created project
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        scan_project = ScanProject()

        pid = scan_project.new_project(creator_id, "")

        return JSONResponse(status_code=status.HTTP_200_OK, content=pid)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post("/configuration/bind", summary="Assign configuration to the given scan project",
             responses={200: {}, 400: {"model": str}})
async def set_project_config(project_id: str, config_id: str) -> JSONResponse:
    """
    Assign configuration by its id to a scan project
    \f
    :param project_id: Identifier of a previously stored scan project
    :param config_id: Identifier of a previously stored configuration
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        scan_project = ScanProject()

        scan_project.set_config(project_id, config_id)

        return JSONResponse(status_code=status.HTTP_200_OK, content=f"New config assigned to project: {project_id}")
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post("/configuration", summary="Create a new scan project configuration",
             responses={200: {}, 400: {"model": str}})
async def post_new_config(creator_id: str) -> JSONResponse:
    """
    Create a new scan project configuration which can be assigned to a project
    \f
    :param creator_id: Identifier of a user who created configuration
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        project_config = ProjectConfig()
        cid = project_config.new_config(creator_id, None)

        return JSONResponse(status_code=status.HTTP_200_OK, content=cid)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post("/configuration/parameters", summary="Set the parameters for configuration by given id",
             responses={200: {}, 400: {"model": str}})
async def set_config_params(config_id: str, parameters: str) -> JSONResponse:
    """
    Assign configuration parameters to scan project configuration
    \f
    :param parameters: Dictionary of tool-specific parameter strings, such as tokens
    :param config_id: Identifier of a previously stored configuration
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        project_config = ProjectConfig()
        parameters_dict = eval(parameters)
        project_config.set_parameters(config_id, parameters_dict)

        return JSONResponse(status_code=status.HTTP_200_OK, content=f"Config modified: {config_id}")
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("", summary="Retrieve list of projects for given user or all projects if no user provided",
            responses={200: {}, 400: {"model": str}})
async def get_all_projects(creator_id: Optional[str] = None) -> JSONResponse:
    """
    Retrieve a list of projects by given user creator
    \f
    :param creator_id: Identifier of a user who created project
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        scan_persistence = ScanProject()
        if creator_id:
            result = scan_persistence.all_projects_by_user(creator_id)
        else:
            result = scan_persistence.all_projects()
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.post("/scan", summary="Initiate IaC scan", responses={200: {}, 400: {"model": str}})
async def post_scan(form_data: ScanModel = Depends(ScanModel.as_form),
                    project_id: Optional[str] = None,
                    scan_response_type: ScanResponseType = ScanResponseType.json) -> Union[JSONResponse, HTMLResponse]:
    """
    Run IaC scan
    \f
    :param form_data: Form data model
    :param project_id: Identifier of a project_id to which where scan run belongs
    :param scan_response_type: Scan response type (JSON or HTML)
    :return: JSONResponse or HTMLResponse object (with status code 200 or 400)
    """
    try:
        if not form_data.checks or form_data.checks == ['']:
            checks = []
        else:
            checks = list(set(form_data.checks[0].split(",")))

        if not project_id:
            project_id = ""

        scan_output = scan_runner.scan_iac(form_data.iac, project_id, checks, scan_response_type)
        if scan_response_type == ScanResponseType.html:
            return HTMLResponse(status_code=status.HTTP_200_OK, content=scan_output)
        return JSONResponse(status_code=status.HTTP_200_OK, content=scan_output)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("/results", summary="Retrieve particular scan result by given uuid",
            responses={200: {}, 400: {"model": str}})
async def get_scan_result(uuid: Optional[str], project_id: Optional[str]) -> JSONResponse:
    """
    Retrieve a particular scan result
    \f
    :param uuid: Identifier of a saved scan record
    :param project_id: Identifier of a project
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        results_persistence = ResultsPersistence()
        if uuid and project_id:
            result = results_persistence.all_scans_by_project(project_id)
        if uuid and not project_id:
            result = results_persistence.show_result(uuid)
        else:
            result = results_persistence.show_all()
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.delete("/results/{uuid}", summary="Delete particular scan result by given uuid",
               responses={200: {}, 400: {"model": str}})
async def delete_scan_result(uuid: str) -> JSONResponse:
    """
    Delete a particular scan result
    \f
    :param uuid: Identifier of a saved scan record
    :return: JSONResponse object (with status code 200 or 400)
    """
    try:
        results_persistence = ResultsPersistence()

        result = results_persistence.show_result(uuid)
        if not result is None:
            results_persistence.delete_result(uuid)
            return JSONResponse(status_code=status.HTTP_200_OK, content=f"Deleted scan result {uuid}")
        else:
            return JSONResponse(status_code=status.HTTP_200_OK, content=f"No such scan result {uuid}")
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))


@router.get("/checks", summary="Retrieve and filter checks", responses={200: {}, 400: {"model": str}})
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


@router.put("/checks/{check_name}/enable", summary="Enable check for running", responses={200: {}, 400: {"model": str}})
async def put_enable_checks(check_name: str, project_id: Optional[str]) -> JSONResponse:
    """
    Enable check for running
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
    Disable check for running
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


@router.post("/checks/scan", summary="Initiate IaC scan", responses={200: {}, 400: {"model": str}})
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
