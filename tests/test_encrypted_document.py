from collections import OrderedDict
from hashlib import sha256
import json

from tests.test_document import TestDocument


class TestEncryptedDocument(TestDocument):

    # Using some ultra-dummy encryption for adjacent documents which is in fact hashing.
    # Please never use that in production.
    def encrypt(self):
        self.as_dict = OrderedDict({
            'type': self.type,
            'id': self.id,
            'encrypted_contents': sha256(json.dumps(self.as_dict).encode('utf-8')).hexdigest()
        })
