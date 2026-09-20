#!/usr/bin/env python3
"""Fit every cast animal's comfortable temperature band to the biome it was cast into.

🔴 **DECIDE's ruling, 2026-08-23** — the animal third of `NORMALIZE_TEMPERATURE_TOLERANCES_1`.
The plant third is `design/Jawa/mods/plant_tolerances.py` and uses the same rule.

## Temperature is a HARD SPAWN GATE for animals, not just a comfort stat

Checked, not assumed. `WildAnimalSpawner.cs:47` and `:111` filter the biome's roster through
`map.mapTemperature.SeasonAcceptableFor(race)` before anything can be chosen, and
`MapTemperature.cs:91` is:

    seasonalTemp > ComfyTemperatureMin - buffer  &&  seasonalTemp < ComfyTemperatureMax + buffer

with **buffer 0** at the wild spawner. So the band must **CONTAIN** the biome's temperature —
a stricter test than the plant gate at `PlantUtility.cs:93`, which only needs the band to
OVERLAP the tile's range. An animal whose band misses is not merely uncomfortable: it is never
spawned at all, and nothing is logged.

## The rule: the BIOME sets the band; shipped hardiness is a capped bonus

Identical to the plant pass, and for the same reason — shipped values describe Earth.

    need_lo, need_hi = p05(home tiles) − SWING, p95(home tiles) + SWING
    band = [ min(shipped min, need_lo − ε) , max(shipped max, need_hi + ε) ]

🔴 **WIDEN ONLY — never narrow.** Narrowing can only cause the very bug this closes, and it
buys nothing: the CAST decides where a creature may appear and temperature only removes it. An
earlier version re-centred the band and `GR_ParagonIguana` came out −110.5 … **30.1** °C, having
LOST 45 °C of the heat tolerance it shipped with, for no gain at all.

🔑 **Climate survives because the cast is exclusive.** `BiomeCast_Ashkarr.xml` puts 581 of 652
creatures in exactly ONE biome and none in more than three, so each animal is fitted to one
climate and still dies elsewhere. The ubiquity the owner objected to is what makes this safe.

⚠️ **EPSILON exists because the comparison is STRICT.** `>` and `<`, not `>=` and `<=`, so a
band that merely touches the temperature fails the gate.

⛔ **`BiomeCast_Ashkarr.xml` is retired, not a co-requirement.** It targeted 22
pre-migration biome defNames that `BIOME_OWNERSHIP_WAVE_1` (2026-09-09) replaced with
`RUT_`-prefixed BiomeDefs, zero of which paint any live tile — confirmed dead and deleted
(`BIOME_CAST_PATCH_DEAD_NAMES_1`). The bands below are fitted to the biome
`cast_assignment.csv` records for each creature, independent of whether any patch ever
turned that record into a live `wildAnimals` entry; see `ANIMAL_TOLERANCES_JOIN_BROKEN_1`
for what the cast assignment does and does not guarantee today.

🔴 **`homes()`'s join had the same pre-migration-name defect as the dead cast file** —
`cast_assignment.csv`'s `biome` column still names the OLD biome defNames, but
`world/ASHKARR_WORLDMAP_tiles.csv` (what `_tile_temps()` keys off) carries only the new
`RUT_` ones. Unlike the cast file, this generator's own xpath targets the animal directly
and is unaffected by the mismatch — the danger was only in ever regenerating blind, which
would have silently emitted zero operations and deleted the whole live safety net. Fixed
by resolving through `_OLD_TO_NEW_BIOME` before the lookup (`ANIMAL_TOLERANCES_JOIN_BROKEN_1`,
derived from the same commonality-multiset rekey `biome_flora.py` used at `366c278d6`, plus
`9350e29a3` for the one biome — `AB_PropaneLakes` → `RUT_Umbra` — that moved to a
differently-named live biome outright).
"""
import collections
import csv
import json
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'mods'))
import biome_flora as bf                                            # noqa: E402  tiles + DB

ROOT = bf.ROOT
CAST = os.path.join(HERE, 'cast_assignment.csv')
PATCH = os.path.join(ROOT, 'src', 'RimUtinni', 'UtinniPatches', 'Patches',
                     'AnimalTolerances_Ashkarr.xml')

MIN, MAX = 'ComfyTemperatureMin', 'ComfyTemperatureMax'
DEFAULTS = {MIN: 0.0, MAX: 40.0}      # StatDef defaultBaseValue, read from Core
SWING = 15.0                          # seasonal allowance — a JUDGEMENT, as in the plant pass
EPSILON = 1.0                         # the gate is a STRICT inequality

