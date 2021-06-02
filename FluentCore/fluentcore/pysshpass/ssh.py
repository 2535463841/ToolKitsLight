#! /usr/bin/python
from __future__ import print_function
import os
import logging
import paramiko

LOG = logging.getLogger(__name__)

DEFAULT_PORT = 22
DEFAULT_TIMEOUT = 60


class SSHOutput(object):

    def __init__(self, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        return self.stderr.decode('utf-8') if self.stderr \
            else self.stdout.decode('utf-8')


class RemoteCmd(object):
    
    def __init__(self, cmd, host, user, port=22, password=None, timeout=60):
        self.cmd = cmd
        self.host = host
        self.user = user
        self.port = port
        self.password = password
        self.timeout = timeout


class SSHClient(object):

    def __init__(self, host, user, password, port=None, timeout=None):
        self.host = host
        self.user = user
        self.password = password
        self.port = port or DEFAULT_PORT
        self.timeout = timeout or DEFAULT_TIMEOUT
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())

    def _connect(self):
        self.client.connect(hostname=self.host,
                            port=self.port,
                            username=self.user,
                            password=self.password,
                            timeout=self.timeout)

    def ssh(self, command, get_pty=False):
        self._connect()
        LOG.debug('execute: %s', command)
        result = self.client.exec_command(command, get_pty=get_pty)
        output = SSHOutput(result[1].read().strip(), result[2].read().strip())
        self.client.close()
        return output

    def get(self, remote_file, local_path='./'):
        if os.path.isdir(local_path):
            save_path = os.path.join(local_path,
                                     os.path.basename(remote_file))
        else:
            save_path = local_path
        LOG.info('get %s -> %s', remote_file, save_path)
        try:
            self._connect()
            sftp = self.client.open_sftp()
            with open(os.path.join(local_path, save_path), 'wb') as f:
                sftp.getfo(remote_file, f)
            sftp.close()
        except IOError as e:
            LOG.error(e)

    def put(self, local_file, remote_path='~/'):
        if not os.path.exists(local_file):
            LOG.error('local %s not exists', local_file)
            return
        self._connect()
        sftp = self.client.open_sftp()
        try:
            sftp.listdir(remote_path)
            save_path = '/'.join([remote_path, os.path.basename(local_file)])
        except IOError:
            save_path = remote_path
        LOG.info('put %s -> %s', local_file, save_path)
        sftp.put(local_file, save_path)
        sftp.close()


def run_cmd_on_host(remote_cmd):
    ssh_client = SSHClient(remote_cmd.host, remote_cmd.user,
                            remote_cmd.password,
                            port=remote_cmd.port,
                            timeout=remote_cmd.timeout)
    return ssh_client.ssh(remote_cmd.cmd)

