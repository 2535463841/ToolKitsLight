import os
import re
import socket
import paramiko
import time
from concurrent import futures

from fluentcore.common import cliparser
from fluentcore.common import log
from fluentcore.pysshpass import ssh

from fluentclient import base

LOG = log.getLogger(__name__)

RE_CONNECTION = re.compile(r'((.*)@){0,1}([^:]+)(:(.*)){0,1}')

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


def support_tqdm():
    try:
        import tqdm
        return True
    except ImportError:
        LOG.warning('tqdm is not installed')
    return False


def parse_connect_info(connect_info):
    """
    Param: 
        connection_info: e.g. root@localhost:/tmp
    Return:
        user, host, remote_path: e.g. root, localhost, /tmp
    """
    matched = RE_CONNECTION.match(connect_info)
    # NOTE: Example 'root@localhost:/tmp' will be parsed as
    # ('root@', 'root', 'localhost', ':/tmp', '/tmp')
    LOG.debug('regex match user=%s, host=%s, remote_path=%s',
            matched.group(2), matched.group(3), matched.group(5))
    return matched.group(2), matched.group(3), matched.group(5)


def parse_connect_info_from_file(file_path, port=22, password=None):
    with open(file_path) as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        columns = line.split()
        user, host, remote_path = parse_connect_info(columns[0])
        options = {}
        for col in columns[1:]:
            key, value = col.split('=')
            options[key] = value
        yield user, host, remote_path, options


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
        results = []
        pbar = None
        if support_tqdm():
            from tqdm import tqdm
            pbar = tqdm(total=len(remote_cmd_list))
        with futures.ThreadPoolExecutor(worker) as executor:
            for result in executor.map(self.run_cmd_on_host, remote_cmd_list):
                results.append(result)
                if pbar:
                    pbar.update(1)
        if pbar:
            pbar.close()
        for result in results:
            print('===== {} ====='.format(result.get('host')))
            print(result.get('output'))

    def __call__(self, args):
        requests = []
        if os.path.isfile(args.host):
            for user, host, _, options in \
                parse_connect_info_from_file(args.host):
                req = ssh.CmdRequest(args.command, host, user=user,
                                     password=options.get('password',
                                                          args.password),
                                     port=options.get('port', args.port),
                                     timeout=args.timeout)
                requests.append(req)
        else:
            user, host, _ = parse_connect_info(args.host)
            req = ssh.CmdRequest(args.command, host, user=user,
                                 password=args.password,
                                 port=args.port, timeout=args.timeout)
            requests.append(req)

        start_time = time.time()
        self.run_cmd_on_hosts(requests, worker=args.worker)
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
            user, host, remote_path = parse_connect_info(args.remote_file)
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
            user, host, remote_path = parse_connect_info(args.remote_path)
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
