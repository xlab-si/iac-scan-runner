#!/bin/bash
# this bash script is used to install checks for IaC Scan Runner, run it as: ./install-checks.sh

# env vars for directories
export ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export VIRTUALENV_DIR="${ROOT_DIR}/.venv"
export TOOLS_DIR="${ROOT_DIR}/tools"
export TMP_DIR="${TOOLS_DIR}/tmp"
export NODE_MODULES_DIR="${ROOT_DIR}/node_modules"
export CONFIG_DIR="${ROOT_DIR}/config"
# env vars for check executables
export OPERA_CHECK_PATH="${VIRTUALENV_DIR}/bin/opera/"
export ANSIBLE_LINT_CHECK_PATH="${VIRTUALENV_DIR}/bin/ansible-lint/"
export TFLINT_CHECK_PATH="${TOOLS_DIR}/tflint"
export TFSEC_CHECK_PATH="${TOOLS_DIR}/tfsec"
export TERRASCAN_CHECK_PATH="${TOOLS_DIR}/terrascan"
export YAMLLINT_CHECK_PATH="${VIRTUALENV_DIR}/bin/yamllint"
export PYLINT_CHECK_PATH="${VIRTUALENV_DIR}/bin/pylint"
export BANDIT_CHECK_PATH="${VIRTUALENV_DIR}/bin/bandit"
export SAFETY_CHECK_PATH="${VIRTUALENV_DIR}/bin/safety"
export GIT_LEAKS_CHECK_PATH="${TOOLS_DIR}/gitleaks"
export GIT_SECRETS_CHECK_PATH="${TOOLS_DIR}/git-secrets/bin/git-secrets"
export MARKDOWN_LINT_CHECK_PATH="${TOOLS_DIR}/mdl"
export HADOLINT_CHECK_PATH="${TOOLS_DIR}/hadolint"
export GIXY_CHECK_PATH="${VIRTUALENV_DIR}/bin/gixy"
export SHELL_CHECK_PATH="${TOOLS_DIR}/shellcheck"
export ES_LINT_CHECK_PATH="${NODE_MODULES_DIR}/.bin/eslint"
export HTMLHINT_CHECK_PATH="${NODE_MODULES_DIR}/.bin/htmlhint"
export STYLELINT_CHECK_PATH="${NODE_MODULES_DIR}/.bin/stylelint"
export CLOC_CHECK_PATH="${NODE_MODULES_DIR}/.bin/cloc"
export CHECKSTYLE_CHECK_PATH="${TOOLS_DIR}/checkstyle.jar"
export SONAR_SCANNER_CHECK_PATH="${TOOLS_DIR}/sonar-scanner/bin/sonar-scanner"
export SNYK_CHECK_PATH="${NODE_MODULES_DIR}/.bin/snyk"

# urls for installation of check tools
checkStyleUrl='https://github.com/checkstyle/checkstyle/releases/download/checkstyle-8.13/checkstyle-8.13-all.jar'
checkShellUrl='https://github.com/koalaman/shellcheck/releases/download/v0.5.0/shellcheck-v0.5.0.linux.x86_64.tar.xz'
hadolintUrl='https://github.com/hadolint/hadolint/releases/download/v1.13.0/hadolint-Linux-x86_64'
gitLeaksUrl='https://github.com/zricethezav/gitleaks/releases/download/v7.5.0/gitleaks-linux-amd64'
gitSecretsUrl='https://github.com/awslabs/git-secrets.git'
tflintUrl='https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh'
tfsecUrl='https://github.com/tfsec/tfsec/releases/download/v0.51.1/tfsec-linux-amd64'
terrascanUrl='https://api.github.com/repos/accurics/terrascan/releases/latest'
sonarScannerUrl='https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.7.0.2747.zip'

# functions below are used to install the check tools
createAndActivateVenvDirIfNot() {
  if [ ! -d "$VIRTUALENV_DIR" ]; then
    python3 -m venv "$VIRTUALENV_DIR" && . "${VIRTUALENV_DIR}/bin/activate"
  fi
}

createDirIfNot() {
  dirPath=$1
  if [ ! -d "$dirPath" ]; then
    mkdir "${dirPath}"
  fi
}

removeDir() {
  rm -rf "$1"
}

downloadCheckStyleJarIfNot() {
  if [ ! -f "$CHECK_STYLE_PATH" ]; then
    wget ${checkStyleUrl} -O "${CHECK_STYLE_PATH}"
  fi
}

