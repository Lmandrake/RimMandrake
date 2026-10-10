"""validation.py -- first script for Mandrake Flame Statues (mandrake.rm.flamestatues).

FLAME_STATUES_MOD_BUILD_1, statue_mods_spec.md §3 step 4 + step 5 (three fuelled sculptures, a set of
flames each via RM_CompFlamePoints, Chemfuel only). Run:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run FlameStatues

Environment: minimal + every DLC + this mod. Toggles are Mod Settings §2.4 (RM_CompFlamePoints, step 5).
Not proven here: the flame drawing and the glow going dark without fuel (first poke: spawn a
colossus, refuel it, screenshot, then empty it). Also not proven: the Helixien link (step 7,
Patches/Helixien_Pipenet.xml + RM_CompFlamePoints.PipeReceiving) -- poke: pipe a fuelled statue to a
Helixien tank, step 2500 ticks, the chemfuel tank must not fall; cut the pipe, it must fall.
"""
import os
import sys
import xml.etree.ElementTree as ET

from modcheck import Suite, ExpectationFailed, shipped_defs

HERE = os.path.dirname(os.path.abspath(__file__))
suite = Suite("FlameStatues")
suite.toggles = ["flamePoints", "flecks", "consumeFuel", "qualityScaling", "glow", "helixienLink"]

STATUES = ("RM_FlameStatue_Ember", "RM_FlameStatue_Dancer", "RM_FlameStatue_Colossus")
POINTS = {"RM_FlameStatue_Ember": 1, "RM_FlameStatue_Dancer": 3, "RM_FlameStatue_Colossus": 5}
NEEDLES = ("mandrake.rm.flamestatues", "RM_FlameStatue", "FlameStatues")
TEX = os.path.join(HERE, "Textures", "Things", "Building", "Art", "RM_FlameStatues", "RM_FlameStatue_Placeholder.png")


@suite.chain("load_clean")
def load_clean(t):
    with t.component("no_errors_naming_this_mod", beyond_toggle=True):
        r = t.bridge_call("jawa/drain_log", limit=400, errorsOnly=True)
        if t._guard():
            msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
            hits = [m[:160] for m in msgs if any(n in m for n in NEEDLES)]
            if hits:
                raise ExpectationFailed("errors name this mod: %r" % hits[:4])


@suite.chain("defs")
def defs(t):
    with t.component("all_defs_resolve", beyond_toggle=True):
        want = ["ThingDef/%s" % d for d in STATUES] + ["RecipeDef/Make_%s" % d for d in STATUES]
        r = t.bridge_call("jawa/get_defs", defs=";".join(want), fields="defName")
        if t._guard():
            if not (r or {}).get("success"):
                raise ExpectationFailed("get_defs failed: %r" % r)
            if r.get("notFound"):
                raise ExpectationFailed("defs missing: %r" % r.get("notFound"))


def static_checks():
    """Offline, no game. Returns failure strings; empty means pass."""
    bad = []
    root = ET.parse(os.path.join(HERE, "Defs", "ThingDefs_Buildings", "RM_FlameStatues.xml")).getroot()
    base = [e for e in root if e.tag == "ThingDef" and e.get("Name") == "RM_FlameStatueBase"]
    got = {e.findtext("defName"): e for e in root if e.tag == "ThingDef" and e.findtext("defName")}
    if set(got) != set(STATUES):
        bad.append("statues parsed %s, want %s" % (sorted(got), sorted(STATUES)))
    if not base:
        bad.append("RM_FlameStatueBase abstract missing")
    else:
        b = base[0]
        if b.get("ParentName") != "SculptureBase":
            bad.append("base must inherit SculptureBase (carving, art comp, quality)")
        if b.findtext("tickerType") != "Normal":
            bad.append("base tickerType must be Normal or CompRefuelable never burns fuel")
        if b.findtext("drawerType") != "MapMeshAndRealTime":
            bad.append("base drawerType must be MapMeshAndRealTime or comp PostDraw (the flames) never runs")
        cats = [li.text for li in b.findall("stuffCategories/li")]
        if sorted(cats) != ["Metallic", "Stony"]:
            bad.append("stuff must be Stony+Metallic, no Woody (spec §2.1): %s" % cats)
    for dn, e in got.items():
        fuel = [li.text for li in e.findall(".//li[@Class='CompProperties_Refuelable']/fuelFilter/thingDefs/li")]
        if fuel != ["Chemfuel"]:
            bad.append("%s fuel must be Chemfuel only (ruling R4): %s" % (dn, fuel))
        if e.findall(".//li[@Class='CompProperties_FireOverlay']"):
            bad.append("%s carries a vanilla fire overlay; flames come from RM_CompFlamePoints only" % dn)
        npts = len(e.findall(".//li[@Class='RimMandrake.FlameStatues.RM_CompProperties_FlamePoints']/points/li"))
        if npts != POINTS[dn]:
            bad.append("%s has %d flame points, spec §2.1 says %d" % (dn, npts, POINTS[dn]))
        if e.find(".//li[@Class='CompProperties_Glower']") is None:
            bad.append("%s has no glower" % dn)
    src = open(os.path.join(HERE, "Source", "RimMandrake.FlameStatues.csproj"), encoding="utf-8").read()
    for f in os.listdir(os.path.join(HERE, "Source")):
        if f.endswith(".cs") and ('Compile Include="%s"' % f) not in src:
            bad.append("%s is not in the csproj (compiles into nothing)" % f)
    mod = open(os.path.join(HERE, "Source", "FlameStatuesMod.cs"), encoding="utf-8").read()
    for f in suite.toggles:
        if '"%s"' % f not in mod:
            bad.append("toggle %s is not Scribed" % f)
    asm = os.path.join(HERE, "Assemblies")
    if not os.path.isdir(asm) or not any(f.endswith(".dll") for f in os.listdir(asm)):
        bad.append("no DLL in Assemblies")
    if not os.path.isfile(TEX):
        bad.append("placeholder texture missing: %s" % TEX)
    return bad


if __name__ == "__main__":
    problems = static_checks()
    print("STATIC: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    sys.exit(1 if problems else 0)


shipped_defs.add_chain(suite, __file__,
                       fields_by_type={"ThingDef": ("label", "fillPercent", "costStuffCount", "tickerType")},   # size: jawa/get_defs answers "(no such field)" for ThingDef.size (a struct), MEASURED live 2026-10-04

                       sanity=("RM_FlameStatue_Colossus",), min_count=3)
