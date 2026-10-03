"""validation.py -- modcheck suite for RimMandrake Abyss (mandrake.rm.abyss).

First script for this mod (debug_process.md). Covers ABYSS_ETCHCAP_BUILD_1 and ABYSS_GHARREK_BUILD_1.
Two layers: `static_check()` is offline (parses the shipped XML, runs with plain
`python3 validation.py`); the chain is a live def-resolution read, NEVER RUN YET.
Mod Settings: the Abyss's only control is the worldgen-rarity slider; the etchcap carries no
toggle (it is a def, and gating a def needs C# plus a DLL rebuild -- owed, see the item).
"""
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))


def _defs(rel):
    return ET.parse(os.path.join(HERE, "Defs", rel)).getroot()


def static_check():
    """Returns a list of failure strings; empty means every etchcap link resolves on disk."""
    bad = []
    plant = next((d for d in _defs("ThingDefs_Plants/RM_Etchcap.xml").iter("ThingDef")
                  if d.findtext("defName") == "RM_Etchcap"), None)
    cap = next((d for d in _defs("ThingDefs_Items/RM_EtchcapCap.xml").iter("ThingDef")
                if d.findtext("defName") == "RM_EtchcapCap"), None)
    ter = next((d for d in _defs("TerrainDefs/RM_EtchHollow.xml").iter("TerrainDef")
                if d.findtext("defName") == "RM_EtchHollow"), None)
    if plant is None or cap is None or ter is None:
        return ["missing def: plant=%s cap=%s terrain=%s" % (plant is not None, cap is not None, ter is not None)]
    p = plant.find("plant")
    if p.findtext("harvestedThingDef") != cap.findtext("defName"):
        bad.append("plant does not harvest RM_EtchcapCap")
    # growth restriction: plant minimum above any ordinary ground, met only by the hollow
    fmin = float(p.findtext("fertilityMin"))
    if not (fmin >= 0.8 and float(ter.findtext("fertility")) >= fmin):
        bad.append("fertility gate broken: plant fertilityMin %s vs hollow %s" % (fmin, ter.findtext("fertility")))
    if float(p.findtext("growMinGlow")) != 0:
        bad.append("etchcap must not need light (growMinGlow != 0)")
    if cap.find("ingestible/foodType") is None or cap.find("ingredient") is None:
        bad.append("cap is not a food ingredient")
    # wiring in the biome, shorthand form
    biome = _defs("BiomeDefs/RM_Abyss.xml")
    wp = biome.find(".//wildPlants/RM_Etchcap")
    if wp is None or not float(wp.text) > 0:
        bad.append("RM_Abyss <wildPlants> lacks <RM_Etchcap>commonality</RM_Etchcap>")
    # textures resolve
    for d, ext in ((plant, "Things/Plant/Etchcap"), (cap, "Things/Item/EtchcapCap")):
        tp = d.findtext("graphicData/texPath")
        if tp != "RM_Abyss/" + ext or not os.path.isfile(os.path.join(HERE, "Textures", tp + ".png")):
            bad.append("texture missing for %s: %s" % (d.findtext("defName"), tp))
    if not os.path.isfile(os.path.join(HERE, "Textures", ter.findtext("texturePath") + ".png")):
        bad.append("terrain texture missing")
    return bad


