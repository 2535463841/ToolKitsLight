from gevent import pywsgi
import os

import flask

from icoding import net
from icoding.common import log
from icoding.server import views


LOG = log.getLogger(__name__)
ROUTE = os.path.dirname(os.path.abspath(__file__))


class WsgiServer:
    RULES = [(r'/', views.IndexView.as_view('index')), ]

    def __init__(self, name, host=None, port=80, template_folder=None,
                 static_folder=None):
        self.host = host or net.get_internal_ip()
        self.port = port
        self.template_folder = template_folder
        self.static_folder = static_folder
        self.app = flask.Flask(name,
                               template_folder=self.template_folder,
                               static_folder=self.static_folder)
        self._register_rules()

        self.app.jinja_env.variable_start_string = '[['
        self.app.jinja_env.variable_end_string = ']]'
        self.app.config['SERVER_NAME'] = '{}:{}'.format(self.host, self.port)

        @self.app.before_request
        def register_before_request():
            self.before_request()

    def before_request(self):
        """Do someting here before reqeust"""
        pass

    def _register_rules(self):
        LOG.debug('register rules')
        for url, view_func in self.RULES:
            self.app.add_url_rule(url, view_func=view_func)

    def start(self, develoment=False, debug=False):
        LOG.info('strarting server: http://%s:%s', self.host, self.port)
        if develoment:
            self.app.run(host=self.host, port=self.port, debug=debug)
        else:
            server = pywsgi.WSGIServer((self.host, self.port), self.app)
            server.serve_forever()
