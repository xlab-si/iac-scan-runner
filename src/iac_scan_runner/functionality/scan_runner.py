import json
import os
import time
import uuid
from os import remove
from shutil import rmtree
from typing import Optional, List, Union

from fastapi import UploadFile
from pydantic import SecretStr

import iac_scan_runner.vars as env
from iac_scan_runner.checks.ansible_lint import AnsibleLintCheck
from iac_scan_runner.checks.bandit import BanditCheck
from iac_scan_runner.checks.checkstyle import CheckStyle
from iac_scan_runner.checks.cloc import ClocCheck
from iac_scan_runner.checks.es_lint import ESLintCheck
from iac_scan_runner.checks.git_leaks import GitLeaksCheck
from iac_scan_runner.checks.git_secrets import GitSecretsCheck
from iac_scan_runner.checks.gixy import GixyCheck
from iac_scan_runner.checks.hadolint import HadolintCheck
from iac_scan_runner.checks.htmlhint import HtmlHintCheck
from iac_scan_runner.checks.markdown_lint import MarkdownLintCheck
from iac_scan_runner.checks.opera_tosca_parser import OperaToscaParserCheck
from iac_scan_runner.checks.pylint import PylintCheck
from iac_scan_runner.checks.pyup_safety import PyUpSafetyCheck
from iac_scan_runner.checks.shellcheck import ShellCheck
from iac_scan_runner.checks.snyk import SnykCheck
from iac_scan_runner.checks.sonar_scanner import SonarScannerCheck
from iac_scan_runner.checks.steampunk_scanner import SteampunkScannerCheck
from iac_scan_runner.checks.stylelint import StyleLintCheck
from iac_scan_runner.checks.terrascan import TerrascanCheck
from iac_scan_runner.checks.tflint import TFLintCheck
from iac_scan_runner.checks.tfsec import TfsecCheck
from iac_scan_runner.checks.ts_lint import TSLintCheck
from iac_scan_runner.checks.yamllint import YamlLintCheck
from iac_scan_runner.functionality.compatibility import Compatibility
from iac_scan_runner.functionality.project_config import ProjectConfig
from iac_scan_runner.functionality.results_persistence import ResultsPersistence
from iac_scan_runner.functionality.results_summary import ResultsSummary
from iac_scan_runner.functionality.scan_project import ScanProject
from iac_scan_runner.enums.scan_response_type import ScanResponseType
from iac_scan_runner.utils import (
    generate_random_pathname,
    unpack_archive_to_dir,
    write_string_to_file,
    file_to_string
)


