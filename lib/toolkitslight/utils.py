import hashlib
import qrcode



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
