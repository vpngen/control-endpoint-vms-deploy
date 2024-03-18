import paramiko
import pytest
from paramiko import SSHClient

from tests.common import ip_url, config_json, execute_remote_command


@pytest.fixture
def ssh_client():
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    yield client
    client.close()


@pytest.fixture
def ipsec_cfg(config_json: dict):
    yield config_json.get('IPSecL2TPManualConfig', {})


def test_ipsec(ipsec_cfg: dict, ssh_client: SSHClient):
    curl_command = f'curl -s {ip_url}'
    initial_external_ip = execute_remote_command(ssh_client, curl_command)
    print(initial_external_ip)

    startup = f'''export VPN_SERVER_IPV4={ipsec_cfg.get("Server", "")} \
export VPN_PSK={ipsec_cfg.get("PSK", "")} \
export VPN_USERNAME={ipsec_cfg.get("Username", "")} \
export VPN_PASSWORD={ipsec_cfg.get("Password", "")} \
&& sh /startup.sh > /dev/null & sleep 60'''
    execute_remote_command(ssh_client, startup)

    route = ("ip route add 195.133.0.108 via 172.18.0.1 && "
             "ip route del default  && "
             "ip route add default via 100.127.0.1 dev ppp0")
    execute_remote_command(ssh_client, route)
    print(route)

    updated_external_ip = execute_remote_command(ssh_client, curl_command)
    print(updated_external_ip)

    assert all(
        [
            updated_external_ip is not None,
            updated_external_ip != "",
            updated_external_ip != initial_external_ip,
        ]
    )
