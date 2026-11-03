#!/usr/bin/env python3
"""Live, read-only proof of the biome decals (WORLD_DECALS_BUILD_ATLAS_PIPELINE_ONCE, clause A1).

Needs: RimMandrake.Biomes (BiomesShell + BlueDesert members) deployed at the proof sha, a world loaded (Playing), the
bridge up with jawa/static_call. Reads only (two reviewed READ_ONLY_STATIC_CALLS). PASS when:
  1. the shipped test atlas is found and read as the contract says (RM_BlueDesert 512x512, grid=2);
  2. the planet was built with decals on ("decals: N glyphs on M flat tiles ..."; N may be 0 when no biome with an atlas
     is on today's map: a biome of ours on 0 tiles is expected, owner 2026-09-20);
  3. the fade alpha in force equals the C# rule for the camera altitude in force (full <= decalFullAlt, gone >=
     decalGoneAlt, smoothstep between), so the per-frame fade is running.
Exit 0 PASS, 1 FAIL, 2 UNMEASURED (no bridge / no world).

    python3 src/RimMandrake/BiomesShell/live_world_decals.py
"""
import json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Utils"))
from live_def_check import _bridge   # noqa: E402

T = "RimMandrake.Biomes.RM_WorldDecals"


def call(method, args):
    r, why = _bridge("jawa/static_call", {"type": T, "method": method, "args": args}, 60, read_only_static=True)
    return None if r is None else json.dumps(r), why


def fade(alt, full, gone):
    if gone <= full:
        return 1.0 if alt <= full else 0.0
    t = min(1.0, max(0.0, (alt - full) / (gone - full)))
    return 1.0 - t * t * (3 - 2 * t)


def main():
    probe, why = call("Probe", "RM_BlueDesert")
    if probe is None:
        print("UNMEASURED: " + why); return 2
    info, why = call("Info", "")
    if info is None:
        print("UNMEASURED: " + why); return 2
    print("probe:", re.search(r"atlas [^\"]*", probe).group(0) if "atlas" in probe else probe[:200])
    print("info:", info[:400])
    errs = []
    if "atlas RM_BlueDesert 512x512 grid=2" not in probe:
        errs.append("test atlas not found or not read as a 2x2 atlas")
    m = re.search(r"decals: (\d+) glyphs on (\d+) flat tiles", info)
    if not m:
        errs.append("planet not built with decals (lastInfo: %s)" % info[:120])
    if "enabled=True" not in info:
        errs.append("setting Planet: biome decals is off")
    g = lambda k: float(re.search(k + r"=(-?[\d.E+-]+)", info).group(1))
    try:
        alt, alpha, full, gone = g("altitude"), g("alpha"), g("fullAlt"), g("goneAlt")
    except AttributeError:
        errs.append("Info lacks altitude/alpha"); alt = alpha = full = gone = None
    if alt is not None:
        if alpha < 0 and m and int(m.group(1)) > 0:
            errs.append("glyphs built but the fade never ran (alpha -1)")
        elif alpha >= 0 and abs(alpha - fade(alt, full, gone)) > 0.01:
            errs.append("alpha %.3f at altitude %.0f, the rule says %.3f (fade not running)" % (alpha, alt, fade(alt, full, gone)))
    print(("PASS" if not errs else "FAIL: " + "; ".join(errs)))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
