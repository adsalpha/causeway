from collections import OrderedDict
from time import time
import requests

from tests.test_settings import server_uri
from tests.test_encrypted_document import TestEncryptedDocument


class TestBid(TestEncryptedDocument):

    class BulkQuery:

        @staticmethod
        def get(job_id):
            return requests.get(server_uri.format(location='jobs/{}/bids'.format(job_id)))

    def __init__(self, description, worker, job):
        self.creator = worker
        self.job = job
        self.type = 'bid'
        self.api_uri = server_uri.format(location='jobs/{}/bids'.format(self.job['id']))
        self.as_dict = OrderedDict({
            'type': self.type,
            'job': OrderedDict({
                'id': self.job['id'],
                'url': server_uri.format(location='jobs/{}'.format(self.job['id']))
            }),
            'created_at': int(time()),
            'worker': OrderedDict({
                'login': worker['login'],
                'email': worker['email'],
                'url': server_uri.format(location='users/{}'.format(worker['login']))
            }),
            'description': description,
            'amount': 0.33
        })
        self.encrypt()
        self.obtain_id()
        self.sign()

    @staticmethod
    def get(job_id, bid_id):
        return requests.get(server_uri.format(location='jobs/{}/bids/{}'.format(job_id, bid_id)))
