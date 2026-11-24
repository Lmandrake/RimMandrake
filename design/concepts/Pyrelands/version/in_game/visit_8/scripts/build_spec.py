#!/usr/bin/env python3
"""rows_spec.json for make_rows.py (visit 8)."""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
T0, T1, T2 = "identity_pyrelands_before_hawkfix.json", "identity_pyrelands.json", "identity_pyrelands_final.json"
RUN = "python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains "
WILD = "our clock's stop, not the mod's: safe_advance stops on harm to wildlife, which this read does not look at. The stop: a wild %s (GOVERNOR_STOP in %s). What hurt the animal is not read. Fixed by the wildlife shield"
EV = "design/concepts/Pyrelands/version/in_game/visit_8/evidence/"
S = []
def row(test, label, ident, sha, **k):
    S.append(dict(test=test, label=label, identity=ident, mod_sha=sha, **k))
row("P_furnace_room", "furnace_room", T0, "454764adbe", note="beast room 81.8 C, control 56.0 C, 0 open roof cells (Huge Things at its defaults)")
row("sc_burn_line_walks", "burn_line", T0, "ee7c70bbf9", outcome="APPARATUS FAULT",
    note=WILD % ("barbslinger downed a wild fire wasp on day 4", "run_burn_line.log, tick 606559"))
row("sc_burn_line_walks", "burn_line2", T0, "05d3da7407", note="with the wildlife shield (05d3da7407); lanes_probe on its walking save: strand share 0.046 (limit 0.25), no one-cell run; naive GPT judge of the hourly and day-end captures: YES (evidence/burn_line_naive_judge_gpt.md)")
row("sc_burn_line_walks", "burn_line3", T2, "259988da10", note="the shield's last edit (6e9257a1af) touches this check, so it ran again; judge reading as burn_line2's")
row("sc_fire_walks_with_wind", "wind_burn_live", T0, "ee7c70bbf9", script="script_wind_burn_live.log")
row("sc_ashwallow", "burrowers", T1, "4ae211941a")
row("sc_firehawk", "gate_off_source", T0, "ee7c70bbf9", script="script_gate_off_source.log", outcome="MOD FAILURE", verdict_is="FAIL", **{"class": "MOD"},
    forbidden=["a fire lit by a fire-hawk's ember 500 ticks after Mod enabled went off"], command="python.exe design/concepts/Pyrelands/version/in_game/visit_8/scripts/gate_off_source.py",
    detail="first seen as walk_gate_off_then_on FAIL on the tier (236 fires after a gate-off day, run_walk_gate_real.log); the probe named the source: a hawk already carrying an ember")
row("sc_firehawk", "firehawk", T1, "4ae211941a", outcome="APPARATUS FAULT",  **{"class": "SITE"},
    unrepaired=None, detail="firehawk_carries_ember PASS; far_hawk_seeks_the_burn FAIL: the spawned hawk was thirsty; RM_DrinkFromTerrain flew it from 104 to 44 cells, inside the ember reach, so the carry took over and the seek band was never tried; far_hawk_spread_off_control PASS")
SW = "python3 src/RimMandrake/Pyrelands/selftest_pyrelands_settings_sweep.py"
PROBE = "python.exe design/concepts/Pyrelands/version/in_game/visit_8/scripts/gate_off_source.py"
row("sc_firehawk", "firehawk2", T2, "f83b30b60a", **{"class": "SITE"},
    mod_fix={"commit": "4a9d62cae0e75bfbbb8a3881275fbbd21302ed8a", "unit": "rm-detached-bench-rimmandrake-drive-pyrelands-in-game-acce-1795488887",
             "red": {"cmd": SW, "rc": 1, "on": "ee7c70bbf9", "live": PROBE + ": a fire at 500 ticks (evidence/script_gate_off_source.log)"},
             "green": {"cmd": SW, "rc": 0, "on": "4a9d62cae0e75bfbbb8a3881275fbbd21302ed8a", "live": PROBE + ": no fire in 60,000 ticks (evidence/script_gate_off_source_fixed.log)"}},
    repair={"class": "SITE", "commit": "f83b30b60ac2ca89053d39c3d82627d0e2bfa2a6",
    "what": "the far hawk starts watered and fed",
    "planted": {"plant": "PYRE_PLANT_FARHAWK_NO_SEEK=1: fireHawkSpreadEnabled off for the row, as if the hawk never sought",
                "command": "PYRE_PLANT_FARHAWK_NO_SEEK=1 (through WSLENV) " + RUN + "firehawk", "verdict": "FAIL", "evidence": EV + "pv8_firehawk_planted_no_seek.json"}})
