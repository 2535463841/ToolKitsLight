import sys

from fluentbingimg import cli
from fluentcore.system import os
from fluentbingimg import downloader


def main():
    args = cli.args

    if args.wget and os.is_windows():
        print('ERROR:', 'wget is not support in windows')
        return 1

    if args.wget and os.is_windows():
        print('ERROR:', 'wget is not support in windows')
        return 1

    driver = downloader.BingImagDownloader()
    driver.download(args.page,
                    resolution=args.resolution,
                    process=args.process,
                    download_dir=args.dir,
                    workers=args.workers,
                    timeout=args.timeout,
                    use_wget=args.wget)


if __name__ == '__main__':
    sys.exit(main())
