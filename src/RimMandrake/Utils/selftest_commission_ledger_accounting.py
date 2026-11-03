#!/usr/bin/env python3
"""selftest_commission_ledger_accounting.py — COMMISSION_LEDGER_CLEANUP_1's per-slug accounting.

    python3 src/RimMandrake/Utils/selftest_commission_ledger_accounting.py

The item's criterion: every one of its 85 owed slugs resolves to built, queued, dropped or
superseded, ruled per slug and not as a bulk claim. The record is
design/Jawa/worldbuilding/review/commission_ledger_85_accounting.json. This test re-measures
that record against the tree, so a row that rots shows up as a failure:

  1. The rows are exactly the 85 slugs listed under the item's "## the 85 owed slugs"
     heading: none missing, none extra, none twice.
  2. Each row's key is a live `ledger:` key in flora_assignment_register.decisions.json.
  3. built: names at least one def or file; every def is a <defName> somewhere under src/,
     and every file exists.
  4. queued: names an item that is still open (not closed, dropped or superseded).
  5. superseded: names an item that exists and was not dropped.
  6. dropped: names a commit that exists in this repo.
  7. Sanity probe: the def scan must see a known def, so an empty scan cannot pass as a
     verdict on anything.
"""
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
ACCOUNTING = os.path.join(ROOT, "design/Jawa/worldbuilding/review/commission_ledger_85_accounting.json")
REGISTER = os.path.join(ROOT, "design/Jawa/worldbuilding/review/flora_assignment_register.decisions.json")
ITEM = os.path.join(ROOT, "infrastructure/state/items/COMMISSION_LEDGER_CLEANUP_1.md")
LEDGER = os.path.join(ROOT, "infrastructure/state/ledger/events")
RESOLUTIONS = {"built", "queued", "superseded", "dropped"}
LIFECYCLE = {"file": "open", "claim": "open", "start": "open", "implemented": "open",
             "close": "closed", "drop": "dropped", "supersede": "superseded"}


def item_slugs():
    """(sheet, slug) pairs from the item's own list: lines '**sheet** (n): `a`, `b`'."""
    text = open(ITEM, encoding="utf-8").read()
    start = text.index("## the 85 owed slugs")
    end = text.index("\n## ", start + 1)
    out, counts = [], {}
    for line in text[start:end].splitlines():
        m = re.match(r"\*\*(.+?)\*\* \((\d+)\): (.*)", line)
        if not m:
            continue
        sheet = m.group(1).replace("+", " + ").replace("  ", " ")
        slugs = re.findall(r"`([^`]+)`", m.group(3))
        counts[sheet] = (int(m.group(2)), len(slugs))
        out += [(sheet, s) for s in slugs]
    return out, counts


def src_defnames():
    names = set()
    for p in glob.glob(os.path.join(ROOT, "src", "**", "*.xml"), recursive=True):
        try:
            names.update(re.findall(r"<defName>\s*([A-Za-z0-9_]+)\s*</defName>",
                                    open(p, encoding="utf-8", errors="ignore").read()))
        except OSError:
            pass
    return names


def item_states():
    state = {}
    # The pre-shard ledger (events.jsonl) holds the older items; the seat shards the rest.
    paths = [LEDGER + ".jsonl"] + sorted(glob.glob(os.path.join(LEDGER, "*.jsonl")))
    for p in (q for q in paths if os.path.exists(q)):
        for line in open(p, encoding="utf-8"):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            ev, iid = e.get("event"), e.get("id")
            if iid and ev in LIFECYCLE:
                state.setdefault(iid, []).append((e.get("ts", ""), LIFECYCLE[ev]))
    return {k: sorted(v)[-1][1] for k, v in state.items()}


def commit_exists(sha):
    return subprocess.run(["git", "-C", ROOT, "cat-file", "-e", sha + "^{commit}"],
                          capture_output=True).returncode == 0


def main():
    fails = []
    doc = json.load(open(ACCOUNTING, encoding="utf-8"))
    rows = doc["rows"]
    register = json.load(open(REGISTER, encoding="utf-8"))["decisions"]
    wanted, counts = item_slugs()
    for sheet, (n, got) in counts.items():
        if n != got:
            fails.append(f"item list: sheet {sheet} says ({n}) but lists {got}")
    if len(wanted) != 85:
        fails.append(f"item list parses to {len(wanted)} slugs, not 85")
    wanted_keys = [f"ledger:{s}:{g}" for s, g in wanted]
    keys = [r["key"] for r in rows]
    for k in sorted(set(wanted_keys) - set(keys)):
        fails.append(f"missing row: {k}")
    for k in sorted(set(keys) - set(wanted_keys)):
        fails.append(f"extra row: {k}")
    for k in sorted({k for k in keys if keys.count(k) > 1}):
        fails.append(f"duplicate row: {k}")

    defs = src_defnames()
    if len(defs) < 1000 or "RM_Shivven" not in defs:
        fails.append(f"sanity: def scan saw {len(defs)} defNames, RM_Shivven present="
                     f"{'RM_Shivven' in defs}; the instrument is blind")
    states = item_states()
    if states.get("COMMISSION_LEDGER_CLEANUP_1") is None:
        fails.append("sanity: ledger scan cannot see this item itself; the instrument is blind")

    for r in rows:
        k, res = r["key"], r.get("resolution")
        if register.get(k, {}).get("decision") != "in":
            fails.append(f"{k}: not an 'in' ledger key in the register")
        if res not in RESOLUTIONS:
            fails.append(f"{k}: resolution {res!r} not one of {sorted(RESOLUTIONS)}")
            continue
        for d in r.get("defs", []):
            if d not in defs:
                fails.append(f"{k}: def {d} not found under src/")
        for f in r.get("files", []):
            if not os.path.exists(os.path.join(ROOT, f)):
                fails.append(f"{k}: file {f} missing")
        for i in r.get("items", []):
            if i not in states:
                fails.append(f"{k}: item {i} not in the ledger")
        if res == "built" and not (r.get("defs") or r.get("files")):
            fails.append(f"{k}: built with no def or file named")
        if res == "queued":
            if not r.get("items"):
                fails.append(f"{k}: queued with no item")
            for i in r.get("items", []):
                if states.get(i) not in (None, "open"):
                    fails.append(f"{k}: queued on {i}, which is {states[i]}; re-resolve the slug")
        if res == "superseded":
            if not r.get("items"):
                fails.append(f"{k}: superseded with no item")
            for i in r.get("items", []):
                if states.get(i) == "dropped":
                    fails.append(f"{k}: superseded into {i}, which was dropped; the slug is lost")
        if res == "dropped" and not (r.get("commit") and commit_exists(r["commit"])):
            fails.append(f"{k}: dropped without an existing commit naming the cut")

    for f in fails:
        print("FAIL", f)
    by = {}
    for r in rows:
        by[r.get("resolution")] = by.get(r.get("resolution"), 0) + 1
    print(f"{'FAIL' if fails else 'PASS'}: {len(rows)} rows {by}, {len(defs)} defNames scanned,"
          f" {len(fails)} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
