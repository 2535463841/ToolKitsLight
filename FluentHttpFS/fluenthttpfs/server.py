import os
import flask
import logging
import argparse

from fluentcore import net
from fluentcore.common import log

from fluenthttpfs import manager
from fluenthttpfs import views

LOG = log.getLogger(__name__)
ROUTE = os.path.dirname(os.path.abspath(__file__))


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
        LOG.info('strarting server, debug=%s', debug)
        self.app.run(host=self.host, port=self.port, debug=debug)


class HttpFsServer(HttpServer):

    RULES = [
        (r'/favicon.ico', views.FaviconView.as_view('favicon')),
        (r'/', views.HomeView.as_view('home')),
        (r'/index.html', views.IndexView.as_view('index')),
        (r'/action', views.ActionView.as_view('action')),
        (r'/download/<file_name>', views.DownloadView.as_view('download')),
        (r'/qrcode', views.QrcodeView.as_view('qrcode')),
        (r'/server', views.ServerView.as_view('server')),
    ]

    def __init__(self, host=None, port=80, fs_root=None):
        super().__init__('FluentFS', host=host, port=port,
                         template_folder=os.path.join(ROUTE, 'templates'),
                         static_folder=os.path.join(ROUTE, 'static'))
        self.fs_root = fs_root or './'
        self.driver = manager.FSManager(self.fs_root)

    def pre_start(self):
        super().pre_start()
        views.FS_CONTROLLER = manager.FSManager(self.fs_root)


def main():
    parser = argparse.ArgumentParser('Fluent HTTP FS Command')
    parser.add_argument('-d', '--debug', action='store_true',
                        help="show debug message")
    parser.add_argument('-P', '--path', help="the path of backend")
    parser.add_argument('-p', '--port', type=int, default=80,
                        help="the port of server, default 80")
    parser.add_argument('--development', action='store_true',
                        help="run server as development mode")
    args = parser.parse_args()
    if args.debug:
        log.set_default(level=logging.DEBUG)
    server = HttpFsServer(fs_root=args.path, port=args.port)

    server.start(debug=args.development)


if __name__ == '__main__':
    main()
