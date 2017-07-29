from app.config.db import jobs
from app.exceptions import NonexistentDocumentException
from .encrypted import EncryptedDocument


class AcceptDelivery(EncryptedDocument):
    """
    Parent: Delivery
    """

    def set_expected(self):
        super().set_expected()
        self.expected_type = 'accept_delivery'

    def is_duplicate(self):
        return jobs.count({'id': self.parent.parent.as_dict['id'], 'delivery.accept_delivery': {'$exists': True}}) != 0

    # FROM INCOMING REQUEST

    def save(self):
        jobs.update_one({'delivery.id': self.parent.as_dict['id']},
                        {'$set': {'delivery.accept_delivery': self.as_dict}})

    # FROM DATABASE

    @classmethod
    def from_database(cls, accept_delivery_id):
        query_result = jobs.find_one({'delivery.accept_delivery.id': accept_delivery_id},
                                     {'id': 1, 'delivery.accept_delivery': 1, '_id': 0})
        if query_result:
            from .delivery import Delivery
            accept_delivery = cls()
            accept_delivery.set_attributes(query_result['delivery']['accept_delivery'],
                                           parent=Delivery.from_database(query_result['delivery']['id']))
            return accept_delivery
        else:
            raise NonexistentDocumentException(accept_delivery_id)

    # FROM PARENT DOCUMENT

    @classmethod
    def from_parent(cls, parent_delivery, **kwargs):
        accept_delivery = cls()
        try:
            accept_delivery.set_attributes(parent_delivery.as_dict['accept_delivery'],
                                           parent=parent_delivery)
        except KeyError:
            raise NonexistentDocumentException('Acceptance for delivery {}.'.format(parent_delivery.as_dict['id']))
        return accept_delivery
