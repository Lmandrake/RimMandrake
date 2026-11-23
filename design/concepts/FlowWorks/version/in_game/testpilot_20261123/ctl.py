# ctl.py <block:0|1> <tag> : leaf DOWN, brim-full moat, 2 raiders, bait gone. Raider A stands on the deck (block=1) or far off
# (block=0); raider B is sent to the plot. Prints B's cell every 10 ticks and whether it is a swim square.
import sys, json, os
sys.path.insert(0, r'src/RimMandrake/FlowWorks/northstar'); sys.path.insert(0, r'src/RimMandrake/Utils'); sys.path.insert(0, r'src/RimMandrake/Utils/modcheck')
import concept_scenes as cs
HERE = os.path.dirname(os.path.abspath(__file__))
block, tag = sys.argv[1] == '1', sys.argv[2]
cs.MOAT_RAIDERS = 2
stage0 = cs._moat_stage
cs._moat_stage = lambda S, raised=True: stage0(S, raised=False)
def rows(S, G):
    B = S.B
    B.call('jawa/pawn_force_incapacitate', pawn=G['colonist'], action='vanish')
    a, b = G['raiders']
    ring = set(G['ring'])
    deck = G['deck']
    to = (deck[0], deck[1]) if block else (deck[0] - 6, deck[1] - 6)
    o = B.call('jawa/order_pawn', pawnId=a, x=to[0], z=to[1], waitTicks=360, draft=False)
    print('A', a, 'sent to', to, ascii(o.get('message')), flush=True)
    print('LEAF', S.sc(cs.DPROOF, 'ProofLeaf', '%d,%d' % G['deck'])[:120], flush=True)
    o = B.call('jawa/order_pawn', pawnId=b, x=deck[0], z=deck[1] + 5, waitTicks=0, draft=False)
    print('B', b, 'ordered to', (deck[0], deck[1] + 5), ascii(o.get('message'))[:120], flush=True)
    path, swam = [], []
    for k in range(40):
        B.ticks(10)
        ps = {p['id']: p for p in (B.call('jawa/site_state').get('pawns') or [])}
        pa, pb = ps.get(a, {}), ps.get(b, {})
        c = (pb.get('x'), pb.get('z'))
        if not path or path[-1][0] != c:
            path.append((c, pb.get('job'), (pa.get('x'), pa.get('z')), pa.get('job')))
            if c in ring: swam.append(c)
        if c == (deck[0], deck[1] + 5): break
    for q in path: print('  B at', q[0], q[1], '| A at', q[2], q[3], '| RING' if q[0] in ring else '')
    print('RESULT block=%s swimSquares=%s' % (block, swam), flush=True)
    S.row('TP_ctl', True, {'swam': swam})
cs._moat_rows = rows
sys.argv = ['x', '--scene', 'scene_moat_raid', '--out', os.path.join(HERE, tag + '.json')]
cs.main()
