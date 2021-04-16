import logging
import argparse

from fluentcore.common import cliparser
from fluentcore.common import log

RESOLUTION_1080 = '1920x1080'
RESOLUTION_UHD = 'uhd'
SUPPORTED_RESOLUTION = [RESOLUTION_1080, RESOLUTION_UHD]


arguments = [
    cliparser.Argument('page', type=int),
    cliparser.Argument('-d', '--debug', action='store_true',
                       help='show debug message'),
    cliparser.Argument('-r', '--resolution', choices=SUPPORTED_RESOLUTION,
                       help='the resolution fo image to dowload'),
    cliparser.Argument('-w', '--workers', type=int, default=12,
                       help='the num download workers, default is 12'),
    cliparser.Argument('-t', '--timeout', type=int, default=300,
                       help='timeout, default is 300s'),
    cliparser.Argument('--dir',
                       help='the directory to save'),
    cliparser.Argument('-p', '--process', action='store_true',
                       help='The password for login, default is ""'),
    cliparser.Argument('--wget', action='store_true', help='use wget'),
]

parser = argparse.ArgumentParser()
for argument in arguments:
    parser.add_argument(*argument.args, **argument.kwargs)

args = parser.parse_args()
if args.debug:
    log.set_default(level=logging.DEBUG)
