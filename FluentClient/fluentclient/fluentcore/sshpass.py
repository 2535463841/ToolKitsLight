import os
import socket
import paramiko
import time
from concurrent import futures

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
    cliparser.Argument('-P', '--port', type=int, default=22,
                       help='The port of SshServer, default is 22. It will be'
                            ' overwrited if set port=<PORT> in file.'),
    cliparser.Argument('-u', '--user',
                       help='The user for login, default is current user'),
    cliparser.Argument('-p', '--password', default='',
                       help='The password for login, default is "". It will be'
                            ' overwrited if set password=<PASSWORD> in file.'),
    cliparser.Argument('-w', '--worker', type=int,
                       help='execute worker, use hosts num if not set'),
]


def get_connect_info(connect_info):
    
    """
    Param: connection_info:
           e.g. root@localhost:/tmp
    Return: user, host, remote_path:
            e.g. root, localhost, /tmp
    """
    import getpass
    user_host_info = connect_info.split('@')

    if len(user_host_info) < 2:
        user, host_path = getpass.getuser(), user_host_info[0].split(':')
    else:
        user, host_path = user_host_info[0], user_host_info[1].split(':')
    host = host_path[0]
    remote_path = './' if len(host_path) < 2 else host_path[1]
    LOG.debug('user=%s, host=%s, remote_path=%s', user, host, remote_path)
    return {'name': host, 'user': user, 'path': remote_path}


def get_connect_info_from_file(file_path, port=22, password=None):
    with open(file_path) as f:
        lines = f.readlines()
    hosts = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        columns = line.split()
        host = get_connect_info(columns[0])
        host.update(port=port, password=password)
        for col in columns[1:]:
            key, value = col.split('=')
            host[key] = int(value) if key == 'port' else value
        hosts.append(host)
    return hosts


@cliparser.register_cli(base.SUB_CLI_PARSER)
class SSHCmd(cliparser.CliBase):
    NAME = 'ssh-cmd'
    ARGUMENTS = [
        cliparser.Argument('host',
                           help='The host to connect, string or file. '
                                'String like: root@host1 , File like: '
                                'root@host1 port=80 password=PASSWORD'),
        cliparser.Argument('command', help='The command to execute')
    ] + BASE_SSH_ARGUMENTS

    def run_cmd_on_host(self, remote_cmd):
        try:
            LOG.debug('run cmd on host %s', remote_cmd.host)
            output = ssh.run_cmd_on_host(remote_cmd)
        except socket.timeout:
            LOG.error('Connect to %s:%s timeout(%s seconds)',
                        remote_cmd.host, remote_cmd.port, remote_cmd.timeout)
            output = 'ERROR: connect timeout'
        except paramiko.ssh_exception.AuthenticationException:
            LOG.error('Authentication %s with "%s" failed',
                    remote_cmd.user, remote_cmd.password)
            output = 'ERROR: auth failed'
        except Exception as e:
            LOG.error(e)
            output = e
        return {'host': remote_cmd.host, 'output': output}

    def run_cmd_on_hosts(self, remote_cmd_list, worker=None):
        worker = worker or len(remote_cmd_list)
        LOG.info('run cmd on %s hosts, worker is %s',
                 len(remote_cmd_list), worker)
        with futures.ThreadPoolExecutor(worker) as executor:
            for result in executor.map(self.run_cmd_on_host, remote_cmd_list):
                print('===== {} ====='.format(result.get('host')))
                print(result.get('output'))

    def __call__(self, args):
        if os.path.isfile(args.host):
            hosts = get_connect_info_from_file(args.host,
                                               port=args.port,
                                               password=args.password)
        else:
            host = get_connect_info(args.host)
            host.update(port=args.port, password=args.password)
            hosts = [host]
        remote_cmd_list = [
            ssh.RemoteCmd(args.command, h['name'], h['user'],
                          port=h.get('port'),
                          password=h.get('password'),
                          timeout=args.timeout
            ) for h in hosts
        ]
        start_time = time.time()
        self.run_cmd_on_hosts(remote_cmd_list, worker=args.worker)
        spend = time.time() - start_time
        LOG.info('Spend %.2f seconds total', spend)


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
