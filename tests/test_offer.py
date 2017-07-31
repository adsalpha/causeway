from bitcoin.core import x, b2x
from bitcoin.core.script import CScript, OP_CHECKMULTISIG
from bitcoin.wallet import CBitcoinAddress
from collections import OrderedDict
from time import time
import requests
import json

from tests.test_settings import server_uri
from tests.test_encrypted_document import TestEncryptedDocument



class TestOffer(TestEncryptedDocument):

    def __init__(self, bid):
        self.bid = bid
        self.creator = self.bid.job.creator
        self.type = 'offer'
        worker_redeem_script = CScript([2,
                                        x(self.bid.creator.delegate_public_key),
                                        x(self.creator.delegate_public_key),
                                        x(self.bid.job.mediator.delegate_public_key),
                                        3,
                                        OP_CHECKMULTISIG])
        worker_escrow_address = str(CBitcoinAddress.from_scriptPubKey(worker_redeem_script.to_p2sh_scriptPubKey()))
        mediator_redeem_script = CScript([2,
                                         x(self.creator.delegate_public_key),
                                         x(self.bid.creator.delegate_public_key),
                                         x(self.bid.job.mediator.delegate_public_key),
                                         3,
                                         OP_CHECKMULTISIG])
        mediator_escrow_address = str(CBitcoinAddress.from_scriptPubKey(mediator_redeem_script.to_p2sh_scriptPubKey()))
        self.as_dict = OrderedDict({
            'type': self.type,
            'bid': OrderedDict({
                'id': self.bid['id'],
                'url': server_uri.format(location='jobs/{}/bids/{}'.format(self.bid.job['id'], self.bid['id']))
            }),
            'created_at': int(time()),
            'worker_escrow': OrderedDict({
                'address': worker_escrow_address,
                'pubkey': self.bid.creator.delegate_public_key,
                'redeem_script': b2x(worker_redeem_script),
                'tx_fee': .002
            }),
            'mediator_escrow': OrderedDict({
                'address': mediator_escrow_address,
                'pubkey': self.bid.job.mediator.delegate_public_key,
                'redeem_script': b2x(mediator_redeem_script),
                'tx_fee': .002
            }),
            'creator_refund': OrderedDict({
                'address': self.creator.delegate_address,
                'pubkey': self.creator.delegate_public_key,
            })
        })
        self.encrypt()
        self.obtain_id()
        self.sign()

    def send(self):
        return requests.post(
            server_uri.format(location='jobs/{}/bids/{}/offer'.format(self.bid.job['id'], self.bid['id'])),
            data={'payload': json.dumps(self.as_dict),
                  'user': self.nonce['user'],
                  'nonce': self.nonce['nonce']}
        )
