import os
import bs4
from fluentcore.common import log
from fluentcore.downloader.urllib import driver as urllib_driver
from fluentcore.downloader.wget import driver as wget_driver

LOG = log.getLogger(__name__)

SCHEME = 'http'
HOST = 'www.bingimg.cn'
FILE_NAME_MAX_SIZE = 50


class BingImagDownloader:

    def __init__(self, host=None, scheme=None, headers=None,):
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
                 workers=None, process=False, timeout=None, use_wget=False):
        """download images found in page

        page : int
            page number
        resolution : string, optional
            the resolution of image to download, by default None
        threads : int, optional
            download threads, if None, save, by default None
        process : bool, optional
            show process, by default False
        """
        download_driver = urllib_driver.Urllib3Driver(
            download_dir=download_dir,
            headers=self.headers,
            timeout=timeout,
            workers=workers,
            process=process)
        # request page and find all img links
        img_links = self.find_all_links(page, download_driver.http,
                                        resolution=resolution)
        LOG.info('found %s links in page %s.', len(img_links), page)

        if use_wget:
            driver = wget_driver.WgetDriver(workers=workers)
            driver.download_urls(img_links)
        else:
            driver = download_driver
        driver.download_urls(img_links)

    def download_use_wget(self, link):
        LOG.debug('Start to download ... %s', link)
        os.system('wget {0}'.format(link))

    def get_page_url(self, page):
        return '{}://{}/list{}'.format(self.scheme, self.host, page)

    def find_all_links(self, page, httpclient, resolution=None):
        resp = httpclient.request('GET', self.get_page_url(page))
        if resp.status != 200:
            raise Exception('http reqeust failed, %s' % resp.data)
        html = bs4.BeautifulSoup(resp.data, features="html.parser")
        img_links = []
        for link in html.find_all(name='a'):
            if not link.get('href').endswith('.jpg'):
                continue
            if resolution and resolution not in link.get('href'):
                continue
            img_links.append(link.get('href'))
        return img_links
