import os
import logging
from re import I
from bs4.element import ProcessingInstruction
import urllib3
import bs4


LOG = logging.getLogger(__name__)


SCHEME = 'http'
HOST = 'www.bingimg.cn'


class BingImagDownloader:
    RESOLUTION_1080 = '1920x1080'
    RESOLUTION_UHD = 'uhd'

    def __init__(self, host=None, scheme=None) -> None:
        self.scheme =  scheme or SCHEME
        self.host = host or HOST
        self.http = urllib3.PoolManager()

    def get_page_url(self, page):
        return '{}://{}/list{}'.format(self.scheme, self.host, page)

    def find_img_link_on_page(self, page, resolution=None):
        url = self.get_page_url(page)
        resp = self.http.request('GET', url)
        html = bs4.BeautifulSoup(resp.data, features="html.parser")
        a_list = html.find_all(name='a')
        links = [
            a.get('href') for a in a_list if a.get('href').endswith('jpg')
        ]
        if resolution:
            return [link for link in links if resolution in link]
        else:
            return links

    def download(self, page, resolution=None, download_dir=None):
        """
        download_format: 1920x1080, uhd, None
        """
        img_links = self.find_img_link_on_page(page, resolution=resolution)
        # print(img_links)
        resp_list = []
        for link in img_links:
            print('==== %s ====' % link)
            resp = self.download_and_save_img(link)
            resp_list.append((link, './', resp))

        def save_data(args):
            _link = args[0]
            _save_dir = args[1]
            _resp = args[2]
            if _resp.status != 200:
                return
            file_name = os.path.basename(_link)
            save_path = os.path.join(_save_dir or '.', file_name)
            import time
            with open(save_path, 'wb') as f:
                for data in _resp.stream(1024000):
                    print(time.time(), 'receive', len(data))
                    f.write(data)
                    f.flush()
            return True

        from concurrent import futures

        with futures.ThreadPoolExecutor(10) as executor:
            results = executor.map(save_data, resp_list)
        
        # for result in results:
        #     print(result)

    def download_and_save_img(self, link, download_dir=None):
        file_name = os.path.basename(link)
        save_path = os.path.join(download_dir or '.', file_name)
        print('    download %s' % link)
        resp = self.http.request('GET', link, preload_content=False)
        return resp
        print('response status is %s', resp.status)
        if resp.status != 200:
            return
        print('        saving %s' % link)
        with open(save_path, 'wb') as f:
            for data in resp.stream(1024):
                f.write(data)


if __name__ == '__main__':
    downloader = BingImagDownloader()
    print('dowloading')
    downloader.download(1, resolution=BingImagDownloader.RESOLUTION_UHD)
    print('finished')