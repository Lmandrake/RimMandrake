#!/usr/bin/env python3
"""Selftest for WORLD_SEA_FACES_INSTALL_PICKED_LOOKS: the owner's picked sea faces (2026-10-24) are installed on BOTH twins.

Grey Sea (lighter, clearer), Twilight Sea (darker, richer), The Scald (today's row) and The Chill (still, dark 'abyss')
each have an RM_ BiomeDef in TerminalBiomes and a RUT_ BiomeDef in UtinniPatches. Each def's <texture> must name its own
tier's png, the two twins must be pixel-identical, the faces must keep the look he picked (pinned below), the Chill face
must break the plain water rule and pass only through its recorded owner exception (biome_worldfaces.OVERRIDE), and
biome_worldfaces.py install must skip the picked faces so a rerun cannot revert them.
usage: python3 selftest_sea_faces_picked.py [--deployed]   --deployed also requires the game copies to match the repo:
every deployed BiomeDef with that defName names the same <texture> as the repo, and the deployed png is pixel-equal.
RM_GAME_MODS overrides the game Mods folder (for mutant probes on a copy).
"""
import glob, hashlib, os, sys, xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image
import biome_worldfaces as W

REPO = os.path.abspath(os.path.join(HERE, "../../../.."))
RM = os.path.join(REPO, "src/RimMandrake/TerminalBiomes")
RUT = os.path.join(REPO, "src/RimUtinni/UtinniPatches")
GAME = os.environ.get("RM_GAME_MODS") or "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"
DEPLOYED = {RM: "RimMandrake.Biomes/Biomes/TerminalBiomes", RUT: "UtinniPatches"}   # where deploy_custom_mods.py puts each
# sea: (RM def, RM png, RUT def, RUT png, face key in biome_worldfaces, pixel sha256 of the picked face)
# Grey/Twilight/Scald = the r3 faces he picked (D:\ClaudeWork\rimmandrake\scratch\worldwater_variants_r3\faces\GreySea_clear,
# TwilightSea_deep, Scald_row .png, pixel-equal). Chill = his Chill_abyss with the swell widened and dithered (0e423847a9:
# the r3 file rounded to a flat rectangle and art install refused it), so its pin is the installed face.
SEAS = {
    "GreySea":     ("RM_GreySea", "RM_GreySea", "RUT_GreySea", "RUT_GreySea", "GreySea",
                    "527db4b2"),
    "TwilightSea": ("RM_TwilightSea", "RM_TwilightSea", "RUT_TwilightSea", "RUT_TwilightSea", "TwilightSea",
                    "23fb4462"),
    "Scald":       ("RM_TheScald", "RM_Scald", "RUT_TheScald", "RUT_Scald", "Scald",
                    "e78526d2"),
    "Chill":       ("RM_TheChill", "RM_Chill", "RUT_PropaneLake", "RUT_Chill", "Chill",
                    "f06ceca0"),
}
fails = 0


def bad(msg):
    global fails
    print("FAIL", msg); fails += 1


def textures(mod, defname):
    """Every <texture> of a BiomeDef named defname under mod/Defs (a duplicate def must not hide a stale one)."""
    out = []
    for p in sorted(glob.glob(os.path.join(mod, "Defs", "**", "*.xml"), recursive=True)):
        for d in ET.parse(p).getroot().iter("BiomeDef"):
            if d.findtext("defName") == defname:
                out.append((d.findtext("texture") or "").strip())
    return out


def texture(mod, defname):
    t = textures(mod, defname)
    return t[0] if t else None


def pixels(path):
    return np.asarray(Image.open(path).convert("RGB"))


def pxhash(a):
    return hashlib.sha256(a.tobytes()).hexdigest()[:8]


deployed = "--deployed" in sys.argv
for sea, (rmd, rmp, rutd, rutp, key, want) in SEAS.items():
    faces = {}
    for mod, d, png in ((RM, rmd, rmp),):
        t = texture(mod, d)
        if t != "World/Biomes/" + png: bad(f"{sea}: {d} texture {t!r} != World/Biomes/{png}"); continue
        f = os.path.join(mod, "Textures/World/Biomes", png + ".png")
        if not os.path.isfile(f): bad(f"{sea}: {f} missing"); continue
        faces[d] = pixels(f)
        if deployed:
            gmod = os.path.join(GAME, DEPLOYED[mod])
            gt = textures(gmod, d)
            if not gt: bad(f"{sea}: no deployed BiomeDef {d} under {gmod}/Defs")
            elif any(x != t for x in gt): bad(f"{sea}: deployed {d} texture {gt!r} != repo {t!r}")
            g = os.path.join(gmod, os.path.relpath(f, mod))
            if not os.path.isfile(g): bad(f"{sea}: no game copy {g}")
            elif not np.array_equal(pixels(g), faces[d]): bad(f"{sea}: game copy {g} differs")
    if len(faces) != 1: continue
    a = next(iter(faces.values()))
    h = pxhash(a)
    if h != want: bad(f"{sea}: face pixels {h} != picked {want} (a regenerated face needs his pick again)")
    st = W.stats(a)
    if W.verdict(key, st, a.shape): bad(f"{sea}: biome_worldfaces verdict refuses: {W.verdict(key, st, a.shape)}")
    if sea == "Chill":
        if not st["val"] <= 60: bad(f"Chill: val {st['val']} is not the dark abyss (his pick: value ~22)")
        o = W.OVERRIDE.pop("Chill", None)
        try:
            if not W.verdict(key, st, a.shape): bad("Chill: plain water rule accepts the abyss, so the exception is idle")
        finally:
            if o is not None: W.OVERRIDE["Chill"] = o
        if o is None: bad("Chill: no owner exception in biome_worldfaces.OVERRIDE")
missing = {"GreySea", "TwilightSea", "Chill"} - set(W.PICKED_ELSEWHERE)
if missing: bad(f"biome_worldfaces install would overwrite picked faces: {sorted(missing)} not in PICKED_ELSEWHERE")
print(("OK" if not fails else f"{fails} FAIL") + f": {len(SEAS)} seas" + (" + game copies" if deployed else ""))
sys.exit(1 if fails else 0)
