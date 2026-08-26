"""
Whole-planet mutator snapshot for the Grey Sea work (BRIEF.md passes 2, 4, 5).

WHY: the owner's standing warning ("the mistake the last two agents made") is
that a per-def check against your own intent can report 100% landed while
silently displacing OTHER mutators elsewhere on the planet (the Twilight
agent wiped 26 CoastalIsland + 2 Oasis this way). The only defence is a
whole-planet before/after diff, not a scoped one. This script takes ONE
snapshot; run it once before any write (tag 'before') and once after the
final world_commit (tag 'after'). apply_grey_mutators.py calls it inline
instead of shelling out, but it is kept standalone so a snapshot can be
re-taken independently if a session is interrupted mid-pass.

Must run under python.exe (bridge access, Windows loopback).

21,872 tiles confirmed via world_neighbors_sub7b.csv (21873 lines incl.
header) and the 2026-08-24 "measured editing 21,872 tiles" commit. One
world_mutators_get call with range=0-21871, onlyWithMutators=True and a
limit above the live histogram's tilesWithMutators count returns every
tile that currently carries a mutator in a single call - cheap, per
world-authoring.md ("writing all 21,872 tiles takes 0.1 seconds").
"""
import sys, json, time

sys.path.insert(0, r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint

TILE_COUNT = 21872


def harvest(rb):
    r = rb.call('jawa/world_mutators_get', {
        'range': '0-%d' % (TILE_COUNT - 1),
        'onlyWithMutators': True,
        'limit': TILE_COUNT + 10,
    })
    if not r.get('success'):
        raise RuntimeError('harvest failed: %r' % r)
    snap = {}
    for row in r['tiles']:
        snap[row['tile']] = sorted(m['def'] for m in row['mutators'] if m.get('def'))
    return snap, r


def main(tag):
    host, port, token = resolve_endpoint()
    with RimBridge(host, port, token) as rb:
        snap, raw = harvest(rb)
    out = {
        'tag': tag,
        'ts': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'tileCount': TILE_COUNT,
        'requested': raw.get('requested'),
        'countReturned': raw.get('count'),
        'errors': raw.get('errors'),
        'ticksGame': raw.get('ticksGame'),
        'mutators': snap,
    }
    path = r'D:\Luke\dev\Rimworld\world\_grey\_planet_mutators_%s.json' % tag
    json.dump(out, open(path, 'w'), indent=0)
    print('tag=%s tilesWithMutators=%d requested=%s returned=%s errors=%d -> %s' % (
        tag, len(snap), raw.get('requested'), raw.get('count'), len(raw.get('errors') or []), path))


if __name__ == '__main__':
    tag = sys.argv[1] if len(sys.argv) > 1 else 'before'
    main(tag)
