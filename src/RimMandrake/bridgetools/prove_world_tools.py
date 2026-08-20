"""W3 proof: tile scalars round-trip, and the change is VISIBLE on the planet.

Run under Windows python:  python.exe src/RimMandrake/bridgetools/prove_world_tools.py
"""
import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb

host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=300.0)
S.connect()

def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r

print("== quicktest ==")
print("  ", call("rimworld/start_debug_game_ready", timeoutMs=280000,
                 readiness="mapData", pauseIfNeeded=True).get("message"))
# CameraJumper.TryShowWorld() returns false unless ProgramState == Playing, and
# "mapData" readiness does NOT guarantee that. Wait for the real thing.
import time
for _ in range(120):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing": break
    time.sleep(1)
print("   programState:", st.get("programState"))

print("== biome histogram BEFORE ==")
b4 = call("jawa/world_stats")
h4 = b4.get("biomes") or {}
print("   tiles:", b4.get("tilesTotal"), " IceSheet:", h4.get("IceSheet"),
      " water%:", b4.get("waterPct"), " top:", list(h4.items())[:4])

print("== PAINT a big obvious band: 4000 tiles -> IceSheet ==")
w = call("jawa/world_tile_set", range="20000-23999", biome="IceSheet",
         elevation=900.0, hilliness="Mountainous", temperature=-45.0, readBack=2)
print("   written:", w.get("written"), "errors:", (w.get("errors") or [])[:2])

print("== COMMIT ==")
c = call("jawa/world_commit")
print("   success:", c.get("success"), "failed:", c.get("failedSteps"))

print("== biome histogram AFTER ==")
af = call("jawa/world_stats")
ha = af.get("biomes") or {}
print("   IceSheet:", h4.get("IceSheet"), "->", ha.get("IceSheet"),
      " delta:", (ha.get("IceSheet") or 0) - (h4.get("IceSheet") or 0))
print("   water%:", b4.get("waterPct"), "->", af.get("waterPct"),
      "(elevation 900 lifted 4000 tiles out of the sea)")

print("== SHOW THE PLANET ==")
v = call("jawa/world_view", show=True, centerTile=22000)
print("  ", {k: v.get(k) for k in ("acted","worldSelectedBefore","worldSelectedAfter","wantedMode","centeredOn")})

print("== close dialogs, then screenshot ==")
for wt in ("LudeonTK.Dialog_DevPalette", "LudeonTK.EditWindow_Log", "LudeonTK.Dialog_Debug"):
    call("rimworld/close_window", windowType=wt)
sh = call("rimworld/take_screenshot", fileName="w3_planet_painted", suppressMessage=True)
print("   screenshot:", sh.get("success"), sh.get("path") or sh.get("fileName") or sh)
