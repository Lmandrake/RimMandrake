"""validation.py -- modcheck suite for RimMandrake Abyss (mandrake.rm.abyss).

First script for this mod (debug_process.md). Today it covers ABYSS_ETCHCAP_BUILD_1 only.
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
except ImportError:
    suite = None

if __name__ == "__main__":
    f = static_check()
    print("ETCHCAP static: %s" % ("PASS" if not f else "FAIL " + "; ".join(f)))
    sys.exit(1 if f else 0)
