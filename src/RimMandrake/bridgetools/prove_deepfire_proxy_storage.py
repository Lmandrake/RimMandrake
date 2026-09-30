"""DEEPFIRE_PROXY_BLOCKS_STORAGE_1 -- quicktest, driven over the bridge. NOT YET RUN.

Run under WINDOWS python.exe from the repo root (the bridge binds Windows loopback):
    python.exe src\\RimMandrake\\bridgetools\\prove_deepfire_proxy_storage.py [--start] [--x 60 --z 60]

--start   start a fresh dev quicktest first (rimworld/start_debug_game_ready).
--x/--z   SOUTH-WEST corner of the 6x6 floor; a multiple of 3 so it sits on the 3x3 cluster
          grid (the 4-proxy assertion needs it).

The static floor/wall light proxy (RM_DeepfireLightProxy) used to be category Item. That
shoved an existing item off its cell on spawn (GenSpawn.Spawn's max-items branch) and made
the cell read full to storage (GetItemCount). It is now Ethereal. This proves:
  0  an 8x8 walled room (6x6 WoodPlankFloor interior) -> a 6x6 stockpile with 10 Steel on
     every cell ("Proxy: stockpile + items").
  1  "Floor: coat 6x6" -> 36 coated, EXACTLY 4 floor proxies (DEEPFIRE_FLOOR_PAINT_1's
     proven count is unchanged), proxy category Ethereal, 0 of 36 Steel stacks displaced
     or lost, each proxy cell's GetItemCount is 1 (the Steel only).
  2  "Proxy: clear placed items" -> every proxy cell is valid storage for a WoodLog
     (StoreUtility.IsValidStorageFor), as is every other empty cell.
  3  the wipe-on-spawn bug the def header warns about stays fixed: a Steel wall outside the
     room is coated ("FirstCoat: spawn wall" / "coat thing") and still stands afterwards,
     with a clustered building proxy added.
  4  no new errors naming LuminousPigment/Deepfire.
Exit 0 = every assertion passed, 1 = at least one failed, 2 = could not run.
"""
import argparse
import json
import sys
import time

sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
import deepfire_log_check

TAGS = ("[DeepfireProxy] ", "[DeepfireFloor] ", "[DeepfireFirstCoat] ")
CATEGORY = "Deepfire"
PREFIXES = ("Proxy:", "Floor:", "FirstCoat:")
EXPECTED_PROXIES = 4
CELLS = 36
WALL_OFFSET = 10  # wall cell = (x + WALL_OFFSET, z): outside the 8x8 room

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


def find_actions():
    r = call("rimworld/list_debug_action_children", path="Actions")
    if not r.get("success", True) and not r.get("children"):
        raise SystemExit("debug tree will not enumerate: %s" % json.dumps(r)[:300])
    for c in r.get("children") or []:
        label = c.get("label") or ""
        if label == CATEGORY or (c.get("path") or "").endswith("\\" + CATEGORY):
            sub = call("rimworld/list_debug_action_children", path=c.get("path"))
            return {(leaf.get("label") or ""): leaf.get("path") for leaf in sub.get("children") or []}
    # 1.6 flattens mod categories: the actions sit directly under Actions as "T: Proxy: ..."
    return {(c.get("label") or ""): c.get("path") for c in r.get("children") or []
            if any(p in (c.get("label") or c.get("path") or "") for p in PREFIXES)}


def run(actions, label_part, x=None, z=None):
    path = next((p for l, p in actions.items() if label_part.lower() in l.lower()), None)
    if not path:
        raise SystemExit("no Deepfire debug action matching %r (have: %s)" % (label_part, list(actions)))
    r = call("rimworld/execute_debug_action", path=path, x=X if x is None else x, z=Z if z is None else z)
    logs = [str(x.get("message") if isinstance(x, dict) else x)
            for x in ((r.get("effects") or {}).get("logs") or [])]
    for line in logs:
        for tag in TAGS:
            i = line.find(tag)
            if i >= 0:
                try:
                    return json.loads(line[i + len(tag):].strip())
                except Exception:
                    pass
    print("    (no tagged line; raw result: %s)" % json.dumps(r)[:400])
    return None


def storage(actions, label):
    rep = run(actions, "storage report 6x6")
    print("  [%s] %s" % (label, json.dumps(rep)[:900]))
    if rep is None:
        raise SystemExit("storage report returned nothing parseable")
    return rep


