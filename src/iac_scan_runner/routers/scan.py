from typing import Optional, Union

from fastapi import APIRouter
from fastapi import status, Depends
from fastapi.responses import JSONResponse, HTMLResponse

from iac_scan_runner.enums.scan_response_type import ScanResponseType
from iac_scan_runner.functionality.results_persistence import ResultsPersistence
from iac_scan_runner.model.Scan import ScanModel
from iac_scan_runner.object_store import scan_runner

router = APIRouter(tags=["Scan"], prefix="/scan")


@router.post("", summary="Initiate IaC scan", responses={200: {}, 400: {"model": str}})
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
