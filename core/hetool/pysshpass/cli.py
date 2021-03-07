import sys
import socket
import getpass
import argparse
import logging
import paramiko
from collections import namedtuple

from pysshpass import ssh


LOG = ssh.LOG


def get_connect_info(connect_info):
    user_host_info = connect_info.split('@')

    if len(user_host_info) < 2:
        user, host_path = getpass.getuser(), user_host_info[0].split(':')
    else:
        user, host_path = user_host_info[0], user_host_info[1].split(':')
    host = host_path[0]
    remote_path = './' if len(host_path) < 2 else host_path[1]
    LOG.debug('user=%s, host=%s, remote_path=%s', user, host, remote_path)
    return user, host, remote_path


def main():
    """Usage:
    1.ssh
        python -m pysshpass.cli ssh root@<HOST> -p <ROOT_PASSWORD> hostname

    2. download file:
        python -m pysshpass.cli get root@<HOST>:<FILE> ./ -p <ROOT_PASSWORD>

    3. upload file:
        python -m pysshpass.cli put <FILE> root@<HOST>:./ -p <ROOT_PASSWORD>
    """
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    )
    LOG.addHandler(stream_handler)
    LOG.setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(help='sshpass for python')
    Argument = namedtuple('Argument', 'args kwargs')

    base_arguments = [
        Argument(['-d', '--debug'],
                 dict(action='store_true', help='show debug messages')),
        Argument(['-T', '--get_pty'],
                 dict(action='store_true', help='if set, use pty')),
        Argument(['-t', '--timeout'],
                 dict(type=int,
                      help='Timeout of ssh, default is {}'.format(
                          ssh.DEFAULT_TIMEOUT))),
        Argument(['-P', '--port'],
                 dict(type=int,
                      help='The port of ssh server, default is {}'.format(
                          ssh.DEFAULT_PORT)
                      )),
        Argument(['-u', '--user'],
                 dict(help='The user for login, default is current user')),
        Argument(['-p', '--password'],
                 dict(default='',
                      help='The password for login, default is ""')),
    ]

    execute_arguments = base_arguments + [
        Argument(['host'], dict(help='The host to connect')),
        Argument(['command'], dict(help='The command to execute'))
    ]
    get_arguments = base_arguments + [
        Argument(['remote_file'], dict(help='The remote file to get.')),
        Argument(['local_path'], dict(help='The local path to save.'))
    ]

    put_arguments = base_arguments + [
        Argument(['local_file'], dict(help='The local file to put.')),
        Argument(['remote_path'], dict(help='The remote path to save.'))
    ]
    sub_parser_map = {'ssh': execute_arguments,
                      'get': get_arguments,
                      'put': put_arguments,
                      }

    for sub_command, arguments in sub_parser_map.items():
        sub_parser = sub_parsers.add_parser(sub_command)
        sub_parser.set_defaults(func=sub_command)
        for argument in arguments:
            sub_parser.add_argument(*argument.args, **argument.kwargs)

    args = parser.parse_args()
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)

    if args.debug:
        LOG.setLevel(logging.DEBUG)
    LOG.debug('args %s', args)
    try:
        if args.func == 'ssh':
            user, host, _ = get_connect_info(args.host)
            ssh_client = ssh.SSHClient(host, user, args.password,
                                       port=args.port,
                                       timeout=args.timeout)
            output = ssh_client.ssh(args.command)
            print(output)
        elif args.func == 'get':
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
        elif args.func == 'put':
            user, host, remote_path = get_connect_info(args.remote_path)
            ssh_client = ssh.SSHClient(host, user, args.password,
                                       port=args.port,
                                       timeout=args.timeout)
            ssh_client.put(args.local_file, remote_path)
        else:
            raise Exception('unknown function {0}'.format(args.func))
        return 0
    except socket.timeout:
        LOG.error('Connect to %s:%s timeout(%s seconds)',
                  args.host, args.port, args.timeout)
    except paramiko.ssh_exception.AuthenticationException:
        LOG.error('Authentication %s with "%s" failed',
                  user, args.password)
    except Exception as e:
        LOG.error(e)
    return 1


if __name__ == "__main__":
    sys.exit(main())
