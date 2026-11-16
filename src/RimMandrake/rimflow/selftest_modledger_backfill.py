#!/usr/bin/env python3
"""Selftest for modledger_backfill.py on a fixture concept folder (never the real ones).

    python3 src/RimMandrake/Utils/run_selftests.py --only modledger_backfill

Shadow mode: the backfill writes only the mod's ledger (every event BACKFILL, every one citing its old file), leaves
every old file byte for byte, is idempotent, turns a blind fault's smallest_fix into the finding's proposed fix, keeps
a FIXED fault open as claimed (no judge verdict), counts his words as answers, and `compare` names a stale journal.
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modledger as M                                            # noqa: E402
import modledger_backfill as B                                   # noqa: E402

FAIL = []
MOD = "FixtureMod"


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        FAIL.append(name)


def w(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(obj if isinstance(obj, str) else json.dumps(obj))


root = tempfile.mkdtemp(prefix="modledger_bf_")
c = os.path.join(root, "design", "concepts", MOD)
v = os.path.join(c, "version")
w(os.path.join(v, "VERSION.json"), {"mod": MOD, "version": "0.1.0", "state": "locked", "locked_on": "2026-11-13",
                                    "locked_by": "owner", "owner_words": "\"Lock it.\" (owner)", "bars_total": 2,
                                    "bars_met": 2})
w(os.path.join(v, "stage_record.json"), {"stage": "offline_build", "stage_label": "Offline build (Stage 3)",
                                         "since": "2026-11-15T17:50:11-08:00", "since_from": "advance",
                                         "moves": [{"from": "offline_build", "to": "in_game", "at": "x", "by": "C",
                                                    "why": "exit met"},
                                                   {"from": "in_game", "to": "offline_build", "at": "y", "by": "C",
                                                    "why": "visit failed"}]})
w(os.path.join(v, "locked_bars.json"), {"ids": ["bar_a", "bar_b"]})
w(os.path.join(v, "test_table.json"), {"made": "2026-11-14", "bars": [
    {"id": "bar_a", "kind": "experience", "source": "tree.json", "proves_at": "6", "decides": ["sc_a"],
     "offline_green_today": True},
    {"id": "bar_b", "kind": "inventory", "source": "record.json", "proves_at": "3", "decides": [],
     "offline_green_today": False}]})
w(os.path.join(v, "in_game", "visit_1", "rows.jsonl"),
  json.dumps({"test": "sc_a", "verdict": "FAIL"}) + "\n" + json.dumps({"test": "sc_a", "verdict": "PASS"}) + "\n")
w(os.path.join(v, "blind_challenge", "cycle_1", "lane2", "faults.json"), {"faults": [
    {"id": "FAULT_ONE", "class": "Problem", "bar": "bar_a", "criterion": "a thrown pawn stops at a wall",
     "evidence": ["row L1 FAIL"], "smallest_fix": "stop the ray at the first impassable cell", "status": "FIXED abc"},
    {"id": "FAULT_TWO", "class": "Polish", "bar": "bar_b", "criterion": "short", "evidence": ["e"],
     "smallest_fix": "K-1", "status": "PENDING"}]})
w(os.path.join(c, "journal.md"), "# j\n\n## The mod as it stands\n\n- **Stage now:** Stage 3, offline build.\n"
  "- Every in-game scene is UNRUN (Stage 6).\n- **Waiting on:** not yet written for this stage.\n\n"
  "### His words on this mod (verbatim)\n\n- 2026-11-10: \"Throw it far.\"\n- 2026-11-12: \"Shelves are open,\n"
  "  period.\"\n\n### Oddities\n")
w(os.path.join(root, "infrastructure", "state", "items", "RIMMANDRAKE_FIX_FIXTUREMOD_THING_ONE.md"),
  "# RIMMANDRAKE_FIX_FIXTUREMOD_THING_ONE\n\nFixtureMod drops goods.\n\n## spec\n\nfile: Source/A.cs — keep the goods.\n")
w(os.path.join(root, "infrastructure", "state", "items", "RIMMANDRAKE_FIX_OTHER_MOD_THING.md"),
  "# RIMMANDRAKE_FIX_OTHER_MOD_THING\n\nNot ours.\n")
before = {}
for d, _, fs in os.walk(c):
    for f in fs:
        p = os.path.join(d, f)
        before[p] = hashlib.sha256(open(p, "rb").read()).hexdigest()

res = B.run(root, MOD)
check("backfill writes events", res["written"] > 0, res)
res2 = B.run(root, MOD)
check("a second backfill writes nothing (idempotent)", res2["written"] == 0 and res2["already"] == res["written"], res2)
after = {p: hashlib.sha256(open(p, "rb").read()).hexdigest() for p in before}
check("shadow mode: every old file is unchanged byte for byte", after == before)
evs = M.read(root, MOD)
check("every event is BACKFILL and cites an existing old file",
      all(e["writer"] == "BACKFILL" and e["evidence"] and
          os.path.exists(os.path.join(root, e["evidence"][0].split("#")[0].rsplit(":", 1)[0])) for e in evs),
      [e["evidence"] for e in evs if not e["evidence"]])
st = M.reduce(evs)
check("stage and version come from the stage record and VERSION.json", st["stage"] == "offline_build" and
      st["version"] == "0.1.0", (st["stage"], st["version"]))
check("bars: two locked, bar_a's verdict from the last live row", len(st["bars"]) == 2 and
      "1 of 1" in (st["bars"]["bar_a"]["verdict"] or ""), st["bars"])
f1 = st["findings"].get("FAULT_ONE") or {}
check("a FIXED fault stays open as claimed, its smallest_fix as the proposed fix",
      f1.get("status") == "claimed_fixed" and "impassable" in (f1.get("proposed_fix") or ""), f1)
f2 = st["findings"].get("FAULT_TWO") or {}
check("a pointer-sized smallest_fix is kept and labelled, not padded", (f2.get("proposed_fix") or "").startswith("K-1 ")
      and "pointer" in f2["proposed_fix"], f2)
check("the item naming the mod is a finding with its spec as the fix, the other mod's is not",
      "file: Source/A.cs" in (st["findings"].get("RIMMANDRAKE_FIX_FIXTUREMOD_THING_ONE") or {}).get("proposed_fix", "")
      and "RIMMANDRAKE_FIX_OTHER_MOD_THING" not in st["findings"], sorted(st["findings"]))
check("his words count as his answers, a wrapped bullet joined", any("Shelves are open, period." in a["answer"]
                                                                    for a in st["answers"].values()), st["answers"])
check("the views exist and the mod ledger lints clean", M.lint(root, MOD, None)[0] == [], M.lint(root, MOD, None)[0])
rows = {r[0]: r for r in B.compare(root, MOD)}
check("compare: the stage agrees with the stage record", rows["stage (version/stage_record.json)"][3])
check("compare: a journal claiming every scene UNRUN against live rows is a DIFF",
      rows["journal.md stands: in-game scenes"][3] is False, rows["journal.md stands: in-game scenes"])
txt, info = M.packet(root, MOD)
check("the packet prints under budget and ends with what it left out", info["tokens"] <= info["budget"] and
      "## Left out" in txt, info)

shutil.rmtree(root, ignore_errors=True)
print("selftest_modledger_backfill: %d failure%s" % (len(FAIL), "" if len(FAIL) == 1 else "s"))
sys.exit(1 if FAIL else 0)
