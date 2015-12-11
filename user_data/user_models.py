from google.appengine.ext import ndb
from google.appengine.api import users
import logging


class UserData(ndb.Model):

    google_user_id = ndb.StringProperty()
    user_email = ndb.StringProperty()
    user_nickname = ndb.StringProperty()
    user_account_type = ndb.StringProperty(default="google_account")
    # attr of UserProperty: id, email, nickname
    created_time = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def get_current_user(cls):
        logging.info('into Function UserData.get_current_user()')
        user_property = users.get_current_user()
        if user_property:
            return cls.query(cls.google_user_id == user_property.user_id()).get()
        else:
            return None

    def is_server_admin(self):
        return users.is_current_user_admin()

    @classmethod
    def get_by_user_email(cls, email):
        user = cls.query(cls.user_email == email).fetch(10)
        if len(user) > 1:
            logging.error('Email %s used by multiple users in our db' % user.user_email)
            raise Exception('Email %s used by multiple users in our db' % user.user_email)
        elif user:
            return user[0]
        else:
            return None
