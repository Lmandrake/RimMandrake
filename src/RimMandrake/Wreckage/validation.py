"""validation.py -- first script for RimMandrake: Wreckage (mandrake.rm.wreckage), composed into
mandrake.rm.biomes as an engine entry.

SALVAGE_WRECKAGE_EVERYWHERE_1, slice 1: the loot half of design step 1
(design/RimMandrake/salvage_wreckage_everywhere_design_2026-10-02.md §3c, §6). Walk:
design/validation_walks/RimMandrake/Wreckage.md. Run:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run Wreckage

Offline: `python3 src/RimMandrake/Wreckage/validation.py` runs static_checks() only.
Not proven here: the drop itself (no bridge verb deconstructs with a pawn yet; the walk says so).
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

from modcheck import Suite, ExpectationFailed

HERE = os.path.dirname(os.path.abspath(__file__))
SCALD = os.path.join(HERE, "..", "TerminalBiomes", "Defs", "ThingDefs_Buildings", "RUT_ScaldWrecks.xml")
suite = Suite("Wreckage")
suite.toggles = ["salvageLoot", "lootGenerosity", "skillScalesRare"]

TIERS = ("Scrap", "Hull", "Tank", "Carapace", "Sealed")
RARE_TIERS = ("Hull", "Tank", "Carapace", "Sealed")
TABLES = ["RM_SalvageLoot_%s" % t for t in TIERS] + ["RM_SalvageLoot_%s_Rare" % t for t in RARE_TIERS]
SCALD_WRECKS = {"RUT_ScaldWreckHull": "Hull", "RUT_ScaldWreckTank": "Tank", "RUT_ScaldWreckFrame": "Scrap"}
COMP_CLASS = "RimMandrake.Wreckage.RM_CompProperties_SalvageLoot"
NEEDLES = ("mandrake.rm.wreckage", "RimMandrake.Wreckage", "RM_SalvageLoot", "RM_CompSalvageLoot")


@suite.chain("load")
def load(t):
    with t.component("no_errors_naming_this_mod", beyond_toggle=True):
        r = t.bridge_call("jawa/drain_log", limit=400, errorsOnly=True)
        if t._guard():
            if not isinstance(r, dict) or r.get("success") is False:
                raise ExpectationFailed("UNMEASURED: drain_log did not answer")
            msgs = [m.get("text", "") for m in (r.get("messages") or [])]
            hits = [m[:160] for m in msgs if any(n in m for n in NEEDLES)]
            if hits:
                raise ExpectationFailed("errors name this mod: %r" % hits[:4])


def _get_defs(t, want):
    r = t.bridge_call("jawa/get_defs", defs=";".join(want), fields="defName")
    if not isinstance(r, dict) or not r.get("success"):
        raise ExpectationFailed("UNMEASURED: get_defs failed: %r" % (r,))
    if r.get("notFound"):
        raise ExpectationFailed("defs missing: %r" % r.get("notFound"))


@suite.chain("defs")
def defs(t):
    with t.component("loot_tables_resolve", beyond_toggle=True):
        if t._guard():
            _get_defs(t, ["ThingSetMakerDef/%s" % d for d in TABLES])
    with t.component("scald_wrecks_resolve", beyond_toggle=True):
        if t._guard():
            # A ThingDef whose comp Class cannot resolve is discarded whole, so presence is the check.
            _get_defs(t, ["ThingDef/%s" % d for d in SCALD_WRECKS])


def static_checks():
    """Offline, no game. Returns failure strings; empty means pass."""
    bad = []
    root = ET.parse(os.path.join(HERE, "Defs", "ThingSetMakerDefs", "RM_SalvageLoot.xml")).getroot()
    got = [e.findtext("defName") for e in root if e.tag == "ThingSetMakerDef"]
    if sorted(got) != sorted(TABLES):
        bad.append("loot tables parsed %s, want %s" % (sorted(got), sorted(TABLES)))
    for e in root:
        if e.tag != "ThingSetMakerDef":
            continue
        opts = e.findall("root/options/li")
        if not opts:
            bad.append("%s has no options" % e.findtext("defName"))
        for li in opts:
            if not li.findall("thingSetMaker/fixedParams/filter/thingDefs/li"):
                bad.append("%s option has no thingDefs" % e.findtext("defName"))
    if not os.path.isfile(SCALD):
        bad.append("Scald wrecks file missing: %s" % SCALD)
    else:
        sroot = ET.parse(SCALD).getroot()
        seen = {}
        for e in sroot:
            dn = e.findtext("defName")
            if dn not in SCALD_WRECKS:
                continue
            comps = [li for li in e.findall("comps/li") if li.get("Class") == COMP_CLASS]
            if len(comps) != 1:
                bad.append("%s carries %d salvage-loot comps (want 1)" % (dn, len(comps)))
                continue
            tier = comps[0].findtext("lootTier")
            rare = float(comps[0].findtext("rareChance") or "0.05")
            seen[dn] = tier
            if tier != SCALD_WRECKS[dn]:
                bad.append("%s tier %s, want %s" % (dn, tier, SCALD_WRECKS[dn]))
            if "RM_SalvageLoot_%s" % tier not in got:
                bad.append("%s names tier %s with no table" % (dn, tier))
            if rare > 0 and "RM_SalvageLoot_%s_Rare" % tier not in got:
                bad.append("%s has rareChance %s but no %s_Rare table" % (dn, rare, tier))
            if e.findtext("comps") is not None and e.find("comps").get("Inherit") == "False":
                bad.append("%s drops ShipChunkBase's inherited comps" % dn)
        if set(seen) != set(SCALD_WRECKS):
            bad.append("Scald wrecks wired: %s, want %s" % (sorted(seen), sorted(SCALD_WRECKS)))
    src_dir = os.path.join(HERE, "Source")
    proj = open(os.path.join(src_dir, "RM_Wreckage.csproj"), encoding="utf-8").read()
    for f in os.listdir(src_dir):
        if f.endswith(".cs") and ('Compile Include="%s"' % f) not in proj:
            bad.append("%s is not in the csproj (compiles into nothing)" % f)
    mod = open(os.path.join(src_dir, "RM_WreckageMod.cs"), encoding="utf-8").read()
    for f in suite.toggles:
        if not re.search(r'Scribe_Values\.Look\(ref %s, "%s"' % (f, f), mod):
            bad.append("toggle %s is not Scribed" % f)
    keyed = open(os.path.join(HERE, "Languages", "English", "Keyed", "RM_Wreckage.xml"), encoding="utf-8").read()
    used = set()
    for f in os.listdir(src_dir):
        if f.endswith(".cs"):
            used |= set(re.findall(r'"(RM_Wreckage_[A-Za-z_]+)"', open(os.path.join(src_dir, f), encoding="utf-8").read()))
    used |= {"RM_Wreckage_Tier_%s" % t for t in TIERS}
    for k in sorted(used):
        if "<%s>" % k not in keyed and not k.endswith("_"):
            bad.append("keyed string %s missing" % k)
    asm = os.path.join(HERE, "Assemblies", "RimMandrake.Wreckage.dll")
    if not os.path.isfile(asm):
        bad.append("no DLL at %s" % asm)
    return bad


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)
