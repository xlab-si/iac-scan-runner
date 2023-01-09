from typing import Optional

from fastapi import File, Form, UploadFile
from pydantic import BaseModel, SecretStr


class CheckConfigurationModel(BaseModel):
    """
    Check configuration model
    """

    config_file: UploadFile
    secret: Optional[SecretStr]

    @classmethod
    def as_form(cls, config_file: Optional[UploadFile] = File(None, description='Check configuration file'),
                secret: Optional[SecretStr] = Form(None, description='Secret needed for configuration '
                                                                     '(e.g., ''API key, token, '
                                                                     'password, cloud credentials, '
                                                                     'etc.)')):
        """
        Converts model to form_data structure for FastAPI

        :param config_file: configuration file
        :param secret: secret
        """

        return cls(config_file=config_file, secret=secret)
