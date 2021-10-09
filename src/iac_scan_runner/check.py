from abc import ABC, abstractmethod
from typing import Optional

from iac_scan_runner.check_output import CheckOutput
from iac_scan_runner.check_target_entity_type import CheckTargetEntityType
from pydantic import SecretStr


class Check(ABC):
    def __init__(self, name: str, description: Optional[str] = "",
                 target_entity_type: Optional[CheckTargetEntityType] = None):
        """Initialize new IaC check

         :param name: Name of the check
         :param description: Check description
        """
        self.name = name
        self.description = description
        self.target_entity_type = target_entity_type
        self.enabled = True
        self.configured = True
        self._config_filename = None

    def configure(self, config_filename: Optional[str], secret: Optional[SecretStr]):
        """Initiate check configuration (override this method if configuration is needed)

         :param config_filename: Name of the check configuration file
         :param secret: Secret needed for configuration (e.g. API key, token, password etc.)
        """
        pass

    @abstractmethod
    def run(self, directory: str) -> CheckOutput:
        """Initiate check run (this method has to be implemented for every subclass)

         :param directory: Target directory where the check will be executed
        """
        pass
