import hashlib
import qrcode
import io
import random

LOWER = 'abcdefghijklmnopqrstuvwxyz'
UPPER = 'abcdefghijklmnopqrstuvwxyz'.upper()
NUMBER = '0123456789'
SPECIAL = '!@#$%^&*,.;:'


def md5sum_file(file_path, read_bytes=None):
    """Calculate the md5 and sha1 values of the file
    Return: md3sum, sha1
    """
    read_bytes or io.DEFAULT_BUFFER_SIZE
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


def random_password(lower=4, upper=4, number=4, special=4):
    kwargs = locals()
    char_map = {'lower': LOWER,
                'upper': UPPER,
                'number': NUMBER,
                'special': SPECIAL}
    password = []
    for char_type, char_num in kwargs.items():
        password += random.sample(char_map[char_type], char_num)
    random.shuffle(password)
    return ''.join(password)
