# sum.py <json>...: one line per run: held ids, who left (holdLeft), ONPIT pawns
import json, sys
for f in sys.argv[1:]:
    try: d = json.load(open(f))
    except Exception as e: print(f.split('/')[-1], 'NO JSON', e); continue
    tr = d.get('holdTrace') or []
    on = sorted({p.split()[1].split('@')[0] for l in tr for p in l.split(' | ') if p.strip().startswith('ONPIT')})
    print(f.split('/')[-1], 'held', d.get('holdHeld'), 'LEFT', json.dumps(d.get('holdLeft'))[:400], 'ONPIT', on, 'lines', len(tr))
