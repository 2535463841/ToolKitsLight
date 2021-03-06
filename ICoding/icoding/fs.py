import contextlib
import fnmatch
import io
import os
import zipfile

from icoding.common import log

LOG = log.getLogger(__name__)


def remove(path, recursive=False):
    """ remove file or dir

    >>> os.makedirs('dir1/dir2/dir3')
    >>> with open('dir1/dir2/dir3/e.txt', 'w') as f:
    ...     f.write('hello, word')
    11
    >>> remove('dir1/dir2/dir3', recursive=True)
    >>> os.makedirs('dir1/dir2/dir3')
    >>> remove('dir1/dir2/dir3', recursive=True)
    """
    if os.path.isfile(path) or not recursive:
        os.remove(path)
    else:
        for p in os.listdir(path):
            remove(os.path.join(path, p), recursive=recursive)
        os.rmdir(path)


def directory_flat(top, set_index=True):
    """Flat a directory
        move files to the top path
    """
    all_files = []
    for root, dirs, files in os.walk(top):
        for f in files:
            all_files.append((root, f))
    index = 0
    index_digit = len(str(len(all_files)))
    file_name_fmt = '{{:0>{}}}_{{}}'.format(index_digit)
    for src_path, file_name in all_files:
        src_file = os.path.join(src_path, file_name)
        if set_index:
            index += 1
            dest_path = os.path.join(top,
                                     file_name_fmt.format(index, file_name))
        else:
            dest_path = os.path.join(top, file_name)
        os.rename(src_file, dest_path)
    # after move files, clean empty directory
    for d in os.listdir(top):
        dir_path = os.path.join(top, d)
        if os.path.isdir(dir_path):
            remove(dir_path, recursive=True)


def zip_fils(path, name=None, zip_root=True):
    """Compress directory use zipfile libriary
    """
    if not os.path.exists(path):
        raise FileExistsError('path %s not exists' % path)

    zip_name = name or (os.path.basename(path) + '.zip')
    zip_path_list = []

    def collect(directory):
        # NOTE(zbw) Add the directory itself, make sure that the directory
        # is still added to the compressed file when it is a file or empty.
        zip_path_list.append(directory)
        if os.path.isfile(directory):
            return
        for root, dirs, files in os.walk(directory):
            for p in files + dirs:
                zip_path_list.append(os.path.join(root, p))

    if zip_root:
        collect(path)
    else:
        children = os.listdir(path)
        os.chdir(path)
        for child in children:
            collect(child)

    with zipfile.ZipFile(zip_name, 'w') as zfile:
        for f in zip_path_list:
            zfile.write(f, f, zipfile.ZIP_DEFLATED)
    return zip_name


def find(path, pattern):
    """Find files on specified path
    """
    matched_pathes = []
    for root, dirs, files in os.walk(path):
        for f in fnmatch.filter(dirs + files, pattern):
            matched_pathes.append((root, f))
    return matched_pathes


def make_file(file_path):
    """Create specified file, make dirs if path is not exists."""
    if os.path.exists(file_path):
        return
    file_dir = os.path.dirname(file_path)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    open(file_path, 'a').close()


class FileBackwardsReader(object):
    NEW_LINES = ['\r\n', '\n', '\r']

    def __init__(self, fp, file_size=None, chunk_size=None):
        self.chunk_size = chunk_size or io.DEFAULT_BUFFER_SIZE
        self.cached_lines = []
        self.fp = fp
        self.file_size = file_size or os.fstat(self.fp.fileno()).st_size
        self.seek = self.file_size
        LOG.debug('readder file with chunk size = %s', self.chunk_size)

    def _update_cached_lines(self):
        while len(self.cached_lines) <= 1:
            data = self._get_next_data()
            if not data:
                break
            lines = io.StringIO(data).readlines()
            self._add_to_cached_lines(lines)

    def _get_next_data(self):
        if self.seek <= 0:
            return ''
        seek = self.seek - self.chunk_size
        self.seek = max(seek, 0)
        self.fp.seek(self.seek)
        data = self.fp.read(self.chunk_size)
        return data

    def _add_to_cached_lines(self, lines):
        if not self.cached_lines:
            self.cached_lines = lines
        elif max(lines[-1].rfind(n) for n in self.NEW_LINES) < 0:
            self.cached_lines[0] = lines[-1] + self.cached_lines[0]
            self.cached_lines = lines[:-1] + self.cached_lines
        else:
            self.cached_lines = lines + self.cached_lines

    def readline(self):
        self._update_cached_lines()
        if not self.cached_lines:
            return ''
        else:
            return self.cached_lines.pop()

    def readlines(self):
        lines = []
        line = self.readline()
        while line:
            lines.append(line)
            line = self.readline()
        return lines

    def __iter__(self):
        return self

    def __next__(self):
        line = self.readline()
        if not line:
            raise StopIteration
        return line

    def close(self):
        self.fp.close()

    @property
    def closed(self):
        return self.fp.closed


@contextlib.contextmanager
def open_backwards(file, chunk_size=None, **kwargs):
    """
    >>> fp = io.StringIO()
    >>> fp.writelines(['aaa\\n', 'bbb\\n', 'ccc\\n'])
    >>> reader = FileBackwardsReader(fp, file_size=len(fp.getvalue()))
    >>> reader.readlines()
    ['ccc\\n', 'bbb\\n', 'aaa\\n']
    >>> file_size = len(fp.getvalue())
    >>> reader = FileBackwardsReader(fp, file_size=file_size, chunk_size=1)
    >>> reader.readlines()
    ['ccc\\n', 'bbb\\n', 'aaa\\n']
    """
    with open(file, mode='r') as fp:
        yield FileBackwardsReader(fp, chunk_size=chunk_size)
