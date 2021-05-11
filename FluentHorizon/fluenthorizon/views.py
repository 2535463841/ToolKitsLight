import os
import json
import flask
import logging

from urllib import parse

from flask import views
from flask import current_app
from flask import session

from fluentcore import code
from fluentcore import fs

from openstack import client

LOG = logging.getLogger(__name__)

OS_AUTH_URL = 'http://controller:35357/v3'

CLIENTS = {}

def get_json_response(data, status=200):
    return flask.Response(json.dumps(data), status=status)


class HomeView(views.MethodView):

    def get(self):
        return flask.redirect('/login')


class IndexView(views.MethodView):

    def get(self):
        if session.get('username') not in CLIENTS:
            return flask.redirect('/login')
        return flask.render_template('index.html')


class QrcodeView(views.MethodView):

    def get(self):
        qr = code.QRCodeExtend(border=1)
        file_name = flask.request.args.get('file')
        file_path = flask.request.args.getlist('path_list') or []
        if file_name and file_path is not None:
            content = parse.urlunparse([
                'http', current_app.config['SERVER_NAME'],
                'download/{0}'.format(file_name), None,
                parse.urlencode({'path_list': file_path}, doseq=True),
                None])
        else:
            content = parse.urlunparse([
                'http', current_app.config['SERVER_NAME'], '', None,
                None, None])
        qr.add_data(content)
        buffer = qr.parse_image_buffer()
        return buffer.getvalue()


class ActionView(views.MethodView):

    ACTIONS = {
        'list_services', 'list_endpoints',
        'list_users', 'list_projects',
        'get_endpoint',

        'list_routers', 'list_networks', 'list_subnets', 'list_ports',
        'list_agents',

        'list_hypervisors', 'list_servers'
    }

    def post(self):
        """
        POST {
            'action': {
                'name': 'ACTION_NAME',
                'params' : {
                    'arg1': ARG1,
                    'arg2': ARG2,
                }
            }
        }
        """
        data = flask.request.get_data()
        if not data:
            msg = 'action body  not found'
            return get_json_response({'error': msg}, status=400)
        
        action = json.loads(data).get('action')
        name = action.get('name')
        params = action.get('params')
        LOG.debug('request action: %s, %s', name, params)
        if name not in self.ACTIONS:
            msg = 'action {0} is not supported'.format(name)
            return get_json_response({'error': msg}, status=400)
        try:
            resp_body = getattr(self, name)(params)
            return resp_body
        except Exception as e:
            LOG.exception(e)
            return get_json_response({'error': str(e)}, status=400)

    def list_services(self, params):
        items = []
        columns = ['id', 'enabled', 'name', 'type']
        for item in CLIENTS[session.get('username')].keystone.services.list():
            print(item)
            items.append(
                {k: getattr(item, k) for k in columns}
            )
        return {'services': items}

    def list_endpoints(self, params):
        items = []
        columns = ['id', 'enabled', 'interface', 'region', 'url', 'service_id']
        for item in CLIENTS[session.get('username')].keystone.endpoints.list():
            items.append(
                {k: getattr(item, k) for k in columns}
            )
        return {'endpoints': items}

    def list_projects(self, params):
        items = []
        columns = ['id', 'enabled', 'name']
        for item in CLIENTS[session.get('username')].keystone.projects.list():
            items.append(
                {k: getattr(item, k) for k in columns}
            )
        return {'projects': items}

    def list_users(self, params):
        items = []
        columns = ['id', 'enabled', 'name']
        for item in CLIENTS[session.get('username')].keystone.users.list():
            items.append(
                {k: getattr(item, k) for k in columns}
            )
        return {'users': items}

    def list_networks(self, params):
        # for network in CLIENTS[session.get('username')].neutron.list_networks():
        #     print(CLIENTS[session.get('username')].neutron.list_networks())
        return CLIENTS[session.get('username')].neutron.list_networks()

    def list_routers(self, params):
        return CLIENTS[session.get('username')].neutron.list_routers()

    def list_subnets(self, params):
        return CLIENTS[session.get('username')].neutron.list_subnets()

    def list_ports(self, params):
        return CLIENTS[session.get('username')].neutron.list_ports()

    def list_agents(self, params):
        return CLIENTS[session.get('username')].neutron.list_agents()

    def _make_dict_list(self, objects, keys):
        items = []
        for item in objects:
            items.append(
                {k: getattr(item, k) for k in keys}
            )
        return items

    def list_hypervisors(self, params):
        return {
            'hypervisors': self._make_dict_list(
                CLIENTS[session.get('username')].nova.hypervisors.list(),
                ['hypervisor_hostname', 'hypervisor_type', 'host_ip',
                 'status', 'state', 'memory_mb_used', 'memory_mb',
                 'vcpus_used', 'vcpus'])
        }

    def list_servers(self, params):
        return {
            'servers': self._make_dict_list(
                CLIENTS[session.get('username')].nova.servers.list(),
                ['id', 'name', 'status'])
        }


class FaviconView(views.MethodView):

    def get(self):
        return flask.send_from_directory(current_app.static_folder,
                                         'httpfs.png')


class ServerView(views.MethodView):

    def get(self):
        return {'server': {
            'name': 'Openstack',
            'version': '0.1'
            }
        }


class LoginView(views.MethodView):
    
    def get(self):
        return flask.render_template('login.html')
    
    def post(self):
        data = flask.request.get_data()
        if not data:
            msg = 'login info not found'
            return get_json_response({'error': msg}, status=400)
        auth = json.loads(data).get('auth', {})
        username = auth.get('username')
        password = auth.get('password')
        project_name = auth.get('project_name')
        user_domain_name = auth.get('user_domain_name', 'Default')
        project_domain_name = auth.get('project_domain_name', 'Default')
        openstackclient = client.OpenstackClient(
            OS_AUTH_URL,
            username=username, password=password, project_name=project_name,
            user_domain_name=user_domain_name,
            project_domain_name=project_domain_name
        )
        try:
            session['username'] = username
            CLIENTS[username] = openstackclient
            return get_json_response({'msg': 'login success'})
        except Exception as e:
            LOG.exception(e)
            return get_json_response({'error': 'auth failed'}, status=400)
