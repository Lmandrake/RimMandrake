"""probe_islands_leaf.py <out.json>: sc_islands experiment (visit 3). Stage the islands scene on the calm site, destroy BOTH
winches (the staged loss), tick, then ask whether a lowered leaf carries a walker: a colonist spawned on the steel span is
ordered to each bank, and the raiders' positions are read for 3,000 ticks. Separates "the lowered leaf is not walkable"
(MOD) from "the raiders do not choose to cross" (SITE). Never a row of rows.jsonl; reloads the calm site at the end."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NS = os.path.join(HERE, *[".."] * 6, "src", "RimMandrake", "FlowWorks", "northstar")
sys.path.insert(0, NS)
import concept_scenes as C  # noqa: E402
import validation_core as V  # noqa: E402
import test_site_saves as T  # noqa: E402

B = V.Bridge()
res = {'calls': []}
out = {}
try:
    out['site'] = T.load_site(B.call, 'calm')
    S = C._Stage(B, res, 'probe_islands_leaf')
    st = C._isl_stage(S)
    out['raiders'] = st['raiders']
    for c in st['winch']:
        out.setdefault('destroyed', []).append(S.call('jawa/destroy_batch', rects='%d,%d,1,1' % c, categories='Building').get('destroyed'))
    prior, S.B.stop_on = S.B.stop_on, C.RAID_STOP_ON
    try:
        S.ticks(10)
    finally:
        S.B.stop_on = prior
    out['leaves'] = [C._isl_leaf(S, dx) for dx in C.ISL_LEAVES]
    cells = B.call('rimworld/get_cells_info', x=C.O[0] - 1, z=C.O[1], width=23, height=1) or {}
    out['row_cells'] = [(q.get('x'), q.get('z'), q.get('terrain') or q.get('terrainDef'), q.get('walkable', q.get('standable')),
                         [t.get('defName') for t in q.get('things') or []]) for q in cells.get('cells') or []]
    walker = S.pawn('Colonist', C._isl_xz(10), 'player')
    out['walk_west'] = S.walk(walker, (C.O[0] - 2, C.O[1]), wait=1500)
    out['walk_east'] = S.walk(walker, (C.O[0] + 23, C.O[1]), wait=1500)
    seen = []
    for _ in range(25):
        S.ticks(120)
        seen.append([(p['id'], p['x'], p['z'], p.get('downed')) for p in B.call('jawa/list_pawns', faction='hostile').get('pawns') or []
                     if p.get('id') in st['raiders']])
    out['raider_track'] = seen[::5] + [seen[-1]]
except Exception as e:  # noqa: BLE001
    out['error'] = repr(e)[:800]
finally:
    out['reload'] = T.load_site(B.call, 'calm').get('verified')
    json.dump(out, open(sys.argv[1], 'w', encoding='utf-8'), indent=1, default=str)
    print(json.dumps({k: (v if k in ('error', 'walk_west', 'walk_east', 'leaves') else '...') for k, v in out.items()}, default=str)[:3000])
