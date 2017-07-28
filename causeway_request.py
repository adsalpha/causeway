from documents.user import User
from config.db import requests
from uuid import uuid4
from time import time
from exceptions import NonexistentDocumentException
import json


class CausewayRequest:

    # def __init__(self):
    #     raise NotImplementedError('Use the `new` or the `validate` class methods to create a request object.')

    @property
    def as_dict(self):
        try:
            return self._as_dict
        except AttributeError:
            raise NotImplementedError('Use the `new` or the `validate` class methods to create a request object '
                                      'with as_dict set correctly.')

    @as_dict.setter
    def as_dict(self, value: dict):
        self._as_dict = value

    def serialize(self):
        self.as_dict.pop('_id', None)
        return json.dumps(self.as_dict)

    # New

    @classmethod
    def new(cls, user: str):
        request = cls()
        try:
            user = User.from_database(user)
            request.as_dict = {'user': user.as_dict['id'], 'nonce': str(uuid4()), 'expiration': int(time()) + 600}
            requests.insert(request.as_dict)
            return request
        except:
            raise NonexistentDocumentException('User with SIN {}.'.format(user))

    # Validate

    @classmethod
    def validate(cls, user: str, nonce: str):
        request = cls()
        request.as_dict = {'user': user, 'nonce': nonce}
        db_request = requests.find_one(request.as_dict)
        if db_request and db_request['expiration'] > time() and 'payload' not in db_request:
            return request
        else:
            raise ValueError('Can not find valid request with nonce {} from user {} expiring after {}.'
                             .format(nonce, user, int(time())))

    def update(self, payload: str):
        try:
            id = json.loads(payload)['id']
            requests.update_one(self.as_dict,
                                {'$set': {'payload': payload, 'document_id': id}})
            self.as_dict['payload'] = payload
            self.as_dict['document_id'] = id
        except:
            raise ValueError('Bad payload.')

    # From document ID

    @classmethod
    def from_database(cls, document_id: str):
        db_request = requests.find_one({'document_id': document_id}, {'_id': 0})
        if db_request:
            request = cls()
            request.as_dict = db_request
            return request
        else:
            raise NonexistentDocumentException(document_id)
