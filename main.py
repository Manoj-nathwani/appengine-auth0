import os, logging, json
from functools import wraps

import webapp2
from webapp2_extras import jinja2, sessions, sessions_memcache

import requests
import requests_toolbelt.adapters.appengine
requests_toolbelt.adapters.appengine.monkeypatch()


class BaseHandler(webapp2.RequestHandler):
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
        return self.session_store.get_session(
            factory=sessions_memcache.MemcacheSessionFactory
        )

    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, _template, **context):
        # Renders a template and writes the result to the response.
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)


def requires_auth(f):
    def _requires_auth(self, *args, **kwargs):
        if 'user' not in self.session:
            self.redirect('/login')
            return        
        return f(self, *args, **kwargs)
    return _requires_auth


class LoginHandler(BaseHandler):
    def get(self):
        self.render_response('login.html', **os.environ)


class CallbackHandler(BaseHandler):
    def get(self):
        code = self.request.GET['code']

        # get token
        token_url = 'https://{}/oauth/token'.format(
            os.environ['AUTH0_DOMAIN']
        )
        token_payload = {
            'client_id': os.environ['AUTH0_CLIENT_ID'],
            'client_secret': os.environ['AUTH0_CLIENT_SECRET'],
            'redirect_uri': os.environ['DOMAIN'] + '/callback',
            'code': code,
            'grant_type': 'authorization_code'
        }
        token_info = requests.post(
            url=token_url,
            json=token_payload,
        ).json()

        # get user
        user_url = 'https://{}/userinfo?access_token={}'.format(
            os.environ['AUTH0_DOMAIN'],
            token_info['access_token']
        )
        user_info = requests.get(user_url).json()

        self.session['user'] = user_info
        print('auth0 user_id {} logged in with memcache key {}'.format(
            user_info['user_id'],
            self.session.container.sid
        ))
        self.redirect('/')  


class DashboardHandler(BaseHandler):
    @requires_auth
    def get(self):
        context = {'user': self.session.get('user')}
        self.render_response('dashboard.html', **context)

app = webapp2.WSGIApplication(
    [
        ('/login', LoginHandler),        
        ('/callback', CallbackHandler),
        ('/', DashboardHandler),
    ],
    debug=os.environ['DEBUG'],
    config={
        'webapp2_extras.sessions':{
            'secret_key': os.environ['SECRET_KEY']
        }
    }
)
