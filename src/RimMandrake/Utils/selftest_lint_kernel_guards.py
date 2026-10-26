#!/usr/bin/env python3
"""selftest_lint_kernel_guards.py - kernel_guards() on fixture mods only (no real csproj is read).

Proves: a clean kernel compiled into both projects yields no errors; every using-directive form that
pulls an engine namespace in is an ERROR (DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 11: `using static`,
`global using` and the alias form `using BG = RimWorld...;` used to pass); a comment naming Verse is not;
a file missing from either project and an absent kernel are ERRORs.
"""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lint_kernel_guards import kernel_guards  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + ("" if cond else " | %r" % (detail,)))
    if not cond:
        FAILS.append(name)


def fixture(root, kernel_text, in_mod=True, in_fuzz=True):
    src = os.path.join(root, "Source")
    os.makedirs(os.path.join(src, "Kernel"), exist_ok=True)
    os.makedirs(os.path.join(src, "SelfTest", "Fuzz"), exist_ok=True)
    with open(os.path.join(src, "Kernel", "K.cs"), "w", encoding="utf-8") as f:
        f.write(kernel_text)
    with open(os.path.join(src, "M.csproj"), "w", encoding="utf-8") as f:
        f.write('<Compile Include="Kernel\\K.cs" />' if in_mod else "")
    with open(os.path.join(src, "SelfTest", "Fuzz", "F.csproj"), "w", encoding="utf-8") as f:
        f.write('<Compile Include="..\\..\\Kernel\\K.cs" />' if in_fuzz else "")
    return kernel_guards(root, "M.csproj", "SelfTest/Fuzz/F.csproj", "t")


tmp = tempfile.mkdtemp(prefix="st_lint_kernel_guards_")
try:
    n = [0]

    def run(text, **kw):
        n[0] += 1
        return fixture(os.path.join(tmp, "m%d" % n[0]), text, **kw)

    clean = "// Verse-free kernel; no using Verse here.\nusing System;\nnamespace X { static class K {} }\n"
    e = run(clean)
    check("sanity: a clean kernel in both projects has no errors", e == [], e)
    for form in ("using Verse;", "using RimWorld.Planet;", "using static Verse.Rand;", "global using UnityEngine;",
                 "using BG = RimWorld.BaseGen.BaseGen;", "using H = global::HarmonyLib.Harmony;"):
        e = run(form + "\n" + clean)
        check("engine using is an ERROR: %s" % form, any("references the engine" in x for x in e), e)
    e = run("using VerseLike;\n" + clean)
    check("a namespace that merely starts with Verse is not the engine", e == [], e)
    e = run(clean, in_mod=False)
    check("not compiled into the mod is an ERROR", any("not compiled into the mod" in x for x in e), e)
    e = run(clean, in_fuzz=False)
    check("not compiled into the fuzz project is an ERROR", any("fuzz project" in x for x in e), e)
    os.makedirs(os.path.join(tmp, "empty", "Source"))
    e = kernel_guards(os.path.join(tmp, "empty"), "M.csproj", "SelfTest/Fuzz/F.csproj", "t")
    check("no kernel at all is an ERROR (sanity probe)", len(e) == 1 and "no .cs files" in e[0], e)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("ALL PASS" if not FAILS else "FAILED: %s" % FAILS)
sys.exit(1 if FAILS else 0)
