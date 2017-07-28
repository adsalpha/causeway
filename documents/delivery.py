from .encrypted import EncryptedDocument
from .accept_delivery import AcceptDelivery
from exceptions import NonexistentDocumentException
from config.db import jobs


class Delivery(EncryptedDocument):
    """
    Parent: Job
    Child: AcceptDelivery
    """

    def set_expected(self):
        super().set_expected()
        self.expected_type = 'delivery'

    def is_duplicate(self):
        return jobs.count({'id': self.parent.as_dict['id'], 'delivery': {'$exists': True}}) != 0

    # FROM INCOMING REQUEST

    def save(self):
        jobs.update_one({'id': self.parent.as_dict['id']},
                        {'$set': {'delivery': self.as_dict}})

    # FROM DATABASE

    @classmethod
    def from_database(cls, delivery_id):
        query_result = jobs.find_one({'delivery.id': delivery_id},
                                     {'id': 1, 'delivery': 1, '_id': 0})
        if query_result:
            from .job import Job
            delivery = cls()
            delivery.set_attributes(query_result['delivery'],
                                    parent=Job.from_database(query_result['id']))
            return delivery
        else:
            raise NonexistentDocumentException(delivery_id)

    # FROM PARENT DOCUMENT

    @classmethod
    def from_parent(cls, parent_job, **kwargs):
        delivery = cls()
        try:
            delivery.set_attributes(parent_job.as_dict['delivery'],
                                    parent=parent_job)
        except KeyError:
            raise NonexistentDocumentException('Delivery for job {}.'.format(parent_job.as_dict['id']))
        return delivery

    # ADJACENT

    @property
    def accept_delivery(self):
        return AcceptDelivery.from_parent(self)

    @accept_delivery.setter
    def accept_delivery(self, value):
        AcceptDelivery.new(value, parent=self)
