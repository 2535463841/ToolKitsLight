import argparse
import logging
import os

from fluentcore.common import log

import server
import conf

LOG = log.getLogger(__name__)
CONF = conf.CONF


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

    conf.retister_opts()
    conf_files = [
        '/etc/horizon.conf', './etc/horizon.conf',
        '.horizon.conf', 'horizon.conf'
    ]
    for conf_file in conf_files:
        if os.path.isfile(conf_file):
            LOG.debug('load config %s', conf_file)
            CONF.load(conf_file)
    if not CONF.conf_files():
        LOG.warning('config file not found: %s', conf_files)
    LOG.debug('auth url is %s', CONF.openstack.auth_url)
    wsig_server = server.HorizonHttpServer(port=CONF.port)
    wsig_server.start(develoment=args.development, debug=args.debug)


if __name__ == '__main__':
    main()
