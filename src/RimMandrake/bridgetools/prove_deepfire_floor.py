"""DEEPFIRE_FLOOR_PAINT_1 -- spec §10 step 6 quicktest, driven over the bridge.

Run under WINDOWS python.exe from the repo root (the bridge binds Windows loopback):
    python.exe src\\RimMandrake\\bridgetools\\prove_deepfire_floor.py [--start] [--x 60 --z 60]

--start   start a fresh dev quicktest first (rimworld/start_debug_game_ready); omit to use
          the map already loaded.
--x/--z   SOUTH-WEST corner of the 6x6 floor. Must be a multiple of 3 so the floor sits on
          the 3x3 cluster grid (an unaligned 6x6 straddles nine blocks -> nine proxies).

What it does (every step goes through the mod's own "Deepfire" dev actions, which call the
same entry points the player path does, so the Harmony postfixes are what is exercised):
  0  jawa/make_empty_room builds an 8x8 walled, roofed room whose 6x6 interior is the floor
     (WoodPlankFloor) -> baseline report.
  1  "Floor: coat 6x6"          -> 36 cells coated, EXACTLY 4 floor proxies, glow at the
                                   centre rises, room Beauty rises by
                                   36*0.5 / CellCountCurve(roomCells) + 6 (the room line:
                                   2 per 10 coated cells, floor(36/10)=3 -> +6).
  2  "Floor: vanilla-paint red" -> TerrainGrid.SetTerrainColor postfix: colour def is
                                   Structure_Red, still 4 proxies, visual glow red-dominant.
  3  "Floor: strip coats"       -> grid zero, 0 floor proxies, room Beauty back to baseline.
  4  re-coat, then "Floor: remove floor" (TerrainGrid.RemoveTopLayer ->
     DoTerrainChangedEffects postfix) -> grid zero, 0 floor proxies, no floor cells left.
  5  no new errors in the log naming LuminousPigment/Deepfire.
Exit 0 = every assertion passed, 1 = at least one failed, 2 = could not run.

NOTE on the spec's arithmetic: §10 row 6 says the readout "rises by 36 x 0.5 per-cell plus
the +6 room line". RoomStatWorker_Beauty.GetScore DIVIDES the per-cell sum by
CellCountCurve (0->20, 40->40; 38 for a 36-cell room), so the per-cell part of the rise is
18/38 ~= 0.47, not 18. This script asserts the engine's real formula.
"""
import argparse
import json
import sys
import time

sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
import deepfire_log_check

TAG = "[DeepfireFloor] "
CATEGORY = "Deepfire"

ap = argparse.ArgumentParser()
ap.add_argument("--start", action="store_true")
ap.add_argument("--x", type=int, default=60)
ap.add_argument("--z", type=int, default=60)
args = ap.parse_args()
X, Z = args.x, args.z
if X % 3 or Z % 3:
    print("WARNING: (%d,%d) is not on the 3x3 cluster grid; the 4-proxy assertion will fail." % (X, Z))

host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
S.connect()


def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except Exception:
            pass
    return r


results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", name, detail))


def near(a, b, tol=0.01):
    return a is not None and b is not None and abs(a - b) <= tol


def curve(n):
    # RimWorld/RoomStatWorker_Beauty.CellCountCurve (RimSage): (0,20) (40,40) (100000,100000)
    if n <= 40:
        return 20.0 + n * 0.5
    return float(n)  # the (40,40)->(100000,100000) segment is the identity


# ---- debug-action discovery: read the leaf paths, never construct them ----
def find_actions():
    r = call("rimworld/list_debug_action_children", path="Actions")
    if not r.get("success", True) and not r.get("children"):
        raise SystemExit("debug tree will not enumerate: %s" % json.dumps(r)[:300])
    for c in r.get("children") or []:
        label = c.get("label") or ""
        if label == CATEGORY or (c.get("path") or "").endswith("\\" + CATEGORY):
            sub = call("rimworld/list_debug_action_children", path=c.get("path"))
            return {(leaf.get("label") or ""): leaf.get("path") for leaf in sub.get("children") or []}
    # 1.6 flattens mod categories: the actions sit directly under Actions as "T: Floor: ..."
    return {(c.get("label") or ""): c.get("path") for c in r.get("children") or []
            if "Floor:" in (c.get("label") or c.get("path") or "")}


def run(actions, label_part):
    path = next((p for l, p in actions.items() if label_part.lower() in l.lower()), None)
    if not path:
        raise SystemExit("no Deepfire debug action matching %r (have: %s)" % (label_part, list(actions)))
    r = call("rimworld/execute_debug_action", path=path, x=X, z=Z)
    logs = [str(x.get("message") if isinstance(x, dict) else x)
            for x in ((r.get("effects") or {}).get("logs") or [])]
    for line in logs:
        i = line.find(TAG)
        if i >= 0:
            try:
                return json.loads(line[i + len(TAG):].strip())
            except Exception:
                pass
    print("    (no %s line; raw result: %s)" % (TAG.strip(), json.dumps(r)[:400]))
    return None


def report(actions, label):
    rep = run(actions, "report 6x6")
    print("  [%s] %s" % (label, json.dumps(rep)[:900]))
    if rep is None:
        raise SystemExit("report action returned nothing parseable")
    return rep


# ---- 0. game + room ----
if args.start:
    r = call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
    print("start_debug_game_ready:", json.dumps(r)[:300])
st = {}
for _ in range(90):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing":
        break
    time.sleep(1)
if st.get("programState") != "Playing":
    print("not Playing:", st.get("programState"))
    sys.exit(2)

LOG_BASE = deepfire_log_check.baseline(call)  # errors already in the buffer do not count

room = call("jawa/make_empty_room", rect="%d,%d,8,8" % (X - 1, Z - 1),
            wallDef="Wall", stuffDef="WoodLog", floorDef="WoodPlankFloor")
