from documents.document import Document
from copy import deepcopy
from hashlib import sha256
from bitcoin.signmessage import BitcoinMessage, VerifyMessage
import json


class UnencryptedDocument(Document):
    """
    Unencrypted documents should subclass this.
    """

    def validate(self):
        super().validate()
        if not self.id_ok():
            raise ValueError('The ID of the document is not the hash of its contents.')
        if not self.signature_ok():
            raise ValueError('Bad Bitcoin signature.')

    def id_ok(self):
        """
        Checks if the document ID is the hash of its contents.
        """
        as_dict_copy = deepcopy(self.as_dict)
        document_id = as_dict_copy.pop('id')
        # Need to exclude this as documents are first hashed to obtain the ID, then signed with Bitcoin.
        as_dict_copy.pop('validity')
        if document_id == sha256(json.dumps(as_dict_copy).encode('utf-8')).hexdigest():
            return True
        else:
            return False

    def signature_ok(self):
        """
        Checks if the signature of a document is valid.
        """
        as_dict_copy = deepcopy(self.as_dict)
        validity = as_dict_copy.pop('validity')
        if VerifyMessage(validity['signature_address'], BitcoinMessage(json.dumps(as_dict_copy)), validity['signature']):
            return True
        else:
            return False
