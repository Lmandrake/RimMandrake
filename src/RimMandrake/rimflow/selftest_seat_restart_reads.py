#!/usr/bin/env python3
"""Offline selftest of seat_restart.py's reads: one test per promise on design/specs/2026-11-19-seat-restart-reads/
boundary.md, each named after it (boundary_check.py reads that).

    python3 src/RimMandrake/rimflow/selftest_seat_restart_reads.py                 every test; exit 0 PASS, 1 FAILED
    python3 src/RimMandrake/rimflow/selftest_seat_restart_reads.py --only t_x ...  those alone
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import seat_restart as SR  # noqa: E402

TMP = tempfile.mkdtemp(prefix="selftest_seat_restart_reads_")
FAILS = []


def check(ok, what, got=None):
    print("%s %s%s" % ("ok  " if ok else "FAIL", what, "" if ok or got is None else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(what)


def write(rel, text):
    p = os.path.join(TMP, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def t_unreadable_transcript_is_no_reading():
    """A transcript path that cannot be read (absent, or a directory) is None from every transcript reader; a read
    transcript with no human input is an answer of its own."""
    for blind, what in ((os.path.join(TMP, "absent.jsonl"), "an absent transcript"), (TMP, "a directory")):
        got = (SR.tx_summary(blind), SR.cursor_scan(blind, 0, peers=()), SR.unanswered(blind, 0, peers=()),
               SR.human_since_offset(blind, 0, peers=()), SR.last_human(blind, peers=()))
        check(got == (None,) * 5, "%s reads None from all five readers" % what, got)
    rec = {"type": "assistant", "timestamp": "2026-11-19T00:00:00Z",
           "message": {"role": "assistant", "content": [{"type": "text", "text": "hi"}], "stop_reason": "end_turn"}}
    p = write("quiet.jsonl", json.dumps(rec) + "\n")
    lh = SR.last_human(p, peers=())
    check(isinstance(lh, tuple) and lh[:3] == (None, None, None) and lh[3] == os.path.getsize(p),
          "a read transcript he never typed in is (None, None, None, size), not None", lh)
    check(SR.human_since_offset(p, 0, peers=()) == [], "and holds no human input: [], not None",
          SR.human_since_offset(p, 0, peers=()))


def t_blind_bridge_reading_holds():
    """bridge_hold: an empty or UNMEASURED bridge reading holds the restart with a reason; a measured free bridge does
    not."""
    for br in ({}, {"state": "UNMEASURED", "holders": [], "why": "planted"}):
        h = SR.bridge_hold("BENCH", br, 1)
        check(isinstance(h, str) and "unreadable" in h, "a blind reading %r holds" % (br,), h)
    free = SR.bridge_hold("BENCH", {"state": "MEASURED", "holders": [], "bridge": []}, 1)
    check(free is None, "a measured free bridge holds nothing", free)


def t_unreadable_shard_is_no_reading():
    """work_since: no shard is [] (no work); a shard that cannot be read, or holds a line that is not JSON, is None."""
    clone = os.path.join(TMP, "clone")
    os.makedirs(clone, exist_ok=True)
    check(SR.work_since(clone, "BENCH", 0) == [], "no shard yet reads [] (no work)", SR.work_since(clone, "BENCH", 0))
    shard = os.path.join(clone, "infrastructure", "state", "ledger", "events", "BENCH.jsonl")
    os.makedirs(shard)                       # a directory where the shard should be: it cannot be read
    check(SR.work_since(clone, "BENCH", 0) is None, "an unreadable shard reads None", SR.work_since(clone, "BENCH", 0))
    os.rmdir(shard)
    write(os.path.relpath(shard, TMP), '{"seat": "BENCH", "event": "claim", "ts": "2026-11-19T00:00:00Z"}\nnot json\n')
    check(SR.work_since(clone, "BENCH", 0) is None, "a shard with a bad line reads None",
          SR.work_since(clone, "BENCH", 0))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    only = set(argv[argv.index("--only") + 1:]) if "--only" in argv else None
    for t in (t_unreadable_transcript_is_no_reading, t_blind_bridge_reading_holds, t_unreadable_shard_is_no_reading):
        if only is not None and t.__name__ not in only:
            continue
        print("== %s" % t.__name__)
        try:
            t()
        except Exception as e:      # noqa: BLE001
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    shutil.rmtree(TMP, ignore_errors=True)
    if FAILS:
        print("FAILED %d: %s" % (len(FAILS), "; ".join(FAILS[:8])))
        return 1
    print("PASS selftest_seat_restart_reads")
    return 0


if __name__ == "__main__":
    sys.exit(main())
