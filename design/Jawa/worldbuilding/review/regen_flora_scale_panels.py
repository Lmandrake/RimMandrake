#!/usr/bin/env python3
"""regen_flora_scale_panels.py — true-scale plant panels with the COLONIST figure.

Owner ruling 2026-09-09: the flora sheet's drawn side-on silhouette is "ugly" — the
same human figure as the fauna sheet (the real RimWorld colonist in
assets/human_anchor_south.png) goes in EVERY scale panel, both sheets.

gen_plant_register.py's `_scale_panel` hardcodes the drawn figure, so this helper
re-renders panels for the ROSTERED flora only (the defs on the flora assignment
sheet), writing `plant_art/<def>.anchor.png` beside the originals — never over
them, so plant_register.html keeps its own coherent layout — plus
`flora_scale_panels.json` with the metadata the sheet generator scales by.

Run from this directory:  python3 regen_flora_scale_panels.py
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
UTILS = HERE.parents[3] / "src" / "RimMandrake" / "Utils"
sys.path.insert(0, str(UTILS))

import gen_plant_register as GPR  # noqa: E402

ROSTERS = HERE.parent / "biomes" / "rosters"
OUT_JSON = HERE / "flora_scale_panels.json"
ANCHOR = HERE / "assets" / "human_anchor_south.png"


def anchored_panel(im, cells, mesh, Image, ImageDraw):
    """GPR._scale_panel with the colonist anchor instead of the drawn figure.

    The original hardcodes fig_w = 0.42*hh for its drawn silhouette; the anchor
    has its own aspect, so the figure slot is sized from the real image."""
    PX = GPR.PX_PER_CELL
    hh = int(round(GPR.HUMAN_CELLS * PX))
    fig = Image.open(ANCHOR).convert("RGBA")
    k = hh / float(fig.height)
    fig = fig.resize((max(1, int(fig.width * k)), hh), Image.LANCZOS)
    fig_w = fig.width

    quad = max(8, int(round(cells * PX)))
    footprint = max(quad, PX) if mesh > 1 else quad
    gap, pad = 18, 10
    tw = pad + fig_w + gap + footprint + pad
    th = pad + max(hh, footprint) + pad
    panel = Image.new("RGBA", (tw, th), (18, 21, 26, 255))
    d = ImageDraw.Draw(panel)
    for x in range(pad, tw, PX):
        d.line([(x, 0), (x, th)], fill=(34, 39, 47, 255))
    for y in range(th - pad, -1, -PX):
        d.line([(0, y), (tw, y)], fill=(34, 39, 47, 255))

    base_y = th - pad
    panel.alpha_composite(fig, (pad, base_y - hh))

    k = min(quad / float(im.width), quad / float(im.height))
    cw = max(1, int(round(im.width * k)))
    ch = max(1, int(round(im.height * k)))
    spr = im.resize((cw, ch), Image.LANCZOS if im.width > cw else Image.NEAREST)

    left = pad + fig_w + gap
    if mesh <= 1:
        panel.alpha_composite(spr, (left, base_y - ch))
    else:
        cell = max(footprint, PX)
        for fx, fz in GPR._mesh_offsets(mesh):
            x = left + int(fx * cell) - cw // 2
            y = base_y - int(fz * cell) - ch // 2
            x = max(0, min(tw - cw, x))
            y = max(0, min(th - ch, y))
            panel.alpha_composite(spr, (x, y))
    return panel


def patch_original_panel(defname: str, art: dict, Image, ImageDraw):
    """Fallback for sprites only the (since-shrunk) bundle cache could resolve:
    take the ORIGINAL panel, erase the drawn figure's slot (its geometry is
    deterministic: pad 10, slot width 0.42*96=40, gap 18, all scaled by
    shownPct), repaint the grid there, and composite the colonist anchor."""
    src = HERE / art["scale"]
    if not src.is_file():
        return None
    panel = Image.open(src).convert("RGB")
    s = (art.get("shownPct") or 100) / 100.0
    W, H = panel.size
    pad = round(10 * s)
    hh = round(96 * s)
    slot_end = round((10 + 40 + 9) * s)          # figure slot + half the gap
    d = ImageDraw.Draw(panel)
    d.rectangle([0, 0, slot_end, H - 1], fill=(16, 22, 18))
    step = 64 * s
    x = 10 * s
    while x <= slot_end:
        d.line([(round(x), 0), (round(x), H)], fill=(32, 42, 34))
        x += step
    y = H - 10 * s
    while y >= 0:
        d.line([(0, round(y)), (slot_end, round(y))], fill=(32, 42, 34))
        y -= step
    fig = Image.open(ANCHOR).convert("RGBA")
    k = hh / float(fig.height)
    fig = fig.resize((max(1, int(fig.width * k)), max(1, hh)), Image.LANCZOS)
    panel.paste(fig, (pad, H - pad - fig.height), fig)
    return panel


def main() -> int:
    from PIL import Image, ImageDraw

    wanted = set()
    for path in sorted(ROSTERS.glob("*.json")):
        if path.name.startswith("_"):
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        wanted |= {e["def"] for e in (doc.get("flora") or [])}
    print(f"{len(wanted)} rostered plant defs")

    reg = {r["defName"]: r
           for r in json.loads((HERE / "plant_register_rows.json")
                               .read_text(encoding="utf-8"))["rows"]}

    # NOT GPR._texture_index(): that builds from the LIVE ModsConfig, which today is
    # a minimal swap list — ModsConfig describes the next load, not the dump the
    # register was built from. Index everything installed on disk instead.
    import game_paths as GP
    import rimworld_loadset as LS
    import thing_contact_sheet as TCS
    import animal_contact_sheet as ACS
    mods = list(LS.discover_mods([GP.WORKSHOP, GP.LOCAL_MODS, GP.GAME_DATA]).values())
    idx, nfiles, nroots = ACS.build_texture_index(mods)
    print(f"texture index over ALL installed mods: {len(idx)} paths "
          f"({nfiles} files, {nroots} roots, {len(mods)} mods)")
    dir_idx = TCS.build_dir_index(idx)
    bundles, _n = ACS.load_bundle_index()

    out, stats = {}, {"ok": 0, "missing": 0, "nosize": 0, "notreg": 0}
    for defname in sorted(wanted):
        r = reg.get(defname)
        if r is None:
            out[defname] = {"file": None, "reason": "not in plant register"}
            stats["notreg"] += 1
            continue
        src, rung = GPR._resolve_plant(r, idx, dir_idx, bundles)
        if not src:
            art = r.get("art") or {}
            panel = (patch_original_panel(defname, art, Image, ImageDraw)
                     if art.get("scale") else None)
            if panel is not None:
                base = re.sub(r"[^A-Za-z0-9_.-]", "_", defname)
                rel = f"plant_art/{base}.anchor.png"
                panel.save(HERE / rel, optimize=True)
                out[defname] = {"file": rel, "w": panel.width, "h": panel.height,
                                "shownPct": art.get("shownPct") or 100,
                                "cells": GPR.mature_cells(r),
                                "mesh": art.get("meshShown") or 1,
                                "patched": True}
                stats["patched"] = stats.get("patched", 0) + 1
                continue
            out[defname] = {"file": None, "reason": rung or "unresolved texture"}
            stats["missing"] += 1
            continue
        try:
            im = Image.open(src).convert("RGBA")
            bbox = im.getbbox()
            if not bbox:
                raise ValueError("blank png")
            im = im.crop(bbox)
        except Exception as exc:  # noqa: BLE001
            out[defname] = {"file": None, "reason": f"unreadable: {exc}"}
            stats["missing"] += 1
            continue
        cells = GPR.mature_cells(r)
        if not cells:
            out[defname] = {"file": None, "reason": "size unmeasured (no drawSize/visualSize)"}
            stats["nosize"] += 1
            continue
        mesh = min(int(r.get("maxMeshCount") or 1), GPR.MESH_CAP)
        panel = anchored_panel(im, cells, mesh, Image, ImageDraw)
        shown = 100
        if max(panel.size) > GPR.SCALE_CAP:
            k = GPR.SCALE_CAP / float(max(panel.size))
            panel = panel.resize((max(1, int(panel.width * k)),
                                  max(1, int(panel.height * k))), Image.LANCZOS)
            shown = int(round(k * 100))
        base = re.sub(r"[^A-Za-z0-9_.-]", "_", defname)
        rel = f"plant_art/{base}.anchor.png"
        panel.convert("RGB").save(HERE / rel, optimize=True)
        out[defname] = {"file": rel, "w": panel.width, "h": panel.height,
                        "shownPct": shown, "cells": round(cells, 3), "mesh": mesh}
        stats["ok"] += 1

    OUT_JSON.write_text(json.dumps(
        {"figure": "assets/human_anchor_south.png (the fauna sheet's colonist)",
         "pxPerCell": GPR.PX_PER_CELL, "humanCells": GPR.HUMAN_CELLS,
         "panels": out}, indent=1) + "\n", encoding="utf-8")
    print(f"panels: {stats}")
    print(f"wrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
