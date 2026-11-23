#!/usr/bin/env python3
"""control_crowd.py - does a raider swim beside the LOWERED leaf because the deck is cheap to cut past, or because it is held?
(RIMMANDRAKE_TRACE_FLOWWORKS_MOAT_SWIMMER_PAST_LOWERED_LEAF_AGAIN)

Vanilla 1.6 PathFinderJob in Python: g = max(grid, provider) + 175 on a blocked square (Cost_Blocked) + 13 / 18 a step, the octile
heuristic x 13 x strength. A raider's strength is RoundToInt(40 cells -> 1 .. 120 -> 2): 1 anywhere on this site. A square is
blocked by another pawn (PathGridDoorsBlockedJob, PawnUtility.PawnBlockedBy) when both have had hostiles close and BOTH have a
collideWithPawns job; JobGiver_AIGotoNearestHostile sets it, a player-ordered Goto (ctl.py's raider B) does not.

Costs: swim 60 (ProofSwim pathCost, live), timber deck 4, anchor 6, winch 30 (Defs/Pits), ground 1 (a guess; it moves nothing).
NOT modelled: the metre of wall above the water in the 4 wide moat (entering or leaving the water there costs more, so its swim
counts are upper bounds), moving blockers, repaths while walking, doors.

    python3 control_crowd.py            the map, both geometries, blockers on 0..W deck squares, every south-bank start
    python3 control_crowd.py --replay   the recorded swimmers: their first poll as start, the others' squares as blockers
"""
import heapq, itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
IG = os.path.join(HERE, '..', 'in_game')
SWIM, DECK, ANCHOR, WINCH, GROUND, BLOCKED = 60, 4, 6, 30, 1, 175


def site(w, ox=60, oz=60):
    n = 8 + 2 * w
    ring = {(ox + i, oz + j) for i in range(n) for j in range(n) if i < w or i >= n - w or j < w or j >= n - w}
    lx = ox + w + 4
    deck = [(lx, oz + j) for j in range(w)]
    cost = {c: SWIM for c in ring}
    cost.update({c: DECK for c in deck})
    cost[(lx, oz - 1)] = cost[(lx, oz + w)] = ANCHOR
    cost[(lx, oz + w + 1)] = WINCH
    return {'ring': ring - set(deck), 'deck': deck, 'cost': cost, 'col': (ox + w + 5, oz + w + 4), 'oz': oz, 'lx': lx, 'w': w,
            'lo': (ox - 10, oz - 14), 'hi': (ox + n + 10, oz + n + 4)}


def path(s, start, blocked=(), strength=1):
    lo, hi, dest, blocked = s['lo'], s['hi'], s['col'], set(blocked)

    def h(c):
        a, b = abs(dest[0] - c[0]), abs(dest[1] - c[1])
        return (a + b - 0.58579 * min(a, b)) * 13 * strength
    g, par, done, q = {start: 0}, {start: start}, set(), [(0, start)]
    while q:
        _, c = heapq.heappop(q)
        if c in done:
            continue
        if c == dest:
            break
        done.add(c)
        for dx, dz in itertools.product((-1, 0, 1), repeat=2):
            d = (c[0] + dx, c[1] + dz)
            if (dx, dz) == (0, 0) or d in done or not (lo[0] <= d[0] <= hi[0] and lo[1] <= d[1] <= hi[1]):
                continue
            v = g[c] + s['cost'].get(d, GROUND) + (BLOCKED if d in blocked else 0) + (18 if dx and dz else 13)
            if d not in g or v < g[d]:
                g[d], par[d] = v, c
                heapq.heappush(q, (v + h(d), d))
    out, c = [], dest
    while True:
        out.append(c)
        if par[c] == c:
            return out[::-1]
        c = par[c]


def swims(s, start, blocked=(), strength=1):
    return [c for c in path(s, start, blocked, strength) if c in s['ring']]


def starts(s):
    return [(x, z) for x in range(s['lx'] - 6, s['lx'] + 7) for z in range(s['oz'] - 8, s['oz'])]


def sweep():
    for w in (2, 4):
        s = site(w)
        line = [(s['lx'], s['oz'] - 1)] + s['deck']
        print('moat %d wide, %d starts' % (w, len(starts(s))))
        for strength in (1, 2):
            n = sum(bool(swims(s, p, (), strength)) for p in starts(s))
            print('  free deck, heuristic x%d: %d of %d starts swim' % (strength, n, len(starts(s))))
        for k in range(1, w + 1):
            for sub in itertools.combinations(s['deck'], k):
                st = [p for p in starts(s) if p not in sub]
                r = [len(swims(s, p, sub)) for p in st]
                print('  held deck squares %s: %d of %d starts swim (squares swum 0..%d)' % (
                    [c[1] - s['oz'] for c in sub], sum(map(bool, r)), len(st), max(r)))


def replay():
    for f, who in (('testpilot_20261123/r3.json', ('24625', '24630')), ('testpilot_20261123/c2.json', ('24634',)),
                   ('visit_8/evidence/sc_moat_raid_20261123T034521.json', ('24626',))):
        calls = json.load(open(os.path.join(IG, f)))['calls']
        i0 = max(i for i, c in enumerate(calls) if c['tool'] == 'jawa/lord_assault_spawn')
        polls = [{p['id'][5:]: (p['x'], p['z']) for p in c['result'].get('pawns', []) if p.get('x') is not None}
                 for c in calls[i0:] if c['tool'] == 'jawa/list_pawns' and isinstance(c['args'], dict) and c['args'].get('faction') == 'hostile']
        s = site(2)
        for pid in who:
            for k, p in enumerate(polls[:2]):
                others = {v for i, v in p.items() if i != pid}
                if pid in p and p[pid] not in s['ring']:
                    print('%-48s %s poll %d at %s: free %s | others as they stand %s' % (f, pid, k + 1, p[pid],
                          swims(s, p[pid]), swims(s, p[pid], others)))
    print('each raider, not only the swimmers, at poll 1 (who the model sends through the water):')
    for f in ('testpilot_20261123/r3.json', 'testpilot_20261123/c2.json', 'testpilot_20261123/c1.json', 'visit_8/evidence/sc_moat_raid_20261123T034521.json'):
        calls = json.load(open(os.path.join(IG, f)))['calls']
        i0 = max(i for i, c in enumerate(calls) if c['tool'] == 'jawa/lord_assault_spawn')
        p = next({q['id'][5:]: (q['x'], q['z']) for q in c['result'].get('pawns', []) if q.get('x') is not None}
                 for c in calls[i0:] if c['tool'] == 'jawa/list_pawns' and isinstance(c['args'], dict) and c['args'].get('faction') == 'hostile')
        s = site(2)
        print(' ', f, sorted(i for i, v in p.items() if swims(s, v, {u for j, u in p.items() if j != i})))


if __name__ == '__main__':
    replay() if '--replay' in sys.argv else sweep()
