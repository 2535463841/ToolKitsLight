from datetime import datetime
from re import I
import flask
import json

from flask import views
from flask import current_app
from flask import session

from fluentlib import date
from fluentlib.common import log

from openstack import client

import conf

LOG = log.getLogger(__name__)

CONF = conf.CONF

CLIENTS = {}

_CACHE_DOMAINS = {}
_CACHE_IMAGES = {}
_CACHE_FLAVORS = {}
_CACHE_PROJECTS = {}

SERVER_NAME = 'FLuentHorizon'
VERSION = 1.0

DEFAULT_CONTEXT = {
    'name': SERVER_NAME,
    'version': VERSION,
}

def get_client():
    auth = session.get('auth')
    username = auth.get('username')
    if username not in CLIENTS:
        password = auth.get('password')
        project_name = auth.get('projectName')
        user_domain_name = auth.get('userDomain', 'Default')
        project_domain_name = auth.get('projectDomain', 'Default')

        openstackclient = client.OpenstackClient(
            CONF.openstack.auth_url,
            username=username, password=password, project_name=project_name,
            user_domain_name=user_domain_name,
            project_domain_name=project_domain_name,
        )
        CLIENTS[username] = openstackclient
    return CLIENTS[username]


def get_json_response(data, status=200):
    return flask.Response(json.dumps(data), status=status)


class HomeView(views.MethodView):

    def get(self):
        return flask.redirect('/login')


class HtmlView(views.MethodView):

    def get(self, name):
        if not session.get('auth'):
            return flask.redirect('/login')
        return flask.render_template('{}.html'.format(name),
                                     **DEFAULT_CONTEXT)


class IndexView(views.MethodView):

    def get(self):
        return flask.render_template('compute.html', **DEFAULT_CONTEXT)


