#!/usr/bin/env python3
"""Selftest: logwait.py (NORTHSTAR_PROCESS_RETRO_1). Temp files and a fake clock, 0 game. Each case can fail: the stale
token, the rotation, the split token and the timeout are the four ways a log wait lies."""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import logwait  # noqa: E402

FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.t += s


def write(p, data, mode="ab"):
    with open(p, mode) as f:
        f.write(data)


def t_all(d):
    p = os.path.join(d, "Player.log")
    write(p, b"[RimBridge] Bridge token: OLD\nend of the last session\n", "wb")

    c = Clock()
    r = logwait.LogCursor(p).wait("Bridge token:", 9, clock=c, sleep=c.sleep)
    ok(not r["ok"] and "within 9 s" in r["why"], "fresh: last session's token does not count, the wait times out")
    ok(c.t >= 9, "the timeout really waited")

    ok(logwait.LogCursor(p, fresh=False).poll("Bridge token:") == "[RimBridge] Bridge token: OLD",
       "fresh=False finds text already there and returns the whole line")

    cur = logwait.LogCursor(p)
    write(p, b"new\r\n[RimBridge] Bridge token: NEW\r\nmore\n")
    ok(cur.poll("Bridge token:") == "[RimBridge] Bridge token: NEW", "new text after the cursor is found, CR stripped")
    ok(cur.poll("Bridge token:") is None, "the same line is not returned twice")

    cur = logwait.LogCursor(p)
    write(p, b"short\n", "wb")                             # Unity rotated: same name, smaller file
    ok(cur.poll("Bridge token:") is None and cur.rotated and cur.pos == 6, "shrinking file reads as a rotation")
    write(p, b"[RimBridge] Bridge token: ROT\n")
    ok(cur.poll("Bridge token:") == "[RimBridge] Bridge token: ROT", "token after a rotation is found")

    cur = logwait.LogCursor(p)
    write(p, b"[RimBridge] Bridge to")
    ok(cur.poll("Bridge token:") is None, "half a token is not a match")
    write(p, b"ken: SPLIT\n")
    ok(cur.poll("Bridge token:") == "[RimBridge] Bridge token: SPLIT", "a token split across two writes is found")

    missing = os.path.join(d, "absent.log")
    c = Clock()
    r = logwait.LogCursor(missing).wait("x", 3, clock=c, sleep=c.sleep)
    ok(not r["ok"], "a missing log is a wait, not a crash")

    c = Clock()
    r = logwait.LogCursor(p).wait("x", 900, clock=c, sleep=c.sleep, abort=lambda: "game exited")
    ok(not r["ok"] and r["why"] == "game exited" and c.t == 0, "abort ends the wait at once with its reason")

    cur = logwait.LogCursor(p)
    write(p, "é token\n".encode("utf-8"))
    ok(cur.poll("é tok") == "é token", "the needle is literal UTF-8")
    ok(logwait.main(["no such text", "--timeout", "0", "--log", p]) == 1, "CLI: exit 1 when the text never comes")
    ok(logwait.main(["é tok", "--existing", "--timeout", "0", "--log", p]) == 0, "CLI: exit 0 on a match")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as d:
        t_all(d)
    print("%d FAIL" % len(FAILS))
    sys.exit(1 if FAILS else 0)
