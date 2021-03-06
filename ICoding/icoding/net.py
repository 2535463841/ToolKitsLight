from collections import namedtuple
from concurrent import futures
import socket

from fluentlib import executor
from fluentlib import system

ScanResult = namedtuple('ScanResult', 'host port connectable')


def port_scan(host, port_start=0, port_end=65535, threads=1, callback=None):
    """scan host ports between [port_start, port_end]

    >>> port_scan('localhost',
    ...           port_start=8001,
    ...           port_end=8002,
    ...           threads=3,
    ...           callback=lambda future : print(future.done()))
    True
    True
    """
    def _connect(port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.connect((host, port))
            return ScanResult(host, port, True)
        except Exception:
            return ScanResult(host, port, False)
        finally:
            server.close()

    with futures.ThreadPoolExecutor(threads) as executor:
        for port in range(port_start, port_end + 1):
            if callback:
                executor.submit(_connect, port).add_done_callback(callback)
            else:
                executor.submit(_connect, port)


def ping(host):
    if system.OS.is_linux():
        result = executor.LinuxExecutor.execute(['ping', '-w', '3', host])
    else:
        result = executor.LinuxExecutor.execute(['ping', '-n', '3', host])
    return result.status == 0


def get_internal_ip():
    """Get the internal network IP address
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    return s.getsockname()[0]