print("make_empty_room:", json.dumps(room)[:300])
if not room.get("success"):
    sys.exit(2)

actions = find_actions()
print("Deepfire dev actions:", sorted(actions))
if not actions:
    print("no 'Deepfire' category under Actions -- is LuminousPigment (this build) loaded?")
    sys.exit(2)

print("== 0 baseline ==")
r0 = report(actions, "baseline")
check("baseline: 36 floor cells, 0 coated, 0 floor proxies",
      r0["floorCellsInRect"] == 36 and r0["coatedInRect"] == 0 and r0["floorLights"] == 0,
      "floor=%s coated=%s lights=%s" % (r0["floorCellsInRect"], r0["coatedInRect"], r0["floorLights"]))
check("baseline: room is the 36-cell interior", r0["roomCells"] == 36 and r0["roomOutdoors"] is False,
      "roomCells=%s outdoors=%s" % (r0["roomCells"], r0["roomOutdoors"]))

print("== 1 coat ==")
a1 = run(actions, "coat 6x6")
check("coat: 36 added", a1 and a1.get("added") == 36, json.dumps(a1))
r1 = report(actions, "coated")
check("coat: grid holds 36 coated cells (1 coat each)", r1["coatedInRect"] == 36 and r1["coatSumInRect"] == 36)
check("coat: EXACTLY 4 floor proxies (one per 3x3 block)", r1["floorLights"] == 4,
      "floorLights=%s list=%s" % (r1["floorLights"], r1["floorLightList"]))
check("coat: centre glow rose above baseline and is > 0",
      r1["centerGroundGlow"] > 0 and r1["centerGroundGlow"] > r0["centerGroundGlow"],
      "%.4f -> %.4f" % (r0["centerGroundGlow"], r1["centerGroundGlow"]))
check("coat: CellBeauty at centre +0.5", near(r1["centerCellBeauty"] - r0["centerCellBeauty"], 0.5),
      "%.4f -> %.4f" % (r0["centerCellBeauty"], r1["centerCellBeauty"]))
check("coat: room line = +6 (36 coated cells)", near(r1["roomDeepfireBonus"], 6.0) and r1["roomCoatedCells"] == 36,
      "bonus=%s coatedInRoom=%s" % (r1["roomDeepfireBonus"], r1["roomCoatedCells"]))
expected_rise = 36 * 0.5 / curve(r0["roomCells"]) + 6.0
check("coat: room Beauty rises by 18/CellCountCurve(n) + 6",
      near(r1["roomBeauty"] - r0["roomBeauty"], expected_rise, 0.02),
      "%.4f -> %.4f (rise %.4f, expected %.4f)" % (r0["roomBeauty"], r1["roomBeauty"],
                                                   r1["roomBeauty"] - r0["roomBeauty"], expected_rise))

print("== 2 vanilla paint red ==")
a2 = run(actions, "paint 6x6 red")
check("paint: Structure_Red found and 36 cells painted", a2 and a2.get("colorDefFound") and a2.get("painted") == 36,
      json.dumps(a2))
r2 = report(actions, "red")
v = r2["centerVisual"]
check("paint: colour def at centre is Structure_Red", r2["centerColorDef"] == "Structure_Red", r2["centerColorDef"])
check("paint: coats kept, still 4 proxies", r2["coatedInRect"] == 36 and r2["floorLights"] == 4,
      "coated=%s lights=%s" % (r2["coatedInRect"], r2["floorLights"]))
check("paint: visual glow at centre is red-dominant", v[0] > v[1] and v[0] > v[2], "rgb=%s (was %s)" % (v, r1["centerVisual"]))

print("== 3 strip coats (remove deepfire) ==")
a3 = run(actions, "strip coats")
check("strip: 36 stripped", a3 and a3.get("stripped") == 36, json.dumps(a3))
r3 = report(actions, "stripped")
check("strip: grid zero, 0 floor proxies", r3["coatedInRect"] == 0 and r3["floorLights"] == 0,
      "coated=%s lights=%s" % (r3["coatedInRect"], r3["floorLights"]))
check("strip: room Beauty back to baseline", near(r3["roomBeauty"], r0["roomBeauty"], 0.02),
      "%.4f vs baseline %.4f" % (r3["roomBeauty"], r0["roomBeauty"]))
check("strip: room line gone", near(r3["roomDeepfireBonus"], 0.0))

print("== 4 re-coat, then remove the floor ==")
a4 = run(actions, "coat 6x6")
r4a = report(actions, "recoated")
check("recoat: 36 coated, 4 proxies", r4a["coatedInRect"] == 36 and r4a["floorLights"] == 4)
a5 = run(actions, "remove floor")
check("remove floor: 36 cells lost their floor", a5 and a5.get("removed") == 36, json.dumps(a5))
r5 = report(actions, "floor removed")
check("remove floor: grid zero, 0 floor proxies, no floor left",
      r5["coatedInRect"] == 0 and r5["floorLights"] == 0 and r5["floorCellsInRect"] == 0,
      "coated=%s lights=%s floorCells=%s" % (r5["coatedInRect"], r5["floorLights"], r5["floorCellsInRect"]))
check("remove floor: room line gone", near(r5["roomDeepfireBonus"], 0.0))

print("== 5 log ==")
new_errors = deepfire_log_check.new_mod_errors(call, LOG_BASE)
check("no LuminousPigment/Deepfire Error-type lines logged (new) during the proof", not new_errors, json.dumps(new_errors[:5]))

failed = [n for n, ok in results if not ok]
print("\n%d/%d passed" % (len(results) - len(failed), len(results)))
for n in failed:
    print("  FAILED:", n)
sys.exit(0 if not failed else 1)
