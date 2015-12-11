# -*- coding: utf-8 -*-
import os

import jinja2
import webapp2
from webapp2_extras import sessions


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'),
    extensions=['jinja2.ext.autoescape'])


class BaseHandler(webapp2.RequestHandler):

    def __init__(self, request, response):
        self.initialize(request, response)

    def get(self, *args, **atts):
        pass

    def post(self, *args, **atts):
        pass

    def error(self, code):
        super(BaseHandler, self).error(code)
        if code == 404:
            self.render('404.html')

    def render(self, template_name, data={}):
        template = JINJA_ENVIRONMENT.get_template(template_name)
        self.response.write(template.render(data))

    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()
