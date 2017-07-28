from .encrypted import EncryptedDocument
from exceptions import NonexistentDocumentException
from config.db import jobs


class Offer(EncryptedDocument):
    """
    Parent: Bid
    """

    def set_expected(self):
        super().set_expected()
        self.expected_type = 'offer'

    def is_duplicate(self):
        return jobs.count({'id': self.parent.parent.as_dict['id'], 'bids.offer': {'$exists': True}}) != 0

    # FROM INCOMING REQUEST

    def save(self):
        jobs.update_one({'bids.id': self.parent.as_dict['id']},
                        {'$set': {'bids.$.offer': self.as_dict}})

    # FROM DATABASE

    @classmethod
    def from_database(cls, offer_id):
        query_result = jobs.find_one({'bids.offer.id': offer_id},
                                     {'id': 1, 'bids.$.offer': 1, '_id': 0})
        if query_result:
            from .bid import Bid
            offer = cls()
            offer.set_attributes(query_result['bids'][0]['offer'],
                                 parent=Bid.from_database(query_result['bids'][0]['id']))
            return offer
        else:
            raise NonexistentDocumentException(offer_id)

    # FROM PARENT DOCUMENT

    @classmethod
    def from_parent(cls, parent_bid, **kwargs):
        offer = cls()
        try:
            offer.set_attributes(parent_bid.as_dict['offer'],
                                 parent=parent_bid)
        except KeyError:
            raise NonexistentDocumentException('Offer for bid {}.'.format(parent_bid.as_dict['id']))
        return offer
