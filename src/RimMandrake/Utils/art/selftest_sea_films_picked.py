#!/usr/bin/env python3
"""Selftest for WORLD_WATER_REDRAW_SEAS_THAT_READ_DEEP: the sea-film defaults ship the owner's pick.

Owner, 2026-10-24 (round 2, "Others confirm"): the "wider shelf" films the sheet showed as the working default. The
numbers live in world_water_variants.FILMS["shelf"] (the generator that rendered the sheet he judged); RM_WorldLook's
public statics (seaShoreColor/Alpha/Tiles, seaDeepColor/Alpha/Tiles) must equal them, and the committed
RimMandrake.Biomes.dll must be built from that source (its .srchash line for RM_WorldLook.cs = sha256 of the file).
A mutant pass (a shelf value nudged, a stale srchash) must turn the check red, so the test can see.
"""
import ast, hashlib, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../../.."))
CS = os.path.join(REPO, "src/RimMandrake/BiomesShell/Source/RM_WorldLook.cs")
SRCHASH = os.path.join(REPO, "src/RimMandrake/BiomesShell/Assemblies/RimMandrake.Biomes.dll.srchash")
GEN = os.path.join(HERE, "world_water_variants.py")


def shelf_films(gen_text):
    """FILMS['shelf'] read by AST (no import: the generator pulls numpy/PIL and the face pipeline)."""
    for node in ast.parse(gen_text).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "FILMS" for t in node.targets):
            films = ast.literal_eval(node.value)
            return films["shelf"]
    raise SystemExit("FAIL: FILMS not found in world_water_variants.py")


def cs_statics(cs_text):
    out = {}
    for m in re.finditer(r'public static (float|string) (sea(?:Shore|Deep)(?:Color|Alpha|Tiles)) = ([^;]+);', cs_text):
        kind, name, val = m.groups()
        out[name] = tuple(float(x) for x in val.strip('"').split(",")) if kind == "string" else float(val.rstrip("f"))
    return out


def check(gen_text, cs_text, srchash_text, cs_bytes):
    errs = []
    shelf = shelf_films(gen_text)
    got = cs_statics(cs_text)
    for film, key in (("shore", "seaShore"), ("deep", "seaDeep")):
        col, alpha, tiles = shelf[film]
        want = {key + "Color": tuple(col), key + "Alpha": alpha, key + "Tiles": tiles}
        for k, v in want.items():
            g = got.get(k)
            if g is None:
                errs.append(f"{k}: not found in RM_WorldLook.cs")
            elif (tuple(round(x, 4) for x in g) if isinstance(g, tuple) else round(g, 4)) != \
                    (tuple(round(x, 4) for x in v) if isinstance(v, tuple) else round(v, 4)):
                errs.append(f"{k}: RM_WorldLook.cs={g} but the pick (FILMS['shelf']) = {v}")
    sha = hashlib.sha256(cs_bytes).hexdigest()
    line = [l for l in srchash_text.splitlines() if l.endswith(" RM_WorldLook.cs")]
    if not line:
        errs.append("srchash has no RM_WorldLook.cs line")
    elif line[0].split()[0] != sha:
        errs.append("RimMandrake.Biomes.dll is not built from this RM_WorldLook.cs (srchash stale): run winbuild.py")
    return errs


def main():
    gen = open(GEN).read()
    cs_b = open(CS, "rb").read()
    cs = cs_b.decode("utf-8-sig")
    sh = open(SRCHASH).read()
    errs = check(gen, cs, sh, cs_b)
    # mutants: each must go red, or the check is blind
    mutants = {
        "shore alpha nudged": (gen, cs.replace("seaShoreAlpha = 0.45f", "seaShoreAlpha = 0.40f"), sh, cs_b),
        "deep tiles nudged": (gen, cs.replace("seaDeepTiles = 6f", "seaDeepTiles = 4f"), sh, cs_b),
        "pick changed": (gen.replace('"deep": ((0.05, 0.09, 0.20), 0.62, 6.0)', '"deep": ((0.05, 0.09, 0.20), 0.70, 6.0)'),
                         cs, sh, cs_b),
        "stale srchash": (gen, cs, sh, cs_b + b"\n// edit"),
    }
    for name, args in mutants.items():
        if args[:2] == (gen, cs) and args[3] == cs_b:
            errs.append(f"mutant '{name}' did not apply (the source text moved; update the mutant)")
        elif not check(*args):
            errs.append(f"mutant '{name}' stayed green: the check is blind")
    for e in errs:
        print("FAIL:", e)
    if errs:
        return 1
    s = shelf_films(gen)
    print(f"OK sea films = the pick: shore {s['shore'][1]} over {s['shore'][2]} tiles, deep {s['deep'][1]} over "
          f"{s['deep'][2]} tiles; DLL srchash matches RM_WorldLook.cs; {len(mutants)} mutants red")
    return 0


if __name__ == "__main__":
    sys.exit(main())
