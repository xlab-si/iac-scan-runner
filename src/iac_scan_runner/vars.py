import os

# vars for paths to directories
ROOT_DIR = os.getenv("ROOT_DIR", os.path.dirname(os.getcwd()))
SRC_DIR = f"{ROOT_DIR}/src"
VIRTUALENV_DIR = os.getenv("VIRTUALENV_DIR", f"{ROOT_DIR}/.venv")
TOOLS_DIR = os.getenv("TOOLS_DIR", f"{ROOT_DIR}/tools")
CONFIG_DIR = os.getenv("CONFIG_DIR", f"{ROOT_DIR}/config")
NODE_MODULES_DIR = os.getenv("NODE_MODULES_DIR", f"{ROOT_DIR}/node_modules")
TMP_DIR = os.getenv("TMP_DIR", f"{TOOLS_DIR}/tmp")

# vars for paths to check executables
OPERA_TOSCA_PARSER_CHECK_PATH = os.getenv("OPERA_TOSCA_PARSER_CHECK_PATH", f"{VIRTUALENV_DIR}/bin/opera-tosca-parser")
ANSIBLE_LINT_CHECK_PATH = os.getenv("ANSIBLE_LINT_CHECK_PATH", f"{VIRTUALENV_DIR}/bin/ansible-lint")
TFLINT_CHECK_PATH = os.getenv("TFLINT_CHECK_PATH", f"{TOOLS_DIR}/tflint")
TFSEC_CHECK_PATH = os.getenv("TFSEC_CHECK_PATH", f"{TOOLS_DIR}/tfsec")
TERRASCAN_CHECK_PATH = os.getenv("TERRASCAN_CHECK_PATH", f"{TOOLS_DIR}/terrascan")
YAMLLINT_CHECK_PATH = os.getenv("YAMLLINT_CHECK_PATH", f"{VIRTUALENV_DIR}/bin/yamllint")
PYLINT_CHECK_PATH = os.getenv("PYLINT_CHECK_PATH", f"{VIRTUALENV_DIR}/bin/pylint")
BANDIT_CHECK_PATH = os.getenv("BANDIT_CHECK_PATH", f"{VIRTUALENV_DIR}/bin/bandit")
SAFETY_CHECK_PATH = os.getenv("SAFETY_CHECK_PATH", f"{VIRTUALENV_DIR}/bin/safety")
GIT_LEAKS_CHECK_PATH = os.getenv("GIT_LEAKS_CHECK_PATH", f"{TOOLS_DIR}/gitleaks")
GIT_SECRETS_CHECK_PATH = os.getenv("GIT_SECRETS_CHECK_PATH", f"{TOOLS_DIR}/git-secrets/bin/git-secrets")
MARKDOWN_LINT_CHECK_PATH = os.getenv("MARKDOWN_LINT_CHECK_PATH", f"{TOOLS_DIR}/mdl")
HADOLINT_CHECK_PATH = os.getenv("HADOLINT_CHECK_PATH", f"{TOOLS_DIR}/hadolint")
GIXY_CHECK_PATH = os.getenv("GIXY_CHECK_PATH", f"{VIRTUALENV_DIR}/bin/gixy")
SHELL_CHECK_PATH = os.getenv("SHELL_CHECK_PATH", f"{TOOLS_DIR}/shellcheck")
ES_LINT_CHECK_PATH = os.getenv("ES_LINT_CHECK_PATH", f"{NODE_MODULES_DIR}/.bin/eslint")
HTMLHINT_CHECK_PATH = os.getenv("HTMLHINT_CHECK_PATH", f"{NODE_MODULES_DIR}/.bin/htmlhint")
STYLELINT_CHECK_PATH = os.getenv("STYLELINT_CHECK_PATH", f"{NODE_MODULES_DIR}/.bin/stylelint")
CLOC_CHECK_PATH = os.getenv("CLOC_CHECK_PATH", f"{NODE_MODULES_DIR}/.bin/cloc")
CHECKSTYLE_CHECK_PATH = os.getenv("CHECKSTYLE_CHECK_PATH", f"{TOOLS_DIR}/checkstyle.jar")
SONAR_SCANNER_CHECK_PATH = os.getenv("SONAR_SCANNER_CHECK_PATH", f"{TOOLS_DIR}/sonar-scanner/bin/sonar-scanner")
SNYK_CHECK_PATH = os.getenv("SNYK_CHECK_PATH", f"{NODE_MODULES_DIR}/.bin/snyk")
STEAMPUNK_SPOTTER_CHECK_PATH = os.getenv("STEAMPUNK_SPOTTER_CHECK_PATH", f"{VIRTUALENV_DIR}/bin/spotter")
