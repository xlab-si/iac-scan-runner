from typing import Optional

from fastapi import APIRouter
from fastapi import status
from fastapi.responses import JSONResponse

from iac_scan_runner.business_logic.project_config import ProjectConfig
from iac_scan_runner.business_logic.scan_project import ScanProject

router = APIRouter(tags=["Project"], prefix="/project")


@router.post("", summary="Generate new scan project for given user as creator",
             responses={200: {}, 400: {"model": str}})
async def post_new_project(creator_id: str) -> JSONResponse:
    """
    Create a new project which might contain multiple scan runs (POST method)
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
    Assign configuration by its id to a scan project (POST method)
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
    Create a new scan project configuration which can be assigned to a project (POST method)
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
    Assign configuration parameters to scan project configuration (POST method)
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
    Retrieve a list of projects by given user creator (GET method)
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
