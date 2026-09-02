#!/usr/bin/env python3
"""Assemble one sea beast's shipping facing set from its raws.

west  = the owner's KEPT mockup, chroma-keyed and fitted (it is already a
        left-facing side profile, which is what Rot4.West means)
east  = west mirrored
south = Transient/sea_raw/<Slug>_south_raw.png, chroma-keyed and fitted
north = same, north

All four land on one canvas at one animal size, then seacheck.py grades the set.

    python3 build_sea_facings.py CrimsonOpee [...]
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sea_creatures import CREATURES, FINAL, MOCKUPS, RAW, canvas_for  # noqa: E402

HERE = Path(__file__).resolve().parent
SKILLS = Path("/mnt/d/Luke/dev/Rimworld/skills")
CHROMA = SKILLS / "generating-images/scripts/chroma_key.py"
SHEET = SKILLS / "generating-rimworld-sprites/scripts/contact_sheet.py"


def run(*args):
    r = subprocess.run([sys.executable, *[str(a) for a in args]],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"FAILED: {' '.join(str(a) for a in args)}\n{r.stderr}")
    return r.stdout


def build(slug: str) -> int:
    stem, draw, _ = CREATURES[slug]
    n = canvas_for(draw)
    mock = Path(MOCKUPS) / f"{stem}.png"
    raw = Path(RAW)
    out = Path(FINAL) / slug
    out.mkdir(parents=True, exist_ok=True)

    cut = raw / f"{stem}_cut.png"
    if not cut.exists():
        run(CHROMA, "--input", mock, "--out", cut)
    run(HERE / "seafit.py", "--input", cut, "--out", out / f"{slug}_west.png",
        "--canvas", n)
    run(HERE / "seafit.py", "--input", out / f"{slug}_west.png",
        "--out", out / f"{slug}_east.png", "--canvas", n, "--mirror")

    for facing in ("south", "north"):
        src = raw / f"{slug}_{facing}_raw.png"
        if not src.exists():
            print(f"MISSING {src.name} - not built", file=sys.stderr)
            return 2
        cutf = raw / f"{slug}_{facing}_cut.png"
        if not cutf.exists():
            run(CHROMA, "--input", src, "--out", cutf)
        run(HERE / "seafit.py", "--input", cutf,
            "--out", out / f"{slug}_{facing}.png", "--canvas", n)

    run(SHEET, "--out", out / f"{slug}_contact_sheet.png", "--reference", mock,
        *[out / f"{slug}_{f}.png" for f in ("south", "east", "north", "west")])

    print(f"[{slug}] canvas {n} (drawSize {draw} x 128 = {int(draw*128)})")
    r = subprocess.run([sys.executable, str(HERE / "seacheck.py"), str(out)],
                       text=True)
    return r.returncode


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    worst = 0
    for slug in sys.argv[1:]:
        if slug not in CREATURES:
            print(f"unknown slug {slug}", file=sys.stderr)
            return 2
        worst = max(worst, build(slug))
    return worst


if __name__ == "__main__":
    sys.exit(main())
