"""validation.py -- first script for RimMandrake: Wreckage (mandrake.rm.wreckage), composed into
mandrake.rm.biomes as an engine entry.

SALVAGE_WRECKAGE_EVERYWHERE_1, slice 1: the loot half of design step 1;
slice 2: the family parents and the weathering row, the Scald reparented as the template
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
EXT_CLASS = "RimMandrake.Wreckage.RM_WreckWeathering"
WDEF_TAG = "RimMandrake.Wreckage.RM_WreckWeatheringDef"
FAMILIES_XML = os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RM_WreckFamilies.xml")
WEATHER_XML = os.path.join(HERE, "Defs", "RM_WreckWeatheringDefs", "RM_WreckWeatherings.xml")
FAMILY_NAMES = ["RM_WreckFamily_%s" % f for f in ("Hull", "Tank", "Frame", "Speeder", "Carapace", "Tread")]
# What the Scald shipped before slice 2 reparented it (96f8113e9): costList and deconstruct fraction.
SCALD_SHIPPED = {
    "RUT_ScaldWreckHull": ({"Steel": 30, "ComponentIndustrial": 1}, 0.75),
    "RUT_ScaldWreckTank": ({"Steel": 20, "GravlitePanel": 5}, 0.75),
    "RUT_ScaldWreckFrame": ({"Steel": 15}, 0.75),
}
NEEDLES = ("mandrake.rm.wreckage", "RimMandrake.Wreckage", "RM_SalvageLoot", "RM_CompSalvageLoot",
           "RM_WreckFamily", "RM_WreckWeathering")


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


def _shift(tier, shift):
    """Mirror of RM_WreckWeathering.ShiftTier (C#)."""
    rank = 0 if tier == "Scrap" else 2 if tier == "Sealed" else 1
    to = max(0, min(2, rank + shift))
    if to == rank:
        return tier
    return "Scrap" if to == 0 else "Sealed" if to == 2 else ("Hull" if rank == 0 else tier)


def _families(bad):
    """{family: (tier, rareChance, costList, fraction)} with the base's fraction inherited."""
    out = {}
    root = ET.parse(FAMILIES_XML).getroot()
    base = [e for e in root if e.get("Name") == "RM_WreckFamilyBase"]
    if len(base) != 1 or base[0].get("ParentName") != "ShipChunkBase" or base[0].get("Abstract") != "True":
        bad.append("RM_WreckFamilyBase missing, not abstract, or not on ShipChunkBase")
        return out
    b = base[0]
    if b.findtext("terrainAffordanceNeeded") != "Walkable":
        bad.append("RM_WreckFamilyBase does not set Walkable (shallows fail on inherited Light)")
    bfrac = float(b.findtext("resourcesFractionWhenDeconstructed") or "0.5")
    for e in root:
        n = e.get("Name")
        if n == "RM_WreckFamilyBase":
            continue
        if e.get("Abstract") != "True" or e.get("ParentName") != "RM_WreckFamilyBase" or e.findtext("defName"):
            bad.append("%s is not an abstract child of RM_WreckFamilyBase" % n)
            continue
        comps = [li for li in e.findall("comps/li") if li.get("Class") == COMP_CLASS]
        if len(comps) != 1:
            bad.append("%s carries %d salvage-loot comps (want 1)" % (n, len(comps)))
            continue
        if e.find("comps").get("Inherit") == "False":
            bad.append("%s drops ShipChunkBase's inherited comps" % n)
        cl = e.find("costList")
        if cl is None or cl.get("Inherit") != "False" or e.find("killedLeavings") is None \
                or e.find("killedLeavings").get("Inherit") != "False":
            bad.append("%s must set costList and killedLeavings Inherit=False (else ShipChunk's 11 components ride along)" % n)
            continue
        cost = {c.tag: int(c.text) for c in cl}
        frac = float(e.findtext("resourcesFractionWhenDeconstructed") or bfrac)
        out[n] = (comps[0].findtext("lootTier"), float(comps[0].findtext("rareChance") or "0.05"), cost, frac)
    if sorted(out) != sorted(FAMILY_NAMES):
        bad.append("families parsed %s, want %s" % (sorted(out), sorted(FAMILY_NAMES)))
    return out


def _weatherings(bad):
    """{defName: (yieldFactor, lootTierShift)}"""
    out = {}
    for e in ET.parse(WEATHER_XML).getroot():
        if e.tag != WDEF_TAG:
            bad.append("weathering file holds a <%s>" % e.tag)
            continue
        yf = float(e.findtext("yieldFactor") or "1")
        sh = int(e.findtext("lootTierShift") or "0")
        if not 0 < yf <= 1.5 or not -2 <= sh <= 2:
            bad.append("%s out of range (yieldFactor %s, shift %s)" % (e.findtext("defName"), yf, sh))
        out[e.findtext("defName")] = (yf, sh)
    if not out:
        bad.append("no weathering rows parsed")
    return out


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
    fams = _families(bad)
    weathers = _weatherings(bad)
    if not os.path.isfile(SCALD):
        bad.append("Scald wrecks file missing: %s" % SCALD)
    else:
        seen = {}
        for e in ET.parse(SCALD).getroot():
            dn = e.findtext("defName")
            if dn not in SCALD_WRECKS:
                continue
            parent = e.get("ParentName")
            if parent not in fams:
                bad.append("%s parent %s is not a wreck family" % (dn, parent))
                continue
            if [li for li in e.findall("comps/li") if li.get("Class") == COMP_CLASS]:
                bad.append("%s restates the salvage comp its family already carries (two rolls)" % dn)
            ext = [li for li in e.findall("modExtensions/li") if li.get("Class") == EXT_CLASS]
            if len(ext) != 1:
                bad.append("%s carries %d weathering extensions (want 1)" % (dn, len(ext)))
                continue
            w = ext[0].findtext("weathering")
            if w not in weathers:
                bad.append("%s names weathering %s, not defined" % (dn, w))
                continue
            for field in ("costList", "resourcesFractionWhenDeconstructed", "terrainAffordanceNeeded", "killedLeavings"):
                if e.find(field) is not None:
                    bad.append("%s restates %s; the family/weathering own it" % (dn, field))
            if not e.findtext("graphicData/texPath"):
                bad.append("%s has no texPath" % dn)
            tier, rare, cost, frac = fams[parent]
            tier = _shift(tier, weathers[w][1])
            seen[dn] = tier
            if tier != SCALD_WRECKS[dn]:
                bad.append("%s resolves to tier %s, want %s" % (dn, tier, SCALD_WRECKS[dn]))
            if "RM_SalvageLoot_%s" % tier not in got:
                bad.append("%s resolves to tier %s with no table" % (dn, tier))
            if rare > 0 and tier != "Scrap" and "RM_SalvageLoot_%s_Rare" % tier not in got:
                bad.append("%s has rareChance %s but no %s_Rare table" % (dn, rare, tier))
            eff = round(frac * weathers[w][0], 4)
            if dn in SCALD_SHIPPED and (cost, eff) != SCALD_SHIPPED[dn]:
                bad.append("%s resolves to cost %r x %s, shipped %r x %s (the reparent changed a yield)"
                           % (dn, cost, eff, SCALD_SHIPPED[dn][0], SCALD_SHIPPED[dn][1]))
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
