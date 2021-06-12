import importlib
import logging
import sys

from fluentlib.common import log

from . import base

LOG = log.getLogger(__name__)


def main():
    importlib.import_module('fluentclient.fluentcore.qrcode')
    importlib.import_module('fluentclient.fluentcore.sshpass')
    importlib.import_module('fluentclient.fluentcore.fs')
    args = base.SUB_CLI_PARSER.parse_args()
    if not hasattr(args, 'cli'):
        base.SUB_CLI_PARSER.print_usage()
        return 1

    if args.debug:
        log.set_default(level=logging.DEBUG)

    try:
        args.cli()(args)
        return 0
    except KeyboardInterrupt:
        LOG.error("user interrupt")
        return 1


if __name__ == '__main__':
    sys.exit(main())
