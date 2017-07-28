from .encrypted import EncryptedDocument
from .offer import Offer
from exceptions import NonexistentDocumentException
from config.db import jobs
import json


class Bid(EncryptedDocument):
    """
    Parent: Job
    Children: Offer
    """

    class BulkQuery:

        def __init__(self, parent_job):
            self.array = []
            for bid_in_parent in parent_job.as_dict['bids']:
                bid = Bid()
                bid.set_attributes(bid_in_parent,
                                   parent=parent_job)
                self.array.append(bid)

        def serialize(self):
            return json.dumps([bid.as_dict for bid in self.array])

    def set_expected(self):
        super().set_expected()
        self.expected_type = 'bid'

    def is_duplicate(self):
        return jobs.count({'bids.id': self.as_dict['id']}) != 0

    # FROM INCOMING REQUEST

    def save(self):
        jobs.update_one({'id': self.parent.as_dict['id']},
                        {'$addToSet': {'bids': self.as_dict}})

    # FROM DATABASE

    @classmethod
    def from_database(cls, bid_id):
        query_result = jobs.find_one({'bids.id': bid_id},
                                     {'id': 1, 'bids.$': 1, '_id': 0})
        if query_result:
            from .job import Job
            bid = cls()
            bid.set_attributes(query_result['bids'][0],
                               parent=Job.from_database(query_result['id']))
            return bid
        else:
            raise NonexistentDocumentException(bid_id)

    # FROM PARENT DOCUMENT

    @classmethod
    def from_parent(cls, parent_job, **kwargs):
        bid = cls()
        for bid_in_parent in parent_job.as_dict['bids']:
            if bid_in_parent['id'] == kwargs.get('bid_id'):
                bid = cls()
                bid.set_attributes(bid_in_parent,
                                   parent=parent_job)
            elif parent_job.as_dict['bids'].index(bid_in_parent) == len(parent_job.as_dict['bids']) - 1:
                raise NonexistentDocumentException()
        return bid

    @classmethod
    def offered_to_from_parent(cls, parent_job):
        bid = cls()
        for bid_in_parent in parent_job.as_dict['bids']:
            if 'offer' in bid_in_parent:
                bid = cls()
                bid.set_attributes(bid_in_parent,
                                   parent=parent_job)
            elif parent_job.as_dict['bids'].index(bid_in_parent) == len(parent_job.as_dict['bids']) - 1:
                raise NonexistentDocumentException()
        return bid

    # ADJACENT

    @property
    def offer(self):
        return Offer.from_parent(self)

    @offer.setter
    def offer(self, value):
        Offer.new(value, parent=self)
