#!/usr/bin/env python3
"""selftest for world_beauty_live.py (WORLD_BEAUTY_VERIFY_OFFLINE_BEAT_THE_GAME), offline.

1. the plan is the offline set's seven cameras and passes its own check;
2. each planned tile id sits, in the ENGINE's tile geometry (world/world_tiles_sub7b.csv, dumped from the live game),
   within MAX_SNAP_DEG of its camera: the record's tile ids are the ids jawa/world_view centres on;
3. check_plan refuses a renamed view, a shared tile and a far snap (it can say no);
4. the Chill instrument reads a dark centre disc in a bright frame as dark, and a bright one as bright;
5. the full list the live half compares against parses to a non-trivial id list;
6. PLANETARY_LOADSCREEN_RENDERS_2 names the seven live captures (the item's verify clause).
"""
import copy
import csv
import math
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world_beauty_live as L  # noqa: E402

fails = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        fails.append(what)


views = L.plan()
ok(tuple(v["name"] for v in views) == L.OFFLINE_NAMES, "plan names are the offline seven")
ok(L.check_plan(views) == [], "plan passes its check: %s" % L.check_plan(views))

geo = {r["tile"]: r for r in csv.DictReader(open(os.path.join(L.REPO, "world/world_tiles_sub7b.csv")))}


def arc(lat1, lon1, lat2, lon2):
    p1, p2, dl = math.radians(lat1), math.radians(lat2), math.radians(lon2 - lon1)
    c = math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dl)
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


ok(len(geo) == 21872, "engine geometry has 21872 tiles (%d)" % len(geo))
for v in views:
    g = geo.get(str(v["tile"]))
    d = arc(v["lat"], v["lon"], float(g["lat"]), float(g["long"])) if g else 999
    ok(d <= L.MAX_SNAP_DEG, "%s tile %d is %.2f deg from its camera in the engine geometry" % (v["name"], v["tile"], d))

bad = copy.deepcopy(views); bad[0]["name"] = "dayside_x"
ok(L.check_plan(bad) != [], "check refuses a renamed view")
bad = copy.deepcopy(views); bad[1]["tile"] = bad[0]["tile"]
ok(L.check_plan(bad) != [], "check refuses a shared tile")
bad = copy.deepcopy(views); bad[2]["snap_deg"] = 5.0
ok(L.check_plan(bad) != [], "check refuses a far snap")
bad = copy.deepcopy(views); bad[6]["face"] = "GreySea"
ok(L.check_plan(bad) != [], "check refuses a Chill camera off the Chill")

from PIL import Image, ImageDraw  # noqa: E402
with tempfile.TemporaryDirectory() as d:
    p = os.path.join(d, "f.png")
    im = Image.new("RGB", (400, 300), (200, 200, 200))
    ImageDraw.Draw(im).ellipse((170, 120, 230, 180), fill=(20, 30, 51))       # max channel 51 -> value 20
    im.save(p)
    v = L.hsv_value_disc(p)
    ok(abs(v - 20.0) < 0.5 and v <= L.CHILL_DARK_MAX, "dark centre disc reads %.1f (20)" % v)
    Image.new("RGB", (400, 300), (40, 120, 160)).save(p)
    v = L.hsv_value_disc(p)
    ok(v > L.CHILL_DARK_MAX, "bright frame reads %.1f > %.0f" % (v, L.CHILL_DARK_MAX))
    ok(L.luminance_std(p) < L.BLANK_STD, "a flat frame reads blank")

ids = L.list_ids(L.FULL_LIST)
ok(len(ids) > 50 and "ludeon.rimworld" in ids, "full list parses (%d ids, Core held)" % len(ids))

ITEM = os.path.join(L.REPO, "infrastructure/state/items/closed/PLANETARY_LOADSCREEN_RENDERS_2.md")
if os.path.isfile(ITEM):        # the Marker's box leaves infrastructure/state/items out (walls.marker.tree_exclude)
    item = open(ITEM).read()
    ok("world_beauty_2026-10-31\\live\\" in item and all(("`%s.png`" % n) in item for n in L.OFFLINE_NAMES),
       "PLANETARY_LOADSCREEN_RENDERS_2 names the seven live captures as its input")
else:
    print("skip PLANETARY_LOADSCREEN_RENDERS_2 naming: items/ is not in this tree")

print("SELFTEST %s" % ("FAIL" if fails else "PASS"))
sys.exit(1 if fails else 0)
