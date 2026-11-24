"""Visit 9 (ArchBig; copied from visit 8): stage the labelled savegame for his walk on the freshly reloaded visit-8 site, capture each station, save.

python.exe, bridge held, the site reloaded first (northstar_site.py --reload-only). Stations sit in open deep-ash windows
found from the live terrain (no rock, no water, no building), plus the map's own charred ruin. Saves
PYRELANDS_0.1.0_VISIT9_WALK and stat-diffs the Saves folder (exactly that file new or changed). Captures go to
Transient/pv9/shots (originals) for looking at; the record keeps copies under 1 MB."""
import sys, json, os, time, shutil, collections
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
SAVES = os.path.join(os.environ["RM_GAME_USERDATA"], "Saves") if os.environ.get("RM_GAME_USERDATA") else \
    os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves")
NAME = sys.argv[1] if len(sys.argv) > 1 else "PYRELANDS_0.1.0_VISIT9_WALK"   # his full list: ..._VISIT9_WALK
SHOTS = r"Transient\pv9\shots"
TAG = "pyre_visit9"
h, p, tk = resolve_endpoint()
out = {"stations": [], "shots": []}
with RimBridge(h, p, tk) as rb:
    call = lambda tool, **kw: rb.call(tool, kw)  # noqa: E731
    r = call("jawa/get_terrain_batch", rects="0,0,250,250")
    cells = {}
    for op in str(r.get("ops") or "").split(";"):
        d, _, rr = op.partition(":")
        try:
            ox, oz, ow, oh = (int(v) for v in rr.split(","))
        except ValueError:
            continue
        for cx in range(ox, ox + ow):
            for cz in range(oz, oz + oh):
                cells[(cx, cz)] = d
    def open_window(x, z, w, hh):
        return all(str(cells.get((cx, cz), "")).startswith("RM_FE_Ash") for cx in range(x, x + w) for cz in range(z, z + hh))
    wins = []
    for z in range(20, 230, 6):
        for x in range(20, 230, 6):
            if open_window(x, z, 20, 16) and all(abs(x - a) > 40 or abs(z - b) > 40 for a, b in wins):
                wins.append((x, z))
    out["windows"] = wins[:8]
    if len(wins) < 4:
        print("UNMEASURED: only %d open 20x16 ash windows" % len(wins)); sys.exit(2)
    (fx, fz), (cx_, cz_), (sx, sz), (rx, rz) = wins[0], wins[1], wins[2], wins[3]
    call("jawa/map_fire", action="extinguish", rect="0,0,250,250")
    call("jawa/weather_set", unlock=True)
    # 1. a live burn front in fresh ember grass
    call("jawa/set_plants", ops="RM_FE_Plant_EmberGrass:%d,%d,20,16" % (fx, fz), growth=1.0)
    fire = call("jawa/map_fire", action="start", rect="%d,%d,2,16" % (fx, fz), fireSize=1.2)
    # 3. scorch-fruit standing in a burned pad
    call("jawa/set_plants", ops="RM_FE_Plant_ScorchFruit:%d,%d,4,4" % (sx + 8, sz + 6), growth=1.0)
    # 4. ember grass under a constructed roof (it withers within about a day), beside an open patch
    call("jawa/set_plants", ops="RM_FE_Plant_EmberGrass:%d,%d,5,5;RM_FE_Plant_EmberGrass:%d,%d,5,5" % (rx + 3, rz + 5, rx + 12, rz + 5), growth=1.0)
    call("jawa/set_roof_batch", ops="RoofConstructed:%d,%d,5,5" % (rx + 3, rz + 5))
    # a fire lit on a paused map is not drawn before its first ticks (visit 8): the save must show the burn front at once
    out["advance"] = (call("jawa/safe_advance", ticks=600) or {}).get("message")
    # 2. the creatures, wild, after the advance: in 600 ticks they walked out of their station (visit 9)
    for i in range(6):
        call("jawa/spawn_pawn", kindDef="RM_Ullai", x=cx_ + 2 + i * 2, z=cz_ + 4, faction="none", count=1)
    call("jawa/spawn_pawn", kindDef="RM_FurnaceBeast", x=cx_ + 8, z=cz_ + 10, faction="none", count=1)
    for i in range(2):
        call("jawa/spawn_pawn", kindDef="RM_Ashwallow", x=cx_ + 15 + i * 2, z=cz_ + 10, faction="none", count=1)
    # 5. the map's own charred ruin
    # limit 2000 truncated on this grass-carpeted map and returned one charred wall (2026-11-21); read past it
    ex = call("jawa/export_things", rect="0,0,250,250", includePawns=False, includeItems=False, limit=100000)
    out["exportCount"], out["exportTruncated"] = ex.get("count"), ex.get("truncated")
    walls = [w for w in ex.get("things") or [] if "Wall" in str(w.get("def")) and w.get("paint") == "RM_FE_Charred"]
    ruin = None
    if len(walls) >= 4:
        # the wall with the most charred walls within 8 cells: a per-axis median of scattered ruins lands on open
        # ground or rock (the first save framed a rock outcrop this way)
        pts = [(int(w.get("x", 0)), int(w.get("z", 0))) for w in walls]
        ruin = max(pts, key=lambda a: sum(abs(a[0] - b[0]) <= 8 and abs(a[1] - b[1]) <= 8 for b in pts))
        out["ruinCluster"] = sum(abs(ruin[0] - b[0]) <= 8 and abs(ruin[1] - b[1]) <= 8 for b in pts)
        if out["ruinCluster"] < 4:
            ruin = None   # a lone charred wall is not a ruin to walk to; the station is dropped and recorded
    stations = [(fx + 10, fz + 17, "VISIT9: LIVE burn front in fresh ember grass - unpause and watch it walk", (fx, fz, 20, 16)),
                (cx_ + 10, cz_ + 17, "VISIT9: creatures - ullai herd, furnace-beast giant, ashwallows", (cx_, cz_, 20, 16)),
                (sx + 10, sz + 12, "VISIT9: scorch-fruit standing in ash", (sx + 4, sz + 2, 12, 12)),
                (rx + 10, rz + 12, "VISIT9: ember grass under a roof (left) withers within a day; open patch (right) stays", (rx, rz, 20, 16))]
    if ruin:
        stations.append((ruin[0], ruin[1] + 6, "VISIT9: charred ruin on deep ash (walls painted RM_FE_Charred)",
                         (ruin[0] - 8, ruin[1] - 6, 16, 12)))
    call("jawa/settle_tweens")
    call("jawa/review_label", action="clear", tag=TAG)
    lab = call("jawa/review_label", action="add", tag=TAG, ops="\n".join("%d|%d|%s" % (x, z, s) for x, z, s, _ in stations))
    call("rimworld/set_time_speed", speed=0)
    out.update({"fire": fire.get("firesStarted"), "ruinWalls": len(walls), "labels": lab.get("success"),
                "stations": [s for _, _, s, _ in stations]})
    os.makedirs(SHOTS, exist_ok=True)
    for i, (x, z, s, (qx, qz, qw, qh)) in enumerate(stations):
        call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % (qx, qz, qw, qh))
        call("jawa/clear_ui"); call("rimworld/jump_camera_to_cell", x=qx + qw // 2, z=qz + qh // 2)
        call("rimworld/frame_cell_rect", x=qx, z=qz, width=qw, height=qh, paddingCells=3); time.sleep(0.4)
        pth = call("rimworld/take_screenshot", fileName="pv9_walk_station_%d" % i).get("path")
        if pth:
            shutil.copy(pth, SHOTS); out["shots"].append(os.path.join(SHOTS, os.path.basename(pth)))
    before = {f: os.stat(os.path.join(SAVES, f)).st_mtime for f in os.listdir(SAVES)}
    r = call("rimworld/save_game", saveName=NAME)
    time.sleep(4)
    after = {f: os.stat(os.path.join(SAVES, f)).st_mtime for f in os.listdir(SAVES)}
    out["save"] = {"success": r.get("success"), "path": r.get("path"),
                   "new": [f for f in after if f not in before],
                   "changed": [f for f in before if f in after and after[f] != before[f]],
                   "bytes": os.path.getsize(os.path.join(SAVES, NAME + ".rws")) if os.path.exists(os.path.join(SAVES, NAME + ".rws")) else None}
print(json.dumps(out, indent=1))
json.dump(out, open(r"design\concepts\Pyrelands\version\in_game\visit_9\evidence\walk_save.json", "w"), indent=1)
