import json

from paramiko import SSHClient, AutoAddPolicy

from tests.common import (
    vm_ep_ip,
    ssh_port,
    ct_address,
    execute_remote_command,
    username, key,
)


def test_get_config():
    with SSHClient() as ssh:
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(vm_ep_ip, ssh_port, username, pkey=key)
        result = execute_remote_command(
            ssh,
            'curl -s '
            '-X POST '
            f'-H "Authorization: Bearer $(curl -s -X POST {ct_address}/token | jq -r .Token)" '
            f'{ct_address}/user | jq'
        )

    assert result
    assert json.loads(result)

    with open('config.json', 'w') as file:
        file.write(result)
