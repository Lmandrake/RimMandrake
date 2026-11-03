#!/usr/bin/env python3
"""Proof for BIOME_FLORAFAUNA_ART_REVIEW_1 over a fresh census (biome_census.py --no-wookiee --out DIR).

    python3 infrastructure/state/evidence/BIOME_FLORAFAUNA_ART_REVIEW_1/proof.py DIR/census.json [--sheets DIR]

Clauses, each red when broken:
  C1 one sheet per biome covering every flora+fauna row: biome_sheet_coverage.coverage() unions every committed
     <slug>_sheet_*.snapshot.json of the biome; every census row key is a snapshot row or in droppedAllRuled;
     >= 20 biomes with rows; no biome without a snapshot.
  C2 >= 1 art version each: census no_art == 0, and every row has >= 1 art column on the newest snapshot
     that holds it.
  C3 canon refs + Must show on every canon creature: every row with a canon entry has has_must_show and >= 1 image;
     canon_missing_entry == 0.
Exit 0 when all hold, 1 otherwise.
"""
import argparse
import glob
import json
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
ART = os.path.join(REPO, "src", "RimMandrake", "Utils", "art")
sys.path[:0] = [ART, os.path.dirname(ART)]
import biome_sheet_coverage as C  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("census")
    ap.add_argument("--sheets", default=os.path.join(REPO, "infrastructure", "state", "art", "sheets"))
    a = ap.parse_args(argv)
    census = json.load(open(a.census))
    fails = []
    cov = C.coverage(census, a.sheets)
    bad = C.failing(cov)
    if len(cov) < 20:
        fails.append("C1 only %d biomes with rows" % len(cov))
    for b, v in sorted(bad.items()):
        fails.append("C1/C2/C3 %s: %d uncovered %s, no_art=%s, canon_missing_entry=%s, snapshots=%d"
                     % (b, len(v["uncovered"]), v["uncovered"][:10], v["no_art"], v["canon_missing_entry"], len(v["snapshots"])))
    n_rows = n_canon = n_cols = 0
    for bk in census["biome_order"]:
        rows = census["biomes"][bk].get("rows") or []
        if not rows:
            continue
        cols = {}
        for p in sorted(glob.glob(os.path.join(a.sheets, "%s_sheet_*.snapshot.json" % C.slug(bk)))):   # dated: newest last wins
            d = json.load(open(p))
            if d.get("biome") not in (None, bk):
                continue
            for k, r in (d.get("rows") or {}).items():
                cols[k] = len((r or {}).get("columns") or {})
        for r in rows:
            n_rows += 1
            k = r["key"]
            if not r["art"]["has_art"]:
                fails.append("C2 %s %s: no art in census" % (bk, k))
            if k in cols:
                if cols[k] < 1:
                    fails.append("C2 %s %s: on the sheet with 0 art columns" % (bk, k))
                else:
                    n_cols += 1
            c = r["canon"]
            if c.get("canon_missing_entry"):
                fails.append("C3 %s %s: canon creature with no canon entry" % (bk, k))
            if c.get("entry"):
                n_canon += 1
                if not c.get("has_must_show"):
                    fails.append("C3 %s %s: canon entry %s has no Must show" % (bk, k, c["entry"]))
                if not c.get("images"):
                    fails.append("C3 %s %s: canon entry %s has no reference image" % (bk, k, c["entry"]))
    if n_canon == 0:
        fails.append("C3 0 canon rows seen: the instrument is blind")
    for f in fails[:60]:
        print("FAIL " + f)
    print("%d biomes, %d rows, %d rows on a sheet with art columns, %d canon rows; %d failures"
          % (len(cov), n_rows, n_cols, n_canon, len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
