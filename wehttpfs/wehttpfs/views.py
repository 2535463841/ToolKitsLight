import os
import json
import flask
import logging

from urllib import parse

from flask import views
from flask import current_app

from wetool import code

FS_CONTROLLER = None


LOG = logging.getLogger(__name__)


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
        file_path = flask.request.args.getlist('path_list')
        if file_name and file_path:
            content = parse.urlunparse([
                'http', current_app.config['SERVER_NAME'], 'download', None,
                parse.urlencode({'file': file_name, 'path_list': file_path}),
                None])
        else:
            content =  parse.urlunparse([
                'http', current_app.config['SERVER_NAME'], '', None,
                None, None])
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
        req_path = flask.request.args.getlist('path_list')
        if not FS_CONTROLLER.path_exists(req_path):
            return get_json_response({'error': 'path required is not exists'},
                                     status=404)
        req_path.append(file_name)
        abs_path = FS_CONTROLLER.get_abs_path(req_path)
        directory = os.path.dirname(abs_path)
        LOG.debug('download file %s', abs_path)
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
            LOG.exception(e)
            return get_json_response({'error': str(e)}, status=400)

    def upload_file(self, params):
        f = flask.request.files.get('file')
        if not f:
            return get_json_response({'error': 'file is null'})
        FS_CONTROLLER.save_file(params.get('path_list'), f)
        return {'result': 'file save success'}

    def list_dir(self, params):
        # self._check_params(params)
        req_path = params.get('path')
        if not req_path:
            req_path = params.get('path_items')
        from wetool import system
        usage = FS_CONTROLLER.disk_usage()
        
        return {
            'dir': {
                'path': req_path,
                'children': FS_CONTROLLER.get_dirs(
                    req_path, all=params.get('all', False)),
                'disk_usage': {
                    'used': usage.used, 'total': usage.total
                    }
                }
            }

    def create_dir(self, params):
        req_path = params.get('path_items')
        if FS_CONTROLLER.path_exists(req_path):
            raise ValueError('path is already exists: %s' % req_path)
        FS_CONTROLLER.create_dir(req_path)
        return {'result': 'create success'}

    def delete_dir(self, params):
        FS_CONTROLLER.delete_dir(params.get('path_items'),
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
        req_path = params.get('path') or params.get('path_items')

        if not req_path:
            raise ValueError('path is None')
        if req_path and not FS_CONTROLLER.path_exists(req_path):
            raise ValueError('path is not exists: %s' % req_path)

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
