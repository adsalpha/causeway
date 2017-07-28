from .encrypted import EncryptedDocument
from exceptions import NonexistentDocumentException
from config.db import jobs


class AcceptDisputeResolution(EncryptedDocument):
    """
    Parent: Dispute
    """

    def set_expected(self):
        super().set_expected()
        self.expected_type = 'accept_dispute_resolution'

    def is_duplicate(self):
        return jobs.count({'id': self.parent.parent.as_dict['id'], 'dispute.accept_resolution': {'$exists': True}}) != 0

    # FROM INCOMING REQUEST

    def save(self):
        jobs.update_one({'dispute.id': self.parent.as_dict['id']},
                        {'$set': {'dispute.accept_resolution': self.as_dict}})

    # FROM DATABASE

    @classmethod
    def from_database(cls, accept_dispute_resolution_id):
        query_result = jobs.find_one({'dispute.accept_resolution.id': accept_dispute_resolution_id},
                                     {'id': 1, 'dispute.accept_resolution': 1, '_id': 0})
        if query_result:
            from .dispute import Dispute
            dispute_resolution = cls()
            dispute_resolution.set_attributes(query_result['dispute']['accept_resolution'],
                                              parent=Dispute.from_database(query_result['dispute']['id']))
            return dispute_resolution
        else:
            raise NonexistentDocumentException(accept_dispute_resolution_id)

    # FROM PARENT DOCUMENT

    @classmethod
    def from_parent(cls, parent_dispute, **kwargs):
        accept_dispute_resolution = cls()
        try:
            accept_dispute_resolution.set_attributes(parent_dispute.as_dict['accept_resolution'],
                                                     parent=parent_dispute)
        except KeyError:
            raise NonexistentDocumentException('Resolution acceptance for dispute {}.'.format(parent_dispute.as_dict['id']))
        return accept_dispute_resolution
