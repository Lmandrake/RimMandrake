#!/usr/bin/env python3
"""rows_spec.json for make_rows.py (visit 9)."""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
T, F = "identity_pyrelands.json", "identity_full.json"
S = []
def row(test, label, ident=T, **k):
    S.append(dict(test=test, label=label, identity=ident, **k))
row("sc_full_list_smoke", "full_list_smoke", F, note="run first: his full list was already up with the a6f05380df DLL; site NS_Pyrelands_site_1_417df172fdb5_visit9full, tile 49")
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
json.dump(S, open(os.path.join(H, "rows_spec.json"), "w"), indent=1)
