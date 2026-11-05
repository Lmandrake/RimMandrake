#!/usr/bin/env python3
"""Live, read-only proof of the biome decals (WORLD_DECALS_BUILD_ATLAS_PIPELINE_ONCE, clause A1); the judge reads the
decal MATERIAL colour back, not only the remembered fade value.

Needs: RimMandrake.Biomes (BiomesShell + BlueDesert members) deployed at the proof sha, a world loaded (Playing) with
the world view shown, the bridge up with jawa/static_call. Reads only (RM_WorldDecals.Probe and .Info, both reviewed
READ_ONLY_STATIC_CALLS). PASS when:
  1. the shipped test atlas is found and read as the contract says (RM_BlueDesert 512x512, grid=2);
  2. the planet was built with decals on ("decals: N glyphs on M flat tiles ..."; N may be 0: a biome of ours on 0
     tiles is expected, owner 2026-09-20) and enabled=True;
  3. the fade alpha in force (alpha=) equals the C# rule for the camera altitude in force (full <= decalFullAlt, gone
     >= decalGoneAlt, smoothstep between); alpha -1 with glyphs built is a dead fade (FAIL); alpha -1 after a build
     that met land biomes but drew none is UNMEASURED (show the world view), never PASS;
  4. Info reports matAlpha= , the colour alpha of a live decal material (-1 when no decal material exists), and when a
     biome with an atlas is on the planet that alpha equals the rule too: the per-frame fade reaches the material the
     glyphs draw with. An Info without matAlpha FAILS: the material fade is then invisible to the live game proof.
     With no biome with an atlas on the planet there is no decal material to read: UNMEASURED, never PASS.
Exit 0 PASS, 1 FAIL, 2 UNMEASURED (no bridge / no world / nothing to read).

    python3 src/RimMandrake/BiomesShell/prove_world_decals_live.py            # live
    python3 src/RimMandrake/BiomesShell/prove_world_decals_live.py --selftest # the judge on recorded Info strings, offline
"""
import json, os, re, sys

T = "RimMandrake.Biomes.RM_WorldDecals"
PROBE_OK = "atlas RM_BlueDesert 512x512 grid=2"
BUILT = re.compile(r"decals: (\d+) glyphs on (\d+) flat tiles of (\d+) biomes with an atlas \((\d+) land biomes without one\)")


def fade(alt, full, gone):
    """Mirror of RM_WorldDecals.FadeAlpha (the selftest pins the C# against this rule)."""
    if gone <= full:
        return 1.0 if alt <= full else 0.0
    t = min(1.0, max(0.0, (alt - full) / (gone - full)))
    return 1.0 - t * t * (3 - 2 * t)


def num(info, key):
    m = re.search(r"(?:^|[\s|])" + key + r"=(-?[\d.]+(?:[Ee][+-]?\d+)?)", info)
    return None if m is None else float(m.group(1))


def judge(probe, info):
    """-> (exit code, verdict line) for one Probe result and one Info result (both the raw bridge JSON or string)."""
    errs, unmeasured = [], []
    if PROBE_OK not in probe:
        errs.append("test atlas not found or not read as a 2x2 atlas (probe: %s)" % probe[:120])
    m = BUILT.search(info)
    if not m:
        errs.append("planet not built with decals (lastInfo: %s)" % info[:120])
    if "enabled=True" not in info:
        errs.append("setting Planet: biome decals is off")
    alt, alpha, full, gone = (num(info, k) for k in ("altitude", "alpha", "fullAlt", "goneAlt"))
    mat = num(info, "matAlpha")
    if None in (alt, alpha, full, gone):
        errs.append("Info lacks altitude/alpha/fullAlt/goneAlt")
    else:
        rule = fade(alt, full, gone)
        glyphs = int(m.group(1)) if m else 0
        atlased = int(m.group(3)) if m else 0
        met = atlased + int(m.group(4)) if m else 0
        if alpha < 0 and glyphs > 0:
            errs.append("glyphs built but the fade never ran (alpha -1)")
        elif alpha < 0 and met > 0:
            unmeasured.append("fade has not run since the build (alpha -1 with %d biomes met); show the world view" % met)
        elif alpha >= 0 and abs(alpha - rule) > 0.01:
            errs.append("alpha %.3f at altitude %.0f, the rule says %.3f (fade not running)" % (alpha, alt, rule))
        if mat is None:
            errs.append("Info does not report matAlpha (the decal material colour alpha): the per-frame material fade "
                        "is invisible to the live proof")
        elif atlased > 0 or glyphs > 0:
            if mat < 0:
                errs.append("a biome with an atlas is on the planet but no decal material reports a colour (matAlpha -1)")
            elif alpha >= 0 and abs(mat - rule) > 0.01:
                errs.append("material colour alpha %.3f at altitude %.0f, the rule says %.3f (the fade does not reach "
                            "the material)" % (mat, alt, rule))
        elif m:
            unmeasured.append("no biome with an atlas on this planet, so no decal material to read")
    if errs:
        return 1, "FAIL: " + "; ".join(errs)
    if unmeasured:
        return 2, "UNMEASURED: " + "; ".join(unmeasured)
    return 0, "PASS"


