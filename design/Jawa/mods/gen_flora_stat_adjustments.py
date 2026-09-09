#!/usr/bin/env python3
"""gen_flora_stat_adjustments.py - every roster `flora_stat_adjustments` row, one patch.

SOURCE    design/Jawa/worldbuilding/biomes/rosters/*.json, key `flora_stat_adjustments`
AUTHORITY BIOME_FAUNA_ASSIGNMENT_SITTING_1, 2026-09-09 fix wave. The plant sibling of
          `design/Jawa/fauna/gen_stat_adjustments.py`, and it exists for the same reason:
          a sheet's admission test failed on ONE number, and the honest fix is to move the
          number rather than evict a plant the biome needs. Two causes so far -

            ban 9 (arid shrubland)  every one of the 10 landed flora burns. MEASURED off
                                    resolved statBases, not guessed - plants inherit
                                    Flammability from abstract PlantBase parents, so raw
                                    mod XML cannot be grepped for it. No Flammability-0
                                    donor fits the sheet's low-shrub/fuzz law (only 32 of
                                    647 pool defs are non-flammable, and every one is a
                                    fungus, a fire/anima form or an Earth-nameable cactus),
                                    so the stand-ins stay and stop burning.
            donor bug (the Rot)     BMT_GreyLady ships Flammability 40. The pool's
                                    next-highest is 1.5. That is a typo upstream, clamped.

    python3 design/Jawa/mods/gen_flora_stat_adjustments.py          # print what it would write
    python3 design/Jawa/mods/gen_flora_stat_adjustments.py --write  # write the patch

🔴 THE FIELD NAMES ARE TRANSLATED, NEVER GUESSED. A roster says `flammability` because
that is the human word; the DEF spells it `statBases/Flammability`. An unknown field name
is a hard stop - inventing an xpath would emit an operation that matches nothing, and a
patch that matches nothing logs nothing.

⚠️ NOT match-only, and that is the difference from the fauna generator. Flammability is
INHERITED from PlantBase on most of these defs, so the node usually does not exist in the
def's own XML and a match-only conditional would be a silent no-op - the exact failure this
patch is fixing. So each operation is nested: statBases present? -> Flammability present?
-> Replace, else Add into statBases; no statBases at all -> Add the whole block. That is
the same shape `plant_tolerances.py` uses, for the same reason.

⛔ PER-DEF STATS ARE GLOBAL. Zeroing Plant_Bush's Flammability changes it everywhere, not
only in the arid shrubland. Accepted because every def touched here is single-biome on the
landed planet (MEASURED via review/rosters_residency.py) - re-check that before adding a
row for a def with two homes.
"""
import argparse
import glob
import json
import os
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
ROSTERS = os.path.join(ROOT, 'design', 'Jawa', 'worldbuilding', 'biomes', 'rosters')
OUT = os.path.join(ROOT, 'src', 'RimUtinni', 'UtinniPatches', 'Patches',
                   'BiomeFloraStatAdjustments_Generated.xml')

# roster field name -> (parent node under ThingDef, node name)
FIELDS = {
    'flammability': ('statBases', 'Flammability'),
}


