import os
import flask
import logging

from wetool import net

import manager
import views

ROUTE = os.path.dirname(os.path.abspath(__file__))

LOG = logging.getLogger(__name__)


class HttpServer:
    RULES = []

    def __init__(self, name, host=None, port=80, template_folder=None,
                 static_folder=None):
        self.host = host or net.get_internal_ip()
        self.port = port
        self.template_folder = template_folder
        self.static_folder = static_folder
        self.app = flask.Flask(name,
                               template_folder=self.template_folder,
                               static_folder=self.static_folder)
        self.app.secret_key = "app secret"
        self._register_rules()

    def _register_rules(self):
        for url, view_func in self.RULES:
            self.app.add_url_rule(url, view_func=view_func)

    def pre_start(self):
        # NOTE(zbw) avoid conflict with vue
        self.app.jinja_env.variable_start_string = '[['
        self.app.jinja_env.variable_end_string = ']]'
        self.app.config['SERVER_NAME'] = '{}:{}'.format(self.host, self.port)

    def start(self, debug=False):
        self.pre_start()
        LOG.info('strarting server')
        self.app.run(host=self.host, port=self.port, debug=debug)


class HorizonHttpServer(HttpServer):

    RULES = [
        (r'/favicon.ico', views.FaviconView.as_view('favicon')),
        (r'/', views.HomeView.as_view('home')),
        (r'/index', views.IndexView.as_view('index')),
        (r'/actions', views.ActionView.as_view('action')),
        (r'/server', views.ServerView.as_view('server')),
        (r'/login', views.LoginView.as_view('login')),
    ]

    def __init__(self, host=None, port=80):
        super().__init__('FluentFS', host=host, port=port,
                         template_folder=os.path.join(ROUTE, 'templates'),
                         static_folder=os.path.join(ROUTE, 'static'))

    def pre_start(self):
        super().pre_start()
  