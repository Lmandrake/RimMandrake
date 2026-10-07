"""selftest_feverwood_broodcampaign.py -- FEVERWOOD_BROOD_RANSOM_1 campaign half, L0.

Static reads that the campaign patch (src/RimUtinni/UtinniPatches/Patches/RUT_BroodRansom_Campaign.xml) and the
free-tier display-tank / trader / lines mechanism (Source/*.cs) agree: every Class the patch names exists, every
field the patch sets is a public field of that class, the faction, parent def and settlement it names exist, and
the C# carries the behaviours the item's criteria lean on (freed tanks never regenerate, a foreign display tank
neither feeds nor escapes on neglect, a breach or a kill still frees the young, the doubled gift survives a save).
Then each check is proven able to fail: it is re-run on temp copies with one break planted (never the shipped files).
"""
import csv
import os
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CAMPAIGN = os.path.join(REPO, "src", "RimUtinni", "UtinniPatches", "Patches", "RUT_BroodRansom_Campaign.xml")
FACTION_XML = os.path.join(REPO, "src", "RimUtinni", "UtinniPatches", "Defs", "FactionDefs", "JawaWildsteamClan.xml")
SETTLEMENTS_CSV = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_settlements.csv")
NS = "RimMandrake.FeverWood."
FAILS = []

# behaviours the C# must carry: (file, label, regex)
BEHAVIOURS = [
    ("RM_CompCapturedSpecimen.cs", "foreign display tank skips feeding/neglect/products (tick asks the kernel)",
     r"RM_TankKernel\.RunsThisTick\(RM_FeverWoodSettings\.sekkulaathTankEnabled, occupied, IsForeignDisplay"),
    ("RM_TankKernel.cs", "foreign display tank skips feeding/neglect/products (kernel rule)",
     r"if \(!tankEnabled \|\| !occupied \|\| foreignDisplay\) return false;"),
    ("RM_CompCapturedSpecimen.cs", "a breach of a foreign display tank frees (not manhunter-escapes) the young",
     r"private void Escape\(string cause\)\s*\{\s*if \(RM_TankKernel\.EscapeFreesDisplayYoung\(IsForeignDisplay, RM_FeverWoodSettings\.broodRansomEnabled\)\)\s*\{\s*FreeDisplayYoung"),
    ("RM_TankKernel.cs", "a breach of a foreign display tank frees the young (kernel rule)",
     r"EscapeFreesDisplayYoung\(bool foreignDisplay, bool ransomOn\) \{ return foreignDisplay && ransomOn; \}"),
    ("RM_CompCapturedSpecimen.cs", "a kill outright still frees the young",
     r"DestroyFreesDisplayYoung\(mode == DestroyMode\.KillFinalize, occupied, Props\.displayTank"),
    ("RM_TankKernel.cs", "a kill outright still frees the young (kernel rule)",
     r"return killFinalize && occupied && displayProps"),
    ("RM_CompCapturedSpecimen.cs", "freeing is idempotent (empty tank does nothing)",
     r"public Pawn FreeDisplayYoung\([^)]*\)\s*\{\s*if \(!RM_TankKernel\.TryFreeDisplay\(ref occupied, map != null\)"),
    ("RM_TankKernel.cs", "freeing is idempotent (kernel rule)",
     r"if \(!occupied \|\| !spawned\) return false;"),
    ("RM_CompCapturedSpecimen.cs", "the freed young carries the tank's gift rolls",
     r"Notify_ReleasedToDeep\(Props\.giftRolls\)"),
    ("RM_CompCapturedSpecimen.cs", "goodwill loss comes from Mod Settings",
     r"TryAffectGoodwillWith\(Faction\.OfPlayer, -loss"),
    ("RM_CompCapturedSpecimen.cs", "the settlement is told its tank was freed",
     r"Notify_DisplayTankFreed\(settlement\)"),
    ("RM_CompEscapedCaptive.cs", "gift rolls are scribed on the young", r'Scribe_Values\.Look\(ref giftRolls, "giftRolls", 1\)'),
    ("RM_CompEscapedCaptive.cs", "gift rolls reach the scheduled gift", r"ScheduleDeepGift\(water, giftRolls\)"),
    ("RM_MapComponent_TentacleWatch.cs", "pending gift rolls are scribed", r'"pendingGiftRolls"'),
    ("RM_MapComponent_TentacleWatch.cs", "a pending gift grants its rolls", r"RM_DeepGift\.Grant\(map, due\[i\]\.Key, due\[i\]\.Value\)"),
    ("RM_BroodRansom.cs", "freed tanks are scribed", r'"freedDisplayTanks"'),
    ("RM_BroodRansom.cs", "the gen step never rebuilds a freed tank", r"DisplayTankFreed\(settlement\) == true\)\)\s*\{\s*return;"),
    ("RM_BroodKernel.cs", "the gen step never rebuilds a freed tank (kernel rule)", r"applies && !alreadyFreed;"),
    ("RM_BroodRansom.cs", "the gen step is gated on the brood ransom and the tank",
     r"PlaceDisplayTank\(RM_FeverWoodSettings\.broodRansomEnabled, RM_FeverWoodSettings\.sekkulaathTankEnabled,\s*tankDef != null"),
    ("RM_BroodKernel.cs", "the gen step is gated on the brood ransom and the tank (kernel rule)",
     r"return ransomOn && tankOn && hasTankDef && applies"),
    ("RM_BroodRansom.cs", "the stock generator honours onlyFactions",
     r"StocksCask\(RM_FeverWoodSettings\.broodRansomEnabled, StocksFor\(faction\)\)"),
    ("RM_BroodKernel.cs", "the stock generator honours onlyFactions (kernel rule)", r"StocksCask\(bool ransomOn, bool stocksFor\) \{ return ransomOn && stocksFor; \}"),
    ("RM_BroodRansom.cs", "the keeper extension counts only named settlements", r"onlySettlementNames\.Contains\(settlement\.Name\)"),
    ("RM_FeverWoodMod.cs", "the goodwill loss setting is saved",
     r'Scribe_Values\.Look\(ref broodDisplayTankGoodwillLoss, "broodDisplayTankGoodwillLoss", 50\)'),
    ("RM_FeverWoodMod.cs", "the goodwill loss setting has a slider", r"broodDisplayTankGoodwillLoss = Mathf\.RoundToInt\(list\.Slider"),
]


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def _src(root):
    out = {}
    for d in (os.path.join(root, "Source"), os.path.join(root, "Source", "Kernel")):
        for f in os.listdir(d) if os.path.isdir(d) else []:
            if f.endswith(".cs"):
                with open(os.path.join(d, f), encoding="utf-8") as fh:
                    out[f] = fh.read()
    return out


