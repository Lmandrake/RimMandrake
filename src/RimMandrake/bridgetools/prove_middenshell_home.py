"""Prove the Middenshell on the HOME map (a generated side map with no colonists gets culled):
regenerate the current debug map as RM_Wasteland, fire RM_MiddenshellArrives, run, and read its
footprint + position over time. Windows python.exe, repo root:
    python.exe src/RimMandrake/bridgetools/prove_middenshell_home.py"""
import sys, json, time, os, re
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
LOG = os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log")
h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=300.0); S.connect()
def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    if isinstance(r, dict): r.pop("operation", None)
    return r
tile = call("jawa/map_info").get("tile")
call("jawa/world_tile_set", tiles=str(tile), biome="RM_Wasteland"); call("jawa/world_commit")
call("rimworld/execute_debug_action", path=r"Actions\Regenerate Current Map"); time.sleep(5)
for _ in range(100):
    if call("rimworld/get_ui_state").get("programState") == "Playing": break
    time.sleep(3)
print("biome:", call("jawa/map_info").get("mapBiome"))
since = os.path.getsize(LOG)
f = call("jawa/fire_incident", incidentDef="RM_MiddenshellArrives")
print("fire:", str(f)[:200])
def read():
    r = call("jawa/list_things", defName="RM_Middenshell")
    th = (r.get("things") or [None])[0]
    return th and {k: th.get(k) for k in ("id", "x", "z", "rot", "hitPoints", "size", "def")}
first = read(); print("read 1:", first)
call("rimworld/set_time_speed", speed="Superfast"); call("rimworld/pause_game", pause=False)
positions = [first]
for i in range(6):
    time.sleep(20)
    r = read(); positions.append(r); print("read", i + 2, r)
call("rimworld/pause_game", pause=True)
with open(LOG, "rb") as fh: fh.seek(since); txt = fh.read().decode("utf-8", "replace")
errs = list(dict.fromkeys(l[:260] for l in txt.split("\n") if not l.startswith(("  at ", "  - ")) and re.search(r"Exception|rror", l)))[:15]
mid = [l[:260] for l in txt.split("\n") if "iddenshell" in l][-10:]
moved = len({(p["x"], p["z"]) for p in positions if p}) > 1
alive = positions[-1] is not None
print("log:", mid); print("errors:", errs)
print("VERDICT spawned=%s alive_at_end=%s moved=%s" % (first is not None, alive, moved))
