import pytest

from tests.common import get_external_ip, config_json, run_cmd


@pytest.fixture
def wg_config(config_json):
    with open('/etc/wireguard/wg0.conf', 'w') as file:
        file.write(config_json['WireguardConfig']['FileContent'])


@pytest.fixture
def real_ip(wg_config):
    run_cmd("sysctl net.ipv4.conf.all.src_valid_mark=1")
    run_cmd("sysctl net.ipv6.conf.all.disable_ipv6=0")
    run_cmd("modprobe wireguard")
    ip = get_external_ip()
    run_cmd("wg-quick up wg0")
    yield ip
    run_cmd("wg-quick down wg0")


def test_wireguard(real_ip: str):
    ip = get_external_ip()
    assert ip
    assert ip != real_ip
