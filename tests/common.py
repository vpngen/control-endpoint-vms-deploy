import json
import os
import shlex
from subprocess import run

import pytest
import requests
from paramiko import SSHClient, RSAKey

print(f"{os.environ.get('CALC_NETWORKS') = }")
print(f"{os.environ.get('EP_NETWORKS') = }")
print(f"{os.environ.get('CT_NETWORKS') = }")

calc_networks = json.loads(os.environ.get('CALC_NETWORKS'))
ep_networks = json.loads(os.environ.get('EP_NETWORKS'))
ct_networks = json.loads(os.environ.get('CT_NETWORKS'))

calc_network_v6_template = f'[{calc_networks[1]}%s]'
ep_address = calc_network_v6_template % '3'
ct_address = calc_network_v6_template % '2'
ep_url = f'http://{ep_address}:8080'
keydesk_url = f'http://{ct_address}:80'
wg_key = 'In4ningHYWutaNHXfkE79I3BF20oKzoWiizL7l2oOSM='
nacl_seal_cmd = 'nacl -b seal /etc/vg-router.json'
curl = 'curl -v'
internal_net_v4 = '172.16.0.1/16'
internal_net_v6 = 'fd0d:86fa:c3bc::1/64'
external_ip = ep_networks[0][-1]['ip']
wgport = 40000
outline_ss_port = 9944
ip_url = 'http://ifconfig.me'

# VMs IP addresses and SSH credentials
vm_ct_ip = ct_networks[0][0]['ip']
vm_ep_ip = ep_networks[0][0]['ip']
ssh_port = 22
username = 'ubuntu'
key = RSAKey.from_private_key_file(
    os.getenv('TEST_SSH_KEY_FILE').removesuffix('.pub')
)


def nacl_seal(cmd: str) -> str:
    return f'{cmd} | {nacl_seal_cmd}'


seal_key = nacl_seal(f'echo {wg_key}')
sealed_preshared_key = nacl_seal('echo 0123456789012345 | base64 -w 0')
sealed_ca_key = nacl_seal('cat pki/private/ca.key | gzip -n | base64 -w 0')
ca_cert_b64 = 'cat pki/ca.crt | gzip -n | base64 -w 0'


def get_external_ip(proxies=None):
    return requests.get(ip_url, proxies=proxies).text.strip()


def get_external_ip_with_socks():
    return get_external_ip({'http': 'socks5://127.0.0.1:1080'})


def run_cmd(cmd: str):
    return run(shlex.split(cmd), check=True)


# Function to execute remote commands on VMs
def execute_remote_command(ssh: SSHClient, command: str):
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode('utf-8').strip()


@pytest.fixture(scope="session")
def config_json():
    with open('config.json') as file:
        return json.load(file)
