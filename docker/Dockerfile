FROM ubuntu:22.04
#test pipeeline

ENV TZ=CET
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update \
    && apt install -y wget git vim curl gnupg software-properties-common  linux-headers-$(uname -r) \
            dnsutils iptables openvpn strongswan xl2tpd ppp findutils openresolv iproute2 wireguard-tools \
            build-essential libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev

RUN add-apt-repository ppa:deadsnakes/ppa && \
        apt install -y python3.11 python3-pip

RUN echo ""deb [arch=amd64 trusted=yes] http://10.255.0.10/ stable main"" >> /etc/apt/sources.list
RUN apt update && apt install vg-nacl

RUN wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | tee /usr/share/keyrings/hashicorp-archive-keyring.gpg \
        && gpg --no-default-keyring --keyring /usr/share/keyrings/hashicorp-archive-keyring.gpg --fingerprint \
        && echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" |  tee /etc/apt/sources.list.d/hashicorp.list

RUN apt update && apt install -y terraform

RUN mkdir -p .vm-nacl-keys/key-pair.${each.value}/etc \
        && nacl genkey > $HOME/.vm-nacl-keys/key-pair.${each.value}/vg-endpoint.json \
        && nacl pubkey < $HOME/.vm-nacl-keys/key-pair.${each.value}/vg-endpoint.json > $HOME/.vm-nacl-keys/key-pair.${each.value}/etc/vg-router.json

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH "$PATH:/root/.local/bin"

RUN echo "#!/bin/sh" > /entrypoint.sh \
    && echo "sysctl net.ipv4.conf.all.src_valid_mark=1"  >> /entrypoint.sh \
    && echo "sysctl net.ipv6.conf.all.disable_ipv6=0"  >> /entrypoint.sh \
    && echo "modprobe wireguard" >> /entrypoint.sh \
    && echo "while true; do" >> /entrypoint.sh \
    && echo "    sleep 3600" >> /entrypoint.sh \
    && echo "done" >> /entrypoint.sh

RUN ssh-keygen -t rsa -q -f "$HOME/.ssh/id_rsa" -N ""

RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]