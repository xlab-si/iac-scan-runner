from typing import Optional, List

from fastapi import File, Form, UploadFile
from pydantic import BaseModel


class ScanModel(BaseModel):
    """
    Scan model
    """
    iac: UploadFile

    @classmethod
    def as_form(cls,
                iac: UploadFile = File(default=None,
                                       description='IaC file (zip or tar compressed) that will be scanned')):
        """
        Converts model to form_data structure for FastAPI

        :param iac: zip file of documents to be scanned
        """
        return cls(iac=iac)


class ScanModelDeprecated(BaseModel):
    """
    Deprecated Scan model
    """
    iac: UploadFile
    checks: Optional[List[str]]

    @classmethod
    def as_form(cls,
                checks: Optional[List[str]] = Form(None,
                                                   description='List of selected checks (by their unique names) to '
                                                               'be executed on IaC'),
                iac: UploadFile = File(default=None,
                                       description='IaC file (zip or tar compressed) that will be scanned')):
        """
        Converts model to form_data structure for FastAPI

        :param iac: zip file of documents to be scanned
        :param checks: List of checks wished to be performed
        """
        return cls(checks=checks, iac=iac)
