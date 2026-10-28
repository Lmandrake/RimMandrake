#!/usr/bin/env python3
"""selftest_reference_textures.py — a census row's `reference_textures` (e.g. the installed canon twin beside the base it
will reskin) is shown read-only and can NEVER become a pickable column: not a graphic, column, letter, snapshot entry,
decision or enact target. Checked on a synthetic row through the real builder helpers, and on every built subject sheet
whose census carries the field."""
from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import art_sheet as A  # noqa: E402
import artledger as L  # noqa: E402

FAILS = []
STALE = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


CANDIDATE_ROLES = ("live", "artpipe")   # a graphics-column `kind` that is a real offered picture
CANDIDATE_LABELS = ("IN GAME", "render ")  # the snapshot's equivalent (it keeps the label, not the kind)


def smuggled_reference_columns(cols, refs, shas):
    """Columns of one row that are the reference texture in disguise. A column is identified by its ROLE metadata
    (graphics `kind`, or the snapshot label), not by pixel sha: the shipped art (live / "IN GAME") or a render may
    legitimately be pixel-identical to the reference. A column is smuggled when it shares the reference's sha (or cites
    its path) WITHOUT carrying a candidate role, or when it cites a reference file path as its source."""
    bad = []
    for col in cols:
        dump = json.dumps({k: v for k, v in col.items() if k not in ("role_checked",)})
        cites = any(p and p in dump for p in refs)
        role = col.get("kind")
        ok_role = role in CANDIDATE_ROLES if role is not None else str(col.get("label", "")).startswith(CANDIDATE_LABELS)
        if cites or (any(h in dump for h in shas) and not ok_role):
            bad.append(col)
    return bad


def role_cases():
    sha = "ab" * 32
    ref = "src/x/ref_south.png"
    live = {"kind": "live", "label": "IN GAME \u2014 FlowWorks", "faces": {"single": sha}}
    check(not smuggled_reference_columns([live], [ref], {sha}), "a reference shown as the labelled IN GAME column (same sha) passes")
    render = {"kind": "artpipe", "label": "render foo", "faces": {"single": sha}}
    check(not smuggled_reference_columns([render], [ref], {sha}), "a render pixel-identical to the reference passes")
    snap = {"label": "IN GAME \u2014 FlowWorks", "single": sha}
    check(not smuggled_reference_columns([snap], [ref], {sha}), "a snapshot column labelled IN GAME (same sha) passes")
    mis = {"kind": "reference", "label": "candidate Z", "faces": {"single": sha}}
    check(len(smuggled_reference_columns([mis], [ref], {sha})) == 1, "a reference image mislabelled as a candidate FAILS")
    unl = {"faces": {"single": sha}}
    check(len(smuggled_reference_columns([unl], [ref], {sha})) == 1, "an unlabelled column carrying the reference sha FAILS")
    cited = {"kind": "artpipe", "label": "render bar", "faces": {"single": "cd" * 32}, "src": ref}
    check(len(smuggled_reference_columns([cited], [ref], {sha})) == 1, "a candidate sourced from the reference file path FAILS")


