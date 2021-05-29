import logging
import argparse

from fluentcore.common import cliparser
from fluentcore.common import log

UHD_CHOICES = ['only', 'include', 'no']

arguments = [
    cliparser.Argument('page', type=int),
    cliparser.Argument('-d', '--debug', action='store_true',
                       help='show debug message'),
    cliparser.Argument('-u', '--uhd', default='only', choices=UHD_CHOICES,
                       help='only: only download UHD; '
                            'include: download UHD and other resolutions; '
                            'no: do not download UHD;'),
    cliparser.Argument('-w', '--workers', type=int, default=12,
                       help='the num download workers, default is 12'),
    cliparser.Argument('-t', '--timeout', type=int, default=300,
                       help='timeout, default is 300s'),
    cliparser.Argument('--dir', default='./', help='the directory to save'),
    cliparser.Argument('-n', '--no-progress', action='store_true',
                       help='do not show progress'),
    cliparser.Argument('--wget', action='store_true', help='use wget'),
]

parser = argparse.ArgumentParser()
for argument in arguments:
    parser.add_argument(*argument.args, **argument.kwargs)

args = parser.parse_args()
if args.debug:
    log.set_default(level=logging.DEBUG)
