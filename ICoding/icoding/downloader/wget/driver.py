import os

from icoding.common import log
from icoding.downloader import driver

LOG = log.getLogger(__name__)


class WgetDriver(driver.DownloadDriver):
    WGET = '/usr/bin/wget'

    def download(self, url):
        cmd = [self.WGET, url, '-P', self.download_dir,
               '--timeout', str(self.timeout)]
        LOG.debug('Run cmd: %s', cmd)
        if not self.progress:
            cmd.append('-q')
        os.system(' '.join(cmd))
