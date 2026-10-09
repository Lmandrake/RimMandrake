#!/usr/bin/env python3
"""Planted-defect selftest for lint_aftermath_defs.py: clean on the real engine and the shipped rule data, then one planted defect at a time
(in a copy of the engine, or in a copy of the rule defs) is caught.

    python3 src/RimMandrake/Utils/selftest_aftermath_lint.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modpack_lint_harness as H  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
RULES = os.path.join(REPO, "src", "RimUtinni", "AftermathRites", "Defs")
M = "Source/RM_AftermathMod.cs"
K = "Source/Kernel/RM_AftermathKernel.cs"
PLANTS = [
    ("slider excludes the default", M, "list.Slider(mentalBreakWindowDays, 0.5f, 7f)", "list.Slider(mentalBreakWindowDays, 3f, 7f)", "af-settings"),
    ("kernel day length wrong", K, "TicksPerDay = 60000;", "TicksPerDay = 2500;", "af-settings"),
    ("kernel imports Verse", K, "using System;", "using System;\nusing Verse;", "af-kernel"),
    ("harmony id differs from the packageId", "Source/AftermathMod.cs", 'HarmonyId = "mandrake.rm.aftermath"', 'HarmonyId = "mandrake.rm.aftermat"', "af-kernel"),
    ("kernel missing from the csproj", "Source/RM_Aftermath.csproj", '<Compile Include="Kernel\\RM_AftermathKernel.cs" />', "", "compile-listed"),
    ("settings key differs", M, 'Scribe_Values.Look(ref maxQueuedTotal, "maxQueuedTotal", 2)', 'Scribe_Values.Look(ref maxQueuedTotal, "queuedTotal", 2)', "settings-scribed"),
]
RULE_PLANTS = [
    ("trigger kind typo", "<triggerKind>BattleOutcome</triggerKind>\n    <triggerOutcomes>", "<triggerKind>BattleOutcom</triggerKind>\n    <triggerOutcomes>", "af-rule"),
    ("outcome typo", "<li>Routed</li>", "<li>Rooted</li>", "af-rule"),
    ("payload faction mode typo", "<payloadFactionMode>SameAsTrigger</payloadFactionMode>", "<payloadFactionMode>SameAsTrigge</payloadFactionMode>", "af-rule"),
    ("payload incident that does not exist", "<payloadIncidentDefName>RaidEnemy</payloadIncidentDefName>", "<payloadIncidentDefName>RaidEnemee</payloadIncidentDefName>", "af-rule"),
    ("delay inverted", "<delayDaysMin>2</delayDaysMin>", "<delayDaysMin>20</delayDaysMin>", "af-rule"),
    ("held days zero", "<minHeldDays>3</minHeldDays>", "<minHeldDays>0</minHeldDays>", "af-rule"),
    ("prisoner rule with the wrong faction mode", "<payloadFactionMode>HeldPrisonerHome</payloadFactionMode>", "<payloadFactionMode>SameAsTrigger</payloadFactionMode>", "af-rule"),
    ("telegraph uses a second argument", "Someone is coming back to look harder at what beat them.", "Someone is coming back to look harder at what beat {1}.", "af-format"),
    ("lone brace in a letter", "did not forget what happened last time.", "did not forget { what happened last time.", "af-format"),
    ("letter uses a third argument", "{0} comes because of what you did to their friends.", "{0} comes because of what you did to {2}.", "af-format"),
    ("alliance names a faction nobody defines", "<b>RUT_Jawa_FreeDroidEnclaves</b>", "<b>RUT_Jawa_FreeDroidEnclave</b>", "af-pairs"),
]


def rules_selftest():
    bad = 0
    import lint_aftermath_defs as L  # noqa: F401
    base = subprocess.run([sys.executable, os.path.join(HERE, "lint_aftermath_defs.py"), "--rules-dir", RULES, "--quiet"], capture_output=True, text=True)
    print(("ok   " if base.returncode == 0 else "FAIL ") + "real rule data is clean")
    bad += base.returncode != 0
    tmp = tempfile.mkdtemp(prefix="afrules_")
    try:
        for label, old, new, want in RULE_PLANTS:
            d = os.path.join(tmp, "defs")
            shutil.rmtree(d, ignore_errors=True)
            shutil.copytree(RULES, d, ignore=shutil.ignore_patterns("__pycache__"))
            hit_file = None
            for fn in os.listdir(d):
                path = os.path.join(d, fn)
                t = open(path, encoding="utf-8").read()
                if old in t:
                    open(path, "w", encoding="utf-8").write(t.replace(old, new, 1))
                    hit_file = fn
                    break
            if hit_file is None:
                print("FAIL %s: pattern not found" % label)
                bad += 1
                continue
            p = subprocess.run([sys.executable, os.path.join(HERE, "lint_aftermath_defs.py"), "--rules-dir", d, "--quiet"], capture_output=True, text=True)
            out = p.stdout + p.stderr
            hit = p.returncode == 1 and any(l.startswith("ERROR") and want in l for l in out.splitlines())
            print(("ok   " if hit else "FAIL ") + label + ("" if hit else " | rc=%s %s" % (p.returncode, out.strip().splitlines()[-1][:120] if out.strip() else "")))
            bad += not hit
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return bad


if __name__ == "__main__":
    rc = H.run("Aftermath", "lint_aftermath_defs.py", PLANTS, keep=("About",))
    bad = rules_selftest()
    n = len(RULE_PLANTS) + 1
    print("aftermath rule-data planted-defect selftest: %d/%d ok" % (n - bad, n))
    sys.exit(1 if (rc or bad) else 0)
