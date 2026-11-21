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
not_run = {}
if not os.path.exists(os.path.join(V2, "evidence", "pv2_walk_season.json")):
    not_run["sc_walk"] = ("the full-list walk_season chain wrote no evidence in run 3 (see Transient/pv2/runner.progress "
                          "FULL lines and SUMMARY's run-3 notes)")
out = []
def _opening_front_row():
    """P_opening_front = the driver's opening_front part (re-arm, front lit) + the old-save part. The site was born after
    the front shipped, so the driver's own old-save read is UNMEASURED (SITE); scripts/old_save_read.py reads a save made
    before 05033a3f7 instead, judged by validation.old_save_opening_verdict."""
    import sys
    root = os.path.abspath(os.path.join(V2, *[".."] * 6))
    sys.path[:0] = [os.path.join(root, "src/RimMandrake/Utils"), os.path.join(root, "src/RimMandrake/Pyrelands")]
    import validation as VAL
    d = json.load(open(os.path.join(V2, "evidence", "pv2_opening_front.json")))
    front = [c for c in d["components"] if c.get("name") == "opening_front"]
    fv = front[0]["verdict"] if front else "UNMEASURED"
    osr_p = os.path.join(V2, "evidence", "old_save_read.json")
    osr = json.load(open(osr_p)) if os.path.exists(osr_p) else {}
    kv = VAL.parse_kv(str(osr.get("before") or "")) if osr.get("ready") else {}
    kv_after = VAL.parse_kv(str(osr.get("after") or "")) if osr.get("ready") else {}
    if kv:
        ov, why = VAL.old_save_opening_verdict(kv)
        if ov == "PASS" and kv_after:
            ov2, why2 = VAL.old_save_opening_verdict(kv_after)
            ov, why = (ov2, "after one window: " + why2) if ov2 != "PASS" else (ov, why + "; after one window: " + why2)
    else:
        ov, why = "UNMEASURED", "old-save read: %s" % (osr.get("load") or "not run")
    v = "FAIL" if "FAIL" in (fv, ov) else "UNMEASURED" if "UNMEASURED" in (fv, ov) else "PASS"
    return ("P_opening_front", v,
            "python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan "
            "src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains opening_front; python.exe " + REL +
            "/scripts/old_save_read.py",
            [REL + "/evidence/pv2_opening_front.json", REL + "/evidence/old_save_read.json"],
            "front part %s; old-save part on %s: %s %s" % (fv, osr.get("save"), ov, why))
ran.append(_opening_front_row())
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
