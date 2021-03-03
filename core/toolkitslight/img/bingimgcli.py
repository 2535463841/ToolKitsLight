import logging
import argparse

from toolkitslight.img import bingimg

LOG = logging.getLogger(__name__)


SUPPORTED_RESOLUTION = [bingimg.BingImagDownloader.RESOLUTION_1080,
                        bingimg.BingImagDownloader.RESOLUTION_UHD]


def main():
    parser = argparse.ArgumentParser('Bing Img Downloader Cli')
    parser.add_argument('page', type=int)
    parser.add_argument('-d', '--debug', action='store_true',
                        help='show debug message')
    parser.add_argument('-r', '--resolution', choices=SUPPORTED_RESOLUTION,
                        help='the resolution fo image to dowload')
    parser.add_argument('-w', '--workers', type=int, default=12,
                        help='the num download workers, default is 12')
    parser.add_argument('-t', '--timeout', type=int, default=300,
                        help='timeout, default is 300s')
    parser.add_argument('--dir',
                        help='the directory to save')
    parser.add_argument('-p', '--process', action='store_true',
                        help='show process, default is False')
    args = parser.parse_args()

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))

    log = logging.getLogger('toolkitslight.web')

    for logger in [LOG, log]:
        logger.addHandler(stream_handler)
        logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    downloader = bingimg.BingImagDownloader()
    downloader.download(args.page,
                        resolution=args.resolution,
                        process=args.process,
                        download_dir=args.dir,
                        workers=args.workers,
                        timeout=args.timeout
                 )


if __name__ == '__main__':
    main()
