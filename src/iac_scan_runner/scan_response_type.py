from enum import Enum


class ScanResponseType(str, Enum):
    json = 'json'
    html = 'html'
