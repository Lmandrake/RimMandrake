#!/usr/bin/env python3
"""Proof for CLONE_POOL_DECIDE_REVERT_CLAUSE_TRIPPED: the pool revert was decided NOT to be carried out, and why.

The item asks: salvage the stranded clones, then carry out the 2026-10-31 pool revert or record why not.
Exit 0 only when every clause holds; each failed clause prints FAIL and the script exits 1.
  C1 the ledger holds an event on this item whose text starts the why-not ('REVERT NOT CARRIED OUT')
     and cites both the salvage item and the owner's widening card ruling
  C2 the salvage item POOL_STRANDS_SALVAGE_BLOCKED_HOLD_THE_BAG is closed with a sha
  C3 the cited ruling RELENTLESS_CAPACITY_WIDEN_EIGHT_ON_SIXTEEN exists, was taken by card, says 16 clones / 70 GB, and is closed
  C4 the cap in force (scratch_clone.py) is that card's 16 clones / 70 GB, so the 40 GB trip is moot
  C5 the revert clause still stands for future trips (CLAUDE.md and scratch_clone.py), at the widened 70 GB
The ledger is read as JSON lines (a Marker box holds the ledger as of the proof commit's parent).
"""
import glob, json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
ITEM, SALVAGE, CARD = ("CLONE_POOL_DECIDE_REVERT_CLAUSE_TRIPPED", "POOL_STRANDS_SALVAGE_BLOCKED_HOLD_THE_BAG",
                       "RELENTLESS_CAPACITY_WIDEN_EIGHT_ON_SIXTEEN")
fails = []


def check(name, ok, detail):
    print(("PASS " if ok else "FAIL ") + name + ": " + detail)
    if not ok:
        fails.append(name)


events = []
shards = sorted(glob.glob(os.path.join(ROOT, "infrastructure/state/ledger/events/*.jsonl")))
for f in shards:
    for line in open(f, encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                events.append(json.loads(line))
            except ValueError:
                pass
# sanity probe: the instrument can see the ledger at all
check("C0 ledger readable", len(shards) > 0 and len(events) > 1000, "%d shards, %d events" % (len(shards), len(events)))

def of(i):
    return [e for e in events if e.get("id") == i]

why = [e for e in of(ITEM) if "REVERT NOT CARRIED OUT" in str(e.get("text", ""))]
check("C1 why-not on the ledger", any(SALVAGE in e["text"] and CARD in (e["text"] + str(e.get("perRuling", "")) + json.dumps(e))
                                      for e in why), "%d why-not event(s) on %s" % (len(why), ITEM))

sc = [e for e in of(SALVAGE) if e.get("event") == "close" and re.fullmatch(r"[0-9a-f]{7,40}", str(e.get("sha", "")))]
check("C2 salvage closed", bool(sc), "close events with a sha: %s" % [e.get("sha", "")[:8] for e in sc])

card = of(CARD)
bycard = " ".join(str(e.get("byCard", "")) for e in card)
closed = any(e.get("event") == "close" for e in card)
check("C3 widening card ruling", bool(re.search(r"16 clones\s*/\s*70 GB", bycard)) and closed,
      "byCard=%r closed=%s" % (bycard[:90], closed))

src = open(os.path.join(ROOT, "src/RimMandrake/Utils/scratch_clone.py"), encoding="utf-8").read()
mc = re.search(r"^POOL_MAX_CLONES\s*=\s*(\d+)\s*$", src, re.M)
mb = re.search(r"^POOL_MAX_BYTES\s*=\s*(\d+)\s*\*\s*10\*\*9\s*$", src, re.M)
check("C4 cap in force is 16 / 70 GB", bool(mc and mb and mc.group(1) == "16" and mb.group(1) == "70"),
      "POOL_MAX_CLONES=%s POOL_MAX_BYTES=%s GB" % (mc and mc.group(1), mb and mb.group(1)))

md = open(os.path.join(ROOT, "CLAUDE.md"), encoding="utf-8").read()
check("C5 revert clause stands", "Revert if a clone strands work or the pool passes 70 GB" in md
      and re.search(r"clone strands work, or the pool passes 70 GB", src) is not None,
      "CLAUDE.md and scratch_clone.py carry the revert line at 70 GB")

print("RESULT", "FAIL " + ",".join(fails) if fails else "PASS")
sys.exit(1 if fails else 0)
