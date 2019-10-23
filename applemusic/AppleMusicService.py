from datetime import datetime, timedelta

import jwt
import requests


class AppleMusicService:
    def __init__(self, secret_key, key_id, team_id):
        self.secret_key = secret_key
        self.key_id = key_id
        self.team_id = team_id
        self.algorithm = "ES256"
        self.session_length = 12
        self.url = "https://api.music.apple.com/v1"
        self.token_string = self.generate_token(self.session_length)

    def generate_token(self, session_length):
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
