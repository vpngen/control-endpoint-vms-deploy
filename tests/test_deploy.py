import pytest
import paramiko

vm_ct = '10.255.0.4'
vm_ep = '10.255.0.5'
hosts = [vm_ct, vm_ep]
port = 22  # Default SSH port
username = 'ubuntu'
private_key_path = '/root/.ssh/id_rsa'

# List of services to check
ct_services_to_check = ["socat-apt-proxy", "socat-rsyslog-proxy", "socat-zabbix-proxy"]
ep_services_to_check = ["zabbix-agent", "outline-ss-logger", "wg-mng.socket"]

# Specify the private key for authentication
private_key = paramiko.RSAKey(filename=private_key_path)

for host in hosts:
    def test_service():
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            host,
            port,
            username,
            private_key_path
        )
        if host == vm_ct:
            for service in ct_services_to_check:
                command = f'systemctl is-active {service}'
                stdin, stdout, stderr = ssh.exec_command(command)
                status = stdout.read().decode('utf-8').strip()
                assert status == 'active'
        else:
            for service in ep_services_to_check:
                command = f'systemctl is-active {service}'
                stdin, stdout, stderr = ssh.exec_command(command)
                status = stdout.read().decode('utf-8').strip()
                assert status == 'active'

        ssh.close()