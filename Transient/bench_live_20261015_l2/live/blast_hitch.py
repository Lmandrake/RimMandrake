"""L2 one-off: FUEL_MOAT_VERIFY_LIGHT_THE_GASOLINE "look for: hitching" -- time the detonation of a 30x30 D2 astrofuel
body. Run from the export root with python.exe on the clean calm save. Reads: jawa/map_comp_timing over 600 real ticks
from the light (game unpaused at speed 1), the detonation count, and jawa/tps_report windows around it."""
import json, sys, time
sys.path.insert(0, "src/RimMandrake/FlowWorks/northstar")
sys.path.insert(0, "src/RimMandrake/Utils/modcheck")
sys.path.insert(0, "src/RimMandrake/Utils")
import proof_hose as PH
import test_site_saves as TSS

out = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 30
X0, Z0 = 40, 170
B = PH.PB()
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
res = {"size": N, "origin": [X0, Z0]}


def sc(typ, method, arg):
    r = B.call("jawa/static_call", type=typ, method=method, args=arg) or {}
    return str(r.get("result") or r.get("message") or r.get("error") or "")


def save():
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1, default=str)


res["load"] = TSS.load_site(B.call, "calm", check=False)
b = 4
res["reset"] = sc("RimMandrake.FlowWorks.RM_NorthstarProofs", "ProofResetRect", "%d;%d;%d;%d" % (X0 - b, Z0 - b, N + 2 * b, N + 2 * b))
B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % (X0 - b, Z0 - b, N + 2 * b, N + 2 * b), categories="All")
B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % (X0 - b, Z0 - b, N + 2 * b, N + 2 * b))
before = {}
for f in ("canalFireEnabled", "explosionIgnitesLiquidEnabled", "astrofuelDetonationEnabled"):
    before[f] = B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f).get("value")
    B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value="True")
res["settings_before"] = before
t0 = time.time()
bad = 0
for i in range(N):
    for j in range(N):
        x, z = X0 + i, Z0 + j
        r = B.call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=2, setFill=-1) or {}
        f = sc("RimMandrake.FlowWorks.RM_FluidIdentityProof", "ProofFillWithFluid", "%d,%d,2,RM_Fluid_Astrofuel" % (x, z))
        if not r.get("success") or not f.startswith("FILLED"):
            bad += 1
res["build_s"] = round(time.time() - t0, 1)
res["cells_failed"] = bad
res["report_before"] = sc("RimMandrake.FlowWorks.RM_LiquidFireProof", "ProofReport", " ")
save()
B.call("rimworld/pause_game", pause=False)
res["light"] = sc("RimMandrake.FlowWorks.RM_LiquidFireProof", "ProofIgnite", "%d,%d" % (X0, Z0))
res["timing"] = B.call("jawa/map_comp_timing", ticks=600, maxSeconds=120, top=8)
B.call("rimworld/pause_game", pause=True)
res["report_after"] = sc("RimMandrake.FlowWorks.RM_LiquidFireProof", "ProofReport", " ")
tps = B.call("jawa/tps_report", last=8) or {}
res["tps"] = {k: tps.get(k) for k in ("ratioMin", "ratioMedian", "ratioMax", "sustained", "samplesJsonl")}
for f, v in before.items():
    if v is not None:
        B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))
save()
tm = res["timing"] or {}
print("cells_failed", bad, "build_s", res["build_s"])
print("before:", res["report_before"])
print("light:", res["light"][:160])
print("after:", res["report_after"])
print("timing: ticks %s real %ss sumMsPerTick %s" % (tm.get("ticksElapsed"), tm.get("realSeconds"), tm.get("sumMsPerTick")))
for c in (tm.get("components") or [])[:5]:
    print("  %-50s msPerTick %s maxMs %s" % (c.get("type"), c.get("msPerTick"), c.get("maxMs")))
print("tps:", json.dumps({k: res["tps"][k] for k in ("ratioMin", "ratioMedian", "ratioMax", "sustained")}))
