from concurrent import futures

from fluentcore.common import log

LOG = log.getLogger(__name__)

DEFAULT_WORKERS = 10


class DownloadDriver(object):

    def __init__(self, workers=None):
        self.workers = workers or DEFAULT_WORKERS

    def download_urls(self, url_list):
        with futures.ThreadPoolExecutor(self.workers) as executor:
            executor.map(self.download, url_list)

    def download(self, url):
        NotImplemented()
