from collections import OrderedDict
from time import time
import requests
import json

from tests.test_settings import server_uri
from tests.test_encrypted_document import TestEncryptedDocument


class TestAcceptDisputeResolution(TestEncryptedDocument):

    def __init__(self, dispute):
        self.dispute = dispute
        self.creator = self.dispute.job.creator
        self.type = 'accept_dispute_resolution'
        self.as_dict = OrderedDict({
            'type': self.type,
            'dispute': OrderedDict({
                'id': self.dispute['id'],
                'url': server_uri.format(location='jobs/{}/dispute'.format(self.dispute.job['id']))
            }),
            'created_at': int(time()),
            'worker_payment': OrderedDict({
                'amount': 0.18,
                'txid': 'dummy-txid-1',
                'sig': ['dummy-signature-1']
            }),
            'mediator_payment': OrderedDict({
                'amount': self.dispute.job.mediator['mediator']['fee'] * 0.33,
                'txid': 'dummy-txid-2',
                'sig': ['dummy-signature-2']
            }),
            'creator_refund': OrderedDict({
                'amount': 0.15,
                'txid': 'dummy-txid-3',
                'sig': ['dummy-signature-3']
            })
        })
        self.encrypt()
        self.obtain_id()
        self.sign()

    def send(self):
        return requests.post(
            server_uri.format(location='jobs/{}/dispute/resolution/accept'.format(self.dispute.job['id'])),
            data={'payload': json.dumps(self.as_dict),
                  'user': self.nonce['user'],
                  'nonce': self.nonce['nonce']}
        )
