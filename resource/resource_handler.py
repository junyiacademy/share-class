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
        if not user:  # make sure user has an account to create resource
            self.render('resource/create-resource-no-auth.html')
        else:
            return self.render('resource/create-resource.html')

    def post(self):

        # upload new content on google drive
        user = UserData.get_current_user()
        if not user:  # make sure user has an account to create resource
            self.redirect('find-resource')

        content_index_list = self.request.get('content-index-list').split(',')
        logging.info("content_index_list: %s" % content_index_list)

        content_list = []
        for i in content_index_list:
            content_name = self.request.get('content-name-%s' % i)
            content_content = io.BytesIO(self.request.get('content-%s' % i))
            content_file = google_drive_api.insert_file(service, content_name, content_content, google_drive_api.DOCX_MIME_TYPE)
            new_content = Content(content_name=content_name,
                                    related_file_id=content_file['id']
                                    )
            new_content.put()
            content_list.append(new_content.key)
        # 我們不在這個時候寄邀請信給使用者，請他同意獲得講義的writer權限
        # 因為我認為使用者很可能不會去收信，我們在使用者第一次真的要使用線上編輯功能的時候
        # 再告知他們我們會寄信邀請他們，請他們去收信  -- By EN

        resource_name = self.request.get('resource-name')
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
        new_resource = Resource(resource_name=resource_name,
                            grade_chunk=grade_chunk,
                            difficulty=difficulty,
                            subject=subject,
                            keywords=keyword_list,
                            contents=content_list,
                            creator=user.key,
                            admins=[user.key],
                            is_public=is_public
                            )
        new_resource.put()

        for keyword in keyword_list:
            keywordindex = KeyWordIndex.get_by_keyword_and_subject(keyword, subject)
            if keywordindex:
                keywordindex.resource_count = keywordindex.resource_count + 1
            else:
                keywordindex = KeyWordIndex(key_word=keyword, related_subject=subject)
            keywordindex.put()

        self.redirect('/show-resource/%s' % new_resource.key.id())


class ShowResource(BaseHandler):

    def get(self, resource_id):

        user = UserData.get_current_user()
        resource = Resource.get_by_id(int(resource_id))
        if not resource.is_visible_to_user(user):
            return self.render('resource/show-resource-no-auth.html')

        else:
            contents = [key.get() for key in resource.contents]
            admins = [key.get().user_nickname for key in resource.admins]
            is_admin = user and user.key in resource.admins

            comments = Comment.get_by_resource(resource)
            comments.sort(key=lambda x: x.created_time, reverse=False)
            for comment in comments:
                comment.created_time = comment.created_time + timedelta(hours=8)
                comment.user_nickname = comment.comment_user.get().user_nickname

            data = {
                'resource': resource,
                'keywords': ', '.join(resource.keywords),
                'admins': ', '.join(admins),
                'contents': contents,
                'is_admin': is_admin,
                'comments': comments
            }

            return self.render('resource/show-resource.html', data)

    def post(self, resource_id):

        # add new admins...
        user = UserData.get_current_user()
        resource = Resource.get_by_id(int(resource_id))
        if not (user.key in resource.admins):  # only admin can edit the resource
            self.redirect('resource/show-resource/%s' % resource_id)

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

        content_uploaded = self.request.get('content_uploaded')
        if content_uploaded:
            new_content_content = io.BytesIO(content_uploaded)
            content_file_id = self.request.get('content-related-file-id')
            google_drive_api.update_file(service, content_file_id, new_content_content, google_drive_api.DOCX_MIME_TYPE)
            logging.info("%s is uploaded" % content_file_id)

        self.redirect('/show-resource/%s' % resource_id)


class FindResource(BaseHandler):

    def get(self):

        user = UserData.get_current_user()
        keywords = self.request.get('keywords')

        if keywords:
            keywords = keywords.split(',')
            resources = Resource.list_resources_for_user(user, keywords, number=20)
        else:
            resources = Resource.list_resources_for_user(user, number=20)
        resources.sort(key=lambda x: x.get_avg_download_count(), reverse=True)

        keyword_str_list = []
        avg_download_count_list = []
        for resource in resources:
            keyword_str_list.append(', '.join(resource.keywords))
            avg_download_count_list.append(resource.get_avg_download_count())

        keyword_index_list = [i.key_word for i in KeyWordIndex.query().fetch()]
        data = {
            'resources': resources,
            'keyword_str_list': keyword_str_list,
            'keyword_index_list': keyword_index_list,
            'avg_download_count_list': avg_download_count_list
        }

        return self.render('resource/find-resource.html', data)


class MyResource(BaseHandler):

    def get(self):
        user = UserData.get_current_user()
        if user is None:
            self.redirect('resource/find-resource')
        resources = Resource.query(Resource.admins == user.key).fetch()
        resources.sort(key=lambda x: x.get_avg_download_count(), reverse=True)
        keyword_str_list = []
        avg_download_count_list = []
        for resource in resources:
            keyword_str_list.append(', '.join(resource.keywords))
            avg_download_count_list.append(resource.get_avg_download_count())

        data = {
            'resources': resources,
            'keyword_str_list': keyword_str_list,
            'avg_download_count_list': avg_download_count_list
        }

        return self.render('resource/my-resource.html', data)


class CommentUpdate(BaseHandler):

    def post(self):

        user_id = int(self.request.get('user_id'))
        user = UserData.get_by_id(user_id)
        user = user or UserData.get_current_user()
        if user is None:
            return

        resource_id = self.request.get('resource_id')
        resource = Resource.get_by_id(int(resource_id))
        content = self.request.get('content')

        new_comment = Comment(parent=resource.key,
                              comment_user=user.key,
                              comment_content=content
                             )
        new_comment.put()
        return


class ContentDownloadUpdate(BaseHandler):

    def post(self):

        content_id = self.request.get('content-id')
        content = Content.get_by_id(int(content_id))
        if content:
            content.download_count = content.download_count + 1
        content.put()

        return
