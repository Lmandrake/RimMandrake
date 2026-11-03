#!/usr/bin/env python3
"""texregen_gaps_check.py — are the 18 biome art gaps of 2026-10-18 closed?

Item TEXREGEN_GAPS_REDRAW_EIGHTEEN_QUEUED. The gap list is
design/RimMandrake/biome_texture_regen_jobs_2026-10-18.json (one artpipe job per
def). A gap is closed when the def, as written in src/, draws a picture that is:

  1. ours    — the texPath resolves to PNG(s) inside the def's OWN mod Textures/
               (a donor path such as swresource/ or StandIn/ resolves nowhere there);
  2. drawn   — not a geometric placeholder (>= MIN_COLOURS distinct RGBA colours);
  3. its own — no other of the 18 defs draws the same file (the relic and the raw
               salt once shared one crystal; the lure organ once wore a fish);
  4. judged  — design/RimMandrake/texregen_gaps_verdicts_2026-11-03.json holds a
               `pass` verdict on exactly these bytes (sha256 of the file on disk).

Exit 0 when all 18 hold, 1 when any fails (one line per failure), 2 on a broken
input. Read-only; stdlib plus Pillow.
"""
from __future__ import annotations

import glob
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
JOBS = ROOT / "design/RimMandrake/biome_texture_regen_jobs_2026-10-18.json"
VERDICTS = ROOT / "design/RimMandrake/texregen_gaps_verdicts_2026-11-03.json"
MIN_COLOURS = 64


def find_defs(names: set[str]) -> dict[str, tuple[str, str, str | None]]:
    """defName -> (mod, texPath, graphicClass) for every name, from src/ XML."""
    out: dict[str, tuple[str, str, str | None]] = {}
    for f in glob.glob(str(ROOT / "src/**/Defs/**/*.xml"), recursive=True):
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for e in root:
            n = e.findtext("defName")
            if n not in names:
                continue
            g = e.find("graphicData")
            tp = g.findtext("texPath") if g is not None else None
            if tp is None:
                continue
            mod = Path(f).relative_to(ROOT / "src").parts[1]
            out[n] = (mod, tp.strip(), g.findtext("graphicClass"))
    return out


def resolve(mod: str, tp: str) -> list[Path]:
    base = ROOT / "src/RimMandrake" / mod / "Textures" / tp
    single = base.with_name(base.name + ".png")
    hits = [single] if single.is_file() else []
    if base.is_dir():
        hits += sorted(p for p in base.glob("*.png") if not p.name.endswith(("_m.png",)))
    return hits


def colours(p: Path) -> int:
    from PIL import Image
    c = Image.open(p).convert("RGBA").getcolors(1 << 24)
    return len(c) if c else 1 << 24


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    try:
        jobs = json.loads(JOBS.read_text())
        verdicts = {v["def"]: v for v in json.loads(VERDICTS.read_text())["verdicts"]}
    except (OSError, ValueError, KeyError) as exc:
        print(f"BROKEN input: {exc}")
        return 2
    names = {j["target_def"] for j in jobs}
    if len(names) != 18:
        print(f"BROKEN: expected 18 target defs, the jobs file names {len(names)}")
        return 2
    defs = find_defs(names)
    fails: list[str] = []
    owner_of: dict[Path, str] = {}
    for n in sorted(names):
        if n not in defs:
            fails.append(f"{n}: no def with a graphicData texPath under src/")
            continue
        mod, tp, _gc = defs[n]
        files = resolve(mod, tp)
        if not files:
            fails.append(f"{n}: texPath {tp} resolves to no PNG in src/RimMandrake/{mod}/Textures (donor or missing)")
            continue
        for p in files:
            k = colours(p)
            if k < MIN_COLOURS:
                fails.append(f"{n}: {p.relative_to(ROOT)} has {k} colours — a placeholder")
            if p in owner_of:
                fails.append(f"{n}: shares {p.relative_to(ROOT)} with {owner_of[p]}")
            owner_of.setdefault(p, n)
        v = verdicts.get(n)
        if v is None:
            fails.append(f"{n}: no judge verdict")
            continue
        if v.get("verdict") != "pass":
            fails.append(f"{n}: verdict is {v.get('verdict')!r}, not pass")
        judged = {v.get("sha256")} | set(v.get("sha256s", []))
        for p in files:
            if sha(p) not in judged:
                fails.append(f"{n}: {p.relative_to(ROOT)} bytes are not the judged bytes")
    for line in fails:
        print("FAIL", line)
    print(f"{'PASS' if not fails else 'FAIL'}: {18 - len({f.split(':')[0] for f in fails})}/18 gaps closed")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
