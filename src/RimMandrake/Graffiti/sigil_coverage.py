#!/usr/bin/env python3
"""Graffiti sigil coverage vs vanilla Ideology data (GRAFFITI_SIGIL_COVERAGE_CHECK_1).

Verify step 3 of GRAFFITI_PUNK_IDEOLIGION_SCOPE_1. Reads the INSTALLED vanilla XML, never
the def dump (the dump holds no IdeoIconDef/IdeoColorDef):

  (a) every IdeoIconDef iconPath names a texture an expansion's AssetBundle manifest lists,
      so the tier-A frame (Filth_Mark.RebuildSigilMats -> Ideo.Icon) has something to draw;
  (b) every IdeoIconDef <memes> gate names a MemeDef the installed Data defines;
  (c) the tier-C glyph defs (ModExtension_Graffiti.requiresAnyMeme) cover every
      non-structure, non-abstract vanilla MemeDef, or the meme is named in EXCLUDED;
  plus: every requiresAnyMeme names a real vanilla meme, IdeoColorDefs is non-empty, and
  every sigilFrameTexPath resolves to a PNG under this mod's Textures/.

Zero rows read on any axis is a FAILURE, never a pass. A missing install root is
UNMEASURED (exit 2), never PASS.

usage: python3 sigil_coverage.py [--data <RimWorld/Data>]
exit: 0 PASS, 1 FAIL, 2 UNMEASURED
"""
import argparse
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

DEFAULT_DATA = "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data"
MOD = os.path.dirname(os.path.abspath(__file__))
# Memes deliberately without a tier-C glyph, each with its reason. Empty: the owner ruled
# 2026-09-25 (by card) that every vanilla meme gets a glyph.
EXCLUDED = {}
# Sanity floors from the 2026-09-08 measurement (27 non-structure ludeon memes).
MIN_MEMES = 20
MIN_ICONS = 20


def parse(path):
    try:
        return ET.parse(path).getroot()
    except ET.ParseError as e:
        print(f"UNPARSEABLE {path}: {e}")
        return None


def meme_categories(data):
    """MemeDef defName -> category, resolving ParentName inheritance (the religious-origin
    structure memes take <category>Structure</category> from an abstract parent)."""
    by_name, rows = {}, []
    for path in sorted(glob.glob(os.path.join(data, "*", "Defs", "**", "*.xml"), recursive=True)):
        root = parse(path)
        if root is None:
            continue
        for el in root.findall("MemeDef"):
            if el.get("Name"):
                by_name[el.get("Name")] = el
            rows.append(el)

    def category(el, depth=0):
        c = el.findtext("category")
        if c or depth > 10:
            return (c or "").strip()
        parent = by_name.get(el.get("ParentName") or "")
        return category(parent, depth + 1) if parent is not None else ""

    return {el.findtext("defName"): category(el) for el in rows
            if (el.get("Abstract") or "").lower() != "true" and el.findtext("defName")}


def vanilla_defs(data, tag):
    out = []
    for path in sorted(glob.glob(os.path.join(data, "*", "Defs", "**", "*.xml"), recursive=True)):
        root = parse(path)
        if root is None:
            continue
        for el in root.findall(tag):
            if (el.get("Abstract") or "").lower() == "true":
                continue
            out.append((el, os.path.relpath(path, data)))
    return out


def manifest_textures(data):
    tex = set()
    for m in glob.glob(os.path.join(data, "*", "AssetBundles", "*.manifest")):
        with open(m, encoding="utf-8", errors="replace") as f:
            for line in f:
                hit = re.search(r"/Textures/(.+)\.(png|psd|jpg)\s*$", line.strip(), re.I)
                if hit:
                    tex.add(hit.group(1).lower())
    return tex


