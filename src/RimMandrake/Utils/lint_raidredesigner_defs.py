#!/usr/bin/env python3
"""Offline lint of the RaidRedesigner mod (a source-only mod: zero Defs, so the checks that bite are compile-listed and settings-scribed;
see lint_mod_defs.py). The roster kernel's own structural guards (Verse-free, listed in both projects) are checked here too.

    python3 src/RimMandrake/Utils/lint_raidredesigner_defs.py [--mod-dir <dir>] [--quiet]
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_mod_defs  # noqa: E402


def kernel_guards(mod_dir):
    """The fuzz compiles Source/Kernel/*.cs directly: it must stay Verse-free, listed in the mod csproj AND in the fuzz csproj."""
    errs = []
    kd = os.path.join(mod_dir, "Source", "Kernel")
    files = sorted(f for f in os.listdir(kd) if f.endswith(".cs")) if os.path.isdir(kd) else []
    if not files:
        return ["ERROR raidredesigner-kernel: Source/Kernel has no .cs files (sanity probe: the kernel moved?)"]
    mod_proj = open(os.path.join(mod_dir, "Source", "RM_RaidRedesigner.csproj"), encoding="utf-8-sig").read()
    fuzz_proj = open(os.path.join(mod_dir, "Source", "SelfTest", "RimMandrakeRaidRedesigner.SelfTest.csproj"), encoding="utf-8-sig").read()
    for f in files:
        text = open(os.path.join(kd, f), encoding="utf-8-sig").read()
        if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)\b", text, re.M):
            errs.append("ERROR raidredesigner-kernel: %s references the engine (the fuzz build cannot compile it)" % f)
        if ('Compile Include="Kernel\\%s"' % f) not in mod_proj:
            errs.append("ERROR raidredesigner-kernel: %s is not compiled into the mod" % f)
        if ('Compile Include="..\\Kernel\\%s"' % f) not in fuzz_proj:
            errs.append("ERROR raidredesigner-kernel: %s is not compiled into the fuzz project" % f)
    if 'Compile Include="..\\RoleTag.cs"' not in fuzz_proj:
        errs.append("ERROR raidredesigner-kernel: RoleTag.cs is not in the fuzz project")
    return errs


def inert_spikes(mod_dir):
    """Files that declare themselves 'COMPILE-ONLY SPIKE' in their first lines are deliberately absent from the csproj."""
    out = set()
    sd = os.path.join(mod_dir, "Source")
    for f in os.listdir(sd):
        if f.endswith(".cs") and "COMPILE-ONLY SPIKE" in "".join(open(os.path.join(sd, f), encoding="utf-8-sig").readlines()[:8]):
            out.add(f)
    return out


if __name__ == "__main__":
    import contextlib
    import io
    argv = sys.argv[1:]
    mod_dir = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else os.path.join(os.path.dirname(HERE), "RaidRedesigner")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lint_mod_defs.run("RaidRedesigner", argv, require_xml=False, require_settings=True, instance_settings=False)
    spikes = inert_spikes(mod_dir)
    lines = buf.getvalue().splitlines()
    kept = [l for l in lines if not any(l.startswith("ERROR compile-listed: Source/%s " % sp) for sp in spikes)]
    dropped = len(lines) - len(kept)
    import re as _re
    for l in kept:
        if dropped and " ERROR," in l:
            l = _re.sub(r"(\d+) ERROR,", lambda m: "%d ERROR," % (int(m.group(1)) - dropped), l) + " (%d inert spike file(s) exempt)" % len(spikes)
        print(l)
    if dropped and not any(l.startswith("ERROR") for l in kept):
        rc = 0
    errs = kernel_guards(mod_dir)
    for e in errs:
        print(e)
    sys.exit(1 if (rc == 1 or errs) else rc)
