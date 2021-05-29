import importlib
import logging
import sys

from fluentcore.common import log

from fluentclient import base

LOG = log.getLogger(__name__)


def main():
    importlib.import_module('fluentclient.fluentcore.qrcode')
    importlib.import_module('fluentclient.fluentcore.sshpass')
    args = base.SUB_CLI_PARSER.parse_args()
    if not hasattr(args, 'cli'):
        base.SUB_CLI_PARSER.print_usage()
        return 1

    if args.debug:
        LOG.setLevel(logging.DEBUG)
        log.set_default(level=logging.DEBUG)

    try:
        args.cli()(args)
        return 0
    except KeyboardInterrupt:
        LOG.error("user interrupt")
        return 1


if __name__ == '__main__':
    sys.exit(main())
