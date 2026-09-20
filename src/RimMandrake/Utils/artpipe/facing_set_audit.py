#!/usr/bin/env python3
"""Full metric audit for a creature FACING SET at wiring time.

Owner ruling 2026-09-16: "wire in the full metric check not just the size."
The sprite validator's structural gates run per file; this instrument runs
the CROSS-FACING checks nothing else owns, plus the per-file gates, so one
command answers "is this set wireable" with measurements instead of memory:

  per file    : canvas, real alpha, corners clear, faint-fringe %, mid-alpha
                band %, opaque coverage sanity
  across set  : canvas uniformity; major-axis size spread (the
                anooba-looks-huge class, flag > 15%); mean-RGB palette
                distance between facings (the mantis-east-wrong-colour
                class, flag > 40); bottom-anchor drift (creatures must sit
                at comparable height in the tile, flag > 12% of canvas);
                sha256 pairwise duplicates (the anooba-female-was-the-male
                class)
  viewpoint   : ⚠️ ADVISORY ONLY since 2026-09-20 — it does NOT gate.
                The south facing is supposed to be eye-level and face-forward
                (the mantistanis/firewasp/furnace-beast top-down-south class,
                owner 2026-09-17), and no pixel statistic separates it, so the
                judge is a `claude -p` vision call. But RE-CALIBRATED against
                DONOR art our pipeline has never touched, that judge returns
                south-OVERHEAD for 5 of 6 sets (83%) — a higher rate than our
                own art scores — so it is measuring "RimWorld animal art",
                whose camera is a high three-quarter view by design. It is a
                shortlist for a human look, never a pass/fail. See
                viewpoint_south()'s docstring for the evidence.
                UNMEASURED (claude unavailable) IS still a flag: ignorance is
                never a silent pass. --no-llm skips it and says so.

Exit 0 = every gate green. Exit 1 = at least one FLAG (wiring should stop
and a human look). Numbers are printed either way — this reports, the
human rules.

Usage:
  python3 facing_set_audit.py <north.png> <south.png> <east.png> [west.png]
  python3 facing_set_audit.py --set <dir-or-glob-prefix>   # finds *_north/_south/_east
  python3 facing_set_audit.py --no-llm <...>               # offline: skip viewpoint
"""
import hashlib
import subprocess
import sys
from pathlib import Path

from PIL import Image

SIZE_SPREAD_FLAG = 15.0     # percent, major-axis across facings
PALETTE_DIST_FLAG = 40.0    # mean-RGB euclidean distance between facings
ANCHOR_DRIFT_FLAG = 12.0    # percent of canvas height, bbox bottom edge
FRINGE_FLAG = 2.0           # percent of pixels at alpha 1..31
MIDALPHA_FLAG = 10.0        # percent of pixels at alpha 32..223
COVERAGE_RANGE = (2.0, 85.0)
VIEWPOINT_TIMEOUT_S = 150   # claude -p is the ruled LLM transport; it can stall

VIEWPOINT_PROMPT = (
    "Read the image file {path} . It is a creature sprite for a top-down colony "
    "game, meant to be the SOUTH facing: the creature seen from directly ahead "
    "at roughly eye level, face and chest toward the viewer. Judge the CAMERA "
    "ELEVATION actually drawn. Answer exactly one word: EYELEVEL (you mainly "
    "see the face, chest, front of the body; the back is hidden) or OVERHEAD "
    "(you mainly see the top of the head, spine, back, shell or shoulders — "
    "looking down on the creature). One word only."
)


