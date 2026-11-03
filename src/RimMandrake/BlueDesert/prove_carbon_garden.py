"""Live proof A4 of BLUEDESERT_GPT_ENRICHMENT_1: on the current (disposable quicktest) map, retiled to RM_BlueDesert at
-5 C through modcheck.bland_world.retile, the Carbon Garden three (RM_Milelace, RM_Hazebell, RM_Longglass) stand after
jawa/set_plants, and a hazebell opens once the RM_Haze weather has fallen over a long tick (its inspect string reads
"Open"), with the weather on Clear it is closed. Exits 0 when the clause holds, 1 when it does not, 2 when unmeasured.

Run under Windows python.exe with the game up (it starts a debug quicktest map if none is playing):
    python.exe src/RimMandrake/BlueDesert/prove_carbon_garden.py < /dev/null   (from the repo root)
It cleans up after itself: plants destroyed, weather unlocked to Clear, the tile's biome and temperature restored.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
sys.path.insert(0, UTILS)
sys.path.insert(0, os.path.join(UTILS, "modcheck"))
import rimbridge_client as rb       # noqa: E402
import bland_world as BW            # noqa: E402
import helpers as H                 # noqa: E402

GARDEN = ("RM_Milelace", "RM_Hazebell", "RM_Longglass")
OPEN_WORD = "breathing out the Haze"   # RM_CompHazeBloom.CompInspectStringExtra: "Open: breathing out the Haze."


class Session(object):
    def __init__(self):
        host, port, token = rb.resolve_endpoint()
        self.b = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
        self.b.connect()

    def call(self, tool, **p):
        r = self.b.call(tool, p) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except Exception:
                pass
        return r


def inspect_lines(s, thing_id):
    r = s.call("jawa/inspect_string", thingIds=thing_id)
    rows = (r or {}).get("things") or []
    if not rows or rows[0].get("error"):
        return None
    return [str(x) for x in (rows[0].get("inspect") or [])]


def is_open(lines):
    return any(OPEN_WORD in l for l in lines)


def advance(s, n):
    start, now, why = H.fast_advance(s, n)
    if start is None:
        return None
    end = (s.call("rimworld/get_game_info") or {}).get("ticksGame")
    return None if end is None else end - start


def main():
    s = Session()
    if s.call("rimworld/get_ui_state").get("programState") != "Playing":
        s.call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
        for _ in range(120):
            if s.call("rimworld/get_ui_state").get("programState") == "Playing":
                break
            time.sleep(1)
    info = s.call("jawa/map_info")
    if info.get("sizeX") is None or info.get("tile") is None:
        print("UNMEASURED: no playing map: %r" % (info,))
        return 2
    cx, cz = int(info["sizeX"]) // 2, int(info["sizeZ"]) // 2
    x0, z0 = cx - 8, cz - 4
    rect = "%d,%d,16,8" % (x0, z0)
    s.call("jawa/destroy_batch", rects=rect, categories="All")
    s.call("jawa/set_terrain_batch", ops="Ice:%s" % rect, layer="top")
    try:
        rec = BW.retile(s, "RM_BlueDesert", temperature=-5)
    except BW.BlandWorldError as ex:
        print("UNMEASURED: retile failed: %s" % ex)
        return 2
    lost, why, verdict = [], {}, {}
    try:
        cells = {}
        for i, d in enumerate(GARDEN):
            px, pz = x0 + 2 + i * 4, z0 + 4
            cells[d] = (px, pz)
            r = s.call("jawa/set_plants", ops="%s:%d,%d,1,1" % (d, px, pz), growth=1.0)
            if isinstance(r, dict) and r.get("rejectionReasons"):
                why[d] = r["rejectionReasons"]
            c = s.call("jawa/list_things", defName=d, limit=1, rect="%d,%d,1,1" % (px, pz))
            if "countMatched" not in c or not c.get("scanned"):
                print("UNMEASURED: list_things(%s) unreadable: %r" % (d, c))
                return 2
            if c["countMatched"] < 1:
                lost.append(d)
        if "RM_Hazebell" not in lost:
            px, pz = cells["RM_Hazebell"]
            rows = (s.call("jawa/list_things", defName="RM_Hazebell", limit=1, rect="%d,%d,1,1" % (px, pz)) or {}).get("things") or []
            hid = rows[0].get("id") if rows else None
            if not hid:
                print("UNMEASURED: hazebell has no thing id: %r" % (rows,))
                return 2
            # Closed under Clear across two long ticks (the sanity half: the instrument can read "closed").
            s.call("jawa/weather_set", weather="Clear", lockWeather=True)
            moved = advance(s, 4200)
            clear_lines = inspect_lines(s, hid)
            s.call("jawa/weather_set", weather="RM_Haze", lockWeather=True)
            got = (s.call("jawa/weather_get") or {}).get("weather")
            if isinstance(got, dict):
                got = got.get("current")
            if got != "RM_Haze":
                print("UNMEASURED: could not lock RM_Haze (read back %r)" % (got,))
                return 2
            moved2 = advance(s, 4200)
            haze_lines = inspect_lines(s, hid)
            verdict = {"ticks_clear": moved, "ticks_haze": moved2, "clear": clear_lines, "haze": haze_lines}
            if clear_lines is None or haze_lines is None or not moved or not moved2 or moved < 2000 or moved2 < 2000:
                print("UNMEASURED: hazebell unreadable or the clock did not move a long tick: %s" % json.dumps(verdict))
                return 2
    finally:
        try:
            s.call("jawa/weather_set", weather="Clear", lockWeather=True)
            s.call("jawa/weather_set", unlock=True)
        except Exception as ex:
            print("weather reset failed: %s" % ex)
        s.call("jawa/destroy_batch", rects=rect, categories="All")
        problems = BW.restore_tile(s, rec)
        if problems:
            print("restore problems: %s" % problems)
    print("garden lost=%s rejectionReasons=%s bloom=%s" % (lost, json.dumps(why), json.dumps(verdict)))
    if lost or why:
        print("FAIL: Carbon Garden flora refused on a -5 C RM_BlueDesert retile")
        return 1
    if is_open(verdict["clear"]):
        print("FAIL: the hazebell stood open under Clear with no Haze seen")
        return 1
    if not is_open(verdict["haze"]):
        print("FAIL: the hazebell did not open after a long tick of RM_Haze")
        return 1
    print("PASS: the Carbon Garden three stand on RM_BlueDesert, and the hazebell is closed in Clear and opens in Haze")
    return 0


if __name__ == "__main__":
    sys.exit(main())
