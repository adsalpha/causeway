from app.config.db import users
from app.exceptions import NonexistentDocumentException
from .unencrypted import UnencryptedDocument


class User(UnencryptedDocument):

    class BulkQuery:

        def __init__(self):
            db_users = users.find({}, {'_id': 0})
            self.array = []
            for db_user in db_users:
                user = User()
                db_user.set_attributes(db_user)
                self.array.append(user)

        def serialize(self):
            return [user.serialize() for user in self.array]

    def set_expected(self):
        self.expected_structure = [
            'created_at',
            'login',
            'email',
            {'addresses': ['master', 'delegate']}
        ]
        self.expected_type = 'user'

    def is_duplicate(self):
        return users.count({'login': self.as_dict['login']}) != 0

    # FROM INCOMING REQUEST

    def save(self):
        users.insert(self.as_dict)

    # FROM DATABASE

    @classmethod
    def from_database(cls, user_id):
        db_user = users.find_one({'$or': [
            {'id': user_id},
            {'login': user_id},
            {'email': user_id}
        ]}, {'_id': 0})
        if db_user:
            user = User()
            user.as_dict = db_user
            user.as_dict['rating'] = user.compute_rating()
            return user
        else:
            raise NonexistentDocumentException(user_id)

    @staticmethod
    def exists(user_id: str):
        return bool(users.count({'$or': [
            {'id': user_id},
            {'login': user_id},
            {'email': user_id}
        ]}))

    # TODO
    def compute_rating(self):
        return 0
