"""FW_PROOF_TOOLS_HARDEN_READ_GAPS: one check per GPT validation-suite finding the item names (4.5, 6.2, 6.4, 7.1, 7.11,
7.12, 8.3), each the finding's own failure scenario run against the fixed reader/verdict, plus the bridge source that now
sends the fields those readers judge (JawaBench flowworks_excavation_rect dl/fluid, flowworks_pulse dl). Offline, 0 ticks.

  python3 src/RimMandrake/FlowWorks/selftest_proof_read_gaps.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
NS = os.path.join(HERE, "northstar")
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in (HERE, NS, os.path.join(REPO, "src", "RimMandrake", "bridgetools")):
    if p not in sys.path:
        sys.path.insert(0, p)

FAILS = []


def check(cond, msg, det=None):
    print("%s  %s%s" % ("PASS" if cond else "FAIL", msg, "" if cond or det is None else "  %r" % (det,)))
    if not cond:
        FAILS.append(msg)


# ---------------------------------------------------------------- 4.5: scenarios_map snapshot / verify_plots / soak
def g45():
    import scenarios_map as M
    Rev = M.review_class()
    CHEM = "RM_Fluid_Chemfuel"

    class FakeB(object):
        def __init__(self, frames):
            self.frames, self.n = frames, 0

        def call(self, t, **kw):
            if t == "jawa/flowworks_excavation_rect":
                rows = self.frames[min(self.n, len(self.frames) - 1)]
                self.n += 1
                return {"success": True, "rows": rows}
            return {"success": True, "things": [], "pawns": []}

    def cell(x, f, dl, fluid):
        return dict(x=x, z=0, d=2, f=f, dl=dl, fluid=fluid, isExcavated=True)

    placed = [{"sc": {"id": "T", "size": (4, 1), "setup": {"dig": [(0, 0, 2, 1, 2)], "fluid": [(0, 0, 2, 1, 1, CHEM)]}},
               "origin": (0, 0), "rect": (0, 0, 4, 1)}]
    right = [cell(0, 1, 10000, CHEM), cell(1, 1, 10000, CHEM)]
    water = [cell(0, 1, 10000, "RM_Fluid_Water"), cell(1, 1, 10000, CHEM)]

    def review(frames):
        r = Rev.__new__(Rev)
        r.B = FakeB(frames)
        r.call = lambda *a, **k: {"success": True}
        return r

    ok = Rev.verify_plots(review([right]), placed)["T"]
    check(ok["ok"] is True and ok["fill_wrong"] == 0, "4.5 sanity: the right liquid at the right level verifies", ok)
    bad = Rev.verify_plots(review([water]), placed)["T"]
    check(bad["ok"] is False and bad["fill_wrong"] == 1, "4.5 water staged where chemfuel is due FAILS verify_plots", bad)
    blind = Rev.verify_plots(review([[dict(c, fluid=None) for c in right]]), placed)["T"]
    check(blind["ok"] is False, "4.5 a bridge row with no fluid never verifies a wet plot", blind)
    moved = [cell(0, 1, 11000, CHEM), cell(1, 1, 19000, CHEM)]
    still = Rev.soak(review([right, moved]), placed, ticks=1)["T"]
    check(still["still"] is False and still["dug_changed"] == 2,
          "4.5 exact water that moves within a notch (same whole-notch f) is not 'still' in the soak", still)
    swap = Rev.soak(review([right, water]), placed, ticks=1)["T"]
    check(swap["still"] is False, "4.5 a liquid that changes identity during the soak is not 'still'", swap)
    calm = Rev.soak(review([right, right]), placed, ticks=1)["T"]
    check(calm["still"] is True, "4.5 sanity: an unchanged plot is still", calm)


# ---------------------------------------------------------------- 7.12: review_map visual_verdict
def g712():
    import review_map as R
    P = {"w": 2, "h": 1, "depth": 2}
    water = [{"d": 2, "f": 1, "fluid": "RM_Fluid_Water"}] * 2
    tar = [{"d": 2, "f": 1, "fluid": "RM_Fluid_Tar"}] * 2
    check(R.visual_verdict(P, 1, False, water, 0.0, 1, want_fluid="RM_Fluid_Tar") is False,
          "7.12 water in the tar station is not built")
    check(R.visual_verdict(P, 1, False, tar, 0.0, 1, want_fluid="RM_Fluid_Tar") is True, "7.12 sanity: tar in the tar station is built")
    check(R.visual_verdict(P, 0, False, [{"d": 2, "f": 0, "fluid": None}] * 2, 0.0, 1, want_fluid=None) is True,
          "7.12 sanity: a dry station needs no fluid")
    src = open(os.path.join(HERE, "review_map.py"), encoding="utf-8").read()
    check('want_fluid=s.get("fluid")' in src, "7.12 verify_visuals passes the station's setup fluid to the verdict")


# ---------------------------------------------------------------- 6.2: validation_v2 Live.pulses compares exact dL
def g62():
    import validation_v2 as V2
    c1, c2 = (5, 5), (6, 5)

    class Oracle(object):
        level_exact = True
        D = {c1: 2, c2: 2}
        F = {c1: 0, c2: 0}
        W = {c1: 5000, c2: 5000}

        def exc(self, c):
            return True

        def idx(self, c):
            return c

        def pulse(self):
            pass

    def run(pulse1):
        class B(object):
            def call(self, t, **kw):
                return {"success": True, "cells": [{"x": 5, "z": 5}, {"x": 6, "z": 5}], "ticksBefore": 1, "ticksGame": 1,
                        "nextPulseTickUntouched": True, "gamePaused": True, "pulsesRun": 1,
                        "pulses": [{"fill": [0, 0], "dl": [5000, 5000]}, pulse1]}
        L = V2.Live.__new__(V2.Live)
        L.B, L.o, L.jobcells = B(), Oracle(), set()
        L._log = lambda s: None
        L.scene_of = lambda c: "S"
        return L.pulses(1, "t")

    probs, mism, _, _ = run({"fill": [0, 0], "dl": [1000, 9000]})
    check(mism.get("S") and len(mism["S"]) == 2, "6.2 1,000/9,000 dL against the oracle's 5,000/5,000 is a mismatch", mism)
    probs, mism, _, _ = run({"fill": [0, 0], "dl": [5000, 5000]})
    check(not mism and not probs, "6.2 sanity: the oracle's own distribution matches", (probs, mism))
    probs, mism, _, _ = run({"fill": [0, 0]})
    check(any("no per-cell dl" in p for p in probs), "6.2 a bridge that sends no dl is a contract problem, not a pass", probs)


# ---------------------------------------------------------------- 6.4: underpass_raid_live band + depth readback
def g64():
    import underpass_raid_live as U
    check(U.band_reading("BAND under=True onDeck=False passes=True view=floor deckNotches=2") == (True, False),
          "6.4 ProofBand parses under/onDeck")
    check(U.band_reading("REFUSED: arg must be a spawned pawn's id") is None, "6.4 a refused band read is blind, not under")
    check(U.verdict(True, [], [(60, 1, (12, 3))], []) == ("FAIL", "MOD"), "6.4 a raider ON the deck at the under squares FAILS")
    check(U.verdict(True, [], [], [(60, 1, (20, 3))]) == ("UNMEASURED", "HARNESS"),
          "6.4 reaching the far side with no band-confirmed under sample is not a PASS")
    check(U.verdict(True, [(60, 1, (12, 3))], [], []) == ("PASS", "MOD"), "6.4 sanity: a band-confirmed under sample passes")
    check(U.verdict(True, [], [], [], [(60, 1, (12, 3), "REFUSED")]) == ("UNMEASURED", "HARNESS"),
          "6.4 a blind band read under the deck is UNMEASURED, never a FAIL against the mod")
    moat = {(0, 3), (1, 3)}
    check(U.moat_depth_problems([{"x": 0, "z": 3, "d": 9}, {"x": 1, "z": 3, "d": 4}], moat) == [((1, 3), 4)],
          "6.4 a moat square short of 8 notches is caught by the depth readback")
    src = open(os.path.join(NS, "underpass_raid_live.py"), encoding="utf-8").read()
    check('method="ProofBand"' in src and "jawa/flowworks_excavation_rect" in src,
          "6.4 the live loop reads ProofBand and reads the moat depth back")


# ---------------------------------------------------------------- 7.1: hose results need the deployed DLL identity
def g71():
    import importlib.util
    spec = importlib.util.spec_from_file_location("fw_validation_rg", os.path.join(HERE, "validation.py"))
    vm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vm)
    tmp = tempfile.mkdtemp(prefix="rg_ns_")
    good = {"mode": "live", "certifiable": True, "mod_hash": "H1", "rows": []}
    json.dump(good, open(os.path.join(tmp, "proof_hose_20261105T000001.json"), "w"))
    check(vm.latest_hose_result("H1", dll_sha="ab", ns=tmp) is None,
          "7.1 a hose result at the repo hash with no deployed-DLL sha certifies nothing")
    json.dump(dict(good, env={"assembly_sha256": "CD"}), open(os.path.join(tmp, "proof_hose_20261105T000002.json"), "w"))
    check(vm.latest_hose_result("H1", dll_sha="ab", ns=tmp) is None, "7.1 a hose result run on another DLL certifies nothing")
    json.dump(dict(good, env={"assembly_sha256": "AB"}), open(os.path.join(tmp, "proof_hose_20261105T000003.json"), "w"))
    check(vm.latest_hose_result("H1", dll_sha="ab", ns=tmp) is not None, "7.1 sanity: the repo's DLL at the repo hash is read")
    vsrc = open(os.path.join(HERE, "validation.py"), encoding="utf-8").read()
    check("latest_hose_result(_st.mod_hash(HERE), dll_sha=repo_dll_sha256())" in vsrc, "7.1 hose_live_rows passes the repo DLL sha")
    psrc = open(os.path.join(NS, "proof_hose.py"), encoding="utf-8").read()
    check('assembly_sha256=ms[0].get("sha256")' not in psrc and 'tp.get("mvidMatchesFile") is True' in psrc,
          "7.1 proof_hose stamps the DLL sha only when type_probe says the process loaded that file")


# ---------------------------------------------------------------- 7.11: P9 reads brace structure, not a 6-line window
def g711():
    import selftest_hose_port as HP
    bad, _ = HP.p9_credit_sites()
    check(bad == [], "7.11 sanity: every production credit site is inside (or after an early exit of) a committed transfer", bad)
    rel, tag = HP.CREDIT_SITES[0]
    planted = "\n".join([
        "class X", "{", "\tvoid F()", "\t{", "\t\tif (made)", "\t\t{", "\t\t\tx();", "\t\t}",
        "\t\tRM_LiquidNet.Credit(parent, t, l, 1, 250);   // " + tag, "\t}", "}"])
    srcs = {r: "" for r, _ in HP.CREDIT_SITES}
    srcs[rel] = planted
    bad, _ = HP.p9_credit_sites(srcs)
    check(any("not inside a committed transfer" in b and tag in b for b in bad),
          "7.11 a credit just after the guarded block's closing brace is caught (GPT's planted case)", bad)
    guarded = planted.replace("\t\t\tx();\n\t\t}\n\t\tRM_LiquidNet.Credit(parent, t, l, 1, 250);   // " + tag,
                              "\t\t\tRM_LiquidNet.Credit(parent, t, l, 1, 250);   // " + tag + "\n\t\t}")
    srcs[rel] = guarded
    bad, _ = HP.p9_credit_sites(srcs)
    check(not any(tag in b and "not inside" in b for b in bad), "7.11 sanity: the same credit inside the block passes", bad)
    early = "\n".join(["\t\tif (RM_LiquidTransfer.Move(units, a, b, out var mv) != units)", "\t\t{", "\t\t\tx();", "\t\t}",
                       "\t\tRM_LiquidNet.Credit(parent, t, l, 1, 250);   // " + tag])
    srcs[rel] = "class X\n{\n\tvoid F()\n\t{\n" + early + "\n\t}\n}"
    bad, _ = HP.p9_credit_sites(srcs)
    check(any(tag in b and "not inside" in b for b in bad),
          "7.11 an early-exit-looking block that does NOT leave (no return) does not guard the credit", bad)


# ---------------------------------------------------------------- 8.3: CR5 needs the unforced start
def g83():
    import validation_hose as VH
    h = {"carry": "Laid", "far": list(VH.CTARGET), "pending": "None", "layOk": True}
    check(VH.cr5_ok(False, True, h) is False, "8.3 a resume only the forced order started FAILS CR5")
    check(VH.cr5_ok(True, True, h) is True, "8.3 sanity: the unforced WorkGiver resume passes CR5")
    src = open(os.path.join(HERE, "validation_hose.py"), encoding="utf-8").read()
    check('"PASS" if cr5_ok(unforced, resumed, h)' in src, "8.3 run_carry's CR5 row uses cr5_ok with the unforced start")


# ---------------------------------------------------------------- C#: the bridge sends the fields
def gcs():
    p = os.path.join(REPO, "src", "RimMandrake", "bridgetools", "JawaBench.BridgeTools", "JawaBenchFlowWorksPulseTools.cs")
    s = open(p, encoding="utf-8").read()
    check("x = c.x, z = c.z, d, f, dEff, fEff, dl, fluid," in s, "C# excavation_rect rows carry dl and fluid")
    check('type.GetMethod("WaterDlAt"' in s and 'type.GetMethod("FluidAt"' in s, "C# reads WaterDlAt / FluidAt by reflection")
    check("dl = s.dl," in s and "sumDl = s.sumDl," in s, "C# flowworks_pulse records carry per-cell dl and sumDl")
    import prove_excavation_rect_fields as PF
    check(PF.judge({"success": True, "rows": [{"x": 1, "z": 1, "d": 0, "f": 0}]})[0] == 1,
          "A1 live proof FAILS rows from an old bridge (no dl/fluid)")
    check(PF.judge({"success": True, "rows": [{"x": 1, "z": 1, "dl": 0, "fluid": None}]})[0] == 0, "A1 live proof passes new rows")
    check(PF.judge({"success": False})[0] == 2, "A1 live proof is NO VERDICT on a failed call")
    # The live round's rows (2026-11-06): the transport drops null members, so a dry cell has neither fluid nor terrain.
    live = {"success": True, "rows": [{"x": 125, "z": 125, "d": 0, "f": 0, "dEff": 0, "fEff": 0, "dl": 0,
                                       "isExcavated": False, "isSource": False, "isSink": False}]}
    ctl = {"success": True, "rows": [{"x": 125, "z": 125, "d": 0, "f": 0, "dl": 0, "terrain": "Sand"}]}
    check(PF.judge(live, ctl)[0] == 0, "A1 passes a null-dropped fluid when terrain is dropped too and the control carries it")
    check(PF.judge(live)[0] == 2, "A1 is NO VERDICT on a null-dropped fluid with no control")
    no_dl = {"success": True, "rows": [{k: v for k, v in live["rows"][0].items() if k != "dl"}]}
    check(PF.judge(no_dl, ctl)[0] == 1, "mutant: a row without dl FAILS even with a good control")
    kept_nulls = {"success": True, "rows": [dict(live["rows"][0], terrain=None)]}
    check(PF.judge(kept_nulls, ctl)[0] == 1, "mutant: fluid absent while nulls survive transport (terrain: null) FAILS")
    ctl_no_terrain = {"success": True, "rows": [{"x": 125, "z": 125, "dl": 0}]}
    check(PF.judge(live, ctl_no_terrain)[0] == 1, "mutant: literal lost its nullable members (control has no terrain) FAILS")
    ctl_no_dl = {"success": True, "rows": [{"x": 125, "z": 125, "terrain": "Sand"}]}
    check(PF.judge(live, ctl_no_dl)[0] == 1, "mutant: control row without dl FAILS")
    check(PF.judge({"success": True, "rows": [{"x": 1, "z": 1, "dl": 3, "fluid": 7}]})[0] == 1, "mutant: non-string fluid FAILS")
    check(PF.judge({"success": True, "rows": [{"x": 1, "z": 1, "dl": -1, "fluid": None}]})[0] == 1, "mutant: negative dl FAILS")
    check(PF.judge({"success": True, "rows": [{"x": 1, "z": 1, "dl": 40, "fluid": "RM_Water"}]})[0] == 0, "A1 passes a wet row")


def main():
    for g in (g45, g712, g62, g64, g71, g711, g83, gcs):
        try:
            g()
        except Exception as ex:  # noqa: BLE001 - a crashed group is a FAIL with its name
            import traceback
            traceback.print_exc()
            check(False, "%s crashed: %r" % (g.__name__, ex))
    print("RESULT: %s (%d failed)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
