#!/usr/bin/env python3
"""rosters_to_cast.py - regenerate cast_assignment.csv FROM the landed biome rosters.

🔑 THE INPUT LAW CHANGED. cast_assignment.csv used to be produced by allocate_cast.py /
refill_cast.py - a SCORING model over wildlife.csv (belong/standout/defence) that picked
a pyramid per biome. Since BIOME_FAUNA_ASSIGNMENT_SITTING_1 (owner cards 2026-09-09) the
cast is AUTHORED, not scored: design/Jawa/worldbuilding/biomes/rosters/*.json is the
source, every row citing the sheet law it passed. This script is the bridge from those
rosters to the CSV CONTRACT gen_cast_patch.py defines (columns, PawnKindDef check,
Cherry Picker cuts, Anomaly entities, MayRequire donor gating, the <li> trap) - that
contract is kept exactly as it is, even though gen_cast_patch.py itself now REFUSES to
consume it (see below).

⛔ Do NOT hand-edit cast_assignment.csv, and do NOT edit the roster JSONs to make this
script happy. If a roster is wrong, stop and say so - the rosters are the owner-facing
design record; this file is derived.

WHICH BIOMES THIS WRITES
    The biomes BiomeCast_Ashkarr.xml used to own wildAnimals for, before that file was
    confirmed fully dead and deleted (BIOME_CAST_PATCH_DEAD_NAMES_1). BIOMECAST_DEFS is
    kept as a LIVE-defName set - rebuilt from biome_name_migration.py's OLD_TO_NEW_BIOME
    (ROSTERS_TO_CAST_BIOMECAST_DEFS_STALE_1) - purely so this script's output stays
    correct for the OTHER consumers of cast_assignment.csv (animal_tolerances.py,
    gen_creature_art_sheet.py, gen_creature_size_sheet.py, gen_name_patch.py), NOT
    because gen_cast_patch.py is expected to consume it again.
    🔴 MEASURED 2026-09-20: every one of those biomes' own BiomeDef XML under
    src/RimUtinni/UtinniPatches/Defs/BiomeDefs/ already declares <wildAnimals> natively
    (transplanted from BiomeCast_Ashkarr.xml at authoring time, 2026-09-09) - ownership
    fully moved to the def files, and gen_cast_patch.py's own refusal guard now checks
    that directly rather than relying on the old biome names never painting a tile.
    ZBiome_Grasslands (never renamed, a donor biome with no RUT_ def of its own) is the
    one exception with no other declared owner today; re-enabling gen_cast_patch.py for
    it alone is unassessed future work, not something this fix does.
    The RUT_-tier defs whose wildAnimals BIOMECAST_DEFS never claimed (RUT_BlueDesert,
    RUT_GreySea, RUT_NightsideIce, RUT_PropaneLake, RUT_TheScald, RUT_TwilightSea) and
    BiomeGRimond (no local override at all) stay deliberately absent here.

INJECTION LAYERS
    A roster whose sheet is an injection layer (fall_line, wreck_fields - rosters/_SCHEMA.md)
    lists the UNDERLYING defs in `defNames`, and its fauna rows are ADDITIONS onto each of
    them, not a replacement. A def named by both its own sheet roster and an injection
    layer keeps the base roster's commonality; the collision is reported, never silent.

THE CSV CONTRACT, read out of gen_cast_patch.py rather than guessed
    biome      the BiomeDef defName - one XML operation per distinct value
    defName    must be a PawnKindDef or the generator emits a SKIPPED comment
    commonality  emitted verbatim as the node TEXT (<Bantha>0.8</Bantha>)
    band, status  appear only in the trailing XML comment ("{band}, {status}")
    label      the same comment
    mod, bodySize, belong, standout, defence, reason, promoted
               untouched by gen_cast_patch.py; carried so the sibling scripts that
               still read this file (biome_fit.py, gen_creature_size_sheet.py,
               refill_cast.py, gen_creature_art_sheet.py) keep their columns.
               belong/standout are SCORES the roster pass does not produce and are
               written empty rather than faked - a number nobody computed is worse
               than a blank.
"""
import collections
import csv
import glob
import json
import os
import sys