def gharrek_check():
    """Offline: gharrek defs, art, gill-ash, comp wiring, roster row, csproj. Returns failures."""
    bad = []
    root = _defs("ThingDefs_Races/RM_Gharrek.xml")
    thing = next((d for d in root.iter("ThingDef") if d.findtext("defName") == "RM_Gharrek"), None)
    kind = next((d for d in root.iter("PawnKindDef") if d.findtext("defName") == "RM_Gharrek"), None)
    hed = next((d for d in root.iter("HediffDef") if d.findtext("defName") == "RM_GharrekDormant"), None)
    ash = next((d for d in _defs("ThingDefs_Items/RM_GillAsh.xml").iter("ThingDef")
                if d.findtext("defName") == "RM_GillAsh"), None)
    if None in (thing, kind, hed, ash):
        return ["missing def: thing=%s kind=%s hediff=%s ash=%s" % (thing is not None, kind is not None, hed is not None, ash is not None)]
    if kind.findtext("race") != "RM_Gharrek":
        bad.append("PawnKind race != RM_Gharrek")
    if thing.find("statBases/MaxFlightTime") is not None:
        bad.append("gharrek must not fly (spec: crawler)")
    comp = thing.find("comps/li[@Class='RimMandrake.Abyss.CompProperties_Gharrek']")
    if comp is None or comp.findtext("dormantHediff") != "RM_GharrekDormant":
        bad.append("gust comp missing or not pointed at RM_GharrekDormant")
    sh = thing.find("comps/li[@Class='CompProperties_Shearable']")
    if sh is None or sh.findtext("woolDef") != "RM_GillAsh":
        bad.append("gill-ash shearable comp missing")
    if hed.find("stages/li/capMods/li/setMax") is None:
        bad.append("dormant hediff does not cap movement")
    # roster: shorthand element form, ~0.6, and one home only
    biome = _defs("BiomeDefs/RM_Abyss.xml")
    wa = biome.find(".//wildAnimals/RM_Gharrek")
    if wa is None or abs(float(wa.text) - 0.6) > 1e-6:
        bad.append("RM_Abyss <wildAnimals> lacks <RM_Gharrek>0.6</RM_Gharrek>")
    if not float(biome.findtext(".//animalDensity")) > 0:
        bad.append("RM_Abyss animalDensity is 0: roster is dead content")
    # art: 3 facings of the pawn, one single for the item
    for tex in {l.findtext("bodyGraphicData/texPath") for l in kind.iter("li") if l.find("bodyGraphicData") is not None}:
        for f in ("south", "east", "north"):
            if not os.path.isfile(os.path.join(HERE, "Textures", "%s_%s.png" % (tex, f))):
                bad.append("missing facing %s_%s.png" % (tex, f))
    if not os.path.isfile(os.path.join(HERE, "Textures", ash.findtext("graphicData/texPath") + ".png")):
        bad.append("gill-ash texture missing")
    # C# sources are compiled (EnableDefaultCompileItems false => unlisted file compiles into nothing)
    proj = open(os.path.join(HERE, "Source", "RM_Abyss.csproj")).read()
    for cs in ("RM_GustController.cs", "RM_CompGharrek.cs"):
        if 'Compile Include="%s"' % cs not in proj:
            bad.append("%s not in csproj" % cs)
        elif not os.path.isfile(os.path.join(HERE, "Source", cs)):
            bad.append("%s missing on disk" % cs)
    return bad


try:
    from modcheck import Suite, ExpectationFailed
    suite = Suite("Abyss")
    suite.toggles = []

    @suite.chain("etchcap_defs_resolve")
    def etchcap_defs_resolve(t):
        """Live: the three defs loaded (a def with an unresolvable field is silently discarded)."""
        with t.component("etchcap_defs_loaded", beyond_toggle=True):
            for d in ("ThingDef/RM_Etchcap", "ThingDef/RM_EtchcapCap", "TerrainDef/RM_EtchHollow"):
                r = t.bridge_call("jawa/get_defs", defs=d)
                if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                    raise ExpectationFailed("def did not load: %s -> %r" % (d, r))
            t.screenshot()

    @suite.chain("gharrek_defs_resolve")
    def gharrek_defs_resolve(t):
        """Live: the gharrek defs loaded and the biome rosters it."""
        with t.component("gharrek_defs_loaded", beyond_toggle=True):
            for d in ("ThingDef/RM_Gharrek", "PawnKindDef/RM_Gharrek", "ThingDef/RM_GillAsh", "HediffDef/RM_GharrekDormant"):
                r = t.bridge_call("jawa/get_defs", defs=d)
                if t._guard() and (not r or not r.get("success") or r.get("foundCount") != 1):
                    raise ExpectationFailed("def did not load: %s -> %r" % (d, r))
except ImportError:
    suite = None

if __name__ == "__main__":
    f = static_check()
    print("ETCHCAP static: %s" % ("PASS" if not f else "FAIL " + "; ".join(f)))
    g = gharrek_check()
    print("GHARREK static: %s" % ("PASS" if not g else "FAIL " + "; ".join(g)))
    sys.exit(1 if (f or g) else 0)
