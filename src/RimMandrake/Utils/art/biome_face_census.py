#!/usr/bin/env python3
"""WORLDMAP_BIOME_APPEARANCE_1: does every shipped biome wear its own face on the planet?

A BiomeDef's <texture> is OWNED when the path resolves to a png inside the def's own mod and the file is named with one of
our tier prefixes (vanilla's World/Biomes has no RM_/RSW_/RUT_ name, and a donor path resolves to no file of ours). Two
different biomes may share a picture only as RM_/RUT_ twins. A patch that rewrites a BiomeDef's texture is a finding too:
the census reads defs, so such a patch would make it lie.
usage: python3 biome_face_census.py [--deployed]    exit 0 = all owned; --deployed also compares each face with the game copy
"""
import argparse, glob, hashlib, os, re, sys, xml.etree.ElementTree as ET

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../.."))
GAME_MODS = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"
PREFIX = ("RM_", "RSW_", "RUT_")
SKIP = ("/selftest_fixtures/", "/Staged/")


def mod_root(path):
    return path.split("/Defs/")[0]


def biome_defs(src):
    """every concrete BiomeDef under src: (defName, texture, xml path); a parent's texture is inherited."""
    rows, parents = [], {}
    for p in glob.glob(os.path.join(src, "**", "Defs", "**", "*.xml"), recursive=True):
        if any(s in p for s in SKIP): continue
        try: root = ET.parse(p).getroot()
        except ET.ParseError as e: raise SystemExit(f"UNMEASURED: {p}: {e}")
        for d in root.iter("BiomeDef"):
            if d.get("Name"): parents[d.get("Name")] = d
            if d.get("Abstract", "").lower() == "true": continue
            rows.append((d, p))
    out = []
    for d, p in rows:
        tex, node = d.findtext("texture"), d
        while tex is None and node.get("ParentName") in parents:
            node = parents[node.get("ParentName")]; tex = node.findtext("texture")
        out.append((d.findtext("defName"), tex, p))
    return sorted(out)


def texture_patches(src):
    hits = []
    for p in glob.glob(os.path.join(src, "**", "Patches", "**", "*.xml"), recursive=True):
        if any(s in p for s in SKIP): continue
        if re.search(r"BiomeDef[^<]*/texture\b", open(p, encoding="utf-8", errors="ignore").read()): hits.append(p)
    return sorted(hits)


def twin_key(png):
    return re.sub(r"^(RM|RSW|RUT)_", "", os.path.basename(png)[:-4])


def census(src):
    """-> (rows, findings); a row is (defName, texture, verdict), a finding is one line."""
    rows, bad, by_pic = [], [], {}
    for name, tex, p in biome_defs(src):
        png = os.path.join(mod_root(p), "Textures", (tex or "") + ".png")
        if not tex: v = "NO_TEXTURE"
        elif not os.path.isfile(png): v = "NOT_OURS"           # vanilla or donor: no such file in this mod
        elif not os.path.basename(png).startswith(PREFIX): v = "LEGACY_NAME"
        else:
            v = "OWNED"
            by_pic.setdefault(hashlib.sha256(open(png, "rb").read()).hexdigest(), []).append((name, png))
        rows.append((name, tex, v))
        if v != "OWNED": bad.append(f"{v} {name} -> {tex}")
    for shared in by_pic.values():
        if len({twin_key(q) for _, q in shared}) > 1:       # same picture under two different biome names
            bad.append("SHARED " + ", ".join(n for n, _ in shared))
    bad += ["PATCHED " + p for p in texture_patches(src)]
    return rows, bad


def deployed(src):
    """-> findings: an OWNED face whose game copy is missing or differs (any mod folder under Mods/)."""
    bad = []
    copies = {}
    for q in glob.glob(os.path.join(GAME_MODS, "**", "Textures", "World", "Biomes", "*.png"), recursive=True):
        copies.setdefault(os.path.basename(q), set()).add(hashlib.sha256(open(q, "rb").read()).hexdigest())
    if not copies: return ["UNMEASURED no face found under " + GAME_MODS]
    for name, tex, p in biome_defs(src):
        png = os.path.join(mod_root(p), "Textures", (tex or "") + ".png")
        if not os.path.isfile(png): continue
        h = hashlib.sha256(open(png, "rb").read()).hexdigest()
        if h not in copies.get(os.path.basename(png), ()): bad.append(f"NOT_DEPLOYED {name} {os.path.basename(png)}")
    return bad


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--deployed", action="store_true")
    a = ap.parse_args()
    src = os.path.join(REPO, "src")
    rows, bad = census(src)
    if a.deployed: bad += deployed(src)
    owned = sum(r[2] == "OWNED" for r in rows)
    if len(rows) < 30: bad.append(f"UNMEASURED only {len(rows)} BiomeDefs seen; the walk went blind")
    for b in bad: print(b)
    print(f"OWNED {owned}/{len(rows)}, {len(rows) - owned} vanilla/donor/legacy faces, {len(bad)} findings")
    sys.exit(1 if bad else 0)
