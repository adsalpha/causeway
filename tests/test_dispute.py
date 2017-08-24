from collections import OrderedDict
from time import time
import requests

from tests.test_settings import server_uri
from tests.test_encrypted_document import TestEncryptedDocument


class TestDispute(TestEncryptedDocument):

    def __init__(self, description, creator, job):
        self.creator = creator
        self.job = job
        self.type = 'dispute'
        self.api_uri = server_uri.format(location='jobs/{}/dispute'.format(self.job['id']))
        self.as_dict = OrderedDict({
            'type': self.type,
            'job': OrderedDict({
                'id': self.job['id'],
                'url': server_uri.format(location='jobs/{}'.format(self.job['id']))
            }),
            'created_at': int(time()),
            'source': OrderedDict({
                'login': creator['login'],
                'email': creator['email'],
                'url': server_uri.format(location='users/{}'.format(creator['login']))
            }),
            'description': description,
        })
        self.encrypt()
        self.obtain_id()
        self.sign()

    @staticmethod
    def get(job_id):
        return requests.get(server_uri.format(location='jobs/{}/dispute'.format(job_id)))
