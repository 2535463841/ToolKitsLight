import socket
import paramiko

from fluentcore.common import cliparser
from fluentcore.common import log
from fluentcore.pysshpass import ssh

from fluentclient import base

LOG = log.getLogger(__name__)

BASE_SSH_ARGUMENTS = base.BASE_ARGUMENTS + [
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


@cliparser.register_cli(base.SUB_CLI_PARSER)
class SSHCmd(cliparser.CliBase):
    NAME = 'ssh-cmd'
    ARGUMENTS = [
        cliparser.Argument('host', help='The host to connect'),
        cliparser.Argument('command', help='The command to execute')
    ] + BASE_SSH_ARGUMENTS

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


@cliparser.register_cli(base.SUB_CLI_PARSER)
class ScpGet(cliparser.CliBase):
    NAME = 'scp-get'
    ARGUMENTS = [
        cliparser.Argument('remote_file', help='The remote file to get.'),
        cliparser.Argument('local_path', help='The local path to save.')
    ] + BASE_SSH_ARGUMENTS

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


@cliparser.register_cli(base.SUB_CLI_PARSER)
class ScpPut(cliparser.CliBase):
    NAME = 'scp-put'
    ARGUMENTS = [
        cliparser.Argument('local_file', help='The local path to put.'),
        cliparser.Argument('remote_path', help='The remote file to save.'),
    ] + BASE_SSH_ARGUMENTS

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