def mod_glyphs():
    """defName -> list of requiresAnyMeme, plus sigilFrameTexPath list, from this mod's Defs."""
    glyphs, frames = {}, []
    for path in sorted(glob.glob(os.path.join(MOD, "Defs", "*.xml"))):
        root = parse(path)
        if root is None:
            continue
        for td in root.iter("ThingDef"):
            name = td.findtext("defName")
            for ext in td.iter("li"):
                if ext.get("Class", "").endswith("ModExtension_Graffiti"):
                    memes = [li.text.strip() for li in ext.findall("requiresAnyMeme/li") if li.text]
                    if memes:
                        glyphs[name] = memes
                    fp = ext.findtext("sigilFrameTexPath")
                    if fp:
                        frames.append((name, fp.strip()))
    return glyphs, frames


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default=DEFAULT_DATA)
    a = ap.parse_args()
    if not os.path.isdir(os.path.join(a.data, "Ideology", "Defs")):
        print(f"UNMEASURED: no Ideology Defs under {a.data}")
        return 2

    fails = []
    memes = meme_categories(a.data)
    meme_names = set(memes)
    nonstructure = sorted(m for m, c in memes.items() if c != "Structure")
    icons = vanilla_defs(a.data, "IdeoIconDef")
    colors = vanilla_defs(a.data, "IdeoColorDef")
    tex = manifest_textures(a.data)
    glyphs, frames = mod_glyphs()

    print(f"read: {len(memes)} MemeDef ({len(nonstructure)} non-structure), {len(icons)} IdeoIconDef, "
          f"{len(colors)} IdeoColorDef, {len(tex)} manifest textures, {len(glyphs)} tier-C glyph defs, {len(frames)} sigil frames")
    for label, n, floor in (("non-structure memes", len(nonstructure), MIN_MEMES), ("icons", len(icons), MIN_ICONS),
                            ("colors", len(colors), 1), ("manifest textures", len(tex), 1), ("glyph defs", len(glyphs), 1),
                            ("sigil frames", len(frames), 1)):
        if n < floor:
            fails.append(f"zero-row guard: {label} read {n} < floor {floor}")

    # (a) icon textures
    missing_tex = [(i.findtext("defName"), i.findtext("iconPath")) for i, _ in icons
                   if (i.findtext("iconPath") or "").strip().lower() not in tex]
    print(f"(a) icon textures: {len(icons) - len(missing_tex)}/{len(icons)} listed in an AssetBundle manifest")
    fails += [f"(a) IdeoIconDef {d}: iconPath {p} in no manifest" for d, p in missing_tex]

    # (b) icon meme gates
    bad_gate = [(i.findtext("defName"), li.text.strip()) for i, _ in icons for li in i.findall("memes/li")
                if li.text and li.text.strip() not in meme_names]
    gates = sum(len(i.findall("memes/li")) for i, _ in icons)
    print(f"(b) icon meme gates: {gates - len(bad_gate)}/{gates} name a real MemeDef")
    fails += [f"(b) IdeoIconDef {d}: gate meme {m} undefined" for d, m in bad_gate]

    # (c) tier-C coverage
    covered = {m for ms in glyphs.values() for m in ms}
    uncovered = [m for m in nonstructure if m not in covered and m not in EXCLUDED]
    print(f"(c) tier-C coverage: {len(nonstructure) - len(uncovered)}/{len(nonstructure)} non-structure memes have a glyph"
          f" ({len(EXCLUDED)} excluded by name)")
    fails += [f"(c) meme {m} has no tier-C glyph and no named exclusion" for m in uncovered]
    unknown = sorted({(g, m) for g, ms in glyphs.items() for m in ms if m not in meme_names})
    fails += [f"(c) glyph {g} requires meme {m}, which no vanilla Data defines" for g, m in unknown]

    # frames
    for name, fp in frames:
        if not os.path.isfile(os.path.join(MOD, "Textures", fp + ".png")):
            fails.append(f"frame: {name} sigilFrameTexPath {fp} has no PNG under Textures/")

    for f in fails:
        print("FAIL", f)
    print("RESULT:", "FAIL" if fails else "PASS", f"({len(fails)} finding(s))")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
