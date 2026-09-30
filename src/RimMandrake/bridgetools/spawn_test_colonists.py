"""Spawn N player colonists near the map centre and close the faction-naming dialog that their
arrival opens (it force-pauses the game). Windows python.exe, repo root:
    python.exe src/RimMandrake/bridgetools/spawn_test_colonists.py [N]"""
import sys, json, time
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=120.0); S.connect()
def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
mi = call("jawa/map_info"); n = int(sys.argv[1]) if len(sys.argv) > 1 else 2
r = call("jawa/spawn_pawn", kindDef="Colonist", x=mi["sizeX"] // 2, z=mi["sizeZ"] // 2, faction="player", count=n)
print("spawned:", r.get("spawnedCount"))
time.sleep(2)
for _ in range(5):
    call("rimworld/close_window", windowType="Dialog_NamePlayerFactionAndSettlement")
    if not call("rimworld/get_ui_state").get("windowsForcePause"): break
    time.sleep(1)
print("forcePause:", call("rimworld/get_ui_state").get("windowsForcePause"))
