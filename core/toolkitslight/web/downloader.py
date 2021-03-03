import io
import os
import logging
import urllib3
from collections import namedtuple
from concurrent import futures

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

LOG = logging.getLogger(__name__)

DownloadItem = namedtuple('DownloadItem', 'url name resp')


class HttpDownloader:

    def __init__(self, download_dir=None, headers=None, timeout=60,
                 workers=None, process=False):
        self.headers = headers or DEFAULT_HEADERS
        self.workers = workers or DEFAULT_WORKERS
        self.http = urllib3.PoolManager(num_pools=self.workers,
                                        headers=self.headers,
                                        timeout=timeout)
        self.download_dir = download_dir or os.path.join('.', 'tmp')
        self.process = process
        self.filename_max = 0

    def download(self, url_list):
        """download all files on the list of url
        """
        resp_list = []
        self.filename_max = 0
        for url in url_list:
            LOG.debug('download %s', url)
            file_name = os.path.basename(url)
            resp = self.http.request('GET', url, preload_content=False)
            resp_list.append(DownloadItem(url=url, name=file_name, resp=resp))
            if len(file_name) > self.filename_max:
                self.filename_max = len(file_name)
        self.filename_max = min(self.filename_max, FILE_NAME_MAX_SIZE)

        LOG.debug('the max length of file name is %s', self.filename_max)
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        with futures.ThreadPoolExecutor(self.workers) as executor:
            results = executor.map(self.save_data, resp_list)
        for result in results:
            LOG.debug('complited %s', result)

    def save_data(self, item: DownloadItem):
        pbar = None
        callback = None
        file_name = item.name
        if self.process:
            try:
                from tqdm import tqdm
                pbar = tqdm(
                    total=int(item.resp.headers.get('Content-Length'))
                )
                desc_template = '{{:{}}}'.format(self.filename_max)
                pbar.set_description(desc_template.format(file_name))
                callback = lambda d: pbar.update(len(d))
            except Exception as e:
                LOG.warning('load tqdm failed, %s', e)
        self._save_resp_data(item, callabck=callback)
        if pbar:
            pbar.close()
        return file_name

    def _save_resp_data(self, resp_file, callabck=None):
        save_path = os.path.join(self.download_dir, resp_file.name)
        with open(save_path, 'wb') as f:
            for data in resp_file.resp.stream(io.DEFAULT_BUFFER_SIZE):
                f.write(data)
                if callabck: 
                    callabck(data)
