"""RIMMANDRAKE_DELETE_FILL_N_ONE_WATER_NUMBER_SEVEN_FIXES item 6, the live half: the slime slip chance follows the cell's exact
water (dL), not a rounded notch count. One 2 m dug square, slime poured to 0.50 m, 0.75 m and 1.00 m; at each depth
RM_PromotionProofs.ProofSlimeSlip reads the chance RM_SlimeSlip would roll for a pawn wading there (not climbing out).
PASS = 0.75 m lies strictly between 0.50 m and 1.00 m (a notch count rounds 0.75 m to 0.50 m or 1.00 m), and each read's
waterDl is the metres poured. Offline twin: SelfTest/SlimeChecks.cs Slime_fuller_and_climbing_out_slip_more.

    python3 src/RimMandrake/FlowWorks/northstar/live_probes/fw_slime_slip_exact.py
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "Utils"))
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=180.0); S.connect()
def call(tool, **kw):
    r = S.call(tool, kw) or {}
    return json.loads(r["content"][0]["text"]) if isinstance(r, dict) and r.get("content") else r
PROOF = "RimMandrake.FlowWorks.RM_PromotionProofs"
FLUIDID = "RimMandrake.FlowWorks.RM_FluidIdentityProof"
SLIME = "RM_Fluid_SlimeGreen"
U = 10000   # dL per 0.5 m notch (RM_Volume.UnitsPerLevel)
X, Z = 30, 180
site = (X - 3, Z - 3, 7, 7)
def need(what, r):
    """A scene write that did not land would read a dry cell's 0 chance: refuse instead of measuring nothing."""
    if not (isinstance(r, dict) and r.get("success")):
        raise SystemExit("UNMEASURED: %s did not land: %s" % (what, str(r)[:200]))
    return r
def text(r): return str(r.get("result") or r.get("message") or r.get("error") or "")
call("jawa/clear_area", rect="%d,%d,%d,%d" % site, dryRun=False)
call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % site)
need("dig 2 m", call("jawa/flowworks_excavation_drive", x=X, z=Z, deepenLevels=4, setBodyWaterM=-1))
reads = {}
for m in (0.5, 0.75, 1.0):
    f = text(need("pour %.2f m" % m, call("jawa/static_call", type=FLUIDID, method="ProofFillWithFluid", args="%d,%d,%g,%s" % (X, Z, m, SLIME))))
    if not f.startswith("FILLED"):
        raise SystemExit("UNMEASURED: pour %.2f m: %s" % (m, f[:200]))
    r = text(need("read %.2f m" % m, call("jawa/static_call", type=PROOF, method="ProofSlimeSlip", args="%d,%d" % (X, Z))))
    kv = dict(tok.split("=", 1) for tok in r.split()[1:] if "=" in tok)
    if not r.startswith("SLIP") or "chance" not in kv or "waterDl" not in kv:
        raise SystemExit("UNMEASURED: ProofSlimeSlip %.2f m: %s" % (m, r[:200]))
    reads[m] = (int(kv["waterDl"]), float(kv["chance"]), kv.get("fluid"))
    print("%.2f m: %s" % (m, r))
dl_ok = all(reads[m][0] == int(round(m * 2 * U)) and reads[m][2] == SLIME for m in reads)
c50, c75, c100 = reads[0.5][1], reads[0.75][1], reads[1.0][1]
ok = dl_ok and 0 < c50 < c75 < c100
print("RESULT", json.dumps({"waterDl_and_fluid_as_poured": dl_ok, "chance": [c50, c75, c100], "pass": ok}))
sys.exit(0 if ok else 1)
