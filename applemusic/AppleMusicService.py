import json
from datetime import datetime, timedelta

import jwt
import requests
import time
from requests.exceptions import HTTPError


class AppleMusicService:
    def __init__(self, secret_key_file, key_id, team_id, max_retries=2, session_length=12, requests_timeout=None):
        with open(secret_key_file, 'r') as f:
            self.secret_key = f.read()

        self.key_id = key_id
        self.team_id = team_id
        self.algorithm = "ES256"
        self.session_length = session_length
        self.max_retries = max_retries
        self.url = "https://api.music.apple.com/v1"
        self.token_string = self._generate_token(self.session_length)
        self.session = requests.Session()
        self.requests_timeout = requests_timeout

    def _generate_token(self, session_length):
        headers = {
            "alg": self.algorithm,
            "kid": self.key_id
        }
        payload = {
            "iss": self.team_id,
            "iat": int(datetime.now().timestamp()),
            "exp": int((datetime.now() + timedelta(hours=session_length)).timestamp())
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm, headers=headers)
        return token.decode()

    def _auth_headers(self):
        """
        Get header for API request
        :return: header in dictionary format
        """
        if self.token_string:
            return {'Authorization': 'Bearer {}'.format(self.token_string)}
        else:
            return {}

    def _call(self, method, url, params):
        """
        Make a call to the API
        :param method: 'GET', 'POST', 'DELETE', or 'PUT'
        :param url: URL of API endpoint
        :param params: API paramaters
        :return: JSON data from the API
        """
        if not url.startswith('http'):
            url = self.url + url
        headers = self._auth_headers()
        headers['Content-Type'] = 'application/json'

        r = self.session.request(method, url,
                                 headers=headers,
                                 proxies=[],
                                 params=params,
                                 timeout=self.requests_timeout)
        r.raise_for_status()  # Check for error
        return r.json()

    def _get(self, url, **kwargs):
        """
        GET request from the API
        :param url: URL for API endpoint
        :return: JSON data from the API
        """
        retries = self.max_retries
        delay = 1
        while retries > 0:
            try:
                return self._call('GET', url, kwargs)
            except HTTPError as e:  # Retry for some known issues
                retries -= 1
                status = e.response.status_code
                if status == 429 or (500 <= status < 600):
                    if retries < 0:
                        raise
                    else:
                        sleep_seconds = int(e.response.headers.get('Retry-After', delay))
                        print('retrying ...' + str(sleep_seconds) + ' secs')
                        time.sleep(sleep_seconds + 1)
                        delay += 1
                else:
                    raise
            except Exception as e:
                print('exception', str(e))
                retries -= 1
                if retries >= 0:
                    print('retrying ...' + str(delay) + 'secs')
                    time.sleep(delay + 1)
                    delay += 1
                else:
                    raise

    def _post(self, url, **kwargs):
        return self._call('POST', url, kwargs)

    def _delete(self, url, **kwargs):
        return self._call('DELETE', url, kwargs)

    def _put(self, url, **kwargs):
        return self._call('PUT', url, kwargs)

    def get_playlists(self):
        data = self._get("/me/library/playlists")
        print(data)


if __name__ == '__main__':
    with open("config.json") as json_file:
        configuration = json.load(json_file)
    service = AppleMusicService(
        configuration["secret_key_file"],
        configuration["key_id"],
        configuration["team_id"]
    )
    print(service.get_playlists())
