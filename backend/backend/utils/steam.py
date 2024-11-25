import urllib
from urllib.parse import urlencode
import urllib.request
import re

from backend.core.settings import settings


class SteamOID:
    _steam_openid_url = 'https://steamcommunity.com/openid/login'

    @staticmethod
    def create_url() -> str:
        params = {
            'openid.ns': 'http://specs.openid.net/auth/2.0',
            'openid.mode': 'checkid_setup',
            'openid.return_to': f'{settings.SERVER_URL}/auth/steam/callback',
            'openid.realm': f'{settings.SERVER_URL}',
            # 'openid.ns.sreg': "http://openid.net/extensions/sreg/1.1",
            'openid.identity': "http://specs.openid.net/auth/2.0/identifier_select",
            'openid.claimed_id': "http://specs.openid.net/auth/2.0/identifier_select",
        }
        query_string = urlencode(params)
        auth_url = SteamOID._steam_openid_url + "?" + query_string
        return auth_url

    @staticmethod
    def validate_response(callback_data: dict) -> str:
        validation_args = {
            'openid.assoc_handle': callback_data['openid.assoc_handle'],
            'openid.signed': callback_data['openid.signed'],
            'openid.sig': callback_data['openid.sig'],
            'openid.ns': callback_data['openid.ns'],
        }
        signed_args = callback_data['openid.signed'].split(',')

        for item in signed_args:
            item_arg = f'openid.{item}'
            if callback_data[item_arg] not in validation_args:
                validation_args[item_arg] = callback_data[item_arg]

        validation_args['openid.mode'] = 'check_authentication'
        parsed_args = urlencode(validation_args).encode("utf-8")

        with urllib.request.urlopen(SteamOID._steam_openid_url, parsed_args) as request_data:
            response = request_data.read().decode('utf-8')

        if re.search('is_valid:true', response):
            matched = re.search(r'https://steamcommunity.com/openid/id/(\d+)', callback_data['openid.claimed_id'])
            if matched and matched.group(1):
                return matched.group(1)
            else:
                return False
        else:
            return False
