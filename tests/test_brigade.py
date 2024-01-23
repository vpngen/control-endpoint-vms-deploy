import paramiko

from tests.common import (
    curl,
    ep_url,
    seal_key,
    internal_net_v4,
    internal_net_v6,
    external_ip,
    outline_ss_port,
    wgport,
    ca_cert_b64,
    sealed_ca_key,
    sealed_preshared_key,
    vm_ct_ip,
    vm_ep_ip,
    ssh_port,
    username,
    key,
    execute_remote_command,
)

# List of services to check on EPs
ep_services_to_check_all = [
    "zabbix-agent",
    "outline-ss-logger.service",
    "wg-mng.socket",
    "accel-ppp-ns@wg0.service",
    "cloak-admin-ns@wg0.service",
    "cloak-ns@wg0.service",
    # "dnsmasq-ns@wg0:*.service",
    "fakehttp-ns@ens161:wg0.service",
    "ipsec-ns@ens161:wg0.service",
    "openvpn-ns@wg0.service",
    "outline-ss-logger.service",
    "outline-ss-ns@wg0.service",
    "wg-quick-ns@wg0.service"
]

ep_services_to_check_wg = [
    "wg-quick-ns@wg0.service",
    "fakehttp-ns@ens161:wg0.service"
]

ep_services_to_check_ipsec = [
    "accel-ppp-ns@wg0.service",
    "fakehttp-ns@ens161:wg0.service",
    "ipsec-ns@ens161:wg0.service",
    "wg-quick-ns@wg0.service"
]

ep_services_to_check_openvpn = [
    "openvpn-ns@wg0.service",
    "cloak-admin-ns@wg0.service",
    "cloak-ns@wg0.service",
    "fakehttp-ns@ens161:wg0.service"
]

ep_services_to_check_outline = [
    "outline-ss-logger.service",
    "outline-ss-ns@wg0.service",
    "fakehttp-ns@ens161:wg0.service"
]

ep_services_to_check = [
    ep_services_to_check_all,
    ep_services_to_check_wg,
    ep_services_to_check_ipsec,
    ep_services_to_check_openvpn,
    ep_services_to_check_outline
]

# List of curl requests add different VPNs to EPs
curl_request_all = (
    f"{curl} '{ep_url}/?"
    f"wg_add='`{seal_key}`'&"
    f"internal-nets={internal_net_v4},{internal_net_v6}&"
    f"external-ip={external_ip}&"
    f"l2tp-preshared-key='`{sealed_preshared_key}`'&"
    f"wireguard-port={wgport}&"
    f"cloak-domain=google.com&"
    f"openvpn-ca-key='`{sealed_ca_key}`'&"
    f"openvpn-ca-crt='`{ca_cert_b64}`'&"
    f"outline-ss-port={outline_ss_port}'"
)

curl_request_wg = (
    f"{curl} '{ep_url}/?"
    f"wg_add='`{seal_key}`'&"
    f"internal-nets={internal_net_v4},{internal_net_v6}&"
    f"external-ip={external_ip}&"
    f"wireguard-port={wgport}'"
)

curl_request_ipsec = (
    f"{curl} '{ep_url}/?"
    f"wg_add='`{seal_key}`'&"
    f"internal-nets={internal_net_v4},{internal_net_v6}&"
    f"external-ip={external_ip}&"
    f"wireguard-port={wgport}&"
    f"l2tp-preshared-key='`{sealed_preshared_key}`"
)

curl_request_openvpn = (
    f"{curl} '{ep_url}/?"
    f"wg_add='`{seal_key}`'&"
    f"internal-nets={internal_net_v4},{internal_net_v6}&"
    f"external-ip={external_ip}&"
    f"wireguard-port={wgport}&"
    f"cloak-domain=google.com&"
    f"openvpn-ca-key='`{sealed_ca_key}`'&"
    f"openvpn-ca-crt='`{ca_cert_b64}`"
)

curl_request_outline = (
    f"{curl} '{ep_url}/?"
    f"wg_add='`{seal_key}`'&"
    f"internal-nets={internal_net_v4},{internal_net_v6}&"
    f"external-ip={external_ip}&"
    f"wireguard-port={wgport}&"
    f"outline-ss-port={outline_ss_port}'"
)

curl_request = [
    curl_request_all,
    curl_request_wg,
    curl_request_ipsec,
    curl_request_openvpn,
    curl_request_outline
]


easyrsa_path = '/usr/share/easy-rsa/easyrsa'
easyrsa_opts = '--batch --use-algo=ec --curve=secp521r1 --digest=sha512'


# Test function to check services after creating VPNs
def test_main():
    for index, _ in enumerate(curl_request):
        for host in [vm_ct_ip, vm_ep_ip]:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                host,
                ssh_port,
                username,
                pkey=key
            )

            if host == vm_ct_ip:
                command_add_keys = f'''sudo apt install vg-nacl easy-rsa -y && \
{easyrsa_path} {easyrsa_opts} init-pki && \
{easyrsa_path} {easyrsa_opts} --days=3650 build-ca nopass && \
EASYRSA_REQ_CN=client1 {easyrsa_path} {easyrsa_opts} gen-req client1 nopass'''
                execute_remote_command(ssh, command_add_keys)
                command_del = f"{curl} '{ep_url}/?wg_del='`{seal_key}`"
                response_del = execute_remote_command(ssh, command_del)
                assert response_del == '{"code": "0"}' or response_del == '{"code": "128", "error": "no interface found for supplied private key"}'
                command_add = curl_request[index]
                response = execute_remote_command(ssh, command_add)
                assert response == '{"code": "0"}' or response == '{"code": "0", "openvpn-client-certificate": "-----BEGIN CERTIFICATE-----\\n.*\\n-----END CERTIFICATE-----\\n"}'
            else:
                ep_services = ep_services_to_check[index]
                for service in ep_services:
                    command = f'systemctl is-active {service}'
                    print(service)
                    status = execute_remote_command(ssh, command)
                    assert status == 'active'

            ssh.close()

    host = vm_ct_ip
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        host,
        ssh_port,
        username,
        pkey=key
    )
    command_del = f"{curl} '{ep_url}/?wg_del='`{seal_key}`"
    response_del = execute_remote_command(ssh, command_del)
    assert response_del == '{"code": "0"}' or response_del == '{"code": "128", "error": "no interface found for supplied private key"}'
    ssh.close()