def _public_fields(src_all, cls):
    """Public instance fields of `cls`, plus inherited ones this patch relies on (StockGenerator.price, CompProperties)."""
    m = re.search(r"public class %s\b[^{]*\{" % re.escape(cls), src_all)
    if not m:
        return None
    depth, i = 1, m.end()
    while depth and i < len(src_all):
        depth += {"{": 1, "}": -1}.get(src_all[i], 0)
        i += 1
    body = src_all[m.end():i]
    names = set(re.findall(r"^\s*public (?!static|const|override|abstract|class)[\w<>\[\], .]+? (\w+)\s*(?:=|;)", body, re.M))
    names.add("price")  # inherited from RimWorld.StockGenerator (decompiled 1.6: `public PriceType price`)
    return names


def problems(fw_root=HERE, campaign=CAMPAIGN, faction_xml=FACTION_XML, settlements_csv=SETTLEMENTS_CSV):
    bad = []
    src = _src(fw_root)
    src_all = "\n".join(src.values())
    root = ET.parse(campaign).getroot()

    # every Class in our namespace exists, and every child it sets is a public field
    for el in root.iter():
        cls = el.get("Class", "")
        if not cls.startswith(NS):
            continue
        short = cls[len(NS):]
        fields = _public_fields(src_all, short)
        if fields is None:
            bad.append("class %s not in Source" % short)
            continue
        for child in el:
            if child.tag not in fields:
                bad.append("%s has no public field %s" % (short, child.tag))

    defs_text = ""
    for dp, _, fs in os.walk(os.path.join(fw_root, "Defs")):
        for f in fs:
            if f.endswith(".xml"):
                with open(os.path.join(dp, f), encoding="utf-8") as fh:
                    defs_text += fh.read()

    tank = next((t for t in root.iter("ThingDef") if t.findtext("defName") == "RUT_SporefallDisplayTank"), None)
    if tank is None:
        bad.append("RUT_SporefallDisplayTank not added")
    else:
        if 'Name="%s"' % tank.get("ParentName") not in defs_text:
            bad.append("display tank ParentName %s not in Fever Wood defs" % tank.get("ParentName"))
        comp = next((li for li in tank.iter("li") if li.get("Class", "").endswith("RM_CompProperties_CapturedSpecimen")), None)
        if comp is None or comp.findtext("displayTank") != "true":
            bad.append("display tank comp not flagged displayTank")
        elif int(comp.findtext("giftRolls") or "1") < 2:
            bad.append("Sporefall's young does not buy the doubled gift")
        like = comp.findtext("occupantLikeTank") if comp is not None else None
        if like and "<defName>%s</defName>" % like not in defs_text:
            bad.append("occupantLikeTank %s not a Fever Wood def" % like)
        if tank.find("designationCategory") is None or tank.find("designationCategory").get("IsNull") != "True":
            bad.append("display tank is buildable (designationCategory not nulled)")

    gen = next((g for g in root.iter("GenStepDef") if g.findtext("defName") == "RUT_SporefallDisplayTank"), None)
    added = [li.text for op in root.iter("li") if op.get("Class") == "PatchOperationAdd"
             and "MapGeneratorDef" in (op.findtext("xpath") or "") for li in op.iter("li")]
    if gen is None:
        bad.append("GenStepDef missing")
    else:
        g = gen.find("genStep")
        if g.findtext("tankDef") != "RUT_SporefallDisplayTank":
            bad.append("gen step places %s" % g.findtext("tankDef"))
        if "RUT_SporefallDisplayTank" not in added:
            bad.append("gen step not added to a MapGeneratorDef")
        fac = g.findtext("faction")
        town = g.findtext("settlementName")
        with open(faction_xml, encoding="utf-8") as fh:
            if "<defName>%s</defName>" % fac not in fh.read():
                bad.append("faction %s not defined" % fac)
        with open(settlements_csv, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        # the CSV records the faction by its pre-RUT_ name; match either spelling
        if not any(r["name"] == town and r["faction_def"] in (fac, fac.replace("RUT_", "", 1)) for r in rows):
            bad.append("no %s settlement named %s in the frozen world record" % (fac, town))
        if not any(r["name"] == "Sporefall" for r in rows):  # sanity probe: the reader can see the town at all
            bad.append("settlement reader blind (Sporefall absent)")

    for f, label, rx in BEHAVIOURS:
        if not re.search(rx, src.get(f, ""), re.S):
            bad.append("C#: " + label)
    return bad


def _copy(tmp):
    fw = os.path.join(tmp, "fw")
    for d in ("Defs", "Source"):
        shutil.copytree(os.path.join(HERE, d), os.path.join(fw, d), ignore=shutil.ignore_patterns("obj", "bin"))
    camp = os.path.join(tmp, "campaign.xml")
    shutil.copy(CAMPAIGN, camp)
    return fw, camp


def _sub(path, old, new):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    assert old in text, (path, old)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text.replace(old, new, 1))


