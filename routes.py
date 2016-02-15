# -*- coding: utf-8 -*-
import sys
import webapp2

import homepage
import login
from resource import resource_handler
from subject import subject_handler

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': '1aqz@SWX3dec$FRV5gtb^HYN7jum*KI<9lo.):P?',
}

reload(sys)
sys.setdefaultencoding('utf-8')
app = webapp2.WSGIApplication([
                              # Admin

                              # Home Page
                              (r'/', resource_handler.FindResource),

                              # Course Page
                              (r'/create-course', resource_handler.CreateResource),
                              (r'/show-course/(\d+)', resource_handler.ShowResource),
                              (r'/find-course', resource_handler.FindResource),
                              (r'/my-course', resource_handler.MyResource),
                              (r'/material-download-update', resource_handler.ContentDownloadUpdate),
                              (r'/course-comment-update', resource_handler.CommentUpdate),
                              # Login Page
                              (r'/login-page', login.LoginPage),
                              (r'/logout', login.Logout),
                              (r'/login', login.Login),
                              # admin Page
                              (r'/admin/upload-subject-tree', subject_handler.UploadSubjectTree),
                              (r'/admin/delete-subject-tree/(\d+)', subject_handler.DeleteSubjectTree),


                              # Error Pages
                              (r'/*', homepage.NotFoundPage),
                              ], debug=True, config=config)
