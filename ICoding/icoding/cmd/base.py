import logging
import sys

from icoding.common import cliparser
from icoding.common import log
from icoding.commands import fs
from icoding.commands import qrcode
from icoding.commands import setpip
from icoding.commands import code

LOG = log.getLogger(__name__)


def main():
    cli_parser = cliparser.SubCliParser('Some Simple utils')
    for cls in [fs.PyTac, qrcode.QrcodeParse, qrcode.QrcodeDump,
                setpip.SetPip, code.JsonGet, code.Md5Sum]:
        cli_parser.register_cli(cls)
    args = cli_parser.parse_args()

    if not hasattr(args, 'cli'):
        cli_parser.print_usage()
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
