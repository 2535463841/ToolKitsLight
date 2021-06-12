
from fluentlib.common import config

CONF = config.ConfigOpts()


default_opts = [
    config.IntOption('port', default=8080),
    config.BooleanOption('debug', default=False),
]
openstack_opts = [
    config.Option('auth_url', default='http://localhost:35357/v3')
]


def retister_opts():
    CONF.register_opts(default_opts)
    CONF.register_opts(openstack_opts, group='openstack')
