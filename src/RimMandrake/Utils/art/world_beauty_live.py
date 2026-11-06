#!/usr/bin/env python3
"""world_beauty_live.py -- WORLD_BEAUTY_VERIFY_OFFLINE_BEAT_THE_GAME: the 2026-10-31 beauty set's seven views, shot on the
REAL globe (ring, rivers, icons, sea films), beside the offline set they repeat.

    python3 src/RimMandrake/Utils/art/world_beauty_live.py plan [--check]     # OFFLINE: the seven cameras -> tile ids
    python3 src/RimMandrake/Utils/art/world_beauty_live.py live [--list <ModsConfig.xml>] [--out DIR]   # LIVE (bridge)

plan  The cameras are world_beauty_render.views() itself (same function, so the live set cannot drift from the offline
      one): five fixed lat/lon points plus the Seas and Chill centroids taken from the tile RECORD
      (world/ASHKARR_WORLDMAP_tiles.csv). jawa/world_view centres on a TILE, not a lat/lon, so each camera becomes the
      record's nearest tile. --check exits 0 only when there are exactly the seven offline names, seven distinct tiles,
      each within MAX_SNAP_DEG of its camera, and the Chill camera's tile is a Chill tile.

live  Run from WSL python3 (the bridge client runs under python.exe), the canonical save already loaded (the live-site
      line does that: live_site.py --save ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3). Refuses (exit 2, a restage, never
      a FAIL) unless the RUNNING load (jawa/running_mods, never ModsConfig.xml) holds every id of --list (default
      infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml): the item asks for the full list. Then for each view:
      jawa/world_view {show, centerTile, altitude 1100 = whole planet, northUp}, jawa/clear_ui, jawa/take_screenshot,
      the frame copied to <out>/<view>.png. One extra close-up, chill_close at altitude CLOSE_ALT on the Chill's tile,
      is the instrument for the darkness clause: median HSV value (max(R,G,B), 0-100) over a central disc of
      CHILL_DISC of the frame height. Writes <out>/live.json. Exit 0 = seven distinct non-blank frames AND (unless --clause views) the
      Chill median value <= CHILL_DARK_MAX; 1 = not so (the line says which); 2 = wrong load (restage).

Why CHILL_DARK_MAX = 45: SEA_FILMS_TUNE_PER_SEA_CHILL_UNLIT measured the global sea films lifting a Chill-dark face value
22 to 39 and a night face 34 to 45. Until that item lands the Chill is expected near 39; above 45 it is no longer dark
by the films' own ceiling. The value is recorded either way, so the next sitting can see the fix move it.

No flyers: the world view draws no pawns, and nothing here touches one.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(UTILS)))
sys.path.insert(0, HERE)

OFFLINE_NAMES = ("dayside", "terminator_east", "terminator_west", "cap_north", "cap_south", "seas", "chill_flatlight")
OFFLINE_DIR = "/mnt/d/ClaudeWork/rimmandrake/art/world_beauty_2026-10-31"
OUT_DIR = OFFLINE_DIR + "/live"
FULL_LIST = os.path.join(REPO, "infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml")
MAX_SNAP_DEG = 2.0          # a tile is ~1.44 deg across (hex spacing 0.0252 rad); the nearest one is always within this
GLOBE_ALT, CLOSE_ALT = 1100.0, 320.0      # whole planet; the SEA_FILMS item's close-up altitude
CHILL_DISC = 0.05           # radius of the measured disc, fraction of frame height (the Chill is ~5 deg, ~4 tiles, wide)
CHILL_DARK_MAX = 45.0
BLANK_STD = 3.0             # a frame whose luminance std is below this is a blank or a loading screen


def plan():
    """-> [{name, lat, lon, tile, snap_deg, biome}] for the seven views, in the offline order."""
    import numpy as np
    import world_beauty_render as W
    xyz, face, _h, keys, _bm = W.load_tiles()
    import csv
    with open(os.path.join(REPO, "world/ASHKARR_WORLDMAP_tiles.csv"), newline="") as f:
        rows = list(csv.DictReader(f))
    V = W.views(xyz, face, keys)
    out = []
    for name, (lat, lon) in V.items():
        c = W.to_xyz(np.array([lat]), np.array([lon]))[0]
        dots = xyz @ c
        i = int(np.argmax(dots))
        out.append({"name": name, "lat": round(float(lat), 3), "lon": round(float(lon), 3), "tile": int(rows[i]["tile"]),
                    "snap_deg": round(float(np.degrees(np.arccos(min(1.0, dots[i])))), 3), "biome": rows[i]["biome"],
                    "face": keys[face[i]] if face[i] >= 0 else None})
    return out


def check_plan(views):
    """-> list of failures (empty = the plan is the offline set's seven cameras, each on a real nearby tile)."""
    bad = []
    names = tuple(v["name"] for v in views)
    if names != OFFLINE_NAMES:
        bad.append("views %s are not the offline set's %s" % (names, OFFLINE_NAMES))
    if len({v["tile"] for v in views}) != len(views):
        bad.append("two views share a tile")
    for v in views:
        if v["snap_deg"] > MAX_SNAP_DEG:
            bad.append("%s: nearest tile %d is %.2f deg from its camera" % (v["name"], v["tile"], v["snap_deg"]))
    chill = [v for v in views if v["name"] == "chill_flatlight"]
    if chill and chill[0]["face"] != "Chill":
        bad.append("the Chill camera's tile %d wears face %s, not Chill" % (chill[0]["tile"], chill[0]["face"]))
    return bad


def hsv_value_disc(path, frac=CHILL_DISC):
    """median of max(R,G,B)*100/255 over a centred disc of radius frac*height."""
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(path).convert("RGB"), dtype=float)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    m = (yy - h / 2) ** 2 + (xx - w / 2) ** 2 <= (frac * h) ** 2
    return float(np.median(a[m].max(axis=1)) * 100 / 255)


