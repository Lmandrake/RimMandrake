#!/usr/bin/env python3
"""Hose port gates, offline (design/RimMandrake/hose_port_to_flowworks_design_FINAL_2026-10-10.md §4 step 2; later steps add
rows). No game, no bridge, no dotnet. Each row has a can-fail beside it.

  P1 no defName is defined in BOTH Gimme Some Slack and FlowWorks (a cross-mod duplicate is silent: the later load wins)
  P2 Gimme Some Slack's C# names no FlowWorks hose code (GSS ends up cables/conduits/electricity only and must not depend on
     FlowWorks); the only FlowWorks mention allowed outside comments is RM_FallenWireShock's soft by-name ignition lookup
     (design §7 "soft cross-mod niceties stay soft"); no Source/Hose folder, no hose def, texture or SelfTest suite left in GSS
  P3 the essential patches (save-skip, type alias) are applied by RM_HoseEssentials, never by attribute, and the hose map
     component removes itself when the save-skip is missing (FINAL §3.9)
  P4 every moved harness script imports with Gimme Some Slack's folder absent from sys.path
  P5 save hygiene (H10b / SL2 / H11): only the FlowWorks curDriver pair is allowed, as a curDriver Class= value only
  P6 validation_style_hose.py --offline (R0) is green
  P8 (step 4) the universal pipe: RM_UniversalPipe carries RM_UniversalPipeExtension; no live def is still RM_LiquidHose;
     the old extension name survives as an [Obsolete] subclass; the def alias is the third essential patch
  P9 (step 6, widened to L7) caller coverage: each of the 22 credit sites (FINAL's 11 - pump draw x2, pour; converter in/out;
     adapter in/out; reactor A/B/product; bath - plus the tank settle, the pump's 6 hose-end credits and the dump drain, the pond return and the sprinkler draw; the
     same list as Source/SelfTest/TransferChecks.cs CreditTags) credits only inside a COMMITTED transfer, and the reflection pump adapter,
     the relay provider, the hand tint table and the two dead settings are gone
  P7 (step 3) FlowWorks loads after Gimme Some Slack (ordering) without depending on it; GSS neither depends on nor orders by FlowWorks
  P10 (review S6) no pointer to a hose file at its pre-port GSS path; every backticked src/ path in the GSS walk exists
"""
import glob
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RM = os.path.dirname(HERE)
GSS = os.path.join(RM, "GimmeSomeSlack")
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def defnames(root):
    out = {}
    for p in glob.glob(os.path.join(root, "Defs", "**", "*.xml"), recursive=True):
        for m in re.finditer(r"<defName>\s*([^<\s]+)\s*</defName>", open(p, encoding="utf-8", errors="replace").read()):
            out.setdefault(m.group(1), p)
    return out


def p1_duplicates(gss_root, fw_root):
    """P1's checker: the defNames defined in both mods' Defs trees, sorted, plus both name maps."""
    g, f = defnames(gss_root), defnames(fw_root)
    return sorted(set(g) & set(f)), g, f


