#!/usr/bin/env python3
"""Does every Baroque biome have a review sheet that covers every flora+fauna row? (BIOME_FLORAFAUNA_ART_REVIEW_1)

For each biome with rows in a census (biome_census.py), a row is COVERED when its key is a row of one of that biome's
committed sheet snapshots (infrastructure/state/art/sheets/<slug>_sheet_*.snapshot.json), or is listed in a snapshot's
`droppedAllRuled` (art_sheet.py leaves off a row whose every option the owner already ruled, rather than re-ask him).
Also fails a biome whose census summary has a row with no art (`no_art`) or a canon row with no canon entry
(`canon_missing_entry`), or that has no snapshot at all.

    python3 src/RimMandrake/Utils/art/biome_census.py --no-wookiee --out /tmp/c
    python3 src/RimMandrake/Utils/art/biome_sheet_coverage.py /tmp/c/census.json [--min-biomes 20] [--json out.json]

Exit 0 when every biome is covered, 1 otherwise (each failing biome and its uncovered rows printed).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path[:0] = [HERE, os.path.dirname(HERE)]


def slug(biome: str) -> str:
    import art_sheet as A
    return A.BIOME_SLUG.get(biome) or A._stem(biome).lower()


def coverage(census: dict, sheets_dir: str, slug_of=slug) -> dict:
    out = {}
    for bk in census["biome_order"]:
        B = census["biomes"][bk]
        rows = B.get("rows") or []
        if not rows:
            continue
        s = B.get("summary") or {}
        snaps = sorted(glob.glob(os.path.join(sheets_dir, f"{slug_of(bk)}_sheet_*.snapshot.json")))
        covered, dropped = set(), set()
        for p in snaps:
            d = json.load(open(p))
            if d.get("biome") not in (None, bk):
                continue                       # a slug collision: another biome's sheet
            covered |= set(d.get("rows") or {})
            dropped |= set(d.get("droppedAllRuled") or [])
        keys = {r["key"] for r in rows}
        out[bk] = {"rows": len(keys), "snapshots": [os.path.basename(p) for p in snaps],
                   "uncovered": sorted(keys - covered - dropped), "dropped_all_ruled": sorted(keys & dropped - covered),
                   "no_art": s.get("no_art") or 0, "canon_missing_entry": s.get("canon_missing_entry") or 0}
    return out


def failing(cov: dict) -> dict:
    return {b: v for b, v in cov.items()
            if v["uncovered"] or v["no_art"] or v["canon_missing_entry"] or not v["snapshots"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("census")
    ap.add_argument("--sheets", default=os.path.join(REPO, "infrastructure", "state", "art", "sheets"))
    ap.add_argument("--min-biomes", type=int, default=20)
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    cov = coverage(json.load(open(a.census)), a.sheets)
    bad = failing(cov)
    if a.json:
        json.dump(cov, open(a.json, "w"), indent=1, sort_keys=True)
    n_rows = sum(v["rows"] for v in cov.values())
    n_unc = sum(len(v["uncovered"]) for v in cov.values())
    for b, v in sorted(bad.items()):
        print(f"FAIL {b}: {len(v['uncovered'])} uncovered of {v['rows']} rows, no_art={v['no_art']}, "
              f"canon_missing_entry={v['canon_missing_entry']}, snapshots={len(v['snapshots'])}: "
              + " ".join(v["uncovered"][:40]))
    print(f"{len(cov)} biomes with rows, {n_rows} rows, {n_unc} uncovered; failing biomes: {len(bad)}")
    return 1 if bad or len(cov) < a.min_biomes else 0


if __name__ == "__main__":
    sys.exit(main())
