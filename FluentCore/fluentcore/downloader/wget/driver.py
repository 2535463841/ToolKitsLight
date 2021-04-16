import os
from concurrent import futures

from fluentcore.common import log
from fluentcore.downloader import driver

LOG = log.getLogger(__name__)

DEFAULT_WORKERS = 10


class WgetDriver(driver.DownloadDriver):

    def download(self, url):
        LOG.debug('Start to download ... %s', url)
        os.system('wget {0}'.format(url))
