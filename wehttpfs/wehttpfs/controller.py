import os
from os.path import abspath
import stat
import json
from sys import api_version, path
from tempfile import tempdir
import flask
import logging
import mimetypes

from flask import views
from flask import Flask
from flask import Response
from flask import current_app

from wetool import date
from wetool import code
from wetool import net
from wetool import fs

FS_CONTROLLER = None


LOG = logging.getLogger(__name__)


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
                'qrcode': '' if stat.S_ISDIR(pathstat.st_mode) else
                '/qrcode?file={0}&path={1}'.format(file_name, path)
                }

    def editable(self, path):
        abs_path = self.get_abs_path(path)
        if os.path.isfile(abs_path):
            t, _ = mimetypes.guess_type(abs_path)
            LOG.debug('path type is %s', t)
            if t in ['text/plain']:
                return True
        return False

    def create_dir(self, path):
        abs_path = self.get_abs_path(path)
        if self.path_exists(abs_path):
            return FileExistsError(path)
        os.makedirs(abs_path)

    def rename_dir(self, path, new_name):
        abs_path = self.get_abs_path(path)
        new_path = os.path.join(os.path.dirname(abs_path), new_name)
        os.rename(abs_path, new_path)

    def delete_dir(self, path, file_name=None, force=False):
        LOG.debug('delete dir: %s, %s', path, file_name)
        if file_name:
            abs_path = self.get_abs_path(path + '/' + file_name)
        else:
            abs_path = self.get_abs_path(path)
        if not self.path_exists(abs_path):
            raise FileNotFoundError(abs_path)
        fs.remove(abs_path, recursive=force)

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
                continue
            pathstat = os.stat(child_path)
            path_dict = self.get_path_dict(child, path, pathstat)
            path_dict['editable'] = self.editable(child_path)
            dirs.append(path_dict)
        return sorted(dirs, key=lambda k: k['type'], reverse=True)

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

    def get_file_content(self, path):
        if not self.path_exists(path):
            return FileNotFoundError('path not found: %s' % path)
        if not self.is_file(path):
            return ValueError('path is not a file: %s' % path)
        abs_path = self.get_abs_path(path)
        with open(abs_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return ''.join(lines)

    def is_file(self, path):
        abs_path = self.get_abs_path(path)
        return os.path.isfile(abs_path)

    def save_file(self, path, fo):
        if not fo:
            raise ValueError('file is null')
        save_path = self.get_abs_path(
            os.path.join(path, *os.path.dirname(fo.filename).split('/'))
        )
        file_name = os.path.basename(fo.filename)

        if not os.path.exists(save_path):
            os.makedirs(save_path)
        fo.save(os.path.join(save_path, file_name))


def get_json_response(data, status=200):
    return flask.Response(json.dumps(data), status=status)


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
            content = 'http://{}/download/{}?path={}'.format(
                current_app.config['SERVER_NAME'], file_name, file_path)
        else:
            content = 'http://{}'.format(current_app.config['SERVER_NAME'])
        qr.add_data(content)
        buffer = qr.parse_image_buffer()
        return buffer.getvalue()


class DirView(views.MethodView):

    def get(self):
        req_path = flask.request.args.get('path', '/')
        if not req_path:
            return flask.Response(json.dumps({'error': 'path is none'}),
                                  status=400)
        if not FS_CONTROLLER.path_exists(req_path):
            return flask.Response(json.dumps({'error': 'path is not exists'}),
                                  status=404)
        resp_data = {'dir': {
            'path': req_path, 'children': FS_CONTROLLER.get_dirs(req_path)}
        }
        return resp_data


class DownloadView(views.MethodView):

    def get(self, file_name):
        req_path = flask.request.args.get('path', '/')
        download_path = req_path + '/' + file_name
        if not FS_CONTROLLER.path_exists(download_path):
            return get_json_response({'error': 'path is not exists'},
                                     status=404)
        abs_path = FS_CONTROLLER.get_abs_path(download_path)
        directory = os.path.dirname(abs_path)
        return flask.send_from_directory(
            directory, file_name, as_attachment=False)


class ActionView(views.MethodView):

    ACTION_MAP = {
        'list_dir': 'list_dir',
        'create_dir': 'create_dir',
        'delete_dir': 'delete_dir',
        'get_qrcode': 'get_qrcode',
        'rename_dir': 'rename_dir',
        'get_file': 'get_file',
        'upload_file': 'upload_file'
    }

    def post(self):
        action = flask.request.form.get('action')
        if action:
            action = json.loads(action)
        else:
            action = json.loads(
                flask.request.get_data() or '{}').get('action')
        if not action:
            msg = 'action not found in body'
            return get_json_response({'error': msg}, status=400)

        name = action.get('name')
        params = action.get('params')
        LOG.debug('request action: %s, %s', name, params)
        if name not in self.ACTION_MAP:
            msg = 'action %s is not supported'.format(name)
            return get_json_response({'error': msg}, status=400)
        try:
            resp_body = getattr(self, name)(params)
            return resp_body
        except Exception as e:
            import traceback
            traceback.print_exc()
            return get_json_response({'error': str(e)}, status=400)

    def upload_file(self, params):
        f = flask.request.files.get('file')
        if not f:
            return get_json_response({'error': 'file is null'})
        FS_CONTROLLER.save_file(params.get('path'), f)
        return {'result': 'file save success'}

    def list_dir(self, params):
        self._check_params(params)
        req_path = params.get('path')
        return {'dir': {
            'path': req_path,
            'children': FS_CONTROLLER.get_dirs(
                req_path, all=params.get('all', False))}
                }

    def create_dir(self, params):
        if not params.get('path'):
            raise ValueError('path is None')
        req_path = params.get('path') + '/' + params.get('dir_name')
        if FS_CONTROLLER.path_exists(req_path):
            raise ValueError('path is already exists: ' + req_path)
        FS_CONTROLLER.create_dir(req_path)
        return {'result': 'create success'}

    def delete_dir(self, params):
        self._check_params(params)
        FS_CONTROLLER.delete_dir(params.get('path'),
                                 file_name=params.get('file'),
                                 force=params.get('force'))
        return {'result': 'delete success'}

    def rename_dir(self, params):
        '''
        params: {'path': 'xxx', 'file': 'yy', 'new_name': 'yy1'}
        '''
        self._check_params(params)
        if not params.get('new_name'):
            return get_json_response({'error': 'new name is none'}, status=400)
        FS_CONTROLLER.rename_dir(
            os.path.join(params.get('path'), params.get('file') or ''),
            params.get('new_name'),
        )
        return {'result': 'rename success'}

    def _check_params(self, params):
        req_path = params.get('path')
        if not req_path:
            raise ValueError('path is None')
        if not FS_CONTROLLER.path_exists(req_path):
            raise ValueError('path is not exists')

    def get_file(self, params):
        '''
        params: {'path': 'xxx', 'file': 'yy'}
        '''
        self._check_params(params)

        if not params.get('file'):
            return get_json_response({'error': 'file name is none'}, status=400)

        content = FS_CONTROLLER.get_file_content(
            os.path.join(params.get('path'), params.get('file')),
        )
        return {'file': {
            'name': params.get('file'),
            'content': content}
        }


class FaviconView(views.MethodView):

    def get(self):
        return flask.send_from_directory(current_app.static_folder,
                                         'httpfs.png')


class HttpFsServer(object):

    def __init__(self, host=None, port=80,
                 template_folder=None, static_folder=None, fs_root=None):
        self.host = host or net.get_internal_ip()
        self.port = port
        self.template_folder = template_folder
        self.static_folder = static_folder
        self.fs_root = fs_root or './'
        self.driver = FSController(self.fs_root)
        self.app = Flask('WeHttpFS',
                         template_folder=self.template_folder,
                         static_folder=self.static_folder)

    def register_rule(self):
        self.app.add_url_rule(r'/favicon.ico',
                              view_func=FaviconView.as_view('favicon'))
        self.app.add_url_rule(r'/', view_func=HomeView.as_view('home'))
        self.app.add_url_rule(r'/index.html',
                              view_func=IndexView.as_view('index'))
        self.app.add_url_rule(r'/dir', view_func=DirView.as_view('dir'))
        self.app.add_url_rule(r'/action',
                              view_func=ActionView.as_view('action'))
        self.app.add_url_rule(r'/download/<file_name>',
                              view_func=DownloadView.as_view('download'))
        self.app.add_url_rule(r'/qrcode',
                              view_func=QrcodeView.as_view('qrcode'))

    def start(self, debug=False):
        LOG.info('config server')
        print(LOG.name)
        global FS_CONTROLLER
        FS_CONTROLLER = FSController(self.fs_root)
        self.register_rule()
        # NOTE(zbw) avoid conflict with vue
        self.app.jinja_env.variable_start_string = '[['
        self.app.jinja_env.variable_end_string = ']]'
        self.app.config['SERVER_NAME'] = '{}:{}'.format(self.host, self.port)
        LOG.info('strarting server')
        self.app.run(host=self.host, port=self.port, debug=debug)