# Pre-migration -> live biome defName. `cast_assignment.csv`'s `biome` column still names
# the biomes `BIOME_OWNERSHIP_WAVE_1` (2026-09-09) retired; `world/ASHKARR_WORLDMAP_tiles.csv`
# (what `_tile_temps()` keys off) and `biome_flora.py`'s `FAMILIES` (rekeyed at `366c278d6`,
# BIOME_FLORA_GENERATOR_REPAIR_1) carry only the new ones. This map is CROSS-DERIVED from
# that same rekey — a commonality-multiset match against the live rosters, not a name
# guess — plus `9350e29a3` (PROPANE_LAKES_ROSTER_STALE_1) for the one pair that moved to a
# differently-named biome outright. See `ANIMAL_TOLERANCES_JOIN_BROKEN_1`.
_OLD_TO_NEW_BIOME = {
    'AB_FeraliskInfestedJungle': 'RUT_Webwork',
    'AB_GelatinousSuperorganism': 'RUT_Slime',
    'AB_MechanoidIntrusion': 'RUT_RustCathedral',
    'AB_MiasmicMangrove': 'RUT_Miasma',
    'AB_MycoticJungle': 'RUT_TheRot',
    'AB_OcularForest': 'RUT_Contagion',
    'AB_PropaneLakes': 'RUT_Umbra',
    'AB_PyroclasticConflagration': 'RUT_TheForge',
    'AB_RockyCrags': 'RUT_ForsakenCrags',
    'AB_TarPits': 'RUT_Sump',
    'AridShrubland': 'RUT_AridShrubland',
    'BiomeCypreJungle': 'RUT_Greentide',
    'COMIGO_GreaterSwamp_Tropical': 'RUT_FeverWood',
    'Desert': 'RUT_Desert',
    'ExtremeDesert': 'RUT_ExtremeDesert',
    'LavaField': 'RUT_TheForge',
    'PoisonForest': 'RUT_PoisonForest',
    'Scarlands': 'RUT_Scarlands',
    'Volcano': 'RUT_TheForge',
    'Wasteland': 'RUT_Wasteland',
    'ZBiome_Badlands': 'RUT_CrackedLands',
    'ZBiome_DesertOasis': 'RUT_WeepingStones',
    # ZBiome_Grasslands was never renamed - carried unchanged in both CSVs.
}


def animals():
    """defName -> its declared comfy stats, for every animal in the def dump."""
    con = sqlite3.connect(f'file:{bf.DB}?mode=ro', uri=True)
    out = {}
    for (j,) in con.execute("SELECT json FROM defs WHERE def_type='ThingDef'"):
        d = json.loads(j)
        if not d['fields'].get('race'):
            continue
        got = {}
        for m in (d['fields'].get('statBases') or []):
            if isinstance(m, dict) and m.get('stat') in (MIN, MAX):
                got[m['stat']] = float(m.get('value'))
        out[d['defName']] = {'declared': got, 'label': d['fields'].get('label') or d['defName']}
    return out


def homes():
    """animal defName -> the tile temperatures of every biome it was cast into."""
    temps = bf._tile_temps()
    h = collections.defaultdict(list)
    misses = set()
    for r in csv.DictReader(open(CAST, encoding='utf-8')):
        biome = _OLD_TO_NEW_BIOME.get(r['biome'], r['biome'])
        ts = temps.get(biome) or []
        if ts:
            h[r['defName']].extend(ts)
        else:
            misses.add(r['biome'])
    if misses:
        print(f"⚠️  {len(misses)} cast biome name(s) matched nothing in the live tile CSV "
              f"even after _OLD_TO_NEW_BIOME, so every animal cast there was SKIPPED: "
              + ', '.join(sorted(misses)))
    return h


