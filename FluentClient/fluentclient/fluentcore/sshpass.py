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
                       help='Execute worker, use hosts num if not set'),
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

    def run_cmd_on_host(self, cmd_request):
        try:
            LOG.debug('run cmd on host %s', cmd_request.host)
            output = ssh.run_cmd_on_host(cmd_request)
        except socket.timeout:
            LOG.error('Connect to %s:%s timeout(%s seconds)',
                        cmd_request.host, cmd_request.port, cmd_request.timeout)
            output = 'ERROR: Connect timeout'
        except paramiko.ssh_exception.AuthenticationException:
            LOG.error('Authentication %s with "%s" failed',
                    cmd_request.user, cmd_request.password)
            output = 'ERROR: Auth failed, password is correct? (-p <PASSWORD>)'
        except Exception as e:
            LOG.error(e)
            output = e
        return {'host': cmd_request.host, 'output': output}

    def run_cmd_on_hosts(self, cmd_requests, worker=None):
        worker = worker or len(cmd_requests)
        LOG.info('run cmd on %s hosts, worker is %s',
                 len(cmd_requests), worker)
        results = []
        pbar = None
        if support_tqdm():
            from tqdm import tqdm
            pbar = tqdm(total=len(cmd_requests))
        with futures.ThreadPoolExecutor(worker) as executor:
            for result in executor.map(self.run_cmd_on_host, cmd_requests):
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
                req = ssh.CmdRequest(args.command, host,
                                     user=user or args.user,
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
        cliparser.Argument('host',
                           help='The remote host to connect, string or file'),
        cliparser.Argument('--remote', help='Remote file path'),
        cliparser.Argument('--local', default='./',
                           help='The local path to save, defualt is ./ .')
    ] + BASE_SSH_ARGUMENTS

    def download_from_host(self, scp_request):
        try:
            LOG.debug('run cmd on host %s', scp_request.host)
            ssh.download_from_host(scp_request)
            output = 'success'
        except socket.timeout:
            LOG.error('Connect to %s:%s timeout(%s seconds)',
                      scp_request.host, scp_request.port, scp_request.timeout)
            output = 'ERROR: connect timeout'
        except paramiko.ssh_exception.AuthenticationException:
            LOG.error('Authentication %s with "%s" failed',
                    scp_request.user, scp_request.password)
            output = 'ERROR: Auth failed, password is correct? (-p <PASSWORD>)'
        except Exception as e:
            LOG.error(e)
            output = e
        return {'host': scp_request.host, 'output': output}

    def download_from_hosts(self, scp_requests, worker=None):
        worker = worker or len(scp_requests)
        LOG.info('download files from %s hosts, worker is %s', 
                 len(scp_requests), worker)
        results = []
        pbar = None
        if support_tqdm():
            from tqdm import tqdm
            pbar = tqdm(total=len(scp_requests))
        with futures.ThreadPoolExecutor(worker) as executor:
            for result in executor.map(self.download_from_host, scp_requests):
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
            for user, host, remote_path, options in \
                parse_connect_info_from_file(args.host):
                remote_path = remote_path or args.remote
                if not remote_path:
                    LOG.error('Remote path must set, error host is %s', host)
                    return
                req = ssh.ScpRequest(os.path.join(args.local, host),
                                     remote_path, host,
                                     user=user or args.user,
                                     password=options.get('password',
                                                          args.password),
                                     port=options.get('port', args.port),
                                     timeout=args.timeout)
                requests.append(req)
        else:
            user, host, remote_path = parse_connect_info(args.host)
            remote_path = remote_path or args.remote
            if not remote_path:
                LOG.error('Remote path must set, error host is %s', host)
                return
            req = ssh.ScpRequest(args.local, remote_path, host, user=user,
                                 password=args.password,
                                 port=args.port, timeout=args.timeout)
            requests.append(req)

        start_time = time.time()
        self.download_from_hosts(requests, worker=args.worker)
        spend = time.time() - start_time
        LOG.info('Spend %.2f seconds total', spend)


@cliparser.register_cli(base.SUB_CLI_PARSER)
class ScpPut(cliparser.CliBase):
    NAME = 'scp-put'
    ARGUMENTS = [
        cliparser.Argument('local', help='The local path to put.'),
        cliparser.Argument('host',
                           help='The remote host to connect, string or file'),
        cliparser.Argument('--remote', default='./',
                           help='The remote path to save.'),
    ] + BASE_SSH_ARGUMENTS

    def upload_to_host(self, scp_request):
        try:
            LOG.debug('run cmd on host %s', scp_request.host)
            ssh.upload_to_host(scp_request)
            output = 'success'
        except socket.timeout:
            LOG.error('Connect to %s:%s timeout(%s seconds)',
                      scp_request.host, scp_request.port, scp_request.timeout)
            output = 'ERROR: connect timeout'
        except paramiko.ssh_exception.AuthenticationException:
            LOG.error('Authentication %s with "%s" failed',
                    scp_request.user, scp_request.password)
            output = 'ERROR: Auth failed, password is correct? (-p <PASSWORD>)'
        except Exception as e:
            LOG.error(e)
            output = e
        return {'host': scp_request.host, 'output': output}

    def upload_to_hosts(self, scp_requests, worker=None):
        worker = worker or len(scp_requests)
        LOG.info('run cmd on %s hosts, worker is %s', 
                 len(scp_requests), worker)
        results = []
        pbar = None
        if support_tqdm():
            from tqdm import tqdm
            pbar = tqdm(total=len(scp_requests))
        with futures.ThreadPoolExecutor(worker) as executor:
            for result in executor.map(self.upload_to_host, scp_requests):
                results.append(result)
                if pbar:
                    pbar.update(1)
        if pbar:
            pbar.close()
        for result in results:
            print('===== {} ====='.format(result.get('host')))
            print(result.get('output'))

    def __call__(self, args):
        if not os.path.exists(args.local):
            LOG.error('Local file %s not found', args.local)
            return
        requests = []
        if os.path.isfile(args.host):
            for user, host, remote_path, options in \
                parse_connect_info_from_file(args.host):
                remote_path = remote_path or args.remote
                if not remote_path:
                    LOG.error('Remote path must set, error host is %s', host)
                    return
                req = ssh.ScpRequest(args.local, remote_path, host,
                                     user=user or args.user,
                                     password=options.get('password',
                                                          args.password),
                                     port=options.get('port', args.port),
                                     timeout=args.timeout)
                requests.append(req)
        else:
            user, host, remote_path = parse_connect_info(args.host)
            remote_path = remote_path or args.remote
            if not remote_path:
                LOG.error('Remote path must set, error host is %s', host)
                return
            req = ssh.ScpRequest(args.local, remote_path, host, user=user,
                                 password=args.password,
                                 port=args.port, timeout=args.timeout)
            requests.append(req)

        start_time = time.time()
        self.upload_to_hosts(requests, worker=args.worker)
        spend = time.time() - start_time
        LOG.info('Spend %.2f seconds total', spend)
