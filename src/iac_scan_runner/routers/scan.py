from typing import Optional, List, Union

from fastapi import APIRouter
from fastapi import File, Form, UploadFile, status
from fastapi.responses import JSONResponse, HTMLResponse

from iac_scan_runner.enums.scan_response_type import ScanResponseType
from iac_scan_runner.object_store import scan_runner
from iac_scan_runner.functionality.results_persistence import ResultsPersistence

router = APIRouter(tags=["Scan"], prefix="/scan")


@router.post("", summary="Initiate IaC scan", responses={200: {}, 400: {"model": str}})
async def post_scan(iac: UploadFile = File(..., description='IaC file (zip or tar compressed) that will be scanned'),
                    project_id: Optional[str] = None,
                    checks: Optional[List[str]] = Form(None,
                                                       description='List of selected checks (by their unique names) to '
                                                                   'be executed on IaC'),
                    scan_response_type: ScanResponseType = ScanResponseType.json) -> Union[JSONResponse, HTMLResponse]:
    """
    Run IaC scan
    \f
    :param iac: IaC file (zip or tar compressed) that will be scanned
    :param project_id: Identifier of a project_id to which where scan run belongs
    :param checks: List of selected checks to be executed on IaC
    :param scan_response_type: Scan response type (JSON or HTML)
    :return: JSONResponse or HTMLResponse object (with status code 200 or 400)
    """
    try:
        if not checks or checks == ['']:
            checks = []
        else:
            checks = list(set(checks[0].split(",")))

        if not project_id:
            project_id = ""

        scan_output = scan_runner.scan_iac(iac, project_id, checks, scan_response_type)
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
