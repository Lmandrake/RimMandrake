#!/usr/bin/env python3
"""Serially pass each listed mod through a GPT full review (GPT_FULL_REVIEW_TOP10_1).
usage: run_gpt_review.py [Mod ...]   (default: the ten in MODS, skipping any whose review file exists)"""
import glob, os, subprocess, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MODS = ["FlowWorks", "CreatureBehaviors", "EnvironmentalHazards", "GimmeSomeSlack", "DivingInteraction",
        "Stillsand", "Scarlands", "TerminalBiomes", "LuminousPigment", "FeverWood"]
OUT = os.path.join(ROOT, "design/RimMandrake/gpt_reviews")
CAP = 380_000


def bundle(mod):
    base = os.path.join(ROOT, "src/RimMandrake", mod)
    pats = ["Source/**/Kernel/*.cs", "Source/*.cs", "Source/**/*.cs", "About/About.xml", "validation.py", "Defs/**/*.xml"]
    seen, parts, size = set(), [], 0
    for p in pats:
        for f in sorted(glob.glob(os.path.join(base, p), recursive=True)):
            if f in seen or "/SelfTest/" in f or "/obj/" in f:
                continue
            seen.add(f)
            t = open(f, errors="ignore").read()
            chunk = f"\n\n===== {os.path.relpath(f, base)} =====\n{t}"
            if size + len(chunk) > CAP:
                parts.append(f"\n\n===== (omitted for size: {os.path.relpath(f, base)}) =====")
                continue
            parts.append(chunk)
            size += len(chunk)
    path = os.path.join(ROOT, "Transient", f"gptreview_{mod}.txt")
    open(path, "w").write(f"MOD: {mod}\n" + "".join(parts))
    return path


for mod in (sys.argv[1:] or MODS):
    out = os.path.join(OUT, f"{mod}.md")
    if os.path.exists(out) and os.path.getsize(out) > 2000:
        print(mod, "exists, skip", flush=True)
        continue
    t0 = time.time()
    r = subprocess.run([sys.executable, os.path.join(ROOT, "src/RimMandrake/Utils/gpt_consult.py"),
                        "--prompt-file", os.path.join(OUT, "PROMPT.md"), "-f", bundle(mod), "--out", out,
                        "--effort", "high", "--timeout", "2400"], capture_output=True, text=True)
    print(mod, "rc", r.returncode, f"{time.time()-t0:.0f}s", os.path.getsize(out) if os.path.exists(out) else 0, flush=True)
    if r.returncode:
        print(r.stderr[-300:], flush=True)