class ScanRunner:
    def __init__(self):
        """Initialize new scan runner that can perform IaC scanning with multiple IaC checks"""
        self.iac_checks = {}
        self.iac_dir = None
        self.compatibility_matrix = Compatibility()
        self.results_summary = ResultsSummary()
        self.archive_name = ""

        self.parameters = dict()

        if os.environ.get("SCAN_PERSISTENCE") == "enabled":
            self.persistence_enabled = True
        else:
            self.persistence_enabled = False

        self.results_persistence = ResultsPersistence()
        self.scan_project = ScanProject()
        self.project_config = ProjectConfig()
        self.project_checklist = None

        if os.environ.get("USER_MANAGEMENT") == "enabled":
            self.users_enabled = True
        else:
            self.users_enabled = False

    def init_checks(self):
        """Initiate predefined check objects"""
        opera_tosca_parser = OperaToscaParserCheck()
        ansible_lint = AnsibleLintCheck()
        steampunk_scanner = SteampunkScannerCheck()
        tflint = TFLintCheck()
        tfsec = TfsecCheck()
        terrascan = TerrascanCheck()
        yamllint = YamlLintCheck()
        pylint = PylintCheck()
        bandit = BanditCheck()
        pyup_safety = PyUpSafetyCheck()
        git_leaks = GitLeaksCheck()
        git_secrets = GitSecretsCheck()
        markdown_lint = MarkdownLintCheck()
        hadolint = HadolintCheck()
        gixy = GixyCheck()
        shellcheck = ShellCheck()
        es_lint = ESLintCheck()
        ts_lint = TSLintCheck()
        htmlhint = HtmlHintCheck()
        stylelint = StyleLintCheck()
        cloc = ClocCheck()
        checkstyle = CheckStyle()
        snyk = SnykCheck()
        sonar_scanner = SonarScannerCheck()

        self.iac_checks = {
            opera_tosca_parser.name: opera_tosca_parser,
            ansible_lint.name: ansible_lint,
            steampunk_scanner.name: steampunk_scanner,
            tflint.name: tflint,
            tfsec.name: tfsec,
            terrascan.name: terrascan,
            yamllint.name: yamllint,
            pylint.name: pylint,
            bandit.name: bandit,
            pyup_safety.name: pyup_safety,
            git_leaks.name: git_leaks,
            git_secrets.name: git_secrets,
            markdown_lint.name: markdown_lint,
            hadolint.name: hadolint,
            gixy.name: gixy,
            shellcheck.name: shellcheck,
            es_lint.name: es_lint,
            ts_lint.name: ts_lint,
            htmlhint.name: htmlhint,
            stylelint.name: stylelint,
            cloc.name: cloc,
            checkstyle.name: checkstyle,
            snyk.name: snyk,
            sonar_scanner.name: sonar_scanner
        }

    def _init_iac_dir(self, iac_file: UploadFile):
        """
        Initiate new unique IaC directory for scanning
        :param iac_file: IaC file
        """
        try:
            iac_filename_local = generate_random_pathname(iac_file.filename)
            self.archive_name = iac_file.filename
            with open(iac_filename_local, "wb+") as iac_file_local:
                iac_file_local.write(iac_file.file.read())
                iac_file_local.close()
            self.iac_dir = unpack_archive_to_dir(iac_filename_local, None)
            remove(iac_filename_local)
        except Exception as e:
            raise Exception(f"Error when initializing IaC directory: {str(e)}.")

    def _cleanup_iac_dir(self):
        """Remove the created IaC directory"""
        try:
            rmtree(self.iac_dir, True)
        except Exception as e:
            raise Exception(f"Error when cleaning IaC directory: {str(e)}.")

    def _run_checks(self, selected_checks: Optional[List], project_id: str, scan_response_type: ScanResponseType) -> \
            Union[dict, str]:
        """
        Run the specified IaC checks
        :param selected_checks: List of selected checks to be executed on IaC
        :param scan_response_type: Scan response type (JSON or HTML)
        :return: Dict or string with output for running checks
        """
        start_time = time.time()
        random_uuid = str(uuid.uuid4())

        # TODO: Replace this hardcoded path with a parameter
        dir_name = "../outputs/logs/scan_run_" + random_uuid
        os.mkdir(dir_name)

        self.results_summary.outcomes = dict()
        self.compatibility_matrix.scanned_files = dict()
        compatible_checks = self.compatibility_matrix.get_all_compatible_checks(self.iac_dir)
        non_compatible_checks = []
        scan_output = {}

        if self.users_enabled:
            if project_id:
                project_temp = self.scan_project.load_project(project_id)
                if project_temp:
                    if len(project_temp["checklist"]) == 0:
                        self.project_checklist = None
                    else:
                        self.project_checklist = project_temp["checklist"]
                    config_temp = self.project_config.load_config(project_temp["active_config"])
                    if config_temp:
                        self.parameters = config_temp["parameters"]

        if selected_checks is not None and len(selected_checks) > 0 and self.project_checklist is None:
            for selected_check in selected_checks:
                check = self.iac_checks[selected_check]
                if check.enabled:
                    if selected_check in compatible_checks:
                        check_output = check.run(self.iac_dir)
                        scan_output[selected_check] = check_output.to_dict()
                        write_string_to_file(check.name, dir_name, scan_output[check.name]["output"])
                        self.results_summary.summarize_outcome(selected_check, scan_output[check.name]["output"],
                                                               self.compatibility_matrix.scanned_files,
                                                               Compatibility.compatibility_matrix)
                    else:
                        non_compatible_checks.append(check.name)
                        write_string_to_file(check.name, dir_name, "No files to scan")
                        self.results_summary.summarize_no_files(check.name)
            end_time = time.time()
            duration = end_time - start_time

            self.results_summary.set_result(random_uuid, self.archive_name, duration)

            if self.users_enabled:
                self.results_summary.outcomes["project_id"] = project_id

            self.results_summary.dump_outcomes(random_uuid)
            self.results_summary.generate_html_prioritized(random_uuid)

            if self.results_persistence.connection_problem is False and self.persistence_enabled is True:
                self.results_persistence.insert_result(self.results_summary.outcomes)

        if (selected_checks is None or len(selected_checks) == 0) and self.project_checklist is None:
            for iac_check in self.iac_checks.values():
                if iac_check.enabled:
                    if iac_check.name in compatible_checks:
                        check_output = iac_check.run(self.iac_dir)
                        scan_output[iac_check.name] = check_output.to_dict()
                        write_string_to_file(iac_check.name, dir_name, scan_output[iac_check.name]["output"])
                        self.results_summary.summarize_outcome(iac_check.name, scan_output[iac_check.name]["output"],
                                                               self.compatibility_matrix.scanned_files,
                                                               Compatibility.compatibility_matrix)
                    else:
                        non_compatible_checks.append(iac_check.name)
                        write_string_to_file(iac_check.name, dir_name, "No files to scan")
                        self.results_summary.summarize_no_files(iac_check.name)

            end_time = time.time()
            duration = end_time - start_time

            self.results_summary.set_result(random_uuid, self.archive_name, duration)

            if self.users_enabled:
                self.results_summary.outcomes["project_id"] = project_id

            self.results_summary.dump_outcomes(random_uuid)
            self.results_summary.generate_html_prioritized(random_uuid)

            if self.results_persistence.connection_problem is False and self.persistence_enabled is True:
                self.results_persistence.insert_result(self.results_summary.outcomes)

        if selected_checks and self.project_checklist:
            for selected_check in selected_checks:
                check = self.iac_checks[selected_check]
                if check.name in self.project_checklist:
                    if selected_check in compatible_checks:
                        check_output = check.run(self.iac_dir)
                        scan_output[selected_check] = check_output.to_dict()
                        write_string_to_file(check.name, dir_name, scan_output[check.name]["output"])
                        self.results_summary.summarize_outcome(selected_check, scan_output[check.name]["output"],
                                                               self.compatibility_matrix.scanned_files,
                                                               Compatibility.compatibility_matrix)
                    else:
                        non_compatible_checks.append(check.name)
                        write_string_to_file(check.name, dir_name, "No files to scan")
                        self.results_summary.summarize_no_files(check.name)
            end_time = time.time()
            duration = end_time - start_time

            self.results_summary.set_result(random_uuid, self.archive_name, duration)

            if self.users_enabled:
                self.results_summary.outcomes["project_id"] = project_id

            self.results_summary.dump_outcomes(random_uuid)
            self.results_summary.generate_html_prioritized(random_uuid)

            if self.results_persistence.connection_problem is False and self.persistence_enabled is True:
                self.results_persistence.insert_result(self.results_summary.outcomes)

        if (selected_checks is None or len(selected_checks) == 0) and self.project_checklist:
            for iac_check in self.iac_checks.values():
                if iac_check.name in self.project_checklist:
                    if iac_check.name in compatible_checks:
                        check_output = iac_check.run(self.iac_dir)
                        scan_output[iac_check.name] = check_output.to_dict()
                        write_string_to_file(iac_check.name, dir_name, scan_output[iac_check.name]["output"])
                        self.results_summary.summarize_outcome(iac_check.name, scan_output[iac_check.name]["output"],
                                                               self.compatibility_matrix.scanned_files,
                                                               Compatibility.compatibility_matrix)
                    else:
                        non_compatible_checks.append(iac_check.name)
                        write_string_to_file(iac_check.name, dir_name, "No files to scan")
                        self.results_summary.summarize_no_files(iac_check.name)

            end_time = time.time()
            duration = end_time - start_time

            self.results_summary.set_result(random_uuid, self.archive_name, duration)

            if self.users_enabled:
                self.results_summary.outcomes["project_id"] = project_id

            self.results_summary.dump_outcomes(random_uuid)
            self.results_summary.generate_html_prioritized(random_uuid)

            if self.results_persistence.connection_problem is False and self.persistence_enabled is True:
                self.results_persistence.insert_result(self.results_summary.outcomes)

                # TODO: Discuss the format of this output
        if scan_response_type == ScanResponseType.json:
            scan_output = json.loads(file_to_string(f"../outputs/json_dumps/{random_uuid}.json"))
        else:
            scan_output = file_to_string(f"../outputs/generated_html/{random_uuid}.html")

        return scan_output

    def enable_check(self, check_name: str, project_id: str) -> str:
        """
        Enables the specified check and makes it available to be used
        :param check_name: Name of the check
        :param project_id: Project identification
        :return: String with result for enabling check
        """
        if project_id and self.users_enabled:
            if check_name in self.iac_checks.keys():
                self.scan_project.add_check(project_id, check_name)
                self.iac_checks[check_name].enabled = True
                active_project = self.scan_project.load_project(project_id)
                enabled_checks = active_project["checklist"]
            else:
                raise Exception(f"Nonexistent check: {check_name}")
        else:
            if check_name in self.iac_checks.keys():
                check = self.iac_checks[check_name]
                if not check.enabled:
                    check.enabled = True
                    return f"Check: {check_name} is now enabled and available to use."
                else:
                    raise Exception(f"Check: {check_name} is already enabled.")
            else:
                raise Exception(f"Nonexistent check: {check_name}")

    def disable_check(self, check_name: str, project_id: str) -> str:
        """
        Disables the specified check and makes it unavailable to be used
        :param check_name: Name of the check
        :param project_id: Project identification
        :return: String with result for disabling check
        """
        if check_name not in self.iac_checks.keys():
            raise Exception(f"Nonexistent check: {check_name}")
        if project_id and self.users_enabled:
            self.scan_project.remove_check(project_id, check_name)
            self.iac_checks[check_name].enabled = False
            active_project = self.scan_project.load_project(project_id)
            enabled_checks = active_project["checklist"]
        else:
            if check_name in self.iac_checks.keys():
                check = self.iac_checks[check_name]
                if check.enabled:
                    check.enabled = False
                    return f"Check: {check_name} is now disabled and cannot be used."
                else:
                    raise Exception(f"Check: {check_name} is already disabled.")
            else:
                raise Exception(f"Nonexistent check: {check_name}")

    def configure_check(self, check_name: str, config_file: Optional[UploadFile], secret: Optional[SecretStr]) -> str:
        """
        Configures the selected check with the supplied optional configuration file or/and secret
        :param check_name: Name of the check
        :param config_file: Check configuration file
        :param secret: Secret needed for configuration (e.g. API key, token, password etc.)
        :return: String with check configuration output
        """
        if check_name in self.iac_checks.keys():
            check = self.iac_checks[check_name]
            if check.enabled:
                config_filename_local = None
                if config_file:
                    config_filename_local = generate_random_pathname("", "-" + config_file.filename)
                    with open(
                            f"{env.CONFIG_DIR}/{config_filename_local}", "wb+"
                    ) as config_file_local:
                        config_file_local.write(config_file.file.read())
                        config_file_local.close()
                check_output = check.configure(config_filename_local, secret)
                check.configured = True
                return check_output.output
            else:
                raise Exception(f'Check: {check_name} is disabled. You need to enable it first.')
        else:
            raise Exception(f'Nonexistent check: {check_name}')

    def scan_iac(
            self, iac_file: UploadFile, project_id: str, checks: List, scan_response_type: ScanResponseType
    ) -> Union[dict, str]:
        """
        Run IaC scanning process (initiate IaC dir, run checks and cleanup IaC dir)
        :param iac_file: IaC file that will be scanned
        :param project_id: Project identification
        :param checks: List of selected checks to be executed on IaC
        :param scan_response_type: Scan response type (JSON or HTML)
        :return: Dict or string with scan result
        """
        nonexistent_checks = list(set(checks) - set(
            map(lambda check: check.name,
                filter(lambda check: check.enabled and check.configured, self.iac_checks.values()))))
        if nonexistent_checks:
            raise Exception(f'Nonexistent, disabled or un-configured checks: {nonexistent_checks}.')

        self._init_iac_dir(iac_file)
        scan_output = self._run_checks(checks, project_id, scan_response_type)
        self._cleanup_iac_dir()
        return scan_output

    def init_checklist(self):
        """
        Initiate list of enabled check lists.
        """
        check_list = []
        if os.environ.get("SCAN_PERSISTENCE") == "enabled":
            for scan in self.iac_checks.values():
                check_list.append(scan.name)
            self.project_checklist = check_list
        else:
            self.project_checklist = None

    def set_scan_runner_check(self, check_list):
        """
        Set enabled statuses
        """
        self.project_checklist = check_list
        for check in self.iac_checks.values():
            if check.name in check_list:
                check.enabled = True
            else:
                check.enabled = False
