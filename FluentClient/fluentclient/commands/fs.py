import time

from fluentlib.common import cliparser
from fluentlib.common import log
from fluentlib import fs

from fluentclient import base

LOG = log.getLogger(__name__)


@cliparser.register_cli(base.SUB_CLI_PARSER)
class PrintBackwards(cliparser.CliBase):
    NAME = 'print-backwards'
    ARGUMENTS = base.BASE_ARGUMENTS + [
        cliparser.Argument('file', help='file'),
        cliparser.Argument('-c', '--chunk', type=int, default=None,
                           help='The chunk size to read, default is None'),
        cliparser.Argument('-n', '--nums', type=int, default=None,
                           help='Print Last N lines')]

    def __call__(self, args):
        start_time = time.time()
        nums = args.nums
        if nums is not None and nums <= 0:
            LOG.error('The value of --nums NUM must >= 1')
            return
        with fs.open_backwards(args.file, chunk_size=args.chunk) as fp:
            for line in fp:
                print(line, end='')
                if nums is not None:
                    nums -= 1
                    if nums <= 0:
                        break
        LOG.debug('file is closed: %s', fp.closed)
        LOG.debug('Used Time: %.2f seconds', time.time() - start_time)
