"""Acceptance of RIMMANDRAKE_SPREAD_SHADE_DASH_SEVEN_ANIMALS_ON_ONE_CELL: on a save of a hot, sunny map, no cell holds three
or more wild animals that rest, idle or dash (the shade behaviour's own jobs). usage: <this> <save.rws>.
Exit 0 holds, 1 fails, 2 could not look (no wild animal on the map).

Wild animals on a job with its own target cell (drinking at one water cell, eating) are listed apart and not judged:
the shade dash never gives those jobs (measured live 2026-11-25: three gizka drinking at one terrain cell, FlowWorks)."""
import collections
import sys
import xml.etree.ElementTree as ET

SHADE_JOBS = {None, "Wait", "Wait_MaintainPosture", "Wait_Wander", "Wait_Asleep", "GotoWander", "LayDown", "RM_ShadeDash"}
try:
    things = ET.parse(sys.argv[1]).getroot().findall("game/maps/li/things/thing")
except Exception as e:  # noqa: BLE001
    print("COULD NOT LOOK: %s" % e); sys.exit(2)
judged, busy = collections.defaultdict(list), collections.defaultdict(list)
for t in things:
    if t.find("kindDef") is not None and t.findtext("faction") is None:
        job = t.findtext("jobs/curJob/def")
        (judged if job in SHADE_JOBS else busy)[t.findtext("pos")].append("%s:%s" % (t.findtext("kindDef"), job))
if not judged and not busy:
    print("COULD NOT LOOK: no wild animal"); sys.exit(2)
bad = {p: v for p, v in judged.items() if len(v) >= 3}
other = {p: v for p, v in busy.items() if len(v) >= 3}
print("%d wild animals; resting/idle/dashing cells with three or more: %s" % (
    sum(map(len, judged.values())) + sum(map(len, busy.values())), bad or "none"))
if other:
    print("not judged (busy on a job with its own target): %s" % other)
sys.exit(1 if bad else 0)
