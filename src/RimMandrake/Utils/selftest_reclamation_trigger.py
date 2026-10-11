#!/usr/bin/env python3
"""Selftest for RECLAMATION_TRIGGER_REWIRE_WOKEN_COUNT (StructureInjectionsRUT).

Owner card 13, 2026-10-10: the Reclamation starts when enough ancients are woken,
not 45 days after a refused claim. Two halves:

1. Static (python, no dotnet): the generated RUT_VaultThaw.xml no longer chains
   RUT_GiveQuest_Reclamation from RUT_VaultClaimConflict; the incident the C# fires
   exists; the counter and its kernel are in the mod's Compile list; the settings
   carry the toggle and threshold.
2. The C# counting rule: Source/SelfTest compiles the REAL WokenAncientsKernel.cs and
   asserts first-sight seeding, eject counting, loot-not-counted, N fires / N-1 does
   not, fires once, toggle off never fires.

    python3 src/RimMandrake/Utils/selftest_reclamation_trigger.py [--static-only]
"""
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
MOD = os.path.join(REPO, "src", "RimUtinni", "StructureInjectionsRUT")
QUESTS = os.path.join(MOD, "Defs", "VaultDungeons", "QuestScriptDefs", "RUT_VaultThaw.xml")
INCIDENTS = os.path.join(MOD, "Defs", "VaultDungeons", "IncidentDefs_Vaults.xml")
CSPROJ = os.path.join(MOD, "Source", "RimMandrake.Utinni.StructureInjectionsRUT.csproj")
SETTINGS = os.path.join(MOD, "Source", "StructureInjectionsRUTSettings.cs")
COMPONENT = os.path.join(MOD, "Source", "VaultDungeons", "GameComponent_WokenAncients.cs")
SELFTEST = os.path.join(MOD, "Source", "SelfTest", "StructureInjectionsRUT.SelfTest.csproj")
DOTNET_CANDIDATES = ["/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe"]

failures = []


def check(ok, what):
    print(("PASS  " if ok else "FAIL  ") + what)
    if not ok:
        failures.append(what)


def static_checks():
    root = ET.parse(QUESTS).getroot()
    quests = {q.findtext("defName"): q for q in root.iter("QuestScriptDef")}
    # Sanity probe: the parse must see the quests it is about to judge.
    check({"RUT_VaultClaimConflict", "RUT_Reclamation"} <= set(quests),
          "probe: RUT_VaultClaimConflict and RUT_Reclamation parse (%d quests seen)" % len(quests))
    claim = quests.get("RUT_VaultClaimConflict")
    if claim is not None:
        incs = [e.text for e in claim.iter("incidentDef")]
        check("RUT_GiveQuest_Reclamation" not in incs,
              "the claim conflict no longer fires the Reclamation (incidentDefs: %s)" % incs)
        delays = [e.findtext("delayTicks") for e in claim.iter("li")
                  if e.get("Class") == "QuestNode_Delay"]
        check(not any("45" in (d or "") for d in delays),
              "no 45-day delay in the claim conflict (delays: %s)" % delays)
        ends = [e.findtext("inSignal") for e in claim.iter("li") if e.get("Class") == "QuestNode_End"]
        check("woken.AllEnemiesDefeated" in ends,
              "the claim conflict ends on the refusal itself (ends: %s)" % ends)
    for name, q in quests.items():
        incs = [e.text for e in q.iter("incidentDef")]
        check(name == "RUT_Reclamation" or "RUT_GiveQuest_Reclamation" not in incs,
              "%s does not chain the Reclamation" % name)
    inc_names = [d.findtext("defName") for d in ET.parse(INCIDENTS).getroot().iter("IncidentDef")]
    check("RUT_GiveQuest_Reclamation" in inc_names, "RUT_GiveQuest_Reclamation incident exists")
    comp = open(COMPONENT, encoding="utf-8").read()
    check('"RUT_GiveQuest_Reclamation"' in comp, "the counter fires that exact incident defName")
    proj = open(CSPROJ, encoding="utf-8").read()
    for f in ("WokenAncientsKernel.cs", "GameComponent_WokenAncients.cs"):
        check(re.search(r'<Compile Include="VaultDungeons\\%s"' % re.escape(f), proj) is not None,
              "%s is in the mod's Compile list" % f)
    sett = open(SETTINGS, encoding="utf-8").read()
    for field in ("reclamationByWokenCount", "reclamationWokenThreshold"):
        check(sett.count(field) >= 3, "settings field %s declared, scribed and drawn" % field)


def kernel_checks():
    dotnet = next((c for c in DOTNET_CANDIDATES if os.path.isfile(c)), None)
    if dotnet is None:
        sys.exit("dotnet.exe not found (%r): kernel half UNMEASURED, not a pass" % DOTNET_CANDIDATES)
    from selftest_winstage import windows_project_path
    win = windows_project_path(SELFTEST)
    r = subprocess.run([dotnet, "run", "--project", win, "-c", "Release"], capture_output=True, text=True)
    print(r.stdout, end="")
    if r.returncode != 0:
        print(r.stderr, end="", file=sys.stderr)
        failures.append("C# kernel selftest exit %d" % r.returncode)


def main():
    static_checks()
    if "--static-only" not in sys.argv:
        kernel_checks()
    if failures:
        print("FAILED: %d" % len(failures))
        sys.exit(1)
    print("selftest_reclamation_trigger: OK")


if __name__ == "__main__":
    main()
