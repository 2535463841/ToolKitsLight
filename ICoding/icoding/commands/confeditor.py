from __future__ import print_function
import argparse
import collections

from icoding.common import cliparser
from icoding.common import log
from icoding.common import confparser

LOG = log.getLogger(__name__)


def print_error(message):
    print('Error:', message)
    return 1


class ConfigList(cliparser.CliBase):
    NAME = 'list'
    ARGUMENTS = [
        cliparser.Argument('file', type=argparse.FileType(),
                           help='The path of file'),
        cliparser.Argument('section', nargs='?',
                           help='Section name'),
    ]

    def __call__(self, args):
        LOG.debug(args)
        parser = confparser.ConfigParserWrapper()
        parser.read(args.file)

        print('[{}]'.format('DEFAULT'))
        for opt, val in parser.options('DEFAULT').items():
            print(opt, '=', val)
        print()
        for section in parser.sections():
            print('[{}]'.format(section))
            for opt, val in parser.options(section,
                                           ignore_default=True).items():
                print(opt, '=', val)
            print()