import shlex
from subprocess import Popen
from time import sleep

import pytest

from tests.common import get_external_ip, config_json
from tests.decode_config import (
    get_cloak_config,
    get_openvpn_config,
    decode_amnezia,
)


@pytest.fixture
def amnz_config(config_json) -> dict:
    return decode_amnezia(config_json['AmnzOvcConfig']['FileContent'])


@pytest.fixture
def cloak_config(amnz_config):
    with open('ckclient.json', 'w') as file:
        file.write(get_cloak_config(amnz_config))


@pytest.fixture
def openvpn_config(amnz_config):
    with open('test.ovpn', 'w') as file:
        file.write(
            get_openvpn_config(amnz_config).replace('block-outside-dns\n', '')
        )


@pytest.fixture
def real_ip(cloak_config, openvpn_config) -> str:
    with Popen(shlex.split("ck-client -l 1194")) as cloak:
        ip = get_external_ip()
        with Popen(shlex.split("openvpn test.ovpn")) as openvpn:
            sleep(1)
            yield ip
            openvpn.terminate()
            cloak.terminate()


def test_cloak_openvpn(real_ip: str):
    ip = get_external_ip()
    assert ip
    assert ip != real_ip
