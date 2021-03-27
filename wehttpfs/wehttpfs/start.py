import os
import sys
import logging

from flask import app

from controller import HttpFsServer


ROUTE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(ROUTE, 'templates')
STATIC = os.path.join(ROUTE, 'static')


def main():
    LOG = logging.getLogger('controller')
    LOG.setLevel(logging.DEBUG)
    stream_hander = logging.StreamHandler()
    stream_hander.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
    )
    LOG.addHandler(stream_hander)

    server = HttpFsServer(template_folder=TEMPLATES,
                          static_folder=STATIC,
                          fs_root=sys.argv[1] if len(sys.argv) > 1 else None)
    server.start(debug=True)


if __name__ == '__main__':
    main()
