import pytest
import paramiko
import subprocess
import json

# VMs IP addresses and SSH credentials
vm_ct = '10.255.0.4'
vm_ep = '10.255.0.5'
port = 22
username = 'ubuntu'
private_key_path = '/root/.ssh/id_rsa'

# List of services to check on CTs
ct_services = [
    "vgstats@WNFRWF4E5VELRL7OMFIK4Z3URI.service",
    "vgkeydesk@WNFRWF4E5VELRL7OMFIK4Z3URI.service"
]


def test_brigade():
    commands = [
        """ssh  -o StrictHostKeyChecking=no -i /root/.ssh/id_rsa_keydesk _serega_@10.255.0.4 destroy -id WNFRWF4E5VELRL7OMFIK4Z3URI""",
        """ssh  -o StrictHostKeyChecking=no -i /root/.ssh/id_rsa_keydesk _serega_@10.255.0.4 create -id WNFRWF4E5VELRL7OMFIK4Z3URI \
              -ep4 195.133.0.108 -int4 100.124.76.0/24 -int6 fd18:98bf:67ab:b2aa::/64 -dns4 100.124.76.1 \
              -dns6 fd18:98bf:67ab:b2aa:5917:f76a:c955:18d3 -kd6 fd70:c7ee:e821:af9b:8c89:7cc9:2c5e:bfee \
              -name 0K/RgNC60LDRjyDQndC10LzQtdGC -person 0K3QstC4INCd0LXQvNC10YI= \
              -desc 0JDQvNC10YDQuNC60LDQvdGB0LrQuNC5INC40L3QttC10L3QtdGALCDQv9C40YHQsNGC0LXQu9GMINC4INC/0YDQtdC/0L7QtNCw0LLQsNGC0LXQu9GMLCDQuNC30LLQtdGB0YLQvdCwINGB0LLQvtC40LzQuCDRjdC60YHQv9C10YDRgtC90YvQvNC4INC/0L7Qt9C90LDQvdC40Y/QvNC4INCyINGB0LjRgdGC0LXQvNC90L7QvCDQsNC00LzQuNC90LjRgdGC0YDQuNGA0L7QstCw0L3QuNC4INC4INGB0LXRgtC10LLRi9GFINGC0LXRhdC90L7Qu9C+0LPQuNGP0YUu \
              -url aHR0cHM6Ly9ydS53aWtpcGVkaWEub3JnL3dpa2kvJUQwJTlEJUQwJUI1JUQwJUJDJUQwJUI1JUQxJTgyLF8lRDAlQUQlRDAlQjIlRDAlQjg= \
              -j -wg native -ipsec text -ovc amnezia -outline access_key -ch -p 54321"""
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
            count +=1
        else:
            assert result.returncode == 0

def execute_remote_command(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode('utf-8').strip()

def test_user():
    for host in [vm_ep, vm_ct]:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            host,
            port,
            username,
            private_key_path
        )

        if host == vm_ep:
            command_token = """curl -s -X 'POST' "http://[fdcc:c385:6c::2]:80/token" -H 'accept: application/json' -d '' | jq -r '.Token' | tr -d ''"""
            token = execute_remote_command(ssh, command_token)
            command_add = f"""curl -s -X 'POST' "http://[fdcc:c385:6c::2]:80/user" -H 'accept: application/json' -H "Authorization: Bearer {token}" -d ''"""
            response = execute_remote_command(ssh, command_add)
            global json_data
            json_data = response
            assert 'AmnzOvcConfig' or 'IPSecL2TPManualConfig' or 'OutlineConfig' or 'WireguardConfig' in response
        else:
            for service in ct_services:
                command = f'systemctl is-active {service}'
                status = execute_remote_command(ssh, command)
                assert status == 'active'

        ssh.close()

def parse_config(json_data):
    subprocess.run(
        'rm -f config.txt',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8',
        timeout=60
    )
    with open('config.txt', 'w') as file:
        config_data = json.loads(json_data)

        amnz_ovc_config = config_data.get('AmnzOvcConfig', {})
        ipsec_l2tp_config = config_data.get('IPSecL2TPManualConfig', {})
        outline_config = config_data.get('OutlineConfig', {})
        wireguard_config = config_data.get('WireguardConfig', {})

        file.write("AmnzOvcConfig:\n")
        for key, value in amnz_ovc_config.items():
            file.write(f"  {key}: {value}\n")

        file.write("\nIPSecL2TPManualConfig:\n")
        for key, value in ipsec_l2tp_config.items():
            file.write(f"  {key}: {value}\n")

        file.write("\nOutlineConfig:\n")
        for key, value in outline_config.items():
            file.write(f"  {key}: {value}\n")

        file.write("\nWireguardConfig:\n")
        for key, value in wireguard_config.items():
            file.write(f"  {key}: {value}\n")

def save_json_to_file(json_data, file_name='config.json'):
    with open(file_name, 'w') as file:
        file.write(json_data)


test_brigade()
test_user()
parse_config(json_data)