def viewpoint_south(path):
    """EYELEVEL | OVERHEAD | UNMEASURED — ADVISORY ONLY, never a blocking flag.

    🔴 RE-CALIBRATED 2026-09-20 against a control the 2026-09-17 pass did not
    have, and the result reverses its conclusion. That pass used 15 of OUR OWN
    wired Pyrelands sets and reported "0 false flags on the 10 clean fronts".
    But our art is the art under suspicion, so it cannot calibrate its own
    judge. Run against DONOR art from SWBestiary — sprites the donor mod ships
    and our pipeline has never touched — the judge returns:

        5 of 6 donor sets judged south-OVERHEAD (83%)

    which is a HIGHER fail rate than our own art scored in the same sitting
    (33 of 50, 66%). ⇒ The judge is measuring "RimWorld animal art", whose
    camera is a high three-quarter view by design, not measuring our defect.
    Evidence: Transient/viewpoint_judge_calibration_20260920.txt.

    Corroborated independently the same day: the art agent auditing all 50
    flagged sets re-checked the judge's 33 OVERHEAD verdicts BY LOOKING and
    kept only 12 — 21 were a legitimate front-lunge/roar predator pose and 5
    were faceless body plans no camera angle can resolve.

    ⛔ So this verdict must never gate wiring on its own, and nobody should arm
    it as one. It is a SHORTLIST for a human look: useful for ranking which
    souths to eyeball first, worthless as a pass/fail. The owner's complaint
    is real and specific; this judge cannot find it unaided.
    """
    try:
        out = subprocess.run(
            ["claude", "-p", VIEWPOINT_PROMPT.format(path=path)],
            capture_output=True, text=True, timeout=VIEWPOINT_TIMEOUT_S)
        word = (out.stdout or "").strip().split()[-1].upper() if out.stdout.strip() else ""
        if word in ("EYELEVEL", "OVERHEAD"):
            return word
        return "UNMEASURED"
    except (OSError, subprocess.TimeoutExpired):
        return "UNMEASURED"


def measure(path):
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    px = im.load()
    alpha = im.split()[3]
    hist = alpha.histogram()
    total = w * h
    opaque = sum(hist[224:])
    fringe = sum(hist[1:32]) / total * 100
    mid = sum(hist[32:224]) / total * 100
    coverage = opaque / total * 100
    bbox = alpha.point(lambda a: 255 if a > 127 else 0).getbbox()
    corners = all(px[x, y][3] == 0 for x in (0, w - 1) for y in (0, h - 1))
    r = g = b = n = 0
    if bbox:
        small = im.crop(bbox)
        small.thumbnail((96, 96))
        for pr, pg, pb, pa in small.getdata():
            if pa > 127:
                r += pr; g += pg; b += pb; n += 1
    mean_rgb = (r / n, g / n, b / n) if n else (0, 0, 0)
    return {
        "path": str(path), "size": (w, h),
        "sha": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        "corners_clear": corners, "fringe": fringe, "mid": mid,
        "coverage": coverage, "bbox": bbox,
        "major": max(bbox[2] - bbox[0], bbox[3] - bbox[1]) if bbox else 0,
        "bottom_pct": (bbox[3] / h * 100) if bbox else 0,
        "mean_rgb": mean_rgb,
    }


