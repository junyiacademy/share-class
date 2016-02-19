# -*- coding: utf-8 -*-
from handlers import BaseHandler
import logging
from google.appengine.api import users
from user_data.user_models import UserData

from google.appengine.api import memcache
from oauth2client.appengine import AppAssertionCredentials
import httplib2
from apiclient.discovery import build

credentials = AppAssertionCredentials(scope='https://www.googleapis.com/auth/drive')
http = credentials.authorize(httplib2.Http(memcache))
service = build('drive', 'v2', http=http)

GOOGLE_DOC_MIME_TYPE = 'application/vnd.google-apps.document'
DOCX_MIME_TYPE = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'


class NotFoundPage(BaseHandler):
    def get(self):
        self.error(404)


class HomePage(BaseHandler):

    def get(self):

        user = UserData.get_current_user()
        if user:
            self.redirect('/find-resource')

        google_login_url = users.create_login_url('/login')

        data = {
            'google_login_url': google_login_url
        }

        return self.render('home_page.html', data)
