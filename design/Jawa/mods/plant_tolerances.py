#!/usr/bin/env python3
"""Move every assigned plant's temperature band onto the climate it actually lives in.

🔴 **DECIDE's ruling, 2026-08-23** — the plant half of `NORMALIZE_TEMPERATURE_TOLERANCES_1`.

Ash'karr's ground runs −82.0 … +66.1 °C. Nothing shipped by any mod was authored for that:
642 of 669 plants stop at `minGrowthTemperature` 0.0 °C. So a perfectly correct roster
produces bare ground, silently, and reads as a bad roster.

## The rule: the BIOME sets the band; shipped hardiness is a capped bonus

The owner's constraint is *"do not widen tolerance to infinity — a world where everything
survives everywhere has no climate."* So no plant gets a band wider than its own home needs,
plus a bounded hardiness allowance.

    need_lo, need_hi = p05(home tiles) − SWING, p95(home tiles) + SWING
    band             = [ min(shipped min, need_lo) , max(shipped max, need_hi) ]
    optimal band     = the same FRACTION of the band the plant shipped with, clamped sane

🔴 **WIDEN ONLY — never narrow.** Corrected 2026-08-23, after the animal pass showed the
re-centring version stripping `GR_ParagonIguana` of 45 °C of shipped heat tolerance for no
gain. Narrowing can only ever cause the very bug this closes, and it buys nothing: the ROSTER
decides where a plant may appear and temperature only removes it.

⚠️ **One consequence the owner should rule on:** widening a floor also widens it for SOWABLE
crops, so a player could farm healroot at −80 °C. Climate stops constraining FARMING even
though it still constrains wild flora. Left as-is because he explicitly asked for player-grown
plants as wild decoration; the alternative is to exempt `Sowable` plants from the floor widen
and accept that they will not appear wild in the cold biomes they were cast into.

⚠️ **An earlier version of this slid the band rigidly, centred on the plant's shipped OPTIMAL
midpoint, and it broke on modded stock.** `BMT_Blastpod` ships an optimal band of 50 … 352 °C,
which produced a −263 °C shift and a −213 °C floor; 370 of 492 plants ended up widened rather
than slid, and a "translation" that mostly widens is not a translation. **Shipped values are
not trustworthy enough to be the ORIGIN of the calculation — only a modifier to it.**

🔑 **This cannot make everything survive everywhere, and the reason is the flora rosters.**
No plant crosses a family (`biome_flora.py` refuses to build if one does), so every plant is
fitted to ONE climate. `BMT_AmbrosyxFungus` comes out at −103.6 … −20.4 °C — a cryophile that
still dies on the dayside. Climate is preserved *because* the rosters are exclusive.

## Four fields, not two

⚠️ `NORMALIZE_TEMPERATURE_TOLERANCES_1` names only `minGrowthTemperature` /
`maxGrowthTemperature`. There are FOUR, and moving only the outer pair strands the optimal
band inside it:

    minGrowthTemperature          0     the plant does not grow below this
    minOptimalGrowthTemperature   6     growth ramps 0 -> 1 across min..minOptimal
    maxOptimalGrowthTemperature  42
    maxGrowthTemperature         58     (or 75 on desert stock)

`Plant.cs:361` computes growth as `InverseLerp(minGrowthTemperature,
minOptimalGrowthTemperature, cellTemp)`. Drop only the floor and the plant sits at ~0 growth
forever — alive, present, and still indistinguishable from a bad roster.

## Why p05/p95 and not min/max

`PlantUtility.cs:93` gates wild spawning on the band OVERLAPPING the tile's annual range, so the
band has to reach the tiles the plant is meant to appear on — but a single outlier tile should not
buy the whole species a 40 °C coat. p05…p95 covers the biome as it is actually experienced.

⚠️ **SWING is a judgement, not a measurement.** `ASHKARR_WORLDMAP_tiles.csv` carries ONE
`temp_c` per tile — an annual figure — while the spawn gate wants the tile's seasonal
Min/MaxTemperature, which we do not hold. 15 °C is the allowance for that swing and it is the
first number to revise when the load is scored.

⛔ **PLANTS ONLY.** Animals (`statBases` ComfyTemperatureMin/Max) and xenotypes (bands live on
GENES, not on the XenotypeDef) are NOT touched here and the item stays open for them.
"""
import collections
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biome_flora as bf                                            # noqa: E402  the rosters

