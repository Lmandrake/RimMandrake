#!/usr/bin/env python3
"""Regression checks for owed.py sync-sources and its Dispatcher hook (RIMMANDRAKE_FILE_OWED_WHERE_RUNS_PARK_FOR_THE_
CONDUCTOR), one per hole Codex's review found on 2026-11-18; the contract itself is acceptance/owed_sources_accept.py.

    python3 src/RimMandrake/rimflow/selftest_owed_sources.py      # exit 0 and "PASS n/n"
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
import owed  # noqa: E402
import dispatcher as D  # noqa: E402

RESULTS = []


def check(ok, what):
    RESULTS.append((bool(ok), what))


class It:
    def __init__(self, open_=True):
        self.open = open_


def keys_round_trip():
    rows = [{"mod": "Example", "version": "0.1.0+build", "stage": "his_walk", "blind": None,
             "next": "NEXT (OWNER, a card in the Conductor log): his words"},
            {"mod": "Other", "version": None, "stage": None, "blind": {"visit": 3},
             "next": "NEXT (PAUSED: three cycles, the Conductor decides): bring the findings"}]
    for key, _, title, _ in owed.maturation_sources(rows):
        got = owed.SOURCE_RX.findall("%s [%s %s]" % (title, owed.SOURCE_TAG, key))
        check(got == [key], "a key reads back whole from its title (%s -> %s)" % (key, got))
    a, b = (owed.maturation_sources([dict(rows[0], version=v)])[0][0] for v in ("0.1.0+build", "0.1.0-build"))
    check(a != b, "two versions never share a key (%s, %s)" % (a, b))
    quoted = [{"mod": "Q", "version": "0.1.0", "stage": "blind_challenge", "blind": None,
               "next": "NEXT (automatic: one steward run): the steward says the Conductor decides later"}]
    check(owed.maturation_sources(quoted) == [], "words quoted after the NEXT tag are not a hand step")


def names_never_run_out():
    known = set()
    recs = [{"unit": "rm-detached-bench-x-%d" % i, "item": "RIMMANDRAKE_FIX_SAME_PREFIX_ITEM_OPEN", "owed_close": "open"}
            for i in range(40)]
    srcs = owed.detached_sources(recs, {"RIMMANDRAKE_FIX_SAME_PREFIX_ITEM_OPEN": It()})
    names = []
    for key, bases, _, _ in srcs:
        n = owed._free_name(bases, known)
        names.append(n)
        if n:
            known.add(n)
    check(len(srcs) == 40 and None not in names and len(set(names)) == 40,
          "40 runs on one item prefix each get their own name (%d named)" % len([n for n in names if n]))


def holds_on_every_path():
    rows = [{"mod": "Graffiti"}, {"mod": "Pyrelands"}]
    recs = [{"item": "RIMMANDRAKE_AUTOBUILD_GRAFFITI_THIRTY_THINGS"}, {"item": "RIMMANDRAKE_JUDGE_PYRELANDS_BLIND"},
            {"item": "RIMMANDRAKE_FIX_GRAFFITIPAINT_OTHER"}]
    r2, c2 = owed.not_held(rows, recs, {"GRAFFITI"})
    check([r["mod"] for r in r2] == ["Pyrelands"], "a held mod's row is dropped, the other kept")
    check([r["item"] for r in c2] == ["RIMMANDRAKE_JUDGE_PYRELANDS_BLIND", "RIMMANDRAKE_FIX_GRAFFITIPAINT_OTHER"],
          "a held mod's run is dropped by its word, a longer word is not that mod")


def unread_records_said():
    tmp = tempfile.mkdtemp(prefix="owed_selftest_")
    det = os.path.join(tmp, "det")
    items = os.path.join(tmp, "items")
    os.makedirs(det)
    os.makedirs(items)
    open(os.path.join(det, "rm-detached-torn.json"), "w").write("{\"unit\": ")
    mj = os.path.join(tmp, "m.json")
    json.dump([{"mod": "Pyrelands", "version": "0.1.0", "stage": "blind_challenge", "blind": {"visit": 3},
                "next": "NEXT (PAUSED: three cycles, the Conductor decides): x"}], open(mj, "w"))
    env = {k: v for k, v in os.environ.items() if not k.startswith("RIMFLOW_")}
    env.update(RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"), RIMFLOW_ITEMS=items, RIMFLOW_SEAT="BENCH",
               RIMFLOW_PROBE="no-reading", PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, os.path.join(HERE, "owed.py"), "sync-sources", "--maturation-json", mj,
                        "--detached-dir", det], cwd=REPO, env=env, capture_output=True, text=True, timeout=300)
    check(r.returncode == 2 and "could not read 1 detached record" in r.stdout and "FILED " in r.stdout,
          "a torn record exits 2 naming it, and the readable source is still filed (rc %d)" % r.returncode)


def one_filing_a_pass():
    tmp = tempfile.mkdtemp(prefix="owed_max_")
    det, items = os.path.join(tmp, "det"), os.path.join(tmp, "items")
    os.makedirs(det)
    os.makedirs(items)
    mj = os.path.join(tmp, "m.json")
    json.dump([{"mod": m, "version": "0.1.0", "stage": "blind_challenge", "blind": {"visit": 3},
                "next": "NEXT (PAUSED: three cycles, the Conductor decides): x"} for m in ("Pyrelands", "FlowWorks")],
              open(mj, "w"))
    env = {k: v for k, v in os.environ.items() if not k.startswith("RIMFLOW_")}
    env.update(RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"), RIMFLOW_ITEMS=items, RIMFLOW_SEAT="BENCH",
               RIMFLOW_PROBE="no-reading", PYTHONDONTWRITEBYTECODE="1")
    argv = [sys.executable, os.path.join(HERE, "owed.py"), "sync-sources", "--maturation-json", mj, "--detached-dir", det,
            "--max-file", "1"]
    outs = [subprocess.run(argv, cwd=REPO, env=env, capture_output=True, text=True, timeout=300) for _ in range(3)]
    filed = [o.stdout.count("FILED ") for o in outs]
    check(filed == [1, 1, 0] and all(o.returncode == 0 for o in outs) and "WAITS " in outs[0].stdout,
          "--max-file 1 files one a pass, says the other waits, exits 0 (filed %s)" % filed)


def dispatcher_gates():
    calls = []
    sch = {"owed_sources_every_s": 300, "ledger_notes": False, "publish": True}

    def run(paused=None, fence=None, last=None):
        st = {"alarms": {}}
        if last is not None:
            st["owed_sources_at"] = last
        calls.clear()
        fx = {"owed_sources": lambda t, d: calls.append(t) or "sync-sources: 0 filed",
              "lock": lambda: open(os.devnull, "w"), "paused": lambda: paused, "publish": lambda n: None}
        root = tempfile.mkdtemp(prefix="owed_disp_")
        try:
            D.execute([], sch, st, root, True, 1000.0, fx=fx, deadline=10 ** 12, fence=fence)
        except D.Fenced:
            return "fenced", st
        return len(calls), st

    n, st = run()
    check(n == 1 and st.get("owed_sources_at") == 1000.0, "an applied tick runs sync-sources once and stamps it")
    check(run(last=900.0)[0] == 0, "within owed_sources_every_s it does not run again")
    check(run(paused="paused")[0] == 0, "a PAUSE skips it")
    check(run(fence=lambda what: False)[0] == "fenced", "a moved metronome generation fences it")
    n, st = run()
    check(n == 1 and calls and calls[0] <= D.OWED_SOURCES_CAP_S, "its child gets at most OWED_SOURCES_CAP_S")


def main():
    keys_round_trip()
    names_never_run_out()
    holds_on_every_path()
    unread_records_said()
    one_filing_a_pass()
    dispatcher_gates()
    passed = sum(ok for ok, _ in RESULTS)
    for ok, what in RESULTS:
        print("%s  %s" % ("ok  " if ok else "FAIL", what))
    print("%s %d/%d" % ("PASS" if passed == len(RESULTS) else "FAIL", passed, len(RESULTS)))
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
