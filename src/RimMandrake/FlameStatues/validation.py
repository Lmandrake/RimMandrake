"""validation.py -- first script for Mandrake Flame Statues (mandrake.rm.flamestatues).

FLAME_STATUES_MOD_BUILD_1, statue_mods_spec.md §3 step 4 (skeleton: three fuelled sculptures, one vanilla
flame each, Chemfuel only). Run:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run FlameStatues

Environment: minimal + every DLC + this mod. No toggles yet: Mod Settings (§2.4) arrive with the C# flame-point
comp at step 5. Not proven here: the flame drawing and the glow going dark without fuel (first poke: spawn a
colossus, refuel it, screenshot, then empty it).
"""
import os
import sys
import xml.etree.ElementTree as ET

from modcheck import Suite, ExpectationFailed, shipped_defs

HERE = os.path.dirname(os.path.abspath(__file__))
suite = Suite("FlameStatues")
suite.toggles = []

STATUES = ("RM_FlameStatue_Ember", "RM_FlameStatue_Dancer", "RM_FlameStatue_Colossus")
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
        cats = [li.text for li in b.findall("stuffCategories/li")]
        if sorted(cats) != ["Metallic", "Stony"]:
            bad.append("stuff must be Stony+Metallic, no Woody (spec §2.1): %s" % cats)
    for dn, e in got.items():
        fuel = [li.text for li in e.findall(".//li[@Class='CompProperties_Refuelable']/fuelFilter/thingDefs/li")]
        if fuel != ["Chemfuel"]:
            bad.append("%s fuel must be Chemfuel only (ruling R4): %s" % (dn, fuel))
        if len(e.findall(".//li[@Class='CompProperties_FireOverlay']")) != 1:
            bad.append("%s must carry exactly one vanilla fire overlay (Graphic_Flicker reads only the first)" % dn)
        if e.find(".//li[@Class='CompProperties_Glower']") is None:
            bad.append("%s has no glower" % dn)
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
                       fields_by_type={"ThingDef": ("label", "fillPercent", "costStuffCount", "tickerType", "size")},
                       sanity=("RM_FlameStatue_Colossus",), min_count=3)
