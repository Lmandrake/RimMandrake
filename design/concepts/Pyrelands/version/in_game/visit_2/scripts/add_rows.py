"""Visit 2 rows with no driver evidence: the standalone proof scripts that ran, and the checks this sitting did not run
(python3, offline; appends to rows.jsonl, identity merged from evidence/identity_<tier>.json)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.dirname(HERE)
REL = "design/concepts/Pyrelands/version/in_game/visit_2"
ident = json.load(open(os.path.join(V2, "evidence", "identity_pyrelands.json")))
ME = "RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO"
SITE = "NS_Pyrelands_site_1_bf7f9e1fe4_visit2 (tile 3), gate B CLEAN at build; read-only getters on the loaded site"
ran = [
    ("P_gate", "PASS", "python.exe src/RimMandrake/Pyrelands/gate_live_proof.py A1; python.exe src/RimMandrake/Pyrelands/gate_live_proof.py A2",
     [REL + "/evidence/gate_A1.log", REL + "/evidence/gate_A2.log"], "A1 ShellPresent=True On=True; A2 ShellOn=True RM_BiomesSettings.Enabled(Pyrelands)=True"),
    ("P_firefoam_aim", "PASS", "python.exe src/RimMandrake/Pyrelands/firefoam_aim_live_proof.py",
     REL + "/evidence/script_firefoam_aim_live_proof.log", "FIREFOAM fire True | cell True | validFire True | validCell True | hitFire True | hitCell True | control fire False cell False"),
    ("sc_fire_walks_with_wind", "PASS", "python.exe src/RimMandrake/Pyrelands/wind_burn_live.py",
     REL + "/evidence/script_wind_burn_live.log", "PASS (9 of 9 rows): downwind 8 vs upwind 0; reversed wind runs west 11 vs 0; no fire beside the lanes; control even spread (42 in the outer lanes); black rain puts the line out (9 -> 0)"),
]
not_run = {
    "sc_walk": "the full-list walk (his 315-mod list, a ~15 min cold load, then two game weeks) did not fit the 3-hour bound after the minimal-list checks",
    "sc_rite_hook_alone": "needs the pyrelands tier without mandrake.rut.pyrelandsmechanics (a second load); not reached",
    "sc_herd_thirst": "started at 20:46, stopped by this run to put the repaired reruns first; seven game days",
    "sc_grass_regreens": "embergrass_regrow (seven game days on the real clock); SteveDesktop's run was UNMEASURED (no site there); not reached here",
    "P_scorchfruit_spoils": "scorchfruit_spoils (up to 270,000 ticks); SteveDesktop's run was UNMEASURED; not reached here",
    "P_scorchfruit_produces": "started 21:37 on Archmagi; the run was stopped by the spend watchdog before the chain wrote evidence; the resumed run (23:06) found game a's bridge held by another run (FlowWorks judge, active), so it was not rerun",
    "P_opening_front": "never started: the run was stopped by the spend watchdog first; the resumed run (23:06) found game a's bridge held by another run (FlowWorks judge, active)",
}
out = []
for test, v, cmd, ev, note in ran:
    r = {"test": test, "verdict": v, "site_checked": True, "game": "archmagi", "command": cmd, "evidence": ev,
         "held": [], "site": SITE, "note": note}
    r.update(ident)
    out.append(r)
CHAIN = {"sc_walk": "walk_season", "sc_rite_hook_alone": "rite_hook_alone", "sc_herd_thirst": "herd_thirst",
         "sc_grass_regreens": "embergrass_regrow", "P_scorchfruit_spoils": "scorchfruit_spoils",
         "P_scorchfruit_produces": "scorchfruit_produces", "P_opening_front": "opening_front"}
DRIVER = ("python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan "
          "src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains %s")
for test, why in not_run.items():
    r = {"test": test, "verdict": "UNMEASURED", "site_checked": False, "game": "archmagi", "command": DRIVER % CHAIN[test],
         "evidence": None, "held": [], "not_run": why, "owner": ME + " (LEFT OPEN: the next run of this brief runs it)"}
    r.update(ident)
    out.append(r)
with open(os.path.join(V2, "rows.jsonl"), "a", encoding="utf-8") as f:
    for r in out:
        f.write(json.dumps(r) + "\n")
print("added", len(out))
