#!/usr/bin/env python3
"""play.py -- the Artisan's live play site for Pyrelands: an ordinary, un-isolated landing, and cheap looks at it.

northstar_site.py builds the suite's fixture with every fire mechanic off at generation and a quiet storyteller. This
builds the map a player gets: every mechanic on, a live storyteller, three colonists at the centre, nothing cleared.

Bridge holder only, python.exe from the repo root (pipe through `tr -d '\\r'`):
  python.exe src/RimMandrake/Pyrelands/play.py build --tag a         # fresh world, 2-ring re-tile, map, save, reload
  python.exe src/RimMandrake/Pyrelands/play.py load  --tag a         # reload that save
  python.exe src/RimMandrake/Pyrelands/play.py census                # terrain, plants, animals, fire, weather, colonists
  python.exe src/RimMandrake/Pyrelands/play.py step 2500 ...         # run N ticks, census after each N given
  python.exe src/RimMandrake/Pyrelands/play.py shot NAME x z w h [px]  # play-zoom capture copied to shots/
  python.exe src/RimMandrake/Pyrelands/play.py overview NAME         # the widest crop the tool can frame
  python.exe src/RimMandrake/Pyrelands/play.py skies x z w h TAG       # one rect under each sky at noon
  python.exe src/RimMandrake/Pyrelands/play.py call jawa/map_info k=v  # any one tool, json result
"""
import argparse
import collections
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import northstar_site as NS                          # noqa: E402
import preflight_pyrelands as P                      # noqa: E402
from northstar_driver.session import FastSession     # noqa: E402
from game_paths import SAVES                         # noqa: E402

SHOTS = r"D:\ClaudeWork\rimmandrake\ralph_pyrelands\shots"
WORK = os.path.join(P.ROOT, "Transient", "pyre_play")
TEMP = 50.0
KEEP_ALIVE_PACKS = 60


def record_path(tag):
    return os.path.join(WORK, "play_%s.json" % tag)


