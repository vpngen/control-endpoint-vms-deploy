import pytest
import paramiko

# VMs IP addresses and SSH credentials
vm_ct = '10.255.0.4'
vm_ep = '10.255.0.5'
port = 22
username = 'ubuntu'
key = paramiko.RSAKey.from_private_key_file("/root/.ssh/id_rsa")

# List of services to check on EPs
ep_services_to_check_all = ["zabbix-agent",
                        "outline-ss-logger.service",
                        "wg-mng.socket",
                        "accel-ppp-ns@wg0.service",
                        "cloak-admin-ns@wg0.service",
                        "cloak-ns@wg0.service",
                        #"dnsmasq-ns@wg0:*.service",
                        "fakehttp-ns@ens161:wg0.service",
                        "ipsec-ns@ens161:wg0.service",
                        "openvpn-ns@wg0.service",
                        "outline-ss-logger.service",
                        "outline-ss-ns@wg0.service",
                        "wg-quick-ns@wg0.service"]

ep_services_to_check_wg = ["wg-quick-ns@wg0.service",
                           "fakehttp-ns@ens161:wg0.service"]

ep_services_to_check_ipsec = ["accel-ppp-ns@wg0.service",
                              "fakehttp-ns@ens161:wg0.service",
                              "ipsec-ns@ens161:wg0.service",
                              "wg-quick-ns@wg0.service"]

ep_services_to_check_openvpn = ["openvpn-ns@wg0.service",
                                "cloak-admin-ns@wg0.service",
                                "cloak-ns@wg0.service",
                                "fakehttp-ns@ens161:wg0.service"]

ep_services_to_check_outline = ["outline-ss-logger.service",
                                "outline-ss-ns@wg0.service",
                                "fakehttp-ns@ens161:wg0.service"]

ep_services_to_check = [ep_services_to_check_all,
                        ep_services_to_check_wg,
                        ep_services_to_check_ipsec,
                        ep_services_to_check_openvpn,
                        ep_services_to_check_outline]

#List of curl requests add different VPNs to EPs
curl_request_all = """curl -v 'http://[fdcc:c385:6c::3]:8080/?wg_add='`echo In4ningHYWutaNHXfkE79I3BF20oKzoWiizL7l2oOSM= | nacl -b seal /etc/vg-router.json`'&internal-nets=172.16.0.1/16,fd0d:86fa:c3bc::1/64&external-ip=195.133.0.108&l2tp-preshared-key='`echo 0123456789012345 | base64 -w 0 | nacl -b seal /etc/vg-router.json`'&wireguard-port=40000&cloak-domain=google.com&openvpn-ca-key='`cat pki/private/ca.key | gzip -n | base64 -w 0 | nacl -b seal /etc/vg-router.json`'&openvpn-ca-crt='`cat pki/ca.crt | gzip -n | base64 -w 0`'&outline-ss-port=9944'"""

curl_request_wg = """curl -v 'http://[fdcc:c385:6c::3]:8080/?wg_add='`echo In4ningHYWutaNHXfkE79I3BF20oKzoWiizL7l2oOSM= | nacl -b seal /etc/vg-router.json`'&internal-nets=172.16.0.1/16,fd0d:86fa:c3bc::1/64&external-ip=195.133.0.108&wireguard-port=40000'"""

curl_request_ipsec = """curl -v 'http://[fdcc:c385:6c::3]:8080/?wg_add='`echo In4ningHYWutaNHXfkE79I3BF20oKzoWiizL7l2oOSM= | nacl -b seal /etc/vg-router.json`'&internal-nets=172.16.0.1/16,fd0d:86fa:c3bc::1/64&external-ip=195.133.0.108&wireguard-port=40000&l2tp-preshared-key='`echo 0123456789012345 | base64 -w 0 | nacl -b seal /etc/vg-router.json`''"""

curl_request_openvpn = """curl -v 'http://[fdcc:c385:6c::3]:8080/?wg_add='`echo In4ningHYWutaNHXfkE79I3BF20oKzoWiizL7l2oOSM= | nacl -b seal /etc/vg-router.json`'&internal-nets=172.16.0.1/16,fd0d:86fa:c3bc::1/64&external-ip=195.133.0.108&wireguard-port=40000&cloak-domain=google.com&openvpn-ca-key='`cat /home/ubuntu/pki/private/ca.key | gzip -n | base64 -w 0 | nacl -b seal /etc/vg-router.json`'&openvpn-ca-crt='`cat /home/ubuntu/pki/ca.crt | gzip -n | base64 -w 0`''"""

curl_request_outline = """curl -v 'http://[fdcc:c385:6c::3]:8080/?wg_add='`echo In4ningHYWutaNHXfkE79I3BF20oKzoWiizL7l2oOSM= | nacl -b seal /etc/vg-router.json`'&internal-nets=172.16.0.1/16,fd0d:86fa:c3bc::1/64&external-ip=195.133.0.108&wireguard-port=40000&outline-ss-port=9944'"""

curl_request = [curl_request_all,
                curl_request_wg,
                curl_request_ipsec,
                curl_request_openvpn,
                curl_request_outline]

#Function to execute remote commands on VMs
def execute_remote_command(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode('utf-8').strip()

# Test function to check services after creating VPNs
def test_main():
    for index,curl in enumerate(curl_request):
        for host in [vm_ct, vm_ep]:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                host,
                port,
                username,
                pkey=key
            )

            if host == vm_ct:
                command_add_keys = '''sudo apt install vg-nacl easy-rsa -y && \
                                    /usr/share/easy-rsa/easyrsa --batch --use-algo=ec --curve=secp521r1 --digest=sha512 init-pki && \
                                    /usr/share/easy-rsa/easyrsa --batch --use-algo=ec --curve=secp521r1 --digest=sha512 --days=3650 build-ca nopass && \
                                    EASYRSA_REQ_CN=client1 /usr/share/easy-rsa/easyrsa --batch --use-algo=ec --curve=secp521r1 --digest=sha512 gen-req client1 nopass'''
                execute_remote_command(ssh, command_add_keys)
                command_del = """curl -v 'http://[fdcc:c385:6c::3]:8080/?wg_del='`echo In4ningHYWutaNHXfkE79I3BF20oKzoWiizL7l2oOSM= | nacl -b seal /etc/vg-router.json`"""
                response_del = execute_remote_command(ssh, command_del)
                assert response_del == '{"code": "0"}' or response_del == '{"code": "128", "error": "no interface found for supplied private key"}'
                command_add = curl_request[index]
                response = execute_remote_command(ssh, command_add)
                assert response == '{"code": "0"}' or response == '{"code": "0", "openvpn-client-certificate": "-----BEGIN CERTIFICATE-----\\n.*\\n-----END CERTIFICATE-----\\n"}'
            else:
                ep_services = ep_services_to_check[index]
                for service in ep_services:
                    command = f'systemctl is-active {service}'
                    status = execute_remote_command(ssh, command)
                    assert status == 'active'
            command_del = """curl -v 'http://[fdcc:c385:6c::3]:8080/?wg_del='`echo In4ningHYWutaNHXfkE79I3BF20oKzoWiizL7l2oOSM= | nacl -b seal /etc/vg-router.json`"""
            response_del = execute_remote_command(ssh, command_del)
            assert response_del == '{"code": "0"}' or response_del == '{"code": "128", "error": "no interface found for supplied private key"}'
            ssh.close()
