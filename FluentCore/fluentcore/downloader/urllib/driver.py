import io
import os
import urllib3

from fluentcore.common import log
from fluentcore.downloader import driver

LOG = log.getLogger(__name__)

DEFAULT_WORKERS = 10
FILE_NAME_MAX_SIZE = 50
DEFAULT_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}


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
