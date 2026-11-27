#!/usr/bin/env python3
"""Selftest for SEA_FILMS_FIX_SPHERE_ASSUMED_WHOLE: the sea films measure "a tile" from the tiles, and Set leaks nothing.

The need. RM_WorldLook.BuildSea fades its shore film over seaShoreTiles and its deep film over seaDeepTiles, both in
tile spacings, and the owner picked those widths on offline renders (FILMS['shelf'], 2026-10-24). Ash'karr is a
partial-coverage planet: 21,872 tiles, not an icosphere count (10*4^n+2), so 4 pi r^2 / TilesCount over-states one
tile spacing and every film in game came out narrower than the pick. RM_WorldDecals had the same defect and was fixed
by measuring the tile's own corners. And RM_WorldLook.Set (the bridge tuning door) forgot its cached Materials
without destroying them: one leaked Material per cache entry per call.

What this reads (the shipped source; constants are parsed, so it cannot drift):
  1. BuildSea's tileSpacing (in BuildSea, or in the BuildCoastField it calls) is computed from
     RM_WorldLook.TileSpacingOf over the water tiles, and no spacing expression there uses TilesCount.
  2. TileSpacingOf is 1.612 x the mean circumradius of the tile's own corners (sqrt(area) of a regular hex), and
     RM_WorldDecals takes its glyph spacing from the same function (one definition of a tile spacing).
  3. A tile spacing measured so, on a hand-made regular hex of circumradius R, equals sqrt(hex area) within 0.1 %
     (the 1.612 factor is the geometry, not a tuning).
  4. Set destroys every Material of BlendMats, FlatMats and SwirlMats before it clears them, and then marks every world
     layer dirty, so no built layer (the sea-floor layer included, which jawa/world_commit does not redraw) keeps
     drawing with a destroyed Material.
  5. The committed RimMandrake.Biomes.dll is built from these two files (.srchash).
Named mutants (the parent's sphere formula, a dropped Destroy, a dropped redraw, a wrong factor, a stale srchash) must each turn it red.

  python3 src/RimMandrake/Utils/art/selftest_sea_films_spacing.py            the shipped files
  python3 src/RimMandrake/Utils/art/selftest_sea_films_spacing.py --rev REV  the files at a git revision (red run)
"""
import hashlib, math, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../../.."))
LOOK = "src/RimMandrake/BiomesShell/Source/RM_WorldLook.cs"
DECALS = "src/RimMandrake/BiomesShell/Source/RM_WorldDecals.cs"
SRCHASH = "src/RimMandrake/BiomesShell/Assemblies/RimMandrake.Biomes.dll.srchash"


def body(text, signature_re):
    """The brace-matched body of the first method whose signature matches."""
    m = re.search(signature_re, text)
    if not m:
        return None
    i = text.index("{", m.end())
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
    return None


