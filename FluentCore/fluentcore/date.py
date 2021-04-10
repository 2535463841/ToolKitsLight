import time
import pytz
from datetime import datetime

FORMAT_YYYY_MM_DD_HHMMSS = '%Y-%m-%d %H:%M:%S'
FORMAT_YYYY_MM_DD_HHMMSS_Z = '%Y-%m-%d %H:%M:%S %Z'


def parse_timestamp2str(timestamp: float, date_format=None):
    """Parse timestamp to string with DATE_FORMAT
    >>> parse_timestamp2str(0.0)
    '1970-01-01 08:00:00'
    """
    dt = datetime.fromtimestamp(timestamp)
    if not date_format:
        return dt.isoformat()
    else:
        return dt.strftime(date_format)


def parse_str2timestamp(datetime_str, date_format=None):
    """Parse timestamp to string with DATE_FORMAT
    >>> parse_str2timestamp('1970-01-01 08:00:00')
    0.0
    """
    if not datetime_str:
        datetime_str = FORMAT_YYYY_MM_DD_HHMMSS
    return time.mktime(time.strptime(datetime_str, date_format))


parse_ts2str = parse_timestamp2str
parse_str2ts = parse_str2timestamp


def now(tz:str=None) -> datetime:
    timezone = pytz.timezone(tz) if tz else None
    return datetime.now(tz=timezone)

def now_str(tz:str=None, date_format=None):
    now = now(tz=tz)
    if not date_format:
        return now.isoformat()
    else:
        return now.strftime(date_format)

def utc_now() -> datetime:
    return datetime.utcnow(tz='utc')

def utc_now_str(date_format=None) -> float:
    return now_str(tz='utc', date_format=date_format)
