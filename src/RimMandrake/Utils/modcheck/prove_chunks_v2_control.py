#!/usr/bin/env python3
"""prove_chunks_v2_control -- can the list CHUNKS_FIX_SAVE_ERRORS_NOT_DEAD_NAMES's A1 runs on see the fault at all?

A1 (save_uncompress.py live RM_TestSite_calm_v3) passes on any list where the fault cannot occur: a list without
Elshender.stackablechunks keeps chunks compressible, and one without Armoury leaves uranium its own hash. So the unrepaired
fixture must read RED on the same list, or A1's green says nothing.

    prove_chunks_v2_control.py offline --red <log> --clean <log>   the record: v2 on a list holding both mods, v2 on one without
    prove_chunks_v2_control.py live RM_TestSite_calm_v2 --lost ChunkMarble=589,...   A2: v2 loaded on A1's list, now

Exit 0 the control holds (the fault shows where the mods are, and does not where they are not), 1 it does not,
2 UNMEASURED. The live verdict is the MAP: Verse.Log's cap can blind the log half on a long session (load 3 of v2 in
session ee0fbaa8 logged no bad line and still lost its chunks), so the log count is reported, never required.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_uncompress as U  # noqa: E402

V2 = "RM_TestSite_calm_v2"
# what makes the chunks non-compressible, and what holds the def that takes MineableUranium's hash
FAULT_MODS = ("elshender.stackablechunks", "mandrake.rsw.armoury")
# one load of v2 on the full list: 1704 chunks + 34 uranium cells dropped (the item's own counts, 3408 lines = 2 x 1704)
RED_LINES_AT_LEAST = 1738
ANY_LOAD = re.compile(r"Loading game from file \S+ with mods:")


def load_slice(log_text, save, which):
    """-> the log from `save`'s first or last load line up to the next load of anything, or None when it never loaded."""
    line = U.LOAD_LINE % save
    at = log_text.find(line) if which == "first" else log_text.rfind(line)
    if at < 0:
        return None
    nxt = ANY_LOAD.search(log_text, at + len(line))
    return log_text[at:nxt.start()] if nxt else log_text[at:]


def mods_of(block):
    """-> the lower-case packageIds Player.log lists under a load line ("  - pkg" rows right after it)."""
    out = set()
    for row in block.splitlines()[1:]:
        m = re.match(r"\s+-\s+(\S+)\s*$", row)
        if not m:
            break
        out.add(m.group(1).lower())
    return out


def offline_problems(red_text, clean_text, save=V2):
    """The two records -> problems. Red: the first load on a list holding both mods logs the dropped things.
    Clean: a load on a list with neither mod reads clean, which is why such a list proves nothing."""
    bad = []
    red = load_slice(red_text, save, "first")
    clean = load_slice(clean_text, save, "last")
    if red is None or clean is None:
        return ["UNMEASURED: %s has no load line in the %s log" % (save, "red" if red is None else "clean")]
    mods = mods_of(red)
    lost = [m for m in FAULT_MODS if m not in mods]
    if lost:
        bad.append("the red log's list lacks %s" % ", ".join(lost))
    _, hits = U.log_verdict(red, save)
    if hits < RED_LINES_AT_LEAST:
        bad.append("the red log has %d bad lines after the load, at least %d expected" % (hits, RED_LINES_AT_LEAST))
    mods = mods_of(clean)
    if not mods:
        bad.append("the clean log lists no mods under its load line")
    held = [m for m in FAULT_MODS if m in mods]
    if held:
        bad.append("the clean log's list holds %s, so it is no contrast" % ", ".join(held))
    problem, hits = U.log_verdict(clean, save)
    if problem:
        bad.append("the clean log reads: %s" % problem)
    return bad


def control_verdict(rows, lost, running):
    """list_things rows, {def: count the save holds}, running packageIds -> (kind, lines).
    "unmeasured": the running list cannot host the control. "red": every def lost, so the list sees the fault: the
    control holds. "blind": something stayed, so a green A1 here would say nothing."""
    missing = [m for m in FAULT_MODS if m not in running]
    if missing:
        return "unmeasured", ["reload needed: %s not in the running load" % ", ".join(missing)]
    short = U.things_verdict(rows, lost)
    kept = [d for d in sorted(lost) if not any(s.startswith(d + ":") for s in short)]
    if kept:
        return "blind", ["%s stood on the map: this list does not lose them" % ", ".join(kept)]
    return "red", short


def cmd_offline(a):
    texts = []
    for path in (a.red, a.clean):
        if not os.path.isfile(path):
            print("UNMEASURED: the log is not on this machine: %s" % path)
            return 2
        with open(path, encoding="utf-8", errors="replace") as f:
            texts.append(f.read())
    bad = offline_problems(texts[0], texts[1])
    for b in bad:
        print(b if b.startswith("UNMEASURED") else "PROBLEM " + b)
    if bad and bad[0].startswith("UNMEASURED"):
        return 2
    print("FAIL" if bad else "PASS")
    return 1 if bad else 0


def cmd_live(a):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from game_paths import PLAYER_LOG
        import live_def_check
        import rimbridge_client as rc
        with open(PLAYER_LOG, encoding="utf-8", errors="replace") as f:
            log = f.read()
        problem, hits = U.log_verdict(log, a.save)
        if problem and problem.startswith("UNMEASURED"):
            print(problem)
            return 2
        lost = U.parse_expect(a.lost)
        host, port, token = rc.resolve_endpoint(None, None, None, None)
        with rc.RimBridge(host, port, token, timeout=120) as rb:
            running = live_def_check.running_ids(rb.call("jawa/running_mods", {"details": False, "assembly": ""}))
            r = rb.call("jawa/list_things", {"defName": ",".join(sorted(lost)), "limit": 5000})
            # the control's own warnings can fill Verse.Log's cap: a proof riding this game after it must keep its log
            rb.call("jawa/static_call", {"type": "Verse.Log", "method": "Clear"})
    except Exception as e:  # noqa: BLE001  no bridge or no log is no measurement, never a FAIL
        print("UNMEASURED: bridge or log not readable: %s" % str(e)[:160])
        return 2
    rows = r.get("things") if isinstance(r, dict) else None
    if running is None or not isinstance(rows, list) or r.get("isCompleteList") is False:
        print("UNMEASURED: running_mods or list_things gave no complete answer")
        return 2
    kind, lines = control_verdict(rows, lost, running)
    print("%s rows %d, %d bad log lines" % (a.save, len(rows), hits))
    for s in lines:
        print(("" if kind == "unmeasured" else "CONTROL ") + s)
    if kind == "unmeasured":
        return 2
    print("PASS" if kind == "red" else "FAIL")
    return 0 if kind == "red" else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("offline")
    o.add_argument("--red", required=True)
    o.add_argument("--clean", required=True)
    v = sub.add_parser("live")
    v.add_argument("save")
    v.add_argument("--lost", required=True)
    a = ap.parse_args(argv)
    return cmd_offline(a) if a.cmd == "offline" else cmd_live(a)


if __name__ == "__main__":
    sys.exit(main())
