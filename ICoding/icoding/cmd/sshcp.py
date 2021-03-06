import logging
import sys

from icoding.common import cliparser
from icoding.common import log
from icoding.commands import sshcp

LOG = log.getLogger(__name__)


def main():
    cli_parser = cliparser.SubCliParser('python SSH & SCP utils')
    cli_parser.register_clis(sshcp.SSHCmd, sshcp.ScpGet, sshcp.ScpPut)
    try:
        cli_parser.call()
        return 0
    except KeyboardInterrupt:
        LOG.error("user interrupt")
        return 1


if __name__ == '__main__':
    sys.exit(main())
