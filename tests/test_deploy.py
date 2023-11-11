import pytest
import paramiko



hosts = ["10.255.0.4", "10.255.0.5"]
port = 22  # Default SSH port
username = 'ubuntu'
private_key_path = '/root/.ssh/id_rsa'


# List of services to check
services_to_check = ["socat-apt-proxy", "socat-rsyslog-proxy", "socat-zabbix-proxy", "brigades_backup"]

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

        for service in services_to_check:
            command = f'systemctl is-active {service}'
            stdin, stdout, stderr = ssh.exec_command(command)
            status = stdout.read().decode('utf-8').strip()
            assert status == 'active'

        ssh.close()