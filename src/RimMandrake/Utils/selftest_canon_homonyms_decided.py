#!/usr/bin/env python3
"""selftest_canon_homonyms_decided.py -- every canon NAME COLLISION has one ruling, and src/ agrees with it.
CANON_HOMONYMS_DECIDE_SAME_WORD_NEW_BIRD. The census (design/RimStarWars/canon_references/gpt_review/
census_no_entry.py, dict VERDICT) marks races whose word is also a different canon creature. Each such row must
have exactly one ruling in canon_homonyms_decision.json (beside it), and the tree must match that ruling:
  accept             the def still exists under that defName
  rename             the old defName is gone from src/ defs and the new one ("to") exists
  retier_at_sitting  the def still exists (Q12: it moves at its biome sitting, not before)
  deleted            no def under src/ carries that defName
Sanity: a planted undecided collision row and a planted 'deleted' def that exists both read red.
    python3 src/RimMandrake/Utils/selftest_canon_homonyms_decided.py
Exit 0 pass, 1 fail.
"""
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GPT = ROOT / "design" / "RimStarWars" / "canon_references" / "gpt_review"
CENSUS = GPT / "census_no_entry.py"
DECISION = GPT / "canon_homonyms_decision.json"
RULINGS = {"accept", "rename", "retier_at_sitting", "deleted"}
DEFNAME = re.compile(r"<defName>\s*([A-Za-z0-9_]+)\s*</defName>")

fails = []


def check(label, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + label + ("" if ok else f"  -- {detail}"))
    if not ok:
        fails.append(label)


def collisions(src_text):
    """The NAME COLLISION keys of the census's VERDICT dict, read with ast (no import, no network)."""
    for node in ast.walk(ast.parse(src_text)):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "VERDICT" for t in node.targets):
            d = ast.literal_eval(node.value)
            return sorted(k for k, v in d.items() if v[0] == "NAME COLLISION")
    return None


def src_defnames():
    names = set()
    for f in (ROOT / "src").rglob("*.xml"):
        try:
            names.update(DEFNAME.findall(f.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            pass
    return names


def problems(coll, rulings, defs):
    out = []
    for name in coll:
        r = rulings.get(name)
        if r is None:
            out.append(f"{name}: no ruling")
            continue
        kind = r.get("ruling")
        if kind not in RULINGS:
            out.append(f"{name}: ruling {kind!r} not one of {sorted(RULINGS)}")
        elif not (r.get("why") or "").strip():
            out.append(f"{name}: ruling has no why")
        elif kind in ("accept", "retier_at_sitting") and name not in defs:
            out.append(f"{name}: ruled {kind} but no def of that name under src/")
        elif kind == "deleted" and name in defs:
            out.append(f"{name}: ruled deleted but a def of that name is under src/")
        elif kind == "rename" and (name in defs or r.get("to") not in defs):
            out.append(f"{name}: ruled rename to {r.get('to')!r} but the tree does not show it")
    for name in rulings:
        if name not in coll:
            out.append(f"{name}: ruling for a row the census does not mark NAME COLLISION")
    return out


coll = collisions(CENSUS.read_text(encoding="utf-8"))
check("census VERDICT dict found and holds collision rows", bool(coll), coll)
doc = json.loads(DECISION.read_text(encoding="utf-8"))
rulings = doc.get("rulings", {})
defs = src_defnames()
check("instrument sees src/ defs (RM_Mirrik and RM_FireHawk found)", {"RM_Mirrik", "RM_FireHawk"} <= defs,
      len(defs))
if coll:
    p = problems(coll, rulings, defs)
    check(f"every one of {len(coll)} collision rows ruled and the tree agrees", not p, p)
    # sanity: the checker can see an undecided row and a lying 'deleted'
    planted = problems(coll + ["RM_PlantedHomonym"], rulings, defs)
    check("sanity: a planted undecided row reads red", any("RM_PlantedHomonym" in x for x in planted), planted)
    liar = dict(rulings, RM_FireHawk={"ruling": "deleted", "why": "planted"})
    check("sanity: 'deleted' on a def that exists reads red",
          any(x.startswith("RM_FireHawk") for x in problems(coll, liar, defs)))
print("RESULT", "FAIL" if fails else "PASS")
sys.exit(1 if fails else 0)
