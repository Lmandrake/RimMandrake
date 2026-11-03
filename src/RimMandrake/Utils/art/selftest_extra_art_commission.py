#!/usr/bin/env python3
"""Selftest: the per-biome extra-art commission (EXTRA_ART_PER_BIOME_COMMISSION_1).

Offline except for one read of the artpipe registry. Checks:
 1 sanity probe: the def reader sees >= 500 animal kinds, >= 100 canon entries and reads RSW_Kybuck as a pack herd with
   canon dimorphism; the walk table has >= 400 rows; the hand-read detector, emptied, finds >= 10 unread hits
 2 extra_art_commission.check(): commission.csv equals a fresh plan from today's defs and walk, no canon hit is unread,
   and every job of each biome in commission_state.json is on the artpipe queue/registry
 3 coverage: every walked herd creature (herdAnimal or canon herd, max group > 1, not canon solitary) with neither a
   female look nor an alternateGraphics variant has exactly one HERD look row, female only on an accepted canon
   dimorphism, a female pack row exactly when it is a female pack beast; every YOUNG row meets the guideline rule
 4 mutant probes: owed() gives no herd look to a solitary-canon, a group-of-one or an already-varied creature; check()
   goes red on a dropped table row, a state biome missing a job id, and a job id absent from the queue
 5 the eligibility gate counts a commissioned slot as drawn by its def (NONE), and still refuses a path the table does
   not name

    python3 src/RimMandrake/Utils/art/selftest_extra_art_commission.py
"""
import copy
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extra_art_commission as E  # noqa: E402

fails = []


def expect(cond, msg):
    if not cond:
        fails.append(msg)


defs = E.Defs()
walk = list(csv.DictReader(open(E.GROUPS, newline="")))
table = E.read_table()
state = E.read_state()

# 1 sanity
expect(len(defs.kinds) >= 500, f"def reader sees only {len(defs.kinds)} PawnKindDefs")
expect(len(defs.canon) >= 100, f"canon library reads only {len(defs.canon)} entries")
expect(len(walk) >= 400, f"walk table has only {len(walk)} rows")
k = defs.creature("RSW_Kybuck")
expect(k is not None and k["pack"] and k["herd"] and k["dimorph"], f"RSW_Kybuck misread: {k and {x: k[x] for x in ('pack', 'herd', 'dimorph')}}")
saved = [dict(d) for d in (E.DIMORPH_ACCEPT, E.DIMORPH_REJECT, E.YOUNG_ACCEPT, E.YOUNG_REJECT)]
for d in (E.DIMORPH_ACCEPT, E.DIMORPH_REJECT, E.YOUNG_ACCEPT, E.YOUNG_REJECT):
    d.clear()
blind = E.unread_hits()
for d, s in zip((E.DIMORPH_ACCEPT, E.DIMORPH_REJECT, E.YOUNG_ACCEPT, E.YOUNG_REJECT), saved):
    d.update(s)
expect(len(blind) >= 10, f"unread-hit detector is blind: {len(blind)} hits with every list emptied")

# 2 the tool's own check, queue included
ids = E.queued_ids()
errs = E.unread_hits(defs) + E.check(E.plan(defs), table, state, ids)
for e in errs:
    fails.append(f"check: {e}")
expect(len(state.get("biomes", {})) >= 1, "no biome is commissioned yet (commission_state.json)")

# 3 coverage against the walk, re-derived independently of plan()
rows_by = {(r["race"], r["slot"]): r for r in table}
herd_races = set()
for g in walk:
    c = defs.creature(g["kind"])
    if c is None or not c["adult_tex"]:
        continue
    canon = (g.get("canon_ruling") or "").strip()
    if (c["herd"] or canon == "herd") and canon != "solitary" and E.gmax(g["set_wildGroupSize"]) > 1 \
            and not (c["has_female"] or c["has_variant"]):
        herd_races.add(c["race"])
        looks = [s for s in ("female", "variant") if (c["race"], s) in rows_by]
        expect(len(looks) == 1, f"{c['race']} ({g['biome']}): herd creature with herd looks {looks}")
        if looks == ["female"]:
            expect(c["race"] in E.DIMORPH_ACCEPT, f"{c['race']}: female look without an accepted canon dimorphism")
            expect(((c["race"], "female_pack") in rows_by) == c["pack"], f"{c['race']}: female pack set wrong")
for (race, slot), r in rows_by.items():
    if r["rule"] == "HERD":
        expect(race in herd_races, f"{race}: HERD row for a creature no walk row makes a herd")
    else:
        c = defs.creature(r["kind"])
        ok = c["young"] or ((c["pack"] or c["domestic"]) and (c["young_days"] or 0) >= E.YOUNG_MIN_DAYS
                            and c["size"] >= E.YOUNG_MIN_SIZE)
        expect(bool(ok) and not c["distinct_young"], f"{race}: YOUNG row breaks the guideline rule")
expect(len(herd_races) >= 100, f"only {len(herd_races)} herd creatures owed a look; walk misread?")

# 4 mutants
g0 = {"set_wildGroupSize": "3~6", "canon_ruling": ""}
c0 = dict(defs.creature("RSW_Kybuck"))
expect(any(s == "female" for _, _, s, _ in E.owed(c0, g0)), "owed(): kybuck herd gets no female look")
expect(not any(r == "HERD" for r, *_ in E.owed(c0, dict(g0, canon_ruling="solitary"))), "solitary canon got a herd look")
expect(not any(r == "HERD" for r, *_ in E.owed(c0, dict(g0, set_wildGroupSize="1"))), "group of one got a herd look")
expect(not any(r == "HERD" for r, *_ in E.owed(dict(c0, has_variant=True), g0)), "already-varied creature got a look")
fresh = E.plan(defs)
expect(E.check(fresh, fresh[1:], {"biomes": {}}, None), "check() blind to a dropped table row")
if state.get("biomes"):
    b, rec = next(iter(state["biomes"].items()))
    bad = copy.deepcopy(state)
    bad["biomes"][b]["jobs"] = rec["jobs"][1:]
    expect(E.check(fresh, fresh, bad, ids), "check() blind to a state biome missing a job id")
    expect(E.check(fresh, fresh, state, ids - {rec["jobs"][0]}), "check() blind to a job absent from the queue")

# 5 the gate
sys.path.insert(0, os.path.dirname(HERE))
import regen_eligibility as RE  # noqa: E402

gate = RE.Gate()
r0 = next(r for r in table if r["facings"])
dest = f"src/{r0['install_mod']}/Textures/{r0['tex_path']}_east.png"
v = gate.classify({"id": "probe", "target_def": r0["race"], "install_to": dest})
expect(v["verdict"] != "REFUSED_UNCONFIRMED",              # NONE before its art lands, REGEN after
       f"gate does not see the commissioned slot {dest}: {v['verdict']} {v['reason'][:120]}")
v2 = gate.classify({"id": "probe2", "target_def": r0["race"], "install_to": dest.replace(r0["tex_path"], r0["tex_path"] + "Bogus")})
expect(v2["verdict"] not in RE.ELIGIBLE, f"gate accepts an uncommissioned path: {v2['verdict']}")

if fails:
    print(f"FAIL selftest_extra_art_commission: {len(fails)}")
    for f in fails[:40]:
        print("  -", f)
    sys.exit(1)
print(f"OK selftest_extra_art_commission: {len(table)} looks over {len({r['biome'] for r in table})} biomes, "
      f"{len(herd_races)} herd creatures covered, commissioned {sorted(state['biomes'])}")
