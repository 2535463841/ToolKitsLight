import abc
from concurrent import futures

from fluentcore.common import log

LOG = log.getLogger(__name__)

DEFAULT_WORKERS = 10


class DownloadDriver(object):

    def __init__(self, download_dir=None, timeout=60, workers=None,
                 progress=False):
        self.download_dir = download_dir or './'
        self.workers = workers or DEFAULT_WORKERS
        self.progress = progress
        self.timeout = timeout

    def download_urls(self, url_list, headers=None):
        with futures.ThreadPoolExecutor(self.workers) as executor:
            results = executor.map(self.download_url, url_list)
        
        for result in results:
            LOG.debug('completed %s', result)

    def download_url(self, url):
        LOG.debug('download %s to %s', url, self.download_dir)
        self.download(url)

    @abc.abstractmethod
    def download(self):
        pass

