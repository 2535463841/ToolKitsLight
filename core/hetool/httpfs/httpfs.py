import os
import stat
import json
import flask
import socket

from flask import Flask
from flask.wrappers import Response
from werkzeug.datastructures import Headers

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
                'size': pathstat.st_size,
                'modify_time': date.parse_timestamp2str(pathstat.st_mtime),
                'type': 'folder' if stat.S_ISDIR(pathstat.st_mode) else 'file',
                'qrcode': lines
            })
        children = sorted(children, key=lambda item: item['type'],
                          reverse=True)
        return children


fs_controller = FSController('e:')
app = Flask(__name__,
            template_folder=os.path.join(ROUTE, 'templates'),
            static_folder=os.path.join(ROUTE, 'static')
)
# avoid conflict with vue 
app.jinja_env.variable_start_string = '[['
app.jinja_env.variable_end_string = ']]'



@app.route('/', methods=['GET'])
def home():
    return flask.redirect('/index.html')


@app.route('/linkQrcode', methods=['GET'])
def linkQrcode():
    qr = code.QRCodeExtend(border=1)
    qr.add_data('http://{0}:{1}'.format(HOST, PORT))
    return Response(
        json.dumps({'qrcode': {'lines': qr.parse_string_lines()}})
    ) 


@app.route('/index.html', methods=['GET'])
def index():
    return flask.render_template('index.html')


@app.route('/download/<file_name>', methods=['GET'])
def download(file_name):
    req_path = flask.request.args.get('path')
    if not req_path:
        return flask.Response(json.dumps({'error': 'path is none'}),
                              status=400)
    if not fs_controller.path_exists(req_path):
        return flask.Response(json.dumps({'error': 'path is not exists'}),
                              status=404)
    abs_path = fs_controller.get_abs_path(req_path)
    directory = os.path.dirname(abs_path)
    filename = os.path.basename(abs_path)
    return flask.send_from_directory(
        directory, filename, as_attachment=False)


@app.route('/dir', methods=['GET'])
def dir():
    req_path = flask.request.args.get('path')
    if not req_path:
        return flask.Response(json.dumps({'error': 'path is none'}),
                              status=400)
    if not fs_controller.path_exists(req_path):
        return flask.Response(json.dumps({'error': 'path is not exists'}),
                             status=404)
    resp_data = {'dir': {
        'path': req_path, 'children': fs_controller.get_dirs(req_path)}
    }
    return json.dumps(resp_data, ensure_ascii=False)


def main():
    global HOST
    HOST = net.get_internal_ip()
    app.run(host=HOST, port=8000, debug=True)



if __name__ == '__main__':
    main()
