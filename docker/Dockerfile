FROM ubuntu:22.04 as base

ENV POETRY_HOME=/etc/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV APP_PATH=/home/app
ENV VENV=$APP_PATH/.venv
ENV BIN_PATH=$VENV/bin
ENV PATH=$BIN_PATH:$PATH

WORKDIR $APP_PATH

# timezone
ENV TZ=CET
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# packages
RUN apt update
RUN --mount=type=cache apt install -y ca-certificates curl gnupg software-properties-common build-essential
# TODO: fix this:
RUN apt install -y linux-headers-$(uname -r) || echo 'Wireguarad is not supported'

# install wireguard
RUN --mount=type=cache apt install -y procps iproute2 openresolv wireguard-tools

# install shadowsocks
RUN curl -sLO https://github.com/shadowsocks/go-shadowsocks2/releases/download/v0.1.5/shadowsocks2-linux.tgz
RUN tar xvf shadowsocks2-linux.tgz
RUN rm shadowsocks2-linux.tgz
RUN ln -s $(realpath shadowsocks2-linux) /usr/local/bin/shadowsocks2-linux

# install cloak
RUN curl -sLO https://github.com/cbeuw/Cloak/releases/download/v2.7.0/ck-client-linux-amd64-v2.7.0
RUN chmod +x ck-client-linux-amd64-v2.7.0
RUN ln -s $(realpath ck-client-linux-amd64-v2.7.0) /usr/local/bin/ck-client

# install openvpn
RUN --mount=type=cache apt install openvpn -y

# python repo
RUN apt update
RUN add-apt-repository ppa:deadsnakes/ppa

# install python
RUN apt update
RUN apt install python3.11 python3-pip -y

# install poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=$POETRY_HOME python3 -
RUN ln -s $POETRY_HOME/bin/poetry /usr/local/bin/poetry
RUN poetry config virtualenvs.in-project true

FROM base as build
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-directory
COPY tests ./tests
RUN poetry install --only main

FROM base as runtime
COPY --from=build $APP_PATH $APP_PATH
CMD poetry run pytest --tb=short tests/test_wg.py tests/test_outline.py tests/test_cloak_openvpn.py
