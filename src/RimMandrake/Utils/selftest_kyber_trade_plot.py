#!/usr/bin/env python3
"""selftest_kyber_trade_plot.py -- KYBER_TRADE_PLOT_1, offline.

Two halves:
  1. The C# selftest (src/RimUtinni/KyberTradePlot/Source/SelfTest/): the mod's real sources compiled against the
     game's real Assembly-CSharp. The sale count over real Tradeable/TradeDeal objects, the Harmony patch applied to
     the real TradeDeal.TryExecute, the donation's delivery read from TradeRequestComp.Fulfill's real IL, the heat
     written into a real GameComponent_ColonyVisibility, and the plot's state machine run tick by tick through sales,
     the one visit and the one donation. Built by winbuild staging, run with dotnet.exe.
  2. The shipped defs, read as XML: the donation quest pays no reward (no QuestNode_GiveRewards, K2), creates no
     faction, pawn or site for anyone, and every node class the plot's defs name is real (vanilla or this mod's own);
     the visit is an incident only this mod's state fires (baseChance 0); every key the C# translates exists.

    python3 src/RimMandrake/Utils/selftest_kyber_trade_plot.py
"""
from __future__ import annotations

import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
MOD = os.path.join(REPO, "src", "RimUtinni", "KyberTradePlot")
CSPROJ = os.path.join(MOD, "Source", "SelfTest", "KyberTradePlot.SelfTest.csproj")

# Nodes that would give the donation a payout, or put a faction, pawn or site on the world for anyone.
FORBIDDEN_NODES = ("QuestNode_GiveRewards", "QuestNode_GenerateFaction", "QuestNode_GeneratePawn", "QuestNode_GenerateSite",
                   "QuestNode_GetFaction", "QuestNode_JoinPlayer", "QuestNode_Reward", "QuestNode_SpawnWorldObjects")