FA = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(FA, '..', '..', '..'))
ROSTERS = os.path.join(ROOT, 'design', 'Jawa', 'worldbuilding', 'biomes', 'rosters')
WILDLIFE = os.path.join(FA, 'wildlife.csv')
REGISTER = os.path.join(ROOT, 'design', 'Jawa', 'worldbuilding', 'review',
                        'creature_register_rows.json')
OUT = os.path.join(FA, 'cast_assignment.csv')

sys.path.insert(0, FA)
from biome_name_migration import OLD_TO_NEW_BIOME                    # noqa: E402

COLUMNS = ['biome', 'defName', 'label', 'mod', 'band', 'bodySize', 'commonality',
           'belong', 'standout', 'defence', 'status', 'reason', 'promoted']

# The defs BiomeCast_Ashkarr.xml owned, keyed to their LIVE defNames. Originally sourced
# from design/Jawa/worldbuilding/biomes/_def_bindings_2026-09-09.md §1 ("wildAnimals
# owner"), which established the table by two-step grep, not by name similarity - but that
# doc, and this set, still named the 23 PRE-MIGRATION biome defNames `BIOME_OWNERSHIP_WAVE_1`
# (2026-09-09) replaced with `RUT_`-prefixed BiomeDefs, while the roster JSONs this script
# reads were already re-authored with the live names — so `b in BIOMECAST_DEFS` was false
# for nearly every roster row and almost the whole cast silently routed to `offowner`
# (`ROSTERS_TO_CAST_BIOMECAST_DEFS_STALE_1`, MEASURED: 62 rows across 5 biomes, versus
# hundreds sitting in the rosters). Rebuilt here via `biome_name_migration.py`'s
# `OLD_TO_NEW_BIOME` (the same table `animal_tolerances.py` uses) rather than by
# name-guessing a second time. `AB_PyroclasticConflagration`, `LavaField` and `Volcano`
# all resolve to the single live biome `RUT_TheForge`, so the 22 pre-migration keys with a
# rename collapse to 20 live names; `ZBiome_Grasslands` was never renamed and is added back
# unchanged, for 21 live biome defNames total (a real drop from 23, entirely the 3-into-1
# TheForge merge — not a loss of coverage).
# ⚠️ Adding a def here without also confirming nothing else declares its wildAnimals
# means two owners for one list and the later loader wins silently.
BIOMECAST_DEFS = set(OLD_TO_NEW_BIOME.values()) | {'ZBiome_Grasslands'}

# Sheets that INJECT onto defs they do not own (rosters/_SCHEMA.md).
INJECTION_SHEETS = {'fall_line', 'wreck_fields', 'the_lantern_deeps'}