def check(look, decals, srchash, look_b, decals_b):
    errs = []
    sea = body(look, r"static string BuildSea\(")
    if sea is None:
        return ["BuildSea not found in RM_WorldLook.cs"]
    if "BuildCoastField(" in sea:
        # since SEABED_LAYER_DESIGN_ITS_OWN_SEA_FLOOR the coast field (spacing and distance) is shared with the floor view
        field = body(look, r"static CoastField BuildCoastField\(")
        if field is None:
            return ["BuildSea calls BuildCoastField, which is not found"]
        sea = sea + field
    for line in sea.splitlines():
        if re.search(r"\btileSpacing\s*=", line) and "TilesCount" in line:
            errs.append("BuildSea sizes a tile by TilesCount (the whole-sphere assumption): " + line.strip())
    if not re.search(r"TileSpacingOf\(\s*verts\s*,", sea):
        errs.append("BuildSea does not measure the water tiles with TileSpacingOf")
    if not re.search(r"float tileSpacing\s*=\s*spacingN\s*>\s*0\s*\?\s*spacingSum\s*/\s*spacingN", sea):
        errs.append("BuildSea's tileSpacing is not the mean TileSpacingOf of the water tiles")
    ts = body(look, r"public static float TileSpacingOf\(List<Vector3> verts, Vector3 center\)")
    if ts is None:
        errs.append("RM_WorldLook.TileSpacingOf(List<Vector3>, Vector3) not found")
    else:
        m = re.search(r"return\s+([0-9.]+)f\s*\*\s*circ\s*/\s*verts\.Count", ts)
        if not m or "(v - center).magnitude" not in ts:
            errs.append("TileSpacingOf is not <factor> x the mean corner distance")
        else:
            k = float(m.group(1))
            # a regular hex of circumradius R: area = 3 sqrt(3) / 2 R^2; spacing = sqrt(area)
            want = math.sqrt(3 * math.sqrt(3) / 2)
            if abs(k - want) / want > 0.001:
                errs.append("TileSpacingOf factor %.4f != sqrt(hex area)/R = %.4f" % (k, want))
    if "RM_WorldLook.TileSpacingOf(verts, center)" not in decals:
        errs.append("RM_WorldDecals does not take its tile spacing from RM_WorldLook.TileSpacingOf")
    st = body(look, r"public static string Set\(string key, string value\)")
    if st is None:
        errs.append("RM_WorldLook.Set not found")
    else:
        for cache in ("BlendMats", "FlatMats", "SwirlMats"):
            d = st.find("DestroyAll(%s.Values)" % cache)
            c = st.find("%s.Clear()" % cache)
            if d < 0 or (c >= 0 and d > c):
                errs.append("Set clears %s without destroying its Materials first (a leak per bridge tuning)" % cache)
        # a destroyed Material is still held by every submesh built with it: on the surface until the next redraw, and on
        # the sea-floor layer (RM_SeabedLayer) for good, because jawa/world_commit regenerates the surface layer only. So
        # Set must mark every world layer dirty after the destroy, as WriteSettings does for the floor toggle.
        last_destroy = max(st.rfind("DestroyAll(%s.Values)" % c) for c in ("BlendMats", "FlatMats", "SwirlMats"))
        dirty = st.find("SetAllLayersDirty()")
        if dirty < 0 or dirty < last_destroy:
            errs.append("Set destroys Materials that built layers still draw with, and marks no world layer dirty after "
                        "(the sea-floor layer keeps them until its next redraw)")
    da = body(look, r"static void DestroyAll\(IEnumerable<Material> mats\)")
    if da is None or "UnityEngine.Object.Destroy(m)" not in da:
        errs.append("DestroyAll does not Destroy each Material")
    for name, b in (("RM_WorldLook.cs", look_b), ("RM_WorldDecals.cs", decals_b)):
        line = [l for l in srchash.splitlines() if l.endswith(" " + name)]
        if not line:
            errs.append("srchash has no %s line" % name)
        elif line[0].split()[0] != hashlib.sha256(b).hexdigest():
            errs.append("RimMandrake.Biomes.dll is not built from this %s (srchash stale): run winbuild.py BiomesShell" % name)
    return errs


def read(rev, path):
    if rev:
        return subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (rev, path)], capture_output=True, check=True).stdout
    with open(os.path.join(REPO, path), "rb") as fh:
        return fh.read()


def main(argv):
    rev = argv[argv.index("--rev") + 1] if "--rev" in argv else None
    look_b, decals_b, sh_b = read(rev, LOOK), read(rev, DECALS), read(rev, SRCHASH)
    look, decals, sh = (b.decode("utf-8-sig") for b in (look_b, decals_b, sh_b))
    errs = check(look, decals, sh, look_b, decals_b)
    if not rev:
        sphere = "float tileSpacing = Mathf.Sqrt(4f * Mathf.PI * radius * radius / Mathf.Max(1, pl.TilesCount));"
        mean = "float tileSpacing = spacingN > 0 ? spacingSum / spacingN : 1f;"
        mutants = {
            "the parent's sphere formula": (look.replace(mean, sphere), decals),
            "FlatMats not destroyed": (look.replace("DestroyAll(FlatMats.Values);", ""), decals),
            "Set marks no layer dirty": (look.replace("Find.World?.renderer?.SetAllLayersDirty();", ""), decals),
            "wrong hex factor": (look.replace("return 1.612f * circ", "return 1.732f * circ"), decals),
            "decals keep their own copy": (look, decals.replace("RM_WorldLook.TileSpacingOf(verts, center)", "1.612f")),
        }
        for name, (lk, dc) in mutants.items():
            if (lk, dc) == (look, decals):
                errs.append("mutant '%s' did not apply (the source moved; update the mutant)" % name)
            elif not check(lk, dc, sh, look_b, decals_b):
                errs.append("mutant '%s' stayed green: the check is blind" % name)
        if not check(look, decals, sh, look_b + b"\n// edit", decals_b):
            errs.append("mutant 'stale srchash' stayed green: the check is blind")
    for e in errs:
        print("FAIL:", e)
    if errs:
        return 1
    print("OK sea films measure a tile from the water tiles (TileSpacingOf, shared with the decals); Set destroys its "
          "Materials and redraws every layer; DLL srchash matches; 6 mutants red")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
