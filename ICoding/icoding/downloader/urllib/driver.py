import io
import os
import re
import urllib3

import bs4
from icoding.common import log
from icoding.downloader import driver

LOG = log.getLogger(__name__)

FILE_NAME_MAX_SIZE = 50


def find_links(url, link_regex=None, headers=None):
    """
    >>> links = find_links('http://www.baidu.com',
    ...                    link_regex=r'.*.(jpg|png)$')
    """
    httpclient = urllib3.PoolManager(headers=headers)
    resp = httpclient.request('GET', url)
    if resp.status != 200:
        raise Exception('get web page failed, %s' % resp.data)
    html = bs4.BeautifulSoup(resp.data, features="html.parser")
    img_links = []
    if link_regex:
        regex_obj = re.compile(link_regex)
    else:
        regex_obj = None
    for link in html.find_all(name='a'):
        if not link.get('href'):
            continue
        if regex_obj and not regex_obj.match(link.get('href')):
            continue
        img_links.append(link.get('href'))
    return img_links


class Urllib3Driver(driver.DownloadDriver):

    def __init__(self, headers=None, **kwargs):
        super().__init__(**kwargs)
        self.headers = headers
        self.filename_length = 1
        self.http = urllib3.PoolManager(num_pools=self.workers,
                                        headers=self.headers,
                                        timeout=self.timeout)

    def download_urls(self, url_list):
        self.filename_length = 1
        for url in url_list:
            file_name = os.path.basename(url)
            if len(file_name) > self.filename_length:
                self.filename_length = len(file_name)
        self.filename_length = min(self.filename_length, FILE_NAME_MAX_SIZE)
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        super().download_urls(url_list)

    def download(self, url):
        pbar = None
        file_name = os.path.basename(url)
        resp = self.http.request('GET', url, preload_content=False)
        if self.progress:
            try:
                from tqdm import tqdm
                pbar = tqdm(
                    total=int(resp.headers.get('Content-Length')))
                desc_template = '{{:{}}}'.format(self.filename_length)
                pbar.set_description(desc_template.format(file_name))
            except Exception as e:
                LOG.warning('load tqdm failed, %s', e)

        save_path = os.path.join(self.download_dir, file_name)
        with open(save_path, 'wb') as f:
            for data in resp.stream(io.DEFAULT_BUFFER_SIZE):
                f.write(data)
                if pbar:
                    pbar.update(len(data))

        if pbar:
            pbar.close()
        return file_name
