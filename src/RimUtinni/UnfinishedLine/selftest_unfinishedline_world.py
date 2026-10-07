"""selftest_unfinishedline_world.py -- UNFINISHED_LINE_WORLD_FOUNDRY_1, offline.

Proves validation.world_static_checks passes on the shipped mod AND can see each defect it claims to catch: every
mutation below is applied to a temp copy of the mod and must produce a finding. A checker that never fails is a
name list, not a test.

    python3 src/RimUtinni/UnfinishedLine/selftest_unfinishedline_world.py
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validation  # noqa: E402

VOL = os.path.join("Defs", "QuestScriptDefs", "RUT_LineVolunteer.xml")
WORLD_CS = os.path.join("Source", "UnfinishedLineWorld.cs")

MUTATIONS = [
    ("volunteer def deleted", VOL, None, None),
    ("joinPlayer false", VOL, "<joinPlayer>true</joinPlayer>", "<joinPlayer>false</joinPlayer>"),
    ("randomly offered", VOL, "<rootSelectionWeight>0</rootSelectionWeight>", "<rootSelectionWeight>1</rootSelectionWeight>"),
    ("watch armed on a signal", VOL, "<pawns>$volunteers</pawns>\n        </li>",
     "<pawns>$volunteers</pawns>\n          <inSignal>Later</inSignal>\n        </li>"),
    ("failable", VOL, "<outcome>Success</outcome>", "<outcome>Fail</outcome>"),
    ("generates a head", VOL, "<kindDef>RSW_DW_KotORDroidGood_3C</kindDef>", "<kindDef>RSW_DW_Head_Labour</kindDef>"),
    ("defName drift in C#", WORLD_CS, 'VolunteerQuestDefName = "RUT_LineVolunteer"', 'VolunteerQuestDefName = "RUT_LineVolunteerX"'),
]


def run():
    fails = []
    base = validation.world_static_checks([])
    if base:
        fails.append("shipped mod has findings: %r" % base)
    if validation.world_static_checks(["RUT_LineVolunteer"]) == []:
        fails.append("volunteer on the spine was not caught")
    tmp = tempfile.mkdtemp(prefix="ulworld_")
    orig_here = validation.HERE
    try:
        for name, rel, old, new in MUTATIONS:
            copy = os.path.join(tmp, name.replace(" ", "_"))
            shutil.copytree(orig_here, copy, ignore=shutil.ignore_patterns("Assemblies", "__pycache__"))
            p = os.path.join(copy, rel)
            if old is None:
                os.remove(p)
            else:
                s = open(p, encoding="utf-8").read()
                if old not in s:
                    fails.append("mutation '%s' did not apply (anchor missing)" % name)
                    continue
                open(p, "w", encoding="utf-8").write(s.replace(old, new, 1))
            validation.HERE = copy
            try:
                found = validation.world_static_checks([])
            finally:
                validation.HERE = orig_here
            if not found:
                fails.append("mutation '%s' produced no finding" % name)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    total = len(MUTATIONS) + 2
    print("selftest_unfinishedline_world: %d/%d" % (total - len(fails), total))
    for f in fails:
        print("  FAIL " + f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(run())
