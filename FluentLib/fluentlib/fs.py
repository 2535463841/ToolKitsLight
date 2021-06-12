import os
import fnmatch
import zipfile


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
