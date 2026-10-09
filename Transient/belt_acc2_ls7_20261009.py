import sys, json, collections, time
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
SET = "RimMandrake.LongShade.RM_LongShadeSettings"
out = {}
mid = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.call("jawa/set_current_map", mapId=mid)
S.quiet()

def pg(pid):
    return (S.call("jawa/pawn_get", pawn=pid).get("pawns") or [{}])[0]

def stabs(pid):
    return [(h.get("def"), round(h.get("severity") or 0, 1)) for h in pg(pid).get("hediffs", []) if h.get("def") in ("Stab", "Bite", "Cut")]

def place_colonist(x, z):
    r = S.call("jawa/spawn_pawn", kindDef="Colonist", x=x, z=z, faction="player", count=1)
    ps = r.get("pawns") or []
    return ps[0]["id"] if ps else None

def harrok_round(label, enabled, ticks):
    # clear old harroks and colonists near the arena
    S.call("jawa/clear_area", rect="20,50,20,20")
    hk = S.call("jawa/spawn_pawn", kindDef="RM_Harrok", x=30, z=60, faction="none", count=1)
    hid = (hk.get("pawns") or [{}])[0].get("id")
    prey = []
    for dx, dz in [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (-2, 2), (2, -2), (-2, -2), (4, 0), (-4, 0), (0, 4), (0, -4)]:
        pid = place_colonist(30 + dx, 60 + dz)
        if pid:
            S.call("jawa/pawn_force_incapacitate", pawn=pid); prey.append((pid, dx, dz))
    with S.setting(SET, harrokEnabled=enabled):
        samples = []
        t = 0
        for chunk in ticks:
            S.run(chunk); t += chunk
            hit = [(dx, dz, stabs(pid)) for pid, dx, dz in prey]
            hit = [h for h in hit if h[2]]
            samples.append((t, len(hit), hit[:6]))
    out[label] = dict(harrok=hid, prey=len(prey), samples=samples)
    print(label, json.dumps(out[label], default=str)[:900], flush=True)

try:
    harrok_round("harrok_on_short", True, [70, 200, 700, 700])
    harrok_round("harrok_off_short", False, [70, 400])
    # ---- clean patches: lairing RM_Mirrak in shade, then run the gen step
    r = S.call("jawa/spawn_pawn", kindDef="RM_Mirrak", x=70, z=40, faction="none", count=1)
    out["mirrak_spawn"] = (r.get("success"), str(r.get("message"))[:100])
    g = S.call("jawa/run_genstep", genStepDef="RM_GenStep_CleanPatches")
    out["genstep"] = (g.get("success"), str(g.get("message"))[:200], g.get("threw"))
    l = S.call("jawa/list_things", defName="RM_LongShadeCleanPatch", limit=20)
    ths = l.get("things") or []
    out["markers"] = [(t.get("id"), t.get("x"), t.get("z")) for t in ths]
    if ths:
        out["marker_inspect"] = json.dumps(S.call("jawa/inspect_string", thingIds=ths[0]["id"]).get("things"), default=str)[:300]
    print(json.dumps({k: out[k] for k in ("mirrak_spawn", "genstep", "markers", "marker_inspect") if k in out}, default=str), flush=True)
    # ---- stampede
    S.call("jawa/clear_area", rect="40,10,30,30")
    r = S.call("jawa/spawn_pawn", kindDef="RSW_Runyip", x=50, z=20, faction="none", count=8)
    out["herd_spawn"] = (r.get("success"), len(r.get("pawns") or []), str(r.get("message"))[:100])
    fi = S.call("jawa/fire_incident", incidentDef="RM_ShadeStampede", dryRun=True)
    out["stampede_dry"] = json.dumps({k: fi.get(k) for k in fi if k not in ("operation", "state")}, default=str)[:600]
    with S.setting(SET, stampedeEnabled=False):
        fi2 = S.call("jawa/fire_incident", incidentDef="RM_ShadeStampede", dryRun=True)
        out["stampede_dry_off"] = json.dumps({k: fi2.get(k) for k in fi2 if k not in ("operation", "state")}, default=str)[:400]
    print(out["stampede_dry"], flush=True); print(out["stampede_dry_off"], flush=True)
finally:
    json.dump(out, open("Transient/belt_acc2_ls7_raw_20261009.json", "w"), indent=1, default=str)