def synthetic():
    from PIL import Image
    with tempfile.TemporaryDirectory(dir=L.REPO_ROOT / "Transient") as td:
        png = Path(td) / "ref.png"
        Image.new("RGBA", (64, 64), (200, 30, 30, 255)).save(png)
        sha = hashlib.sha256(png.read_bytes()).hexdigest()
        rel = str(png.relative_to(L.REPO_ROOT))
        size = {"status": "fallback", "kind": "plant", "drawSize": [1.0, 1.0], "visualMax": 2.0, "mesh": 1, "quad": 2.0,
                "cells": 2.0, "color": [1, 1, 1], "source": "FALLBACK test"}
        had = L.store_has(sha)
        refs = A._reference_panels({"key": "ST_Row", "reference_textures": [rel, "no/such.png"]}, size, Path(td))
        check(len(refs) == 2 and refs[0].get("img") and (Path(td).parent / refs[0]["img"]).exists(),
              "a reference texture renders a true-scale panel")
        check(refs[1].get("missing") is True, "a missing reference path is reported, not dropped")
        check(set(refs[0]) == {"path", "img", "full"}, f"a reference panel carries no letter/sha/faces: {sorted(refs[0])}")
        check(L.store_has(sha) == had, "a reference texture is never put in the art store (so no column can name it)")
        # a sized entry {path, size} renders at ITS size, not the row's (a composite of several pieces: a joined weir wall)
        wide = {"path": rel, "size": {"drawSize": [6, 2], "footprint": [6, 2], "source": "selftest composite"}}
        sized = A._reference_panels({"key": "ST_Row", "reference_textures": [rel, wide]}, size, Path(td))
        check(len(sized) == 2 and sized[1].get("img") and sized[1]["img"] != sized[0]["img"]
              and (Path(td).parent / sized[1]["img"]).exists(),
              "a sized reference entry renders its own panel at its own size")
        check(set(sized[1]) == {"path", "img", "full"} and sized[1]["path"] == rel, "a sized entry reports its path only")


def built_sheets():
    n = 0
    for cj in sorted(A.BIOME_OUT.glob("*.subjects.json")):
        c = json.loads(cj.read_text())
        for b in c.get("biomes", {}).values():
            for r in b.get("rows", []):
                refs = [e["path"] if isinstance(e, dict) else e for e in r.get("reference_textures") or []]
                if not refs:
                    continue
                shas = {hashlib.sha256((L.REPO_ROOT / p).read_bytes()).hexdigest() for p in refs if (L.REPO_ROOT / p).is_file()}
                for snap in sorted((L.REPO_ROOT / "infrastructure/state/art/sheets").glob(f"{b['slug']}_sheet_*.snapshot.json")):
                    s = json.loads(snap.read_text())
                    srow = (s.get("rows") or {}).get(r["key"], {})
                    scols = [{"letter": k, "label": (srow.get("labels") or {}).get(k, ""),
                              "graphic_of": (srow.get("graphic_of") or {}).get(k), **(v if isinstance(v, dict) else {"v": v})}
                             for k, v in (srow.get("columns") or {}).items()]
                    n += 1
                    check(not smuggled_reference_columns(scols, refs, shas),
                          f"{snap.stem} {r['key']}: no reference texture is a column")
                for html in sorted(A.BIOME_OUT.glob(f"{b['slug']}_sheet_*.html")):
                    if html.stat().st_mtime < cj.stat().st_mtime:
                        # built BEFORE the census last changed (the row may have gained reference_textures after this
                        # HTML was written): a stale artifact, not a builder defect -- a rebuild shows them. Only sheets
                        # built from the current census are held to "every reference texture is shown".
                        continue
                    h = html.read_text()
                    m = re.search(r'<script id="ITEMS" type="application/json">(.*?)</script>', h, re.S)
                    items = json.loads(m.group(1)) if m else []
                    it = next((i for i in items if i.get("key") == r["key"] or i.get("id") == r["key"]), None)
                    if it is None:
                        continue
                    gcols = [c for g in it.get("graphics") or [] for c in g.get("cols") or []]
                    check(not smuggled_reference_columns(gcols, refs, shas),
                          f"{html.stem} {r['key']}: no reference texture in the row's graphics")
                    if "refs" not in (it.get("scale") or {}) and (it.get("scale") or {}).get("status") != "none":
                        # no `refs` key at all = built by a builder from before reference panels existed (a measured-size
                        # sheet always writes the key). Not a shown/hidden verdict: counted and named, rebuild owed.
                        STALE.append(f"{html.stem} {r['key']}")
                        continue
                    check(len((it.get("scale") or {}).get("refs") or []) == len(refs),
                          f"{html.stem} {r['key']}: every reference texture is shown ({len(refs)})")
    print(f"built-sheet rows with reference_textures checked: {n}; pre-reference-panel HTML rows not judged (rebuild owed): {len(STALE)}")


def main():
    synthetic()
    role_cases()
    built_sheets()
    print(f"{len(FAILS)} failed" if FAILS else "all passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