def compute(beasts):
    rows, bonus, already, unknown = [], 0, 0, []
    for a, ts in sorted(homes().items()):
        d = beasts.get(a)
        if not d:
            unknown.append(a)
            continue
        cur = {k: d['declared'].get(k, DEFAULTS[k]) for k in (MIN, MAX)}

        need_lo = _pct(ts, 0.05) - SWING
        need_hi = _pct(ts, 0.95) + SWING

        if cur[MIN] < need_lo and cur[MAX] > need_hi:               # strict, like the gate
            already += 1
            continue

        # 🔴 WIDEN ONLY. Narrowing a band can only ever CAUSE the bug this closes - an
        # animal that is never spawned - and it buys nothing, because the CAST decides
        # where a creature may appear and temperature only removes it. A band that is
        # already generous on one side keeps its shipped value on that side.
        new = {MIN: round(min(cur[MIN], need_lo - EPSILON), 1),
               MAX: round(max(cur[MAX], need_hi + EPSILON), 1)}
        bonus += (new[MIN] == cur[MIN]) or (new[MAX] == cur[MAX])
        rows.append((a, cur, new, round(need_lo, 1), round(need_hi, 1), len(ts), d['label']))
    return rows, bonus, already, unknown


def _pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, max(0, int(round((len(xs) - 1) * p))))] if xs else 0.0


def _deployed_defnames():
    """defNames the CURRENTLY DEPLOYED patch already covers, or set() if it doesn't exist yet.

    Read before `emit()` overwrites the file. ANIMAL_TOLERANCES_JOIN_BROKEN_1: of the 401
    animals the 2026-09-12 patch covers, only ~230 are still in today's cast_assignment.csv
    at all (the rest are stale AA_/BMT_ names `MLIE_FAUNA_ABSORPTION_1` passes moved on from)
    - but 310 of the 401 are STILL live race ThingDefs in the current def dump, meaning most
    of that drift is "no longer curated", not "no longer real". pin_orphans() below is why a
    regenerate cannot just emit `compute()`'s rows and call it done.
    """
    if not os.path.exists(PATCH):
        return set()
    import re
    return set(re.findall(r'<xpath>/Defs/ThingDef\[defName="([^"]+)"\]/statBases</xpath>',
                          open(PATCH, encoding='utf-8').read()))


def pin_orphans(rows, beasts):
    """Never let a regenerate DROP an animal the deployed patch already covers.

    🔴 Dropping a PatchOperation is narrowing by omission - the animal reverts to whatever
    its donor mod ships, which is exactly the bug WIDEN ONLY exists to prevent. An animal
    missing from `rows` because it fell out of `cast_assignment.csv` (ported/renamed/cut by
    a later pass) is NOT evidence it stopped needing its widened band; only a def genuinely
    absent from the current dump is safe to drop (the patch would no-op on it anyway, per
    `PatchOperationConditional`'s documented no-match-no-log behaviour). Everything else
    already-covered gets re-emitted pinned to its own current (already-patched) value, so
    the file can never regress even when the cast roster moves out from under it.
    """
    covered = {r[0] for r in rows}
    pinned, gone = [], []
    for a in sorted(_deployed_defnames() - covered):
        d = beasts.get(a)
        if not d:
            gone.append(a)          # def no longer exists at all - nothing to pin
            continue
        cur = {k: d['declared'].get(k, DEFAULTS[k]) for k in (MIN, MAX)}
        pinned.append((a, cur, cur, None, None, 0, d['label']))
    return pinned, gone


