"""Folder reads shared by the deploy inventory and the def guard."""

import errno
import os
import time
from contextlib import contextmanager


# Native Windows Python has no directory-fd support.
USE_DIR_FD = os.scandir in os.supports_fd and os.stat in os.supports_dir_fd and hasattr(os, "O_DIRECTORY")


class ListingError(OSError):
    """An incomplete folder listing, with the folder path even for fd errors."""


def _read_folder(path, missing_ok):
    fd = None
    try:
        try:
            if USE_DIR_FD:
                fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
            scan = os.scandir(fd if fd is not None else path)
        except (FileNotFoundError, NotADirectoryError):
            if missing_ok and fd is None:
                return None, []
            raise
        with scan:
            return fd, list(scan)
    except BaseException:
        if fd is not None:
            os.close(fd)
        raise


@contextmanager
def listed_folder(path, *, missing_ok=False):
    """Yield (directory fd or None, entries), keeping the fd open to stat entries.

    Buffer each attempt so a failure partway through cannot leak a partial listing.
    Open the folder again for each retry to start from the beginning.
    """
    for wait in (0.5, 1, 2, 4, 8, None):
        try:
            fd, entries = _read_folder(path, missing_ok)
        except OSError as exc:
            if exc.errno != errno.ENOMEM or wait is None:
                raise ListingError(exc.errno, f"could not list folder: {exc.strerror}", path) from exc
            time.sleep(wait)
        else:
            break
    try:
        yield fd, entries
    finally:
        if fd is not None:
            os.close(fd)


def entry_stat(entry, fd):
    return entry.stat() if fd is None else os.stat(entry.name, dir_fd=fd)
