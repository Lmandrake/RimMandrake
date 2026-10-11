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
  P9 (step 6) caller coverage: each of the 11 liquid mutation sites (pump draw x2, pour; converter in/out; adapter in/out;
     reactor A/B/product; bath) credits the hose route right after a SUCCESSFUL mutation, and the reflection pump adapter,
     the relay provider, the hand tint table and the two dead settings are gone
  P7 (step 3) FlowWorks loads after Gimme Some Slack (ordering) without depending on it; GSS neither depends on nor orders by FlowWorks
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
    g, f = defnames(GSS), defnames(HERE)
    both = sorted(set(g) & set(f))
    check("P1 no defName in both mods (%d GSS, %d FlowWorks)" % (len(g), len(f)), not both and "RM_HoseReel" in f and len(g) > 20, both[:6])
    check("P1 can-fail: a planted shared name is caught", bool(set(g) & set(dict(f, **{next(iter(g)): "x"})))
          if g else False)
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
    check("P3 save-skip + type alias applied by RM_HoseEssentials (GetPatchedMethods census), not by attribute",
          'AccessTools.Method(typeof(Map), "ExposeComponents")' in ess and "nameof(GenTypes.GetTypeInAnyAssembly)" in ess
          and "GetPatchedMethods()" in ess and "HarmonyPatch" not in attr.split("</summary>")[-1]
          and "if (!RM_HoseEssentials.SaveSkipPatched) map.components.Remove(this);" in mc)
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
    check("P8 def alias is an essential patch (census of three)", "nameof(BackCompatibility.BackCompatibleDefName)" in ess and "DefAliasPatched" in ess
          and "save-skip, type alias, def alias" in ess)
    # P9
    sites = [("LiquidTypes/Building_LiquidPump.cs", "credit site: pump draw (channel)"), ("LiquidTypes/Building_LiquidPump.cs", "credit site: pump draw (source)"),
             ("LiquidTypes/Building_LiquidPump.cs", "credit site: pump pour"), ("Machinery/CompLiquidConverter.cs", "credit site: converter input"),
             ("Machinery/CompLiquidConverter.cs", "credit site: converter output"), ("Machinery/CompLiquidPipeAdapter.cs", "credit site: adapter feeds the pipe net"),
             ("Machinery/CompLiquidPipeAdapter.cs", "credit site: adapter draws from the pipe net"), ("Machinery/Kits/RM_LiquidReaction.cs", "credit site: reactor A"),
             ("Machinery/Kits/RM_LiquidReaction.cs", "credit site: reactor B"), ("Machinery/Kits/RM_LiquidReaction.cs", "credit site: reactor product"),
             ("Machinery/Kits/RM_LiquidBath.cs", "credit site: bath")]
    bad = []
    for rel, tag in sites:
        lines = open(os.path.join(HERE, "Source", rel), encoding="utf-8").read().split("\n")
        hit = [i for i, ln in enumerate(lines) if tag in ln]
        if len(hit) != 1 or "RM_LiquidNet.Credit(" not in lines[hit[0]]:
            bad.append("%s: %s (%d)" % (rel, tag, len(hit)))
            continue
        # the credit sits inside the block of a SUCCESSFUL mutation: the nearest mutation call above it is in an if(...)
        above = "\n".join(lines[max(0, hit[0] - 4):hit[0]])
        if not re.search(r"if \(.*Try(Add|Remove)Liquid\(|made\)|if \(made\)", above):
            bad.append("%s: %s is not guarded by a successful mutation" % (rel, tag))
    allsrc = "".join(open(p, encoding="utf-8").read() for p in glob.glob(os.path.join(HERE, "Source", "**", "*.cs"), recursive=True) if "/SelfTest/" not in p)
    calls = len(re.findall(r"RM_LiquidNet\.Credit\(", allsrc))
    check("P9 11 credit sites, each right after a successful mutation", not bad and calls == 11, (bad, calls))
    gone = [x for x in ("class FlowWorksPumpFlow", "class RelayHoseFlow", "class HoseTint", "bool useFlowWorksPumps", "string defaultFluid",
                                  "hose_useFlowWorksPumps", "hose_defaultFluid") if x in allsrc]
    check("P9 the reflection adapter, relay provider, tint table and the two dead settings are deleted", not gone, gone)
    print("hose port gates: %s (%d failing)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