def p1_planted():
    """Review S5: P1's can-fail runs the REAL checker (defnames + p1_duplicates) on two planted mod folders: one shared
    defName must be reported, and two disjoint folders must report none."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        a, b, c = (os.path.join(d, x, "Defs", "Sub") for x in ("A", "B", "C"))
        for p_, names in ((a, ["RM_Shared", "RM_OnlyA"]), (b, ["RM_Shared", "RM_OnlyB"]), (c, ["RM_OnlyC"])):
            os.makedirs(p_)
            with open(os.path.join(p_, "x.xml"), "w", encoding="utf-8") as fh:
                fh.write("<Defs>%s</Defs>" % "".join("<ThingDef><defName> %s </defName></ThingDef>" % n for n in names))
        shared = p1_duplicates(os.path.join(d, "A"), os.path.join(d, "B"))[0]
        none = p1_duplicates(os.path.join(d, "A"), os.path.join(d, "C"))[0]
    return shared, none


# P9: every hose credit site, mirroring Source/SelfTest/TransferChecks.cs CreditTags (24: L7's 19 + pond return + sprinkler draw + levelling + pump overflow spill + gravity overflow). Each tag must appear exactly
# once, in its file, on a line that makes a credit call, inside the block of a committed transfer (an `RM_LiquidTransfer.Move(`
# a few lines above; the pre-L1 Try*Liquid guard is still accepted).
CREDIT_SITES = [
    ("LiquidTypes/Building_LiquidPump.cs", "credit site: pump draw (channel)"), ("LiquidTypes/Building_LiquidPump.cs", "credit site: pump draw (source)"),
    ("LiquidTypes/Building_LiquidPump.cs", "credit site: pump pour"), ("Machinery/CompLiquidConverter.cs", "credit site: converter input"),
    ("Machinery/CompLiquidConverter.cs", "credit site: converter output"), ("Machinery/CompLiquidPipeAdapter.cs", "credit site: adapter feeds the pipe net"),
    ("Machinery/CompLiquidPipeAdapter.cs", "credit site: adapter draws from the pipe net"), ("Machinery/Kits/RM_LiquidReaction.cs", "credit site: reactor A"),
    ("Machinery/Kits/RM_LiquidReaction.cs", "credit site: reactor B"), ("Machinery/Kits/RM_LiquidReaction.cs", "credit site: reactor product"),
    ("Machinery/Kits/RM_LiquidBath.cs", "credit site: bath"), ("Machinery/RM_LiquidNet.cs", "credit site: tank settle"),
    ("LiquidTypes/Building_LiquidPump.cs", "credit site: pump to outflow"), ("LiquidTypes/Building_LiquidPump.cs", "credit site: pump intake (to outflow)"),
    ("LiquidTypes/Building_LiquidPump.cs", "credit site: pump intake (channel)"), ("LiquidTypes/Building_LiquidPump.cs", "credit site: pump intake (source)"),
    ("LiquidTypes/Building_LiquidPump.cs", "credit site: outflow pour (tank)"), ("LiquidTypes/Building_LiquidPump.cs", "credit site: outflow pour (end)"),
    ("Machinery/RM_LiquidNet.cs", "credit site: dump drain"),
    ("LiquidTypes/Building_LiquidPump.cs", "credit site: pond return (pump)"),   # POND_RETURN_LEG_BUILD_WATER_GOES_HOME
    ("Sprinklers/RM_Sprinkle.cs", "credit site: sprinkler draw"),   # SPRINKLER_HEADS_BUILD_PUMP_REQUIRED
    ("Machinery/RM_Levelling.cs", "credit site: levelling"),   # PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL
    ("LiquidTypes/Building_LiquidPump.cs", "credit site: pump overflow spill"),   # CANAL_OVERFLOW stage 1 (mirrors TransferChecks.CreditTags)
    ("Machinery/RM_LiquidNet.cs", "credit site: gravity overflow"),   # CANAL_OVERFLOW stage 2
]
CREDIT_CALL = re.compile(r"(?:RM_LiquidNet\.Credit|\bCreditTo|\bCreditRoute)\(")
CREDIT_DEF = re.compile(r"static void (?:Credit|CreditTo|CreditRoute)\(")


def _credit_calls(text):
    """Credit calls in one C# file, outside // comments and outside the crediting functions' own bodies (the service, not a site)."""
    code = "\n".join(ln.split("//", 1)[0] for ln in text.split("\n"))
    spans = []
    for m in CREDIT_DEF.finditer(code):
        i = code.index("{", m.end())
        depth, j = 0, i
        while j < len(code):
            depth += {"{": 1, "}": -1}.get(code[j], 0)
            if depth == 0:
                break
            j += 1
        spans.append((m.start(), j))
    return sum(1 for m in CREDIT_CALL.finditer(code) if not any(a <= m.start() <= b for a, b in spans))


def p9_credit_sites(srcs=None):
    """(bad, calls): each CREDIT_SITES tag once on a credit line inside a committed transfer, and the production credit-call count.
    <srcs> plants {rel: text}; by default every non-SelfTest .cs under Source/."""
    if srcs is None:
        root = os.path.join(HERE, "Source")
        srcs = {os.path.relpath(p, root).replace(os.sep, "/"): open(p, encoding="utf-8").read()
                for p in glob.glob(os.path.join(root, "**", "*.cs"), recursive=True)
                if not any(x in p.replace(os.sep, "/") for x in ("/SelfTest/", "/bin/", "/obj/"))}
    bad = []
    for rel, tag in CREDIT_SITES:
        lines = srcs.get(rel, "").split("\n")
        hit = [i for i, ln in enumerate(lines) if tag in ln]
        if len(hit) != 1 or not CREDIT_CALL.search(lines[hit[0]].split("//", 1)[0]):
            bad.append("%s: %s (%d)" % (rel, tag, len(hit)))
            continue
        above = "\n".join(lines[max(0, hit[0] - 6):hit[0]])
        if not re.search(r"if \(RM_LiquidTransfer\.Move\(|if \(.*Try(Add|Remove)Liquid\(|if \(made\)", above):
            bad.append("%s: %s is not inside a committed transfer" % (rel, tag))
    return bad, sum(_credit_calls(t) for t in srcs.values())