def rows():
    out = []
    for fp in sorted(glob.glob(os.path.join(ROSTERS, '*.json'))):
        name = os.path.basename(fp)
        if name.startswith('_'):
            continue
        with open(fp, encoding='utf-8') as fh:
            d = json.load(fh)
        for s in d.get('flora_stat_adjustments') or []:
            out.append((d.get('sheet') or name[:-5], s))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args(argv)

    rs = rows()
    unknown = sorted({s['field'] for _, s in rs if s['field'] not in FIELDS})
    if unknown:
        print('🔴 STOP - roster field(s) with no known def xpath: ' + ', '.join(unknown)
              + '\n   Add them to FIELDS after reading the def, or the operation would '
                'match nothing and report nothing.')
        return 1

    seen = {}
    for sheet, s in rs:
        key = (s['def'], s['field'])
        if key in seen and seen[key][1]['to'] != s['to']:
            print(f'🔴 STOP - {s["def"]}.{s["field"]} is adjusted to two different values '
                  f'({seen[key][0]}: {seen[key][1]["to"]}, {sheet}: {s["to"]}). '
                  f'Fix the rosters; do not pick one here.')
            return 1
        seen.setdefault(key, (sheet, s))

    o = ['<?xml version="1.0" encoding="utf-8"?>',
         '<!--',
         '  ==========================================================================',
         '  BiomeFloraStatAdjustments_Generated.xml   GENERATED - do not hand-edit',
         '  ==========================================================================',
         '  Regenerate: python3 design/Jawa/mods/gen_flora_stat_adjustments.py, flag `write`',
         '  (⛔ the flag is spelled with two hyphens, which XML forbids inside a comment.)',
         '',
         '  SOURCE     design/Jawa/worldbuilding/biomes/rosters/*.json,',
         '             key `flora_stat_adjustments`.',
         '  AUTHORITY  BIOME_FAUNA_ASSIGNMENT_SITTING_1, 2026-09-09 FIX WAVE. Two findings',
         '             from the flora portfolio (figF3) are answered here:',
         '',
         '             BAN 9, arid shrubland (arid_shrubland.md §6, frozen): "No flammable',
         '             living flora. The native plants resist fire greatly and burn only',
         '             grudgingly." All 10 landed flora rows burn - 10/10 violation,',
         '             MEASURED off resolved statBases (plants inherit Flammability from',
         '             abstract PlantBase parents, so raw mod XML cannot be grepped for it).',
         '             Every one of the 10 was re-checked against the pool for a',
         '             Flammability-0 alien donor fitting the sheet\'s low-shrub/fuzz law;',
         '             none exists (32 of 647 pool defs are non-flammable and every one is a',
         '             fungus, a fire/anima form or an Earth-nameable cactus, most already',
         '             bound to another flora family). So the interim stand-ins are KEPT and',
         '             stop burning. The sheet\'s own designed flora - the fuzz, venomvine -',
         '             is non-flammable by design; this patch retires when they land.',
         '',
         '             DONOR BUG, the Rot: BMT_GreyLady ships Flammability 40, against a',
         '             whole-pool maximum of 1.5. Clamped, not zeroed - it is an ordinary',
         '             living fungus, and the Rot has no flammability ban.',
         '',
         f'  {len(seen)} adjustment(s) across {len({d for d, _f in seen})} def(s).',
         '',
         '  ⚠️ NESTED conditionals, NOT match-only. Flammability is inherited from PlantBase',
         '  on most of these defs, so the node is absent from the def\'s own XML and a',
         '  match-only Replace would be a silent no-op - the very failure being fixed. Each',
         '  operation therefore tests statBases, then Flammability, and Adds where either is',
         '  missing. Load this mod LAST.',
         '',
         '  ⛔ PER-DEF STATS ARE GLOBAL: every def below is single-biome on the landed planet',
         '  (MEASURED, review/rosters_residency.py). Re-check that before adding a row.',
         '-->',
         '<Patch>']

    for (dn, field), (sheet, s) in sorted(seen.items()):
        parent, node = FIELDS[field]
        base = f'/Defs/ThingDef[defName="{dn}"]'
        val = f'{s["to"]:g}' if isinstance(s['to'], (int, float)) else str(s['to'])
        frm = s.get('from')
        frm = f'{frm:g}' if isinstance(frm, (int, float)) else str(frm)
        o += ['',
              f'  <!-- {dn}.{field}: {frm} -> {val}   ({sheet}.json)']
        for line in textwrap.wrap(' '.join((s.get('authority') or '').split()), 90):
            o.append(f'       {line}')
        o += ['  -->',
              '  <Operation Class="PatchOperationConditional">',
              f'    <xpath>{base}/{parent}</xpath>',
              '    <match Class="PatchOperationConditional">',
              f'      <xpath>{base}/{parent}/{node}</xpath>',
              '      <match Class="PatchOperationReplace">',
              f'        <xpath>{base}/{parent}/{node}</xpath>',
              f'        <value><{node}>{val}</{node}></value>',
              '      </match>',
              '      <nomatch Class="PatchOperationAdd">',
              f'        <xpath>{base}/{parent}</xpath>',
              f'        <value><{node}>{val}</{node}></value>',
              '      </nomatch>',
              '    </match>',
              '    <nomatch Class="PatchOperationAdd">',
              f'      <xpath>{base}</xpath>',
              f'      <value><{parent}><{node}>{val}</{node}></{parent}></value>',
              '    </nomatch>',
              '  </Operation>']
    o += ['', '</Patch>', '']

    for (dn, field), (sheet, s) in sorted(seen.items()):
        print(f'  {dn:26s} {field:14s} {s.get("from")} -> {s["to"]}   ({sheet})')
    if not a.write:
        print(f'\n({len(seen)} adjustment(s); pass --write to emit {OUT})')
        return 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(o))
    print(f'\nwrote {OUT}: {len(seen)} operation(s)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
