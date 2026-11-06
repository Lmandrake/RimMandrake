#!/usr/bin/env python3
"""Offline proof for SHIRO_REDRAW_CANON_PAINTERLY: a new RSW_Shiro body set, judged ACCEPT by art_eval, installed.

Exit 0 only when ALL hold:
  1. a committed art_eval production run (infrastructure/state/art_eval/runs/*/decisions.jsonl, not --test) holds a
     decision for subject RSW_Shiro with decision ACCEPT whose artpipe job came from this item's redraw series
     (shiro_redraw_canon_painterly_* or its art_eval regens arteval_RSW_Shiro_*), and its source_sha256 names the
     south, east and north pictures it judged;
  2. the installed body set src/RimStarWars/SWBestiary/Textures/RimStarWars/SWBestiary/Shiro/Shiro_{south,east,north}.png
     is byte-identical (sha256) to those judged pictures;
  3. none of the three is the pre-item art (shas recorded 2026-11-05 before the redraw);
  4. each is a 512x512 RGBA PNG with real transparency (some alpha 0, some alpha 255).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TEX = ROOT / "src/RimStarWars/SWBestiary/Textures/RimStarWars/SWBestiary/Shiro"
RUNS = ROOT / "infrastructure/state/art_eval/runs"
FACINGS = ("south", "east", "north")
PRE_ITEM = {
    "east": "4348fa036025054c93ee477d90891e1e6538ada0bc32861d4321471014255dd3",
    "north": "ccac63128766fa94d1bb3e16d96b15550016c06bc94182f0c1c152e7225ccd1e",
    "south": "5fe9a03867f0373a780df923e4f4782f67ae3da6b0cdada4441fb622bfbd2396",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def accepted() -> list[tuple[str, dict]]:
    out = []
    for run in sorted(RUNS.iterdir()):
        meta, dec = run / "run.json", run / "decisions.jsonl"
        if not dec.is_file():
            continue
        if meta.is_file() and json.loads(meta.read_text()).get("test"):
            continue
        for line in dec.read_text().splitlines():
            if not line.strip():
                continue
            d = json.loads(line)
            job = str(d.get("artpipe_job") or "")
            if (d.get("subject") == "RSW_Shiro" and d.get("decision") == "ACCEPT"
                    and (job.startswith("shiro_redraw_canon_painterly") or job.startswith("arteval_RSW_Shiro_"))):
                out.append((run.name, d))
    return out


def main() -> int:
    fails = []
    installed = {}
    for f in FACINGS:
        p = TEX / f"Shiro_{f}.png"
        if not p.is_file():
            fails.append(f"missing {p}")
            continue
        installed[f] = sha(p)
        if installed[f] == PRE_ITEM[f]:
            fails.append(f"{f}: still the pre-item art")
        try:
            from PIL import Image
            im = Image.open(p)
            if im.size != (512, 512) or im.mode != "RGBA":
                fails.append(f"{f}: {im.size} {im.mode}, want 512x512 RGBA")
            else:
                lo, hi = im.getchannel("A").getextrema()
                if lo != 0 or hi != 255:
                    fails.append(f"{f}: alpha range {lo}..{hi}, want real transparency")
        except ImportError:
            fails.append("PIL missing: cannot check canvas")
    acc = accepted()
    match = None
    for run, d in acc:
        src = d.get("source_sha256") or {}
        if all(src.get(f) and src.get(f) == installed.get(f) for f in FACINGS):
            match = (run, d)
    if not acc:
        fails.append("no committed production ACCEPT decision for RSW_Shiro from this redraw series")
    elif match is None:
        fails.append(f"installed shas {installed} match no ACCEPT decision's judged pictures "
                     f"({[(r, d.get('source_sha256')) for r, d in acc]})")
    for f, h in installed.items():
        print(f"installed Shiro_{f}.png sha256={h}")
    if match:
        print(f"judged ACCEPT in run {match[0]} job {match[1].get('artpipe_job')}")
    if fails:
        print("FAIL: " + "; ".join(fails))
        return 1
    print("PASS: new RSW_Shiro body set judged ACCEPT and installed byte-identical")
    return 0


if __name__ == "__main__":
    sys.exit(main())