row("sc_firehawk_rewards", "firehawk_first_sighting_letter", T1, "4ae211941a")
row("firehawk_first_sighting_letter", "firehawk_first_sighting_letter", T1, "4ae211941a")
row("sc_scorchfruit", "scorchfruit", T1, "4ae211941a")
row("sc_fire_dusts_ash", "fire_tick_effects", T1, "4ae211941a")
row("sc_furnace", "furnace_warmth", T1, "4ae211941a")
row("sc_burn_compounds", "fresh_burn_bonus", T1, "4ae211941a", outcome="APPARATUS FAULT",
    note=WILD % ("barbslinger downed a wild fire-hawk on day 1", "run_fresh_burn_bonus.log"))
row("sc_burn_compounds", "fresh_burn_bonus2", T2, "6e9257a1af")
row("sc_grass_regreens", "regrow", T1, "4ae211941a", outcome="APPARATUS FAULT",
    note=WILD % ("nuna hen was downed beside a burned flamefang", "run_regrow.log"))
row("sc_grass_regreens", "regrow2", T2, "6e9257a1af")
row("P_animal_census", "animal_census", T2, "259988da10")
T3, TF = "identity_pyrelands_final.json", "identity_full.json"
TS, TL = "identity_full_smoke4.json", "identity_pyrelands_last.json"
row("sc_firehawk_rewards", "letter3", T3, "694d79e5b8")
row("firehawk_first_sighting_letter", "letter3", T3, "694d79e5b8")
row("sc_reload_keeps_the_burn", "reload_keeps_the_burn", T3, "dc4758cbb1", note="plants front_lost and old_save both FAIL (pv8_reload_planted_*.json)")
row("sc_fire_sense", "fire_sense", T3, "dc4758cbb1", outcome="APPARATUS FAULT", **{"class": "HARNESS"},
    detail="fire_sense_hungry_eats_first FAIL: the harness's feeder (t.feed) topped H's Food from 0.08 to 1.0 in the first chunk, so H was not hungry; the other four parts PASS (visit 2's F9 is the same)")
row("sc_fire_sense", "fire_sense2", T3, "694d79e5b8", **{"class": "HARNESS"}, repair={"class": "HARNESS", "commit": "694d79e5b85b6412d9fad2d9588ef4f3fe24494b",
    "what": "the hunger row runs with the feeder off (_unfed) and asserts Food at the start",
    "planted": {"plant": "PYRE_PLANT_EAT_FIRST_GATE_OFF=1: Mod enabled off for the row, as if the mod's think-tree insert did nothing",
                "command": "PYRE_PLANT_EAT_FIRST_GATE_OFF=1 (through WSLENV) " + RUN + "fire_sense", "verdict": "FAIL", "evidence": EV + "pv8_fire_sense_planted.json"}})
row("sc_full_list_smoke", "full_list_smoke", TF, "dc4758cbb1", outcome="APPARATUS FAULT",
    note="stopping the long walk by killing its driver had left Mod enabled off in the running game (evidence/script_settings_peek.log); the scene read that state FAIL, as it should")
row("sc_full_list_smoke", "full_list_smoke2", TF, "dc4758cbb1", note="the centre moved 3.04 cells against 3.0; the pad was never-burned soil (see full_list_smoke3)")
row("sc_full_list_smoke", "full_list_smoke3", TS, "694d79e5b8", outcome="APPARATUS FAULT", **{"class": "SITE"},
    detail="the centre moved 2.7 cells (< 3.0): the scene laid never-burned soil, where every fire lit in the three hours still burned (25, 52, 79 fires), so the centre of all that burns moved half the front's way; the front itself walked")
row("sc_full_list_smoke", "full_list_smoke4", TS, "177a585e57", **{"class": "SITE"}, repair={"class": "SITE", "commit": "177a585e571a205c0bde9d900dabd562371da7f1",
    "what": "the pad is deep ash, the biome's own ground, where a fire ends with its grass",
    "planted": {"plant": "PYRE_PLANT_SMOKE=no_front: the map put out every hour (and log_error: an error that names Pyrelands; both FAIL)",
                "command": "PYRE_PLANT_SMOKE=no_front (through WSLENV) " + RUN + "full_list_smoke", "verdict": "FAIL", "evidence": EV + "pv8_smoke4_planted_no_front.json"}},
    note="11, 15, 11 fires, centre moved 4.2 cells, no error of ours, 99.7% of his list. Identity: the mod hash was read on the tier load eleven minutes later with no deploy between, the list from the full-list reading of 00:03 (the same 315 ids were live at 03:13)")
row("sc_reload_keeps_the_burn", "reload2", TL, "177a585e57", note="again after the scene file changed; the plants of 02:33 and 02:35 read FAIL on the same reload code")
json.dump(S, open(os.path.join(H, "rows_spec.json"), "w"), indent=1)
