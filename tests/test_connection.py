import json
import pytest
import subprocess
import paramiko

host_ipsec = '172.18.0.20'
port = 22
username = 'root'
private_key_path = '/root/.ssh/id_rsa'

def parse_config():
    with open('config.json', 'r') as config_file:
        config_data = json.load(config_file)

    wireguard_config_data = config_data.get('WireguardConfig', {}).get('FileContent', '')
    with open('/etc/wireguard/wg0.conf', 'w') as file:
        file.write(wireguard_config_data)

    global ipsec_config_data
    ipsec_config_data = config_data.get('IPSecL2TPManualConfig', {})


def execute_remote_command(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode('utf-8').strip()


def get_external_ip():
    external_ip = subprocess.run(
        "curl -s http://ifconfig.me",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8'
    ).stdout.strip()
    return external_ip

def test_wg():
    initial_external_ip = get_external_ip()
    subprocess.run("wg-quick up wg0", shell=True, check=True)
    updated_external_ip = get_external_ip()
    subprocess.run("wg-quick down wg0", shell=True, check=True)
    assert initial_external_ip != updated_external_ip
    print(initial_external_ip)
    print(updated_external_ip)
    print("wg")

def test_ipsec():
    host = host_ipsec
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        host,
        port,
        username,
        private_key_path
    )

    curl = "curl -s http://ifconfig.me"
    initial_external_ip = execute_remote_command(ssh, curl)
    external_ip = initial_external_ip
    startup = f'''export VPN_SERVER_IPV4={ipsec_config_data.get("Server", "")} \
                export VPN_PSK={ipsec_config_data.get("PSK", "")} \
                export VPN_USERNAME={ipsec_config_data.get("Username", "")} \
                export VPN_PASSWORD={ipsec_config_data.get("Password", "")} \
                && sh /startup.sh > /dev/null & sleep 60'''
    execute_remote_command(ssh, startup)
    route = "ip route add 195.133.0.108 via 172.17.0.1 && ip route del default  && ip route add default via 100.127.0.1 dev ppp0"
    execute_remote_command(ssh, route)
    updated_external_ip = execute_remote_command(ssh, curl)
    print(route)
    print(initial_external_ip)
    print(updated_external_ip)

    assert updated_external_ip is not None and updated_external_ip != "" and updated_external_ip != external_ip

    ssh.close()

parse_config()
get_external_ip()