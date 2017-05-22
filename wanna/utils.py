import sys
import os.path
import threading
import hashlib
import contextlib
import signal


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
    def __init__(self, filename, size=None):
        self._filename = filename
        self._size = size or float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        """Call progress

        To simplify we'll assume this is hooked up to a single filename
        """
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100

            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()
