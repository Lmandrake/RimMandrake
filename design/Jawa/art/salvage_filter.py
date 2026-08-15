#!/usr/bin/env python3
"""THE DECONSTRUCTIBLE FILTER — which shipped wreck props can the player strip?

v1 deliverable, owner's ruling 2026-08-13. This is an INGREDIENT the campaign
keeps spending: every authored wreck, ruin or salvage field we ever place is
unstrippable garbage to the player unless the palette is filtered first. Get it
right once, nobody pays again.

🔴 THE DAMAGE THIS PREVENTS. Two abstract parents in
`Data/Core/Defs/ThingDefs_Buildings/Buildings_Ancient_Outdoors.xml:4-28` look
identical from a texture folder:

    AncientBuildingBase                    alwaysDeconstructible true
    NonDeconstructibleAncientBuildingBase  deconstructible false   <- refuses

A prop on the second can only be removed with explosives. A colonist simply will
not take the job, and you find out hours into a playthrough. The twins are one
word apart: `AncientCryptosleepPod` is permanent; `AncientCryptosleepCasket` is
the richest salvage in the whole kit.

THREE PROPERTIES, INDEPENDENT — a def can pass any one and fail the others:
    placeable   does it have a designationCategory (or can one be patched on)
    removable   building.deconstructible
    yielding    costList x resourcesFractionWhenDeconstructed  (default 0.5)
                ...or killedLeavings, which requires DESTROYING it instead

WHY A SCRIPT AND NOT A TABLE. 580-odd active mods, and mods patch each other's
defs — Vanilla Vehicles Expanded has already rewritten the whole Core
vehicle-wreck salvage list in this install. A hand-written list rots silently the
first time someone subscribes to something. This reads the LIVE MERGED def state,
so it is right for the stack that exists today and can be re-run when it changes.

Run:    python3 design/Jawa/art/salvage_filter.py
Writes: salvage_palette.tsv    every wreck def, machine-readable
        SALVAGE_PALETTE.md     the two filtered lists, for humans
Both are COMMITTED beside this script — that is the point of the deliverable.
"""

import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scan_graphics import stream_objects, DUMP          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(HERE, "salvage_palette.tsv")
MD = os.path.join(HERE, "SALVAGE_PALETTE.md")

MODSCONFIG = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
              "RimWorld by Ludeon Studios/Config/ModsConfig.xml")
WORKSHOP = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"

KW = ("ancient", "slag", "chunk", "rubble", "debris", "wreck", "ruin", "scrap",
      "junk", "broken", "damaged", "destroyed", "busted", "rusted", "crashed",
      "derelict", "hulk", "shipchunk", "collapsed")

# RimWorld's default when resourcesFractionWhenDeconstructed is unset.
DEFAULT_FRACTION = 0.5
PX_PER_CELL_MAX = 64          # fully zoomed in
PX_PER_CELL_PLAY = 22         # ordinary play zoom

COLS = ["verdict", "defName", "modName", "label", "size", "minPx", "graphicClass",
        "deconstructible", "fraction", "yield", "chance", "costList", "killedLeavings",
        "designationCategory", "texOnDisk", "texPath"]


def counts(v):
    if not isinstance(v, list):
        return []
    return [(str(i.get("thingDef")), i.get("count") or 0)
            for i in v if isinstance(i, dict)]


def fmt(pairs):
    return ", ".join("%s x%s" % p for p in pairs)


def texture_index():
    """Every loose texture path shipped by any workshop mod, as a set of
    lowercase Textures-relative paths without extension.

    ⚠️ Vanilla ships NONE. `Data/*/Textures` does not exist for any DLC — Core,
    Royalty, Ideology, Biotech, Anomaly and Odyssey all pack their art into
    AssetBundles. So a vanilla wreck prop's sprite CANNOT be inspected offline,
    and this index will report every one of them as packed. That is a real
    finding, not a gap in the scan: judging vanilla wreck art at sprite scale
    needs either a Unity bundle extraction or an in-game screenshot.
    """
    idx = set()
    if not os.path.isdir(WORKSHOP):
        return idx
    for mod in os.listdir(WORKSHOP):
        root = os.path.join(WORKSHOP, mod, "Textures")
        if not os.path.isdir(root):
            continue
        for dirpath, _dirs, files in os.walk(root):
            rel = os.path.relpath(dirpath, root)
            for f in files:
                if f.lower().endswith(".png"):
                    stem = os.path.splitext(f)[0]
                    p = stem if rel == "." else os.path.join(rel, stem)
                    idx.add(p.replace("\\", "/").lower())
    return idx


def tex_present(texpath, idx):
    """Graphic_Multi appends _north/_east/_south; Graphic_Random appends A/B/C."""
    if not texpath:
        return False
    t = texpath.replace("\\", "/").lower()
    if t in idx:
        return True
    for suf in ("_north", "_south", "_east", "_west", "a", "b", "c", "_a", "_b"):
        if t + suf in idx:
            return True
    return False