def build(s, tag, temp):
    rec = {"tag": tag, "temp": temp, "world": NS.fresh_quicktest_world(s)}
    rec["colonyTile"] = NS._call(s, "jawa/map_info").get("tile")
    rec["pick"] = NS.choose_tile(s, os.path.join(WORK, "world_%s" % tag), rec["colonyTile"])
    centre = rec["pick"]["centre"]
    NS.retile(s, rec["pick"]["patch"], temp)
    NS.strip_mutators(s, centre)
    NS.set_midsummer_noon(s, rec["pick"]["lat"], rec["pick"]["long"])
    g = NS.generate(s, centre)
    rec["mapId"] = g["mapId"]
    NS.home(s, g["mapId"])
    NS.retire_offsite_colonies(s, centre)
    NS.stock_food(s, P.MAP_SIZE // 2, P.MAP_SIZE // 2, packs=KEEP_ALIVE_PACKS)
    NS.name_colony(s, centre)
    rec["saveName"] = "NS_Pyrelands_play_%s" % tag
    rec["save"] = NS.save_fixture(s, rec["saveName"], SAVES, os.path.join(WORK, "saves_backup"))
    os.makedirs(WORK, exist_ok=True)
    with open(record_path(tag), "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1, default=str)
    return rec


def load(s, tag):
    """A plain load, no settle_site: settle_site applies the quiet profile, which is exactly what this site refuses."""
    rec = json.load(open(record_path(tag), encoding="utf-8"))
    if NS._ui_state(s).get("programState") == "Playing":
        try:
            s.call("rimworld/go_to_main_menu")
        except Exception:
            pass
        NS._wait_state(s, "Entry", 180)
    try:
        s.call("rimworld/load_game", saveName=rec["saveName"])
    except Exception as ex:
        print("load_game raised %s, polling" % type(ex).__name__)
    NS._wait_state(s, "Playing", 420)
    t0 = time.time()
    while time.time() - t0 < 420:
        try:
            if NS._call(s, "jawa/map_info").get("tile") is not None:
                break
        except NS.Unmeasured:
            pass
        time.sleep(1)
    NS.name_colony(s, rec["pick"]["centre"])
    NS._call(s, "jawa/set_current_map", mapId=NS.find_site_map(s, rec["pick"]["centre"]))
    return rec


def census(s, terrain=True):
    mi = NS._call(s, "jawa/map_info")
    clk = NS._call(s, "jawa/time_clock")
    wx = NS._call(s, "jawa/weather_get").get("weather")
    print("tick %s map %s %s outdoor %s weather %s" % (clk.get("ticksGame"), mi.get("mapId"), mi.get("mapBiome"),
                                                       mi.get("outdoorTempNow"), wx))
    if terrain:
        w, h = mi.get("sizeX", 250), mi.get("sizeZ", 250)
        r = NS._call(s, "jawa/get_terrain_batch", rects="0,0,%d,%d" % (w, h))
        c = collections.Counter()
        for op in (r.get("ops") or "").replace("\n", ";").split(";"):
            if ":" in op:
                d, nums = op.split(":", 1)
                p = [int(v) for v in nums.split(",") if v.strip()]
                c[d] += p[2] * p[3] if len(p) >= 4 else 1
        print("terrain %s" % [(k, round(100.0 * v / (w * h), 1)) for k, v in c.most_common(12)])
    r = NS._call(s, "jawa/list_things", group="Plant", limit=1)
    print("plants %s %s" % (r.get("countMatched"), sorted((r.get("perDef") or {}).items(), key=lambda kv: -kv[1])[:12]))
    fires = NS._call(s, "jawa/list_things", defName="Fire", limit=2000).get("things") or []
    if fires:
        print("fires %d x %d..%d z %d..%d" % (len(fires), min(t["x"] for t in fires), max(t["x"] for t in fires),
                                              min(t["z"] for t in fires), max(t["z"] for t in fires)))
    else:
        print("fires 0")
    items = NS._call(s, "jawa/list_things", group="HaulableEver", limit=1)
    print("items %s %s" % (items.get("countMatched"), sorted((items.get("perDef") or {}).items(), key=lambda kv: -kv[1])[:6]))
    pawns = NS._call(s, "jawa/list_pawns", limit=500).get("pawns") or []
    print("wild %s" % collections.Counter(p.get("kind") for p in pawns if not p.get("isPlayer") and not p.get("dead")).most_common(30))
    print("colony %s" % [(p.get("name"), p.get("x"), p.get("z"), "DEAD" if p.get("dead") else ("down" if p.get("downed") else ""))
                         for p in pawns if p.get("isPlayer")])


def shot(s, name, x, z, w, h, ppc=64):
    """A rect at a measured px per cell, under a unique capture name, copied to the shots folder once written."""
    from modcheck import play_zoom

    class Refused(Exception):
        pass
    cap = "pyre_%s_%d" % (name, int(time.time()))
    path = play_zoom.shoot(s, play_zoom.Calibration(), (x, z, w, h), 0, ppc, cap, Refused)
    os.makedirs(SHOTS, exist_ok=True)
    out = os.path.join(SHOTS, name + ".png")
    t0 = time.time()
    while time.time() - t0 < 30:               # the tool writes asynchronously
        if os.path.exists(path) and os.path.getsize(path) > 0:
            time.sleep(0.5)
            shutil.copy2(path, out)
            return out
        time.sleep(0.5)
    raise Refused("no image at %s" % path)


def overview(s, name):
    """A 200x200 centred crop, the widest the screenshot tool can frame, so a burn's whole shape is visible at once."""
    s.call("rimworld/set_camera_zoom_extension", enabled=True)
    s.call("jawa/clear_ui")
    cap = "pyre_%s_%d" % (name, int(time.time()))
    r = s.call("rimworld/screenshot_cell_rect", fileName=cap, x=25, z=25, width=200, height=200, paddingCells=0,
               rootSize=100, suppressMessage=True) or {}
    path = r.get("path")
    out = os.path.join(SHOTS, name + ".png")
    t0 = time.time()
    while path and time.time() - t0 < 30:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            time.sleep(0.5)
            shutil.copy2(path, out)
            return out
        time.sleep(0.5)
    return str(r)[:300]


def to_hour(s, hour):
    """Advance to the next local `hour`, in slices the populated-map budget allows."""
    clk = NS._call(s, "jawa/time_clock")
    lon = NS._call(s, "jawa/map_info").get("longitude") or 0.0
    now = (int(clk["ticksAbs"]) + int(round(lon / 15.0)) * 2500) % 60000
    left = (hour * 2500 - now) % 60000
    while left > 0:
        n = min(left, 25000)
        s.call("jawa/safe_advance", ticks=n, stopOn="cancel", timeoutMs=230000)
        left -= n


def skies(s, x, z, w, h, tag):
    """The same ground under each sky between 08:00 and 17:00, each held long enough to finish its transition."""
    to_hour(s, 8)
    for wx in ("Clear", "RM_FE_Weather_AshDrift", "RM_FE_Weather_AshFall", "RM_FE_Weather_Cinderfall", "RM_FE_BlackRain"):
        NS._call(s, "jawa/weather_set", weather=wx, lockWeather=True)
        s.call("jawa/safe_advance", ticks=4500, stopOn="cancel", timeoutMs=120000)
        print(wx, shot(s, "sky_%s_%s" % (tag, wx), x, z, w, h), NS._call(s, "jawa/weather_get").get("weather"))
    NS._call(s, "jawa/weather_set", weather="RM_FE_Weather_AshDrift", lockWeather=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("verb", choices=["build", "load", "census", "step", "shot", "overview", "skies", "call"])
    ap.add_argument("rest", nargs="*")
    ap.add_argument("--tag", default="a")
    ap.add_argument("--temp", type=float, default=TEMP)
    a = ap.parse_args()
    s = FastSession(strict=False)
    with s:
        if a.verb == "build":
            rec = build(s, a.tag, a.temp)
            print(json.dumps({k: rec.get(k) for k in ("saveName", "mapId", "pick")}, default=str)[:400])
            load(s, a.tag)
            census(s)
        elif a.verb == "load":
            load(s, a.tag)
            census(s)
        elif a.verb == "census":
            census(s)
        elif a.verb == "step":
            for n in a.rest:
                t0 = time.time()
                r = s.call("jawa/safe_advance", ticks=int(n), stopOn="cancel", timeoutMs=max(60000, int(n) * 100)) or {}
                print("advanced %s of %s in %.0fs %s" % (r.get("executed"), n, time.time() - t0, r.get("stopBy") or r.get("message") or ""))
                census(s, terrain=False)
        elif a.verb == "shot":
            print(shot(s, a.rest[0], *[int(v) for v in a.rest[1:]]))
        elif a.verb == "overview":
            print(overview(s, a.rest[0]))
        elif a.verb == "skies":
            skies(s, *[int(v) for v in a.rest[:4]], a.rest[4])
        elif a.verb == "call":
            kw = {}
            for kv in a.rest[1:]:
                k, v = kv.split("=", 1)
                try:
                    kw[k] = json.loads(v)
                except ValueError:
                    kw[k] = v
            print(json.dumps(s.call(a.rest[0], **kw), default=str))


if __name__ == "__main__":
    main()
