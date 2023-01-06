import iac_scan_runner.vars as env
from iac_scan_runner.interface.check import Check
from iac_scan_runner.functionality.check_output import CheckOutput
from iac_scan_runner.enums.check_target_entity_type import CheckTargetEntityType
from iac_scan_runner.utils import run_command


class OperaToscaParserCheck(Check):
    def __init__(self):
        super().__init__("opera-tosca-parser", "xOpera TOSCA parser can validate TOSCA YAML templates and CSARs",
                         CheckTargetEntityType.iac)

    def run(self, directory: str) -> CheckOutput:
        return run_command(f'{env.OPERA_TOSCA_PARSER_CHECK_PATH} parse .', directory)