def p9_planted():
    """P9's can-fail: the real checker on planted sources - the bath credit moved out of its committed block (unguarded), the
    dump drain tag deleted (missing), and one extra credit call appended (count)."""
    root = os.path.join(HERE, "Source")
    srcs = {os.path.relpath(p, root).replace(os.sep, "/"): open(p, encoding="utf-8").read()
            for p in glob.glob(os.path.join(root, "**", "*.cs"), recursive=True)
            if not any(x in p.replace(os.sep, "/") for x in ("/SelfTest/", "/bin/", "/obj/"))}
    srcs["Machinery/Kits/RM_LiquidBath.cs"] = "\n".join(["x();"] * 8) + "\nRM_LiquidNet.Credit(parent, t, l, 1, 250);   // credit site: bath\n" + \
        srcs["Machinery/Kits/RM_LiquidBath.cs"].replace("// credit site: bath", "// (moved)").replace("RM_LiquidNet.Credit(", "RM_LiquidNet.Credit_(")
    srcs["Machinery/RM_LiquidNet.cs"] = srcs["Machinery/RM_LiquidNet.cs"].replace("// credit site: dump drain", "//")
    srcs["Machinery/Extra.cs"] = "class E { void F() { RM_LiquidNet.Credit(a, b, c, 1, 2); } }"
    return p9_credit_sites(srcs)


OLD_HOSE_PATHS = ("GimmeSomeSlack/validation_hose", "GimmeSomeSlack/validation_style_hose", "GimmeSomeSlack/Source/Hose/")
WALK_GSS = os.path.join(os.path.dirname(os.path.dirname(RM)), "design", "validation_walks", "RimMandrake", "GimmeSomeSlack.md")


def p10_stale_pointers(texts=None):
    """Review S6: (file, problem) for each pointer to a hose file at its pre-port GSS path, in the GSS walk and in both mods'
    C#/Python, and each backticked src/... path the GSS walk names that does not exist. <texts> plants {name: text}."""
    repo = os.path.dirname(os.path.dirname(RM))
    if texts is None:
        texts = {WALK_GSS: open(WALK_GSS, encoding="utf-8").read()}
        for root in (GSS, HERE):
            for p in glob.glob(os.path.join(root, "**", "*.cs"), recursive=True) + glob.glob(os.path.join(root, "**", "*.py"), recursive=True):
                if "/bin/" in p or "/obj/" in p or p.endswith("selftest_hose_port.py"):
                    continue
                texts[p] = open(p, encoding="utf-8", errors="replace").read()
    out = []
    for name, text in texts.items():
        for old in OLD_HOSE_PATHS:
            if old in text:
                out.append((os.path.relpath(name, repo), "names " + old))
        if name == WALK_GSS or name.endswith(".md"):
            for m in re.finditer(r"`(src/RimMandrake/[^`\s]+)`", text):
                if not os.path.exists(os.path.join(repo, m.group(1))):
                    out.append((os.path.relpath(name, repo), "missing " + m.group(1)))
    return out


def code_lines(text):
    """Lines of C# with // comments and /// docs stripped (string literals kept)."""
    out = []
    for ln in text.split("\n"):
        s = ln.strip()
        if s.startswith("//"):
            continue
        i = ln.find("//")
        out.append(ln if i < 0 or ln.count('"', 0, i) % 2 else ln[:i])
    return out