def luminance_std(path):
    import numpy as np
    from PIL import Image
    return float(np.asarray(Image.open(path).convert("L"), dtype=float).std())


def list_ids(path):
    root = ET.parse(path).getroot()
    return [li.text.strip().lower() for li in root.find("activeMods") if li.text]


def _bridge(tool, params, timeout=60):
    sys.path.insert(0, UTILS)
    import live_def_check
    return live_def_check._bridge(tool, params, timeout)


def _res(reply):
    return reply.get("result", reply) if isinstance(reply, dict) else {}


def _shot(name, out):
    """take one frame into the game's Screenshots folder, wait for it, copy it to out/<name>.png -> (path, why)."""
    stamp = "wbl_%s_%d" % (name, int(time.time()))
    reply, why = _bridge("jawa/take_screenshot", {"fileName": stamp})
    wpath = _res(reply).get("filePath") if reply else None
    if not wpath:
        return None, "no screenshot path: %s" % (why or json.dumps(reply)[:200])
    upath = subprocess.run(["wslpath", "-u", wpath], capture_output=True, text=True, timeout=20).stdout.strip()
    for _ in range(30):                     # ScreenCapture resolves a frame or two later; the call cannot confirm it
        if upath and os.path.isfile(upath) and os.path.getsize(upath) > 0:
            break
        time.sleep(0.5)
    else:
        return None, "the frame %s never appeared" % wpath
    time.sleep(0.5)
    dst = os.path.join(out, name + ".png")
    shutil.copyfile(upath, dst)
    return dst, None


