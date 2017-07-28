from collections import OrderedDict
from abc import ABC, abstractmethod, abstractclassmethod
import json


class Document(ABC):
    """
    Documents are the main Rein abstraction.
    This class is only intended for subclassing.
    """

    # FROM INCOMING REQUEST

    @classmethod
    def new(cls, payload, **kwargs):
        document = cls()
        document.set_expected()
        document.set_attributes(payload, **kwargs)
        document.validate()
        document.save()
        return document

    @abstractmethod
    def set_expected(self):
        pass

    def set_attributes(self, payload, **kwargs):
        if type(payload) is str:
            self.as_dict = json.loads(payload, object_pairs_hook=OrderedDict)
        else:
            self.as_dict = payload

    @property
    def as_dict(self):
        try:
            return self._as_dict
        except AttributeError:
            raise NotImplementedError('Use the `new` or the `from_database` methods to create a '
                                      'document with as_dict set correctly.')

    @as_dict.setter
    def as_dict(self, value: OrderedDict):
        self._as_dict = value

    def serialize(self):
        return json.dumps(self.as_dict)

    def validate(self):
        if not self.expected_structure_ok():
            raise ValueError('Bad expected structure, please check the Rein Document Specification v3.')
        if not self.incoming_structure_ok():
            raise ValueError('Bad incoming document structure, expected {}.'
                             .format(self.expected_structure))
        if not self.type_ok():
            raise ValueError('Bad incoming document type, expected {}.'
                             .format(self.expected_type))
        if self.is_duplicate():
            raise ValueError('The server already has a document with ID {}'
                             .format(self.as_dict['id']))

    @abstractmethod
    def save(self):
        pass

    # Expected

    _base_expected_structure = ['type', 'id', {'validity': ['signature', 'signature_address']}]

    @property
    def expected_structure(self):
        """
        An array that contains the keys an uploaded document should include.
        See _base_expected_structure above for an example.
        Must be set by subclasses.
        """
        try:
            return self._expected_structure
        except AttributeError:
            raise NotImplementedError("Subclasses of Document must set the _expected_structure attribute.")

    @expected_structure.setter
    def expected_structure(self, value: list):
        self._expected_structure = self._base_expected_structure + value

    @property
    def expected_type(self):
        try:
            return self._expected_type
        except AttributeError:
            raise NotImplementedError("Subclasses of Document must set the _expected_type attribute.")

    @expected_type.setter
    def expected_type(self, value: str):
        self._expected_type = value

    # Validators

    def expected_structure_ok(self):
        if type(self.expected_structure) is list:
            for field in self.expected_structure:
                if type(field) is dict:
                    keys = list(field.keys())
                    if len(keys) == 1:
                        key = keys[0]
                        if type(field[key]) is list:
                            for child_field in field[key]:
                                if type(child_field) is not str:
                                    return False
                        else:
                            return False
                    else:
                        return False
                elif type(field) is not str:
                    return False
        else:
            return False
        return True

    def incoming_structure_ok(self):
        for field in self.expected_structure:
            if type(field) is dict:
                # A dict field looks like {'key': ['nested_key', 'another_nested_key']}
                # The dict only has one key because a JSON field can only be defined by a single key.
                keys = list(field.keys())
                if len(keys) == 1:
                    key = keys[0]
                    for child_field in field[key]:
                        if child_field not in self.as_dict[key]:
                            return False
                else:
                    return False
            elif field not in self.as_dict:
                return False
        return True

    def type_ok(self):
        return self.expected_type == self.as_dict['type']

    @abstractmethod
    def is_duplicate(self):
        pass

    # FROM DATABASE

    @abstractclassmethod
    def from_database(cls, document_id):
        """
        Initializes a document using the database.
        """
        pass
