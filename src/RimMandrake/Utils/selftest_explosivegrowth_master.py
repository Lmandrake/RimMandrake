#!/usr/bin/env python3
"""ExplosiveGrowth's master switch stops everything (owner by card 2026-10-23: "Master stops everything").

Static check, no game, no build. Every Harmony Prefix/Postfix in RM_ExplosiveGrowthPatches.cs and every named runtime
entry point (map pass, soak, wet read, suppression, the bloom incident) must read `ExplosiveGrowthSettings.On` — the
master ANDed with the Baroque Biomes roster toggle — and no per-mechanic switch may exist that runs without it (the old
everyday-band `BandsOn` that ignored the master: EGROWTH_MASTER_FIX_SPARES_THE_BANDS).

Sanity probe first: the check is run once on a copy with one gate removed and MUST fail, so a pass means the
instrument can see.

    python3 src/RimMandrake/Utils/selftest_explosivegrowth_master.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "ExplosiveGrowth", "Source")
GATE = "ExplosiveGrowthSettings.On"

# (file, method signature regex) — each body must read the master gate.
ENTRY_POINTS = [
    ("RM_MapComponent_ExplosiveGrowth.cs", r"public override void MapComponentTick\(\)"),
    ("RM_MapComponent_ExplosiveGrowth.cs", r"public bool TrySoak\(IntVec3 c, int ticks\)"),
    ("RM_MapComponent_ExplosiveGrowth.cs", r"public bool IsWetFor\("),
    ("RM_MapComponent_ExplosiveGrowth.cs", r"public void Suppress\(IntVec3 center, int radius, int ticks\)"),
    ("RM_IncidentWorker_BloomBurst.cs", r"CanFireNowSub\("),
]


def body_after(text, start):
    """The text of the method whose signature ends at `start`: brace-matched block, or an expression body up to ';'."""
    i = start
    while i < len(text) and text[i] not in "{=;":
        i += 1
    if i >= len(text):
        return ""
    if text[i] == "=":  # expression-bodied member
        j = text.index(";", i)
        return text[i:j]
    if text[i] == ";":
        return ""
    depth, j = 0, i
    while j < len(text):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
        j += 1
    return text[i:]


def check(files):
    """files: name -> source text. Returns a list of failures."""
    fails = []
    patches = files["RM_ExplosiveGrowthPatches.cs"]
    hooks = list(re.finditer(r"public static \w+ (Prefix|Postfix|Transpiler)\(", patches))
    if len(hooks) < 5:
        fails.append(f"only {len(hooks)} Harmony hooks found in RM_ExplosiveGrowthPatches.cs: the parser is blind")
    for m in hooks:
        line = patches.count("\n", 0, m.start()) + 1
        if GATE not in body_after(patches, m.end()):
            fails.append(f"RM_ExplosiveGrowthPatches.cs:{line} {m.group(1)} does not read {GATE}")
    for name, sig in ENTRY_POINTS:
        text = files[name]
        m = re.search(sig, text)
        if not m:
            fails.append(f"{name}: entry point /{sig}/ not found (renamed? update this test)")
            continue
        if GATE not in body_after(text, m.end()):
            fails.append(f"{name}: /{sig}/ does not read {GATE}")
    for name, text in files.items():
        for m in re.finditer(r"\bBandsOn\b|\bbandsEnabled\s*=", text):
            line = text.count("\n", 0, m.start()) + 1
            fails.append(f"{name}:{line} a band switch is back ({m.group(0)}); it must go through {GATE}")
    return fails


def main():
    names = {n for n, _ in ENTRY_POINTS} | {"RM_ExplosiveGrowthPatches.cs"}
    files = {}
    for n in names:
        with open(os.path.join(SRC, n), encoding="utf-8") as f:
            files[n] = f.read()

    # Sanity probe: remove the Suppress gate in a copy; the check must catch it.
    broken = dict(files)
    mc = broken["RM_MapComponent_ExplosiveGrowth.cs"]
    probe = "!ExplosiveGrowthSettings.On || !ExplosiveGrowthSettings.suppressionEnabled"
    if probe not in mc:
        print("FAIL sanity probe: the Suppress gate line moved; update the probe string")
        return 1
    broken["RM_MapComponent_ExplosiveGrowth.cs"] = mc.replace(probe, "!ExplosiveGrowthSettings.suppressionEnabled")
    if not any("Suppress" in f for f in check(broken)):
        print("FAIL sanity probe: a removed master gate went unseen")
        return 1

    fails = check(files)
    for f in fails:
        print("FAIL", f)
    if fails:
        return 1
    print(f"PASS master switch gates every ExplosiveGrowth hook and entry point ({len(ENTRY_POINTS)} entry points; probe caught)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
