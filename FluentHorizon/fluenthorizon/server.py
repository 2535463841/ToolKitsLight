import os
import flask

from flask import session

from fluentcore.common import log
from fluentcore.server import httpserver

import views


ROUTE = os.path.dirname(os.path.abspath(__file__))

LOG = log.getLogger(__name__)


class HorizonHttpServer(httpserver.WsgiServer):

    RULES = [
        (r'/favicon.ico', views.FaviconView.as_view('favicon')),
        (r'/', views.HomeView.as_view('home')),
        (r'/index', views.IndexView.as_view('index')),
        (r'/<name>.html', views.HtmlView.as_view('html')),
        (r'/actions', views.ActionView.as_view('action')),
        (r'/server', views.ServerView.as_view('server')),
        (r'/login', views.LoginView.as_view('login')),
    ]

    def __init__(self, host=None, port=80):
        super().__init__('HorizonHttpServer', host=host, port=port,
                         template_folder=os.path.join(ROUTE, 'templates'),
                         static_folder=os.path.join(ROUTE, 'static'))
        self.app.config['SECRET_KEY'] = 'HorizonHttpServer'

    def before_request(self):
        if not session.get('auth'):
            return flask.redirect('/login')
