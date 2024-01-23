import paramiko
from paramiko import SSHClient

from tests.common import (
    vm_ct_ip, vm_ep_ip, ssh_port, username, key, execute_remote_command,
)

# List of services to check
ct_services_to_check = [
    "socat-apt-proxy",
    "socat-rsyslog-proxy",
    "socat-zabbix-proxy"
]
ep_services_to_check = ["zabbix-agent", "outline-ss-logger", "wg-mng.socket"]


def test_deploy_ct():
    with SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vm_ct_ip, ssh_port, username, pkey=key)
        # # Add a wait until the cloud init script is executed
        # max_attempts = 10
        # current_attempt = 0
        # while current_attempt < max_attempts:
        #     result = execute_remote_command(
        #         ssh,
        #         f'sleep 60 && '
        #         f'pgrep -c -f "/var/lib/cloud/instance/scripts/part-001"'
        #     )
        #     print(result)
        #     if int(result) == 0 or current_attempt == max_attempts:
        #         break
        #     else:
        #         current_attempt += 1

        # Checking the installation of packages
        command = "dpkg -s vgkeydesk-all cert-vpn-works > /dev/null; echo $?"
        exit_code = execute_remote_command(ssh, command)
        assert exit_code == '0'

        # Check that all services have started
        for service in ct_services_to_check:
            command = f'systemctl is-active {service}'
            status = execute_remote_command(ssh, command)
            assert status == 'active'


def test_deploy_ep():
    with SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vm_ep_ip, ssh_port, username, pkey=key)
        # # Add a wait until the cloud init script is executed
        # max_attempts = 10
        # current_attempt = 0
        # while current_attempt < max_attempts:
        #     result = execute_remote_command(
        #         ssh,
        #         f'sleep 60 && '
        #         f'pgrep -c -f "/var/lib/cloud/instance/scripts/part-001"'
        #     )
        #     print(result)
        #     if int(result) == 0 or current_attempt == max_attempts:
        #         break
        #     else:
        #         current_attempt += 1

        # Checking the installation of packages
        command = "sudo iptables -m ipp2p --help 2>/dev/null | fgrep -c BitTorrent"
        iptables_module = execute_remote_command(ssh, command)
        assert iptables_module == '1'

        # Check that all services have started
        for service in ep_services_to_check:
            command = f'systemctl is-active {service}'
            status = execute_remote_command(ssh, command)
            assert status == 'active'

# Test function to check deployment
# def test_deploy():
#     for host in [vm_ct_ip, vm_ep_ip]:
#         ssh = paramiko.SSHClient()
#         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         ssh.connect(
#             host,
#             ssh_port,
#             username,
#             pkey=key
#         )
#         if host == vm_ct_ip:
#             # Add a wait until the cloud init script is executed
#             max_attempts = 10
#             current_attempt = 0
#             while current_attempt < max_attempts:
#                 command = f'''sleep 60 && pgrep -c -f "/var/lib/cloud/instance/scripts/part-001"'''
#                 result = execute_remote_command(ssh, command)
#                 print(result)
#                 if int(result) == 0 or current_attempt == max_attempts:
#                     break
#                 else:
#                     current_attempt += 1
#
#             # Checking the installation of packages
#             command = "dpkg -s vgkeydesk-all cert-vpn-works > /dev/null; echo $?"
#             exit_code = execute_remote_command(ssh, command)
#             assert exit_code == '0'
#
#             # Check that all services have started
#             for service in ct_services_to_check:
#                 command = f'systemctl is-active {service}'
#                 status = execute_remote_command(ssh, command)
#                 assert status == 'active'
#         else:
#             # Add a wait until the cloud init script is executed
#             max_attempts = 10
#             current_attempt = 0
#             while current_attempt < max_attempts:
#                 command = f'''sleep 60 && pgrep -c -f "/var/lib/cloud/instance/scripts/part-001"'''
#                 result = execute_remote_command(ssh, command)
#                 print(result)
#                 if int(result) == 0 or current_attempt == max_attempts:
#                     break
#                 else:
#                     current_attempt += 1
#
#             # Checking the installation of packages
#             command = "sudo iptables -m ipp2p --help 2>/dev/null | fgrep -c BitTorrent"
#             iptables_module = execute_remote_command(ssh, command)
#             assert iptables_module == '1'
#
#             # Check that all services have started
#             for service in ep_services_to_check:
#                 command = f'systemctl is-active {service}'
#                 status = execute_remote_command(ssh, command)
#                 assert status == 'active'
#     ssh.close()
