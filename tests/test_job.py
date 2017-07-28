from tests.test_settings import server_uri
from tests.test_document import TestDocument
from collections import OrderedDict
from time import time
import requests
import json


class TestJob(TestDocument):

    class BulkQuery:

        @staticmethod
        def get_active():
            return requests.get(server_uri.format(location='jobs/active'))

        @staticmethod
        def get_all():
            return requests.get(server_uri.format(location='jobs/all'))

    def __init__(self, name, description, tags, creator, mediator):
        self.creator = creator
        self.mediator = mediator
        self.as_dict = OrderedDict({
            'type': 'job',
            'time': {
                'created_at': int(time()),
                'bidding_closes_at': int(time()) + 100000,
            },
            'name': name,
            'description': description,
            'tags': tags,
            'creator': OrderedDict({
                'login': creator['login'],
                'email': creator['email'],
                'url': server_uri.format(location='users/{}'.format(creator['login']))
            }),
            'mediator': OrderedDict({
                'login': mediator['login'],
                'email': mediator['email'],
                'url': server_uri.format(location='users/{}'.format(mediator['login'])),
                'fee': mediator['mediator']['fee']
            })
        })
        self.obtain_id()
        self.sign()

    def send(self):
        return requests.post(server_uri.format(location='jobs/add'), data={'payload': json.dumps(self.as_dict),
                                                                           'user': self.nonce['user'],
                                                                           'nonce': self.nonce['nonce']})

    @staticmethod
    def get(job_id):
        return requests.get(server_uri.format(location='jobs/{}'.format(job_id)))
