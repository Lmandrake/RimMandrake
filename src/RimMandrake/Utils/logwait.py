#!/usr/bin/env python3
"""logwait.py -- wait for a LITERAL string in Player.log (NORTHSTAR_PROCESS_RETRO_1).

    python3 src/RimMandrake/Utils/logwait.py "Bridge token:" --timeout 900
    python3 src/RimMandrake/Utils/logwait.py "Bridge token:" --existing     # text already in the log counts

Exit 0 and the matching line, or exit 1 with why. A wait is not a count, so this needs no MEASURE_ALLOW_SCAN override and
never trips .claude/hooks/block_blind_scan.py (a shell `grep` on Player.log does). Literal bytes only, no regex.

By default only text written AFTER the call counts: the previous session's token is still in the log until Unity rotates
it, and a wait that reads the whole file returns at once on that stale line. In code, open the cursor BEFORE launching:

    cur = LogCursor()                 # remembers where the log ends now
    launch()
    cur.wait("Bridge token:", 900)    # {"ok": True, "line": ..., "waited_s": ...} or {"ok": False, "why": ...}

Rotation shows up as the file shrinking below the cursor, or a new inode, and rereads from 0. Keep polling from before the
launch: a new log that outgrew the old offset between two polls on the same inode would go unnoticed.

Selftest: selftest_logwait.py (temp files, fake clock, 0 game).
"""
import argparse
import os
import sys
import time


class LogCursor:
    """A read position in one log. poll() scans only new bytes, so a 15-minute wait on a big log stays cheap."""

    def __init__(self, path=None, fresh=True):
        if path is None:
            from game_paths import PLAYER_LOG as path      # resolves per machine; needs Utils on sys.path
        self.path, self.tail, self.rotated = path, b"", False
        st = self._stat()
        self.ino, self.pos = (st.st_ino, st.st_size if fresh else 0) if st else (None, 0)

    def _stat(self):
        try:
            return os.stat(self.path)
        except OSError:
            return None

    def poll(self, token):
        """The first line holding `token` since the cursor, or None. A missing log is 'not yet', never an error."""
        needle = token.encode("utf-8")
        st = self._stat()
        if st is None:
            return None
        if st.st_size < self.pos or (self.ino is not None and st.st_ino != self.ino):
            self.pos, self.tail, self.rotated = 0, b"", True
        self.ino = st.st_ino
        with open(self.path, "rb") as f:
            f.seek(self.pos)
            new = f.read()
        self.pos += len(new)
        buf = self.tail + new                              # the tail catches a token split across two reads
        at = buf.find(needle)
        if at < 0:
            nl = buf.rfind(b"\n")                          # keep the unfinished line: it may become the match
            self.tail = buf[nl + 1:] if nl >= 0 else buf
            return None
        start = buf.rfind(b"\n", 0, at) + 1
        end = buf.find(b"\n", at)
        self.tail = buf[end + 1:] if end >= 0 else b""
        return buf[start:end if end >= 0 else len(buf)].decode("utf-8", "replace").rstrip("\r")

    def wait(self, token, timeout_s, poll_s=3.0, abort=None, clock=time.time, sleep=time.sleep):
        """{"ok": True, "line", "waited_s"} or {"ok": False, "why", "waited_s"}. `abort()` truthy ends the wait early
        with its value as the reason (a game that died cannot print the token)."""
        t0 = clock()
        while True:
            line = self.poll(token)
            if line is not None:
                return {"ok": True, "line": line, "waited_s": clock() - t0, "rotated": self.rotated}
            why = abort() if abort else None
            if why:
                return {"ok": False, "why": str(why), "waited_s": clock() - t0, "rotated": self.rotated}
            if clock() - t0 >= timeout_s:
                return {"ok": False, "why": "no %r within %d s in %s" % (token, timeout_s, self.path),
                        "waited_s": clock() - t0, "rotated": self.rotated}
            sleep(poll_s)


def literal_log_wait(token, timeout_s=900, fresh=True, path=None, poll_s=3.0, abort=None):
    """One call: wait for `token` written after now (fresh) or anywhere in the log (fresh=False)."""
    return LogCursor(path, fresh).wait(token, timeout_s, poll_s=poll_s, abort=abort)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("token", help="literal text, not a regex")
    ap.add_argument("--timeout", type=float, default=900.0, help="seconds (default 900)")
    ap.add_argument("--existing", action="store_true", help="text already in the log counts")
    ap.add_argument("--log", default=None, help="another log (default: game_paths.PLAYER_LOG)")
    a = ap.parse_args(argv)
    r = literal_log_wait(a.token, a.timeout, fresh=not a.existing, path=a.log)
    print(("%d s: %s" % (r["waited_s"], r["line"])) if r["ok"] else r["why"])
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main())
