FROM debian:bullseye-20220228-slim

# add python virtualenv and tools dir to path to be able to invoke commands
ENV PATH="/iac-scan-runner/.venv/bin:/iac-scan-runner/tools:$PATH"

# add CMD instruction TO run the API
CMD ["uvicorn", "iac_scan_runner.api:app", "--host", "0.0.0.0", "--port", "80"]

# set working directory
WORKDIR /iac-scan-runner/src

# copy all the files
COPY . /iac-scan-runner

# install system and API requirements
RUN cd /iac-scan-runner \
    && apt-get update \
    && apt-get -y install --no-install-recommends build-essential bash gcc git curl wget openjdk-17-jre \
                                                  ruby2.7 nodejs npm unzip python3 python3-pip python3-venv \
    && apt-get update \
    && mkdir -p /usr/share/man/man1 \
    && npm i npm@latest -g \
    && python3 -m venv .venv \
    && . .venv/bin/activate \
    && pip3 install --upgrade pip \
    && pip install -r requirements.txt \
    && ./install-checks.sh \
    && npm uninstall npm \
    && apt-get -y remove build-essential gcc npm curl wget \
    && apt-get autoremove -y \
    && apt-get autoclean -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/* \
    && rm -rf /root/.cache/
