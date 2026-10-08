#!/usr/bin/env python3
"""Offline lint of Colony Visibility (mandrake.rm.visibility), a C#-only mod with no Defs: the generic lint (lint_mod_defs.py, settings
Scribe/default/slider/dead-toggle checks) plus structure checks it cannot see.

  vis-kernel    the kernel is Verse-free; its season length is GenDate's 900000 and its launch floor/ceiling are the 5 / 15 the settings
                text promises; the curve nodes are strictly ascending in x and non-decreasing in y; the 0..2 strength slider can never drive
                the factor to 0 or below at the curve's lowest point
  vis-wiring    the mod's own files call the kernel for every rule (no second copy of the clamp, the decay or the band ladder survives
                beside it), and the csproj keeps SelfTest out of the mod assembly
  vis-about     About.xml packageId is mandrake.rm.visibility and depends on Harmony (every patch is Harmony)

    python3 src/RimMandrake/Utils/lint_visibility_defs.py [--quiet] [--mod-dir D]
"""
import contextlib
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_mod_defs  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DEFAULT_MOD = os.path.join(REPO, "src", "RimMandrake", "Visibility")


def read(p):
    return open(p, encoding="utf-8-sig").read()


def main(argv):
    quiet = "--quiet" in argv
    mod = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else DEFAULT_MOD
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lint_mod_defs.run("Visibility", ["--mod-dir", mod], require_xml=False)
    gl = buf.getvalue().splitlines()
    if rc == 2:
        print("\n".join(gl))
        return 2
    errs = [l for l in gl if l.startswith("ERROR")]
    warns = [l for l in gl if l.startswith("WARN")]
    E = lambda c, m: errs.append(f"ERROR {c}: {m}")
    src = os.path.join(mod, "Source")
    kernel = read(os.path.join(src, "Kernel", "RM_VisibilityKernel.cs"))
    gc = read(os.path.join(src, "GameComponent_ColonyVisibility.cs"))
    settings = read(os.path.join(src, "RM_VisibilityMod.cs"))
    raid = read(os.path.join(src, "ColonyVisibilityRaidPatch.cs"))
    n = {"kernel consts": 0, "calls": 0}

    if re.search(r"^\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)", kernel, flags=re.M):
        E("vis-kernel", "the kernel imports Verse/RimWorld/UnityEngine/HarmonyLib (the fuzz build would break)")
    m = re.search(r"public const int TicksPerSeason = (\d+);", kernel)
    n["kernel consts"] += 1
    if not m or m.group(1) != "900000":
        E("vis-kernel", f"kernel TicksPerSeason is {m.group(1) if m else '(missing)'}, GenDate.TicksPerSeason is 900000")
    fl = re.search(r"LaunchFloor = ([0-9.]+)f", kernel)
    ce = re.search(r"LaunchCeiling = ([0-9.]+)f", kernel)
    n["kernel consts"] += 2
    if not fl or not ce or (fl.group(1), ce.group(1)) != ("5", "15") and (float(fl.group(1)), float(ce.group(1))) != (5.0, 15.0):
        E("vis-kernel", f"launch floor/ceiling {fl.group(1) if fl else None}/{ce.group(1) if ce else None} are not the 5/15 the settings text promises")
    if "floor 5, ceiling 15" not in settings:
        E("vis-kernel", "the settings text no longer states the launch floor 5 / ceiling 15 the kernel enforces")
    xs = [float(x) for x in re.findall(r"[0-9.]+(?=f)", re.search(r"CurveX = \{([^}]*)\}", kernel).group(1))] if "CurveX" in kernel else []
    ys = [float(x) for x in re.findall(r"[0-9.]+(?=f)", re.search(r"CurveY = \{([^}]*)\}", kernel).group(1))] if "CurveY" in kernel else []
    n["kernel consts"] += 2
    if len(xs) < 2 or len(xs) != len(ys) or any(b <= a for a, b in zip(xs, xs[1:])) or any(b < a for a, b in zip(ys, ys[1:])):
        E("vis-kernel", f"threat curve nodes x={xs} y={ys} are not strictly ascending in x / non-decreasing in y")
    elif ys and 1 + (min(ys) - 1) * 2 <= 0:
        E("vis-kernel", f"the lowest curve point {min(ys)} at the 2x strength slider limit drives the factor to {1 + (min(ys) - 1) * 2}")
    sm = re.search(r"raidScalingStrength = list\.Slider\(raidScalingStrength, ([0-9.]+)f, ([0-9.]+)f\)", settings)
    if not sm or float(sm.group(2)) > 2.0:
        E("vis-kernel", f"strength slider {sm.groups() if sm else None} may exceed 2x, past the range the factor stays positive for")

    # vis-wiring: the mod calls the kernel; no hand copy of a rule survives
    for fn in ("BandFor", "ThreatFactor", "ScaledThreatFactor", "Adjust", "ResetOnLaunch", "SeasonsAway", "DecayedTileVisibility", "RestoreDelta", "ScalePoints"):
        n["calls"] += 1
        if f"RM_VisibilityKernel.{fn}(" not in (gc + settings + raid):
            E("vis-wiring", f"nothing in the mod calls RM_VisibilityKernel.{fn} (the rule was re-declared or dropped; the fuzz tests a function the mod does not run)")
    for pat, what in ((r"Mathf\.Clamp\(shipVisibility", "a hand copy of the dial clamp"), (r"Mathf\.Pow\(0\.5f", "a hand copy of the memory decay"),
                      (r"if \(v < 20f\)", "a hand copy of the band ladder"), (r"new SimpleCurve", "a second threat curve"),
                      (r"Mathf\.Clamp\(parms\.points", "a hand copy of the point clamp")):
        if re.search(pat, gc + settings + raid):
            E("vis-wiring", f"{what} survives in the mod beside the kernel")
    csproj = read(os.path.join(src, "Visibility.csproj"))
    if 'Compile Remove="SelfTest/**/*.cs"' not in csproj:
        E("vis-wiring", "the csproj does not keep Source/SelfTest (two Main entry points, the fuzz) out of the mod assembly")

    ab = read(os.path.join(mod, "About", "About.xml"))
    if "<packageId>mandrake.rm.visibility</packageId>" not in ab:
        E("vis-about", "About.xml packageId is not mandrake.rm.visibility")
    if "brrainz.harmony" not in ab:
        E("vis-about", "About.xml does not depend on Harmony although every hook is a Harmony patch")

    if not quiet:
        for l in warns:
            print(l)
    for l in errs:
        print(l)
    print(f"visibility lint (data): {n['kernel consts']} kernel constants, {n['calls']} kernel call sites, {len(errs)} ERROR, {len(warns)} WARN")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
