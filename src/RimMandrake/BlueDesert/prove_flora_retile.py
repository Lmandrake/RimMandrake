"""Live proof A2 of BLUEDESERT_FLORA_PLANT_REFUSAL_1: on the current (disposable quicktest) map, retiled to
RM_BlueDesert at -5 C through modcheck.bland_world.retile, every BlueDesert PlantBase flora stands after
jawa/set_plants with no rejectionReasons. Exits 0 when the clause holds, 1 when it does not, 2 when unmeasured.

Why it failed before: Tile.MinTemperature is a lazy cache RimWorld never invalidates; mapgen had read the bland
tile's warm min, so PlantUtility.CanEverPlantAt refused the cold-only plants (maxGrowthTemperature -1) even after
the tile temperature read back -5. retile() now nulls the caches (jawa/world_tile_cache_reset, verifiedNull).

Run under Windows python.exe with the game up (it starts a debug quicktest map if none is playing):
    python.exe "$(wslpath -w src/RimMandrake/BlueDesert/prove_flora_retile.py)" < /dev/null
It cleans up after itself: the plants are destroyed and the tile's biome and temperature restored.
"""
import glob
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
sys.path.insert(0, UTILS)
sys.path.insert(0, os.path.join(UTILS, "modcheck"))
import rimbridge_client as rb       # noqa: E402
import bland_world as BW            # noqa: E402


def flora():
    """BlueDesert ThingDefs whose ParentName is PlantBase, parsed from this mod's own Defs/ (as validation.py does)."""
    out = []
    for path in sorted(glob.glob(os.path.join(HERE, "Defs", "*", "*.xml"))):
        with open(path, encoding="utf-8") as fh:
            txt = re.sub(r"<!--.*?-->", "", fh.read(), flags=re.S)
        for m in re.finditer(r"<ThingDef\b([^>]*)>(.*?)</ThingDef>", txt, re.S):
            nm = re.search(r"<defName>([^<]+)</defName>", m.group(2))
            if nm and re.search(r'ParentName\s*=\s*"PlantBase"', m.group(1)) \
                    and not re.search(r'Abstract\s*=\s*"[Tt]rue"', m.group(1)):
                out.append(nm.group(1).strip())
    return out


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


def main():
    plants = flora()
    if len(plants) < 8:
        print("UNMEASURED: only %d PlantBase flora parsed from %s/Defs" % (len(plants), HERE))
        return 2
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
    w = 4 * len(plants) + 4
    x0, z0 = cx - w // 2, cz - 4
    rect = "%d,%d,%d,8" % (x0, z0, w)
    s.call("jawa/destroy_batch", rects=rect, categories="All")
    s.call("jawa/set_terrain_batch", ops="Ice:%s" % rect, layer="top")
    try:
        rec = BW.retile(s, "RM_BlueDesert", temperature=-5)
    except BW.BlandWorldError as ex:
        print("UNMEASURED: retile failed: %s" % ex)
        return 2
    lost, why = [], {}
    try:
        audit = s.call("jawa/world_cache_audit", tiles=str(rec["tile"]), includeTemps=True, limit=5)
        print("cache audit after retile: staleTotal=%r" % (audit.get("staleTotal"),))
        for i, d in enumerate(plants):
            px, pz = x0 + 2 + i * 4, z0 + 4
            r = s.call("jawa/set_plants", ops="%s:%d,%d,1,1" % (d, px, pz), growth=1.0)
            if isinstance(r, dict) and r.get("rejectionReasons"):
                why[d] = r["rejectionReasons"]
            c = s.call("jawa/list_things", defName=d, limit=1, rect="%d,%d,1,1" % (px, pz))
            if "countMatched" not in c or not c.get("scanned"):
                print("UNMEASURED: list_things(%s) unreadable: %r" % (d, c))
                return 2
            if c["countMatched"] < 1:
                lost.append(d)
    finally:
        s.call("jawa/destroy_batch", rects=rect, categories="All")
        problems = BW.restore_tile(s, rec)
        if problems:
            print("restore problems: %s" % problems)
    print("flora asked=%d lost=%s rejectionReasons=%s" % (len(plants), lost, json.dumps(why)))
    if lost or why:
        print("FAIL: BlueDesert flora refused on a -5 C retile")
        return 1
    print("PASS: all %d BlueDesert flora stand on a -5 C RM_BlueDesert retile" % len(plants))
    return 0


if __name__ == "__main__":
    sys.exit(main())
