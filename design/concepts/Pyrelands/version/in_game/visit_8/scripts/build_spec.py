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
row("sc_firehawk", "firehawk", T1, "4ae211941a", outcome="APPARATUS FAULT",  **{"class": "SITE"},
    unrepaired=None, detail="firehawk_carries_ember PASS; far_hawk_seeks_the_burn FAIL: the spawned hawk was thirsty; RM_DrinkFromTerrain flew it from 104 to 44 cells, inside the ember reach, so the carry took over and the seek band was never tried; far_hawk_spread_off_control PASS")
row("sc_firehawk", "firehawk2", T2, "f83b30b60a", **{"class": "SITE"}, repair={"class": "SITE", "commit": "f83b30b60ac2ca89053d39c3d82627d0e2bfa2a6",
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
json.dump(S, open(os.path.join(H, "rows_spec.json"), "w"), indent=1)
