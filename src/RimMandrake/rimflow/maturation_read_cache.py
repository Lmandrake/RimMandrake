"""Shared file reads for the maturation tick and its separately scheduled page."""

from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
import json
import os
import stat
import tempfile

from doorbell import state_dir  # noqa: F401  also read by the phone image manifest


_current = ContextVar("maturation_read_cache", default=None)
MAX_ENTRIES = 16384


def fingerprint(s):
    return [s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def save(path, data):
    """An optional cache can go cold if it cannot be written. Readers see a whole file."""
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=os.path.dirname(path),
                                         prefix=".maturation-cache-", delete=False) as f:
            tmp = f.name
            json.dump(data, f, separators=(",", ":"))
        os.replace(tmp, path)
        tmp = None
    except OSError:
        pass
    finally:
        if tmp is not None:
            try:
                os.unlink(tmp)
            except OSError:
                pass


class FileReads:
    def __init__(self, path):
        self.path = path
        self.entries = load(path)
        self.dirty = False

    def read(self, path, parser, reader):
        key = parser + ":" + os.path.abspath(path)
        try:
            info = os.stat(path)
        except OSError:
            return reader(path)
        if not stat.S_ISREG(info.st_mode):
            return reader(path)
        stamp = fingerprint(info)
        entry = self.entries.get(key)
        if isinstance(entry, list) and len(entry) == 2 and entry[0] == stamp:
            return deepcopy(entry[1])
        value = reader(path)
        try:
            unchanged = stamp == fingerprint(os.stat(path))
        except OSError:
            unchanged = False
        if unchanged:
            self.entries.pop(key, None)
            self.entries[key] = [stamp, deepcopy(value)]
            self.dirty = True
        return value

    def flush(self):
        if self.dirty:
            save(self.path, dict(list(self.entries.items())[-MAX_ENTRIES:]))


@contextmanager
def reading():
    """One cache per tick or page. A nested page read uses the enclosing tick's cache."""
    if _current.get() is not None:
        yield
        return
    cache = FileReads(os.path.join(state_dir(), "maturation-file-reads-v1.json"))
    token = _current.set(cache)
    try:
        yield
    finally:
        _current.reset(token)
        cache.flush()


def read(path, parser, reader):
    cache = _current.get()
    return reader(path) if cache is None or not path else cache.read(path, parser, reader)


def _json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def read_json(path):
    return read(path, "json", _json)