# ---- 0. game + room + stockpile ----
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
    print("no Deepfire dev actions under Actions -- is LuminousPigment (this build) loaded?")
    sys.exit(2)

print("== 0 stockpile + items ==")
a0 = run(actions, "stockpile + items")
check("stock: 36 stockpile cells, 36 Steel stacks placed on their own cells",
      a0 and a0.get("zoneCells") == CELLS and a0.get("items") == CELLS, json.dumps(a0))
r0 = storage(actions, "stocked")
check("stock: no floor proxies yet, nothing displaced", r0["floorLights"] == 0 and r0["displaced"] == 0 and r0["lost"] == 0)

print("== 1 coat under the items ==")
a1 = run(actions, "coat 6x6")
check("coat: 36 added", a1 and a1.get("added") == CELLS, json.dumps(a1))
r1 = storage(actions, "coated")
check("coat: proxy def is category Ethereal", r1["proxyCategory"] == "Ethereal", r1["proxyCategory"])
check("coat: EXACTLY 4 floor proxies (DEEPFIRE_FLOOR_PAINT_1 count unchanged)",
      r1["floorLights"] == EXPECTED_PROXIES and r1["proxyCellsInRect"] == EXPECTED_PROXIES,
      "floorLights=%s inRect=%s" % (r1["floorLights"], r1["proxyCellsInRect"]))
check("coat: the proxies are really spawned in the thing grid", r1["proxiesSeenInGrid"] == EXPECTED_PROXIES,
      "seen=%s" % r1["proxiesSeenInGrid"])
check("coat: 0 of 36 Steel stacks displaced or lost",
      r1["tracked"] == CELLS and r1["displaced"] == 0 and r1["lost"] == 0,
      "tracked=%s displaced=%s lost=%s" % (r1["tracked"], r1["displaced"], r1["lost"]))
check("coat: a proxy cell counts only the Steel (GetItemCount 1)", r1["maxItemCountOnProxyCell"] == 1,
      "max=%s" % r1["maxItemCountOnProxyCell"])

print("== 2 empty the stockpile ==")
a2 = run(actions, "clear placed items")
check("clear: 36 destroyed", a2 and a2.get("destroyed") == CELLS, json.dumps(a2))
r2 = storage(actions, "emptied")
check("storage: all 4 proxy cells accept a WoodLog", r2["proxyCellsValidStorage"] == EXPECTED_PROXIES,
      "valid=%s of %s" % (r2["proxyCellsValidStorage"], r2["proxyCellsInRect"]))
check("storage: all 36 empty cells accept a WoodLog",
      r2["emptyCellsInRect"] == CELLS and r2["emptyCellsValidStorage"] == CELLS,
      "empty=%s valid=%s" % (r2["emptyCellsInRect"], r2["emptyCellsValidStorage"]))
check("storage: still 4 proxies", r2["floorLights"] == EXPECTED_PROXIES)

print("== 3 wall survives its own proxy ==")
wx = X + WALL_OFFSET
floor_before = run(actions, "Floor: report 6x6")
w0 = run(actions, "spawn wall at cell", x=wx, z=Z)
check("wall: spawned", w0 and w0.get("found") and w0.get("def") == "Wall", json.dumps(w0))
w1 = run(actions, "coat thing at cell", x=wx, z=Z)
check("wall: coated to 1", w1 and w1.get("coats") == 1, json.dumps(w1))
w2 = run(actions, "report thing at cell", x=wx, z=Z)
check("wall: still standing after its proxy spawned", w2 and w2.get("found") and w2.get("thingId") == w0.get("thingId"),
      json.dumps(w2))
floor_after = run(actions, "Floor: report 6x6")
if floor_before and floor_after:
    check("wall: a clustered building proxy was added",
          floor_after["clusteredBuildingLights"] == floor_before["clusteredBuildingLights"] + 1,
          "%s -> %s" % (floor_before["clusteredBuildingLights"], floor_after["clusteredBuildingLights"]))
else:
    check("wall: floor report readable", False)

print("== 4 log ==")
new_errors = deepfire_log_check.new_mod_errors(call, LOG_BASE)
check("no LuminousPigment/Deepfire Error-type lines logged (new) during the proof", not new_errors, json.dumps(new_errors[:5]))

failed = [n for n, ok in results if not ok]
print("\n%d/%d passed" % (len(results) - len(failed), len(results)))
for n in failed:
    print("  FAILED:", n)
sys.exit(0 if not failed else 1)
