# -*- coding: utf-8 -*-

from handlers import BaseHandler
from resource_models import Resource, Content, KeyWordIndex
from datetime import timedelta
from user_data.user_models import UserData
from comment.comment_models import Comment
from google.appengine.api import memcache
from oauth2client.appengine import AppAssertionCredentials
import httplib2
from apiclient.discovery import build
import google_drive_api
import logging
import json
import io

credentials = AppAssertionCredentials(scope='https://www.googleapis.com/auth/drive')
http = credentials.authorize(httplib2.Http(memcache))
service = build('drive', 'v2', http=http)


class CreateResource(BaseHandler):

    def get(self):
        user = UserData.get_current_user()
        if not user:  # make sure user has an account to create course
            self.render('course/create-course-no-auth.html')
        else:
            return self.render('course/create-course.html')

    def post(self):

        # upload new material on google drive
        user = UserData.get_current_user()
        if not user:  # make sure user has an account to create course
            self.redirect('find-course')

        material_index_list = self.request.get('material-index-list').split(',')
        logging.info("material_index_list: %s" % material_index_list)

        material_list = []
        for i in material_index_list:
            material_name = self.request.get('material-name-%s' % i)
            material_content = io.BytesIO(self.request.get('material-content-%s' % i))
            material_file = google_drive_api.insert_file(service, material_name, material_content, google_drive_api.DOCX_MIME_TYPE)
            new_content = Content(material_name=material_name,
                                    related_file_id=material_file['id']
                                    )
            new_content.put()
            material_list.append(new_content.key)
        # 我們不在這個時候寄邀請信給使用者，請他同意獲得講義的writer權限
        # 因為我認為使用者很可能不會去收信，我們在使用者第一次真的要使用線上編輯功能的時候
        # 再告知他們我們會寄信邀請他們，請他們去收信  -- By EN

        course_name = self.request.get('resource-name')
        grade_chunk = self.request.get('grade-chunk')
        difficulty = self.request.get('difficulty')
        subject = self.request.get('subject')
        is_public = bool(int(self.request.get('is_public')))
        keywords = self.request.get('keywords')
        keyword_list = []
        if keywords:
            keyword_list = keywords.strip().split(',')
        keyword_list.append(subject)
        keyword_list.append(grade_chunk)
        keyword_list = set(keyword_list)
        new_course = Resource(course_name=course_name,
                            grade_chunk=grade_chunk,
                            difficulty=difficulty,
                            subject=subject,
                            keywords=keyword_list,
                            materials=material_list,
                            creator=user.key,
                            admins=[user.key],
                            is_public=is_public
                            )
        new_course.put()

        for keyword in keyword_list:
            keywordindex = KeyWordIndex.get_by_keyword_and_subject(keyword, subject)
            if keywordindex:
                keywordindex.course_count = keywordindex.course_count + 1
            else:
                keywordindex = KeyWordIndex(key_word=keyword, related_subject=subject)
            keywordindex.put()

        self.redirect('/show-course/%s' % new_course.key.id())


class ShowResource(BaseHandler):

    def get(self, course_id):

        user = UserData.get_current_user()
        course = Resource.get_by_id(int(course_id))
        if not course.is_visible_to_user(user):
            return self.render('course/show-course-no-auth.html')

        else:
            materials = [key.get() for key in course.materials]
            admins = [key.get().user_nickname for key in course.admins]
            is_admin = user and user.key in course.admins

            comments = Comment.get_by_course(course)
            comments.sort(key=lambda x: x.created_time, reverse=False)
            for comment in comments:
                comment.created_time = comment.created_time + timedelta(hours=8)
                comment.user_nickname = comment.comment_user.get().user_nickname

            data = {
                'course': course,
                'keywords': ', '.join(course.keywords),
                'admins': ', '.join(admins),
                'materials': materials,
                'is_admin': is_admin,
                'comments': comments
            }

            return self.render('course/show-course.html', data)

    def post(self, course_id):

        # add new admins...
        user = UserData.get_current_user()
        resource = Resource.get_by_id(int(course_id))
        if not (user.key in resource.admins):  # only admin can edit the course
            self.redirect('course/show-course/%s' % course_id)

        admins_email = self.request.get('admins-email')
        if admins_email:  # we will need to update the admin list
            admin_key_list = resource.admins
            email_list = admins_email.strip().split(',')

            for email in email_list:
                user = UserData.get_by_user_email(email)
                if user and not (user.key in admin_key_list):
                    admin_key_list.append(user.key)

            # 我們不在這個時候寄邀請信給使用者，請他同意獲得講義的writer權限
            # 因為我認為使用者很可能不會去收信，我們在使用者第一次真的要使用線上編輯功能的時候
            # 再告知他們我們會寄信邀請他們，請他們去收信  -- By EN

            admin_key_list = set(admin_key_list)
            resource.admins = admin_key_list

        change_public_state = self.request.get('change_public_state')
        if change_public_state:
            resource.is_public = not resource.is_public

        resource.put()

        material_uploaded = self.request.get('material_uploaded')
        if material_uploaded:
            new_material_content = io.BytesIO(material_uploaded)
            material_file_id = self.request.get('material-related-file-id')
            google_drive_api.update_file(service, material_file_id, new_material_content, google_drive_api.DOCX_MIME_TYPE)
            logging.info("%s is uploaded" % material_file_id)

        self.redirect('/show-course/%s' % course_id)


class FindResource(BaseHandler):

    def get(self):

        user = UserData.get_current_user()
        keywords = self.request.get('keywords')

        if keywords:
            keywords = keywords.split(',')
            courses = Resource.list_courses_for_user(user, keywords, number=20)
        else:
            courses = Resource.list_courses_for_user(user, number=20)
        courses.sort(key=lambda x: x.get_avg_download_count(), reverse=True)

        keyword_str_list = []
        avg_download_count_list = []
        for course in courses:
            keyword_str_list.append(', '.join(course.keywords))
            avg_download_count_list.append(course.get_avg_download_count())

        keyword_index_list = [i.key_word for i in KeyWordIndex.query().fetch()]
        data = {
            'courses': courses,
            'keyword_str_list': keyword_str_list,
            'keyword_index_list': keyword_index_list,
            'avg_download_count_list': avg_download_count_list
        }

        return self.render('course/find-course.html', data)


class MyResource(BaseHandler):

    def get(self):
        user = UserData.get_current_user()
        if user is None:
            self.redirect('course/find-course')
        courses = Resource.query(Resource.admins == user.key).fetch()
        courses.sort(key=lambda x: x.get_avg_download_count(), reverse=True)
        keyword_str_list = []
        avg_download_count_list = []
        for course in courses:
            keyword_str_list.append(', '.join(course.keywords))
            avg_download_count_list.append(course.get_avg_download_count())

        data = {
            'courses': courses,
            'keyword_str_list': keyword_str_list,
            'avg_download_count_list': avg_download_count_list
        }

        return self.render('course/my-course.html', data)


class CommentUpdate(BaseHandler):

    def post(self):

        user_id = int(self.request.get('user_id'))
        user = UserData.get_by_id(user_id)
        user = user or UserData.get_current_user()
        if user is None:
            return

        course_id = self.request.get('course_id')
        course = Resource.get_by_id(int(course_id))
        content = self.request.get('content')

        new_comment = Comment(parent=course.key,
                              comment_user=user.key,
                              comment_content=content
                             )
        new_comment.put()
        return


class ContentDownloadUpdate(BaseHandler):

    def post(self):

        material_id = self.request.get('material-id')
        material = Content.get_by_id(int(material_id))
        if material:
            material.download_count = material.download_count + 1
        material.put()

        return
