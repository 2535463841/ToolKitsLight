import sys

from icoding.common import cliparser
from icoding.common import log
from icoding.commands import fs
from icoding.commands import setpip
from icoding.commands import code

LOG = log.getLogger(__name__)


def main():
    cli_parser = cliparser.SubCliParser('Some Simple utils')
    cli_parser.register_clis(fs.PyTac, setpip.SetPip,
                             code.JsonGet, code.Md5Sum)
    try:
        cli_parser.call()
        return 0
    except KeyboardInterrupt:
        LOG.error("user interrupt")
        return 1


if __name__ == '__main__':
    sys.exit(main())
