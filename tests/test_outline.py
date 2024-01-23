import shlex
from subprocess import Popen
from time import sleep

import pytest

from tests.common import (
    get_external_ip_with_socks,
    get_external_ip,
    config_json,
)
from tests.decode_config import decode_outline


@pytest.fixture
def outline_config(config_json: dict):
    return config_json['OutlineConfig']['AccessKey']


@pytest.fixture
def real_ip(outline_config: str):
    ip = get_external_ip()
    cmd = f'./shadowsocks2-linux -verbose -socks :1080 -c ss://{decode_outline(outline_config)}'
    with Popen(shlex.split(cmd)) as ss:
        sleep(1)
        yield ip
        ss.terminate()


def test_outline(real_ip: str):
    ip = get_external_ip_with_socks()
    assert ip
    assert ip != real_ip
