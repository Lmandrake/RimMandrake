"""probe_islands_exit.py --out <json> [--read NAME ...] [--at N] [--after M] [--early NAME ...]: sc_islands experiment
(item RIMMANDRAKE_STAGE_FLOWWORKS_ISLAND_RAIDERS_NEVER_CROSS_LOWERED_LEAF). Stage the islands scene on the calm site, let
the raiders take a winch (natural loss, concept_scenes._isl_watch), then poll 120 ticks with list_pawns only. At poll --at
with nobody off the span (the stuck state) run the named reads ONCE on every live raider, poll --after more, then dump
every read. --early runs reads every poll from the start (the 'a reader frees them' arm). One change per run.
Never a row of rows.jsonl; reloads the calm site at the end."""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import concept_scenes as C  # noqa: E402
import validation_core as V  # noqa: E402
import test_site_saves as T  # noqa: E402

READS = {   # name -> (type, method, args template; %s = pawn id)
    'edge': ('Verse.ReachabilityUtility', 'CanReachMapEdge', '%s'),
    'trace': ('RimMandrake.FlowWorks.RM_RaiderTrench', 'ProofJobTrace', '%s'),
    'trapped': ('RimMandrake.FlowWorks.RM_SuperdeepTrap', 'IsTrapped', '%s'),
    'pedge': ('RimMandrake.FlowWorks.RM_PocketGrid', 'ProofEdge', '%s'),
    'timing': ('RimMandrake.FlowWorks.RM_PocketGrid', 'ProofPocketTiming', 'x%.0s'),
    'inert': ('RimWorld.SappersUtility', 'IsGoodSapper', '%s'),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--read', nargs='*', default=[])
    ap.add_argument('--early', nargs='*', default=[])
    ap.add_argument('--at', type=int, default=10)
    ap.add_argument('--after', type=int, default=15)
    ap.add_argument('--dump', nargs='*', default=['trace', 'edge', 'trapped'])
    ap.add_argument('--keep', action='store_true', help='leave the scene up (no reload) for a look')
    a = ap.parse_args()
    B = V.Bridge()
    res, out = {'calls': []}, {'args': vars(a), 'track': []}
    try:
        out['site'] = T.load_site(B.call, 'calm').get('verified')
        S = C._Stage(B, res, 'probe_islands_exit')
        st = C._isl_stage(S)
        mine = set(st['raiders'])

        def read(names, ids):
            return {n: {p: S.sc(READS[n][0], READS[n][1], READS[n][2] % p)[:900] for p in ids[:(1 if n == 'timing' else 9)]} for n in names}

        def live():
            ps = [p for p in S.call('jawa/list_pawns', faction='hostile').get('pawns') or []
                  if p.get('id') in mine and not p.get('dead') and p.get('x') is not None]
            esc = [p['id'] for p in ps if p['x'] <= C.O[0] or p['x'] >= C.O[0] + 21]
            return ps, esc

        prior, S.B.stop_on = S.B.stop_on, C.RAID_STOP_ON
        try:
            lost, esc, k = [], [], 0
            for k in range(C.ISL_POLLS):                       # to the first winch lost (as _isl_watch until='loss')
                S.ticks(C.ISL_POLL)
                ps, esc = live()
                if a.early:
                    out.setdefault('early', []).append(read(a.early, [p['id'] for p in ps][:2]))
                lost = [dx for dx in C.ISL_LEAVES if C._isl_leaf(S, dx).get('winch') != 'True']
                if lost or esc:
                    break
            out['loss'] = {'polls': k + 1, 'lost': lost, 'escaped_before': esc}
            S.ticks(10)
            out['leaves'] = [C._isl_leaf(S, dx) for dx in C.ISL_LEAVES]
            done = False
            for k in range(a.at + a.after):
                S.ticks(C.ISL_POLL)
                ps, esc = live()
                out['track'].append([k, len(ps), esc, [(p['x'], p['z'], p.get('downed')) for p in ps]])
                if esc:
                    out['escaped_at'] = k
                    break
                if a.early:
                    out['early'].append(read(a.early, [p['id'] for p in ps][:2]))
                if k + 1 == a.at and not done:
                    done = True
                    out['stuck_read'] = read(a.read, [p['id'] for p in ps if not p.get('downed')])
            ps, esc = live()
            out['final'] = {'escaped': esc, 'live': len(ps), 'leaves': [C._isl_leaf(S, dx).get('progress') for dx in C.ISL_LEAVES]}
            out['dump'] = read(a.dump, [p['id'] for p in ps if not p.get('downed')])
        finally:
            S.B.stop_on = prior
    except Exception as e:  # noqa: BLE001
        out['error'] = repr(e)[:800]
    finally:
        if not a.keep:
            out['reload'] = T.load_site(B.call, 'calm').get('verified')
        json.dump(out, open(a.out, 'w', encoding='utf-8'), indent=1, default=str)
        print(json.dumps({k: v for k, v in out.items() if k not in ('track', 'early', 'dump', 'args', 'leaves')}, default=str)[:2500])
        print('TRACK', json.dumps(out['track'][-2:], default=str)[:600])
        print('DUMP', json.dumps(out.get('dump'), default=str)[:2500])


if __name__ == '__main__':
    main()
