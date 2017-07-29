from abc import abstractclassmethod

from .document import Document


class EncryptedDocument(Document):
    """
    Encrypted documents should subclass this.
    """

    def set_expected(self):
        self.expected_structure = [
            'encrypted_contents',
        ]

    def set_attributes(self, payload, **kwargs):
        super().set_attributes(payload, **kwargs)
        self.parent = kwargs.get('parent')

    @abstractclassmethod
    def from_parent(cls, parent, **kwargs):
        """
        Initialize a document using the parent document dictionary.
        Please only use this method for job related documents, from_database() is much less efficient.
        """
        pass

    @property
    def parent(self):
        try:
            return self._parent
        except AttributeError:
            raise NotImplementedError()

    @parent.setter
    def parent(self, value):
        self._parent = value
