from collections import OrderedDict
from bip32utils import BIP32Key, BIP32_HARDEN
from hashlib import sha256, sha512
from unicodedata import normalize
from binascii import hexlify
from pbkdf2 import PBKDF2
from os import urandom
from time import time
import requests
import hmac
import json

from tests.test_settings import server_uri
from tests.test_document import TestDocument


class TestUser(TestDocument):

    def __init__(self, name, mediator=False):
        self.name = name
        self.type = 'user'
        self.as_dict = OrderedDict({
            'type': self.type,
            'login': name,
            'created_at': int(time()),
            'email': '{}@example.com'.format(name),
            'addresses': OrderedDict({
                'master': self.master_address,
                'delegate': self.delegate_address
            })
        })
        if mediator:
            self.as_dict['mediator'] = OrderedDict({
                'fee': 1.0,
                'pubkey': self.delegate_public_key
            })
        self.creator = self
        self.obtain_id()
        self.sign()

    def send(self):
        return requests.post(server_uri.format(location='users/add'), data={'payload': json.dumps(self.as_dict)})

    @property
    def mnemonic(self):
        try:
            return self._mnemonic
        except AttributeError:
            # Seed + checksum
            strength = 128
            entropy = urandom(strength // 8)
            bin_entropy = bin(int(hexlify(entropy), 16))[2:].zfill(strength)
            checksum = bin(int(sha256(entropy).hexdigest(), 16))[2:].zfill(256)[:4]
            bin_mnemonic = bin_entropy + checksum
            # Binary to words
            cursor = 0
            mnemonic = []
            with open('./english.json') as words_file:
                words = json.loads(words_file.read())
                while cursor < len(bin_mnemonic):
                    index = int(bin_mnemonic[cursor:cursor + 11], 2)
                    mnemonic.append(words[index])
                    cursor += 11
            self.mnemonic = normalize('NFKD', ' '.join(mnemonic))
            return self._mnemonic

    @mnemonic.setter
    def mnemonic(self, value):
        self._mnemonic = value

    @property
    def seed(self):
        try:
            return self._seed
        except AttributeError:
            self.seed = PBKDF2(self.mnemonic, u'mnemonic', iterations=2048, macmodule=hmac, digestmodule=sha512).read(64)
            return self._seed

    @seed.setter
    def seed(self, value):
        self._seed = value

    @property
    def key(self):
        try:
            return self._key
        except AttributeError:
            secret, chain = self.seed[:32], self.seed[32:]
            self.key = BIP32Key(secret=secret, chain=chain, depth=0, index=0, fpr=b'\0\0\0\0', public=False)
            return self._key

    @key.setter
    def key(self, value):
        self._key = value

    @property
    def master_private_key(self):
        try:
            return self._master_private_key
        except AttributeError:
            self._master_private_key = self.key.ChildKey(0).WalletImportFormat()
            return self._master_private_key

    @property
    def master_public_key(self):
        try:
            return self._master_public_key
        except AttributeError:
            key = self.key.ChildKey(0)
            key.SetPublic()
            self._master_public_key = hexlify(key.PublicKey()).decode('utf-8')
            return self._master_public_key

    @property
    def master_address(self):
        try:
            return self._master_address
        except AttributeError:
            key = self.key.ChildKey(0)
            key.SetPublic()
            self._master_address = key.Address()
            return self._master_address

    @property
    def delegate_private_key(self):
        try:
            return self._delegate_private_key
        except AttributeError:
            self._delegate_private_key = self.key.ChildKey(1 + BIP32_HARDEN).WalletImportFormat()
            return self._delegate_private_key

    @property
    def delegate_public_key(self):
        try:
            return self._delegate_public_key
        except AttributeError:
            key = self.key.ChildKey(1 + BIP32_HARDEN)
            key.SetPublic()
            self._delegate_public_key = hexlify(key.PublicKey()).decode('utf-8')
            return self._delegate_public_key

    @property
    def delegate_address(self):
        try:
            return self._delegate_address
        except AttributeError:
            key = self.key.ChildKey(1 + BIP32_HARDEN)
            key.SetPublic()
            self._delegate_address = key.Address()
            return self._delegate_address
