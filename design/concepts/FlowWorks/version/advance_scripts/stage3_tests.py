#!/usr/bin/env python3
"""Throwaway (FlowWorks Stage 3 reconcile, 2026-11-14): point the six owed offline tests at selftest_stage3_owed.py and
mark the 17 written scene entries as existing, UNRUN, with their exact command. Run rerun_tests.py after it."""
import json, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 5))
os.chdir(ROOT)
P = "design/concepts/FlowWorks/version/test_table.json"
tab = json.load(open(P))
F = "src/RimMandrake/FlowWorks/selftest_stage3_owed.py"
for k, sec in {"T_PRISON_CARE_OFFLINE": "prison_care", "T_WETTING_OFFLINE": "wetting", "T_WETNESS_PROBE_OFFLINE": "wetness_probe",
               "T_TOSS_FLAME_OFFLINE": "toss_flame", "T_FETCH_FALLEN_OFFLINE": "fetch_fallen", "T_LIQUID_COATING_OFFLINE": "coating"}.items():
    t = tab["tests"][k]
    t["file"] = F
    t["command"] = "python3 %s --only %s" % (F, sec)
    t["reads"] = sorted(set((t.get("reads") or []) + [F]))
CS = "src/RimMandrake/FlowWorks/northstar/concept_scenes.py"
src = open(CS).read()
n = 0
for k, t in tab["tests"].items():
    if t["kind"].startswith("live") and t.get("file") == CS and t.get("entry") and t["entry"] != "scene_hole_prison":
        assert "\nscene_%s = _run(" % t["entry"][6:] in src or "\ndef %s(" % t["entry"] in src, t["entry"]
        t["command"] = "python.exe src\\RimMandrake\\FlowWorks\\northstar\\concept_scenes.py --scene %s --out <json>  (bridge held; %s)" % (
            t["entry"], "his full list" if t["kind"] == "live_full" else "minimal list + FlowWorks")
        t["runs_today"] = {"ran": False, "entry_exists": True,
                           "why": "UNRUN: written Stage 3 2026-11-14, import- and lint-checked and smoke-run on a fake bridge; never the game"}
        n += 1
json.dump(tab, open(P, "w"), indent=1)
print(n, "scenes marked")