def main():
    bad = problems()
    check("shipped: campaign patch and mechanism agree", bad == [], bad)
    check("sanity: %d behaviours checked" % len(BEHAVIOURS), len(BEHAVIOURS) >= 18)

    plants = [
        ("unknown field", "camp", "<giftRolls>2</giftRolls>", "<giftRollz>2</giftRollz>", "no public field giftRollz"),
        ("single gift", "camp", "<giftRolls>2</giftRolls>", "<giftRolls>1</giftRolls>", "doubled gift"),
        ("wrong town", "camp", "<settlementName>Sporefall</settlementName>", "<settlementName>Nowhere</settlementName>", "named Nowhere"),
        ("buildable", "camp", '<designationCategory IsNull="True" />', "", "buildable"),
        ("unknown class", "camp", "RimMandrake.FeverWood.RM_StockGenerator_DeepYoung", "RimMandrake.FeverWood.RM_StockGen_Nope", "not in Source"),
        ("regenerates freed", "Source/RM_BroodRansom.cs", "DisplayTankFreed(settlement) == true)", "DisplayTankFreed(settlement) == false)", "never rebuilds"),
        ("neglect escapes", "Source/Kernel/RM_TankKernel.cs", "if (!tankEnabled || !occupied || foreignDisplay) return false;", "if (!tankEnabled || !occupied) return false;", "skips feeding"),
        ("escape manhunters a display tank", "Source/Kernel/RM_TankKernel.cs", "{ return foreignDisplay && ransomOn; }", "{ return false; }", "frees the young (kernel rule)"),
        ("kill leaves young", "Source/Kernel/RM_TankKernel.cs", "return killFinalize && occupied && displayProps", "return false && occupied && displayProps", "kill outright"),
        ("gen ignores freed", "Source/Kernel/RM_BroodKernel.cs", "applies && !alreadyFreed;", "applies;", "never rebuilds"),
        ("cask ignores faction list", "Source/Kernel/RM_BroodKernel.cs", "{ return ransomOn && stocksFor; }", "{ return ransomOn; }", "honours onlyFactions"),
        ("rolls dropped on save", "Source/RM_MapComponent_TentacleWatch.cs", '"pendingGiftRolls"', '"pendingGiftRollz"', "pending gift rolls"),
    ]
    for label, where, old, new, expect in plants:
        tmp = tempfile.mkdtemp()
        try:
            fw, camp = _copy(tmp)
            _sub(camp if where == "camp" else os.path.join(fw, where), old, new)
            got = problems(fw_root=fw, campaign=camp)
            check("planted %s reddens" % label, any(expect in g for g in got), got)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