def cmd_live(a):
    os.makedirs(a.out, exist_ok=True)
    rec = {"item": "WORLD_BEAUTY_VERIFY_OFFLINE_BEAT_THE_GAME", "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "offline_set": OFFLINE_DIR, "frames": {}}

    def end(code, line):
        rec["result"], rec["line"] = {0: "PASS", 1: "FAIL", 2: "RESTAGE"}[code], line
        with open(os.path.join(a.out, "live.json"), "w") as f:
            json.dump(rec, f, indent=1)
        print(("PASS " if code == 0 else "FAIL " if code == 1 else "RESTAGE ") + line)
        return code

    views = plan()
    bad = check_plan(views)
    if bad:
        return end(1, "plan broken: " + "; ".join(bad))
    sys.path.insert(0, UTILS)
    import live_def_check
    running = live_def_check.call_running_mods(60)
    if not running:
        return end(2, "jawa/running_mods gave no packageIds (bridge down or no game)")
    want = set(list_ids(a.list))
    missing = sorted(want - {r.lower() for r in running})
    rec["running_mods"], rec["list"], rec["list_missing"] = len(running), a.list, len(missing)
    if missing:
        return end(2, "the running load lacks %d of %s's ids (e.g. %s): not the full list" %
                   (len(missing), os.path.basename(a.list), ", ".join(missing[:3])))
    shots = [(v["name"], v["tile"], GLOBE_ALT) for v in views]
    chill_tile = next(v["tile"] for v in views if v["name"] == "chill_flatlight")
    shots.append(("chill_close", chill_tile, CLOSE_ALT))
    for name, tile, alt in shots:
        reply, why = _bridge("jawa/world_view", {"show": True, "centerTile": tile, "altitude": alt, "northUp": True})
        r = _res(reply)
        if not reply or r.get("success") is not True or r.get("centeredOn") != tile:
            return end(1, "%s: world_view did not centre the planet on tile %d: %s" % (name, tile, why or json.dumps(reply)[:200]))
        _bridge("jawa/clear_ui", {"all": True})
        time.sleep(3.0)                     # camera settle, world layers regenerate after a jump
        path, why = _shot(name, a.out)
        if not path:
            return end(1, "%s: %s" % (name, why))
        with open(path, "rb") as f:
            md5 = hashlib.md5(f.read()).hexdigest()
        rec["frames"][name] = {"tile": tile, "altitude": alt, "path": path, "md5": md5,
                               "lum_std": round(luminance_std(path), 2), "world_view": {k: r.get(k) for k in ("centeredOn", "altitude", "worldSelectedAfter")}}
    frames = rec["frames"]
    blank = [n for n, f in frames.items() if f["lum_std"] < BLANK_STD]
    if blank:
        return end(1, "blank frames: %s" % ", ".join(blank))
    if len({f["md5"] for f in frames.values()}) != len(frames):
        return end(1, "two views gave the identical frame: the camera did not move")
    v = hsv_value_disc(frames["chill_close"]["path"])
    rec["chill_value"] = round(v, 1)
    if a.clause == "views":
        return end(0, "seven views captured to %s (The Chill reads value %.1f, judged by --clause chill)" % (a.out, v))
    if v > CHILL_DARK_MAX:
        return end(1, "seven views captured, but The Chill reads value %.1f > %.0f: not dark" % (v, CHILL_DARK_MAX))
    return end(0, "seven views captured to %s; The Chill reads value %.1f (<= %.0f, dark)" % (a.out, v, CHILL_DARK_MAX))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--check", action="store_true")
    p.add_argument("--json")
    l = sub.add_parser("live")
    l.add_argument("--list", default=FULL_LIST)
    l.add_argument("--out", default=OUT_DIR)
    l.add_argument("--clause", choices=("views", "chill", "both"), default="both",
                   help="views: exit 0 on seven good frames; chill: also needs The Chill dark; both = chill")
    a = ap.parse_args()
    if a.cmd == "live":
        return cmd_live(a)
    views = plan()
    for v in views:
        print("%-16s lat %7.2f lon %8.2f -> tile %5d (%.2f deg) %s" % (v["name"], v["lat"], v["lon"], v["tile"], v["snap_deg"], v["biome"]))
    if a.json:
        with open(a.json, "w") as f:
            json.dump(views, f, indent=1)
    if a.check:
        bad = check_plan(views)
        for b in bad:
            print("FAIL " + b)
        print("CHECK %s" % ("FAIL" if bad else "PASS"))
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
