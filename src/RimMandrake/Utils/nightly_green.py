#!/usr/bin/env python3
"""nightly_green.py -- is the nightly selftest sweep GREEN N nights running? (NIGHTLY_SELFTESTS_DRAIN_THIRTEEN_RED_NIGHTS)

    python3 src/RimMandrake/Utils/nightly_green.py [--nights 2] [--log <path>]

Exit 0 iff the N newest finished sweeps in Transient/selftests_nightly.log of the data clone each say RESULT: GREEN with a
whole suite behind them, the newest is under MAX_AGE_H old and each is within MAX_GAP_H of the next (a night that died or
never ran between two greens breaks "running"). Exit 1 otherwise; each night read is printed. A sweep with no RESULT line
(in progress, or dead) is not a night. A known-red entry does not help: this reads the verdict, not the list.
"""
import argparse
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import known_reds  # noqa: E402

MAX_AGE_H = 30      # as known_reds.MAX_NIGHT_AGE_H: the timer fires every 24 h
MAX_GAP_H = 30
MIN_SUITE = 500     # a green over fewer tests than this is a sweep that barely ran (the suite is past 1000)
COUNTS = re.compile(r"^PASS (\d+)/(\d+)\s+FAIL (\d+)/\d+\s+UNMEASURED \d+/\d+\s+CRASH (\d+)/\d+")


def read_nights(text):
    """The log -> finished sweeps, oldest first: {at, t, result, total, fail, crash}."""
    out, cur = [], None
    for ln in text.splitlines():
        m = known_reds.SECTION.match(ln)
        if m:
            cur = {"at": m.group(1), "t": known_reds.epoch(m.group(1)), "result": None, "total": None, "fail": None, "crash": None}
            out.append(cur)
        elif cur is not None:
            m = COUNTS.match(ln)
            if m:
                cur.update(total=int(m.group(2)), fail=int(m.group(3)), crash=int(m.group(4)))
            elif ln.startswith("RESULT:"):
                cur["result"] = ln.split()[1] if len(ln.split()) > 1 else "?"
    return [n for n in out if n["result"]]


def is_green(night):
    return night["result"] == "GREEN" and night["fail"] == 0 and night["crash"] == 0 and (night["total"] or 0) >= MIN_SUITE


def judge(nights, want, now):
    """-> list of reasons it is not yet `want` green nights running; empty means it is."""
    if len(nights) < want:
        return ["only %d finished sweep(s) in the log, want %d" % (len(nights), want)]
    last = nights[-want:]
    why = ["%s is not green (result %s, FAIL %s, CRASH %s, of %s)" % (n["at"], n["result"], n["fail"], n["crash"], n["total"])
           for n in last if not is_green(n)]
    age = (now - last[-1]["t"]) / 3600.0
    if age > MAX_AGE_H:
        why.append("newest sweep is %.0f h old, limit %d h" % (age, MAX_AGE_H))
    why += ["%.0f h between %s and %s, limit %d h: a night is missing" % ((b["t"] - a["t"]) / 3600.0, a["at"], b["at"], MAX_GAP_H)
            for a, b in zip(last, last[1:]) if b["t"] - a["t"] > MAX_GAP_H * 3600]
    return why


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--nights", type=int, default=2)
    ap.add_argument("--log", default=None, help="default: the data clone's Transient/selftests_nightly.log")
    a = ap.parse_args(argv)
    path = Path(a.log) if a.log else known_reds.log_path()
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print("UNMEASURED: cannot read %s: %s" % (path, e))
        return 1
    nights = read_nights(text)
    for n in nights[-a.nights:]:
        print("%s %s FAIL %s CRASH %s of %s" % (n["at"], n["result"], n["fail"], n["crash"], n["total"]))
    why = judge(nights, a.nights, time.time())
    for w in why:
        print("NOT YET:", w)
    if not why:
        print("GREEN %d nights running" % a.nights)
    return 1 if why else 0


if __name__ == "__main__":
    sys.exit(main())
