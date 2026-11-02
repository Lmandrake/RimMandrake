#!/usr/bin/env python3
"""block_migrate.py — turn text-only blockers into structured ones, where the text says so plainly
(PLAN_BUILD_BLOCKED_BY_IS_TEXT_ONLY).

    python3 src/RimMandrake/rimflow/block_migrate.py            # dry run: what it would write, and what it skipped
    python3 src/RimMandrake/rimflow/block_migrate.py --apply --seat BENCH

Two sources:
  ledger    an open item blocked with no --on whose reason says "Follows X", "depends on X [and Y]", "precondition
            unmet: X", "blocked on X", "waits/waiting on X" for a filed, OPEN X: re-blocked --on X, reason kept.
  store     a relentless item (its store, items/*/state.json) still in line whose last ending is a blocker class
            (relentless_rules.json blocker_classes): relentless_block.resolve, as a worker's snag now does.
Only items the writing seat owns are written (a block is the owner's verb); the rest are listed for that seat.
Anything vaguer than those phrases is left alone: a wrong predecessor would release an item early.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from rimflow import model, priority          # noqa: E402
import relentless_block                      # noqa: E402

ID = r"[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+"
PHRASE = re.compile(r"(?:\bfollows|\bdepends on|\bprecondition unmet:|\bblocked on|\bwaits on|\bwaiting on)\s+(%s)"
                    r"((?:\s*(?:,|and)\s*%s)*)" % (ID, ID), re.I)


def ledger_ids(reason):
    out = []
    for m in PHRASE.finditer(reason or ""):
        for x in [m.group(1)] + re.findall(ID, m.group(2) or ""):
            if x not in out:
                out.append(x)
    return out


def from_ledger(w):
    rows = []
    for it in sorted(w.items.values(), key=lambda i: i.id):
        if not (it.open and it.blocked) or it.blocked_on:
            continue
        ons = [x for x in ledger_ids(it.blocked_reason) if x != it.id]
        live = [x for x in ons if x in w.items and w.items[x].open]
        if live and len(live) == len(ons):
            rows.append({"id": it.id, "owner": it.owner, "kind": "item", "on": live, "reason": it.blocked_reason,
                         "src": "ledger"})
    return rows


def from_store(w, store_dir, rules):
    rows = []
    def state(x):
        it = w.items.get(x)
        return None if it is None else {"state": it.state}
    for p in sorted(glob.glob(os.path.join(store_dir, "items", "*", "state.json"))):
        try:
            with open(p, encoding="utf-8") as f:
                st = json.load(f)
        except (OSError, ValueError):
            continue
        lf = st.get("last_fail") or {}
        it = w.items.get(st.get("item"))
        if it is None or not it.open or it.blocked or st.get("status") not in ("queued", "held", "candidate", "stopping"):
            continue
        pend = relentless_block.from_snag(lf.get("class"), lf.get("detail"), rules)
        if not pend:
            continue
        kind, ons, reason = relentless_block.resolve(pend, it.id, state)
        rows.append({"id": it.id, "owner": it.owner, "kind": kind, "on": ons, "reason": reason, "src": "store"})
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--seat", default=os.environ.get("RIMFLOW_SEAT") or "BENCH")
    ap.add_argument("--store", default=os.path.join(os.environ.get("RELENTLESS_ROOT") or "/home/mandrake/rm/relentless",
                                                    "store"))
    a = ap.parse_args(argv)
    with open(os.path.join(HERE, "relentless_rules.json"), encoding="utf-8") as f:
        rules = json.load(f)
    w = model.replay(model.read())
    rows = from_ledger(w) + from_store(w, a.store, rules)
    rc = 0
    for r in rows:
        mine = r["owner"] == a.seat
        line = "%-6s %-44s %-8s kind %-8s on %s" % (r["src"], r["id"], r["owner"], r["kind"], ",".join(r["on"]) or "-")
        if not (a.apply and mine):
            print(("SKIP (owner %s) " % r["owner"] if a.apply else "WOULD ") + line)
            continue
        cmd = [sys.executable, os.path.join(HERE, "cli.py"), "block", r["id"], "--kind", r["kind"],
               "--reason", r["reason"][:600], "--why", "block_migrate: text-only blocker made structured"]
        for x in r["on"]:
            cmd += ["--on", x]
        p = subprocess.run(cmd, capture_output=True, text=True, env=dict(os.environ, RIMFLOW_SEAT=a.seat))
        print(("WROTE " if p.returncode == 0 else "FAILED ") + line + ("" if p.returncode == 0 else
                                                                      " :: " + (p.stderr or p.stdout)[-200:]))
        rc = rc or p.returncode
    print("%d row(s)" % len(rows))
    return rc


if __name__ == "__main__":
    sys.exit(main())
