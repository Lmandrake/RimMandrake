"""Second pass: a raid that is not swallowed (Mechanoid, exempt from the protection-fee modal) to prove the
deferred-delivery chain, plus infestation cleanup. Appends to Transient/foundry_awareness_live_20261010.json."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
U = os.path.join(HERE, '..', 'src', 'RimMandrake', 'Utils')
for p in (U, os.path.join(U, 'modcheck')):
    sys.path.insert(0, p)
from rimdrive import Session
import helpers as H

OUT = os.path.join(HERE, 'foundry_awareness_live_20261010.json')
R = json.load(open(OUT))
S = R['steps']


def c(s, tool, **p):
    r = s.call(tool, **p)
    if isinstance(r, dict) and r.get('content') and isinstance(r['content'], list):
        try:
            r = json.loads(r['content'][0]['text'])
        except Exception:
            pass
    return r


def check(name, ok, detail):
    R['checks'].append({'check': name, 'pass': bool(ok), 'detail': detail})
    print(('PASS ' if ok else 'FAIL ') + name, flush=True)
    json.dump(R, open(OUT, 'w'), indent=1, default=str)


with Session(lock=None) as s:
    j = c(s, 'jawa/incident_journal', limit=5)
    seq0 = max([r.get('aseq', -1) for r in j.get('rows') or []] + [-1])
    before = set(r['id'] for r in H.read_pawns(s, health=False))
    fr = c(s, 'jawa/fire_incident', incidentDef='RaidEnemy', points=300, faction='Mechanoid')
    S['fire_raid_mech'] = fr
    S['step_mech'] = c(s, 'rimworld/step_game_ticks', ticks=900)
    after = H.read_pawns(s, health=False)
    new = [r for r in after if r['id'] not in before]
    S['mech_new_pawns'] = [{k: r.get(k) for k in ('id', 'kindDef', 'kind', 'faction', 'hostile')} for r in new]
    j1 = c(s, 'jawa/incident_journal', sinceSeq=seq0, limit=50)
    S['journal_mech'] = j1
    raid = [r for r in j1.get('rows') or [] if r.get('def') == 'RaidEnemy']
    if new:
        o = c(s, 'jawa/pawn_origin', ids=','.join(str(r['id']) for r in new[:30]))
        S['origin_mech'] = o
        rows = o.get('pawns') or []
        chained = [p for p in rows if 'fire_incident' in json.dumps(p) and 'RaidEnemy' in json.dumps(p)]
        check('deferred delivery: raid pawns carry bridge:jawa/fire_incident > incident:RaidEnemy (%d of %d)'
              % (len(chained), len(rows)), rows and len(chained) == len(rows),
              {'statements': [p.get('statement') for p in rows][:10]})
        nonours = [p for p in rows if p.get('ourInvolvement') not in ('confirmedIndirectAction', 'confirmedDirectAction')]
        check('raid pawns: ourInvolvement is ours (not a stranger)', rows and not nonours,
              {'involvement': [p.get('ourInvolvement') for p in rows]})
    else:
        check('deferred delivery: raid pawns carry the chain', False, {'why': 'no new pawns after 900 ticks', 'fired': fr,
                                                                       'journal': raid})
    # infestation leftovers: hives / tunnel spawners from the pass-1 Infestation
    hives = {}
    for d in ('TunnelHiveSpawner', 'Hive'):
        hives[d] = c(s, 'jawa/list_things', defName=d, limit=50)
    S['infestation_things'] = hives
    S['awareness_status_end2'] = c(s, 'jawa/awareness', action='status')
    kh = H.kill_hostiles(s, ())
    S['killHostiles_end2'] = {'acted': kh.acted, 'verified': kh.verified, 'residue': kh.residue}
json.dump(R, open(OUT, 'w'), indent=1, default=str)
print('DONE')
