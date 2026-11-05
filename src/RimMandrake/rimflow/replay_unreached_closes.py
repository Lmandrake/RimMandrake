#!/usr/bin/env python3
"""Replay past Relentless closes under the unreached-first rule (CHECKER_WEAK_FIX_UNREACHED_READ_AS_PASS, plan step 1 of
design/RimMandrake/relentless_recovery_plan_2026-11-05.md).

Before the fix, relentless_wall.read_as tested a structured verdict's `unreached` list only under PASS / FAIL /
UNMEASURED: a WEAK tagged GAP:OTHER with unreached evidence narrowed to PASS and closed. This reads every closed item's
last check (state.json `check`: verdict, reasons, defects, unreached - the store keeps it after close) and counts the
closes the old rule passed and the current rule refuses.

  replay_unreached_closes.py [--root STORE_ROOT] [--json]   the count, and each item it names
  replay_unreached_closes.py --selftest                     probe: a planted store proves the instrument sees one

A zero is trusted only beside `seen`, the number of closed checks it could read: zero seen is a blind instrument.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relentless_wall as W     # noqa: E402

DEFAULT_STORE = "/home/mandrake/rm/relentless/store"


def old_read_as(word, reasons, defects=None, unreached=None):
    """The rule as it stood before the fix: unreached tested only for PASS / FAIL / UNMEASURED."""
    if defects is not None or unreached is not None:
        defects, unreached = W.clean_list(defects) or [], W.clean_list(unreached) or []
        if defects:
            return "FAIL"
        if word in ("PASS", "FAIL", W.UNMEASURED) and unreached:
            return W.UNMEASURED
        if word == W.UNMEASURED:
            return W.read_as(word, reasons)[0]
        return W.acted_weak(word, reasons)
    return W.read_as(word, reasons)[0]


def closed(st):
    return bool(st.get("done_at")) or st.get("status") in ("done", "closed")


def replay(root):
    """-> {items, closed, seen, refused: [{item, word, unreached}]}"""
    out = {"root": root, "items": 0, "closed": 0, "seen": 0, "refused": []}
    base = os.path.join(root, "items")
    for item in sorted(os.listdir(base)):
        try:
            with open(os.path.join(base, item, "state.json"), encoding="utf-8") as f:
                st = json.load(f)
        except (OSError, ValueError):
            continue
        out["items"] += 1
        if not closed(st):
            continue
        out["closed"] += 1
        chk = st.get("check") or {}
        word = str(chk.get("verdict") or "").upper()
        if word not in W.WORDS:
            continue
        out["seen"] += 1
        args = (word, chk.get("reasons"), chk.get("defects"), chk.get("unreached"))
        if old_read_as(*args) == "PASS" and W.read_as(*args)[0] != "PASS":
            out["refused"].append({"item": item, "word": word, "unreached": W.clean_list(chk.get("unreached"))})
    return out


def _plant(root, item, check, done=True):
    d = os.path.join(root, "items", item)
    os.makedirs(d)
    st = {"item": item, "status": "done" if done else "candidate", "check": check}
    if done:
        st["done_at"] = 1.0
    with open(os.path.join(d, "state.json"), "w", encoding="utf-8") as f:
        json.dump(st, f)


def selftest():
    root = tempfile.mkdtemp(prefix="rl-replay-")
    try:
        _plant(root, "BAD", {"verdict": "WEAK", "reasons": "GAP:OTHER. my own mutant stays green", "defects": [],
                             "unreached": ["ssh stevedesktop exit 255"]})
        _plant(root, "GOOD", {"verdict": "PASS", "reasons": "ran it", "defects": [], "unreached": []})
        _plant(root, "OLDFMT", {"verdict": "PASS", "reasons": "ran it"})
        _plant(root, "OPEN", {"verdict": "WEAK", "reasons": "GAP:OTHER", "defects": [], "unreached": ["x"]}, done=False)
        got = replay(root)
        fails = []
        if got["seen"] != 3 or got["closed"] != 3:
            fails.append("seen/closed %s/%s, wanted 3/3" % (got["seen"], got["closed"]))
        if [r["item"] for r in got["refused"]] != ["BAD"]:
            fails.append("refused %s, wanted [BAD]" % got["refused"])
        print("selftest: %s" % ("ok" if not fails else "; ".join(fails)))
        return 1 if fails else 0
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--root", default=os.environ.get("RELENTLESS_STORE", DEFAULT_STORE))
    p.add_argument("--json", action="store_true")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args(argv)
    if a.selftest:
        return selftest()
    got = replay(a.root)
    if a.json:
        print(json.dumps(got, indent=1, sort_keys=True))
    else:
        print("items %d, closed %d, closing check readable %d, closes the unreached-first rule refuses %d"
              % (got["items"], got["closed"], got["seen"], len(got["refused"])))
        for r in got["refused"]:
            print("  %s  %s  unreached: %s" % (r["item"], r["word"], "; ".join(r["unreached"])[:200]))
    return 2 if not got["seen"] else 0


if __name__ == "__main__":
    sys.exit(main())
