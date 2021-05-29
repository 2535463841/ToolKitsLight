import sys

from fluentcore.common import log
from fluentcore.system import os

from fluentbingimg import cli
from fluentbingimg import downloader

LOG = log.getLogger(__name__)

RESOLUTION_UHD = 'uhd'
RESOLUTION_1080 = '1920x1080'
UHD_CHOICES = ['only', 'include', 'no']
UHD_RESOLUTION_MAPPING = {
    'include': None,
    'no': RESOLUTION_1080,
    'only': RESOLUTION_UHD}


def main():
    args = cli.args

    if args.wget and os.is_windows():
        LOG.error('wget is not support in windows')
        return 1

    driver = downloader.BingImagDownloader()
    driver.download(args.page,
                    resolution=UHD_RESOLUTION_MAPPING[args.uhd],
                    progress=not args.no_progress,
                    download_dir=args.dir,
                    workers=args.workers,
                    timeout=args.timeout,
                    use_wget=args.wget)


if __name__ == '__main__':
    sys.exit(main())