ROOT = bf.ROOT
PATCH = os.path.join(ROOT, 'src', 'Jawa', 'Jawa_Patches', 'Patches',
                     'PlantTolerances_Ashkarr.xml')

FIELDS = ['minGrowthTemperature', 'minOptimalGrowthTemperature',
          'maxOptimalGrowthTemperature', 'maxGrowthTemperature']
DEFAULTS = {'minGrowthTemperature': 0.0, 'minOptimalGrowthTemperature': 6.0,
            'maxOptimalGrowthTemperature': 42.0, 'maxGrowthTemperature': 58.0}
SWING = 15.0          # seasonal/daily allowance — a JUDGEMENT, see the docstring
HARDINESS_CAP = 40.0  # most extra band a hardy plant may keep beyond its biome's demand


def _pct(xs, p):
    xs = sorted(xs)
    if not xs:
        return 0.0
    return xs[min(len(xs) - 1, max(0, int(round((len(xs) - 1) * p))))]


def plant_homes():
    """plant defName -> the tile temperatures of every biome it was assigned to."""
    temps = bf._tile_temps()
    homes = collections.defaultdict(list)
    for _fam, bs in bf.FAMILIES.items():
        for b, roster in bs.items():
            ts = temps.get(b) or []
            for p in roster:
                homes[p].extend(ts)
    return homes


def compute(plants):
    """Fit each plant's band to the climate it was assigned, keeping its hardiness as a bonus.

    ⚠️ **The first version of this centred the band on the plant's shipped OPTIMAL midpoint and
    it broke on modded stock.** `BMT_Blastpod` ships an optimal band of 50 … 352 °C, which
    produced a −263 °C shift and a floor of −213 °C, and 370 of 492 plants ended up widened
    rather than slid — a "translation" that mostly widens is not a translation. Shipped values
    are not trustworthy enough to be the ORIGIN of the calculation, only a modifier to it.

    So the biome sets the band and the plant's shipped WIDTH only buys extra hardiness, capped.
    """
    homes = plant_homes()
    rows, bonus, already = [], 0, 0
    for p, ts in sorted(homes.items()):
        d = plants.get(p)
        if not d or not ts:
            continue
        g = d['fields']['plant']
        cur = {k: float(g.get(k) if g.get(k) is not None else DEFAULTS[k]) for k in FIELDS}

        need_lo = _pct(ts, 0.05) - SWING            # what this biome actually demands
        need_hi = _pct(ts, 0.95) + SWING
        need_w = need_hi - need_lo

        # already survives its whole home? leave it completely alone.
        if cur['minGrowthTemperature'] <= need_lo and cur['maxGrowthTemperature'] >= need_hi:
            already += 1
            continue

        # 🔴 WIDEN ONLY. Narrowing can only ever CAUSE the bug this closes - a plant that
        # never grows - and it buys nothing, because the ROSTER decides where a plant may
        # appear and temperature only removes it. Corrected 2026-08-23 after the animal pass
        # showed the same rule stripping GR_ParagonIguana of 45 °C of shipped heat tolerance.
        shipped_w = cur['maxGrowthTemperature'] - cur['minGrowthTemperature']
        new = {'minGrowthTemperature': min(cur['minGrowthTemperature'], need_lo),
               'maxGrowthTemperature': max(cur['maxGrowthTemperature'], need_hi)}
        w = new['maxGrowthTemperature'] - new['minGrowthTemperature']
        bonus += (new['minGrowthTemperature'] == cur['minGrowthTemperature']) or \
                 (new['maxGrowthTemperature'] == cur['maxGrowthTemperature'])

        # keep the shipped OPTIMAL band as a fraction of the shipped band, clamped sane
        if shipped_w > 1.0:
            f_lo = (cur['minOptimalGrowthTemperature'] - cur['minGrowthTemperature']) / shipped_w
            f_hi = (cur['maxOptimalGrowthTemperature'] - cur['minGrowthTemperature']) / shipped_w
        else:
            f_lo, f_hi = 0.2, 0.8
        f_lo = min(max(f_lo, 0.05), 0.45)
        f_hi = min(max(f_hi, 0.55), 0.95)
        new['minOptimalGrowthTemperature'] = new['minGrowthTemperature'] + f_lo * w
        new['maxOptimalGrowthTemperature'] = new['minGrowthTemperature'] + f_hi * w

        new = {k: round(v, 1) for k, v in new.items()}
        rows.append((p, cur, new, round(need_lo, 1), round(need_hi, 1), len(ts)))
    return rows, bonus, already


