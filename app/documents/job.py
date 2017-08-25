import json

from app.config.db import jobs
from app.exceptions import NonexistentDocumentException
from .bid import Bid
from .delivery import Delivery
from .dispute import Dispute
from .unencrypted import UnencryptedDocument


class Job(UnencryptedDocument):
    """
    Children: Bid, Delivery, Dispute
    """

    class BulkQuery:

        def __init__(self, active_only=False):
            if active_only:
                query = {'finished': False}
            else:
                query = {}
            db_jobs = jobs.find(query, {'_id': 0})
            self.array = []
            for db_job in db_jobs:
                job = Job()
                job.set_attributes(db_job)
                self.array.append(job)

        def serialize(self):
            return json.dumps([job.as_dict for job in self.array])

    def set_expected(self):
        self.expected_structure = [
            {'time': ['created_at', 'bidding_closes_at']},
            'name',
            'description',
            'tags',
            {'creator': ['login', 'email', 'url']},
            {'mediator': ['login', 'email', 'fee', 'url']}
        ]
        self.expected_type = 'job'

    def is_duplicate(self):
        return jobs.count({'id': self.as_dict['id']}) != 0

    def finish(self):
        jobs.update_one({'id': self.as_dict['id']}, {'$set': {'finished': True}})

    # FROM INCOMING REQUEST

    def save(self):
        jobs.insert(self.as_dict)

    # FROM DATABASE

    @classmethod
    def from_database(cls, document_id):
        db_job = jobs.find_one({'id': document_id}, {'_id': 0})
        if db_job:
            job = cls()
            job.set_attributes(db_job)
            return job
        else:
            raise NonexistentDocumentException(document_id)

    # ADJACENT

    def get_bid(self, bid_id):
        return Bid.from_parent(self, bid_id=bid_id)

    def add_bid(self, payload):
        Bid.new(payload, parent=self)

    def all_bids(self):
        return Bid.BulkQuery(self)

    def bid_offered_to(self):
        return Bid.offered_to_from_parent(self)

    def get_delivery(self):
        return Delivery.from_parent(self)

    def set_delivery(self, delivery):
        Delivery.new(delivery, parent=self)

    def get_dispute(self):
        return Dispute.from_parent(self)

    def set_dispute(self, dispute):
        Dispute.new(dispute, parent=self)
