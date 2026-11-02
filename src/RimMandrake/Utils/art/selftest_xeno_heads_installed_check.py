#!/usr/bin/env python3
"""Selftest: xeno_heads_installed_check.py passes only shots taken of the art deployed NOW.

Gen-2 blind fail of XENO_HEADS_SCENE_PROVE_ALIENS_WEAR_THEM: shots from before the head refit passed a bare
existence check. Builds a fake game mod (repo copy of the 3 def files and the head PNGs), a fake Screenshots
folder and a manifest, then: all good -> 0; a shot older than the art -> 1; manifest art hash stale -> 1;
manifest headType wrong -> 1; manifest missing -> 1.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "xeno_heads_installed_check.py")
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
MOD = os.path.join(REPO, "src", "RimStarWars", "StarWarsRaces")
DEFS = ("Defs/HeadTypeDefs/SW_HeadTypes.xml", "Defs/GeneDefs/SW_Genes.xml", "Defs/XenotypeDefs/RimMandrakeXenotypes.xml")
SPECIES = ("Lasat", "Mimbanese", "Nelvaanian", "Ortolan")
SHOTS = [f"xeno_heads_v3{g}_{f}.png" for g in "AB" for f in ("south", "east", "north", "west")]


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def build(root):
    game = os.path.join(root, "Mods", "StarWarsRaces")
    for rel in DEFS:
        os.makedirs(os.path.dirname(os.path.join(game, rel)), exist_ok=True)
        shutil.copy(os.path.join(MOD, rel), os.path.join(game, rel))
    heads = {}
    for s in SPECIES:
        rel = f"Textures/RimMandrakeSW/Heads/{s}"
        shutil.copytree(os.path.join(MOD, rel), os.path.join(game, rel))
        for n in os.listdir(os.path.join(game, rel)):
            os.utime(os.path.join(game, rel, n), (time.time() - 3600,) * 2)
            heads[f"{rel}/{n}"] = sha(os.path.join(game, rel, n))
    shots_dir = os.path.join(root, "Shots")
    os.makedirs(shots_dir)
    shots = {}
    for i, n in enumerate(SHOTS):
        with open(os.path.join(shots_dir, n), "wb") as fh:
            fh.write(b"PNG%d" % i)
        shots[n] = sha(os.path.join(shots_dir, n))
    man = {"pawns": {s: {"headType": f"RSW_{s}_Head"} for s in SPECIES}, "shots": shots,
           "head_pngs": heads, "failures": []}
    return game, shots_dir, man


def run(root, man):
    mpath = os.path.join(root, "manifest.json")
    if man is None:
        if os.path.exists(mpath):
            os.remove(mpath)
    else:
        with open(mpath, "w") as fh:
            json.dump(man, fh)
    env = dict(os.environ, RM_GAME_MODS=os.path.join(root, "Mods"), RM_GAME_SCREENSHOTS=os.path.join(root, "Shots"),
               RM_XENO_MANIFEST=mpath)
    r = subprocess.run([sys.executable, CHECK], env=env, capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout


def main():
    bad = []
    with tempfile.TemporaryDirectory() as root:
        game, shots_dir, man = build(root)
        code, out = run(root, man)
        if code != 0:
            bad.append(f"good fixture should pass, got {code}: {out[-400:]}")
        m = json.loads(json.dumps(man))
        m["pawns"]["Ortolan"]["headType"] = "Male_AverageNormal"
        code, out = run(root, m)
        if code != 1 or "Ortolan: the shot pawn drew" not in out:
            bad.append(f"wrong headType should fail, got {code}")
        m = json.loads(json.dumps(man))
        m["head_pngs"][next(iter(m["head_pngs"]))] = "0" * 64
        code, out = run(root, m)
        if code != 1 or "does not record the deployed art" not in out:
            bad.append(f"stale art hash should fail, got {code}")
        code, out = run(root, None)
        if code != 1 or "manifest unreadable" not in out:
            bad.append(f"missing manifest should fail, got {code}")
        old = time.time() - 7200
        os.utime(os.path.join(shots_dir, SHOTS[0]), (old, old))
        code, out = run(root, man)
        if code != 1 or "predates the deployed head art" not in out:
            bad.append(f"shot older than the art should fail, got {code}")
    for b in bad:
        print("FAIL", b)
    print("PASS selftest_xeno_heads_installed_check" if not bad else f"FAIL {len(bad)} case(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
