import sys
import logging
import socket
import paramiko


from fluentcore.common import cliparser
from fluentcore.common import log
from fluentcore import code
from fluentcore.pysshpass import ssh


LOG = log.getLogger(__name__)

SUB_CLI_PARSER = cliparser.get_sub_cli_parser('fluent utils sub commands')


@cliparser.register_cli(SUB_CLI_PARSER)
class QrcodeCli(cliparser.CliBase):
    DEFAULT_BORDER = 4
    NAME = 'qrcode'
    ARGUMENTS = [
        cliparser.Argument('string', help='the string to create qrcode'),
        cliparser.Argument('-b', '--border', type=int,
                           help='the border of qrcode'),
    ]

    def __call__(self, args):
        border = self.DEFAULT_BORDER if args.border is None else args.border
        qr = code.QRCodeExtend(border=border)
        qr.add_data(args.string)
        for line in qr.parse_string_lines():
            print(line)


base_arguments = [
    cliparser.Argument('-d', '--debug',
                       action='store_true', help='show debug messages'),
    cliparser.Argument('-T', '--get_pty',
                       action='store_true', help='if set, use pty'),
    cliparser.Argument('-t', '--timeout', type=int,
                       help='Timeout of ssh, default is {}'.format(
                           ssh.DEFAULT_TIMEOUT)),
    cliparser.Argument('-P', '--port', type=int,
                       help='The port of ssh server, default is {}'.format(
                           ssh.DEFAULT_PORT)),
    cliparser.Argument('-u', '--user',
                       help='The user for login, default is current user'),
    cliparser.Argument('-p', '--password', default='',
                       help='The password for login, default is ""'),
]


def get_connect_info(connect_info):
    import getpass
    user_host_info = connect_info.split('@')

    if len(user_host_info) < 2:
        user, host_path = getpass.getuser(), user_host_info[0].split(':')
    else:
        user, host_path = user_host_info[0], user_host_info[1].split(':')
    host = host_path[0]
    remote_path = './' if len(host_path) < 2 else host_path[1]
    LOG.debug('user=%s, host=%s, remote_path=%s', user, host, remote_path)
    return user, host, remote_path


@cliparser.register_cli(SUB_CLI_PARSER)
class SSHCmd(cliparser.CliBase):
    NAME = 'ssh-cmd'
    ARGUMENTS = [
        cliparser.Argument('host', help='The host to connect'),
        cliparser.Argument('command', help='The command to execute')
    ] + base_arguments

    def __call__(self, args):
        try:
            user, host, _ = get_connect_info(args.host)
            ssh_client = ssh.SSHClient(host, user, args.password,
                                       port=args.port,
                                       timeout=args.timeout)
            output = ssh_client.ssh(args.command)
            print(output)
        except socket.timeout:
            LOG.error('Connect to %s:%s timeout(%s seconds)',
                      args.host, args.port, args.timeout)
        except paramiko.ssh_exception.AuthenticationException:
            LOG.error('Authentication %s with "%s" failed',
                      user, args.password)
        except Exception as e:
            LOG.error(e)


@cliparser.register_cli(SUB_CLI_PARSER)
class ScpGet(cliparser.CliBase):
    NAME = 'scp-get'
    ARGUMENTS = [
        cliparser.Argument('remote_file', help='The remote file to get.'),
        cliparser.Argument('local_path', help='The local path to save.')
    ] + base_arguments

    def __call__(self, args):
        try:
            if ':' not in args.remote_file:
                raise Exception('remote file must be set')
            user, host, remote_path = get_connect_info(args.remote_file)
            print(user, host, remote_path)
            if not remote_path:
                raise Exception('remote path is none')
            ssh_client = ssh.SSHClient(host, user, args.password,
                                       port=args.port,
                                       timeout=args.timeout)
            ssh_client.get(remote_path, args.local_path)
        except socket.timeout:
            LOG.error('Connect to %s:%s timeout(%s seconds)',
                      args.host, args.port, args.timeout)
        except paramiko.ssh_exception.AuthenticationException:
            LOG.error('Authentication %s with "%s" failed',
                      user, args.password)
        except Exception as e:
            LOG.error(e)


@cliparser.register_cli(SUB_CLI_PARSER)
class ScpPut(cliparser.CliBase):
    NAME = 'scp-put'
    ARGUMENTS = [
        cliparser.Argument('local_file', help='The local path to put.'),
        cliparser.Argument('remote_path', help='The remote file to save.'),
    ] + base_arguments

    def __call__(self, args):
        try:
            user, host, remote_path = get_connect_info(args.remote_path)
            ssh_client = ssh.SSHClient(host, user, args.password,
                                       port=args.port,
                                       timeout=args.timeout)
            ssh_client.put(args.local_file, remote_path)
        except socket.timeout:
            LOG.error('Connect to %s:%s timeout(%s seconds)',
                      args.host, args.port, args.timeout)
        except paramiko.ssh_exception.AuthenticationException:
            LOG.error('Authentication %s with "%s" failed',
                      user, args.password)
        except Exception as e:
            LOG.error(e)


def main():

    # stream_handler = logging.StreamHandler()
    # stream_handler.setLevel(logging.DEBUG)
    # stream_handler.setFormatter(
    #     logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    # )
    # LOG.addHandler(stream_handler)
    # LOG.setLevel(logging.INFO)

    args = SUB_CLI_PARSER.parse_args()
    if args.debug:
        LOG.setLevel(logging.DEBUG)
        log.set_default(level=logging.DEBUG)
    if not hasattr(args, 'cli'):
        SUB_CLI_PARSER.print_usage()
    else:
        try:
            args.cli()(args)
        except KeyboardInterrupt:
            print("user interrupt")
            return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
