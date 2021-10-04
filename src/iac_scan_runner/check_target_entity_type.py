from enum import Enum


class CheckTargetEntityType(str, Enum):
    iac = 'IaC'
    component = 'component'
    all = "IaC and component"
