#!/usr/bin/env python3
"""Proof for MUTTAVAQ_ART_POLISH_NORTH_SIZE_AND_FACE: is the installed Muttavaq the same size in every
facing, and did the art judge ACCEPT exactly these pictures without a STYLE_CARTOON reason?

Exit 0 iff
  1. north's alpha bounding box (alpha > 128) is within TOL of south's in width AND height, and south's
     and north's heights are within TOL of east's (east is longer by anatomy, so only height compares);
  2. some infrastructure/state/art_eval/runs/*/decisions.jsonl row for RM_Muttavaq has decision ACCEPT,
     its source_sha256 south/north/east equal the installed PNGs' sha256, and no reason names STYLE_CARTOON
     or F_SIZE_JUMP.
Exit 1 otherwise; prints one line per check.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[4]
TEX = REPO / 'src/RimMandrake/CrackedLands/Textures/Things/Pawn/Animal/RM_Muttavaq'
RUNS = REPO / 'infrastructure/state/art_eval/runs'
SUBJECT = 'RM_Muttavaq'
FACINGS = ('south', 'north', 'east')
TOL = 0.07
BANNED = ('STYLE_CARTOON', 'F_SIZE_JUMP')


def bbox(path):
    """Width and height of the opaque body (alpha > 128), in pixels."""
    alpha = np.array(Image.open(path).convert('RGBA'))[:, :, 3] > 128
    ys, xs = np.where(alpha)
    if xs.size == 0:
        raise SystemExit(f'FAIL {path.name}: no opaque pixel')
    return int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)


def within(a, b):
    return abs(a / b - 1.0) <= TOL


def main():
    ok = True
    files = {f: TEX / f'{SUBJECT}_{f}.png' for f in FACINGS}
    box = {f: bbox(p) for f, p in files.items()}
    (sw, sh), (nw, nh), (_, eh) = box['south'], box['north'], box['east']
    size_ok = within(nw, sw) and within(nh, sh) and within(sh, eh) and within(nh, eh)
    ok &= size_ok
    print(f"{'PASS' if size_ok else 'FAIL'} size: S {sw}x{sh}, N {nw}x{nh}, E height {eh}; "
          f"N:S width {nw / sw:.3f}, height {nh / sh:.3f}; S:E height {sh / eh:.3f}; tolerance {TOL:.0%}")

    sha = {f: hashlib.sha256(p.read_bytes()).hexdigest() for f, p in files.items()}
    hits = []
    for log in sorted(RUNS.glob('*/decisions.jsonl')):
        for line in log.read_text().splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get('subject') != SUBJECT:
                continue
            src = row.get('source_sha256') or {}
            if all(src.get(f) == sha[f] for f in FACINGS):
                hits.append((log.parent.name, row))
    judged = [(run, r) for run, r in hits if r.get('decision') == 'ACCEPT'
              and not any(code in str(r.get('reasons')) for code in BANNED)]
    judge_ok = bool(judged)
    ok &= judge_ok
    if judged:
        run, row = judged[-1]
        print(f"PASS judge: run {run} decision ACCEPT on the installed shas; reasons name none of {BANNED}")
    else:
        seen = '; '.join(f"{run}: {r.get('decision')} {r.get('reasons')}" for run, r in hits) or 'no row judged these shas'
        print(f"FAIL judge: no ACCEPT without {BANNED} on the installed shas ({seen})")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