class ActionView(views.MethodView):

    ACTIONS = {
        'get_auth_info',
        'get_endpoint',
        'list_services', 'list_endpoints',
        'list_users', 'list_projects', 'list_groups', 'list_roles',
        'list_routers', 'list_networks', 'list_subnets', 'list_ports',
        'list_agents',
        'list_hypervisors', 'list_servers', 'list_instances',
        'list_images', 'list_flavors', 'list_keypairs',
        'list_quotas',
        'list_floatingips', 'list_security_groups',
        'show_usages',
    }

    def post(self):
        """
        POST {
            'action': {
                'name': 'ACTION_NAME',
                'params' : {'arg1': ARG1, 'arg2': ARG2,}
            }
        }
        """
        data = flask.request.get_data()
        if not data:
            msg = 'action body  not found'
            return get_json_response({'error': msg}, status=400)

        action = json.loads(data).get('action')
        name = action.get('name')
        params = action.get('params', {})
        LOG.debug('request action: %s, %s', name, params)
        if name not in self.ACTIONS:
            msg = 'action {0} is not supported'.format(name)
            return get_json_response({'error': msg}, status=400)
        try:
            resp_body = getattr(self, name)(**params)
            return resp_body
        except Exception as e:
            LOG.exception(e)
            return get_json_response({'error': str(e)}, status=400)

    def list_services(self, **params):
        items = []
        columns = ['id', 'enabled', 'name', 'type']
        for item in get_client().keystone.services.list():
            items.append(
                {k: getattr(item, k) for k in columns}
            )
        return {'services': items}

    def list_endpoints(self, **params):
        items = []
        columns = ['id', 'enabled', 'interface', 'region', 'url', 'service_id']
        for item in get_client().keystone.endpoints.list():
            items.append(
                {k: getattr(item, k) for k in columns}
            )
        return {'endpoints': items}

    def list_projects(self, **params):
        if not _CACHE_DOMAINS:
            self.list_domains()
        items = []
        columns = ['id', 'enabled', 'name', 'description', 'domain_id']
        user_id = session.get('auth').get('userId')
        for item in get_client().keystone.projects.list():
            item_dict = self._make_dict_object(item, columns)
            if item.domain_id in _CACHE_DOMAINS:
                item_dict['domain_name'] = _CACHE_DOMAINS[item.domain_id].name
            else:
                item_dict['domain_name'] = ''
            items.append(item_dict)
        LOG.debug('projects %s', items)
        return {'projects': items}

    def list_domains(self):
        if not _CACHE_DOMAINS:
            domains = get_client().keystone.domains.list()
            for domain in domains:
                _CACHE_DOMAINS[domain.id] = domain
        items = self._make_dict_list(_CACHE_DOMAINS.values(),
                                     ['id', 'name', 'enabled', 'description'])
        return items

    def list_users(self, **params):
        if not _CACHE_DOMAINS:
            self.list_domains()
        items = []
        columns = ['id', 'enabled', 'name', 'description', 'domain_id']
        for item in get_client().keystone.users.list():
            item_dict = self._make_dict_object(item, columns)
            if item.domain_id in _CACHE_DOMAINS:
                item_dict['domain_name'] = _CACHE_DOMAINS[item.domain_id].name
            else:
                item_dict['domain_name'] = ''
            items.append(item_dict)
        return {'users': items}

    def list_networks(self, **params):
        # for network in get_client().neutron.list_networks():
        #     print(get_client().neutron.list_networks())
        return get_client().neutron.list_networks()

    def list_routers(self, **params):
        return get_client().neutron.list_routers()

    def list_subnets(self, **params):
        return get_client().neutron.list_subnets()

    def list_ports(self, **params):
        return get_client().neutron.list_ports()

    def list_agents(self, **params):
        return get_client().neutron.list_agents()

    def list_floatingips(self, **params):
        return get_client().neutron.list_floatingips()

    def list_security_groups(self, **params):
        return get_client().neutron.list_security_groups()

    def _make_dict_list(self, objects, keys):
        items = []
        for item in objects:
            items.append(
                {k: getattr(item, k) for k in keys}
            )
        return items

    def _make_dict_object(self, obj, keys):
        item = {}
        for key in keys:
            item[key] = getattr(obj, key, '')
        return item

    def list_hypervisors(self, **params):
        return {
            'hypervisors': self._make_dict_list(
                get_client().nova.hypervisors.list(),
                ['hypervisor_hostname', 'hypervisor_type', 'host_ip',
                 'status', 'state', 'memory_mb_used', 'memory_mb',
                 'vcpus_used', 'vcpus'])
        }

    def list_servers(self, **params):
        global _CACHE_IMAGES, _CACHE_FLAVORS
        nclient = get_client().nova
        servers = self._make_dict_list(
            nclient.servers.list(),
            ['id', 'name', 'status', "OS-EXT-STS:task_state", 'addresses',
             "image", 'OS-EXT-STS:vm_state', 'created',
             'OS-EXT-AZ:availability_zone', 'flavor',
             "OS-EXT-STS:power_state", 'key_name'])
        for server in servers:
            image_id = server.get('image').get('id')
            if image_id not in _CACHE_IMAGES:
                _CACHE_IMAGES = {
                    i['id']: i for i in self.list_images().get('images')
                }
            server['image'] = _CACHE_IMAGES[image_id]
            flavor_id = server.get('flavor').get('id')
            if flavor_id not in _CACHE_FLAVORS:
                _CACHE_FLAVORS = {
                    i['id']: i for i in self.list_flavors().get('flavors')
                }
            server['flavor'] = _CACHE_FLAVORS[flavor_id]
        return {'servers': servers}

    def list_instances(self, **params):
        return {
            'instances': self.list_servers().get('servers')
        }

    def get_auth_info(self, **params):
        return {'auth': session.get('auth')}

    def list_images(self, **params):
        global _CACHE_PROJECTS
        gclient = get_client().glance
        images = self._make_dict_list(
            gclient.images.list(),
            ['id', 'name', 'status', 'container_format', 'disk_format',
             'size', 'visibility', 'protected', 'owner'])

        user_id = session.get('auth').get('userId')
        for image in images:
            owner_id = image.get('owner')
            if owner_id not in _CACHE_PROJECTS:
                projects = get_client().keystone.projects.list(user=user_id)
                _CACHE_PROJECTS = {p.id: p for p in projects}
            if owner_id in _CACHE_PROJECTS:
                image['owner_name'] = _CACHE_PROJECTS.get(owner_id).name
            else:
                image['owner_name'] = None
        return {'images': images}

    def list_flavors(self, **params):
        nclient = get_client().nova
        return {'flavors': self._make_dict_list(
            nclient.flavors.list(),
            ['id', 'name', 'ram', 'vcpus', 'os-flavor-access:is_public',
             'rxtx_factor', 'disk', 'OS-FLV-EXT-DATA:ephemeral', 'swap'
             ])
        }

    def list_keypairs(self, **params):
        nclient = get_client().nova
        return {'keypairs': self._make_dict_list(
            nclient.keypairs.list(),
            ['id', 'name', 'fingerprint', 'public_key'])
        }

    def list_quotas(self, **params):
        c = get_client()
        quota = self._make_dict_object(c.get_quota(),
                                       ['instances', 'cores', 'ram',
                                        'floating_ips', 'security_groups',
                                        'key_pairs'])
        return {'quotas': quota}

    def show_usages(self, **params):
        import time
        start, end = None, None
        if 'start' in params:
            start_ts = date.parse_str2timestamp(params['start'],
                                                date_format='%Y-%m-%d')
            start = datetime.fromtimestamp(start_ts)
        if 'end' in params:
            end_ts = date.parse_str2timestamp(params['end'],
                                              date_format='%Y-%m-%d')
            end = datetime.fromtimestamp(end_ts)
        if not start:
            start = date.datetime_before(days=30)
        if not end:
            end = datetime.now()
        nova = get_client().nova
        usage = nova.usage.get(session['auth']['projectId'], start, end)
        return {'usage': usage.to_dict()}

    def list_groups(self):
        keystone = get_client().keystone
        return {'groups': self._make_dict_list(
            keystone.groups.list(), ['id', 'name', 'description'])
        }

    def list_roles(self):
        keystone = get_client().keystone
        return {'roles': self._make_dict_list(
            keystone.roles.list(), ['id', 'name'])
        }