def emit(rows):
    o = ['<?xml version="1.0" encoding="utf-8"?>', '<Patch>',
         '  <!-- GENERATED by design/Jawa/fauna/animal_tolerances.py - do not hand-edit.',
         '',
         '       Every CAST animal\'s comfy band refitted to the biome it was cast into.',
         '       Temperature is a HARD SPAWN GATE, not a comfort stat: WildAnimalSpawner.cs:47',
         '       and :111 filter the roster through SeasonAcceptableFor(race) with buffer 0,',
         '       so an animal whose band misses the biome is NEVER SPAWNED and nothing logs it.',
         '',
         '       The biome sets the band; the animal\'s shipped width only buys a capped',
         '       hardiness bonus. The cast puts 581 of 652 creatures in exactly one biome, so',
         '       each is fitted to one climate and still dies elsewhere.',
         '',
         '       Fitted against the live RUT_-prefixed biome cast_assignment.csv records for',
         '       each creature. BiomeCast_Ashkarr.xml, which once tried to turn that same cast',
         '       into wildAnimals entries, is retired and deleted; see',
         '       ANIMAL_TOLERANCES_JOIN_BROKEN_1 for what the cast assignment does and does',
         '       not guarantee today. -->', '']
    for a, cur, new, nlo, nhi, n, lab in rows:
        if nlo is None:      # pin_orphans(): no live cast row, pinned to avoid narrowing
            comment = (f'  <!-- {lab} ({a}) - not in current cast_assignment.csv; pinned to '
                       f"today's live value so a regenerate cannot narrow it "
                       f'(ANIMAL_TOLERANCES_JOIN_BROKEN_1)  {cur[MIN]:g}..{cur[MAX]:g} -->')
        else:
            comment = (f'  <!-- {lab} ({a}) - {n} tiles, home demands {nlo:g} … {nhi:g} °C  '
                       f'{cur[MIN]:g}..{cur[MAX]:g} -> {new[MIN]:g}..{new[MAX]:g} -->')
        o += [comment,
              '  <Operation Class="PatchOperationConditional">',
              f'    <xpath>/Defs/ThingDef[defName="{a}"]/statBases</xpath>',
              '    <match Class="PatchOperationSequence">',
              '      <operations>']
        for k in (MIN, MAX):
            o += ['        <li Class="PatchOperationConditional">',
                  f'          <xpath>/Defs/ThingDef[defName="{a}"]/statBases/{k}</xpath>',
                  '          <match Class="PatchOperationReplace">',
                  f'            <xpath>/Defs/ThingDef[defName="{a}"]/statBases/{k}</xpath>',
                  f'            <value><{k}>{new[k]:g}</{k}></value>',
                  '          </match>',
                  '          <nomatch Class="PatchOperationAdd">',
                  f'            <xpath>/Defs/ThingDef[defName="{a}"]/statBases</xpath>',
                  f'            <value><{k}>{new[k]:g}</{k}></value>',
                  '          </nomatch>',
                  '        </li>']
        o += ['      </operations>', '    </match>',
              # a race with no statBases block at all still needs one
              '    <nomatch Class="PatchOperationAdd">',
              f'      <xpath>/Defs/ThingDef[defName="{a}"]</xpath>',
              '      <value>', '        <statBases>',
              f'          <{MIN}>{new[MIN]:g}</{MIN}>',
              f'          <{MAX}>{new[MAX]:g}</{MAX}>',
              '        </statBases>', '      </value>',
              '    </nomatch>',
              '  </Operation>', '']
    o.append('</Patch>')
    os.makedirs(os.path.dirname(PATCH), exist_ok=True)
    open(PATCH, 'w', encoding='utf-8').write('\n'.join(o) + '\n')
    return PATCH


def main() -> int:
    beasts = animals()
    rows, bonus, already, unknown = compute(beasts)
    print(f"\n{len(rows)} animals refitted · {already} already survived their whole home · "
          f"{bonus} kept a shipped bound that was already generous enough")
    if unknown:
        print(f"⚠️  {len(unknown)} cast names are not animals in the dump and were SKIPPED: "
              + ', '.join(unknown[:6]) + ('…' if len(unknown) > 6 else ''))
    if rows:
        lo = [r[2][MIN] for r in rows]
        hi = [r[2][MAX] for r in rows]
        print(f"new floors {min(lo):+g} … {max(lo):+g} °C   "
              f"new ceilings {min(hi):+g} … {max(hi):+g} °C")
        for tag, grp in (('coldest', sorted(rows, key=lambda r: r[2][MIN])[:3]),
                         ('warmest', sorted(rows, key=lambda r: -r[2][MAX])[:3])):
            for a, cur, new, nlo, nhi, n, lab in grp:
                print(f"  {tag:8s} {a:30s} {cur[MIN]:g}..{cur[MAX]:g} -> "
                      f"{new[MIN]:g}..{new[MAX]:g}")
    pinned, gone = pin_orphans(rows, beasts)
    if pinned:
        print(f"\n📌 {len(pinned)} animal(s) the DEPLOYED patch already covers but that are no "
              f"longer in cast_assignment.csv will be PINNED to their current live value, not "
              f"dropped (ANIMAL_TOLERANCES_JOIN_BROKEN_1) — a regenerate must never narrow an "
              f"animal by omission.")
    if gone:
        print(f"ℹ️  {len(gone)} deployed defName(s) are no longer any def at all and are safe "
              f"to drop (the patch would already no-op on them): "
              + ', '.join(gone[:6]) + ('…' if len(gone) > 6 else ''))
    all_rows = rows + pinned

    if '--write' not in sys.argv:
        print("\n(pass --write to emit the patch)")
        return 0
    print(f"\nwrote {emit(all_rows)}  ({len(all_rows)} operations = {len(rows)} refitted/kept + "
          f"{len(pinned)} pinned)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
