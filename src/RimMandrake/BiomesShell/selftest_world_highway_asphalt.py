#!/usr/bin/env python3
"""Selftest for WORLD_HIGHWAY_TUNE_NAVY_IN_DISGUISE: the ancient highway reads as old asphalt, not as water.

The need (judge of the live8 shots, 2026-11-02): the highway fill (RM_WorldPaths.LayerColor "Gravel") rendered navy
under the planet light, so a road read as a river. The pale stripe kept it a road; the fill must not read blue.

The screen model. worldpaths/design.py fitted screen = 1-(1-c)^2.5 per channel on the day side (worldlook3 shots,
within ~5%). That model alone predicts the old fill (0.08,0.08,0.085) as neutral (48,48,49), but the live8 crop
measured (~48,56,80): the planet light adds a blue lift on dark paths. The lift is that measured difference,
(0, 8, 29) in 8-bit units. The same model and lift predict the stone road (0.18,0.15,0.12) as (100,93,99), which the
judge saw as neutral grey: the lift agrees with the second observation, so it is not fitted to the one being fixed.

What this reads (constants parsed from the C#, so it cannot drift):
  1. The highway fill, so rendered, is no bluer than the stone road that reads neutral: (B - R) <= the stone's + 3.
  2. It stays a dark asphalt: darker than the stone road and than the pale "Asphalt" stripe, so the tiers stay apart.
  3. The committed RimMandrake.Biomes.dll is built from this RM_WorldPaths.cs (.srchash).
Named mutants (the parent's navy fill, a stale srchash, a fill as pale as the stripe) must each turn it red.
What it does not read: the live picture. The in-game look is the judge's (WORLD_FACES / paths sheet route).

  python3 src/RimMandrake/BiomesShell/selftest_world_highway_asphalt.py            the shipped files
  python3 src/RimMandrake/BiomesShell/selftest_world_highway_asphalt.py --rev REV  the files at a git revision
"""
import hashlib, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../.."))
PATHS = "src/RimMandrake/BiomesShell/Source/RM_WorldPaths.cs"
SRCHASH = "src/RimMandrake/BiomesShell/Assemblies/RimMandrake.Biomes.dll.srchash"

P = 2.5                       # worldpaths/design.py screen model exponent
OLD_FILL = (0.08, 0.08, 0.085)
MEASURED_OLD = (48, 56, 80)   # live8 crop of the old fill, D:\ClaudeWork\rimmandrake\scratch\wpv\anvil_hwy.png
NEUTRAL_MARGIN = 3            # 8-bit units of blue over the stone road's own (B - R) still read neutral


def screen(c):
    return tuple(255.0 * (1 - (1 - x) ** P) for x in c)


LIFT = tuple(m - s for m, s in zip(MEASURED_OLD, screen(OLD_FILL)))


def rendered(c):
    return tuple(s + l for s, l in zip(screen(c), LIFT))


def colours(cs):
    out = {}
    for m in re.finditer(r'\{\s*"(\w+)",\s*new Color\(([0-9.]+)f,\s*([0-9.]+)f,\s*([0-9.]+)f\)\s*\}', cs):
        out[m.group(1)] = tuple(float(x) for x in m.groups()[1:])
    return out


def lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def check(cs, srchash, cs_b):
    errs = []
    col = colours(cs)
    for k in ("Gravel", "Stone", "Asphalt"):
        if k not in col:
            return ["LayerColor %s not found in RM_WorldPaths.cs" % k]
    hw, st, stripe = rendered(col["Gravel"]), rendered(col["Stone"]), rendered(col["Asphalt"])
    blue_hw, blue_st = hw[2] - hw[0], st[2] - st[0]
    if blue_hw > blue_st + NEUTRAL_MARGIN:
        errs.append("highway fill %s renders %s: %.0f more blue than red, the neutral stone road %.0f (navy, reads as water)"
                    % (col["Gravel"], tuple(round(x) for x in hw), blue_hw, blue_st))
    if not lum(hw) < lum(st):
        errs.append("highway fill renders no darker than the stone road: the tiers merge")
    if not lum(hw) < lum(stripe):
        errs.append("highway fill renders no darker than its pale Asphalt stripe: the stripe vanishes")
    line = [l for l in srchash.splitlines() if l.endswith(" RM_WorldPaths.cs")]
    if not line:
        errs.append("srchash has no RM_WorldPaths.cs line")
    elif line[0].split()[0] != hashlib.sha256(cs_b).hexdigest():
        errs.append("RimMandrake.Biomes.dll is not built from this RM_WorldPaths.cs (srchash stale): run winbuild.py BiomesShell")
    return errs


def read(rev, path):
    if rev:
        return subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (rev, path)], capture_output=True, check=True).stdout
    with open(os.path.join(REPO, path), "rb") as fh:
        return fh.read()


def main(argv):
    rev = argv[argv.index("--rev") + 1] if "--rev" in argv else None
    cs_b, sh_b = read(rev, PATHS), read(rev, SRCHASH)
    cs, sh = cs_b.decode("utf-8-sig"), sh_b.decode("utf-8")
    errs = check(cs, sh, cs_b)
    stone = rendered(colours(cs).get("Stone", (0, 0, 0)))
    if abs((stone[2] - stone[0])) > 10:
        errs.append("the lift no longer predicts the stone road as neutral (%s): the light model is stale"
                    % (tuple(round(x) for x in stone),))
    if not rev:
        g = re.search(r'\{\s*"Gravel",\s*new Color\([^)]*\)\s*\}', cs).group(0)
        mutants = {
            "the parent's navy fill": cs.replace(g, '{ "Gravel",  new Color(0.08f, 0.08f, 0.085f) }'),
            "fill as pale as the stripe": cs.replace(g, '{ "Gravel",  new Color(0.42f, 0.41f, 0.38f) }'),
        }
        for name, m in mutants.items():
            if m == cs:
                errs.append("mutant '%s' did not apply (the source moved; update the mutant)" % name)
            elif not check(m, sh, cs_b):
                errs.append("mutant '%s' stayed green: the check is blind" % name)
        if not check(cs, sh, cs_b + b"\n// edit"):
            errs.append("mutant 'stale srchash' stayed green: the check is blind")
    for e in errs:
        print("FAIL:", e)
    if errs:
        return 1
    hw = rendered(colours(cs)["Gravel"])
    print("OK highway fill renders %s (stone road %s): asphalt, not water; DLL srchash matches; 3 mutants red"
          % (tuple(round(x) for x in hw), tuple(round(x) for x in stone)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
