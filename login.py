# -*- coding: utf-8 -*-
from handlers import BaseHandler
from user_data.user_models import UserData
from google.appengine.api import users
import logging


class LoginPage(BaseHandler):

    def get(self):

        user = UserData.get_current_user()
        if user:
            self.redirect('/find-course')

        google_login_url = users.create_login_url('/login')

        data = {
            'google_login_url': google_login_url
        }

        return self.render('home_page.html', data)


class Login(BaseHandler):

    def get(self):

        user = UserData.get_current_user()
        if user:
            # we already have this user in datastore, do nothing at this time
            pass
        else:
            logging.info('into Login handler')
            google_user_property = users.get_current_user()
            user = UserData.get_by_user_email(google_user_property.email())
            if user:
                # 內部已經有一個帳號有此email，目前沒有預備要處理這種問題
                logging.error('Email %s already used by one of our user' % user.user_email)
                raise Exception('Email %s already used by one of our user' % user.user_email)
            else:  # email 也沒有重複，可以新增一個使用者
                new_user = UserData(google_user_id=google_user_property.user_id(),
                                user_email=google_user_property.email(),
                                user_nickname=google_user_property.nickname()
                                )
            new_user.put()
        self.redirect('/find-course')


class Logout(BaseHandler):

    def get(self):

        user_property = users.get_current_user()

        if user_property:
            google_logout_url = users.create_logout_url('/')
            self.redirect(google_logout_url)

        else:
            self.redirect('/')
