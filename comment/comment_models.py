# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from user_data.user_models import UserData


class Comment(ndb.Model):

    comment_user = ndb.KeyProperty(required=True, kind=UserData)
    created_time = ndb.DateTimeProperty(auto_now_add=True)
    comment_content = ndb.TextProperty()
    # type = ndb.StringPRoperty(choices=[u'心情', u'討論'])
    comment_parent = ndb.KeyProperty()

    @classmethod
    def get_by_course(cls, course):
        comments = cls.query(ancestor=course.key).fetch()
        return comments
