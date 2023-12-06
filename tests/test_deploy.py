import pytest
import paramiko
import time

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

# Test function to check deployment
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
                #Add a wait until the cloud init script is executed
                max_attempts = 10
                current_attempt = 0
                while current_attempt < max_attempts:
                    command = f'''sleep 60 && pgrep -c -f "/var/lib/cloud/instance/scripts/part-001"'''
                    result = execute_remote_command(ssh, command)
                    print(result)
                    if int(result) == 0 or current_attempt == max_attempts:
                        break
                    else:
                        current_attempt += 1

                #Checking the installation of packages
                command = "dpkg -s vgkeydesk-all cert-vpn-works > /dev/null; echo $?"
                exit_code = execute_remote_command(ssh, command)
                assert exit_code == '0'

                #Check that all services have started
                for service in ct_services_to_check:
                    command = f'systemctl is-active {service}'
                    status = execute_remote_command(ssh, command)
                    assert status == 'active'
            else:
                # Add a wait until the cloud init script is executed
                max_attempts = 10
                current_attempt = 0
                while current_attempt < max_attempts:
                    command = f'''sleep 60 && pgrep -c -f "/var/lib/cloud/instance/scripts/part-001"'''
                    result = execute_remote_command(ssh, command)
                    print(result)
                    if int(result) == 0 or current_attempt == max_attempts:
                        break
                    else:
                        current_attempt += 1

                #Checking the installation of packages
                command = "sudo iptables -m ipp2p --help 2>/dev/null | fgrep -c BitTorrent"
                iptables_module = execute_remote_command(ssh, command)
                assert iptables_module == '1'

                #Check that all services have started
                for service in ep_services_to_check:
                    command = f'systemctl is-active {service}'
                    status = execute_remote_command(ssh, command)
                    assert status == 'active'
        ssh.close()