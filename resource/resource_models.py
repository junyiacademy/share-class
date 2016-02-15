# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from user_data.user_models import UserData


class Content(ndb.Model):

    content_name = ndb.StringProperty()
    related_file_id = ndb.StringProperty()
    related_file_type = ndb.StringProperty(choices=['GOOGLE_DOC'], default='GOOGLE_DOC')
    download_count = ndb.IntegerProperty(default=0)


class Resource(ndb.Model):

    resource_name = ndb.StringProperty(required=True)
    grade_chunk = ndb.StringProperty(choices=[u'國小', u'國中', u'高中'])
    difficulty = ndb.StringProperty(choices=[u'易', u'中', u'難'])
    subject = ndb.StringProperty()
    keywords = ndb.StringProperty(repeated=True)
    contents = ndb.KeyProperty(repeated=True, kind=Content)
    # course_instruction = ndb.TextProperty(default="")
    creator = ndb.KeyProperty(required=True, kind=UserData)
    admins = ndb.KeyProperty(repeated=True, kind=UserData)
    is_public = ndb.BooleanProperty(default=False)
    created_time = ndb.DateTimeProperty(auto_now_add=True)

    def is_visible_to_user(self, user=None):
        if self.is_public:
            return True
        elif user and user.key in self.admins:
            return True
        return False

    @classmethod
    def filter_by_keywords(cls, query, keywords):

        for keyword in keywords:
            query = query.filter(cls.keywords == keyword)
        return query

    @classmethod
    def filter_by_user_visibility(cls, query, user):
        if user is None:
            query = query.filter(cls.is_public == True)

        elif not user.is_server_admin():  # server admin can see anything
            query = query.filter(ndb.OR(cls.is_public == True,
                                        cls.admins == user.key
                                        ))
        return query

    @classmethod
    def list_courses_for_user(cls, user=None, keywords=None, number=20):
        query = cls.query()
        if keywords:
            query = cls.filter_by_keywords(query, keywords)

        query = cls.filter_by_user_visibility(query, user)

        return query.fetch(number)

    def get_avg_download_count(self):
        download_count_list = [key.get().download_count for key in self.contents]
        return sum(download_count_list) / len(download_count_list)

    def is_public_chinese(self):
        if self.is_public:
            return "是"
        else:
            return "否"


class KeyWordIndex(ndb.Model):
    key_word = ndb.StringProperty()
    related_subject = ndb.StringProperty()
    resource_count = ndb.IntegerProperty(default=1)

    @classmethod
    def get_by_keyword_and_subject(cls, keyword, subject):
        return cls.query(cls.key_word == keyword, cls.related_subject==subject).get()
