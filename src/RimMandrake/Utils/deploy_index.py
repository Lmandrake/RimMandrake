#!/usr/bin/env python3
"""The deploy index: what the deploy check already knows about each file of a game's Mods folder.

Reading file contents on the Windows drive from WSL costs 1.0 to 1.7 s per 300 small files, against
0.007 s on the Linux drive (measured 2026-11-26). The deploy plan used to read every game-side file of
the target mod (compare) and open and parse every game-side XML of every other mod (def guard). This
index keeps, on the LINUX drive, for each game-side file: size, modified time (ns), sha256 and the
def guard's parse. A file whose size and time equal its entry is not opened again.

Derived state: delete it at any time. A missing or unreadable index means every file is read, as
before, and the index is written again. Page: design/specs/2026-11-26-deploy-index/boundary.md.

An entry is written only from bytes that were read from the game file in this run, with the size and
time of that open file. It cannot see an edit that keeps both size and time (`--full-read` can).
"""
import errno
import hashlib
import json
import os
import sqlite3
import sys
import time

DEFAULT_PATH = os.path.join(os.path.expanduser("~"), ".local", "state", "rimmandrake", "deploy_index", "index.sqlite")
_SCHEMA = ("CREATE TABLE IF NOT EXISTS files ("
           "path TEXT PRIMARY KEY, size INTEGER NOT NULL, mtime_ns INTEGER NOT NULL, sha TEXT, parsed TEXT)")


def _read_retry(f, n=1 << 16):
    """One read, waiting out ENOMEM (a /mnt/c read can be refused for seconds; measured 2026-10-31)."""
    for wait in (0.5, 1, 2, 4, 8):
        try:
            return f.read(n)
        except OSError as e:
            if e.errno != errno.ENOMEM:
                raise
            time.sleep(wait)
    return f.read(n)


def hash_open(path):
    """-> (sha256 hex, size, mtime_ns) of the bytes read; the stat is the OPEN file's (fstat)."""
    h = hashlib.sha256()
    with open(path, "rb", buffering=0) as f:
        st = os.fstat(f.fileno())
        while True:
            b = _read_retry(f)
            if not b:
                break
            h.update(b)
    return h.hexdigest(), st.st_size, st.st_mtime_ns


def hash_plain(path):
    """sha256 hex of a repo-side file (Linux drive: no index, always read)."""
    return hash_open(path)[0]


class Index:
    """One index per run. `scope` limits what is loaded (and used) to paths under it; None = all paths."""

    def __init__(self, path=None, scope=None, full_read=False, disabled=False):
        self.path = path or os.environ.get("RM_DEPLOY_INDEX") or DEFAULT_PATH
        self.scope = os.path.abspath(scope) if scope else None
        self.full_read = bool(full_read)
        self.rows = {}              # path -> (size, mtime_ns, sha, parsed json text)
        self.dirty = {}             # path -> row, or None = delete
        self.ok = True              # False: the file could not be used; a run then reads everything
        self.reads = 0
        if disabled:                # a throwaway Mods folder (a selftest's): nothing is read from or written to the file
            self.ok = False
        else:
            self._load()

    # ---- file ---------------------------------------------------------------------------------
    def _connect(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        con = sqlite3.connect(self.path, timeout=60)
        con.execute(_SCHEMA)
        return con

    def _load(self):
        for attempt in (0, 1):
            try:
                con = self._connect()
                try:
                    if self.scope:
                        cur = con.execute("SELECT path,size,mtime_ns,sha,parsed FROM files WHERE path >= ? AND path < ?",
                                          (self.scope + os.sep, self.scope + chr(ord(os.sep) + 1)))
                    else:
                        cur = con.execute("SELECT path,size,mtime_ns,sha,parsed FROM files")
                    self.rows = {r[0]: tuple(r[1:]) for r in cur}
                finally:
                    con.close()
                return
            except sqlite3.DatabaseError as e:
                # not a database / malformed: derived state, make a new one. A lock or a permission error is not.
                if attempt == 0 and ("not a database" in str(e) or "malformed" in str(e)):
                    try:
                        os.remove(self.path)
                        continue
                    except OSError:
                        pass
                self.ok = False
                return
            except OSError:
                self.ok = False
                return
        self.ok = False

    def save(self):
        """Write what this run learned. Never raises: a bad index must not fail the plan."""
        if not self.ok or not self.dirty:
            return
        try:
            con = self._connect()
            try:
                with con:
                    for p, row in self.dirty.items():
                        if row is None:
                            con.execute("DELETE FROM files WHERE path=?", (p,))
                        else:
                            con.execute("INSERT OR REPLACE INTO files (path,size,mtime_ns,sha,parsed) VALUES (?,?,?,?,?)",
                                        (p,) + tuple(row))
            finally:
                con.close()
            self.dirty = {}
        except (sqlite3.Error, OSError) as e:
            print("deploy_index: could not write %s (%s); the next check reads every file again" % (self.path, e),
                  file=sys.stderr)

    # ---- use ----------------------------------------------------------------------------------
    def covers(self, path):
        return self.scope is None or os.path.abspath(path).startswith(self.scope + os.sep)

    def entry(self, path):
        """The row for path, or None. A full read has no entries."""
        return None if self.full_read else self.rows.get(os.path.abspath(path))

    def valid(self, entry, size, mtime_ns):
        """An entry stands for a file only when its size AND its time (ns) equal the file's now."""
        return entry is not None and entry[0] == size and entry[1] == mtime_ns

    def _put(self, path, size, mtime_ns, sha=None, parsed=None):
        path = os.path.abspath(path)
        old = self.rows.get(path)
        if old is not None and old[0] == size and old[1] == mtime_ns:
            sha = sha if sha is not None else old[2]
            parsed = parsed if parsed is not None else old[3]
        row = (size, mtime_ns, sha, parsed)
        self.rows[path] = row
        self.dirty[path] = row

    def sha(self, path, size, mtime_ns):
        """sha256 of a game-side file: from the entry when size and time still match, else read the file
        and record what was read (with the open file's own size and time)."""
        e = self.entry(path)
        if self.valid(e, size, mtime_ns) and e[2]:
            return e[2]
        digest, rsize, rmtime = hash_open(path)
        self.reads += 1
        self._put(path, rsize, rmtime, sha=digest)
        return digest

    def parsed_get(self, path, size, mtime_ns):
        e = self.entry(path)
        if self.valid(e, size, mtime_ns) and e[3] is not None:
            try:
                return json.loads(e[3])
            except ValueError:
                return None
        return None

    def parsed_put(self, path, size, mtime_ns, value):
        self._put(path, size, mtime_ns, parsed=json.dumps(value))

    def drop(self, path):
        path = os.path.abspath(path)
        self.rows.pop(path, None)
        self.dirty[path] = None

    def drop_under(self, root, rels):
        """A deploy wrote or deleted these files: their entries no longer describe them."""
        for r in rels:
            self.drop(os.path.join(root, r))
