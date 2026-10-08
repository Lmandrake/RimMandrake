#!/usr/bin/env python3
"""Structural guard shared by the per-mod lints: a mod's Verse-free kernel (Source/Kernel/*.cs) must stay engine-free, be compiled into the
mod AND into its fuzz project (the fuzz compiles the production file directly). Returns ERROR lines; a sanity probe errors when it
finds no kernel at all, so a moved folder cannot read as a clean bill of health.

    errors = kernel_guards(mod_dir, "RM_SeaShores.csproj", "SelfTest/Fuzz/RimMandrakeSeaShores.Fuzz.csproj", "seashores-kernel")
"""
import os
import re


def kernel_guards(mod_dir, mod_csproj, fuzz_csproj_rel, tag, extra_fuzz_includes=()):
    errs = []
    kd = os.path.join(mod_dir, "Source", "Kernel")
    files = sorted(f for f in os.listdir(kd) if f.endswith(".cs")) if os.path.isdir(kd) else []
    if not files:
        return ["ERROR %s: Source/Kernel has no .cs files (sanity probe: the kernel moved?)" % tag]
    mod_proj = open(os.path.join(mod_dir, "Source", mod_csproj), encoding="utf-8-sig").read()
    fz = os.path.join(mod_dir, "Source", *fuzz_csproj_rel.split("/"))
    if not os.path.exists(fz):
        return ["ERROR %s: fuzz project %s is missing" % (tag, fuzz_csproj_rel)]
    fuzz_proj = open(fz, encoding="utf-8-sig").read()
    depth = "..\\" * (fuzz_csproj_rel.count("/"))
    for f in files:
        text = open(os.path.join(kd, f), encoding="utf-8-sig").read()
        if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)\b", text, re.M):
            errs.append("ERROR %s: %s references the engine (the fuzz build cannot compile it)" % (tag, f))
        if ('Compile Include="Kernel\\%s"' % f) not in mod_proj:
            errs.append("ERROR %s: %s is not compiled into the mod" % (tag, f))
        if ('Compile Include="%sKernel\\%s"' % (depth, f)) not in fuzz_proj:
            errs.append("ERROR %s: %s is not compiled into the fuzz project" % (tag, f))
    for inc in extra_fuzz_includes:
        if inc not in fuzz_proj:
            errs.append("ERROR %s: the fuzz project no longer includes %s" % (tag, inc))
    return errs
