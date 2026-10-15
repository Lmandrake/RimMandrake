"""r5 S2 BURROW_TIMEOUT_FIX_DEJA_VU_CURED. On the loaded Pyrelands fixture: pick a wild RM_Ashwallow the FIXTURE holds,
light a 6x6 fire 4 cells from it, step until it shows RM_Burrowed; compress the 60000-tick burrow limit with a declared
time_set_ticks (+60500, timeException) so the hide toil times out with fire still near (NoteTimeout); A2: 1200 more ticks
beside the fire -> no re-burrow (cooldown 7500). Then reload the fixture (the earlier tick) and burn beside the SAME id:
A1 PASS iff it shows RM_Burrowed within 1500 ticks (a static table would refuse it)."""
import sys, os, json, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
U = os.path.join(ROOT, "src", "RimMandrake", "Utils")
sys.path.insert(0, U); sys.path.insert(0, os.path.join(U, "modcheck"))
import validation_core as V
import clockgate as CG
out_path = sys.argv[1]
SITE = ["python.exe", "src/RimMandrake/Pyrelands/northstar_site.py", "--site", "1", "--fingerprint", "417df172fdb5", "--tag",
        "r6", "--reload-only", "--tile", "5", "--work", r"D:\Luke\dev\_rmscratch\bench_live_20261015_r5\sites"]
B = V.Bridge()
res = {"steps": []}
def log(k, v):
    res["steps"].append({k: v}); print(k, json.dumps(v, default=str)[:400], flush=True)
    json.dump(res, open(out_path, "w"), indent=1, default=str)
def pawns():
    return (B.call("jawa/list_pawns", limit=2000, includeHealth=True) or {}).get("pawns") or []
def row(pid):
    return next((p for p in pawns() if p.get("id") == pid), None)
def burrowed(r):
    return "RM_Burrowed" in json.dumps(((r or {}).get("health") or {}).get("hediffs") or [])
def tick():
    return (B.call("rimworld/get_game_info") or {}).get("ticksGame")
def fire_near(p):
    x, z = p["x"], p["z"]
    fx = x - 6 if x > 20 else x + 2
    return B.call("jawa/map_fire", action="start", rect="%d,%d,4,4" % (fx, z - 2), fireSize=1.2)
def wait_burrow(pid, steps=15):
    for i in range(steps):
        CG.advance_chunk(B, 100)
        r = row(pid)
        if burrowed(r):
            return i + 1, r
    return None, row(pid)
import subprocess
def reload():
    B.call("rimworld/load_game", saveName="R5_S2_fixture")
    for _ in range(200):
        time.sleep(2)
        try:
            gi = B.call("rimworld/get_game_info") or {}
        except Exception:
            continue
        if (gi.get("state") or {}).get("programState") == "Playing" and gi.get("ticksGame") is not None:
            break
    time.sleep(20)
    return {"tick": tick()}
try:
    o = subprocess.run(SITE, capture_output=True, text=True, timeout=400)
    log("site", (o.stdout.strip().splitlines() or [""])[-1][:160])
    cols0 = [p for p in pawns() if p.get("isPlayer")]
    sx = int(sum(p["x"] for p in cols0) / max(1, len(cols0))); sz = int(sum(p["z"] for p in cols0) / max(1, len(cols0)))
    sxx = sx + 45 if sx < 180 else sx - 45
    log("spawn", {k: v for k, v in (B.call("jawa/spawn_pawn", kindDef="RM_Ashwallow", x=sxx, z=sz, faction="none") or {}).items() if k in ("success", "message")})
    CG.advance_chunk(B, 2)
    log("save", (B.call("rimworld/save_game", saveName="R5_S2_fixture") or {}).get("exists"))
    log("reload0", reload())
    cols = [p for p in pawns() if p.get("isPlayer")]
    cx = sum(p["x"] for p in cols) / max(1, len(cols)); cz = sum(p["z"] for p in cols) / max(1, len(cols))
    ash = [p for p in pawns() if p.get("kindDef") == "RM_Ashwallow" and not p.get("downed") and not p.get("dead")]
    ash.sort(key=lambda p: -((p["x"] - cx) ** 2 + (p["z"] - cz) ** 2))
    log("ashwallows", [(p["id"], p["x"], p["z"]) for p in ash][:6])
    if not ash:
        log("verdict", "UNMEASURED no RM_Ashwallow on the fixture"); sys.exit(2)
    g = ash[0]; gid = g["id"]
    log("fire1", fire_near(g))
    n, r = wait_burrow(gid)
    log("burrow1", {"afterSteps": n, "burrowed": burrowed(r), "tick": tick()})
    if not n:
        log("verdict", "UNMEASURED it never burrowed"); sys.exit(2)
    t0 = tick()
    log("jump", B.call("jawa/time_set_ticks", ticks=t0 + 60500, timeException=True, why="S2: compress BurrowMaxTicks 60000"))
    CG.advance_chunk(B, 60, time_exception=True)
    r = row(gid)
    fires = (B.call("jawa/map_fire", action="status") or {})
    log("after_timeout", {"burrowed": burrowed(r), "tick": tick(), "fireStatus": {k: fires.get(k) for k in ("fireCount", "fires", "count")}})
    timed_out = not burrowed(r)
    # A2: stays up for the cooldown while fire is near
    log("fire2", fire_near(r or g))
    seen = False
    for _ in range(12):
        CG.advance_chunk(B, 100)
        if burrowed(row(gid)):
            seen = True; break
    log("A2", {"timedOut": timed_out, "reburrowedWithinCooldown": seen})
    a2 = "PASS" if timed_out and not seen else ("UNMEASURED" if not timed_out else "FAIL")
    # A1: reload the fixture (earlier tick) and burn beside the same id
    log("reload1", reload())
    g2 = row(gid)
    if not g2:
        log("verdict", {"A2": a2, "A1": "UNMEASURED same id not on the reloaded map"}); sys.exit(2)
    log("fire3", fire_near(g2))
    n2, r2 = wait_burrow(gid)
    a1 = "PASS" if n2 else "FAIL"
    log("verdict", {"A1": a1, "A1steps": n2, "A2": a2, "id": gid})
finally:
    try:
        B.call("jawa/map_fire", action="extinguish", rect="0,0,250,250")
    except Exception:
        pass
