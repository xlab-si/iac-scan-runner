from os import remove
from shutil import rmtree
from typing import Optional, List

import iac_scan_runner.vars as env
from fastapi import UploadFile
from iac_scan_runner.checks.ansible_lint import AnsibleLintCheck
from iac_scan_runner.checks.bandit import BanditCheck
from iac_scan_runner.checks.es_lint import ESLintCheck
from iac_scan_runner.checks.git_leaks import GitLeaksCheck
from iac_scan_runner.checks.git_secrets import GitSecretsCheck
from iac_scan_runner.checks.gixy import GixyCheck
from iac_scan_runner.checks.hadolint import HadolintCheck
from iac_scan_runner.checks.htmlhint import HtmlHintCheck
from iac_scan_runner.checks.markdown_lint import MarkdownLintCheck
from iac_scan_runner.checks.pylint import PylintCheck
from iac_scan_runner.checks.pyup_safety import PyUpSafetyCheck
from iac_scan_runner.checks.shellcheck import ShellCheck
from iac_scan_runner.checks.stylelint import StyleLintCheck
from iac_scan_runner.checks.terrascan import TerrascanCheck
from iac_scan_runner.checks.tflint import TFLintCheck
from iac_scan_runner.checks.tfsec import TfsecCheck
from iac_scan_runner.checks.ts_lint import TSLintCheck
from iac_scan_runner.checks.yamllint import YamlLintCheck
from iac_scan_runner.utils import generate_random_pathname, unpack_archive_to_dir
from pydantic import SecretStr


class ScanRunner:
    def __init__(self):
        """Initialize new scan runner that can perform IaC scanning with multiple IaC checks"""
        self.iac_checks = {}
        self.iac_dir = None

    def init_checks(self):
        """Initiate predefined check objects"""
        ansible_lint = AnsibleLintCheck()
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

        self.iac_checks = {
            ansible_lint.name: ansible_lint,
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
            stylelint.name: stylelint
        }

    def _init_iac_dir(self, iac_file: UploadFile):
        """Initiate new unique IaC directory for scanning

         :param iac_file: IaC file
        """
        try:
            iac_filename_local = generate_random_pathname(iac_file.filename)
            with open(iac_filename_local, 'wb+') as iac_file_local:
                iac_file_local.write(iac_file.file.read())
                iac_file_local.close()
            self.iac_dir = unpack_archive_to_dir(iac_filename_local, None)
            remove(iac_filename_local)
        except Exception as e:
            raise Exception(f'Error when initializing IaC directory: {str(e)}.')

    def _cleanup_iac_dir(self):
        """Remove the created IaC directory"""
        try:
            rmtree(self.iac_dir, True)
        except Exception as e:
            raise Exception(f'Error when cleaning IaC directory: {str(e)}.')

    def _run_checks(self, selected_checks: Optional[List]) -> dict:
        """Run the specified IaC checks

         :param selected_checks: List of selected checks to be executed on IaC
        """
        scan_output = {}
        if selected_checks:
            for selected_check in selected_checks:
                check = self.iac_checks[selected_check]
                if check.enabled:
                    scan_output[selected_check] = check.run(self.iac_dir).to_dict()
        else:
            for iac_check in self.iac_checks.values():
                if iac_check.enabled:
                    scan_output[iac_check.name] = iac_check.run(self.iac_dir).to_dict()

        return scan_output

    def enable_check(self, check_name: str) -> str:
        """Enables the specified check and makes it available to be used

         :param check_name: Name of the check
        """
        if check_name in self.iac_checks.keys():
            check = self.iac_checks[check_name]
            if not check.enabled:
                check.enabled = True
                return f'Check: {check_name} is now enabled and available to use.'
            else:
                raise Exception(f'Check: {check_name} is already enabled.')
        else:
            raise Exception(f'Nonexistent check: {check_name}')

    def disable_check(self, check_name: str) -> str:
        """Disables the specified check and makes it unavailable to be used

         :param check_name: Name of the check
        """
        if check_name in self.iac_checks.keys():
            check = self.iac_checks[check_name]
            if check.enabled:
                check.enabled = False
                return f'Check: {check_name} is now disabled and cannot be used.'
            else:
                raise Exception(f'Check: {check_name} is already disabled.')
        else:
            raise Exception(f'Nonexistent check: {check_name}')

    def configure_check(self, check_name: str, config_file: Optional[UploadFile], secret: Optional[SecretStr]) -> str:
        """Configures the selected check with the supplied optional configuration file or/and secret

         :param check_name: Name of the check
         :param config_file: Check configuration file
         :param secret: Secret needed for configuration (e.g. API key, token, password etc.)
        """
        if check_name in self.iac_checks.keys():
            check = self.iac_checks[check_name]
            if check.enabled:
                config_filename_local = None
                if config_file:
                    config_filename_local = generate_random_pathname("", "-" + config_file.filename)
                    with open(f'{env.CONFIG_DIR}/{config_filename_local}', 'wb+') as config_file_local:
                        config_file_local.write(config_file.file.read())
                        config_file_local.close()
                check_output = check.configure(config_filename_local, secret)
                check.configured = True
                return check_output.output
            else:
                raise Exception(f'Check: {check_name} is disabled. You need to enable it first.')
        else:
            raise Exception(f'Nonexistent check: {check_name}')

    def scan_iac(self, iac_file: UploadFile, checks: List) -> dict:
        """Run IaC scanning process (initiate IaC dir, run checks and cleanup IaC dir)

         :param iac_file: IaC file that will be scanned
         :param checks: List of selected checks to be executed on IaC
        """
        nonexistent_checks = list(set(checks) - set(
            map(lambda check: check.name,
                filter(lambda check: check.enabled and check.configured, self.iac_checks.values()))))
        if nonexistent_checks:
            raise Exception(f'Nonexistent, disabled or un-configured checks: {nonexistent_checks}.')

        self._init_iac_dir(iac_file)
        scan_output = self._run_checks(checks)
        self._cleanup_iac_dir()
        return scan_output
