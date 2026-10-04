#!/usr/bin/env python3
"""Offline proof that every GelatinousSlime check can FAIL (and passes on the clean mock).
Runs the suite under the northstar_driver mock once clean and once per injected fault
(NS_SLIME_MOCK_BREAK, see northstar_mock.py); each fault must turn its named component non-PASS.
    python3 src/RimMandrake/GelatinousSlime/selftest_slime_suite.py"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CLI = os.path.join(ROOT, "src", "RimMandrake", "Utils", "northstar_driver", "cli.py")
PLAN = os.path.join(HERE, "northstar_plan.py")

# fault -> components that must NOT pass
CASES = {
    "nodef:ThingDef/RM_RawSlime": ["all_defs_resolve"],
    "notag": ["terrain_tagged"],
    "noflight": ["dwommo_flight_def"],
    "nosalve": ["glurro_salve_slows_growth"],
    "nodef:ThingDef/RM_GlurroSalve": ["glurro_salve_defs"],
    "nodef:RecipeDef/RM_Render_TwistedMeat": ["pit_solvent_defs"],
    "nodef:ThingDef/RM_TitanoslimeChunk": ["seal_breach_defs"],
    "nodef:ThingDef/RM_Proj_TitanoslimeChunk": ["chunk_bomb_defs"],
    "nodef:ThingDef/RM_ArchiveVat": ["archive_resurrection_defs"],
    "nodry": ["drying_biomes_tagged"],
    "nostep": ["visitor_genstep_registered"],
    "nofarmstep": ["farm_ruins_genstep_registered"],
    "defaultswrong": ["settings_defaults"],
    "noexpose": ["exposure_applies_on_slime"],
    "growfast": ["growth_rate_on_slime"],
    "nolaw2": ["stage3_ends_panic_law2"],
    "noalert": ["standing_alert_lists_pawn"],
    "nodissolve": ["returned_to_the_flow"],
    "nosmear": ["returned_to_the_flow"],
    "antidote_noop": ["antidote_clears_film_and_poisons"],
    "antidote_nocost": ["antidote_clears_film_and_poisons"],
    "eat_nocure": ["raw_slime_cures_poison_and_charges_fee"],
    "eat_nofee": ["raw_slime_cures_poison_and_charges_fee"],
    "nosmearsetting": ["read_marks_follow_setting"],
    "nomarkedcost": ["marked_colonist_is_liked_less"],
    "noseeker": ["blank_seeker_reports_unprimed"],
    "noweather": ["slime_rain_can_fall"],
    "noclamp": ["stage_roll_spreads"],
    "noshed": ["sheds_when_cut"],
    "shedignore": ["does_not_shed_when_setting_off"],
    "noload": ["seeker_loads_without_the_dialog"],
    "noswap": ["extract_job_swaps_to_a_loaded_seeker"],
    "slowclock": ["injection_marks_starts_fast_clock_and_antidote_wins_the_race"],
    "noreek": ["injection_marks_starts_fast_clock_and_antidote_wins_the_race"],
    "nocharm": ["injection_marks_starts_fast_clock_and_antidote_wins_the_race"],
    "offignored": ["slimification_off_reverses_the_injected_clock"],
}


def run(env_extra):
    out = os.path.join(tempfile.mkdtemp(prefix="gs_"), "r.json")
    env = dict(os.environ, **env_extra)
    subprocess.run([sys.executable, CLI, "run", "--mock", "--mod", "GelatinousSlime", "--plan", PLAN,
                    "--mock-skip-site", "--out", out], env=env, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, check=False)
    with open(out) as f:
        return {c["name"]: c["verdict"] for c in json.load(f)["components"]}


def main():
    bad = []
    clean = run({"NS_SLIME_MOCK_BREAK": ""})
    n = len(clean)
    nonpass = {k: v for k, v in clean.items() if not v.startswith("PASS")}
    if n < 31 or set(nonpass) != {"drying_biome_decays"}:
        bad.append("clean run: %d components, non-pass %s (expected only drying_biome_decays UNMEASURED)" % (n, nonpass))
    dry = run({"NS_SLIME_MOCK_BIOME": "Desert"})
    if not dry.get("drying_biome_decays", "").startswith("PASS") or any(
            v == "FAIL" for v in dry.values()):
        bad.append("Desert run: %s" % {k: v for k, v in dry.items() if not v.startswith("PASS")})
    bp = os.path.join(tempfile.mkdtemp(prefix="gs_"), "bad.xml")
    with open(bp, "w") as f:
        f.write('<Patch><Operation Class="PatchOperationRemove" MayRequire="x"><xpath>/Defs/BiomeDef[defName="RM_GelatinousSlime"]/baseWeatherCommonalities/Rain</xpath></Operation></Patch>')
    got = run({"NS_SLIME_MOCK_BREAK": "", "NS_SLIME_RAIN_PATCH": bp})
    if got.get("campaign_rain_strip_patch", "MISSING").startswith("PASS"):
        bad.append("broken rain-strip patch did not turn campaign_rain_strip_patch red")
    leak = os.path.join(tempfile.mkdtemp(prefix="gs_"), "Defs")
    os.makedirs(leak)
    with open(os.path.join(leak, "x.xml"), "w") as f:
        f.write("<Defs><GeneDef><label>wookiee hide</label></GeneDef></Defs>")
    got = run({"NS_SLIME_MOCK_BREAK": "", "NS_SLIME_LEAK_DIR": os.path.dirname(leak)})
    if got.get("free_tier_text_leak", "MISSING").startswith("PASS"):
        bad.append("canon term in a scanned dir did not turn free_tier_text_leak red")
    for fault, comps in CASES.items():
        got = run({"NS_SLIME_MOCK_BREAK": fault})
        for c in comps:
            if got.get(c, "MISSING").startswith("PASS"):
                bad.append("fault %s did not turn %s red (%s)" % (fault, c, got.get(c, "MISSING")))
    print("selftest_slime_suite: %d components clean, %d faults, %d problem(s)" % (n, len(CASES), len(bad)))
    for b in bad:
        print("  FAIL " + b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
