#!/bin/bash

# env vars
export ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export TOOLS_DIR="${ROOT_DIR}/tools"
export CONFIG_DIR="${ROOT_DIR}/config"
export NODE_MODULES_DIR="${ROOT_DIR}/node_modules"
export TMP_DIR="${TOOLS_DIR}/tmp"
export GIT_SECRETS_DIR="${TOOLS_DIR}/git-secrets"
export CHECK_STYLE_PATH="${TOOLS_DIR}/checkstyle.jar"
export CHECK_SHELL_PATH="${TOOLS_DIR}/shellcheck"
export HADOLINT_PATH="${TOOLS_DIR}/hadolint"
export MDL_PATH="${TOOLS_DIR}/mdl"
export GIT_LEAKS_PATH="${TOOLS_DIR}/gitleaks"
export TF_SEC_PATH="${TOOLS_DIR}/tfsec"
export TERRASCAN_PATH="${TOOLS_DIR}/terrascan"
export SONAR_SCANNER_PATH="${TOOLS_DIR}/sonar-scanner/bin/sonar-scanner"

# urls for installation of tools
checkStyleUrl='https://github.com/checkstyle/checkstyle/releases/download/checkstyle-8.13/checkstyle-8.13-all.jar'
checkShellUrl='https://github.com/koalaman/shellcheck/releases/download/v0.5.0/shellcheck-v0.5.0.linux.x86_64.tar.xz'
hadolintUrl='https://github.com/hadolint/hadolint/releases/download/v1.13.0/hadolint-Linux-x86_64'
gitLeaksUrl='https://github.com/zricethezav/gitleaks/releases/download/v7.5.0/gitleaks-linux-amd64'
gitSecretsUrl='https://github.com/awslabs/git-secrets.git'
tflintUrl='https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh'
tfsecUrl='https://github.com/tfsec/tfsec/releases/download/v0.51.1/tfsec-linux-amd64'
terrascanUrl='https://api.github.com/repos/accurics/terrascan/releases/latest'
sonarScannerUrl='https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.6.2.2472-linux.zip'

# functions below are used to install the tools
createDirIfNot() {
  dirPath=$1
  if [ ! -d "$dirPath" ]; then
    mkdir "${dirPath}"
  fi
}

downloadCheckStyleJarIfNot() {
  if [ ! -f "$CHECK_STYLE_PATH" ]; then
    wget ${checkStyleUrl} -O "${CHECK_STYLE_PATH}"
  fi
}

downloadCheckShellIfNot() {
  if [ ! -f "$CHECK_SHELL_PATH" ]; then
    wget ${checkShellUrl} -O "${TMP_DIR}/checkShell.linux.x86_64.tar.xz"
    tar --xz -xvf "${TMP_DIR}/checkShell.linux.x86_64.tar.xz" -C "${TMP_DIR}"
    cp "${TMP_DIR}"/shellcheck*/shellcheck "${TOOLS_DIR}"
    chmod u+x "${CHECK_SHELL_PATH}"
  fi
}

downloadHadolintlIfNot() {
  if [ ! -f "$HADOLINT_PATH" ]; then
    wget ${hadolintUrl} -O "${HADOLINT_PATH}"
    chmod u+x "${HADOLINT_PATH}"
  fi
}

installMDLIfNot() {
  if [ ! -f "$MDL_PATH" ]; then
    gem install chef-utils -v 16.6.14
    gem install --user-install -n "${TOOLS_DIR}" mdl
  fi
}

installRequiredNpmModules() {
  npm i
}

installPythonModules() {
  pip install pylint==2.9.6
  pip install gixy==0.1.20
  pip install ansible-lint==5.1.2
  pip install ansible==4.3.0
  pip install yamllint==1.26.1
  pip install bandit==1.7.0
  pip install safety==1.10.3
}

installGitLeaksIfNot() {
  if [ ! -f "${GIT_LEAKS_PATH}" ]; then
    wget ${gitLeaksUrl} -O "${GIT_LEAKS_PATH}"
    chmod +x "${GIT_LEAKS_PATH}"
  fi
}


installGitSecretsIfNot(){
  if [ ! -d "$GIT_SECRETS_DIR" ]; then
    git clone ${gitSecretsUrl} "${GIT_SECRETS_DIR}"
    cd "${GIT_SECRETS_DIR}" || exit
    make install
  fi
}

installTFLintIfNot(){
  if ! [ -x "$(command -v tflint)" ]; then
    curl -fsSL ${tflintUrl} | bash
  fi
}

installTfsecIfNot(){
  if [ ! -f "${TF_SEC_PATH}" ]; then
    wget ${tfsecUrl} -O "${TF_SEC_PATH}"
    chmod +x "${TF_SEC_PATH}"
  fi
}

installTerrascanIfNot(){
  if [ ! -f "${TERRASCAN_PATH}" ]; then
    curl -L "$(curl -s ${terrascanUrl} | grep -o -E "https://.+?_Linux_i386.tar.gz")" > "${TOOLS_DIR}"/terrascan.tar.gz
    tar -xf "${TOOLS_DIR}"/terrascan.tar.gz terrascan && rm "${TOOLS_DIR}"/terrascan.tar.gz
    install terrascan "${TOOLS_DIR}" && rm terrascan
    chmod +x "${TERRASCAN_PATH}"
  fi
}

installSonarScannerIfNot(){
  if [ ! -f "${TERRASCAN_PATH}" ]; then
    wget ${sonarScannerUrl} -O "${TMP_DIR}"/sonar-scanner
    unzip "${TMP_DIR}"/sonar-scanner -d "${TOOLS_DIR}"
    mv "${TOOLS_DIR}"/sonar-scanner sonar-scanner
  fi
}

# call the functions above to install all necessary tools
createDirIfNot "${TOOLS_DIR}"
createDirIfNot "${TMP_DIR}"
createDirIfNot "${CONFIG_DIR}"
installPythonModules
installRequiredNpmModules
downloadCheckStyleJarIfNot
downloadCheckShellIfNot
downloadHadolintlIfNot
installMDLIfNot
installGitLeaksIfNot
installGitSecretsIfNot
installTFLintIfNot
installTfsecIfNot
installTerrascanIfNot
installSonarScannerIfNot
