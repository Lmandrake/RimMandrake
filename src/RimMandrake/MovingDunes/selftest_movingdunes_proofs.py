#!/usr/bin/env python3
"""selftest_movingdunes_proofs.py -- offline proof for MovingDunes' slow_* chains (MOVINGDUNES_COVERAGE_GAPS_1).

Run bare: python3 src/RimMandrake/MovingDunes/selftest_movingdunes_proofs.py   (exit 0 = clean)

A mock jawa/static_call answers MovingDunesProof the way the shipped C# does (numbers derived from the material XML).
Clean must PASS (the dune-field-only bars UNMEASURED, never PASS, off a dune map; the day-scale stubs always UNMEASURED);
each planted break must redden its component. Statically, planted source breaks (a gate removed, a proof-read function no
longer called) must redden gate_findings, and the shipped source must be clean.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

import runner                                                  # noqa: E402
import validation as V                                         # noqa: E402
from northstar_driver.session import FastSession               # noqa: E402
from northstar_driver.transport import MockGame, MockTransport  # noqa: E402

FAILS = []
V_PROOF = "RimMandrake.MovingDunes.MovingDunesProof"
MAT = V.material_params()


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def math_text(brk):
    base = MAT["influxPerDay"] / 240.0
    att = lambda f: V.expected_attempts(MAT, f)           # noqa: E731
    d = dict(att1=att(1.0), att2=att(2.0), att05=att(0.5),
             infl_base1=base, infl_base2=2 * base, infl_loss1=10.0 * MAT["influxLossRatio"], infl_loss2=10.0 * MAT["influxLossRatio"],
             choke1=att(1.0) * MAT["plantChokeSampleFraction"], choke2=att(2.0) * MAT["plantChokeSampleFraction"],
             dmg_a=17, dmg_b=1, lock_tt="True", lock_ft="False", lock_tf="False", lock_tn="False",
             yield_on=3, yield_x2=6, yield_off=0, bear_n=0, bear_e=90, wind_away_n=4, wind_toward_n=0, wind_away_e=6)
    if "slider_ignored" in brk:
        d["att2"] = d["att1"]
    if "slider_squared" in brk:
        d["infl_loss2"] = 20.0
    if "choke_flat" in brk:
        d["dmg_a"] = 1
    if "lock_ignores_setting" in brk:
        d["lock_ft"] = "True"
    if "wind_flipped" in brk:
        d["wind_away_n"] = 0
    if "yield_off_pays" in brk:
        d["yield_off"] = 3
    if "yield_mult_ignored" in brk:
        d["yield_x2"] = 3
    return " ".join("%s=%s" % kv for kv in d.items())


def bury_text(brk, field):
    s = "cell=3,4 cand=%s cand_forbidden=%s api_cache=True api_count=1 api_spawned=False" % (
        "False" if "no_candidate" in brk else "True", "True" if "forbidden_buried" in brk else "False")
    if "api_dead" in brk:
        s = s.replace("api_cache=True", "api_cache=False")
    if not field:
        return s + " field=False arm_off_cache=- arm_off_spawned=- arm_on_cache=- arm_on_spawned=-"
    off = "True" if "toggle_ignored" in brk else "False"
    return s + " field=True arm_off_cache=%s arm_off_spawned=%s arm_on_cache=True arm_on_spawned=False" % (off, "False" if off == "True" else "True")


def move_text(brk, field, calm):
    if not field:
        return "field=False"
    return "field=True wind=%s thr=0.6 changed=%d before=100 after=101 batches=300" % ("0.3" if calm else "1.1", 0 if "no_motion" in brk else 40)


def make_ext(brk, field=True, calm=False, stale=False):
    def ext(game, tool, p):
        if tool != "jawa/static_call" or p.get("type") != V_PROOF:
            return None
        if stale:
            return {"success": False, "message": "no public static method %s" % p.get("method")}
        m = p.get("method")
        txt = {"ProofMath": lambda: math_text(brk), "ProofBury": lambda: bury_text(brk, field),
               "ProofMove": lambda: move_text(brk, field, calm)}[m]()
        return {"success": True, "result": txt}
    return ext


CHAINS = ("slow_crests_hop_downwind_and_bank_in_shelter", "slow_upwind_influx_and_downwind_loss", "slow_loose_gear_buried_and_returns",
          "slow_deep_drift_kills_plants", "slow_wind_locked_to_the_sun_on_stillsand", "slow_shovelled_drift_yields_sand")


def run(brk=(), **kw):
    game = MockGame()
    game.ext = make_ext(set(brk), **kw)
    s = FastSession(transport=MockTransport(game), strict=False)
    with s:
        res = runner.run_suite(V.suite, s, anchor=None, mod=None)
    out = {}
    for ch in res["chains"]:
        if ch["name"] in CHAINS:
            for c in ch["components"]:
                out[c["name"]] = c["verdict"]
    return out


def main():
    check("validation static is clean on the shipped source", V.static_checks() == [], V.static_checks())
    check("sanity: material params parsed (7.7 attempts/cell/day)", abs(MAT["attemptsPerCellPerDay"] - 7.7) < 1e-6, MAT)
    check("oracle: 62500 cells, factor 1 -> 2005 attempts", V.expected_attempts(MAT, 1.0) == 2005, V.expected_attempts(MAT, 1.0))

    clean = run()
    stubs = [k for k in clean if k.endswith("state_read")]
    check("clean: every non-stub bar PASSes", all(v == "PASS" for k, v in clean.items() if k not in stubs), clean)
    check("clean: the 6 day-scale/instrument stubs are UNMEASURED, never PASS", len(stubs) == 6 and all(clean[k] == "UNMEASURED" for k in stubs), (stubs, clean))
    off = run(field=False)
    check("off a dune map: sand_actually_moves + burial off-arm UNMEASURED", off["sand_actually_moves_on_a_dune_field"] == "UNMEASURED"
          and off["burialEnabled_off_arm_buries_nothing"] == "UNMEASURED", off)
    check("calm wind: sand_actually_moves UNMEASURED (calm moves nothing by design)", run(calm=True)["sand_actually_moves_on_a_dune_field"] == "UNMEASURED")
    got = run(stale=True)
    check("stale DLL (no ProofX): proof bars UNMEASURED, never PASS", got["transport_attempts_scale_with_the_drift_slider"] == "UNMEASURED", got)

    for brk, comp in (("slider_ignored", "transport_attempts_scale_with_the_drift_slider"), ("no_motion", "sand_actually_moves_on_a_dune_field"),
                      ("slider_squared", "loss_term_is_not_squared_by_the_slider"), ("api_dead", "burial_api_caches_the_thing_and_removes_it_from_the_map"),
                      ("no_candidate", "only_wild_unforbidden_loot_is_a_burial_candidate"), ("forbidden_buried", "only_wild_unforbidden_loot_is_a_burial_candidate"),
                      ("toggle_ignored", "burialEnabled_off_arm_buries_nothing"), ("choke_flat", "choke_damage_kills_a_buried_plant_in_plantChokeDays"),
                      ("lock_ignores_setting", "lock_applies_only_with_setting_and_a_locking_biome"), ("wind_flipped", "locked_wind_follows_the_sun_bearing"),
                      ("yield_off_pays", "clearYieldEnabled_off_arm_yields_nothing"), ("yield_mult_ignored", "yield_scales_with_depth_removed_and_multiplier")):
        got = run((brk,))
        check("break %-20s reddens %s" % (brk, comp), got.get(comp) == "FAIL", got.get(comp))

    # static: planted source breaks
    srcs = V.load_sources()
    check("gate_findings clean on shipped source", V.gate_findings(srcs) == [], V.gate_findings(srcs))
    for fn, old, new, tag in (
            ("MapComponent_DuneField.cs", "if (!MovingDunesSettings.plantChokeEnabled)", "if (false)", "plantChokeEnabled"),
            ("MapComponent_DuneField.cs", "if (!MovingDunesSettings.burialEnabled)", "if (false)", "burialEnabled"),
            ("MapComponent_DuneField.cs", "if (!MovingDunesSettings.duneEngineEnabled)", "if (false)", "duneEngineEnabled"),
            ("Patch_ClearSandYield.cs", "MovingDunesSettings.clearYieldEnabled", "true", "clearYieldEnabled"),
            ("MapComponent_DuneField.cs", "WindLockApplies(MovingDunesSettings.windLockEnabled, ext)", "WindLockApplies(true, ext)", "windLockEnabled"),
            ("MapComponent_DuneField.cs", "influxDebt += InfluxDebtDelta(", "influxDebt += 0f * InfluxDebtDeltaX(", "InfluxDebtDelta")):
        mut = dict(srcs)
        check("source break (%s) is findable in the shipped text" % tag, old in mut[fn], old)
        mut[fn] = mut[fn].replace(old, new)   # every occurrence: a gate is gone only when ALL reads are
        got = V.gate_findings(mut)
        check("source break %-22s reddens gate_findings" % tag, any("[%s]" % tag in f for f in got), got)
    proj = open(os.path.join(HERE, "Source", "RimMandrake_MovingDunes.csproj"), encoding="utf-8").read()
    check("MovingDunesProof.cs is in the csproj compile list", 'Compile Include="MovingDunesProof.cs"' in proj)
    proof = srcs["MovingDunesProof.cs"]
    check("proof restores burialEnabled in a finally", "burialEnabled = wasBurial;" in proof)
    check("proof reads the shipped functions", all(x in proof for x in ("TransportAttempts(", "InfluxDebtDelta(", "ChokeSamples(", "WindLockApplies(", "YieldAmount(", "BuryThingsAt(")))

    if FAILS:
        print("\n%d MovingDunes proof selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall MovingDunes proof selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
