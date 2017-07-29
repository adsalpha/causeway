from app.config.db import jobs
from app.exceptions import NonexistentDocumentException
from .accept_dispute_resolution import AcceptDisputeResolution
from .dispute_resolution import DisputeResolution
from .encrypted import EncryptedDocument


class Dispute(EncryptedDocument):
    """
    Parent: Job
    Children: DisputeResolution, AcceptDisputeResolution
    """

    def set_expected(self):
        super().set_expected()
        self.expected_type = 'dispute'

    def is_duplicate(self):
        return jobs.count({'id': self.parent.as_dict['id'], 'dispute': {'$exists': True}}) != 0

    # FROM INCOMING REQUEST

    def save(self):
        jobs.update_one({'id': self.parent.as_dict['id']},
                        {'$set': {'dispute': self.as_dict}})

    # FROM DATABASE

    @classmethod
    def from_database(cls, dispute_id):
        query_result = jobs.find_one({'dispute.id': dispute_id},
                                     {'id': 1, 'dispute': 1, '_id': 0})
        if query_result:
            from .job import Job
            dispute = cls()
            dispute.set_attributes(query_result['dispute'],
                                   parent=Job.from_database(query_result['id']))
            return dispute
        else:
            raise NonexistentDocumentException(dispute_id)

    # FROM PARENT DOCUMENT

    @classmethod
    def from_parent(cls, parent_job, **kwargs):
        dispute = cls()
        try:
            dispute.set_attributes(parent_job.as_dict['dispute'],
                                   parent=parent_job)
        except KeyError:
            raise NonexistentDocumentException('Dispute for job {}.'.format(parent_job.as_dict['id']))
        return dispute

    # ADJACENT

    @property
    def resolution(self):
        return DisputeResolution.from_parent(self)

    @resolution.setter
    def resolution(self, value):
        DisputeResolution.new(value, parent=self)

    @property
    def accept_resolution(self):
        return AcceptDisputeResolution.from_parent(self)

    @accept_resolution.setter
    def accept_resolution(self, value):
        AcceptDisputeResolution.new(value, parent=self)
