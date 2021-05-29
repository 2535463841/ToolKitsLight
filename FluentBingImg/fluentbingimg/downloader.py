import os
import bs4
import urllib3

from fluentcore.common import log
from fluentcore.downloader.urllib import driver as urllib_driver
from fluentcore.downloader.wget import driver as wget_driver

LOG = log.getLogger(__name__)

SCHEME = 'http'
HOST = 'www.bingimg.cn'
FILE_NAME_MAX_SIZE = 50

URL_GET_IMAGES_PAGE = '{scheme}://{host}/list{page}'


class BingImagDownloader:

    def __init__(self, host=None, scheme=None, headers=None):
        self.scheme = scheme or SCHEME
        self.host = host or HOST
        self.headers = headers or self.default_headers

    @property
    def default_headers(self):
        return {
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': self.host,
            'Referer': '{0}://{1}/'.format(self.scheme, self.host),
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }

    def download(self, page, download_dir=None, resolution=None,
                 workers=None, progress=False, timeout=None, use_wget=False):
        """download images found in page

        page : int
            page number
        resolution : string, optional
            the resolution of image to download, by default None
        threads : int, optional
            download threads, if None, save, by default None
        progress : bool, optional
            show progress, by default False
        """
        if use_wget:
            driver = wget_driver.WgetDriver(download_dir=download_dir,
                                            timeout=timeout,
                                            workers=workers,
                                            progress=progress)
        else:
            driver = urllib_driver.Urllib3Driver(headers=self.headers,
                                                 download_dir=download_dir,
                                                 timeout=timeout,
                                                 workers=workers,
                                                 progress=progress)

        img_links = self.find_all_links(page, resolution=resolution)
        LOG.info('found %s links in page %s.', len(img_links), page)
        driver.download_urls(img_links)

    def get_page_url(self, page):
        return URL_GET_IMAGES_PAGE.format(scheme=self.scheme,
                                          host=self.host,page=page)

    def find_all_links(self, page, resolution=None):
        httpclient = urllib3.PoolManager(headers=self.headers)
        resp = httpclient.request('GET', self.get_page_url(page))
        if resp.status != 200:
            raise Exception('get web page failed, %s' % resp.data)
        html = bs4.BeautifulSoup(resp.data, features="html.parser")
        img_links = []
        for link in html.find_all(name='a'):
            if link.get('href').endswith('.jpg') and (
               not resolution or resolution in link.get('href')):
                img_links.append(link.get('href'))
        return img_links
