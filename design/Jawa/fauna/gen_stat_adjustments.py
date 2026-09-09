#!/usr/bin/env python3
"""gen_stat_adjustments.py - every roster `stat_adjustments` row, as one patch file.

SOURCE   design/Jawa/worldbuilding/biomes/rosters/*.json, key `stat_adjustments`
AUTHORITY owner cards 2026-09-09 (BIOME_FAUNA_ASSIGNMENT_SITTING_1): "SW staples:
          adjust-and-keep". An icon that fails a sheet's law is not evicted, it is
          adjusted until it passes - so the eviction the sheet demanded becomes a
          stat edit here instead, and the roster row carries the argument.

    python3 design/Jawa/fauna/gen_stat_adjustments.py          # print what it would write
    python3 design/Jawa/fauna/gen_stat_adjustments.py --write  # write the patch

🔴 THE FIELD NAMES ARE TRANSLATED, NEVER GUESSED. A roster says `moveSpeed` because
that is what creature_register_rows.json calls the number; the DEF spells it
`statBases/MoveSpeed`, and `predator` lives under `race`. An unknown field name is a
hard stop - inventing an xpath for it would emit an operation that matches nothing,
and a patch that matches nothing logs nothing.

⚠️ MATCH-ONLY, DELIBERATELY. Every operation is a PatchOperationConditional whose
<match> replaces the node, with NO <nomatch>. Beldon is why: it carries
`race.predator = true` in the live dump but no <predator> node in its own mod XML
(mlie.starwarsanimalcollection) - another mod's PatchOperation puts it there. An Add
in <nomatch> would race that patch and could leave TWO predator nodes. A no-op is
visible (validate_patch --defs prints 0 nodes) and harmless; a duplicated field is
neither. Our mod loads last, so by the time these run the node is there.
"""
import argparse
import glob
import json
import os
import sys

FA = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(FA, '..', '..', '..'))
ROSTERS = os.path.join(ROOT, 'design', 'Jawa', 'worldbuilding', 'biomes', 'rosters')
OUT = os.path.join(ROOT, 'src', 'RimUtinni', 'UtinniPatches', 'Patches',
                   'BiomeFaunaStatAdjustments_Generated.xml')

# roster field name -> (xpath tail below /Defs/ThingDef[defName="X"], node name)
FIELDS = {
    'moveSpeed': ('statBases/MoveSpeed', 'MoveSpeed'),
    'predator': ('race/predator', 'predator'),
}


def _xml_value(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    return str(v)


def rows():
    out = []
    for fp in sorted(glob.glob(os.path.join(ROSTERS, '*.json'))):
        name = os.path.basename(fp)
        if name.startswith('_'):
            continue
        with open(fp, encoding='utf-8') as fh:
            d = json.load(fh)
        for s in d.get('stat_adjustments') or []:
            out.append((d.get('sheet') or name[:-5], s))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args(argv)

    rs = rows()
    unknown = sorted({s['field'] for _, s in rs if s['field'] not in FIELDS})
    if unknown:
        print('🔴 STOP - roster field(s) with no known def xpath: '
              + ', '.join(unknown)
              + '\n   Add them to FIELDS after reading the def, or the operation would '
                'match nothing and report nothing.')
        return 1

    # One def may be adjusted by two rosters; the same field twice is a contradiction
    # the rosters must resolve, not this script.
    seen = {}
    for sheet, s in rs:
        key = (s['def'], s['field'])
        if key in seen and seen[key][1]['to'] != s['to']:
            print(f'🔴 STOP - {s["def"]}.{s["field"]} is adjusted to two different values '
                  f'({seen[key][0]}: {seen[key][1]["to"]}, {sheet}: {s["to"]}). '
                  f'Fix the rosters; do not pick one here.')
            return 1
        seen.setdefault(key, (sheet, s))

    out = ['<?xml version="1.0" encoding="utf-8"?>',
           '<!--',
           '  ==========================================================================',
           '  BiomeFaunaStatAdjustments_Generated.xml    GENERATED - do not hand-edit',
           '  ==========================================================================',
           '  Regenerate:  python3 design/Jawa/fauna/gen_stat_adjustments.py, flag `write`',
           '  (⛔ the flag is spelled with two hyphens, which XML forbids inside a comment.)',
           '',
           '  SOURCE     design/Jawa/worldbuilding/biomes/rosters/*.json, `stat_adjustments`.',
           '  AUTHORITY  owner cards 2026-09-09, BIOME_FAUNA_ASSIGNMENT_SITTING_1:',
           '             "SW staples: adjust-and-keep - icons survive by fitting the law."',
           '             Every row below exists because a biome sheet\'s admission test',
           '             failed on one number, and the owner ruled the icon stays and the',
           '             number moves. The roster row carries the full argument; the',
           '             comment on each operation carries its head.',
           '',
           f'  {len(seen)} adjustment(s) across {len({d for d, _f in seen})} def(s).',
           '',
           '  ⚠️ Match-only conditionals, no <nomatch>. Beldon carries race.predator=true',
           '  in the live dump but has no <predator> node in its own mod XML - another',
           '  mod patches it in - so an Add here could race that patch and leave two',
           '  nodes. A no-op is visible to validate_patch and harmless; a duplicate is',
           '  neither. Load this mod LAST.',
           '-->',
           '<Patch>']

    for (dn, field), (sheet, s) in sorted(seen.items()):
        tail, node = FIELDS[field]
        xp = f'/Defs/ThingDef[defName="{dn}"]/{tail}'
        auth = ' '.join((s.get('authority') or '').split())
        out += ['',
                f'  <!-- {dn}.{field}: {_xml_value(s.get("from"))} -> {_xml_value(s["to"])}'
                f'   ({sheet}.json)',
                f'       {auth} -->',
                '  <Operation Class="PatchOperationConditional">',
                f'    <xpath>{xp}</xpath>',
                '    <match Class="PatchOperationReplace">',
                f'      <xpath>{xp}</xpath>',
                f'      <value><{node}>{_xml_value(s["to"])}</{node}></value>',
                '    </match>',
                '  </Operation>']
    out += ['', '</Patch>', '']

    for (dn, field), (sheet, s) in sorted(seen.items()):
        print(f'  {dn:24s} {field:12s} {_xml_value(s.get("from")):>6s} -> '
              f'{_xml_value(s["to"]):<6s} ({sheet})')
    if not a.write:
        print(f'\n({len(seen)} adjustment(s); pass --write to emit {OUT})')
        return 0
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(out))
    print(f'\nwrote {OUT}: {len(seen)} operation(s)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
