FROM python:3.10.2-slim-bullseye

# copy all files
COPY . /iac-scan-runner
WORKDIR /iac-scan-runner

# install system and API requirements
RUN apt-get update \
    && apt-get -y install build-essential bash gcc git openssh-client ruby-full curl wget default-jdk nodejs npm \
    && apt-get update \
    && mkdir -p /usr/share/man/man1 \
    && npm i npm@latest -g \
    && python3 -m venv .venv \
    && . .venv/bin/activate \
    && pip3 install --upgrade pip \
    && pip install -r requirements.txt \
    && ./install-checks.sh

#add python virtualenv and tools dir to path to be able to invoke commands
ENV PATH="/iac-scan-runner/.venv/bin:$PATH"
ENV PATH="/iac-scan-runner/tools:$PATH"

# set working directory
WORKDIR /iac-scan-runner/src

# start the API
CMD ["uvicorn", "iac_scan_runner.api:app", "--host", "0.0.0.0", "--port", "80"]