class FaviconView(views.MethodView):

    def get(self):
        return flask.send_from_directory(current_app.static_folder,
                                         'httpfs.png')


class ServerView(views.MethodView):

    def get(self):
        return {'server': {
            'name': 'Openstack',
            'version': '0.1',
            'username': session.get('auth').get('username')}
        }


class LoginView(views.MethodView):

    def get(self):
        return flask.render_template('login.html', **DEFAULT_CONTEXT)

    def post(self):
        data = flask.request.get_data()
        if not data:
            msg = 'login info not found'
            return get_json_response({'error': msg}, status=400)
        auth = json.loads(data).get('auth', {})
        username, password = auth.get('username'), auth.get('password')
        project_name = auth.get('projectName')
        user_domain_name = auth.get('userDomain', 'Default')
        project_domain_name = auth.get('projectDomain', 'Default')
        openstackclient = client.OpenstackClient(
            CONF.openstack.auth_url,
            username=username, password=password, project_name=project_name,
            user_domain_name=user_domain_name,
            project_domain_name=project_domain_name,
        )
        try:
            # for user in openstackclient.keystone.users.list():
            session['auth'] = auth
            session['auth']['userId'] = openstackclient.session.get_user_id()
            session['auth']['projectId'] = \
                openstackclient.session.get_project_id()
            session['auth']['authUrl'] = CONF.openstack.auth_url
            CLIENTS[username] = openstackclient
            LOG.debug('login user: %s', session.get('auth'))
            return get_json_response({'msg': 'login success'})
        except Exception as e:
            LOG.exception(e)
            return get_json_response({'error': 'auth failed'}, status=400)
