import os
import sys
import logging

from fluentcore import log
from fluenthttpfs.server import HttpFsServer


ROUTE = os.path.dirname(os.path.abspath(__file__))


def main():
    log.set_default(level=logging.DEBUG)
    server = HttpFsServer(fs_root=sys.argv[1] if len(sys.argv) > 1 else None)
    server.start(debug=True)


if __name__ == '__main__':
    main()
