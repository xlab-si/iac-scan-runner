from enum import Enum


class ScanResponseType(str, Enum):
    """Scan response class object."""

    JSON = 'json'
    HTML = 'html'
