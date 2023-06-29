from enum import Enum


class CheckTargetEntityType(str, Enum):
    """Entity target type class object."""

    IAC = "IaC"
    COMPONENT = "component"
    ALL = "IaC and component"
