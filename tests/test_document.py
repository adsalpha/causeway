from abc import ABC
from collections import OrderedDict
from bitcoin.wallet import CBitcoinSecret
from bitcoin.signmessage import BitcoinMessage, SignMessage
from hashlib import sha256
import requests
import json

from tests.test_settings import server_uri


class TestDocument(ABC):

    @property
    def api_uri(self):
        try:
            return self._api_uri
        except AttributeError:
            raise NotImplementedError('Documents must define the API URI they shall be sent to.')

    @api_uri.setter
    def api_uri(self, value):
        self._api_uri = value

    @property
    def as_dict(self):
        try:
            return self._as_dict
        except AttributeError:
            raise NotImplementedError('Documents must define a dict representation that is sent to server.')

    @as_dict.setter
    def as_dict(self, value):
        self._as_dict = value

    def __getitem__(self, item):
        return self.as_dict[item]

    def __setitem__(self, key, value):
        try:
            self.as_dict[key] = value
        except AttributeError:
            self.as_dict = {key: value}

    @property
    def id(self):
        return sha256(json.dumps(self.as_dict).encode('utf-8')).hexdigest()

    @property
    def type(self):
        try:
            return self._type
        except AttributeError:
            raise NotImplementedError('Documents must have a type.')

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def validity(self):
        return OrderedDict({
            'signature': SignMessage(CBitcoinSecret(self.creator.delegate_private_key),
                                     BitcoinMessage(json.dumps(self.as_dict))).decode('utf-8'),
            'signature_address': self.creator.delegate_address
        })

    @property
    def creator(self):
        try:
            return self._creator
        except AttributeError:
            raise NotImplementedError('Documents must be created by somebody.')

    @creator.setter
    def creator(self, value):
        self._creator = value

    @property
    def token(self):
        try:
            return self._token
        except AttributeError:
            return self.new_token()

    def new_token(self):
        self._token = requests.get(
            server_uri.format(location='token'),
            data={'user_id': self.creator['id']}
        ).json()['token']
        return self.token

    def encrypt(self):
        raise NotImplementedError('Expecting for this to be implemented by subclasses.')

    def obtain_id(self):
        self['id'] = self.id
        self.as_dict.move_to_end('id', last=False)

    def sign(self):
        self['validity'] = self.validity

    def send(self):
        return requests.post(
            self.api_uri,
            data={'payload': json.dumps(self.as_dict),
                  'token': self.token}
        )
