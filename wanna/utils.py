import sys
import re
import os.path
import threading
import hashlib
import contextlib
import signal


suffixes = {
    'decimal': ('kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'),
    'binary': ('KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'),
}

def humanize(value, binary=True, format='%.1f'):
    """
    Format number of bytes like a human readable filesize (eg. 10 kB).
    Args: 
        value (numeric): number of bytes
        binary (bool): use binary base (1024) or decimal (1000)
        format (string): optional format string

    Returns:
        filesize-like formatted string
    """

    suffix = suffixes['binary'] if binary else suffixes['decimal']

    base = 1024 if binary else 1000
    bytes = float(value)

    if bytes == 1: return '1 Byte'
    elif bytes < base: return '%d Bytes' % bytes

    for i,s in enumerate(suffix):
        unit = base ** (i+2)
        if bytes < unit:
            return (format + ' %s') % ((base * bytes / unit), s)
    
    return (format + ' %s') % ((base * bytes / unit), s)


def fuzzyfinder(input, collection, accessor=lambda x: x):
    """
    Args:
        input (str): A partial string which is typically entered by a user.
        collection (iterable): A collection of strings which will be filtered
             based on the `input`.

    Returns:
        suggestions (generator): A generator object that produces a list of
         suggestions narrowed down from `collection` using the `input`.
    """
    suggestions = []
    input = str(input) if not isinstance(input, str) else input
    pat = '.*?'.join(map(re.escape, input))
    regex = re.compile(pat)
    for item in collection:
        r = regex.search(accessor(item))
        if r:
            suggestions.append((len(r.group()), r.start(), accessor(item), item))

    return (z[-1] for z in sorted(suggestions))


def md5sum(filepath):
    """Calculate md5_sum

    Args:
       filepath (string):  path to the file

    Returns:
       string - digest value as a string of hexadecimal digits
    """
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    return md5.hexdigest()


def touch(fname):
    try:
        os.utime(fname, None)
    except OSError:
        open(fname, 'a').close()


@contextlib.contextmanager
def ignore_ctrl_c():
    original = signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        yield
    finally:
        signal.signal(signal.SIGINT, original)


class ProgressPercentage(object):
    """A simple progress bar"""
    def __init__(self, filename, size=None, humanized=False):
        self._filename = filename
        self._size = size or float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()
        self._humanized = humanized

    def __call__(self, bytes_amount):
        """Call progress

        To simplify we'll assume this is hooked up to a single filename
        """
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (float(self._seen_so_far) / self._size) * 100

            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, 
                    self._seen_so_far if not self._humanized else humanize(self._seen_so_far), 
                    self._size if not self._humanized else humanize(self._size),
                    percentage))
            sys.stdout.flush()
