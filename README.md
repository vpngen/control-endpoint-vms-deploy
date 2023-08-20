######
# Endpoint API
######

# Create brigade
curl -v 'http://[fdcc:c385:76::3]:8080/?wg_add='`echo In4ningHYWutaNHXfkE79I3BF20oKzoWiizL7l2oOSM= | nacl -b seal /etc/vg-router.json`'&internal-nets=172.16.0.1/16,fd0d:86fa:c3bc::1/64&external-ip=195.133.0.118&l2tp-preshared-key='`echo 0123456789012345 | base64 -w 0 | nacl -b seal /etc/vg-router.json`'&wireguard-port=40000&cloak-domain=google.com&openvpn-ca-key='`cat pki/private/ca.key | gzip -n | base64 -w 0 | nacl -b seal /etc/vg-router.json`'&openvpn-ca-crt='`cat pki/ca.crt | gzip -n | base64 -w 0`
# Delete brigade
curl -v 'http://[fdcc:c385:76::3]:8080/?wg_del='`echo In4ningHYWutaNHXfkE79I3BF20oKzoWiizL7l2oOSM= | nacl -b seal /etc/vg-router.json`

# Create user
curl -v 'http://[fdcc:c385:76::3]:8080/?peer_add=In4ningHYWutaNHXfkE79I3BF20oKzoWiizL7l2oOSM=&wg-public-key=dUAM1u5nOou3IH6Z07IvjkZU+7zhddqNFecgiMz3cls=&allowed-ips=172.16.0.2,fd0d:86fa:c3bc::2&control-host=fd0d:b00b::1&l2tp-username='`echo -n VPN_USERNAME1 | base64 -w 0 | nacl -b seal /etc/vg-router.json`'&l2tp-password='`echo -n VPN_USER_PASSWORD1 | base64 -w 0 | nacl -b seal /etc/vg-router.json`'&openvpn-client-csr='`cat pki/reqs/client1.req | gzip -n | base64 -w 0`
# Delete user
curl -v 'http://[fdcc:c385:76::3]:8080/?peer_del=In4ningHYWutaNHXfkE79I3BF20oKzoWiizL7l2oOSM=&wg-public-key=dUAM1u5nOou3IH6Z07IvjkZU+7zhddqNFecgiMz3cls='

# Block whole brigade
curl -v 'http://[fdcc:c385:76::3]:8080/?wg_block=dUAM1u5nOou3IH6Z07IvjkZU+7zhddqNFecgiMz3cls='
# Unblock whole brigade
curl -v 'http://[fdcc:c385:76::3]:8080/?wg_unblock=dUAM1u5nOou3IH6Z07IvjkZU+7zhddqNFecgiMz3cls='

# Set user bandwidth limits
curl -v 'http://[fdcc:c385:76::3]:8080/?bw_set=In4ningHYWutaNHXfkE79I3BF20oKzoWiizL7l2oOSM=&wg-public-key=dUAM1u5nOou3IH6Z07IvjkZU+7zhddqNFecgiMz3cls=&up-kbit=100&down-kbit=100'
# Unset user bandwidth limits
curl -v 'http://[fdcc:c385:76::3]:8080/?bw_unset=In4ningHYWutaNHXfkE79I3BF20oKzoWiizL7l2oOSM=&wg-public-key=dUAM1u5nOou3IH6Z07IvjkZU+7zhddqNFecgiMz3cls='
