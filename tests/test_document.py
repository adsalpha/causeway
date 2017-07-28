from tests.test_settings import server_uri
from abc import ABC, abstractmethod
from collections import OrderedDict
from bitcoin.wallet import CBitcoinSecret
from bitcoin.signmessage import BitcoinMessage, SignMessage
from hashlib import sha256
import requests
import json


class TestDocument(ABC):

    def encrypt(self):
        raise NotImplementedError('Expecting for this to be implemented by subclasses.')

    def obtain_id(self):
        self['id'] = self.id
        self.as_dict.move_to_end('id', last=False)

    def sign(self):
        self['validity'] = self.validity

    @abstractmethod
    def send(self):
        return

    @property
    def nonce(self):
        try:
            return self._nonce
        except AttributeError:
            self._nonce = json.loads(
                requests.get(server_uri.format(location='nonce'), data={'user': self.creator['id']}).content
            )
            return self._nonce

    def refresh_nonce(self):
        self._nonce = json.loads(
            requests.get(server_uri.format(location='nonce'), data={'user': self.creator['id']}).content
        )

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
