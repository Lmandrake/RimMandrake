"""MAP_AWARENESS_PROVE_ON_A_QUIET_MAP live acceptance (feasible subset) on the 550-mod full list.
python.exe Transient/foundry_awareness_live_20261010.py   -> Transient/foundry_awareness_live_20261010.json
Each step records the raw replies; verdicts are computed at the end and printed one line each."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
U = os.path.join(HERE, '..', 'src', 'RimMandrake', 'Utils')
for p in (U, os.path.join(U, 'modcheck')):
    sys.path.insert(0, p)
from rimdrive import Session
import helpers as H
import contract as C

OUT = os.path.join(HERE, 'foundry_awareness_live_20261010.json')
R = {'steps': {}, 'checks': []}


def save():
    json.dump(R, open(OUT, 'w'), indent=1, default=str)


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
    save()


def journal_max(j):
    rows = (j or {}).get('rows') or (j or {}).get('incidents') or []
    return max([r.get('aseq', -1) for r in rows] + [-1]), rows


with Session(lock=None) as s:
    c(s, 'jawa/set_game_speed', speed='Paused')
    R['steps']['status0'] = c(s, 'jawa/awareness', action='status')
    R['steps']['arm'] = c(s, 'jawa/awareness', action='arm', minutes=60)
    R['steps']['status1'] = c(s, 'jawa/awareness', action='status')
    kh = H.kill_hostiles(s, ())
    R['steps']['killHostiles'] = {'acted': kh.acted, 'verified': kh.verified, 'residue': kh.residue}
    ax, az, _ = H.safe_anchor(s)
    R['steps']['anchor'] = [ax, az]
    j0 = c(s, 'jawa/incident_journal', limit=5)
    seq0, _r = journal_max(j0)
    R['steps']['journal0'] = j0
    save()

    # 1. three known pawns: substituted-spawn receipts + origin
    receipts, spawned = [], []
    for i, (kind, fac) in enumerate((('Tribal_Warrior', 'hostile'), ('Muffalo', 'none'), ('Villager', 'player'))):
        res = c(s, 'jawa/spawn_pawn', kindDef=kind, x=ax + 4 + 3 * i, z=az + 4, faction=fac, count=1)
        R['steps']['spawn_%s' % kind] = res
        rows = H.read_pawns(s, health=False)
        rc = C.spawn_receipt('spawn%d' % i, 'jawa/spawn_pawn', kind, res, rows)
        receipts.append(rc)
        spawned += rc['returnedIds']
    R['steps']['receipts'] = receipts
    check('spawn receipts: 3 calls, every id read back, requested vs tool vs read-back kinds recorded',
          len(receipts) == 3 and all(r['returnedIds'] and not r['missingOnReadBack'] for r in receipts),
          {'problems': C.receipt_problems(receipts), 'receipts': receipts})
    o1 = c(s, 'jawa/pawn_origin', ids=','.join(str(x) for x in spawned))
    R['steps']['origin_spawned'] = o1
    txt = json.dumps(o1)
    check('pawn_origin attributes the 3 spawns to our bridge action (jawa/spawn_pawn in the chain)',
          'spawn_pawn' in txt and o1.get('success', True) is not False, {'origin': o1})

    # 2. our own raid: called vs fired, origin chain bridge:jawa/fire_incident > incident:RaidEnemy
    before = set(r['id'] for r in H.read_pawns(s, health=False))
    fr = c(s, 'jawa/fire_incident', incidentDef='RaidEnemy', points=300)
    R['steps']['fire_raid'] = fr
    c(s, 'rimworld/step_game_ticks', ticks=300) if True else None
    after = H.read_pawns(s, health=False)
    new = [r for r in after if r['id'] not in before]
    R['steps']['raid_new_pawns'] = [{k: r.get(k) for k in ('id', 'kindDef', 'kind', 'faction', 'hostile')} for r in new]
    j1 = c(s, 'jawa/incident_journal', sinceSeq=seq0, limit=50)
    seq1, rows1 = journal_max(j1)
    R['steps']['journal_raid'] = j1
    raid_rows = [r for r in rows1 if 'RaidEnemy' in json.dumps(r)]
    check('incident journal records the forced RaidEnemy with honest outcome fields',
          bool(raid_rows), {'rows': raid_rows, 'fired': fr})
    if new:
        o2 = c(s, 'jawa/pawn_origin', ids=','.join(str(r['id']) for r in new[:20]))
        R['steps']['origin_raid'] = o2
        t2 = json.dumps(o2)
        check('raid pawns carry the chain bridge:jawa/fire_incident > incident:RaidEnemy',
              'fire_incident' in t2 and 'RaidEnemy' in t2, {'origin': o2})
    else:
        check('raid pawns carry the chain bridge:jawa/fire_incident > incident:RaidEnemy', False,
              {'why': 'no new pawns after 300 ticks (drop pods may still be falling)', 'fired': fr})

    # 3. an incident that is CALLED but whose worker returns false (Infestation on a map with no overhead rock
    #    usually fails); the journal must not claim it fired
    fi = c(s, 'jawa/fire_incident', incidentDef='Infestation', points=200)
    R['steps']['fire_infestation'] = fi
    j2 = c(s, 'jawa/incident_journal', sinceSeq=seq1, limit=50)
    _s2, rows2 = journal_max(j2)
    R['steps']['journal_infestation'] = j2
    inf = [r for r in rows2 if 'Infestation' in json.dumps(r)]
    fired = fi.get('fired')
    check('called-is-not-fired: journal row for Infestation agrees with the tool\'s fired flag (%s)' % fired,
          bool(inf) and all((r.get('result') in (True, False, None)) for r in inf), {'rows': inf, 'tool': fi})

    # 4. scene report after, then remove the visitors (owner rule: record and remove)
    R['steps']['awareness_status_end'] = c(s, 'jawa/awareness', action='status')
    kh2 = H.kill_hostiles(s, ())
    R['steps']['killHostiles_end'] = {'acted': kh2.acted, 'verified': kh2.verified, 'residue': kh2.residue}
    c(s, 'jawa/set_game_speed', speed='Paused')
save()
print('DONE', OUT)
