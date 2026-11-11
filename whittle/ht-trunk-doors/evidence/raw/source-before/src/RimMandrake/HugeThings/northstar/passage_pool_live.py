#!/usr/bin/env python3
"""Focused complete-pool / arrival receipt checks for TITAN_PASSAGE_PRUNE_WHALES_ON_FOOT.

This module never drives a game. It validates raw outputs from the existing
TitanValidationHooks surface without shortening strings. An audit is complementary
content evidence, never fresh-process/deployment/save-restoration certification.
Live prerequisites must pass separately; the historical titan_events_live runner
is insufficient by itself (truncated receipts, vacuous pools, whole-map rollback).

PROVE: complete PassageCanFire on RM_Stillsand; EXPECT nonempty and every kind land.
LIES: an empty/truncated pool, a foreign biome, or only checking the picked kind.
PROVE: PassageReport after explicit DebugArriveNow; EXPECT actual spawned ID, own
roster and eligible-pool membership, seaMatch=True. LIES: pending-kind duplicate
key parsed as arrived-kind, cached LastArrived, synthetic roster, missing census.
No crossing, natural elapsed warning, flight, showcase or restoration claim.

Usage (offline): passage_pool_live.py --inventory --out inventory.json
  passage_pool_live.py --audit raw.json --out audit.json
Audit input keys: pool_response, arrival_response (raw static_call payloads),
own_roster (resolved positive-commonality kind names, with separate provenance).
No source/modelled roster can authenticate a live arrival.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
HOOKS = 'RimMandrake.TitanicCreatures.TitanValidationHooks'
BIOME = 'RM_Stillsand'


class ReceiptRefusal(ValueError):
    """An incomplete instrument cannot produce a pass."""


class ContentFailure(AssertionError):
    """A complete answer that violates the bar stays FAIL."""


def require(condition, reason):
    if not condition:
        raise ReceiptRefusal(reason)


def raw_result(response):
    require(isinstance(response, dict) and response.get('success') is True,
            'static_call payload success must be exactly true')
    result = response.get('result')
    require(isinstance(result, str) and result and not result.startswith('FAIL'),
            'missing/refused raw static result')
    return result


def pool(response):
    """Parse the entire current hook grammar; fail on count mismatch or suffix."""
    text = raw_result(response)
    match = re.fullmatch(
        r'canFire=(True|False) active=(True|False) t3OnMap=(True|False) '
        r'biome=(\w+) seaMap=(True|False) hints=(roster|none|list\d+) '
        r'eligible=(\d+) \[([^\[\]]*)\]', text)
    require(match is not None, 'pool grammar incomplete, truncated, or unknown')
    can, active, t3, biome, sea, hints, count, body = match.groups()
    kinds = []
    for token in body.split(',') if body else []:
        row = re.fullmatch(r'(\w+):(T2|T3):(sea|land)', token)
        require(row is not None, 'unknown kind/tier/sea marker in complete pool')
        name, tier, habitat = row.groups()
        kinds.append(dict(kind=name, tier=tier, habitat=habitat))
    require(len(kinds) == int(count), 'declared pool count differs from full raw list')
    require(len({x['kind'] for x in kinds}) == len(kinds), 'duplicate eligible kind')
    return dict(canFire=can == 'True', active=active == 'True', t3OnMap=t3 == 'True',
                biome=biome, seaMap=sea == 'True', hints=hints, kinds=kinds)


def land_pool(response):
    got = pool(response)
    require(got['biome'] == BIOME and got['seaMap'] is False, 'owed R3 Stillsand land biome not measured')
    if not got['kinds']:
        raise ContentFailure('empty eligible pool cannot pass')
    if any(k['habitat'] != 'land' for k in got['kinds']):
        raise ContentFailure('sea kind eligible on land')
    return got


def arrival(response, eligible, own_roster):
    """Keep the pending and arrived `kind=` keys distinct, including ID/state."""
    text = raw_result(response)
    m = re.fullmatch(
        r'pending=False kind=none arrivalIn=-1 arrived=(\w+) kind=(\w+) '
        r'tier=(T2|T3) spawned=(True|False) homedHere=(True|False) seaMatch=(True|False) '
        r'lord=LordJob_ExitMapNear pos=(-?\d+),(-?\d+)', text)
    require(m is not None, 'no complete actual spawned own-biome sea-matching arrival')
    require(isinstance(own_roster, list) and own_roster and
            all(isinstance(x, str) and x for x in own_roster), 'resolved own roster missing')
    pawn, kind, tier, spawned, home, sea, x, z = m.groups()
    if (spawned, home, sea) != ('True', 'True', 'True'):
        raise ContentFailure('arrival not spawned, own-biome, and sea-matching')
    if kind not in {k['kind'] for k in eligible['kinds']}:
        raise ContentFailure('arrived kind was outside measured eligible pool')
    if kind not in own_roster:
        raise ContentFailure('arrived kind outside resolved positive-commonality own roster')
    return dict(pawn=pawn, kind=kind, tier=tier, x=int(x), z=int(z))


def inventory(saves_dir):
    """Read only permitted existing test-site saves; never decode with a stale hash table."""
    p = Path(saves_dir)
    out = dict(directory=str(p), glob='RM_TestSite_*.rws', saves=[],
               biome_resolution='UNMEASURED: needs exact saved-set shortHash table or guarded live read')
    require(p.is_dir(), 'configured Saves directory absent')
    for f in sorted(p.glob(out['glob'])):
        root = ET.parse(f).getroot()
        maps = []
        for m in root.findall('./game/maps/li'):
            info = m.find('mapInfo')
            maps.append(dict(id=m.findtext('uniqueID'), mapInfo=ET.tostring(info, encoding='unicode')
                             if info is not None else None))
        out['saves'].append(dict(path=str(f), bytes=f.stat().st_size,
            sha256=hashlib.sha256(f.read_bytes()).hexdigest(),
            modIds=[x.text for x in root.findall('./meta/modIds/li')], maps=maps))
    return out


def audit(data):
    rec = dict(scope='offline raw-content audit only', certifiable=False, rows=[])
    for name, fn in [('complete_land_pool', lambda: land_pool(data['pool_response'])),
                     ('arrival_membership', lambda: arrival(data['arrival_response'],
                         land_pool(data['pool_response']), data['own_roster']))]:
        try:
            rec[name] = fn()
            rec['rows'].append(dict(id=name, status='PASS'))
        except (ReceiptRefusal, KeyError) as ex:
            rec['rows'].append(dict(id=name, status='UNMEASURED', reason=str(ex)))
        except ContentFailure as ex:
            rec['rows'].append(dict(id=name, status='FAIL', reason=str(ex)))
    rec['ok'] = all(r['status'] == 'PASS' for r in rec['rows'])
    return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--inventory', action='store_true')
    mode.add_argument('--audit', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    if a.inventory:
        sys.path.insert(0, str(ROOT/'src/RimMandrake/Utils'))
        from game_paths import SAVES
        rec = inventory(SAVES)
        rc = 0
    else:
        rec = audit(json.loads(a.audit.read_text()))
        rc = 0 if rec['ok'] else 2
    a.out.write_text(json.dumps(rec, indent=2)+'\n')
    print(json.dumps(dict(output=str(a.out), certifiable=False, exit_code=rc)))
    return rc


if __name__ == '__main__':
    sys.exit(main())
