from tests.test_settings import server_uri
from tests.test_encrypted_document import TestEncryptedDocument
from collections import OrderedDict
from time import time
import requests
import json


class TestDelivery(TestEncryptedDocument):

    def __init__(self, description, worker, job):
        self.creator = worker
        self.job = job
        self.type = 'delivery'
        self.as_dict = OrderedDict({
            'type': self.type,
            'job': OrderedDict({
                'id': self.job['id'],
                'url': server_uri.format(location='jobs/{}'.format(self.job['id']))
            }),
            'created_at': int(time()),
            'description': description,
            'worker_payment': OrderedDict({
                'inputs': 'dummy-inputs',
                'address': worker.delegate_address,
                'amount': 0.33,
                'sig': ['dummy-signature1']
            }),
            'mediator_payment': OrderedDict({
                'inputs': 'dummy-inputs',
                'address': job.mediator.delegate_address,
                'amount': job.mediator['mediator']['fee'] * 0.33,
                'sig': ['dummy-signature2']
            })
        })
        self.encrypt()
        self.obtain_id()
        self.sign()

    def send(self):
        return requests.post(server_uri.format(location='jobs/{}/delivery/add'.format(self.job['id'])),
                             data={'payload': json.dumps(self.as_dict),
                                   'user': self.nonce['user'],
                                   'nonce': self.nonce['nonce']})

    @staticmethod
    def get(job_id):
        return requests.get(server_uri.format(location='jobs/{}/delivery'.format(job_id)))