installShellCheckIfNot() {
  if [ ! -f "$SHELL_CHECK_PATH" ]; then
    wget ${checkShellUrl} -O "${TMP_DIR}/checkShell.linux.x86_64.tar.xz"
    tar --xz -xvf "${TMP_DIR}/checkShell.linux.x86_64.tar.xz" -C "${TMP_DIR}"
    cp "${TMP_DIR}"/shellcheck*/shellcheck "${TOOLS_DIR}"
    chmod u+x "${SHELL_CHECK_PATH}"
  fi
}

installHadolintlIfNot() {
  if [ ! -f "$HADOLINT_CHECK_PATH" ]; then
    wget ${hadolintUrl} -O "${HADOLINT_CHECK_PATH}"
    chmod u+x "${HADOLINT_CHECK_PATH}"
  fi
}

installMarkdownLintIfNot() {
  if [ ! -f "$MARKDOWN_LINT_CHECK_PATH" ]; then
    gem install --user-install -n "${TOOLS_DIR}" mdl
  fi
}

installRequiredNpmModulesIfNot() {
  if [ ! -f "$NODE_MODULES_DIR" ]; then
    npm install --force
  fi
}

installPythonModules() {
  pip install opera==0.6.8 pylint==2.12.2 gixy==0.1.20 ansible-lint==5.4.0 yamllint==1.26.3 bandit==1.7.2 safety==1.10.3
}

installGitLeaksIfNot() {
  if [ ! -f "$GIT_LEAKS_CHECK_PATH" ]; then
    wget ${gitLeaksUrl} -O "${GIT_LEAKS_CHECK_PATH}"
    chmod +x "${GIT_LEAKS_CHECK_PATH}"
  fi
}

installGitSecretsIfNot() {
  if [ ! -f "$GIT_SECRETS_CHECK_PATH" ]; then
    git clone ${gitSecretsUrl} "${TMP_DIR}/git-secrets"
    cd "${TMP_DIR}/git-secrets" || exit
    PREFIX="${TOOLS_DIR}/git-secrets" make install
  fi
}

installTFLintIfNot() {
  if [ ! -f "$TFLINT_CHECK_PATH" ]; then
    export TFLINT_INSTALL_PATH="$TOOLS_DIR"
    curl -fsSL ${tflintUrl} | bash
  fi
}

installTfsecIfNot() {
  if [ ! -f "$TFSEC_CHECK_PATH" ]; then
    wget ${tfsecUrl} -O "${TFSEC_CHECK_PATH}"
    chmod +x "${TFSEC_CHECK_PATH}"
  fi
}

installTerrascanIfNot() {
  if [ ! -f "$TERRASCAN_CHECK_PATH" ]; then
    curl -L "$(curl -s ${terrascanUrl} | grep -o -E "https://.+?_Linux_i386.tar.gz")" >"${TMP_DIR}/terrascan.tar.gz"
    tar -xf "${TMP_DIR}/terrascan.tar.gz" terrascan
    install terrascan "${TOOLS_DIR}"
    chmod +x "${TERRASCAN_CHECK_PATH}"
  fi
}

installSonarScannerIfNot() {
  if [ ! -f "$SONAR_SCANNER_CHECK_PATH" ]; then
    wget ${sonarScannerUrl} -O "${TMP_DIR}/sonar-scanner"
    unzip "${TMP_DIR}/sonar-scanner" -d "${TOOLS_DIR}"
    mv "${TOOLS_DIR}/sonar-scanner-cli-4.7.0.2747" "${TOOLS_DIR}/sonar-scanner"
  fi
}

# call the functions above to install all the necessary tools
createAndActivateVenvDirIfNot
createDirIfNot "${TOOLS_DIR}"
createDirIfNot "${TMP_DIR}"
createDirIfNot "${NODE_MODULES_DIR}"
createDirIfNot "${CONFIG_DIR}"
installPythonModules
installRequiredNpmModulesIfNot
downloadCheckStyleJarIfNot
installShellCheckIfNot
installHadolintlIfNot
installMarkdownLintIfNot
installGitLeaksIfNot
installGitSecretsIfNot
installTFLintIfNot
installTfsecIfNot
installTerrascanIfNot
installSonarScannerIfNot
removeDir "${TMP_DIR}"
