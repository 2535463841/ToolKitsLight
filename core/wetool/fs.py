import os


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
