from enum import Enum


class CheckTargetEntityType(str, Enum):
    IAC = "IaC"
    COMPONENT = "component"
    ALL = "IaC and component"
