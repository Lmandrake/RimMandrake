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

⛔ **This assumes `BiomeCast_Ashkarr.xml` SHIPS.** The bands are fitted to the biome each
creature is cast into, so if the cast does not deploy, the shipped `wildAnimals` lists put
these animals somewhere else and the fitted bands are wrong for it. The cast is
`BIOME_CAST_APPLY_1`, in flight with BUILD. **Deploy both or neither.**
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
PATCH = os.path.join(ROOT, 'src', 'Jawa', 'Jawa_Patches', 'Patches',
                     'AnimalTolerances_Ashkarr.xml')

MIN, MAX = 'ComfyTemperatureMin', 'ComfyTemperatureMax'
DEFAULTS = {MIN: 0.0, MAX: 40.0}      # StatDef defaultBaseValue, read from Core
SWING = 15.0                          # seasonal allowance — a JUDGEMENT, as in the plant pass
EPSILON = 1.0                         # the gate is a STRICT inequality


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
    for r in csv.DictReader(open(CAST, encoding='utf-8')):
        ts = temps.get(r['biome']) or []
        if ts:
            h[r['defName']].extend(ts)
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
         '       ⛔ Assumes BiomeCast_Ashkarr.xml ships. Deploy both or neither. -->', '']
    for a, cur, new, nlo, nhi, n, lab in rows:
        o += [f'  <!-- {lab} ({a}) - {n} tiles, home demands {nlo:g} … {nhi:g} °C  '
              f'{cur[MIN]:g}..{cur[MAX]:g} -> {new[MIN]:g}..{new[MAX]:g} -->',
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
    if '--write' not in sys.argv:
        print("\n(pass --write to emit the patch)")
        return 0
    print(f"\nwrote {emit(rows)}  ({len(rows)} operations)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
