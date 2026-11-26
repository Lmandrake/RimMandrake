#!/usr/bin/env python3
"""rows_spec.json for make_rows.py (visit 9)."""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
T, F = "identity_pyrelands.json", "identity_full.json"
S = []
def row(test, label, ident=T, **k):
    S.append(dict(test=test, label=label, identity=ident, **k))
row("sc_ashwallow", "burrowers")
row("sc_heat_dome", "heat_dome", note="naive GPT judge of the two unlabelled crops (text cropped out) named the domed one: evidence/dome_naive_judge_gpt.md")
row("sc_fire_dusts_ash", "fire_tick_effects")
row("sc_scorchfruit", "scorchfruit")
row("sc_no_rain", "no_ordinary_rain")
row("P_mapgen_log", "mapgen_log")
row("P_grass_cover", "grass")
row("P_ambient_ash_drift", "ambient_ash_drift")
row("P_blackrain", "blackrain")
row("P_gate", "gate_live_proof", script="script_gate_live_proof.log", pass_line="A1 ShellPresent=True On=True")
row("sc_ullai", "ullai_and_giant")
row("sc_reload_keeps_the_burn", "reload_keeps_the_burn")

row("sc_fire_walks_with_wind", "wind_burn_live", script="script_wind_burn_live.log")
S2, NEW = "identity_small.json", "4980c8dcdd"
FIX = "4980c8dcdd1da6d0724ab2732145261fc90a8867"
EV = "design/concepts/Pyrelands/version/in_game/visit_9/evidence/"
RUN = "python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains "
row("sc_ash_watered", "ash_watered", mod_sha="3a3294ac36", note="the short scene (five reads over 50,000 ticks, hot and cool hours both read)")
row("sc_burn_compounds", "fresh_burn", mod_sha="3a3294ac36")
row("sc_grass_regreens", "regrow", mod_sha="3a3294ac36", outcome="APPARATUS FAULT", **{"class": "HARNESS"},
    detail="regrow_dry_watered_vanilla FAIL 'bursts off the watered cells': the dry patch held 16, 13, 14, 15, 15, 15 plants, and its check matched plants by rank, so a newcomer at 0.68 beside fourteen mature read as a burst (a restart stands at 0.05, and gains 0.51 a day). The other four parts PASS. Visit 8's unfenced row held 16 at every read, and inside a ring 16 of 16 stood at all six daily reads (run growth_real), so what took them came from outside the patches; what it was is not shown: in 4,000 unstaged ticks on ArchSmall none went and no animal came near; a hungry nuna set beside the patches ate one of 48, none inside a ring (graze_read.py, graze_stage.py)")
row("sc_grass_regreens", "growth_real", mod_sha="82bdcf15cf", outcome="APPARATUS FAULT", command="PYRE_REGROW_PART=growth " + RUN + "embergrass_regrow", components=["regrow_dry_watered_vanilla"], parts=[["growth_real", ["regrow_dry_watered_vanilla"]]],
    detail="this run's own shortening held freshBurnDays at one day and left ExplosiveGrowth's fresh ash on, so both patches matured within a day")
row("sc_grass_regreens", "growth_small", S2, mod_sha=NEW, **{"class": "HARNESS"}, command=RUN + "regrow_growth   (and the four other parts from " + RUN + "grass_cover,embergrass_regrow, run regrow at 09:47 on ArchBig)",
    parts=[["regrow", ["grass_chokes_ground", "embergrass_regrows", "grass_census_first", "plant_density_one_control_map"]], ["growth_small", ["regrow_dry_watered_vanilla"]]],
    note="the sown patches as one staged growth step (16,000 ticks, 74 s): dry gain 0.0796 (its vanilla rate 0.0666), watered 0.0840, bursts 16 of 16 on the soaked patch and 0 on the dry ones, 16 plants in each patch at every read. Four parts stand from run regrow; their code did not change",
    repair={"class": "HARNESS", "commit": FIX, "what": "each plant is followed by id over one growth step, a moved plant is UNMEASURED, and a soaked mature patch shows a burst",
            "planted": {"plant": "PYRE_PLANT_REGROW_SOAK_DRY=1: bursts on the dry mature patch (and PYRE_PLANT_REGROW_WET_ROOTS_OFF=1: water does nothing; both FAIL)",
                        "command": "PYRE_PLANT_REGROW_SOAK_DRY=1 (through WSLENV) " + RUN + "regrow_growth", "verdict": "FAIL", "evidence": EV + "pv9_growth_small_soak_dry.json"}})
row("sc_burn_line_walks", "burn_line", mod_sha="82bdcf15cf", outcome="APPARATUS FAULT", **{"class": "SITE"},
    detail="burn_line_present and burn_line_burned_share PASS; hourly UNMEASURED: the game window was 1458x831 and a 23-cell crop did not fit one screen (HARNESS, play_zoom); off_control FAIL, 34 fires: the site's two furnace-beasts lit the grass they slept in (SITE: off_control_source.py, first fire one cell from a beast; none in 131,000 ticks with furnaceThermalEnabled off too)")
row("sc_burn_line_walks", "walk_small", S2, mod_sha=NEW, **{"class": "SITE"}, command=RUN + "burn_line_walk,burn_line_off_control   (and burn_line_burned_share from " + RUN + "burn_line, run burn_line at 09:47 on ArchBig)",
    parts=[["walk_small", ["burn_line_present", "burn_line_walks_hourly"]], ["off_small", ["burn_line_off_control"]], ["burn_line", ["burn_line_burned_share"]]],
    note="relight and switch control staged by the quiet counter (10,360 ticks each), eight hourly captures; the naive GPT judge of the captures and the four day-end maps: YES (evidence/burn_line_naive_judge_gpt.md). The share (0.31 at worst with the wind on, 0.84 off, limit 0.50) stands from run burn_line",
    repair={"class": "SITE", "commit": FIX, "what": "furnaceThermalEnabled held off in the switch control, which is one step long; play_zoom stitches columns",
            "planted": {"plant": "PYRE_PLANT_BURNLINE_TOGGLE_IGNORED=1: the switch left on, 39 fires (and PYRE_PLANT_FRONT_OUT=1: the watch FAILs)",
                        "command": "PYRE_PLANT_BURNLINE_TOGGLE_IGNORED=1 (through WSLENV) " + RUN + "burn_line_off_control", "verdict": "FAIL", "evidence": EV + "pv9_off_small_planted.json"}})
row("sc_firehawk_rewards", "letter", S2, mod_sha=NEW)
row("firehawk_first_sighting_letter", "letter", S2, mod_sha=NEW)
row("firehawk_crestfeather_yield", "crest", S2, mod_sha=NEW)
row("P_mapgen_log", "mapgen2", S2, mod_sha=NEW)
row("sc_reload_keeps_the_burn", "reload2", S2, mod_sha=NEW, note="again: front_walks' wording changed in the file it imports")
json.dump(S, open(os.path.join(H, "rows_spec.json"), "w"), indent=1)