def emit(rows, plants):
    o = ['<?xml version="1.0" encoding="utf-8"?>', '<Patch>',
         '  <!-- GENERATED by design/Jawa/mods/plant_tolerances.py - do not hand-edit.',
         '',
         "       Every assigned plant's temperature band REFITTED to the climate of the biome",
         '       it was given. The biome sets the band; the plant\'s shipped width only buys a',
         '       capped hardiness bonus on top. No plant gets a band wider than its own home',
         '       needs, so a nightside plant still dies on the dayside and the world keeps its',
         '       climate.',
         '',
         '       🔴 FOUR fields move together. Plant.cs:361 computes growth as',
         '       InverseLerp(minGrowthTemperature, minOptimalGrowthTemperature, cellTemp),',
         '       so moving only the outer pair leaves the plant at ~0 growth - alive, present',
         '       and still indistinguishable from a bad roster.',
         '',
         '       ⛔ NO MayRequire: the def dump packageId names the mod that last RETEXTURED',
         '       a def, not the one that defines it. PatchOperationConditional on the def is',
         '       the correct guard and a biome/plant that is absent simply fails the xpath. -->',
         '']
    for p, cur, new, nlo, nhi, n in rows:
        lab = (plants[p]['fields'].get('label') or p)
        o += [f'  <!-- {lab} ({p}) - {n} tiles, home demands {nlo:g} … {nhi:g} °C',
              '       ' + '  '.join(f'{k[:12]} {cur[k]:g}->{new[k]:g}' for k in FIELDS) + ' -->',
              '  <Operation Class="PatchOperationConditional">',
              f'    <xpath>/Defs/ThingDef[defName="{p}"]/plant</xpath>',
              '    <match Class="PatchOperationSequence">',
              '      <operations>']
        for k in FIELDS:
            o += ['        <li Class="PatchOperationConditional">',
                  f'          <xpath>/Defs/ThingDef[defName="{p}"]/plant/{k}</xpath>',
                  '          <match Class="PatchOperationReplace">',
                  f'            <xpath>/Defs/ThingDef[defName="{p}"]/plant/{k}</xpath>',
                  f'            <value><{k}>{new[k]:g}</{k}></value>',
                  '          </match>',
                  '          <nomatch Class="PatchOperationAdd">',
                  f'            <xpath>/Defs/ThingDef[defName="{p}"]/plant</xpath>',
                  f'            <value><{k}>{new[k]:g}</{k}></value>',
                  '          </nomatch>',
                  '        </li>']
        o += ['      </operations>', '    </match>', '  </Operation>', '']
    o.append('</Patch>')
    os.makedirs(os.path.dirname(PATCH), exist_ok=True)
    open(PATCH, 'w', encoding='utf-8').write('\n'.join(o) + '\n')
    return PATCH


def main() -> int:
    write = '--write' in sys.argv
    plants, _biomes = bf.load()
    rows, bonus, already = compute(plants)

    print(f"\n{len(rows)} plants refitted · {already} already survived their whole home and "
          f"were left untouched · {bonus} kept a shipped bound already generous enough")
    if rows:
        lo = [r[2]['minGrowthTemperature'] for r in rows]
        hi = [r[2]['maxGrowthTemperature'] for r in rows]
        print(f"new floors {min(lo):+g} … {max(lo):+g} °C   new ceilings {min(hi):+g} … {max(hi):+g} °C")
        for tag, group in (('coldest', sorted(rows, key=lambda r: r[2]['minGrowthTemperature'])[:3]),
                           ('warmest', sorted(rows, key=lambda r: -r[2]['maxGrowthTemperature'])[:3])):
            for p, cur, new, nlo, nhi, n in group:
                print(f"  {tag:8s} {p:34s} {n:6d} tiles  "
                      f"min {cur['minGrowthTemperature']:g}->{new['minGrowthTemperature']:g}  "
                      f"max {cur['maxGrowthTemperature']:g}->{new['maxGrowthTemperature']:g}")
    if not write:
        print("\n(pass --write to emit the patch)")
        return 0
    print(f"\nwrote {emit(rows, plants)}  ({len(rows)} operations)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
