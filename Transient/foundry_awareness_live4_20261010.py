"""Pass 4: in-game handshake, disarm -> no AWARE row, first-map wildlife origin, awareness meters. Appends to the json."""
import json, os, sys, datetime
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


with Session(lock=None) as s:
    S['handshake_ingame'] = c(s, 'jawa/companion_handshake')
    S['disarm'] = c(s, 'jawa/awareness', action='disarm')
    S['disarm_utc'] = datetime.datetime.utcnow().isoformat() + 'Z'
    S['fire_after_disarm'] = c(s, 'jawa/fire_incident', incidentDef='ResourcePodCrash')
    S['journal_after_disarm'] = c(s, 'jawa/incident_journal', limit=3)
    rows = H.read_pawns(s, health=False)
    wild = [r for r in rows if not r.get('faction') and not r.get('dead')]
    S['wild_ids'] = [r['id'] for r in wild][:40]
    S['origin_wild'] = c(s, 'jawa/pawn_origin', ids=','.join(S['wild_ids'])) if wild else None
    S['awareness_final'] = c(s, 'jawa/awareness', action='status')
    S['tps_report_final'] = c(s, 'jawa/tps_report')
json.dump(R, open(OUT, 'w'), indent=1, default=str)
print('DONE')
