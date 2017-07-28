from tests.test_settings import server_uri
from tests.test_encrypted_document import TestEncryptedDocument
from collections import OrderedDict
from time import time
import requests
import json


class TestDisputeResolution(TestEncryptedDocument):

    def __init__(self, winner, description, dispute):
        self.dispute = dispute
        self.creator = self.dispute.job.mediator
        self.type = 'dispute_resolution'
        self.as_dict = OrderedDict({
            'type': self.type,
            'dispute': OrderedDict({
                'id': self.dispute['id'],
                'url': server_uri.format(location='jobs/{}/dispute'.format(self.dispute.job['id']))
            }),
            'created_at': int(time()),
            'winner': OrderedDict({
                'login': winner['login'],
                'email': winner['email'],
                'url': server_uri.format(location='users/{}'.format(winner['login']))
            }),
            'description': description,
        })
        self.encrypt()
        self.obtain_id()
        self.sign()

    def send(self):
        return requests.post(
            server_uri.format(location='jobs/{}/dispute/resolution/add'.format(self.dispute.job['id'])),
            data={'payload': json.dumps(self.as_dict),
                  'user': self.nonce['user'],
                  'nonce': self.nonce['nonce']}
        )
