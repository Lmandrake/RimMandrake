"""RIMMANDRAKE_DELETE_FILL_N_ONE_WATER_NUMBER_SEVEN_FIXES item 1, the live half: the game's kernel and excavation component
keep ONE water number per square (int dL, waterGrid), no whole-notch fill byte plus part. One 4-square 2 m channel; 0.73 m
of water (14,600 dL, not a whole notch) poured into its west square; 50 kernel pulses (jawa/flowworks_pulse, no game ticks).
PASS = the pour reads back to the decilitre, the channel still holds exactly 14,600 dL after the pulses (nothing lost to a
notch split), and it stands as one surface (every square within 3 dL of the others: equal depths, one level).
Offline twins: SelfTest ExcavationSanity_corrupt_grid_is_clamped_and_palette_compacts (the dL load repair) and the
StepPulse/ExcavationTick cases (the kernel on int[] water); guard selftest_flowworks_one_water_number.py.

    python.exe src/RimMandrake/FlowWorks/northstar/live_probes/fw_one_water_grid_exact.py
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
WATER = "RM_Fluid_Water"
U = 10000   # dL per 0.5 m notch (RM_Volume.UnitsPerLevel)
X, Z, N = 40, 180, 4
POUR_M = 0.73
WANT_DL = int(round(POUR_M * 2 * U))
site = (X - 3, Z - 3, N + 6, 7)
def need(what, r):
    """A scene write that did not land would read a dry channel: refuse instead of measuring nothing."""
    if not (isinstance(r, dict) and r.get("success")):
        raise SystemExit("UNMEASURED: %s did not land: %s" % (what, str(r)[:200]))
    return r
def text(r): return str(r.get("result") or r.get("message") or r.get("error") or "")
def row():
    r = text(need("read row", call("jawa/static_call", type=PROOF, method="ProofFluidRow", args="%d,%d,%d,1" % (X, Z, N))))
    if not r.startswith("ROW"):
        raise SystemExit("UNMEASURED: ProofFluidRow: %s" % r[:200])
    cells = {}
    for tok in r.split(" ", 3)[-1].split(";"):
        if ":" not in tok:
            continue
        xz, rest = tok.split(":", 1)
        d, dl, fl = rest.split("/")[:3]
        cells[tuple(int(v) for v in xz.split(","))] = (int(d), int(dl), fl)
    if len(cells) != N:
        raise SystemExit("UNMEASURED: ProofFluidRow read %d of %d squares: %s" % (len(cells), N, r[:200]))
    return cells
call("jawa/clear_area", rect="%d,%d,%d,%d" % site, dryRun=False)
call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % site)
for i in range(N):
    need("dig 2 m at %d" % (X + i), call("jawa/flowworks_excavation_drive", x=X + i, z=Z, deepenLevels=4, setBodyWaterM=-1))
f = text(need("pour", call("jawa/static_call", type=FLUIDID, method="ProofFillWithFluid", args="%d,%d,%g,%s" % (X, Z, POUR_M, WATER))))
if not f.startswith("FILLED"):
    raise SystemExit("UNMEASURED: pour %.2f m: %s" % (POUR_M, f[:200]))
before = row()
need("pulse", call("jawa/flowworks_pulse", count=50, x=X, z=Z, w=N, h=1, includeBodies=False))
after = row()
dug = all(v[0] == 4 for v in after.values())
poured = before[(X, Z)][1] == WANT_DL and sum(v[1] for v in before.values()) == WANT_DL
total = sum(v[1] for v in after.values())
dls = [after[(X + i, Z)][1] for i in range(N)]
level = max(dls) - min(dls) <= 3
ok = dug and poured and total == WANT_DL and level and all(v[2] == WATER for v in after.values())
print("before", before)
print("after ", after)
print("RESULT", json.dumps({"dug_2m": dug, "pour_reads_back_to_the_dL": poured, "total_dl": total, "want_dl": WANT_DL,
                            "squares_dl": dls, "one_surface": level, "pass": ok}))
sys.exit(0 if ok else 1)
