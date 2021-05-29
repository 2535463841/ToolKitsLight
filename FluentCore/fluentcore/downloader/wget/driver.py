import os

from fluentcore.common import log
from fluentcore.downloader import driver

LOG = log.getLogger(__name__)

DEFAULT_WORKERS = 10


class WgetDriver(driver.DownloadDriver):
    WGET = '/usr/bin/wget'

    def download(self, url):
        cmd = [self.WGET, url, '-P', self.download_dir,
               '--timeout', str(self.timeout)]
        LOG.debug('Run cmd: %s', cmd)
        if not self.progress:
            cmd.append('-q')
        os.system(' '.join(cmd))