def live():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Utils"))
    from live_def_check import _bridge

    def call(method, args):
        r, why = _bridge("jawa/static_call", {"type": T, "method": method, "args": args}, 60, read_only_static=True)
        return None if r is None else json.dumps(r), why

    probe, why = call("Probe", "RM_BlueDesert")
    if probe is None:
        print("UNMEASURED: " + why); return 2
    info, why = call("Info", "")
    if info is None:
        print("UNMEASURED: " + why); return 2
    print("probe:", probe[:200])
    print("info:", info[:500])
    code, line = judge(probe, info)
    print(line)
    return code


# ---------------------------------------------------------------- offline: the judge on recorded strings
P = "atlas RM_BlueDesert 512x512 grid=2"
TAIL = " | size=0.3 spread=0.22 lift=0.0045 queue=3507 fullAlt=380 goneAlt=620 flipX=False"


def _info(built, alpha, alt, mat=None, enabled=True):
    s = built + " | enabled=%s alpha=%s altitude=%s atlases=1" % (enabled, alpha, alt)
    return s + TAIL + ("" if mat is None else " matAlpha=%s" % mat)


B1 = "decals: 120 glyphs on 48 flat tiles of 1 biomes with an atlas (13 land biomes without one), 4 ms"
B0 = "decals: 0 glyphs on 0 flat tiles of 0 biomes with an atlas (14 land biomes without one), 3 ms"
CASES = [   # (name, probe, info, wanted exit)
    ("close zoom, material at full", P, _info(B1, 1, 300, 1), 0),
    ("far zoom, material gone", P, _info(B1, 0, 900, 0), 0),
    ("mid zoom, material on the smoothstep", P, _info(B1, round(fade(500, 380, 620), 4), 500, round(fade(500, 380, 620), 4)), 0),
    # the checker's gaps, as Info would read under each mutant
    ("current Info: no matAlpha", P, _info(B1, 1, 300), 1),
    ("colour ignores fade (alpha 1f into the material)", P, _info(B1, 0, 900, 1), 1),
    ("fade forgotten on the material", P, _info(B1, 0.5, 500, 1), 1),
    ("material never made though an atlas biome is on the planet", P, _info(B1, 1, 300, -1), 1),
    ("fade guard always true (glyphs, alpha -1)", P, _info(B1, -1, 300, 1), 1),
    ("fade not from altitude", P, _info(B1, 1, 900, 1), 1),
    ("never built", P, _info("never built", -1, 0, -1), 1),
    ("decals off", P, _info(B1, 1, 300, 1, enabled=False), 1),
    ("atlas missing", "atlas RM_BlueDesert none", _info(B1, 1, 300, 1), 1),
    ("atlas misread", "atlas RM_BlueDesert 512x512 grid=4", _info(B1, 1, 300, 1), 1),
    # what cannot be read is never a PASS
    ("0 glyphs, no atlas biome on the planet (expected today)", P, _info(B0, 1, 300, -1), 2),
    ("0 glyphs, fade not yet run (map view)", P, _info(B0, -1, 0, -1), 2),
]


def selftest():
    bad = 0
    for name, probe, info, want in CASES:
        got, line = judge(json.dumps({"result": probe}), json.dumps({"result": info}))
        ok = got == want
        bad += not ok
        print(("ok  " if ok else "FAIL") + " %-62s exit %d (want %d)  %s" % (name, got, want, line[:110]))
    # the C# must give the judge something to read: Info() emits matAlpha= from a decal material's colour
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Source", "RM_WorldDecals.cs"), encoding="utf-8").read()
    body = re.search(r"public static string Info\(\)\s*\{(.*?)\n        \}", src, re.S)
    emits = bool(body) and '" matAlpha="' in body.group(1) and ".color.a" in body.group(1)
    bad += not emits
    print(("ok  " if emits else "FAIL") + " RM_WorldDecals.Info() emits matAlpha= read from a decal material's color.a"
          + ("" if emits else ": it does not, so the live A1 judge FAILs on today's build"))
    print("RESULT %s: %d judge cases + Info source, %d wrong" % ("PASS" if not bad else "FAIL", len(CASES), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv[1:] else live())
