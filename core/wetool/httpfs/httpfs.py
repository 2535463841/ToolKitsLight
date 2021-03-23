import os
import stat
import json
from sys import path
import flask

from flask import views
from flask import Flask
from flask import Response

from hetool import date
from hetool import code
from hetool import net
from qrcode import constants

from werkzeug.utils import redirect

HOST = None
PORT = 8000

ROUTE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(ROUTE, 'templates')
STATIC = os.path.join(ROUTE, 'static')


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

    def get_path_dict(self, file_name, path, pathstat):
        return {'name': file_name,
                'size': self.parse_size(pathstat.st_size),
                'modify_time': date.parse_timestamp2str(
                    pathstat.st_mtime, '%Y/%m/%d %H:%M'),
                'type': 'folder' if stat.S_ISDIR(pathstat.st_mode) else 'file',
                'qrcode': '' if stat.S_ISDIR(pathstat.st_mode) else \
                    '/qrcode?file={0}&path={1}'.format(file_name, path)
        }

    def create_dir(self, path):
        abs_path = self.get_abs_path(path)
        if self.path_exists(abs_path):
            return FileExistsError(path)
        os.makedirs(abs_path)

    def delete_dir(self, path, file_name=None):
        if file_name:
            abs_path = self.get_abs_path(path + '/' + file_name)
        else:
            abs_path = self.get_abs_path(path)
        if not self.path_exists(abs_path):
            raise FileNotFoundError(path)
        elif os.path.isdir(abs_path):
            os.removedirs(abs_path)
        else:
            os.remove(abs_path)

    def get_dirs(self, path, all=False):
        children = []
        if not path:
            return children
        find_path = self.get_abs_path(path)
        dirs = []
        for child in os.listdir(find_path):
            child_path = os.path.join(find_path, child)
            
            if not all and \
                (child.startswith('.') or not os.access(child_path, os.R_OK)):
                print('continue')
                continue
            pathstat = os.stat(child_path)
            dirs.append(self.get_path_dict(child, path, pathstat))
        return sorted(dirs, key=lambda k:k['type'], reverse=True)

    def _get_file_type(self, file_name):
        suffix = os.path.splitext(file_name)[1]
        file_suffix_map = {
            'video': ['mp4', 'avi', 'mpeg'],
            'pdf': ['pdf'],
            'word': ['word'],
            'excel': ['xls', 'xlsx'],
            'archive': ['zip', 'tar', 'rar', '7zip'],
            'python': ['py', 'pyc']
        }
        if not suffix:
            return 'file'
        if suffix:
            suffix = suffix[1:].lower()
            for key, values in file_suffix_map.items():
                if suffix in values:
                    return key
            return 'file'

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


def get_json_response(data, status=200):
    return flask.Response(json.dumps(data), status=status)


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
        file_name = flask.request.args.get('file')
        file_path = flask.request.args.get('path')
        if file_name and file_path:
            qr.add_data('http://{0}:{1}/download/{2}?path={3}'.format(
                HOST, PORT, file_name, file_path))
        else:
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
        print('download', download_path)
        if not fs_controller.path_exists(download_path):
            return get_json_response({'error': 'path is not exists'},
                                     status=404)
        abs_path = fs_controller.get_abs_path(download_path)
        directory = os.path.dirname(abs_path)
        return flask.send_from_directory(
            directory, file_name, as_attachment=False)


class ActionView(views.MethodView):

    ACTION_MAP = {
        'list_dir': 'list_dir',
        'create_dir': 'create_dir',
        'delete_dir': 'delete_dir',
        'get_qrcode': 'get_qrcode'
    }

    def post(self):
        data = json.loads(flask.request.get_data())
        print(data)
        if 'action' not in data:
            msg = 'action not found in body'
            return get_json_response({'error': msg}, status=400)
        name = data.get('action').get('name')
        if name not in self.ACTION_MAP:
            msg = 'action %s is not supported'.format(name)
            return get_json_response({'error': msg}, status=400)
        try:
            resp_body = getattr(self, name)(data.get('action').get('params'))
            return resp_body
        except Exception as e:
            return get_json_response({'error': str(e)}, status=400) 

    def list_dir(self, params):
        self._check_params(params)
        req_path = params.get('path')
        print(params)
        return {'dir': {
            'path': req_path,
            'children': fs_controller.get_dirs(
                req_path, all=params.get('all', False))}
        }

    def create_dir(self, params):
        if not params.get('path'):
            raise ValueError('path is None')
        req_path = params.get('path')
        if fs_controller.path_exists(req_path):
            raise ValueError('path is already exists')
        fs_controller.create_dir(req_path)
        return {'result': 'create success'}

    def delete_dir(self, params):
        self._check_params(params)
        fs_controller.delete_dir(params.get('path'),
                                 file_name=params.get('file'))
        return {'result': 'delete success'}

    def _check_params(self, params):
        req_path = params.get('path')
        if not req_path:
            raise ValueError('path is None')
        if not fs_controller.path_exists(req_path):
            raise ValueError('path is not exists')


class FaviconView(views.MethodView):
    
    def get(self):
        return flask.send_from_directory(STATIC, 'httpfs.png')


app = Flask(__name__, template_folder=TEMPLATES, static_folder=STATIC)

# avoid conflict with vue
app.jinja_env.variable_start_string = '[['
app.jinja_env.variable_end_string = ']]'


app.add_url_rule(r'/favicon.ico', view_func=FaviconView.as_view('favicon'))
app.add_url_rule(r'/', view_func=HomeView.as_view('home'))
app.add_url_rule(r'/index.html', view_func=IndexView.as_view('index'))
app.add_url_rule(r'/dir', view_func=DirView.as_view('dir'))
app.add_url_rule(r'/action', view_func=ActionView.as_view('action'))
app.add_url_rule(r'/download/<file_name>',
                 view_func=DownloadView.as_view('download'))
app.add_url_rule(r'/qrcode',
                 view_func=QrcodeView.as_view('qrcode'))



def main():
    import sys
    global HOST, fs_controller
    HOST = net.get_internal_ip()
    if len(sys.argv[1]) > 1:
        fs_controller = FSController(sys.argv[1])
    app.run(host=HOST, port=8000, debug=True)


if __name__ == '__main__':
    main()
