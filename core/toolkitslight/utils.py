import hashlib
import qrcode
import time
from datetime import datetime


def md5sum_file(file_path, read_bytes=1024):
    """Calculate the md5 and sha1 values of the file
    Return: md3sum, sha1
    """
    sha1 = hashlib.sha1()
    md5sum = hashlib.md5()

    def read_from_fo(fo):
        data = fo.read(read_bytes)
        while data:
            yield data
            data = fo.read(read_bytes)

    with open(file_path, 'rb') as f:
        for data in read_from_fo(f):
            md5sum.update(data)
            sha1.update(data)
    return (md5sum.hexdigest(), sha1.hexdigest())


def create_qrcode(content, output=None):
    """create qrcode
    >>> test_qrcode = create_qrcode('http://www.baidu.com')
    >>> test_qrcode is None
    False
    """
    img = qrcode.make(content)
    if output:
        img.save(output)
    return img
    # qr = qrcode.QRCode(
    #     version=5,
    #     error_correction=qrcode.constants.ERROR_CORRECT_H,
    #     box_size=8,
    #     border=4)


def convert_base(src_number,  src_base: int, target_base: int=10):
    """
    >>> convert_base('10', 10, target_base=2)
    '1010'
    >>> convert_base('10', 10, target_base=8)
    '12'
    >>> convert_base('10', 10, target_base=10)
    '10'
    >>> convert_base('10', 10, target_base=16)
    'a'
    >>> convert_base(11, 10, target_base=16)
    'b'
    """
    supported_base = {
        2: bin,
        8: oct,
        10: str,
        16: hex
    }
    if target_base not in supported_base:
        raise ValueError('supported base: %s' % supported_base.keys())
    if src_base == target_base:
        return src_number
    base_10 = src_number if isinstance(src_number, int) \
        else int(src_number, src_base)
    target_num = supported_base[target_base](base_10)
    if target_num[:2] in ['0b', '0x', '0o']:
        return target_num[2:]
    else:
        return target_num


def format_timestamp(timestamp: float, date_format='%Y-%m-%d %H:%M:%S'):
    """Parse timestamp to string with DATE_FORMAT
    >>> format_timestamp(0)
    '1970-01-01 08:00:00'
    """
    if timestamp is not None:
        return datetime.fromtimestamp(timestamp).strftime(date_format)
    else:
        return None


def format_datetime(datetime_str: str, date_format='%Y-%m-%d %H:%M:%S'):
    """Parse timestamp to string with DATE_FORMAT
    >>> format_datetime('1970-01-01 08:00:00')
    0.0
    """
    if datetime_str is not None:
        return time.mktime(time.strptime(datetime_str, date_format))
    else:
        return None
