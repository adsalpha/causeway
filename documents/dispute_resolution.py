from .encrypted import EncryptedDocument
from exceptions import NonexistentDocumentException
from config.db import jobs


class DisputeResolution(EncryptedDocument):
    """
    Parent: Dispute
    """

    def set_expected(self):
        super().set_expected()
        self.expected_type = 'dispute_resolution'

    def is_duplicate(self):
        return jobs.count({'id': self.parent.parent.as_dict['id'], 'dispute.resolution': {'$exists': True}}) != 0

    # FROM INCOMING REQUEST

    def save(self):
        jobs.update_one({'dispute.id': self.parent.as_dict['id']},
                        {'$set': {'dispute.resolution': self.as_dict}})

    # FROM DATABASE

    @classmethod
    def from_database(cls, dispute_resolution_id):
        query_result = jobs.find_one({'dispute.resolution.id': dispute_resolution_id},
                                     {'id': 1, 'dispute.resolution': 1, '_id': 0})
        if query_result:
            from .dispute import Dispute
            dispute_resolution = cls()
            dispute_resolution.set_attributes(query_result['dispute']['resolution'],
                                              parent=Dispute.from_database(query_result['dispute']['id']))
            return dispute_resolution
        else:
            raise NonexistentDocumentException(dispute_resolution_id)

    # FROM PARENT DOCUMENT

    @classmethod
    def from_parent(cls, parent_dispute, **kwargs):
        dispute_resolution = cls()
        try:
            dispute_resolution.set_attributes(parent_dispute.as_dict['dispute_resolution'],
                                              parent=parent_dispute)
        except KeyError:
            raise NonexistentDocumentException('Resolution for dispute {}.'.format(parent_dispute.as_dict['id']))
        return dispute_resolution
