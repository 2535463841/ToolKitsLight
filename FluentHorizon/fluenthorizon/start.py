import os
import sys
import logging

import server
from fluentcore import log

LOG = log.getLogger(__name__)
ROUTE = os.path.dirname(os.path.abspath(__file__))


def main():
    log.set_default(level=logging.DEBUG)

    http_server = server.HorizonHttpServer()
    http_server.start(debug=True)


if __name__ == '__main__':
    main()