def collect(idx):
    rows = []
    for raw in stream_objects(DUMP):
        if not any(k in raw[:4000].lower() for k in KW):
            continue
        try:
            d = json.loads(raw)
        except Exception:
            continue
        dn = d.get("defName", "")
        if dn.startswith(("Blueprint_", "Frame_")):
            continue
        if not any(k in (dn + " " + (d.get("label") or "")).lower() for k in KW):
            continue
        f = d.get("fields") or {}
        if f.get("category") != "Building":
            continue
        b = f.get("building") or {}
        gd = f.get("graphicData") or {}
        sz = f.get("size") or {}
        w, h = (sz.get("x") or 1), (sz.get("z") or 1)

        decon = b.get("deconstructible", True)          # unset => True
        frac = f.get("resourcesFractionWhenDeconstructed")
        frac = DEFAULT_FRACTION if frac is None else float(frac)
        cost = counts(f.get("costList"))
        killed = counts(f.get("killedLeavings"))
        got = [(t, c * frac) for t, c in cost]
        # RimWorld rounds a fractional return with GenMath.RoundRandom, so 0.4 means
        # "40% chance of one" rather than a reliable return. Only >=1 is dependable,
        # and only that counts as a yield for bucketing purposes.
        chance = [(t, c) for t, c in got if 0 < c < 1]
        got = [(t, c) for t, c in got if c >= 1]

        if decon is False:
            verdict = "EXCLUDED"
        elif got:
            verdict = "USABLE-YIELDS"
        elif killed:
            verdict = "USABLE-DESTROY-ONLY"
        else:
            verdict = "USABLE-EMPTY"

        rows.append(dict(
            verdict=verdict, defName=dn, modName=d.get("modName", ""),
            label=d.get("label", ""), size="%dx%d" % (w, h),
            minPx=min(w, h) * PX_PER_CELL_PLAY,
            graphicClass=(gd.get("graphicClass") or "").replace("Verse.", ""),
            deconstructible=decon, fraction=round(frac, 6),
            **{"yield": fmt([(t, round(c, 1)) for t, c in got])},
            chance=fmt([(t, round(c, 2)) for t, c in chance]),
            costList=fmt(cost), killedLeavings=fmt(killed),
            designationCategory=f.get("designationCategory") or "",
            texOnDisk=tex_present(gd.get("texPath"), idx),
            texPath=gd.get("texPath", "")))
    return rows


RUINS = ("Ancient", "Chunk", "Rubble", "Ship", "Slag", "Collapsed", "Scrap",
         "Wreck", "Ruined", "Busted", "Broken", "Damaged", "Destroyed", "Crashed")


def md_table(rows, cols, headers):
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(cols)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(
            ("`%s`" % r[c]) if c == "defName" else str(r[c] or "-") for c in cols) + " |")
    return "\n".join(out)


