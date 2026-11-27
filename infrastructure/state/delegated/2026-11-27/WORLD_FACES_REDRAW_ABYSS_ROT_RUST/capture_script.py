"""Stage a temporary patch of RM_Abyss and RM_RustCathedral (in memory, restored after, never saved), capture the three
faces at close/mid zoom with soft and hard borders, then restore every tile's biome and the border setting."""
import sys, json, time, shutil, csv, collections
sys.path.insert(0, r"\\wsl.localhost\Ubuntu\home\mandrake\rm\runs\clones\WORLD_FACES_REDRAW_ABYSS_ROT_RUST.det\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
OUT = r"D:\ClaudeWork\rimmandrake\scratch\faces_judge_20261127"
T = "RimMandrake.Biomes.RM_BiomesSettings"
R = 6
ALTS = [140.0, 200.0, 320.0]
tiles = {x["tile"]: x for x in json.load(open(OUT + r"\tiles.json"))}
nb = {}
for row in csv.DictReader(open(OUT + r"\nbr.csv")):
    nb[int(row["tile"])] = [int(v) for k, v in row.items() if k != "tile" and v not in ("", "-1")]
def patch(c):
    seen, q = {c: 0}, collections.deque([c])
    while q:
        t = q.popleft()
        if seen[t] >= R: continue
        for n in nb[t]:
            if n not in seen and not tiles[n]["waterCovered"]:
                seen[n] = seen[t] + 1; q.append(n)
    return sorted(seen)
STAGE = {"RM_Abyss": 89502, "RM_RustCathedral": 65773}
ROT = 60110
restore = {}
with RimBridge(*resolve_endpoint()) as rb:
    def commit():
        rb.call("jawa/world_commit", {"redraw": True, "clearCaches": False, "recalcPaths": False, "lazy": True}, check=False); time.sleep(6)
    def info():
        return json.dumps(rb.call("jawa/static_call", {"type": "RimMandrake.Biomes.RM_WorldLook", "method": "Info"}, check=False), default=str)[:260]
    orig_blend = rb.call("jawa/mod_settings_field", {"typeName": T, "action": "get", "field": "worldBorderBlend"}, check=False).get("value")
    try:
        for b, c in STAGE.items():
            p = patch(c)
            for t in p: restore[t] = tiles[t]["biome"]
            r = rb.call("jawa/world_tile_set", {"tiles": ",".join(map(str, p)), "biome": b}, check=False)
            print("staged", b, "centre", c, "tiles", len(p), "was", dict(collections.Counter(tiles[t]["biome"] for t in p)), json.dumps(r, default=str)[:200], flush=True)
        for mode, val in (("soft", "true"), ("hard", "false")):
            rb.call("jawa/mod_settings_field", {"typeName": T, "action": "set", "field": "worldBorderBlend", "value": val}, check=False)
            commit(); print(mode, info(), flush=True)
            for name, c in list(STAGE.items()) + [("RM_TheRot", ROT)]:
                for alt in ALTS:
                    rb.call("jawa/clear_ui", {}, check=False)
                    v = rb.call("jawa/world_view", {"centerTile": int(c), "altitude": alt}, check=False); time.sleep(3)
                    s = rb.call("rimworld/take_screenshot", {}, check=False)
                    dst = "%s\\z_%s_%s_%d.png" % (OUT, name, mode, int(alt))
                    try: shutil.copy(s.get("path"), dst); print("shot", dst, v.get("success"), v.get("centerError"), flush=True)
                    except Exception as e: print("SHOT FAILED", name, mode, alt, e, flush=True)
    finally:
        by = collections.defaultdict(list)
        for t, b in restore.items(): by[b].append(t)
        for b, ts in by.items():
            r = rb.call("jawa/world_tile_set", {"tiles": ",".join(map(str, ts)), "biome": b}, check=False)
            print("restored", b, len(ts), r.get("success"), flush=True)
        if orig_blend is not None:
            rb.call("jawa/mod_settings_field", {"typeName": T, "action": "set", "field": "worldBorderBlend", "value": str(orig_blend).lower()}, check=False)
        commit()
        chk = rb.call("jawa/world_tile_get", {"tiles": ",".join(map(str, list(restore)[:400]))}, check=False).get("tiles") or []
        bad = [x["tile"] for x in chk if x.get("biome") != restore.get(x["tile"])]
        print("RESTORE CHECK", len(chk), "read back,", len(bad), "differ", bad[:10], "|", info(), flush=True)
