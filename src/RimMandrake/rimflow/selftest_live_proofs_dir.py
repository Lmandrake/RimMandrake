#!/usr/bin/env python3
"""selftest_live_proofs_dir.py - LIVE_PROOFS_POPULATE_CLEAN_BUILDS_FIRST and LIVE_PROOFS_STRAY_PRUNE_RED_SELFTEST: the
real infrastructure/state/live_proofs/ holds only proof files whose every line parses, plus a proof's own .py/.json, and
every file names an item the ledger knows. Carried verbatim out of selftest_relentless_live_round.py's t_proofs_file
when the retired tick went (RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES); its line grammars are
proof_lines.py's, plus live-without and live-companion, which no live reader parses any more but three proof files
still carry.

    python3 src/RimMandrake/rimflow/selftest_live_proofs_dir.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import proof_lines as R      # noqa: E402

LIVE_COMPANION = re.compile(r"^\s*(?:[-*]\s+)?`?live-companion\s*:\s*(?P<what>[^`#]*?)`?\s*(?:#.*)?$")
LIVE_WITHOUT = re.compile(r"^\s*(?:[-*]\s+)?`?live-without\s*:\s*(?P<mods>[^`]*)`?\s*$")
FAILS = []


def check(name, cond, detail=""):
    print("%s %s%s" % ("PASS" if cond else "FAIL", name, (": %s" % detail) if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


def t_proofs_file():
    real = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), R.PROOFS_DIR)
    names = sorted(os.listdir(real)) if os.path.isdir(real) else []
    bad = []
    crit_line = re.compile(r"^[A-Z]+\d+ [A-Z0-9-]+: \S")     # <ID>.criteria: `A2 L1: what is observed` (worker brief)
    for n in names:
        if n.endswith((".py", ".json")) or n.count(".") > 1 and n.endswith(".txt"):   # <ID>.<kind>.txt is data
            continue        # a proof's own script/fixture (`live-proof A1: python3 <ID>_live.py`), not a proof file
        with open(os.path.join(real, n), encoding="utf-8") as f:
            for line in f:
                ok = crit_line.match(line) if n.endswith(".criteria") else (R.PROOF_LINE.match(line.rstrip("\n"))
                                                                             or R.LIVE_MODS.match(line.rstrip("\n"))
                                                                             or R.SITE_LINE.match(line.rstrip("\n"))
                                                                             or R.LIVE_TIER.match(line.rstrip("\n"))
                                                                             or LIVE_WITHOUT.match(line.rstrip("\n"))
                                                                             or LIVE_COMPANION.match(line.rstrip("\n"))
                                                                             or R.LIVE_MENU.match(line.rstrip("\n"))
                                                                             or R.LIVE_TOGGLE.match(line.rstrip("\n")))
                if line.strip() and not line.startswith("#") and not ok:
                    bad.append("%s: %s" % (n, line[:60]))
    check("proofs: every real live_proofs file is .txt/.criteria (or a proof's .py/.json) and every line parses", names and all(
        n.endswith((".txt", ".criteria", ".py", ".json")) for n in names) and not bad, "%s %s" % (names[:3], bad[:3]))
    # LIVE_PROOFS_STRAY_PRUNE_RED_SELFTEST: a proof's own .py/.json/.<kind>.txt may sit here, but every file is
    # <ID>[_suffix].<ext> for an item the ledger knows; an orphan (typo'd id, item deleted) is a stray to prune.
    ids = set()
    books = os.path.dirname(real)
    for sub in ("items", "items/closed"):
        p = os.path.join(books, sub)
        ids.update(f[:-3] for f in (os.listdir(p) if os.path.isdir(p) else []) if f.endswith(".md"))
    ev = os.path.join(books, "ledger", "events")
    for shard in (os.listdir(ev) if os.path.isdir(ev) else []):
        with open(os.path.join(ev, shard), encoding="utf-8") as f:
            text = f.read()
        ids.update(m.group(1) for m in re.finditer(r'"id": ?"([^"]+)"', text))
        # a spawned item (no items/<ID>.md yet) is named by its spawn event's `name`, never an `id`
        ids.update(m.group(1) for m in re.finditer(r'"event": ?"spawn"[^\n]*?"name": ?"([^"]+)"', text))
    stems = {n.split(".")[0] for n in names}
    orphans = sorted(s for s in stems if not any(s == i or s.startswith(i + "_") for i in ids if s.startswith(i)))
    check("proofs: every real live_proofs file names a ledger item (no orphan strays)",
          len(ids) > 100 and stems and not orphans, "%d ids, orphans %s" % (len(ids), orphans[:5]))


if __name__ == "__main__":
    t_proofs_file()
    print("selftest_live_proofs_dir: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    sys.exit(1 if FAILS else 0)