def static_checks():
    fails, oks = [], []

    def check(name, ok, detail=""):
        (oks if ok else fails).append(name + (("  [" + detail + "]") if detail else ""))

    quest = ET.parse(os.path.join(MOD, "Defs", "QuestScriptDefs", "RUT_KyberDonationSmuggle.xml")).getroot()
    nodes = [e for e in quest.iter() if e.get("Class")]
    classes = [e.get("Class") for e in nodes]
    bad = sorted({c for c in classes if any(c.startswith(f) for f in FORBIDDEN_NODES)})
    check("the donation quest pays no reward and creates no faction, pawn or site", not bad, ", ".join(bad) or "%d nodes read" % len(classes))
    fulfilled = [e for e in nodes if (e.findtext("inSignal") or "") == "settlement.TradeRequestFulfilled"]
    kinds = sorted(li.get("Class") for li in fulfilled)
    check("on delivery: goodwill to the Homestead, a memory, the letter of thanks, the end - nothing else",
          kinds == sorted(["QuestNode_ChangeFactionGoodwill", "QuestNode_RecordHistoryEvent", "QuestNode_Letter", "QuestNode_End"]),
          ", ".join(kinds))
    gw = [li for li in fulfilled if li.get("Class") == "QuestNode_ChangeFactionGoodwill"]
    guard = [e for e in nodes if e.get("Class") == "QuestNode_IsSet" and e.findtext("name") == "homestead"]
    check("the delivery's goodwill goes to the live Homestead faction, modestly, and only when one exists",
          len(gw) == 1 and gw[0].findtext("faction") == "$homestead" and 0 < int(gw[0].findtext("change")) <= 10
          and len(guard) == 1 and guard[0].find("node") is gw[0])
    rendezvous = [e for e in nodes if e.get("Class", "").endswith("QuestNode_GetKyberRendezvous")]
    check("the rendezvous node stores the Homestead faction and the kyber's real market value the quest reads",
          len(rendezvous) == 1 and rendezvous[0].findtext("storeHomesteadAs") == "homestead"
          and rendezvous[0].findtext("storeKyberUnitValueAs") == "kyberUnitValue"
          and any("$kyberUnitValue" in (e.findtext("value") or "") for e in nodes))
    letter = next((li for li in fulfilled if li.get("Class") == "QuestNode_Letter"), None)
    text = (letter.findtext("text") if letter is not None else "") or ""
    check("the letter of thanks says it plainly: no way to help it here", "no way to help it here" in text)
    check("the rendezvous is picked by this mod's lane-only node, not vanilla's any-faction picker",
          "RimMandrake.Utinni.KyberTradePlot.QuestNode_GetKyberRendezvous" in classes and "QuestNode_GetNearbySettlement" not in classes)
    check("the donation asks for kyber by its def", any((e.findtext("value") or "") == "Force_KyberCrystal" for e in nodes))
    alltext = ""
    for root, _, files in os.walk(os.path.join(MOD, "Defs")):
        for f in files:
            alltext += open(os.path.join(root, f), encoding="utf-8").read()
    check("no def in the mod names a Rebellion faction or ally", not re.search(r"<(faction|factionDef|def)>[^<]*Rebel", alltext, re.I))

    inc = ET.parse(os.path.join(MOD, "Defs", "IncidentDefs", "IncidentDefs_KyberTradePlot.xml")).getroot()
    incs = {d.findtext("defName"): d for d in inc.findall("IncidentDef")}
    check("both incidents exist and neither is ever rolled by the storyteller (baseChance 0)",
          set(incs) == {"RUT_KyberHomesteadVisit", "RUT_GiveQuest_KyberDonationSmuggle"} and all(d.findtext("baseChance") == "0" for d in incs.values()))
    check("the visit is this mod's own visitor worker",
          incs["RUT_KyberHomesteadVisit"].findtext("workerClass") == "RimMandrake.Utinni.KyberTradePlot.IncidentWorker_KyberHomesteadVisit")

    keyed = ET.parse(os.path.join(MOD, "Languages", "English", "Keyed", "KyberTradePlot.xml")).getroot()
    keys = {e.tag: (e.text or "") for e in keyed}
    used = set()
    for f in os.listdir(os.path.join(MOD, "Source")):
        if f.endswith(".cs"):
            used |= set(re.findall(r'"(RUT_Kyber\w+)"\s*\.Translate', open(os.path.join(MOD, "Source", f), encoding="utf-8").read()))
            used |= set(re.findall(r'Answer\("(RUT_Kyber\w+)"', open(os.path.join(MOD, "Source", f), encoding="utf-8").read()))
    check("every key the C# translates is in the English Keyed file", used and used <= set(keys), ", ".join(sorted(used - set(keys))))
    check("the visitor never says 'Jedi' of themself: the word appears only as what nobody says",
          "Nobody uses the word \"Jedi\"" in keys.get("RUT_KyberVisitText", "") and
          sum(v.count("Jedi") for v in keys.values()) == 1)
    return oks, fails


def run_csharp():
    sys.path.insert(0, HERE)
    import winbuild
    if winbuild.dotnet_exe() is None:
        print("UNMEASURED: no dotnet.exe; the C# half cannot run here")
        return 2
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="SelfTest_kyber_trade_plot")
    if rc:
        print("selftest build FAILED")
        return rc
    dotnet = winbuild.dotnet_exe()
    cmd = [dotnet, "run", "--project", winbuild.staged_win(rec, CSPROJ), "-c", "Release", "--no-build"]
    result = winbuild.run_interop_captured(cmd, capture_output=True, text=True)
    print(result.stdout, end="")
    if result.stderr.strip():
        print(result.stderr, end="", file=sys.stderr)
    return result.returncode


def main():
    print("== the shipped defs ==")
    oks, fails = static_checks()
    for o in oks:
        print("ok    " + o)
    for f in fails:
        print("FAIL  " + f)
    print()
    rc = run_csharp()
    print("STATIC %s (%d ok, %d failed); C# exit %d" % ("PASS" if not fails else "FAIL", len(oks), len(fails), rc))
    sys.exit(1 if fails or rc else 0)


if __name__ == "__main__":
    main()
