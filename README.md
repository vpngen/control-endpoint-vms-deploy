######
# Endpoint API
######

# Create brigade
curl -v 'http://[fdcc:c385:76::3]:8080/?wg_add='`echo In4ningHYWutaNHXfkE79I3BF20oKzoWiizL7l2oOSM= | nacl -b seal /etc/vg-router.json`'&internal-nets=172.16.0.1/16,fd0d:86fa:c3bc::1/64&external-ip=195.133.0.118&l2tp-preshared-key='`echo 0123456789012345 | base64 -w 0 | nacl -b seal /etc/vg-router.json`'&wireguard-port=40000&cloak-domain=google.com&openvpn-ca-key='`cat pki/private/ca.key | gzip -n | base64 -w 0 | nacl -b seal /etc/vg-router.json`'&openvpn-ca-crt='`cat pki/ca.crt | gzip -n | base64 -w 0`'&outline-ss-port=9944'
# Delete brigade
curl -v 'http://[fdcc:c385:76::3]:8080/?wg_del='`echo In4ningHYWutaNHXfkE79I3BF20oKzoWiizL7l2oOSM= | nacl -b seal /etc/vg-router.json`

# Create user
curl -v 'http://[fdcc:c385:76::3]:8080/?peer_add=In4ningHYWutaNHXfkE79I3BF20oKzoWiizL7l2oOSM=&wg-public-key=dUAM1u5nOou3IH6Z07IvjkZU+7zhddqNFecgiMz3cls=&allowed-ips=172.16.0.2,fd0d:86fa:c3bc::2&control-host=fd0d:b00b::1&l2tp-username='`echo -n VPN_USERNAME1 | base64 -w 0 | nacl -b seal /etc/vg-router.json`'&l2tp-password='`echo -n VPN_USER_PASSWORD1 | base64 -w 0 | nacl -b seal /etc/vg-router.json`'&openvpn-client-csr='`cat pki/reqs/client1.req | gzip -n | base64 -w 0`'&cloak-uid='`echo RlT7vOF12o0V5yCIzPdyWw== | nacl -b seal /etc/vg-router.json`'&outline-ss-password='`echo -n hjG_leNCXm6Yu5n7G_zZIxnfDBm_s7@e9cT0wxaJQX5bZtqzk_ka1jQsHbzBRHhx | base64 -w 0 | nacl -b seal /etc/vg-router.json`
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

# Testing


## Docker

In docker directory, Dockerfiles are provided for creating images used by the runner. Additionally, a systemd script "dckr_net_connector.service" is included for connecting the runner's container to the network of client VPN containers.

Images are automatically built through the GitHub Actions pipeline and stored in a local registry on testing-management vm.

### Pipeline Structure

1. **docker-build:** Builds images if changes have been made to the Dockerfiles and pushes them to the registry.
2. **terraform-build:** Deploys a test environment with two nodes (endpoint and control).
3. **client-containers:** Launches containers for VPN clients.
4. **tests:** Executes tests.
5. **destroy-terraform:** Destroys the test environment.
6. **destroy-containers:** Disconnects the script adding the runner's container to the test network.

### Tests

- **test_brigade.py:** Creates and deletes a brigade via the API endpoint.
- **test_connection.py:** Tests client connections.
- **test_deploy.py:** Checks for successful stand creation and installation of all necessary dependencies.
- **test_keydesk_api.py:** Creates and deletes a brigade via the Keydesk API.

### Debugging Instructions

- If tests fail, the stand persists. Debug the error on the stand and rerun the tests.
- If Terraform fails to create the stand, try clearing the directory /opt/runner-custom/terraform/ on the testing-management VM before rerunning the pipeline.

### TODO

- Add negative testing scenarios.
- Add testing for statistics.
- Add testing for Amnezia VPN and Outline-SS.
- Reduce hardcoded values.
- Use fixtures.
- Create a script to wait for a successful stand deployment (instead of the current sleep).
- Add print statements for debugging.
- Add  several stands and a queue for using the stands