def main(argv):
    args = argv[1:]
    no_llm = "--no-llm" in args
    args = [a for a in args if a != "--no-llm"]
    if args and args[0] == "--set":
        stem = args[1]
        paths = []
        for f in ("north", "south", "east", "west"):
            hits = sorted(Path(".").glob(f"{stem}*{f}*.png")) or \
                   sorted(Path(stem).glob(f"*{f}*.png") if Path(stem).is_dir() else [])
            if hits:
                paths.append(hits[-1])
    else:
        paths = [Path(p) for p in args]
    if len(paths) < 2:
        print("need at least two facings"); return 2

    ms = [measure(p) for p in paths]
    flags = []
    advisories = []

    for m in ms:
        name = Path(m["path"]).name
        if not m["bbox"]:
            flags.append(f"{name}: EMPTY (no opaque pixels)")
        if not m["corners_clear"]:
            flags.append(f"{name}: corner not transparent")
        if m["fringe"] > FRINGE_FLAG:
            flags.append(f"{name}: faint-fringe {m['fringe']:.2f}% > {FRINGE_FLAG}%")
        if m["mid"] > MIDALPHA_FLAG:
            flags.append(f"{name}: mid-alpha wash {m['mid']:.1f}% > {MIDALPHA_FLAG}%")
        if not (COVERAGE_RANGE[0] <= m["coverage"] <= COVERAGE_RANGE[1]):
            flags.append(f"{name}: coverage {m['coverage']:.1f}% outside {COVERAGE_RANGE}")

    # RimWorld sprites legitimately TRANSPOSE between facings — vanilla's own
    # AutomatedSmelter is 512x640 north/south and 640x512 east/west. So the gate is
    # "every canvas is the same set of two edge lengths", not "every canvas is
    # identical": {(512,640),(640,512)} passes, {(512,640),(512,512)} does not.
    # Measured 2026-09-20: the identity form false-flagged AutomatedSmelter, whose
    # art is correct and whose transposition the sprite skill documents.
    if len({tuple(sorted(m["size"])) for m in ms}) > 1:
        flags.append("canvas sizes differ across facings (beyond transposition): " +
                     ", ".join(f"{Path(m['path']).name}={m['size']}" for m in ms))

    majors = [m["major"] for m in ms if m["major"]]
    if majors:
        spread = (max(majors) - min(majors)) / (sum(majors) / len(majors)) * 100
        if spread > SIZE_SPREAD_FLAG:
            flags.append(f"size spread {spread:.1f}% > {SIZE_SPREAD_FLAG}%")
    else:
        spread = 0.0

    for i in range(len(ms)):
        for j in range(i + 1, len(ms)):
            a, b = ms[i], ms[j]
            if a["sha"] == b["sha"]:
                flags.append(f"BYTE-IDENTICAL: {Path(a['path']).name} == {Path(b['path']).name}")
            d = sum((x - y) ** 2 for x, y in zip(a["mean_rgb"], b["mean_rgb"])) ** 0.5
            if d > PALETTE_DIST_FLAG:
                flags.append(f"palette distance {d:.0f} > {PALETTE_DIST_FLAG}: "
                             f"{Path(a['path']).name} vs {Path(b['path']).name}")

    bottoms = [m["bottom_pct"] for m in ms if m["bbox"]]
    if bottoms and max(bottoms) - min(bottoms) > ANCHOR_DRIFT_FLAG:
        flags.append(f"bottom-anchor drift {max(bottoms)-min(bottoms):.1f}% > {ANCHOR_DRIFT_FLAG}%")

    souths = [m["path"] for m in ms if "south" in Path(m["path"]).name.lower()]
    if no_llm:
        print("viewpoint check SKIPPED (--no-llm) — south camera elevation not judged")
    else:
        for sp in souths:
            v = viewpoint_south(sp)
            if v == "OVERHEAD":
                # ADVISORY, not a flag — see viewpoint_south()'s docstring: this
                # judge fails 83% of DONOR art it has never seen our pipeline touch,
                # so a FLAG here would refuse the sprites the game itself ships.
                advisories.append(
                    f"{Path(sp).name}: south reads as OVERHEAD to the judge — ADVISORY, "
                    f"look at it yourself before believing it (83% false-positive rate "
                    f"measured against donor art 2026-09-20)")
            elif v == "UNMEASURED":
                # UNMEASURED stays a FLAG: ignorance is never a silent pass.
                flags.append(f"{Path(sp).name}: south viewpoint UNMEASURED (claude -p unavailable) — judge by eye")

    print(f"{'file':44s} {'canvas':>9s} {'major':>6s} {'cov%':>6s} {'fringe%':>8s} {'meanRGB':>13s}")
    for m in ms:
        print(f"{Path(m['path']).name:44s} {str(m['size']):>9s} {m['major']:6d} "
              f"{m['coverage']:6.1f} {m['fringe']:8.2f} "
              f"{','.join(str(int(c)) for c in m['mean_rgb']):>13s}")
    print(f"size spread {spread:.1f}%  |  anchor drift "
          f"{(max(bottoms)-min(bottoms)) if bottoms else 0:.1f}%")

    if advisories:
        print("\nADVISORY (a human look, never a gate):")
        for a in advisories:
            print("  NOTE", a)

    if flags:
        print("\nFLAGS:")
        for f in flags:
            print("  FLAG", f)
        return 1
    if advisories:
        print("\nPASS on every gate — the advisory above is not one.")
        return 0
    print("\nPASS — full metric gate green.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