def _facts():
    """defName -> {label, mod, bodySize, status, defence}, wildlife.csv then the register.

    Two sources because neither is complete: wildlife.csv is the cast pipeline's own
    per-def table and carries `status`/`defence`, but it predates the RimStarWars sea
    beasts; creature_register_rows.json carries those. A def in neither is emitted with
    its defName as the label rather than dropped - gen_cast_patch.py's PawnKindDef gate
    is the check that matters, and a missing LABEL only degrades a comment.
    """
    out = {}
    with open(WILDLIFE, encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            out[r['defName']] = {'label': r['label'], 'mod': r['mod'],
                                 'bodySize': r['bodySize'], 'status': r['status'],
                                 'defence': r['defence']}
    with open(REGISTER, encoding='utf-8') as fh:
        for r in json.load(fh)['rows']:
            dn = r.get('defName')
            if not dn or dn in out:
                continue
            out[dn] = {'label': r.get('label') or dn, 'mod': r.get('mod') or '',
                       'bodySize': r.get('bodySize') if r.get('bodySize') is not None else '',
                       'status': '', 'defence': ''}
    return out


def load_rosters():
    """[(sheet, defNames, [fauna row])] for every roster file, `_`-prefixed excluded."""
    out = []
    for fp in sorted(glob.glob(os.path.join(ROSTERS, '*.json'))):
        name = os.path.basename(fp)
        if name.startswith('_'):
            continue
        with open(fp, encoding='utf-8') as fh:
            d = json.load(fh)
        out.append((d.get('sheet') or name[:-5], d.get('defNames') or [],
                    d.get('fauna') or []))
    return out


def build_rows():
    facts = _facts()
    # biome -> defName -> (row, sheet). dict keeps the base roster's row on a collision.
    cast = collections.defaultdict(dict)
    collisions, unbound, offowner = [], [], collections.Counter()

    for pas in (0, 1):                       # base sheets first, injections second
        for sheet, defnames, fauna in load_rosters():
            if (sheet in INJECTION_SHEETS) != bool(pas):
                continue
            if not fauna:
                continue
            if not defnames:
                unbound.append(sheet)
                continue
            for b_raw in defnames:
                # A roster is allowed to still name a pre-migration biome on purpose -
                # `fall_line.json` and `the_lantern_deeps.json` do, deliberately targeting
                # an OLD defName that BIOMECAST_DEFS no longer carries now it is keyed to
                # live names (ROSTERS_TO_CAST_BIOMECAST_DEFS_STALE_1). Resolve through the
                # same shared table before the ownership check, so those rows land on the
                # live biome instead of silently falling to offowner.
                b = OLD_TO_NEW_BIOME.get(b_raw, b_raw)
                if b not in BIOMECAST_DEFS:
                    offowner[b_raw] += len(fauna)
                    continue
                for f in fauna:
                    dn = f['def']
                    if dn in cast[b]:
                        collisions.append((b, dn, cast[b][dn][1], sheet))
                        continue
                    cast[b][dn] = (f, sheet)

    rows = []
    for b in sorted(cast):
        for f, sheet in sorted(cast[b].values(),
                               key=lambda t: (-float(t[0]['commonality']), t[0]['def'])):
            dn = f['def']
            fx = facts.get(dn, {})
            rows.append({
                'biome': b,
                'defName': dn,
                'label': fx.get('label') or dn,
                'mod': fx.get('mod', ''),
                'band': f.get('band', ''),
                'bodySize': fx.get('bodySize', ''),
                'commonality': f['commonality'],
                'belong': '',
                'standout': '',
                'defence': fx.get('defence', ''),
                # `status` reaches the XML only as comment text. The roster's own
                # verdict (keep/import/adjust-keep) is more informative there than
                # wildlife.csv's dormancy flag, and nothing computes on it.
                'status': f.get('action', ''),
                'reason': f'{sheet}: ' + (f.get('law') or ''),
                'promoted': 0,
            })
    return rows, collisions, unbound, offowner


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    out = OUT
    if '--out' in argv:
        out = argv[argv.index('--out') + 1]

    rows, collisions, unbound, offowner = build_rows()
    with open(out, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)

    biomes = sorted({r['biome'] for r in rows})
    print(f'wrote {out}: {len(rows)} rows across {len(biomes)} biome(s)')
    missing = sorted(BIOMECAST_DEFS - set(biomes))
    if missing:
        print(f'\n🔴 {len(missing)} BiomeCast-owned def(s) get NO row - their roster is '
              f'empty or absent, so the biome keeps whatever its donor mod ships:')
        for b in missing:
            print(f'     {b}')
    if collisions:
        print(f'\n⚠️ {len(collisions)} injection row(s) collided with a base roster row '
              f'and the BASE row was kept:')
        for b, dn, keep, drop in collisions:
            print(f'     {b:32s} {dn:28s} kept {keep}, dropped {drop}')
    if unbound:
        print(f'\nℹ️ roster(s) with fauna but no defNames (bind nothing): {unbound}')
    if offowner:
        print('\nℹ️ roster rows aimed at defs this file does not own (their wildAnimals '
              'lives in the def\'s own XML - written there, not here):')
        for b, n in sorted(offowner.items()):
            print(f'     {b:32s} {n} row(s)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
