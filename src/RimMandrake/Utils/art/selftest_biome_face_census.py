#!/usr/bin/env python3
"""Selftest for biome_face_census.py: the census catches a vanilla face, a donor path, a legacy file name, two biomes
sharing one picture and a texture patch on a fixture tree, then reads the real src/ as all owned."""
import os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import biome_face_census as C

DEF = '<Defs>{}</Defs>'
B = '<BiomeDef><defName>{}</defName><texture>{}</texture></BiomeDef>'
fails = 0


def check(got, want, what):
    global fails
    if got != want: print(f"FAIL {what}: {got} != {want}"); fails += 1


with tempfile.TemporaryDirectory() as t:
    def png(mod, name, body=b"x"):
        d = os.path.join(t, mod, "Textures/World/Biomes"); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, name + ".png"), "wb").write(body)
    os.makedirs(os.path.join(t, "A/Defs/BiomeDefs")); os.makedirs(os.path.join(t, "A/Patches"))
    png("A", "RM_Own", b"own"); png("A", "RM_Twin", b"twin"); png("A", "RUT_Twin", b"twin"); png("A", "Old", b"old")
    png("A", "RM_One", b"same"); png("A", "RM_Two", b"same")
    xml = "".join(B.format(n, "World/Biomes/" + x) for n, x in (
        ("RM_Own", "RM_Own"), ("RM_Twin", "RM_Twin"), ("RUT_Twin", "RUT_Twin"), ("RM_Legacy", "Old"),
        ("RM_Vanilla", "Ocean"), ("RM_One", "RM_One"), ("RM_Two", "RM_Two")))
    xml += '<BiomeDef Name="Base" Abstract="True"><texture>World/Biomes/RM_Own</texture></BiomeDef>'
    xml += '<BiomeDef ParentName="Base"><defName>RM_Kid</defName></BiomeDef>'
    open(os.path.join(t, "A/Defs/BiomeDefs/b.xml"), "w").write(DEF.format(xml))
    open(os.path.join(t, "A/Patches/p.xml"), "w").write('<Patch><Operation><xpath>Defs/BiomeDef[defName="Ocean"]/texture</xpath></Operation></Patch>')
    rows, bad = C.census(t)
    v = {r[0]: r[2] for r in rows}
    check(v, {"RM_Own": "OWNED", "RM_Twin": "OWNED", "RUT_Twin": "OWNED", "RM_Legacy": "LEGACY_NAME", "RM_Vanilla": "NOT_OURS",
              "RM_One": "OWNED", "RM_Two": "OWNED", "RM_Kid": "OWNED"}, "verdicts")
    kinds = sorted(b.split()[0] for b in bad)
    check(kinds, ["LEGACY_NAME", "NOT_OURS", "PATCHED", "SHARED"], "findings")

import numpy as np
import world_beauty_render as R
pts = R.to_xyz(np.random.default_rng(1).uniform(-85, 85, 400), np.random.default_rng(2).uniform(-180, 180, 400))
tiles = R.to_xyz(np.random.default_rng(3).uniform(-90, 90, 4000), np.random.default_rng(4).uniform(-180, 180, 4000))
brute = np.argsort(np.linalg.norm(pts[:, None] - tiles[None], axis=2), axis=1)[:, :3]
check(int((R.Nearest(tiles, cell=0.3).query(pts)[1] != brute).sum()), 0, "beauty render Nearest vs brute force")

x = subprocess.run([sys.executable, C.__file__], capture_output=True, text=True)
print(x.stdout.strip().splitlines()[-1])
if x.returncode: print(x.stdout); fails += 1
print(f"{'PASS' if not fails else 'FAIL'} biome_face_census: {fails} failures")
sys.exit(1 if fails else 0)
