#!/usr/bin/env python3
# selftest-timeout: 600   (one staged net8 build of the Graffiti kernel harness, ~1-2 min)
"""T_UGLINESS_OFFLINE (RIMMANDRAKE_REPIN_GRAFFITI_UGLINESS_BAR_STAT_NOBODY_INSPECTS): a vandal scrawl inspects uglier than a tally when
the same hand made both, offline, no game. Owner by card 2026-11-16 ("Look and stat agree"): the bar ugliness_visible says a scrawl looks
worse than a tally AND inspects as uglier when the same hand made both, with no numbers named.

Two halves:
  kernel  RM_GraffitiKernel.MarkBeauty (src/RimMandrake/Graffiti/Source/Kernel/RM_GraffitiKernel.cs), run as the `beauty` family of the
          kernel fuzz harness (src/RimMandrake/Graffiti/Source/SelfTest/GraffitiFuzz.cs): at each of the seven crafts a hand can roll,
          capped by each form as Filth_Mark.MakeMark caps it, the scrawl's beauty is strictly below the tally's, fresh and crossed out;
          within every form a better hand is never uglier and craft counts. Four planted mutants must go red, among them "craft alone",
          the formula before this item, which ties at awful and poor.
  source  the stat a player inspects is Filth_Mark.NetBeauty (Verse, cannot be loaded offline), so a narrow source read: NetBeauty's
          crafted branch takes MarkBeauty of the mark's own form (a def with no Graffiti extension, which no shipped mark is, keeps the
          craft alone); the Beauty StatPart, the mark's
          inspect line and the wall's inspect line all read NetBeauty, whole (`val = m.NetBeauty;`, not an expression around it).
          The form passed is the mark's own extension's, bare (`<ext>.form` with <ext> = def.GetModExtension<ModExtension_Graffiti>()):
          a conditional that hands a scrawl over as another form kept the old read green (blind challenge cycle 2,
          RIMMANDRAKE_TIGHTEN_GRAFFITI_UGLINESS_READ_SCRAWL_PASSED_AS_TAG). Four planted source mutants must each turn it red, every run.

    python3 src/RimMandrake/Utils/selftest_graffiti_ugliness.py [--source-only]

Exit 0 = every check green; 1 = a check red; 2 = the build or a source read could not be made (UNMEASURED).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import graffiti_src_read as S  # noqa: E402

SOURCE = os.path.join(REPO, "src", "RimMandrake", "Graffiti", "Source")
SELFTEST = os.path.join(SOURCE, "SelfTest")
KERNEL = os.path.join(SOURCE, "Kernel")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeGraffiti.SelfTest.csproj")
DLL_REL = "bin\\Release\\net8.0\\RimMandrakeGraffiti.SelfTest.dll"

# ---------------------------------------------------------------- the inspected stat, by source read

def _getter(sources, prop):
    """-> the body of property `prop`'s getter (the first `public float <prop>` in the sources), or None."""
    for _, text in sorted(sources.items()):
        code = S.strip_comments(text)
        m = re.search(r"\bpublic\s+float\s+%s\s*\{" % re.escape(prop), code)
        if m:
            close = S._match(code, m.end() - 1, "{", "}")
            return code[m.end():close] if close > 0 else None
    return None


def inspected_rule(sources):
    """-> list of failures (empty = the inspected beauty of a crafted mark is MarkBeauty of its form)."""
    body = _getter(sources, "NetBeauty")
    if body is None:
        return ["UNREAD: no `public float NetBeauty` getter in the Graffiti source"]
    fails = []
    head, sep, crafted = body.partition("if (!hasCraft)")
    if not sep:
        return ["UNREAD: NetBeauty has no `if (!hasCraft)` branch for an uncrafted mark"]
    crafted = crafted.split(";", 1)[1] if ";" in crafted else ""
    call = re.search(r"\bRM_GraffitiKernel\.MarkBeauty\s*\(\s*(\w+)\s*\??\.\s*form\s*,\s*craft\s*\)", crafted)
    if not call:
        fails.append("NetBeauty's crafted branch does not take RM_GraffitiKernel.MarkBeauty(<the mark's form>, craft)")
    elif not re.search(r"\b%s\s*=\s*def\s*\.\s*GetModExtension\s*<\s*ModExtension_Graffiti\s*>\s*\(\s*\)" % re.escape(call.group(1)), crafted):
        fails.append("NetBeauty passes %s.form, and %s is not the mark's own def.GetModExtension<ModExtension_Graffiti>()" % (call.group(1), call.group(1)))
    stat = [b for _, _, b in S.find_method(sources, "TransformValue")]
    if not any(re.search(r"\bval\s*=\s*m\.NetBeauty\s*;", b) for b in stat):
        fails.append("StatPart_GraffitiCraft.TransformValue does not set the Beauty stat to NetBeauty")
    for name in ("GetInspectString", "Postfix"):
        hits = [b for _, _, b in S.find_method(sources, name) if "BeautyWord" in b]
        if not hits:
            fails.append("UNREAD: no %s that writes a Beauty line" % name)
        elif not all(re.search(r"\bbeauty\s*=\s*(?:m\.)?NetBeauty\s*;", b) for b in hits):
            fails.append("%s writes a Beauty line that is not NetBeauty" % name)
    return fails


