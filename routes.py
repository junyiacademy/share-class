# -*- coding: utf-8 -*-
import sys
import webapp2

import homepage
import login
from course import course_handler
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
                              (r'/', course_handler.FindCourse),

                              # Course Page
                              (r'/create-course', course_handler.CreateCourse),
                              (r'/show-course/(\d+)', course_handler.ShowCourse),
                              (r'/find-course', course_handler.FindCourse),
                              (r'/my-course', course_handler.MyCourse),
                              (r'/material-download-update', course_handler.MaterialDownloadUpdate),
                              (r'/course-comment-update', course_handler.CommentUpdate),
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
