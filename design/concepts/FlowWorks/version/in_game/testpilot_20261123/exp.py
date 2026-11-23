# exp.py stage <save>            : run the moat scene to the drained-and-held moment, drive off the free, save it (keeper)
# exp.py cap <save> <ticks> <step> <raider:x,z|raider:auto>... [--no-order] : load it, one warden per spec, order, trace
import sys, json, time, os
sys.path.insert(0, r'src/RimMandrake/FlowWorks/northstar'); sys.path.insert(0, r'src/RimMandrake/Utils'); sys.path.insert(0, r'src/RimMandrake/Utils/modcheck')
import concept_scenes as cs
import validation_core as V
import test_site_saves as T
from game_paths import SAVES
HERE = os.path.dirname(os.path.abspath(__file__))
mode, save = sys.argv[1], sys.argv[2]
side = os.path.join(HERE, save + '.held.json')
NSP = cs.NSP
def line(B, ids):
    r = B.call('jawa/site_state') or {}
    out = []
    for p in r.get('pawns') or []:
        if p.get('id') in ids or p.get('faction') != 'PlayerColony':
            t = p.get('targetA') or {}
            out.append('%s@%s,%s:%s>%s' % (p['id'].replace('Human', ''), p.get('x'), p.get('z'), (p.get('job') or '-').replace('RM_CaptureDown', 'CD'),
                                         str(t.get('id') or t.get('thingId') or ('%s,%s' % (t.get('x'), t.get('z')) if t else '-')).replace('Human', '')))
    return ' '.join(sorted(out))
def sc(B, m, a=''):
    return str((B.call('jawa/static_call', type=NSP, method=m, args=a) or {}).get('result'))
if mode == 'stage':
    def rows(S, G):
        w = cs._moat_watch(S, G)
        up = S.sc(cs.DOORS, 'ProofSetGate', 'current|%d,%d|true' % G['sluice'])
        for k in range(cs.MOAT_DRAIN_PULSES):
            S.pulse(1)
            dl = S.dl(G['ring'])
            if None not in dl and not any(dl): break
        S.ticks(60)
        held = []
        for pid, x, z in cs._moat_live(S, G):
            v = S.sc(NSP, 'ProofCaptureDown', pid)
            if (x, z) in set(G['ring']) and 'held=True' in v: held.append([pid, x, z, v])
        gone = cs._raid_driven_off(S, {h[0] for h in held}) if held else []
        S.B.call('jawa/pawn_force_incapacitate', pawn=G['colonist'], action='vanish')
        sv = T.save_site(S.B.call, save, SAVES)
        json.dump({'held': held, 'swam': sorted(w['swam']), 'gone': gone, 'G': {k: G[k] for k in ('ring', 'col')}}, open(side, 'w'))
        print('STAGED held=%s gone=%d swam=%s' % (held, len(gone), sorted(w['swam'])), flush=True)
        S.row('TP_staged', bool(held), {'held': held})
    cs._moat_rows = rows
    sys.argv = ['x', '--scene', 'scene_moat_raid', '--out', os.path.join(HERE, save + '.stage.json')]
    cs.main(); sys.exit(0)
B = V.Bridge()
B.stop_on = cs.RAID_STOP_ON
ticks, step = int(sys.argv[3]), int(sys.argv[4])
specs = [a for a in sys.argv[5:] if not a.startswith('--')]
r = T.load_site(B.call, 'calm', name=save, check=False, map_controls=('modal_broker',))
assert r['verified'], r
ws = {}
extra = []
for a in sys.argv[5:]:
    if a.startswith('--move='):
        rid, at = a.split('=')[1].split(':'); x, z = at.split(',')
        o = B.call('jawa/order_pawn', pawnId='Human' + rid, x=int(x), z=int(z), waitTicks=240, draft=False)
        print('MOVE', rid, at, str({k: o.get(k) for k in o if k not in ('operation', 'state')})[:300], sc(B, 'ProofCaptureDown', 'Human' + rid), flush=True)
for a in sys.argv[5:]:
    if a.startswith('--raider='):
        x, z = a.split('=')[1].split(',')
        rr = B.call('jawa/spawn_pawn', kindDef=cs.MOAT_KIND, x=int(x), z=int(z), faction=cs._isl_hostile_faction(type('S', (), {'call': lambda self, t, **k: B.call(t, **k), 'B': B, 'sc': lambda self, ty, m, a='': str((B.call('jawa/static_call', type=ty, method=m, args=a) or {}).get('result'))})()), count=1)
        extra.append(rr['pawns'][0]['id']); print('EXTRA raider', extra[-1], 'at', x, z, sc(B, 'ProofCaptureDown', extra[-1]), flush=True)
for a in sys.argv[5:]:
    if a.startswith('--hold='):
        o = B.call('jawa/ordered_job', pawnId='Human' + a.split('=')[1], jobDef='Wait')
        print('HOLD', a, o.get('accepted'), o.get('afterJobDef'), flush=True)
for a in sys.argv[5:]:
    if a.startswith('--down='):
        o = B.call('jawa/pawn_force_incapacitate', pawn='Human' + a.split('=')[1], action='downed')
        print('DOWN', a, str({k: o.get(k) for k in o if k not in ('operation', 'state')})[:200], flush=True)
def place(s):
    pid, at = s.split(':')[:2]
    pid = 'Human' + pid if pid.isdigit() else pid
    v = sc(B, 'ProofCaptureDown', pid); cell = tuple(int(q) for q in v.split('cell=')[1].split(','))
    lip = cs._moat_plot_lip(cell) if at == 'auto' else tuple(int(q) for q in at.split(','))
    w = B.call('jawa/spawn_pawn', kindDef='Colonist', x=lip[0], z=lip[1], faction='player', count=1, xenotype='Baseliner')['pawns'][0]['id']
    ws[w] = pid; IDS.update((w, pid))
    acc = None
    if '--no-order' not in sys.argv:
        acc = B.call('jawa/ordered_job', pawnId=w, jobDef='RM_CaptureDown', targetAId=pid, targetBX=lip[0], targetBZ=lip[1]).get('accepted')
    print('SPEC %s at %s lip %s warden %s accepted=%s | %s' % (pid, cell, lip, w, acc, v), flush=True)
IDS = set()
later = sorted((int(s.split(':')[2]), s) for s in specs if s.count(':') == 2)
for s in specs:
    if s.count(':') == 1: place(s)
for a in sys.argv[5:]:
    if a.startswith('--attack='):
        rid = 'Human' + a.split('=')[1]
        print('ATTACK order', rid, '->', list(ws)[0], B.call('jawa/ordered_job', pawnId=rid, jobDef='AttackMelee', targetAId=list(ws)[0]), flush=True)
        extra.append(rid)
IDS |= set(extra)
last = line(B, IDS); print('t0', last, flush=True)
for t in range(step, ticks + 1, step):
    B.ticks(step)
    while later and later[0][0] <= t: place(later.pop(0)[1])
    now = line(B, IDS) + ' | ' + ' '.join(sc(B, 'ProofCaptureDown', p).split('held=')[-1] for p in ws.values())
    if now != last: print('t+%d' % t, now, flush=True)
    last = now
for w, p in ws.items():
    e = (B.call('jawa/damage_log', thingId=w, limit=12) or {}).get('events') or []
    print('END warden %s victim %s | %s | hits %s' % (w, p, sc(B, 'ProofCaptureDown', p), ['%s %s %s' % (x.get('tick'), x.get('instigatorId'), x.get('damageDef')) for x in e]))
