"""selftest_structureinjectionssw_static.py -- NORTHSTAR_PARTIAL_GAPS_FILL_1.

Runs StructureInjectionsSW/validation.py static_checks() offline against a synthetic ThingDef name set (so the
result does not move with the def capture), then proves each bar can FAIL by mutating a scratch copy of the mod:
a missing template, an unknown plan verb, a dangling extraGenSteps entry, an unresolved THING defName, a stale
KNOWN_UNRESOLVED/KNOWN_UNPLACED entry, an unplaced shipped ThingDef and a TEMPLATE_CHECKS count that disagrees with its template. No game, no bridge."""
import importlib.util
import os
import re
import shutil
import sys
import tempfile

MOD = os.path.dirname(os.path.abspath(__file__))


def load():
    spec = importlib.util.spec_from_file_location("sisw_validation", os.path.join(MOD, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    return v


def template_things(root):
    out = set()
    for f in os.listdir(os.path.join(root, "Templates")):
        for ln in open(os.path.join(root, "Templates", f), encoding="utf-8"):
            c = ln.split("\t")
            if c[0] == "THING" and len(c) > 1:
                out.add(c[1])
    return out


def main():
    v = load()
    fails = []
    things = (template_things(MOD) - set(v.KNOWN_UNRESOLVED)) | {"Steel"}
    base = v.static_checks(things=things)
    if base:
        fails.append("clean tree should pass: %r" % base)
    if len(v.DEF_PAIRS) < 17 or any(b and "ZBiome_Grasslands" in b for _, _, b in v.DEF_PAIRS):
        fails.append("DEF_PAIRS not derived from the XML: %r" % (v.DEF_PAIRS,))

    def mutated(edit, expect, things_=things):
        tmp = tempfile.mkdtemp(prefix="sisw_")
        try:
            root = os.path.join(tmp, "mod")
            shutil.copytree(MOD, root, ignore=shutil.ignore_patterns("Textures", "*.png", "__pycache__"))
            edit(root)
            got = v.static_checks(root=root, things=things_)
            if not any(re.search(expect, p) for p in got):
                fails.append("mutation expecting /%s/ not caught: %r" % (expect, got))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def append(root, rel, text):
        with open(os.path.join(root, rel), "a", encoding="utf-8") as fh:
            fh.write(text)

    def sub(root, rel, a, b):
        p = os.path.join(root, rel)
        s = open(p, encoding="utf-8").read()
        assert a in s, (rel, a)
        open(p, "w", encoding="utf-8").write(s.replace(a, b, 1))

    mutated(lambda r: os.remove(os.path.join(r, "Templates", "beast_lair.txt")), r"planFile .*beast_lair.txt does not exist")
    mutated(lambda r: append(r, "Templates/beast_lair.txt", "WOBBLE\t1\t1\n"), r"unknown plan verbs")
    mutated(lambda r: append(r, "Templates/beast_lair.txt", "THING\tRSW_NoSuchThing\t1\t1\t0\t-\n"),
            r"RSW_NoSuchThing .* resolves in no loaded mod")
    mutated(lambda r: append(r, "Templates/moisture_farm.txt", "THING\tKotOR_MoistureVaporator_big\t2\t2\t0\t-\n"),
            r"expects 6 KotOR_MoistureVaporator_big, template has 7")
    mutated(lambda r: sub(r, "Defs/TileMutatorDefs_BeastLair.xml", "<li>RSW_GenStep_BeastLair</li>",
                          "<li>RSW_GenStep_BeastLair</li><li>RSW_GenStep_Nowhere</li>"), r"RSW_GenStep_Nowhere")
    mutated(lambda r: None, r"KNOWN_UNRESOLVED QE_Sign now resolves", things_=things | {"QE_Sign"})
    mutated(lambda r: append(r, "Templates/beast_lair.txt", "THING\tRSW_BeastNest_Large\t3\t3\t0\t-\n"),
            r"KNOWN_UNPLACED RSW_BeastNest_Large is now placed", things_=things | {"RSW_BeastNest_Large"})
    mutated(lambda r: sub(r, "Defs/BeastLairs/ThingDefs_Buildings/RSW_BeastLairs_Buildings.xml",
                          "<defName>RSW_BeastNest_Large</defName>", "<defName>RSW_BeastNest_Huge</defName>"),
            r"ThingDef RSW_BeastNest_Huge ships here but no template")
    for f in fails:
        print("FAIL " + f)
    print("selftest_structureinjectionssw_static: %s" % ("FAIL" if fails else "PASS (9 checks)"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