def write_md(rows):
    ex = sorted([r for r in rows if r["verdict"] == "EXCLUDED"],
                key=lambda r: (r["modName"], r["defName"]))
    yields = sorted([r for r in rows if r["verdict"] == "USABLE-YIELDS"],
                    key=lambda r: r["defName"])
    destroy = [r for r in rows if r["verdict"] == "USABLE-DESTROY-ONLY"]
    empty = [r for r in rows if r["verdict"] == "USABLE-EMPTY"]

    L = []
    L.append("# SALVAGE_PALETTE.md — which shipped wreck props the player can actually strip\n")
    L.append("🔴 **GENERATED FILE. Do not hand-edit.** Regenerate with "
             "`python3 design/Jawa/art/salvage_filter.py`.\n")
    L.append("Read from the **live merged def state** (`DefDump/defs/ThingDef.json`), not "
             "shipped XML, because mods patch each other's defs — *Vanilla Vehicles Expanded* "
             "has already rewritten the entire Core vehicle-wreck salvage list in this "
             "install. **Re-run this after any modstack change.**\n")
    L.append("Yield shown is what a colonist actually receives: "
             "`costList x resourcesFractionWhenDeconstructed` (RimWorld's default fraction "
             "is 0.5 when unset). ⚠️ A fractional return is rounded by `GenMath.RoundRandom`, so "
             "0.4 means *a 40% chance of one*, not a reliable return — only entries of 1 or "
             "more count as a yield here. Sub-1 returns are kept in the `chance` column of "
             "the TSV.\n")
    L.append("| bucket | count | meaning |")
    L.append("|---|---:|---|")
    L.append("| 🔴 **EXCLUDED** | %d | refuses deconstruction — removable only by explosives |" % len(ex))
    L.append("| ✅ **USABLE-YIELDS** | %d | deconstructs AND returns materials |" % len(yields))
    L.append("| ⚠️ **USABLE-DESTROY-ONLY** | %d | deconstructs for nothing; must be destroyed for `killedLeavings` |" % len(destroy))
    L.append("| ⚪ **USABLE-EMPTY** | %d | deconstructs, returns nothing, ever — pure scenery |" % len(empty))
    L.append("")

    L.append("---\n\n## 1. 🔴 EXCLUDED — do not place where the clan must salvage\n")
    L.append("These descend from `NonDeconstructibleAncientBuildingBase` or otherwise set "
             "`building.deconstructible false`. **They are indistinguishable from the usable "
             "ones in a mod's texture folder**; the difference surfaces only when a colonist "
             "refuses the job. Place one only where a *permanent* scar is wanted.\n")
    L.append(md_table(ex, ["defName", "modName", "size", "label"],
                      ["defName", "mod", "size", "label"]))

    L.append("\n---\n\n## 2. ✅ USABLE — deconstructs and yields\n")
    L.append("This is where the salvage economy gets tuned. Sorted by defName; "
             "`Graphic_Random` entries are marked because repetition is what makes a big "
             "wreck read as wallpaper, and variety is free when the def already has it.\n")
    L.append(md_table(yields,
                      ["defName", "modName", "size", "graphicClass", "fraction", "yield"],
                      ["defName", "mod", "size", "graphic", "frac", "a colonist receives"]))

    L.append("\n---\n\n## 3. ⚠️ USABLE but returns NOTHING on deconstruct\n")
    L.append("**%d defs deconstruct for nothing and %d more give up materials only when "
             "DESTROYED.** Over half the ruins kit is scenery, not salvage. If the campaign "
             "wants these to be strippable, this is the list to patch a `costList` onto — "
             "the established local idiom (*Salvage Rubble*, *Vanilla Vehicles Expanded*).\n"
             % (len(empty), len(destroy)))
    L.append("**Destroy-only (has `killedLeavings`):**\n")
    L.append(md_table(sorted(destroy, key=lambda r: r["defName"])[:40],
                      ["defName", "modName", "size", "killedLeavings"],
                      ["defName", "mod", "size", "yields when destroyed"]))
    L.append("\n**Returns nothing either way — first 40 of %d:** " % len(empty)
             + ", ".join("`%s`" % r["defName"] for r in
                         sorted(empty, key=lambda r: r["defName"])[:40]) + "\n")

    L.append("\n---\n\n## 4. Does it read as BROKEN at sprite scale?\n")
    onwoff = [r for r in rows if r["verdict"].startswith("USABLE") and r["texOnDisk"]]
    packed = [r for r in rows if r["verdict"].startswith("USABLE") and not r["texOnDisk"]]
    L.append("🔴 **This cannot be answered offline for the vanilla kit, and that is a "
             "finding rather than a gap.** `Data/*/Textures` **does not exist for any DLC** — "
             "Core, Royalty, Ideology, Biotech, Anomaly and Odyssey all pack their art into "
             "`AssetBundles`. Zero loose PNGs ship with the base game.\n")
    L.append("- **%d** usable wreck defs have a loose PNG on disk (workshop mods) and CAN be "
             "rendered offline.\n- **%d** are packed and cannot. For those the routes are a "
             "Unity bundle extraction, or an in-game screenshot over the live bridge — which "
             "is cheap and needs no reload.\n" % (len(onwoff), len(packed)))
    L.append("**Free proxy in the meantime: footprint.** A prop's smallest on-screen dimension "
             "at ordinary play zoom is `min(size) x 22 px`. Below ~44 px the silhouette is "
             "carrying the entire read and interior detail is wasted (as per "
             "the trap file). Usable defs at or below that threshold:\n")
    tiny = sorted([r for r in rows if r["verdict"].startswith("USABLE") and r["minPx"] <= 44],
                  key=lambda r: (r["minPx"], r["defName"]))
    L.append("- **%d of %d** usable defs are 1x1 or 2x wide, i.e. **%d px or less** on screen. "
             "Place these in CLUSTERS, never singly — one 22 px prop is noise, nine are a "
             "debris field.\n" % (len(tiny), len([r for r in rows if r['verdict'].startswith('USABLE')]),
                                  PX_PER_CELL_PLAY * 2))
    big = sorted([r for r in rows if r["verdict"].startswith("USABLE") and r["minPx"] >= 66],
                 key=lambda r: -r["minPx"])[:25]
    L.append("**The props big enough to read on their own** (>= 3 cells on the short side, "
             "so >= 66 px at play zoom) — these are the ones that carry a wreck:\n")
    L.append(md_table(big, ["defName", "modName", "size", "minPx", "verdict"],
                      ["defName", "mod", "size", "px at play zoom", "bucket"]))
    L.append("")
    with open(MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


def main():
    idx = texture_index()
    print("loose workshop textures indexed: %d" % len(idx), file=sys.stderr)
    rows = collect(idx)
    with open(TSV, "w", encoding="utf-8") as fh:
        fh.write("\t".join(COLS) + "\n")
        for r in sorted(rows, key=lambda r: (r["verdict"], r["modName"], r["defName"])):
            fh.write("\t".join(str(r[c]).replace("\t", " ") for c in COLS) + "\n")
    write_md(rows)
    c = Counter(r["verdict"] for r in rows)
    print("wreck defs: %d  %s" % (len(rows), dict(c)), file=sys.stderr)
    print("wrote %s and %s" % (TSV, MD), file=sys.stderr)


if __name__ == "__main__":
    main()
