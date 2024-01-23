import base64
import json
import zlib


def decode_amnezia(s: str):
    return json.loads(
        zlib.decompress(
            base64.urlsafe_b64decode(
                base64_padding(s.removeprefix('vpn://'))
            )[4:]
        ).decode('utf-8')
    )


def decode_outline(s: str):
    l, _ = s.removeprefix('ss://').split('#')
    return base64.b64decode(base64_padding(l)).decode()


def base64_padding(s: str):
    return s + '=' * (4 - len(s) % 4)


def get_cloak_config(amnezia_config: dict) -> str:
    return amnezia_config['containers'][0]['cloak']['last_config']


def get_openvpn_config(amnezia_config: dict) -> str:
    return json.loads(
        amnezia_config['containers'][0]['openvpn']['last_config']
    )['config']
