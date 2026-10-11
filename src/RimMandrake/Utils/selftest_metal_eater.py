#!/usr/bin/env python3
"""selftest_metal_eater.py -- offline proof for KHORRAK_STEEL_DIET_TIER_1: the steel diet moved from SWBestiary's
RSW_Khorrak to RM_Khorrak (mandrake.rm.longshade) on CreatureBehaviors' RM_CompMetalEater.

    python3 src/RimMandrake/Utils/selftest_metal_eater.py      (exit 0 = clean)

STATIC (the source is the truth, no game):
  - RM_Khorrak carries RM_CompProperties_MetalEater with the donor's numbers, and no def anywhere under src/ still names
    RSW_Khorrak or the retired RimMandrake.StarWars.SWBestiary metal-eater types / RSW_EatMetal job.
  - every class the def, the JobDef and the think-tree insert name is declared in a file the CreatureBehaviors csproj
    compiles (EnableDefaultCompileItems is off: a file missing there compiles into nothing, with no error).
  - the kernel stays Verse-free and is in the fuzz csproj; the giver, driver and patch call the kernel.
  - metalEatingEnabled is a Scribed setting drawn inside a Group whose names list it.
CHAIN (mock bridge): CreatureBehaviors' metal_eater_seeks_its_metal must PASS on a healthy RM_MetalEaterProof answer,
and a hungry eater given nothing, a fed eater still eating, a toggle that does not gate, a proof that errors and a stale
DLL with no such method must each turn it red.
"""
import importlib.util
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(os.path.dirname(HERE))
CB = os.path.join(SRC, "RimMandrake", "CreatureBehaviors")
CBS = os.path.join(CB, "Source")
for p in (HERE, os.path.join(HERE, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def read(*parts):
    return open(os.path.join(*parts), encoding="utf-8").read()


def static_checks():
    fauna = ET.parse(os.path.join(SRC, "RimMandrake", "LongShade", "Defs", "ThingDefs_Races", "RM_LongShade_Fauna.xml")).getroot()
    kh = [d for d in fauna.findall("ThingDef") if d.findtext("defName") == "RM_Khorrak"]
    check("RM_Khorrak ThingDef exists once", len(kh) == 1, len(kh))
    li = [c for c in (kh[0].find("comps") if kh else []) if c.get("Class") == "RimMandrake.CreatureBehaviors.RM_CompProperties_MetalEater"]
    check("RM_Khorrak carries RM_CompProperties_MetalEater", len(li) == 1)
    if li:
        c = li[0]
        check("eats Steel and ChunkSlagSteel", [x.text for x in c.findall("customThingToEat/li")] == ["Steel", "ChunkSlagSteel"])
        check("donor numbers kept (nutrition 1, bite 0.2, digs ChunkSlagSteel, blocks food)",
              c.findtext("nutrition") == "1" and c.findtext("percentageOfDestruction") == "0.2"
              and c.findtext("digThingIfMapEmpty") == "true" and c.findtext("thingToDigIfMapEmpty") == "ChunkSlagSteel"
              and c.findtext("blockNormalFood") == "true")

    # Nothing shipped still names the retired twin or the retired RSW types. Sanity probe: the same walk must find RM_Khorrak.
    # A USE is a def name, an element/value naming it, a Class attribute or a C# binding; history in comments is fine.
    stale, seen_rm = [], 0
    dead = re.compile(r"<defName>(RSW_Khorrak|RSW_EatMetal|RSW_MetalEaterInsert)<|<RSW_Khorrak[ >]|>RSW_Khorrak<"
                      r"|Class=\"RimMandrake\.StarWars\.SWBestiary\.\w*(MetalEater|EatMetal)\""
                      r"|RSW_BeastMechanicsDefOf\.RSW_EatMetal|class (CompProperties_MetalEater|CompMetalEater|JobGiver_EatMetal|JobDriver_EatMetal|RSW_EatKernel)\b")
    for root, _, files in os.walk(SRC):
        for f in files:
            if not f.endswith((".xml", ".cs")):
                continue
            txt = open(os.path.join(root, f), encoding="utf-8", errors="replace").read()
            seen_rm += len(re.findall(r"<defName>RM_Khorrak<|>RM_Khorrak<|<RM_Khorrak[ >]", txt))
            for m in dead.finditer(txt):
                stale.append("%s: %s" % (os.path.relpath(os.path.join(root, f), SRC), m.group(0)))
    check("sanity probe: the src walk sees RM_Khorrak", seen_rm >= 5, seen_rm)
    check("no def/type use of the retired RSW_Khorrak / RSW metal eater remains", not stale, stale[:5])

    proj = read(CBS, "RM_CreatureBehaviors.csproj")
    compiled = set(re.findall(r'<Compile Include="([^"]+)"', proj))
    declared = {}
    for f in compiled:
        path = os.path.join(CBS, *f.replace("\\", "/").split("/"))
        if os.path.exists(path):
            for m in re.finditer(r"\b(?:class|struct)\s+(\w+)", read(path)):
                declared[m.group(1)] = f
    for ty in ("RM_CompProperties_MetalEater", "RM_CompMetalEater", "RM_JobGiver_EatMetal", "RM_JobDriver_EatMetal",
               "RM_MetalEaterPatches", "RM_MetalEaterKernel", "RM_MetalEaterProof"):
        check("%s is declared in a compiled file" % ty, ty in declared)
    jobs = ET.parse(os.path.join(CB, "Defs", "JobDefs", "RM_JobDefs.xml")).getroot()
    jd = [j for j in jobs.findall("JobDef") if j.findtext("defName") == "RM_EatMetal"]
    check("JobDef RM_EatMetal drives RM_JobDriver_EatMetal",
          len(jd) == 1 and jd[0].findtext("driverClass") == "RimMandrake.CreatureBehaviors.RM_JobDriver_EatMetal")
    check("RM_JobDefOf binds RM_EatMetal", "public static JobDef RM_EatMetal;" in read(CBS, "RM_JobDefOf.cs"))
    tt = ET.parse(os.path.join(CB, "Defs", "ThinkTreeDefs", "RM_ThinkTree_MetalEater.xml")).getroot().find("ThinkTreeDef")
    check("think-tree insert at Animal_PreMain runs RM_JobGiver_EatMetal",
          tt is not None and tt.findtext("insertTag") == "Animal_PreMain"
          and [li.get("Class") for li in tt.iter("li")] == ["RimMandrake.CreatureBehaviors.RM_JobGiver_EatMetal"])

    kern = read(CBS, "RM_MetalEaterKernel.cs")
    check("kernel is Verse-free", not re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)", kern, re.M))
    check("kernel is in the fuzz csproj",
          '<Compile Include="..\\RM_MetalEaterKernel.cs" />' in read(CBS, "SelfTestFuzz", "RimMandrakeCreatureBehaviors.Fuzz.SelfTest.csproj"))
    for f, need in (("RM_JobDriver_EatMetal.cs", "RM_MetalEaterKernel.Chew("), ("RM_JobGiver_EatMetal.cs", "RM_MetalEaterKernel.Priority("),
                    ("RM_MetalEaterPatches.cs", "RM_MetalEaterKernel.BlocksNormalFood(")):
        check("%s calls %s" % (f, need), need in read(CBS, f))
    proof = read(CBS, "RM_MetalEaterProof.cs")
    check("the proof subclasses the SHIPPED giver and restores the toggle in a finally",
          "class EatProbe : RM_JobGiver_EatMetal" in proof and "RM_CreatureBehaviorsSettings.metalEatingEnabled = was;" in proof)

    mod = read(CBS, "RM_CreatureBehaviorsMod.cs")
    check("metalEatingEnabled is Scribed under its own name", 'Scribe_Values.Look(ref metalEatingEnabled, "metalEatingEnabled", true);' in mod)
    check("metalEatingEnabled is drawn inside a Group naming it",
          re.search(r'Group\(list, "Metal-eating creatures", new\[\] \{ "metalEatingEnabled" \}', mod) is not None
          and "ref metalEatingEnabled" in mod)


def load_validation():
    spec = importlib.util.spec_from_file_location("cb_validation", os.path.join(CB, "validation.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def chain_checks():
    import runner                                                  # noqa: E402
    from modcheck import Suite                                     # noqa: E402
    from northstar_driver.session import FastSession               # noqa: E402
    from northstar_driver.transport import MockGame, MockTransport  # noqa: E402
    V = load_validation()

    def make_ext(brk):
        def ext(game, tool, p):
            if tool != "jawa/static_call" or p.get("type") != V.METAL_PROOF:
                return None
            if "stale" in brk:
                return {"success": False, "message": "no public static method %s" % p.get("method")}
            if "eat_error" in brk:
                return {"success": True, "result": "ERROR no open non-home cell"}
            job = "RM_EatMetal|target=Steel|targetB=-"
            hungry = "none" if "eat_never" in brk else job
            fed = job if "eat_fed" in brk else "none"
            off = job if "eat_ungated" in brk else "none"
            return {"success": True, "result": "eater=RM_Khorrak food=Steel hungry=%s fed=%s off=%s" % (hungry, fed, off)}
        return ext

    def run(brk=()):
        suite = Suite("CreatureBehaviorsMetalEater")
        suite.chain("metal_eater_seeks_its_metal")(V.metal_eater_seeks_its_metal)
        game = MockGame()
        game.ext = make_ext(set(brk))
        s = FastSession(transport=MockTransport(game), strict=False)
        with s:
            res = runner.run_suite(suite, s, anchor=None, mod=None)
        return dict((c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"])

    EAT = "a_hungry_eater_is_sent_to_the_metal_beside_it"
    got = run()
    check("clean: PASS", got == {EAT: "PASS"}, got)
    for brk in ("eat_never", "eat_fed", "eat_ungated", "eat_error", "stale"):
        got = run((brk,))
        check("break %-12s reddens it" % brk, got == {EAT: "FAIL"}, got)
    check("metalEatingEnabled is a suite toggle", "metalEatingEnabled" in V.suite.toggles)


def main():
    static_checks()
    chain_checks()
    if FAILS:
        print("\n%d metal-eater selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall metal-eater selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
