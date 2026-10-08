import sys, json, re, time
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rbc
host, port, token = rbc.resolve_endpoint()
LOG = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"
def act(rb, label, tag):
    n = len(open(LOG, errors="ignore").read().splitlines())
    r = rb.call("rimworld/execute_debug_action", {"path": "Actions\\" + label}, check=False)
    time.sleep(1.5)
    ls = [l for l in open(LOG, errors="ignore").read().splitlines()[n:] if tag in l]
    return ls[-1] if ls else "(no line; %s)" % str(r)[:100]
def step(rb, n): rb.call("rimworld/step_game_ticks", {"ticks": n}, check=False)
with rbc.RimBridge(host, port, token, timeout=240.0) as rb:
    print("clear", act(rb, "Clear debug refuge ledges (current map)", "RMFloodedCanyonDebug")[:120])
    led = rb.call("jawa/list_things", {"defName": "RM_MercyLedge", "limit": 400}, check=False)["things"]
    pts = [(l["x"], l["z"]) for l in led]
    best = max(((x, z) for x in range(30, 220, 12) for z in range(30, 220, 12)), key=lambda c: min((c[0]-a)**2+(c[1]-b)**2 for a, b in pts))
    print("far spot", best, "ledges", len(pts))
    x, z = best
    m = rb.call("jawa/spawn_pawn", {"kindDef": "Muffalo", "x": x, "z": z, "faction": "PlayerColony", "count": 1}, check=False)
    print("muffalo", str(m)[:160])
    for fac in ("neutral", "Outlander", "OutlanderCivil", "Pirate-"):
        v = rb.call("jawa/spawn_pawn", {"kindDef": "Villager", "x": x+3, "z": z+3, "faction": fac, "count": 1}, check=False)
        print("visitor", fac, v.get("success"), str(v.get("message"))[:140])
        if v.get("success") and v.get("spawnedCount"): break
    print("teach", act(rb, "Teach player animals Obedience (current map)", "RMFloodedCanyonDebug")[:120])
    print("pre ", act(rb, "Report ledge refuge (current map)", "refuge:")[:400])
    print("arm ", act(rb, "Arm chime + flood soon (current map)", "RMFloodedCanyonDebug")[:200])
    step(rb, 30); print("t+30", act(rb, "Report ledge refuge (current map)", "refuge:")[:400])
    step(rb, 600); print("t+630", act(rb, "Report ledge refuge (current map)", "refuge:")[:400])
    step(rb, 1200); print("t+1830", act(rb, "Report ledge refuge (current map)", "refuge:")[:400])
    print("flood", act(rb, "Report flood state (current map)", "RMFloodedCanyonDebug")[:600])
