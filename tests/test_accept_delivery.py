from collections import OrderedDict
from time import time

from tests.test_settings import server_uri
from tests.test_encrypted_document import TestEncryptedDocument


class TestAcceptDelivery(TestEncryptedDocument):

    def __init__(self, delivery):
        self.delivery = delivery
        self.creator = self.delivery.job.creator
        self.type = 'accept_delivery'
        self.api_uri = server_uri.format(location='jobs/{}/delivery/acceptance'.format(self.delivery.job['id']))
        self.as_dict = OrderedDict({
            'type': self.type,
            'delivery': OrderedDict({
                'id': self.delivery['id'],
                'uri': server_uri.format(location='jobs/{}/delivery'.format(self.delivery.job['id']))
            }),
            'created_at': int(time()),
            'worker_payment': OrderedDict({
                'amount': 0.33,
                'txid': 'dummy-txid-1',
                'sig': ['dummy-signature-1']
            }),
            'mediator_payment': OrderedDict({
                'amount': self.delivery.job.mediator['mediator']['fee'] * 0.33,
                'txid': 'dummy-txid-2',
                'sig': ['dummy-signature-2']
            })
        })
        self.encrypt()
        self.obtain_id()
        self.sign()
