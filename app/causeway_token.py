from time import time
import jwt

from app.documents.user import User
from app.config.db import requests
from app.exceptions import BadTokenException, NonexistentDocumentException

class CausewayToken:

    secret_key = 'a5k4Zu%<>mo?|w"qlRj4LC_s,y!s@RvV5_$`"j"~)sg#bvF;WYS~E^@\\~a9aAApb'

    @classmethod
    def new(cls, user_id):
        if User.exists(user_id):
            token = cls()
            token.decoded = {
                'usr': user_id,
                'exp': time() + 600
            }
            token.encoded = jwt.encode(token.decoded, cls.secret_key)
            token.user = user_id
            return token
        else:
            raise NonexistentDocumentException('User with SIN {}.'.format(user_id))

    @classmethod
    def parse(cls, encoded_token):
        if not requests.find_one({'token': encoded_token}):
            try:
                token = cls()
                token.decoded = jwt.decode(encoded_token, cls.secret_key)
                token.encoded = encoded_token
                token.user = token.decoded['usr']
                return token
            except (jwt.exceptions.DecodeError, jwt.exceptions.ExpiredSignatureError):
                raise BadTokenException()
        else:
            print(requests.find_one({'token': encoded_token}))
            raise BadTokenException()

    def save(self, payload):
        requests.insert_one({
            'token': self.encoded,
            'user': self.user,
            'payload': payload
        })
