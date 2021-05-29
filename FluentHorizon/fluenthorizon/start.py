import argparse
import logging

from fluentcore.common import log

import server


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
    wsig_server = server.HorizonHttpServer()
    wsig_server.start(develoment=args.development, debug=args.debug)


if __name__ == '__main__':
    main()