def main():
    # P1
    both, g, f = p1_duplicates(GSS, HERE)
    check("P1 no defName in both mods (%d GSS, %d FlowWorks)" % (len(g), len(f)), not both and "RM_HoseReel" in f and len(g) > 20, both[:6])
    shared, none = p1_planted()
    check("P1 can-fail: the P1 checker run on planted mod folders reports the shared defName, and none for disjoint ones",
          shared == ["RM_Shared"] and none == [], (shared, none))
    # P2
    hits = []
    for p in glob.glob(os.path.join(GSS, "Source", "**", "*.cs"), recursive=True):
        # RM_FallenWireShock: the soft ignition lookup; LegacyName(+Checks): the MessyConduit -> GSS rename table, whose
        # FireHosesMod handle still renames the oldest hose settings file so FlowWorks can import it (data, not a dependency)
        if "/bin/" in p or "/obj/" in p or p.endswith(("RM_FallenWireShock.cs", "LegacyName.cs", "LegacyNameChecks.cs")):
            continue
        for ln in code_lines(open(p, encoding="utf-8").read()):
            if "FlowWorks" in ln or re.search(r"\bHose(Math|Relay|Styles|Settings|Probe|Look)\b|CompHoseReel|RM_MapComponent_Hoses", ln):
                hits.append("%s: %s" % (os.path.relpath(p, GSS), ln.strip()[:100]))
    leftovers = [x for x in ("Source/Hose", "Defs/Hose", "Textures/RimMandrake/GimmeSomeSlack/Hose", "Source/SelfTest/HoseSelfTest.cs",
                             "validation_hose.py", "validation_style_hose.py") if os.path.exists(os.path.join(GSS, x))]
    check("P2 GSS C# names no FlowWorks hose code; no hose folder/def/art/suite left", not hits and not leftovers, (hits + leftovers)[:6])
    check("P2 can-fail: a planted FlowWorks reference is seen", any("FlowWorks" in ln for ln in code_lines('x = "RimMandrake.FlowWorks.Hose.HoseProbe";')))
    check("P2 can-fail: a comment-only mention is not a dependency", not any("FlowWorks" in ln for ln in code_lines("    // moved to FlowWorks")))
    # P3
    ess = open(os.path.join(HERE, "Source", "Hose", "RM_HoseLegacy.cs"), encoding="utf-8").read()
    mc = open(os.path.join(HERE, "Source", "Hose", "RM_MapComponent_Hoses.cs"), encoding="utf-8").read()
    i = mc.index("class Patch_Map_ExposeComponents_SkipHoses")
    attr = mc[max(0, i - 400):i]
    check("P3 (source shape) save-skip + type alias applied by RM_HoseEssentials (GetPatchedMethods census), not by attribute",
          'AccessTools.Method(typeof(Map), "ExposeComponents")' in ess and "nameof(GenTypes.GetTypeInAnyAssembly)" in ess
          and "GetPatchedMethods()" in ess and "HarmonyPatch" not in attr.split("</summary>")[-1]
          and "if (!RM_HoseEssentials.SaveSkipPatched) { UnhookMapEvents(); map.components.Remove(this); }" in mc)
    mod = open(os.path.join(HERE, "Source", "RimMandrakeFlowWorksMod.cs"), encoding="utf-8").read()
    check("P3 the FlowWorks Mod constructor applies the essentials and the one-time import", "Hose.RM_HoseEssentials.Apply();" in mod and "Hose.RM_HoseLegacy.ImportOnce()" in mod)
    # P4
    code = ("import sys\nsys.path=[p for p in sys.path if 'GimmeSomeSlack' not in p]\nsys.path.insert(0, %r)\n"
            "import validation_hose, validation_style_hose, validation_hose_offline\n"
            "bad=[m for m,v in sys.modules.items() if 'GimmeSomeSlack' in str(getattr(v,'__file__','') or '')]\n"
            "print('GSSMODS', bad)\n" % HERE)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd="/tmp")
    check("P4 moved scripts import with GSS absent", r.returncode == 0 and "GSSMODS []" in r.stdout, (r.stdout + r.stderr)[-300:])
    # P5
    sys.path.insert(0, HERE)
    import validation_hose as VH
    ok_blob = b'<curDriver Class="RimMandrake.FlowWorks.Hose.Jobs.JobDriver_CarryHoseEnd"> rmHoseState rmHoseState'
    h = VH.save_class_hits(ok_blob)
    check("P5 a FlowWorks mid-carry driver is allowed", h["drivers"] == 1 and not h["offending"] and h["rmHoseState"] == 2, h)
    for label, blob in (("old GSS driver name", b'<curDriver Class="RimMandrake.GimmeSomeSlack.Hose.Jobs.JobDriver_CarryHoseEnd">'),
                        ("MessyConduit driver name", b'<curDriver Class="RimMandrake.MessyConduit.Hose.Jobs.JobDriver_RetractHose">'),
                        ("map component written", b'<li Class="RimMandrake.FlowWorks.Hose.RM_MapComponent_Hoses">'),
                        ("FlowWorks hose class outside curDriver", b'<thing Class="RimMandrake.FlowWorks.Hose.CompHoseReel">'),
                        ("a non-whitelisted FlowWorks driver", b'<curDriver Class="RimMandrake.FlowWorks.Hose.Jobs.JobDriver_Other">')):
        check("P5 refused: %s" % label, bool(VH.save_class_hits(blob)["offending"]))
    check("P5 H11 sees old and new class names", VH.names_hose_class("Could not find class RimMandrake.GimmeSomeSlack.Hose.X")
          and VH.names_hose_class("type RimMandrake.FlowWorks.Hose.Y") and not VH.names_hose_class("RM_HoseReel missing def"))
    # P6
    r = subprocess.run([sys.executable, os.path.join(HERE, "validation_style_hose.py"), "--offline"], capture_output=True, text=True)
    check("P6 validation_style_hose.py --offline (R0)", r.returncode == 0 and "R0_reel_styles_offline       PASS" in r.stdout, r.stdout[-300:])
    # P7
    import xml.etree.ElementTree as ET
    fa = ET.parse(os.path.join(HERE, "About", "About.xml")).getroot()
    ga = ET.parse(os.path.join(GSS, "About", "About.xml")).getroot()
    after = [li.text.strip().lower() for li in fa.findall("loadAfter/li")]
    fdeps = [(li.findtext("packageId") or "").lower() for li in fa.findall("modDependencies/li")]
    gall = [(li.text or "").strip().lower() for li in ga.iter("li") if li.text] + [(li.findtext("packageId") or "").lower() for li in ga.findall("modDependencies/li")]
    check("P7 FlowWorks loadAfter mandrake.rm.gimmesomeslack, not a dependency", "mandrake.rm.gimmesomeslack" in after and "mandrake.rm.gimmesomeslack" not in fdeps, (after, fdeps))
    check("P7 Gimme Some Slack names FlowWorks nowhere in its About", not any("flowworks" in x for x in gall), gall)
    # P8
    lg = open(os.path.join(HERE, "Defs", "Machinery", "RM_LiquidLogistics.xml"), encoding="utf-8").read()
    net = open(os.path.join(HERE, "Source", "Machinery", "RM_LiquidNet.cs"), encoding="utf-8").read()
    check("P8 RM_UniversalPipe def with the pipe extension; RM_LiquidHose is no live defName", "<defName>RM_UniversalPipe</defName>" in lg
          and "RimMandrake.FlowWorks.Machinery.RM_UniversalPipeExtension" in lg and "RM_LiquidHose" not in f)
    check("P8 RM_LiquidHoseExtension kept as an [Obsolete] subclass", "public class RM_LiquidHoseExtension : RM_UniversalPipeExtension" in net
          and "[System.Obsolete(" in net)
    check("P8 (source shape) def alias is an essential patch (census of three)", "nameof(BackCompatibility.BackCompatibleDefName)" in ess and "DefAliasPatched" in ess
          and "save-skip, type alias, def alias" in ess)
    # P9
    bad, calls = p9_credit_sites()
    check("P9 %d credit sites (FINAL's 11 + tank settle + 6 pump hose ends + dump drain + pond return + sprinkler draw), each inside a committed transfer"
          % len(CREDIT_SITES), not bad and calls == len(CREDIT_SITES), (bad, calls))
    pbad, pcalls = p9_planted()
    check("P9 can-fail: a planted unguarded credit, a missing tag and an extra call are all caught", len(pbad) == 2 and pcalls == len(CREDIT_SITES) + 1,
          (pbad, pcalls))
    allsrc = "".join(open(p, encoding="utf-8").read() for p in glob.glob(os.path.join(HERE, "Source", "**", "*.cs"), recursive=True) if "/SelfTest/" not in p)
    gone = [x for x in ("class FlowWorksPumpFlow", "class RelayHoseFlow", "class HoseTint", "bool useFlowWorksPumps", "string defaultFluid",
                                  "hose_useFlowWorksPumps", "hose_defaultFluid") if x in allsrc]
    check("P9 the reflection adapter, relay provider, tint table and the two dead settings are deleted", not gone, gone)
    # P10 (review S6): no pointer to a hose file at its pre-port GSS path, and every backticked src/ path the GSS walk cites exists
    stale = p10_stale_pointers()
    check("P10 no pointer to a moved hose file at its old Gimme Some Slack path; the GSS walk's src/ paths exist", not stale, stale[:6])
    check("P10 can-fail: a planted old-path pointer and a planted missing path are both caught",
          sorted(x[1] for x in p10_stale_pointers({"planted.md": "see `src/RimMandrake/GimmeSomeSlack/validation_hose.py` and `src/RimMandrake/Nope/x.cs`"}))
          == ["missing src/RimMandrake/GimmeSomeSlack/validation_hose.py", "missing src/RimMandrake/Nope/x.cs", "names GimmeSomeSlack/validation_hose"])
    # review S5: P3 and P8 read the source shape only; that the aliases actually resolve a pre-port save is proved only by the
    # live PP1/PP2 rows (proof_hose), which need pre-port save fixtures that do not exist yet
    print("UNMEASURED  PP1/PP2 pre-port saves load through the aliases (live rows; no fixtures yet) -- P3/P8 above are source shape only")
    print("hose port gates: %s (%d failing)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
