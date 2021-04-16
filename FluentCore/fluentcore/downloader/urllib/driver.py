import io
import os
import urllib3
from collections import namedtuple
from concurrent import futures

from fluentcore.common import log

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

DownloadItem = namedtuple('DownloadItem', 'url name resp')


class Urllib3Driver:

    def __init__(self, download_dir=None, headers=None, timeout=60,
                 workers=None, process=False):
        self.headers = headers or DEFAULT_HEADERS
        self.workers = workers or DEFAULT_WORKERS
        self.http = urllib3.PoolManager(num_pools=self.workers,
                                        headers=self.headers,
                                        timeout=timeout)
        self.download_dir = download_dir or './'
        self.process = process
        self.filename_max = 0

    def download_urls(self, url_list):
        self.filename_max = 0
        for url in url_list:
            file_name = os.path.basename(url)
            if len(file_name) > self.filename_max:
                self.filename_max = len(file_name)
        self.filename_max = min(self.filename_max, FILE_NAME_MAX_SIZE)
        LOG.debug('the max length of file name is %s', self.filename_max)
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        with futures.ThreadPoolExecutor(self.workers) as executor:
            results = executor.map(self.download, url_list)
        for result in results:
            LOG.debug('complited %s', result)

    def download(self, url):
        LOG.debug('download %s', url)
        pbar = None
        file_name = os.path.basename(url)
        resp = self.http.request('GET', url, preload_content=False)
        if self.process:
            try:
                from tqdm import tqdm
                pbar = tqdm(
                    total=int(resp.headers.get('Content-Length')))
                desc_template = '{{:{}}}'.format(self.filename_max)
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
