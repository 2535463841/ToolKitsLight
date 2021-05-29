import platform
import psutil
import collections


cpu_count = collections.namedtuple('cpu_count', 'phy_core v_core')


class os:

    @staticmethod
    def is_linux():
        platform_name = os.uname()[0]
        return 'linux' in platform_name.lower()

    @staticmethod
    def is_windows():
        platform_name = os.uname()[0]
        return 'windows' in platform_name.lower()

    @staticmethod
    def uname():
        return platform.uname()

    @staticmethod
    def release():
        return platform.release()


class cpu:

    @staticmethod
    def count():
        return cpu_count(psutil.cpu_count(logical=False),
                         psutil.cpu_count(logical=True))

    @staticmethod
    def freq():
        return psutil.cpu_freq()


class memory:

    @staticmethod
    def virtual():
        return psutil.virtual_memory()

    @staticmethod
    def swap():
        return psutil.swap_memory()


class disk:

    @staticmethod
    def partitions():
        return psutil.disk_partitions()

    @staticmethod
    def io_counters():
        return psutil.disk_io_counters()

    def usage(path):
        return psutil.disk_usage(path)


class net:

    def if_addrs():
        return psutil.net_if_addrs()

    def if_stats():
        return psutil.net_if_stats()()

    def io_counters(pernic=False):
        return psutil.net_io_counters(pernic=pernic)
