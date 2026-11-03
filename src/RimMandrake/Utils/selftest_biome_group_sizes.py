#!/usr/bin/env python3
"""Selftest: every custom creature on a live biome roster spawns in its walked group size (BIOME_GROUP_SIZE_WALK_1).

Offline, a few seconds. Checks:
 1 sanity probe: the roster reader sees at least 25 live biomes and 400 custom rows, and reads RSW_Skalder on
   RM_Cauldron (patch-added) and RM_Ullai on RM_Pyrelands (inline)
 2 biome_group_sizes.check(): every roster row has a walk row, every walk row is on a roster, each def's
   wildGroupSize equals the walk's, src is delegated:design, and the canon herd/solitary rulings hold
 3 the judge record names the GPT judge and covers every walked kind; a SET or KEEP row's size equals the
   judge's; a SPEC_PINNED row names a spec path that exists
 4 mutant probes: the checker goes red on a changed def size, a dropped or duplicate walk row, a fractional
   size, a reversed range, a missing PawnKindDef, a canon-solitary creature in a group, and a canon-herd creature alone; write_size() edits only the
   named PawnKindDef and refuses one whose comment names the field; a fixture roster applies a Conditional's
   match branch (single-quoted xpath), not its nomatch branch nor a match nested in an inactive nomatch, and merges
   a parent BiomeDef's roster into the child's

    python3 src/RimMandrake/Utils/selftest_biome_group_sizes.py
"""
import copy
import json
import os
import pathlib
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biome_group_sizes as bgs  # noqa: E402

RECORD = bgs.ROOT / "infrastructure/state/delegated/2026-11-03/BIOME_GROUP_SIZE_WALK_1.json"
fails = []


def expect(cond, msg):
    if not cond:
        fails.append(msg)


rows = bgs.measure()
table = bgs.read_csv(bgs.TABLE)
rulings = bgs.read_csv(bgs.RULINGS)

# 1 sanity probe
biomes = {r["biome"] for r in rows}
expect(len(biomes) >= 25, f"only {len(biomes)} live biomes read")
expect(len(rows) >= 400, f"only {len(rows)} custom roster rows read")
keys = {(r["biome"], r["kind"]) for r in rows}
expect(("RM_Cauldron", "RSW_Skalder") in keys, "patch-added RSW_Skalder on RM_Cauldron not read")
expect(("RM_Pyrelands", "RM_Ullai") in keys, "inline RM_Ullai on RM_Pyrelands not read")

# 2 the real check
for b in bgs.check(rows, table, rulings):
    fails.append("check: " + b)

# 3 the judge record
record = json.loads(RECORD.read_text(encoding="utf-8"))
expect("gpt" in str(record.get("judge_model", "")).lower(), "judge record does not name the GPT judge")
judged = {v["subject"]: v for v in record["rows"]}
for t in table:
    j = judged.get(t["kind"])
    if j is None:
        fails.append(f"{t['kind']}: no judge row")
        continue
    if t["judge_verdict"] in ("KEEP", "SET"):
        expect(t["set_wildGroupSize"] == j["size"], f"{t['kind']}: walk {t['set_wildGroupSize']} != judge {j['size']}")
    elif t["judge_verdict"] == "SPEC_PINNED":
        spec = t["judge_reason"].split("spec ", 1)[-1].split(":", 1)[0]
        expect((bgs.ROOT / spec).is_file(), f"{t['kind']}: pinned to missing spec {spec!r}")
    else:
        fails.append(f"{t['kind']}: verdict {t['judge_verdict']!r}")

# 4 mutant probes
if rows:
    m = copy.deepcopy(rows)
    m[0]["wildGroupSize"] = "99~99"
    expect(bgs.check(m, table, rulings), "mutant: a changed def size passed")
    expect(bgs.check(rows, table[1:], rulings), "mutant: a dropped walk row passed")
    solo = {"defs": rows[0]["kind"], "decision": "solitary"}
    herd = {"defs": rows[0]["kind"], "decision": "herd"}
    m2 = copy.deepcopy(rows)
    m2[0]["wildGroupSize"] = "3~6"
    t2 = copy.deepcopy(table)
    for t in t2:
        if t["kind"] == rows[0]["kind"]:
            t["set_wildGroupSize"] = "3~6"
    expect(any("canon solitary" in b for b in bgs.check(m2, t2, [solo])), "mutant: canon-solitary in a group passed")
    m2[0]["wildGroupSize"] = "1"
    for t in t2:
        if t["kind"] == rows[0]["kind"]:
            t["set_wildGroupSize"] = "1"
    expect(any("canon herd" in b for b in bgs.check(m2, t2, [herd])), "mutant: canon-herd alone passed")
