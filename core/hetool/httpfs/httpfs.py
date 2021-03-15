import os
import stat
import json
import flask

from flask import views
from flask import Flask

from hetool import date
from hetool import code
from hetool import net

HOST = None
PORT = 8000

ROUTE = os.path.dirname(os.path.abspath(__file__))


class FSController:

    def __init__(self, home) -> None:
        self.home = home

    def get_abs_path(self, path):
        if isinstance(path, str):
            return os.path.join(self.home, *path.split('/'))
        else:
            return os.path.join(self.home, *path)

    def path_exists(self, path):
        return os.path.exists(self.get_abs_path(path))

    def _get_qrcode_lines(self, path, child):
        qr = code.QRCodeExtend()
        if path == '/':
            qr.add_data(
                'http://{0}:{1}/download/{2}?path=/{2}'.format(
                    HOST, PORT, child))
        else:
            qr.add_data(
                'http://{0}:{1}/download/{3}?path={2}/{3}'.format(
                    HOST, PORT, path, child))
        return qr.parse_string_lines()

    def get_dirs(self, path):
        children = []
        if not path:
            return children
        find_path = self.get_abs_path(path)
        for child in os.listdir(find_path):
            pathstat = os.stat(os.path.join(find_path, child))
            if stat.S_ISDIR(pathstat.st_mode):
                lines = []
            else:
                lines = self._get_qrcode_lines(path, child)
            children.append({
                'name': child,
                'size': self.parse_size(pathstat.st_size),
                'modify_time': date.parse_timestamp2str(
                    pathstat.st_mtime, '%Y-%m-%d %H:%M:%S %Z'),
                'type': 'folder' if stat.S_ISDIR(pathstat.st_mode) else 'file',
                'qrcode': lines
            })
        children = sorted(children, key=lambda item: item['type'],
                          reverse=True)
        return children

    def parse_size(self, size):
        ONE_KB = 1024
        ONE_MB = ONE_KB * 1024
        ONE_GB = ONE_MB * 1024
        if size >= ONE_GB:
            return '{:.2f} GB'.format(size / ONE_GB)
        elif size >= ONE_MB:
            return '{:.2f} MB'.format(size / ONE_MB)
        elif size >= ONE_KB:
            return '{:.2f} KB'.format(size / ONE_KB)
        else:
            return '{:.2f} B'.format(size)


fs_controller = FSController('e:')


class HomeView(views.MethodView):

    def get(self):
        return flask.redirect('/index.html')


class IndexView(views.MethodView):

    def get(self):
        return flask.render_template('index.html')


class QrcodeView(views.MethodView):
    
    def get(self):
        qr = code.QRCodeExtend(border=1)
        qr.add_data('http://{0}:{1}'.format(HOST, PORT))
        buffer = qr.parse_image_buffer()
        return buffer.getvalue()


class DirView(views.MethodView):

    def get(self):
        req_path = flask.request.args.get('path', '/')
        if not req_path:
            return flask.Response(json.dumps({'error': 'path is none'}),
                                status=400)
        if not fs_controller.path_exists(req_path):
            return flask.Response(json.dumps({'error': 'path is not exists'}),
                                status=404)
        resp_data = {'dir': {
            'path': req_path, 'children': fs_controller.get_dirs(req_path)}
        }
        return resp_data


class DownloadView(views.MethodView):

    def get(self, file_name):
        req_path = flask.request.args.get('path', '/')
        download_path = req_path + '/' + file_name
        if not fs_controller.path_exists(download_path):
            return flask.Response(json.dumps({'error': 'path is not exists'}),
                                  status=404)
        abs_path = fs_controller.get_abs_path(download_path)
        directory = os.path.dirname(abs_path)
        return flask.send_from_directory(
            directory, file_name, as_attachment=False)


class ActionView(views.MethodView):

    def post(self):
        print(self)
        print(flask.request)


app = Flask(__name__,
            template_folder=os.path.join(ROUTE, 'templates'),
            static_folder=os.path.join(ROUTE, 'static')
)

# avoid conflict with vue
app.jinja_env.variable_start_string = '[['
app.jinja_env.variable_end_string = ']]'

app.add_url_rule(r'/', view_func=HomeView.as_view('home'))
app.add_url_rule(r'/index.html', view_func=IndexView.as_view('index'))
app.add_url_rule(r'/dir', view_func=DirView.as_view('dir'))
app.add_url_rule(r'/action', view_func=ActionView.as_view('action'))
app.add_url_rule(r'/download/<file_name>',
                 view_func=DownloadView.as_view('download'))
app.add_url_rule(r'/qrcode',
                 view_func=QrcodeView.as_view('qrcode'))


def main():
    global HOST
    HOST = net.get_internal_ip()
    app.run(host=HOST, port=8000, debug=True)


if __name__ == '__main__':
    main()