SOURCE_MUTANTS = [
    ("craft alone (the source before this item)", "Filth_Mark.cs",
     re.compile(r"RM_GraffitiKernel\.MarkBeauty\s*\([^;]*?,\s*craft\s*\)"), "RM_GraffitiKernel.CraftBeauty(craft)"),
    ("the stat line reads the def", "StatPart_GraffitiCraft.cs", re.compile(r"val\s*=\s*m\.NetBeauty"), "val = val"),
    # blind challenge cycle 2: both survived the old read while the behaviour broke
    ("a scrawl handed over as a tag", "Filth_Mark.cs", re.compile(r"RM_GraffitiKernel\.MarkBeauty\(ext\.form, craft\)"),
     "RM_GraffitiKernel.MarkBeauty(ext.form == GraffitiForm.Scrawl ? GraffitiForm.Tag : ext.form, craft)"),
    ("the stat keeps the def around NetBeauty", "StatPart_GraffitiCraft.cs", re.compile(r"val\s*=\s*m\.NetBeauty;"), "val = m.NetBeauty * 0f + val;"),
]


def source_half():
    sources = S.read_source(SOURCE)
    fails = inspected_rule(sources)
    unread = [f for f in fails if f.startswith("UNREAD")]
    print("source: the inspected beauty is MarkBeauty of the mark's form: %s" % ("green" if not fails else "RED"))
    for f in fails:
        print("FAIL " + f)
    blind = []
    for name, fname, pat, new in SOURCE_MUTANTS:
        rel = next((k for k in sources if os.path.basename(k) == fname), None)
        if rel is None or not pat.search(sources[rel]):
            blind.append("mutant '%s': its anchor is gone from %s (re-anchor it)" % (name, fname))
            continue
        mutated = dict(sources)
        mutated[rel] = pat.sub(new, sources[rel], count=1)
        red = inspected_rule(mutated)
        print("  source mutant '%s': %s" % (name, "RED (caught)" if red else "GREEN (survived)"))
        if not red:
            blind.append("mutant '%s' survived the inspected-beauty read" % name)
    for b in blind:
        print("FAIL " + b)
    return (2 if unread else 1) if (fails or blind) else 0

# ---------------------------------------------------------------- the kernel half

def main(argv):
    src_rc = source_half()
    if "--source-only" in argv:
        print("T_UGLINESS_OFFLINE: %s (source only)" % {0: "PASS", 1: "FAIL", 2: "UNMEASURED"}[src_rc])
        return src_rc
    import winbuild  # noqa: E402
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="GraffitiUglinessSelfTest", extra_dirs=[KERNEL])
    if rc:
        print("T_UGLINESS_OFFLINE: UNMEASURED - harness build failed (%d)" % rc)
        return 2
    k_rc = winbuild.run_interop([winbuild.dotnet_exe(), winbuild.staged_win(rec, SELFTEST) + "\\" + DLL_REL, "--fuzz-only", "beauty"],
                                cwd=winbuild.BUILD_ROOT, timeout=300)
    parts = ["kernel beauty family %s" % ("green" if k_rc == 0 else "RED"),
             "inspected beauty %s" % {0: "green", 1: "RED", 2: "UNREAD"}[src_rc]]
    ok = k_rc == 0 and src_rc == 0
    print("T_UGLINESS_OFFLINE: %s (%s)" % ("PASS" if ok else ("UNMEASURED" if src_rc == 2 else "FAIL"), "; ".join(parts)))
    return 0 if ok else (2 if src_rc == 2 and k_rc == 0 else 1)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
