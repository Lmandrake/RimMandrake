#!/usr/bin/env python3
"""Offline selftest: RSW_Leaftail can fly (LEAFTAIL_WIRE_FLIGHT_WINGED_RODENT_GROUNDED).

Canon calls the leaf-tail a "winged rodent" and "flying omnivores"; the standing rule (owner 2026-09-19) is that a
creature that flies in the fiction flies in the game. In 1.6, Pawn_FlightTracker.CanEverFly is
GetStatValue(MaxFlightTime) > 0, so the stat is the switch (skills/rimworld-modding/references/flight.md); race flags
alone leave a grounded animal. Flip-book frames are a separate art item and are not checked here.
Also checks that flyer_census.py no longer adjudicates the leaf-tail as a flier missing MaxFlightTime.
"""
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DEF = os.path.join(REPO, 'src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Leaftail.xml')
CENSUS = os.path.join(HERE, 'art', 'flyer_census.py')
RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append(bool(ok))
    print('%s %s%s' % ('ok  ' if ok else 'FAIL', name, ('  -- %s' % detail) if detail and not ok else ''))


def num(el, path):
    node = el.find(path)
    try:
        return float(node.text) if node is not None else None
    except (TypeError, ValueError):
        return None


def main():
    root = ET.parse(DEF).getroot()
    things = [t for t in root.findall('ThingDef') if t.findtext('defName') == 'RSW_Leaftail']
    check('exactly one RSW_Leaftail ThingDef', len(things) == 1, 'found %d' % len(things))
    if len(things) != 1:
        return 1
    t = things[0]
    mft = num(t, 'statBases/MaxFlightTime')
    cd = num(t, 'statBases/FlightCooldown')
    chance = num(t, 'race/flightStartChanceOnJobStart')
    check('statBases MaxFlightTime > 0 (CanEverFly)', mft is not None and mft > 0, 'MaxFlightTime=%r' % mft)
    check('statBases FlightCooldown > 0', cd is not None and cd > 0, 'FlightCooldown=%r' % cd)
    check('race flightStartChanceOnJobStart in (0, 1]', chance is not None and 0 < chance <= 1, 'chance=%r' % chance)
    # sanity probe: the instrument can see a stat that is known present
    check('probe: MoveSpeed readable', num(t, 'statBases/MoveSpeed') == 5.0)
    with open(CENSUS, encoding='utf-8') as fh:
        src = fh.read()
    check('flyer_census ADJ no longer lists RSW_Leaftail as missing MaxFlightTime',
          '"RSW_Leaftail": ("should-fly"' not in src)
    print('RESULT: %d/%d ok' % (sum(RESULTS), len(RESULTS)))
    return 0 if all(RESULTS) else 1


if __name__ == '__main__':
    sys.exit(main())
