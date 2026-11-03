#!/usr/bin/env python3
"""Offline proof that the four painted xeno heads are installed and were shot live.

Item XENO_HEADS_SCENE_PROVE_ALIENS_WEAR_THEM. For Lasat, Mimbanese, Nelvaanian and Ortolan:
  - the HeadTypeDef RSW_<S>_Head exists, requires gene RSW_<S>Head;
  - GeneDef RSW_<S>Head exists and xenotype RSW_RimMandrake<S> lists it;
  - the 3 facing PNGs exist (plus the all-black _m masks when the head uses CutoutComplex);
  - the deployed game copy matches the repo: the HeadTypeDef and GeneDef whole (as parsed XML),
    the xenotype's gene list (its other fields, e.g. nameMaker, do not decide the head), every PNG
    byte for byte. Unrelated undeployed edits elsewhere in the same def files do not count;
  - the live line-up screenshots (fresh pawns of the four species, 4 facings) exist, each NEWER than every
    deployed head PNG, and the manifest written by xeno_heads_live_shot.py beside the run records the same
    sha256 for every deployed head PNG and every shot as today, and each species drawing RSW_<S>_Head.
    (Gen-2 blind fail: the 2026-10-20 08:24 shots predated the 17:39-18:04 head refit, and a bare
    existence check passed them.)
Exit 0 = all hold, 1 = a check failed (each failure printed), 2 = an instrument could not see.
"""
import hashlib
import json
import os
import sys
import xml.etree.ElementTree as ET

SPECIES = ("Lasat", "Mimbanese", "Nelvaanian", "Ortolan")
FACINGS = ("south", "east", "north")
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
MOD_REL = os.path.join("src", "RimStarWars", "StarWarsRaces")
GAME_MOD = os.environ.get(
    "RM_GAME_MODS", "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods") + "/StarWarsRaces"
import sys as _sys; _sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game_paths import LOCALLOW  # noqa: E402
SHOTS = os.environ.get(
    "RM_GAME_SCREENSHOTS",
    LOCALLOW + "/Screenshots")
MANIFEST = os.environ.get("RM_XENO_MANIFEST",
                          "/mnt/d/ClaudeWork/rimmandrake/scratch/xeno_heads/xeno_heads_v3_manifest.json")
SHOT_NAMES = [f"xeno_heads_v3{part}_{f}.png" for part in ("A", "B") for f in ("south", "east", "north", "west")]
DEF_FILES = ("Defs/HeadTypeDefs/SW_HeadTypes.xml", "Defs/GeneDefs/SW_Genes.xml",
             "Defs/XenotypeDefs/RimMandrakeXenotypes.xml")


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def defs_by_name(path, tag):
    return {d.findtext("defName"): d for d in ET.parse(path).getroot().iter(tag) if d.findtext("defName")}


def view(d, genes_only):
    if genes_only:
        g = d.find("genes")
        return sorted(li.text or "" for li in g.iter("li")) if g is not None else []
    return ET.tostring(d)


def shot_failures(files):
    """The shots must show the art deployed NOW: newer than it, and hash-bound to it by the manifest."""
    fails = []
    deployed = {rel: os.path.join(GAME_MOD, rel) for rel in files}
    newest = max((os.path.getmtime(p) for p in deployed.values() if os.path.isfile(p)), default=0)
    shots = {}
    for name in SHOT_NAMES:
        pth = os.path.join(SHOTS, name)
        if not os.path.isfile(pth):
            fails.append(f"live screenshot missing: {name}")
        elif os.path.getmtime(pth) < newest:
            fails.append(f"live screenshot {name} predates the deployed head art (retake: xeno_heads_live_shot.py)")
        else:
            shots[name] = sha(pth)
    try:
        with open(MANIFEST, encoding="utf-8") as fh:
            man = json.load(fh)
    except (OSError, ValueError) as exc:
        return fails + [f"live-shot manifest unreadable: {MANIFEST} ({type(exc).__name__})"]
    for rel, pth in deployed.items():
        if os.path.isfile(pth) and man.get("head_pngs", {}).get(rel) != sha(pth):
            fails.append(f"manifest does not record the deployed art for {rel}: the shots show other art")
    for name, h in shots.items():
        if man.get("shots", {}).get(name) != h:
            fails.append(f"manifest does not record shot {name} as it is now")
    for s in SPECIES:
        got = (man.get("pawns", {}).get(s) or {}).get("headType")
        if got != f"RSW_{s}_Head":
            fails.append(f"{s}: the shot pawn drew headType {got}, not RSW_{s}_Head")
    if man.get("failures"):
        fails.append(f"the live run itself failed: {man['failures']}")
    return fails


