import subprocess

import paramiko

from tests.common import (
    vm_ct_ip,
    vm_ep_ip,
    ssh_port,
    username,
    key,
    keydesk_url,
    execute_remote_command,
)

paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)

# List of services to check on CTs
ct_services = [
    "vgstats@WNFRWF4E5VELRL7OMFIK4Z3URI.service",
    "vgkeydesk@WNFRWF4E5VELRL7OMFIK4Z3URI.service"
]


def test_brigade():
    commands = [
        """ssh  -o StrictHostKeyChecking=no -i /root/.ssh/id_rsa_keydesk _serega_@10.255.0.4 destroy -id WNFRWF4E5VELRL7OMFIK4Z3URI""",
        """ssh  -o StrictHostKeyChecking=no -i /root/.ssh/id_rsa_keydesk _serega_@10.255.0.4 create -id WNFRWF4E5VELRL7OMFIK4Z3URI \
-ep4 195.133.0.108 -int4 100.124.76.0/24 \
-int6 fd18:98bf:67ab:b2aa::/64 \
-dns4 100.124.76.1 \
-dns6 fd18:98bf:67ab:b2aa:5917:f76a:c955:18d3 \
-kd6 fd70:c7ee:e821:af9b:8c89:7cc9:2c5e:bfee \
-name 0K/RgNC60LDRjyDQndC10LzQtdGC \
-person 0K3QstC4INCd0LXQvNC10YI= \
-desc 0JDQvNC10YDQuNC60LDQvdGB0LrQuNC5INC40L3QttC10L3QtdGALCDQv9C40YHQsNGC0LXQu9GMINC4INC/0YDQtdC/0L7QtNCw0LLQsNGC0LXQu9GMLCDQuNC30LLQtdGB0YLQvdCwINGB0LLQvtC40LzQuCDRjdC60YHQv9C10YDRgtC90YvQvNC4INC/0L7Qt9C90LDQvdC40Y/QvNC4INCyINGB0LjRgdGC0LXQvNC90L7QvCDQsNC00LzQuNC90LjRgdGC0YDQuNGA0L7QstCw0L3QuNC4INC4INGB0LXRgtC10LLRi9GFINGC0LXRhdC90L7Qu9C+0LPQuNGP0YUu \
-url aHR0cHM6Ly9ydS53aWtpcGVkaWEub3JnL3dpa2kvJUQwJTlEJUQwJUI1JUQwJUJDJUQwJUI1JUQxJTgyLF8lRDAlQUQlRDAlQjIlRDAlQjg= \
-j \
-wg native \
-ipsec text \
-ovc amnezia \
-outline access_key \
-ch \
-p 54321"""
    ]
    count = 0
    for command in commands:
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            timeout=60
        )
        if count == 0:
            assert result.returncode == 0 or 1
            count += 1
        else:
            assert result.returncode == 0


def test_user():
    json_header = "-H 'accept: application/json'"
    curl = 'curl -s -X POST'
    for host in [vm_ep_ip, vm_ct_ip]:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            host,
            ssh_port,
            username,
            pkey=key
        )

        if host == vm_ep_ip:
            command_token = f"""{curl} "{keydesk_url}/token" {json_header} -d '' | jq -r '.Token' | tr -d ''"""
            token = execute_remote_command(ssh, command_token)
            command_add = f"""{curl} "{keydesk_url}/user" {json_header} -H "Authorization: Bearer {token}" -d ''"""
            response = execute_remote_command(ssh, command_add)
            global json_data
            json_data = response
            assert 'AmnzOvcConfig' or 'IPSecL2TPManualConfig' or 'OutlineConfig' or 'WireguardConfig' in response
            with open("/config.json", 'w') as file:
                file.write(json_data)
        else:
            for service in ct_services:
                command = f'systemctl is-active {service}'
                status = execute_remote_command(ssh, command)
                assert status == 'active'

        ssh.close()
