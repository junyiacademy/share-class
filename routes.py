# -*- coding: utf-8 -*-
import sys
import webapp2

import homepage
import login
from course import course

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': '1aqz@SWX3dec$FRV5gtb^HYN7jum*KI<9lo.):P?',
}

reload(sys)
sys.setdefaultencoding('utf-8')
app = webapp2.WSGIApplication([
                              # Admin

                              # Home Page
                              (r'/', course.FindCourse),

                              # Course Page
                              (r'/create-course', course.CreateCourse),
                              (r'/show-course/(\d+)', course.ShowCourse),
                              (r'/find-course', course.FindCourse),
                              (r'/my-course', course.MyCourse),
                              (r'/material-download-update', course.MaterialDownloadUpdate),
                              (r'/course-comment-update', course.CommentUpdate),
                              # Login Page
                              (r'/login-page', login.LoginPage),
                              (r'/logout', login.Logout),
                              (r'/login', login.Login),


                              # Error Pages
                              (r'/*', homepage.NotFoundPage),
                              ], debug=True, config=config)
