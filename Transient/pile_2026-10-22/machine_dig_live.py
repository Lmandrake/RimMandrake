"""machine_dig_live.py -- DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL live rows (design/RimMandrake/machine_dig_2026-10-21.md §8).
python.exe Transient/pile_2026-10-22/machine_dig_live.py X,Z   (repo root; bridge held; any map with a free colonist)
Probe-based: jawa/flowworks_job_probe asks the designator + WorkGiver for ONE pawn on ONE cell (nothing ordered).
Cell staged at D=4 notches (2 m, the colonist cap) and designated RM_DigCanal; then a real dig with ticks.
"""
import json, sys, os
sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint

S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
x0, z0 = (int(v) for v in sys.argv[1].split(","))
out = {}
h, p, t = resolve_endpoint()
with RimBridge(h, p, t) as B:
    def call(n, **a):
        try:
            return B.call(n, a) or {}
        except Exception as e:  # noqa
            return {"success": False, "error": str(e)[:300]}
    def sget(f):
        return call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f)
    def sset(f, v):
        return call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))
    out["settings0"] = {f: sget(f).get("value") for f in ("maxDigDepth", "machineDigEnabled", "maxMachineDigDepth", "digToDepthEnabled")}
    spc = call("jawa/spawn_pawn", kindDef="Colonist", x=x0 - 2, z=z0 - 2, faction="player", count=1)
    pc = (spc.get("pawns") or [{}])[0]
    col = {"pawnId": pc.get("id"), "name": pc.get("name"), "position": [pc.get("x"), pc.get("z")]}
    ctl = (x0 + 4, z0)
    out["digCtl2"] = call("jawa/flowworks_excavation_drive", x=ctl[0], z=ctl[1], deepenLevels=2, setFill=-1)
    out["desCtl"] = call("jawa/designate_batch", action="add", designation="RM_DigCanal", rect="%d,%d,1,1" % ctl)
    out["colonist"] = col and {k: col.get(k) for k in ("pawnId", "name", "position")}
    c = (x0, z0)
    out["dig4"] = call("jawa/flowworks_excavation_drive", x=x0, z=z0, deepenLevels=4, setFill=-1)
    out["des"] = call("jawa/designate_batch", action="add", designation="RM_DigCanal", rect="%d,%d,1,1" % c)
    sp = call("jawa/spawn_pawn", kindDef="Mech_Tunneler", x=x0 + 2, z=z0 + 2, faction="player", count=1)
    out["spawnTunneler"] = sp
    tid = None
    for k in ("pawnIds", "ids", "pawns", "spawned"):
        v = sp.get(k)
        if v:
            tid = v[0] if isinstance(v[0], str) else (v[0].get("pawnId") or v[0].get("id"))
            break
    out["tunnelerId"] = tid
    cid = (col or {}).get("pawnId", "")
    cid_bare = cid.replace("Thing_", "")
    def pr(pid):
        return call("jawa/flowworks_job_probe", x=x0, z=z0, kind="dig", pawnId=pid)
    out["probe_colonist_on"] = pr(cid_bare)
    out["probe_colonist_ctl_D2"] = call("jawa/flowworks_job_probe", x=ctl[0], z=ctl[1], kind="dig", pawnId=cid_bare)
    out["probe_tunneler_on"] = pr(tid) if tid else None
    out["setMachineOff"] = sset("machineDigEnabled", False)
    out["probe_tunneler_off"] = pr(tid) if tid else None
    out["probe_colonist_off"] = pr(cid_bare)
    out["setMachineOn"] = sset("machineDigEnabled", True)
    out["settings1"] = {f: sget(f).get("value") for f in ("maxDigDepth", "machineDigEnabled", "maxMachineDigDepth")}
def slim(v):
    if isinstance(v, dict):
        return {k: slim(x) for k, x in v.items() if k not in ("operation", "state", "typeIdentity", "ticksGame")}
    return v
print(json.dumps(slim(out), default=str))
