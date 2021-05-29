from fluentcore import code
from fluentcore.common import cliparser
from fluentcore.common import log

from fluentclient import base

LOG = log.getLogger(__name__)

DEFAULT_BORDER = 0


@cliparser.register_cli(base.SUB_CLI_PARSER)
class QrcodeParse(cliparser.CliBase):
    NAME = 'qrcode-parse'
    ARGUMENTS = base.BASE_ARGUMENTS + [
        cliparser.Argument('string', help='the string to create qrcode'),
        cliparser.Argument('-b', '--border', type=int, default=DEFAULT_BORDER,
                           help='the border of qrcode, deafult is {}'.format(
                               DEFAULT_BORDER)),
        cliparser.Argument('-o', '--output', default=None,
                           help='the file name to save image'),
    ]

    def __call__(self, args):
        border = args.border
        qr = code.QRCodeExtend(border=border)
        qr.add_data(args.string)
        if args.output:
            qr.save(args.output)
        else:
            for line in qr.parse_string_lines():
                print(line)


@cliparser.register_cli(base.SUB_CLI_PARSER)
class QrcodeDump(cliparser.CliBase):
    NAME = 'qrcode-dump'
    ARGUMENTS = base.BASE_ARGUMENTS + [
        cliparser.Argument('filename', help='the image file of qrcode'),
    ]

    def __call__(self, args):
        text_lines = code.QRCodeExtend.dump(args.filename)
        for line in text_lines:
            print(line)
