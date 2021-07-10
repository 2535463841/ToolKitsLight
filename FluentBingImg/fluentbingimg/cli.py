import argparse
import logging
import sys

from fluentlib.common import log
from fluentlib import system

from fluentlib.common import cliparser
from fluentlib.common import log

from . import downloader

LOG = log.getLogger(__name__)

UHD_CHOICES = ['only', 'include', 'no']
RESOLUTION_UHD = 'uhd'
RESOLUTION_1920 = '1920x1080'
UHD_CHOICES = ['only', 'include', 'no']
UHD_RESOLUTION_MAPPING = {'include': None,
                          'no': RESOLUTION_1920,
                          'only': RESOLUTION_UHD}

arguments = [
    cliparser.Argument('page', type=int,
                       help='download page begin with'),
    cliparser.Argument('-d', '--debug', action='store_true',
                       help='show debug message'),
    cliparser.Argument('-e', '--end', type=int,
                       help='end page, default is None'),
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


def main():
    parser = argparse.ArgumentParser()
    for argument in arguments:
        parser.add_argument(*argument.args, **argument.kwargs)

    args = parser.parse_args()
    if args.debug:
        log.set_default(level=logging.DEBUG)

    if args.wget and system.OS.is_windows():
        LOG.error('wget is not support in windows')
        return 1

    if args.end and args.end < args.page:
        LOG.error('invalid value, end page can not lower than start page.')
        return 1

    driver = downloader.BingImagDownloader()
    for page in range(args.page, (args.end or args.page) + 1):
        driver.download(page,
                        resolution=UHD_RESOLUTION_MAPPING[args.uhd],
                        progress=not args.no_progress,
                        download_dir=args.dir,
                        workers=args.workers,
                        timeout=args.timeout,
                        use_wget=args.wget)


if __name__ == '__main__':
    sys.exit(main())
