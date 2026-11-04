#!/usr/bin/env python3
"""Offline selftest of testq/unmeasured.py (TESTQ_ROWS_MEASURE_THE_UNMEASURED_THIRD).

    python3 src/RimMandrake/Utils/testq/selftest_testq_unmeasured.py

A synthetic testq store in a temp dir: the NEWEST run of each chain is the status (an older UNMEASURED row of a chain
that now passes is gone); a run whose rows for a chain are all NOT_RUN did not run it; each UNMEASURED class is read
(HARNESS, UPSTREAM taking its stopper's class, LOOK, NOT_ON_MAP, PREDICATE_OWED, SITE); an undelivered driver row is
HARNESS and holds its chain out of the verdict share; a never-measured chain fails --check until it is held or
registered; a register entry for a chain that has measured warns, never fails; an empty store fails (the instrument
must see something); a non-DONE job is not read.
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import unmeasured as U  # noqa: E402

FAILS = []


def check(ok, msg):
    print("%-5s %s" % ("ok" if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


def row(chain, name, verdict, detail=""):
    return {"chain": chain, "row": name, "verdict": verdict, "detail": detail}


def job(d, name, finished, rows, outcome="DONE"):
    with open(os.path.join(d, "done", name + ".json"), "w") as fh:
        json.dump({"job": {"mod": "M"}, "result": {"outcome": outcome, "finished": finished, "rows": rows}}, fh)


LOOK = "ExpectationFailed: UNMEASURED: live check owed -- judged by eye"
OWED = "UNMEASURED: owed, no predicate yet: xEnabled"
NOMAP = "UNMEASURED: not on this map: no river"
DRIVER = "UNMEASURED: no proof_x result at the current mod hash: run it"
UP = "an UNMEASURED component ended this chain earlier: x"


def main():
    d = tempfile.mkdtemp(prefix="st_unmeasured_")
    try:
        os.makedirs(os.path.join(d, "done"))
        empty = U.status(U.load(d), {})
        check(U.problems(empty) and "no rows read" in U.problems(empty)[0], "an empty store fails --check")
        job(d, "J1", "2026-11-01T00:00:00Z", [row("a", "a1", "UNMEASURED", LOOK), row("b", "b1", "PASS")])
        job(d, "J2", "2026-11-02T00:00:00Z", [row("a", "a1", "PASS"), row("b", "b1", "NOT_RUN")])
        job(d, "J3", "2026-11-02T01:00:00Z", [
            row("c", "c1", "PASS"), row("c", "c2", "UNMEASURED", LOOK), row("c", "c3", "UNMEASURED", UP),
            row("e", "e1", "UNMEASURED", OWED), row("f", "f1", "UNMEASURED", NOMAP),
            row("g", "g1", "PASS"), row("g", "g2", "UNMEASURED", DRIVER),
            row("h", "h1", "PASS"), row("h", "h2", "UNMEASURED", "UNMEASURED: no legal site on this map"),
            row(None, "z", "NOT_RUN")])
        job(d, "J4", "2026-11-03T00:00:00Z", [row("x", "x1", "UNMEASURED", OWED)], outcome="INVALID")
        st = U.status(U.load(d), {})
        check(st["chains"] == 7, "seven chains have a newest run (b keeps J1: J2's NOT_RUN did not run it): %s"
              % st["chains"])
        check(st["verdicts"].get("UNMEASURED") == 6 and st["rows"] == 11, "the newest a1 is PASS, so its old UNMEASURED is gone: %s"
              % st["verdicts"])
        cls = {(r["chain"], r["row"]): r["class"] for r in st["rows_unmeasured"]}
        check(cls.get(("c", "c2")) == "LOOK" and cls.get(("c", "c3")) == "LOOK",
              "LOOK, and an UPSTREAM row takes its stopper's class: %s" % cls)
        check(cls.get(("e", "e1")) == "PREDICATE_OWED" and cls.get(("f", "f1")) == "NOT_ON_MAP"
              and cls.get(("h", "h2")) == "SITE", "PREDICATE_OWED, NOT_ON_MAP, SITE")
        check(cls.get(("g", "g2")) == "HARNESS" and "M/g" in st["held_chains"],
              "an undelivered driver row is HARNESS and holds its chain")
        check(st["held_rows"] == 2 and st["verdict_rows"] == st["rows"] - 2,
              "a held chain's rows leave the verdict share: %s" % st)
        check(st["verdict_unmeasured"] == 5 and abs(st["verdict_share"] - 5 / 9) < 1e-3,
              "verdict share 5 of 9: %s" % st["verdict_share"])
        check(abs(st["raw_share"] - 6 / 11) < 1e-3, "the raw share is reported beside it: %s" % st["raw_share"])
        check(not any(r["chain"] is None for r in st["rows_unmeasured"]) and not any(r["chain"] == "x" for r in st["rows_unmeasured"]),
              "orphan rows and non-DONE jobs are not read")
        never = {n["chain"]: n for n in st["never_measured"]}
        check(set(never) == {"M/e", "M/f"}, "e and f never measured (g measured a PASS): %s" % sorted(never))
        bad = U.problems(st)
        check(any("M/e" in b for b in bad) and any("raw UNMEASURED share" in b for b in bad),
              "--check fails on an unregistered never-measured chain and a raw share over target: %s" % bad)
        check(any("not accounted for: M/c" in b for b in bad) and any("not accounted for: M/g" in b for b in bad),
              "--check fails on an UNMEASURED chain no register entry owns, HARNESS-held ones included: %s" % bad)
        IDS = {"X", "Y", "Z", "W"}
        owed = {"M/c": {"reason": "look owed", "item": "W"}, "M/g": {"reason": "driver", "item": "W"},
                "M/h": {"reason": "no site", "item": "W"}, "_doc": "x"}
        reg = {"M/e": {"reason": "no predicate", "item": "X"}, "M/f": {"reason": "no river", "item": "Y"},
               "M/a": {"reason": "old", "item": "Z"}, "M/nope": {"reason": "?", "item": "Z"}, "_doc": "x",
               "_unmeasured": owed}
        acc = {a["chain"]: a for a in U.status(U.load(d), reg, target=0.6, ids=IDS)["accounted"]}
        check(set(acc) == {"M/c", "M/e", "M/f", "M/g", "M/h"} and all(a["ok"] for a in acc.values())
              and acc["M/c"]["rows"] == 2, "five UNMEASURED chains, each owned (top level or _unmeasured): %s" % acc)
        bad_item = dict(reg, _unmeasured=dict(owed, **{"M/h": {"reason": "no site", "item": "NOT_FILED"}}))
        check(any("M/h" in b and "NOT_FILED" in b for b in U.problems(U.status(U.load(d), bad_item, target=0.6, ids=IDS))),
              "an entry naming an item the ledger does not hold does not count")
        saved_ledger, U.LEDGER = U.LEDGER, os.path.join(d, "noledger")
        try:
            blind = U.problems(U.status(U.load(d), reg, target=0.6))
        finally:
            U.LEDGER = saved_ledger
        check(any("ledger unreadable" in b for b in blind), "an unreadable ledger accounts for nothing (--check fails)")
        held_d = os.path.join(d, "held")
        os.makedirs(os.path.join(held_d, "done"))
        job(held_d, "H1", "2026-11-02T00:00:00Z", [row("m", "m1", "PASS"), row("m", "m2", "PASS"), row("m", "m3", "PASS"),
                                                   row("g", "g2", "UNMEASURED", DRIVER)])
        hs = U.status(U.load(held_d), {"_unmeasured": {"M/g": {"reason": "driver", "item": "W"}}}, ids=IDS)
        check(hs["verdict_share"] == 0 and abs(hs["raw_share"] - 0.25) < 1e-3
              and any("raw UNMEASURED share" in b for b in U.problems(hs)),
              "the RAW share is the condition: held rows count; a verdict share of 0 does not pass: %s" % U.problems(hs))
        st2 = U.status(U.load(d), reg, target=0.6, ids=IDS)
        check(not U.problems(st2), "registered with a reason and under target: --check passes: %s" % U.problems(st2))
        w = U.warnings(st2)
        check(any("M/a" in x and "STALE" in x for x in w) and any("M/nope" in x for x in w) and len(w) == 2,
              "a stale or unknown entry warns, never fails: %s" % w)
        w2 = U.warnings(U.status(U.load(d), dict(reg, _unmeasured=dict(owed, **{"M/b": {"reason": "r", "item": "W"}})),
                                 target=0.6, ids=IDS))
        check(any("M/b" in x and "STALE" in x for x in w2), "an _unmeasured entry whose chain measures now warns: %s" % w2)
        st3 = U.status(U.load(d), {"M/e": {"reason": "", "item": "X"}, "M/f": reg["M/f"], "_unmeasured": owed},
                       target=0.6, ids=IDS)
        check(any("M/e" in b for b in U.problems(st3)), "an entry with an empty reason does not count")
        rc = U.main(["--qhome", d, "--register", os.path.join(HERE, "owed_register.json"), "--check"])
        check(rc == 1, "main --check exits 1 on this store (share over 15%%): %s" % rc)
        creg = dict(reg, _census_never_measured={"M/a": {}, "M/e": {}, "M/q": {}, "M/?": {"not_a_chain": "plan rows"},
                                                 "_doc": "x"})
        cen = {c["chain"]: c for c in U.status(U.load(d), creg, target=0.6, ids=IDS)["census"]}
        check(set(cen) == {"M/a", "M/e", "M/q", "M/?"}, "one census entry per listed chain, _doc skipped: %s" % sorted(cen))
        check(cen["M/a"]["ok"] and cen["M/a"]["fate"].startswith("measured since")
              and cen["M/e"]["ok"] and cen["M/e"]["fate"].startswith("owed")
              and cen["M/?"]["ok"] and cen["M/?"]["fate"].startswith("not a chain"),
              "census fates: measured since / owed / not a chain: %s" % cen)
        st4 = U.status(U.load(d), creg, target=0.6, ids=IDS)
        check(not cen["M/q"]["ok"] and any("census" in b and "M/q" in b for b in U.problems(st4)),
              "a census chain with no measurement and no reason fails --check: %s" % U.problems(st4))
        snap = os.path.join(d, "snap.jsonl.gz")
        U.freeze(U.load(d), snap)
        a_st = U.status(U.load(d), reg, target=0.6, ids=IDS)
        b_st = U.status(U.load_snapshot(snap), reg, target=0.6, ids=IDS)
        check(a_st == b_st, "a frozen snapshot judges exactly as the live store it froze")
        snap2 = os.path.join(d, "snap2.jsonl.gz")
        U.freeze(U.load(d), snap2)
        with open(snap, "rb") as f1, open(snap2, "rb") as f2:
            check(f1.read() == f2.read(), "freezing an unchanged store is byte-identical")
        empty_q = os.path.join(d, "emptyq")
        os.makedirs(os.path.join(empty_q, "done"))
        check(U.main(["--qhome", empty_q, "--register", os.path.join(HERE, "owed_register.json"), "--freeze",
                      os.path.join(d, "never.gz")]) == 1 and not os.path.exists(os.path.join(d, "never.gz")),
              "--freeze refuses an empty store and writes nothing")
        saved = U.SNAPSHOT
        U.SNAPSHOT = snap
        try:
            rc2 = U.main(["--qhome", empty_q, "--register", os.path.join(HERE, "owed_register.json"), "--check"])
            U.SNAPSHOT = os.path.join(d, "absent.gz")
            rc3 = U.main(["--qhome", empty_q, "--register", os.path.join(HERE, "owed_register.json"), "--check"])
        finally:
            U.SNAPSHOT = saved
        check(rc2 == 1, "an empty live store falls back to the snapshot (this one over target, so exit 1): %s" % rc2)
        check(rc3 == 1, "no live store and no snapshot: --check fails (no rows read): %s" % rc3)
        check(U.main(["--snapshot", snap, "--register", os.path.join(HERE, "owed_register.json"), "--check"]) == 1,
              "--snapshot judges the named file")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    with open(os.path.join(HERE, "owed_register.json"), encoding="utf-8") as fh:
        real = json.load(fh)
    check(all(k.startswith("_") or (v.get("reason") and v.get("item")) for k, v in real.items()),
          "every entry of the real register names a reason and an item")
    um = real.get("_unmeasured") or {}
    check(um and all(k.startswith("_") or (v.get("reason") and v.get("item")) for k, v in um.items()),
          "every _unmeasured entry of the real register names a reason and an item")
    known = U.ledger_ids()
    check(known is not None and all(k.startswith("_") or v.get("item") in known
                                    for k, v in list(um.items()) + list(real.items()) if isinstance(v, dict)),
          "every item the real register names is in the ledger: %s"
          % sorted(v.get("item") for k, v in list(um.items()) + list(real.items())
                   if not k.startswith("_") and isinstance(v, dict) and v.get("item") not in (known or ())))
    cn = real.get("_census_never_measured") or {}
    check(len([k for k in cn if not k.startswith("_")]) == 12,
          "the real register lists the census's 12 never-measured chains: %d" % len([k for k in cn if not k.startswith("_")]))
    if FAILS:
        print("%d FAILED" % len(FAILS))
        return 1
    print("selftest_testq_unmeasured: all ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
