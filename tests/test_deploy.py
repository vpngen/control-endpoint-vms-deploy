import pytest
import paramiko

# VMs IP addresses and SSH credentials
vm_ct = '10.255.0.4'
vm_ep = '10.255.0.5'
port = 22
username = 'ubuntu'
private_key_path = '/root/.ssh/id_rsa'

# List of services to check
ct_services_to_check = ["socat-apt-proxy", "socat-rsyslog-proxy", "socat-zabbix-proxy"]
ep_services_to_check = ["zabbix-agent", "outline-ss-logger", "wg-mng.socket"]

#Function to execute remote commands on VMs
def execute_remote_command(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode('utf-8').strip()

# Test function to check services on VMs after deployment is finished
def test_deploy():
        for host in [vm_ct, vm_ep]:
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
                    status = execute_remote_command(ssh, command)
                    assert status == 'active'
            else:
                for service in ep_services_to_check:
                    command = f'systemctl is-active {service}'
                    status = execute_remote_command(ssh, command)
                    assert status == 'active'

        ssh.close()