def main():
    mod = os.path.join(REPO, MOD_REL)
    for where in (mod, GAME_MOD, SHOTS):
        if not os.path.isdir(where):
            print(f"UNMEASURED: cannot see {where}")
            return 2
    heads = defs_by_name(os.path.join(mod, DEF_FILES[0]), "HeadTypeDef")
    genes = defs_by_name(os.path.join(mod, DEF_FILES[1]), "GeneDef")
    xenos = defs_by_name(os.path.join(mod, DEF_FILES[2]), "XenotypeDef")
    # Sanity: the parse must see a real population, or a zero below is the parser's blindness.
    if len(heads) < 4 or len(genes) < 50 or len(xenos) < 4:
        print(f"UNMEASURED: parse saw heads={len(heads)} genes={len(genes)} xenotypes={len(xenos)}")
        return 2
    game = [defs_by_name(os.path.join(GAME_MOD, rel), tag) for rel, tag in
            zip(DEF_FILES, ("HeadTypeDef", "GeneDef", "XenotypeDef"))]
    fails, files, ndefs = [], [], 0
    for s in SPECIES:
        head, gene, xeno = f"RSW_{s}_Head", f"RSW_{s}Head", f"RSW_RimMandrake{s}"
        h = heads.get(head)
        if h is None:
            fails.append(f"{s}: HeadTypeDef {head} missing")
            continue
        if gene not in [li.text for li in h.iter("li") if li.text]:
            fails.append(f"{s}: {head} does not require {gene}")
        if gene not in genes:
            fails.append(f"{s}: GeneDef {gene} missing")
        x = xenos.get(xeno)
        if x is None:
            fails.append(f"{s}: XenotypeDef {xeno} missing")
        elif gene not in [li.text for li in x.iter("li") if li.text]:
            fails.append(f"{s}: {xeno} does not carry {gene}")
        for repo_defs, game_defs, name in zip((heads, genes, xenos), game, (head, gene, xeno)):
            if name in repo_defs:
                ndefs += 1
                if name not in game_defs:
                    fails.append(f"{s}: {name} not deployed")
                elif view(repo_defs[name], name == xeno) != view(game_defs[name], name == xeno):
                    fails.append(f"{s}: deployed {name} differs from repo")
        tex = h.findtext("graphicPath")
        masked = h.find(".//shaderType") is not None and h.findtext(".//shaderType") == "CutoutComplex"
        for f in FACINGS:
            for suffix in ("", "m") if masked else ("",):
                rel = f"Textures/{tex}_{f}{suffix}.png"
                if not os.path.isfile(os.path.join(mod, rel)):
                    fails.append(f"{s}: texture {rel} missing in repo")
                else:
                    files.append(rel)
    for rel in files:
        deployed = os.path.join(GAME_MOD, rel)
        if not os.path.isfile(deployed):
            fails.append(f"not deployed: {rel}")
        elif sha(deployed) != sha(os.path.join(mod, rel)):
            fails.append(f"deployed copy differs from repo: {rel}")
    fails += shot_failures(files)
    for line in fails:
        print("FAIL", line)
    print(f"{'PASS' if not fails else 'FAIL'}: {len(SPECIES)} species, {ndefs} defs and {len(files)} PNGs "
          f"compared repo vs deployed, {len(SHOT_NAMES)} screenshots checked, {len(fails)} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
