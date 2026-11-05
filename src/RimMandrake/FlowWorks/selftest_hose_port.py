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
  P9 (step 6, widened to L7) caller coverage: each of the 25 credit sites (FINAL's 11 - pump draw x2, pour; converter in/out;
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


# P9: every hose credit site, mirroring Source/SelfTest/TransferChecks.cs CreditTags (26: L7's 19 + pond return + sprinkler draw + levelling + pump overflow spill + gravity overflow + faucet draw + ice melter). Each tag must appear exactly
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
    ("Thirst/Building_RM_PipeFaucet.cs", "credit site: faucet draw"),   # PIPE_FAUCET_BUILD_TAP_NAME_NOW_FREE (mirrors TransferChecks.CreditTags)
    ("RM_IceMelter.cs", "credit site: ice melter"),   # a8f10174f1 ice melter (mirrors TransferChecks.CreditTags)
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


P9_GUARD = r"if \(RM_LiquidTransfer\.Move\(|if \(.*Try(Add|Remove)Liquid\(|if \(made\)"


def _header(lines, i, j):
    """The statement header ending at the `{` at lines[i][j]: that line's code before the brace plus the lines above it back
    to the previous statement boundary (a multi-line `if (Move(...,\n ...) == n)` header is read whole; at most 6 lines)."""
    out = [lines[i].split("//", 1)[0][:j]]
    k = i - 1
    while k >= 0 and len(out) < 7:
        code = lines[k].split("//", 1)[0].rstrip()
        if not code.strip() or code.rstrip().endswith((";", "{", "}")):
            break
        out.insert(0, code)
        k -= 1
    return "\n".join(out)


def _open_brace(lines, at, col=None):
    """(line, col) of the innermost unclosed `{` before line `at` (before column `col` of it when given), or None."""
    depth = 0
    for i in range(at, -1, -1):
        code = lines[i].split("//", 1)[0]
        hi = (col if i == at and col is not None else 0 if i == at else len(code))
        for j in range(hi - 1, -1, -1):
            if code[j] == "}":
                depth += 1
            elif code[j] == "{":
                if depth == 0:
                    return i, j
                depth -= 1
    return None


def _enclosing_guard(lines, at):
    """The guard that commits line `at`'s credit, as text for P9_GUARD to match ("" when there is none):
    (a) the header of the innermost block holding it, or (b) an early-exit block just before it at the same level,
    `if (Move(...) != n) { ... return; }` (its header, only when its body leaves by return/continue/break).
    A 6-line text window passed a credit moved just after the guarded block's closing brace (GPT 7.11,
    FW_PROOF_TOOLS_HARDEN_READ_GAPS); brace structure does not."""
    got = []
    ob = _open_brace(lines, at)
    if ob:
        h = _header(lines, *ob)
        if _move_guard(h) in (None, "commit"):
            got.append(h)
    k = at - 1
    while k >= 0 and not lines[k].split("//", 1)[0].strip():
        k -= 1
    if k >= 0 and lines[k].split("//", 1)[0].strip() == "}":
        col = lines[k].index("}")
        inner = _open_brace(lines, k, col)
        if inner:
            body = "\n".join(ln.split("//", 1)[0] for ln in lines[inner[0]:k + 1])
            body = body[inner[1] + 1:]   # from just inside the opening brace (its column survives the comment strip)
            h = _header(lines, *inner)
            if _ends_in_exit(body[:body.rindex("}")]) and _move_guard(h) in (None, "refuse"):
                got.append(h)
    return "\n".join(got)


# TRANSFER_LINT_HARDEN_REFUSED_CREDIT_PASSES (Codex rev_i), mirroring TransferChecks.CommittedBlocks: a Move guard commits only
# as the Move call plus ONE comparison, `== name` or `> 0` (`== 0` is the refusal: Move returns 0 on every refusal); an
# early-exit branch is `!= name` and must END in an exit at its own top level (a return nested in an inner if falls through).
# `name` is Move's own first argument, what was asked for (`== none`, none = 0, is the refusal again under another name).


def _close_paren(s, i):
    """Index of the ')' matching the '(' at s[i] (string literals skipped), or -1."""
    depth, j = 0, i
    while j < len(s):
        c = s[j]
        if c == '"':
            j += 1
            while j < len(s) and s[j] != '"':
                j += 2 if s[j] == "\\" else 1
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return j
        j += 1
    return -1


def _first_arg(s, open_, close):
    """The text of the call's first argument (between the '(' at s[open_] and its first top-level ',' or its ')')."""
    depth, j = 0, open_ + 1
    while j < close:
        c = s[j]
        if c == '"':
            j += 1
            while j < close and s[j] != '"':
                j += 2 if s[j] == "\\" else 1
        elif c == "'" and j + 2 < close:
            j += 3 if s[j + 1] == "\\" else 2
        elif c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == "," and depth == 0:
            return s[open_ + 1:j].strip()
        j += 1
    return s[open_ + 1:close].strip()


def _move_guard(header):
    """None when the header names no Move; "commit" for `if (RM_LiquidTransfer.Move(n, ...) == n)` or `... > 0)`; "refuse" for
    `... != n)`; "" for any other Move header (a Move that is not the whole left side, `== 0`, `== other`, `== n || x`)."""
    if not re.search(r"RM_LiquidTransfer\.Move\(", header):
        return None
    m = re.search(r"if\s*\(\s*RM_LiquidTransfer\.Move\(", header)
    if not m:
        return ""
    close, mclose = _close_paren(header, header.index("(", m.start())), _close_paren(header, m.end() - 1)
    if close < 0 or mclose < 0 or mclose > close:
        return ""
    tail = header[mclose + 1:close].strip()
    if re.match(r"^>\s*0$", tail):
        return "commit"
    eq = re.match(r"^(==|!=)\s*(.+)$", tail)
    asked = re.sub(r"\s+", "", _first_arg(header, m.end() - 1, mclose))
    if not eq or not asked or re.sub(r"\s+", "", eq.group(2)) != asked:
        return ""
    return "commit" if eq.group(1) == "==" else "refuse"


def _ends_in_exit(body):
    """True when a block body's last top-level statement is return/continue/break (nested blocks read as "{}")."""
    top, depth, j = [], 0, 0
    while j < len(body):
        c = body[j]
        if c == '"':
            j += 1
            while j < len(body) and body[j] != '"':
                j += 2 if body[j] == "\\" else 1
            if depth == 0:
                top.append('""')
        elif c == "'" and j + 2 < len(body):   # review: a '}' char literal is no brace
            j += 3 if body[j + 1] == "\\" else 2
            continue
        elif c == "{":
            depth += 1
            if depth == 1:
                top.append("{")
        elif c == "}":
            depth -= 1
            if depth == 0:
                top.append("}")
        elif depth == 0:
            top.append(c)
        j += 1
    return re.search(r"(^|[;}])\s*(return\b[^;{}]*|continue|break);\s*$", "".join(top)) is not None


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
        if not re.search(P9_GUARD, _enclosing_guard(lines, hit[0])):
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


def p9_refused_planted():
    """P9's refused-credit can-fail (TRANSFER_LINT_HARDEN_REFUSED_CREDIT_PASSES): the real checker on two real sites made wrong -
    the bath's committed guard turned to `== 0` (a credit on the refusal) and the pump pour's refusal branch given only a
    conditional return (a refused pour falls through to its credit). Both must be caught, by those two sites' tags only."""
    root = os.path.join(HERE, "Source")
    srcs = {os.path.relpath(p, root).replace(os.sep, "/"): open(p, encoding="utf-8").read()
            for p in glob.glob(os.path.join(root, "**", "*.cs"), recursive=True)
            if not any(x in p.replace(os.sep, "/") for x in ("/SelfTest/", "/bin/", "/obj/"))}
    bath, pump = "Machinery/Kits/RM_LiquidBath.cs", "LiquidTypes/Building_LiquidPump.cs"
    srcs[bath], nb = re.subn(r"out _\) == ext\.UnitsPerCraft\)", "out _) == 0)", srcs[bath])
    srcs[pump], np_ = re.subn(r"(\n\s*)(return mv\.DestRefused \?[^;]*;)", r"\1if (mv.DestRefused) { \2 }", srcs[pump], count=1)
    melt = "RM_IceMelter.cs"   # == another name than what was asked for
    srcs[melt], nm = re.subn(r"out RM_MoveOutcome o\) == units\)", "out RM_MoveOutcome o) == spare)", srcs[melt])
    bad, _ = p9_credit_sites(srcs)
    return bad, nb + np_ + nm


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
    check("P9 %d credit sites (FINAL's 11 + tank settle + 6 pump hose ends + dump drain + pond return + sprinkler draw + levelling + overflow spills + faucet draw + ice melter), each inside a committed transfer"
          % len(CREDIT_SITES), not bad and calls == len(CREDIT_SITES), (bad, calls))
    pbad, pcalls = p9_planted()
    check("P9 can-fail: a planted unguarded credit, a missing tag and an extra call are all caught", len(pbad) == 2 and pcalls == len(CREDIT_SITES) + 1,
          (pbad, pcalls))
    rbad, planted = p9_refused_planted()
    units = (_move_guard("if (ok && RM_LiquidTransfer.Move(n, a, b, out _) == n)"), _move_guard("if (RM_LiquidTransfer.Move(n, a, b, out _) == n || x)"),
             _move_guard("if (RM_LiquidTransfer.Move(f(a, b), a, b, out _) != f(a, b))"), _ends_in_exit(" char c = '}'; if (y) { return; } "),
             _ends_in_exit(" if (x) return; "), _ends_in_exit(' log("}"); return mv.A ? 1 : 2; '))
    check("P9 refused-credit can-fail: a credit under `if (Move(...) == 0)` (bath), one after a refusal branch whose return is only "
          "conditional (pump pour) and one under `== another name` (ice melter) are all caught; a Move not alone on the left, "
          "a '}' char literal and `if (x) return;` are not committed shapes", planted == 3 and sorted(b.split(":")[0] for b in rbad) ==
          ["LiquidTypes/Building_LiquidPump.cs", "Machinery/Kits/RM_LiquidBath.cs", "RM_IceMelter.cs"]
          and units == ("", "", "refuse", False, False, True), (rbad, planted, units))
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