text = ("<Defs>\n  <PawnKindDef>\n    <defName>A</defName>\n    <wildGroupSize>1</wildGroupSize>\n  </PawnKindDef>\n"
        "  <PawnKindDef>\n    <defName>B</defName>\n    <race>B</race>\n  </PawnKindDef>\n</Defs>\n")
out = bgs.write_size(bgs.write_size(text, "A", "2~4"), "B", "3~6")
expect("<defName>A</defName>\n    <wildGroupSize>2~4</wildGroupSize>" in out, "write_size did not replace A's size")
expect("<defName>B</defName>\n    <wildGroupSize>3~6</wildGroupSize>\n    <race>B</race>" in out,
       "write_size did not insert B's size")
expect(out.count("<wildGroupSize>") == 2, "write_size touched more than the named defs")

dup = table + [dict(table[0])]
expect(any("duplicate" in b for b in bgs.check(rows, dup, rulings)), "mutant: a duplicate walk row passed")
m3 = copy.deepcopy(rows)
m3[0]["wildGroupSize"] = "2.9~5.9"
expect(bgs.check(m3, table, rulings), "mutant: a fractional def size passed")
m4, t4 = copy.deepcopy(rows), copy.deepcopy(table)
m4[0]["wildGroupSize"] = "5~2"
for t in t4:
    if t["kind"] == rows[0]["kind"]:
        t["set_wildGroupSize"] = "5~2"
expect(bgs.check(m4, t4, rulings), "mutant: a reversed range in both def and walk passed")
for t in t4:
    if t["kind"] == rows[0]["kind"]:
        t["set_wildGroupSize"] = "unset"
m4[0]["wildGroupSize"] = "NO_KINDDEF"
expect(bgs.check(m4, t4, rulings), "mutant: a missing PawnKindDef against an unset walk size passed")
try:
    bgs.write_size(text.replace("<race>B</race>", "<!-- wildGroupSize was 2 --><race>B</race>"), "B", "3~6")
    fails.append("write_size edited a def whose comment names wildGroupSize")
except ValueError:
    pass
# roster fixture: inline row, a Conditional's match branch applies, its nomatch branch does not
with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    (tmp / "d.xml").write_text(
        "<Defs><BiomeDef Name=\"RM_FxBase\" Abstract=\"True\"><wildAnimals><RM_E>1</RM_E></wildAnimals></BiomeDef>"
        "<BiomeDef ParentName=\"RM_FxBase\"><defName>RM_Fx</defName><wildAnimals><RM_A>1</RM_A></wildAnimals></BiomeDef>"
        + "".join(f"<PawnKindDef><defName>RM_{k}</defName><race>RM_{k}</race></PawnKindDef>" for k in "ABCDE")
        + "</Defs>", encoding="utf-8")
    (tmp / "p.xml").write_text(
        "<Patch><Operation Class=\"PatchOperationConditional\"><xpath>Defs/BiomeDef[defName='RM_Fx']/wildAnimals</xpath>"
        "<match Class=\"PatchOperationAdd\"><xpath>Defs/BiomeDef[defName='RM_Fx']/wildAnimals</xpath>"
        "<value><RM_B>1</RM_B></value></match>"
        "<nomatch Class=\"PatchOperationAdd\"><xpath>Defs/BiomeDef[defName='RM_Fx']/wildAnimals</xpath>"
        "<value><RM_C>1</RM_C></value></nomatch></Operation>"
        "<Operation Class=\"PatchOperationConditional\"><xpath>Defs/BiomeDef[defName='RM_Fx']/wildAnimals</xpath>"
        "<nomatch Class=\"PatchOperationConditional\"><xpath>Defs/PawnKindDef[defName='RM_D']</xpath>"
        "<match Class=\"PatchOperationAdd\"><xpath>Defs/BiomeDef[defName='RM_Fx']/wildAnimals</xpath>"
        "<value><RM_D>1</RM_D></value></match></nomatch></Operation></Patch>", encoding="utf-8")
    got = sorted(r["kind"] for r in bgs.measure(tmp))
    expect(got == ["RM_A", "RM_B", "RM_E"], f"roster fixture read {got}, expected RM_A, RM_B and inherited RM_E")

for f in fails:
    print("FAIL", f)
print(f"selftest_biome_group_sizes: {len(rows)} rows, {len(biomes)} biomes, {len(fails)} failures")
sys.exit(1 if fails else 0)
