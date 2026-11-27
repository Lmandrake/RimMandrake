#!/usr/bin/env python3
"""THROWAWAY: show that preflight_wreckedmachines.py refuses a table with a planted fault, check by check.

Each plant changes one thing in a copy of version/test_table.json, runs the preflight on the copy (--table, --out to the
agent storage root; the real record is not touched) and wants the named check to refuse with more refusals than it has on
the real table. C12 (pins) and C14 (bridge tools) read files, not the table: C12 is shown by hand (journal), and C14 carries
its own probe.
Usage: python3 plant_preflight_faults.py <repo>      exit 0 every plant refused where it should, 1 otherwise
"""
import copy
import json
import os
import subprocess
import sys

REPO = os.path.abspath(sys.argv[1])
os.chdir(REPO)
HERE = "design/concepts/WreckedMachines/version"
PRE = HERE + "/pilot_throwaway/preflight_wreckedmachines.py"
STORE = subprocess.run(["python3", os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")],
                       capture_output=True, text=True).stdout.strip()
if not STORE:
    sys.exit("could not read the agent storage root")
W = os.path.join(STORE, "rimmandrake/scratch/wreckedmachines_preflight/plants")
os.makedirs(W, exist_ok=True)
REAL = json.load(open(HERE + "/test_table.json"))


def run(tab, name):
    tp, op = os.path.join(W, name + ".table.json"), os.path.join(W, name + ".preflight.json")
    json.dump(tab, open(tp, "w"))
    if os.path.exists(op):
        os.remove(op)
    p = subprocess.run(["python3", PRE, REPO, "--table", tp, "--out", op], capture_output=True, text=True)
    if not os.path.exists(op):
        return None, "no record (rc %s): %s" % (p.returncode, (p.stdout + p.stderr)[-300:])
    return {c["id"]: len(c["refusals"]) for c in json.load(open(op))["checks"]}, ""


def bar(t, i):
    return next(b for b in t["bars"] if b["id"] == i)


def p_version(t): t["version"] = "0.2.0"
def p_drop_bar(t): t["bars"] = [b for b in t["bars"] if b["id"] != "whole_journey"]
def p_no_decider(t): bar(t, "wreck_is_found")["decides"] = []
def p_look_decides(t): bar(t, "whole_journey")["decides"].append("LOOK_STAGE8")
def p_undefined(t): bar(t, "wreck_is_found")["decides"].append("sc_no_such_scene")
def p_stage(t): t["tests"]["sc_marks_agree"]["stage"] = "5"
def p_proves_at(t): bar(t, "whole_journey")["proves_at"] = "4-5"
def p_file(t): t["tests"]["T_KERNEL_FUZZ"]["file"] = "src/RimMandrake/Utils/selftest_no_such_file.py"
def p_reads(t): t["tests"]["T_SALVAGE_RULE"]["reads"] = ["src/RimMandrake/WreckedMachines/no_such_file.py"]
def p_entry_flag(t): t["tests"]["sc_menu_and_research"]["entry_exists"] = False
def p_stale_new(t): t["tests"]["T_SALVAGE_RULE"]["new"] = True
def p_red(t): t["tests"]["T_SALVAGE_RULE"]["runs_today"]["result"] = "FAIL"
def p_not_run(t): t["tests"]["sc_wreck_link_tags"]["runs_today"] = {"ran": False}
def p_entry_gone(t): t["tests"]["sc_component_gate"]["entry"] = "scene_no_such_entry"
def p_why_game(t): t["tests"]["sc_carry_wreck_home"]["why_game"] = ""
def p_held(t): t["held_note"] = ""
def p_def(t): t["tests"]["sc_forge_plasteel"]["observes"] += " RM_WM_NoSuchDef_Planted"
def p_donor_def(t): t["tests"]["sc_forge_plasteel"]["observes"] += " VFEFactory_NoSuchMachine_Planted"
def p_no_tier(t): t["tests"]["sc_marks_agree"]["tier"] = None
def p_tier(t): t["tests"]["sc_marks_agree"]["tier"] = "no_such_tier"
def p_tier_flag(t): t["tests"]["sc_marks_agree"]["tier_defined"] = False
def p_kind_none(t): del t["tests"]["sc_marks_agree"]["test_kind"]
def p_kind_b(t): t["tests"]["sc_rare_wreck_ordinary_map"]["test_kind"] = "B"
def p_x_of_y(t): t["tests"]["sc_rare_wreck_ordinary_map"]["x_of_y"] = [3, 2]
def p_scene_gone(t): del t["tests"]["sc_first_look_built_mod"]
def p_check_gone(t): del t["checks_map"]["C_old_save"]
def p_accept_not_decider(t): bar(t, "wreck_comes_home")["decides"].remove("sc_carry_wreck_home")
def p_item(t): t["tests"]["sc_marks_agree"]["item"] = "RIMMANDRAKE_NO_SUCH_ITEM_PLANTED"


def p_hunt_only(t):
    for d in bar(t, "wreck_comes_home")["decides"]:
        t["tests"][d].update(test_kind="C", tag_evidence="planted: a symptom seen once in forty opportunities, trace in a log")


PLANTS = [("C0_version_locked", p_version), ("C1_bars_complete", p_drop_bar), ("C2_every_bar_has_a_test", p_no_decider),
          ("C2_every_bar_has_a_test", p_look_decides), ("C2_every_bar_has_a_test", p_undefined),
          ("C3_every_test_has_a_stage", p_stage), ("C3_every_test_has_a_stage", p_proves_at), ("C4_test_files_real", p_file),
          ("C5_read_files_real", p_reads), ("C6a_table_flags_true", p_entry_flag), ("C6a_table_flags_true", p_stale_new),
          ("C6_built_deciders_run", p_red), ("C6_built_deciders_run", p_not_run), ("C6_built_deciders_run", p_entry_gone),
          ("C7_game_reason_written", p_why_game), ("C8_held_statements_placed", p_held), ("C9_defs_real", p_def),
          ("C9_defs_real", p_donor_def), ("C10_mods_real", p_no_tier), ("C10b_tiers_defined", p_tier),
          ("C10_mods_real", p_tier_flag), ("C11_scene_kinds", p_kind_none), ("C11_scene_kinds", p_kind_b),
          ("C11_scene_kinds", p_x_of_y), ("C11_scene_kinds", p_hunt_only), ("C13_scenes_and_checks_wired", p_scene_gone),
          ("C13_scenes_and_checks_wired", p_check_gone), ("C13_scenes_and_checks_wired", p_accept_not_decider),
          ("C15_items_real", p_item)]

base, why = run(REAL, "real")
if base is None:
    sys.exit("the preflight wrote no record on the real table: " + why)
bad = 0
for want, plant in PLANTS:
    t = copy.deepcopy(REAL)
    plant(t)
    got, why = run(t, plant.__name__)
    ok = got is not None and got.get(want, 0) > base.get(want, 0)
    bad += not ok
    print("%-8s %-28s %-22s real %d, planted %s %s" % ("RED" if ok else "MISSED", want, plant.__name__, base.get(want, 0),
                                                       got.get(want) if got else "no record", why))
print("plants: %d, refused where planted: %d, missed: %d" % (len(PLANTS), len(PLANTS) - bad, bad))
sys.exit(1 if bad else 0)
