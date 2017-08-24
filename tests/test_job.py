from collections import OrderedDict
from time import time
import requests

from tests.test_settings import server_uri
from tests.test_document import TestDocument


class TestJob(TestDocument):

    class BulkQuery:

        @staticmethod
        def get_active():
            return requests.get(server_uri.format(location='jobs/active'))

        @staticmethod
        def get_all():
            return requests.get(server_uri.format(location='jobs'))

    def __init__(self, name, description, tags, creator, mediator):
        self.creator = creator
        self.mediator = mediator
        self.api_uri = server_uri.format(location='jobs')
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

    @staticmethod
    def get(job_id):
        return requests.get(server_uri.format(location='jobs/{}'.format(job_id)))
