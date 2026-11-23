#!/usr/bin/env python3
"""Conform each generated tank (raw/) to the shipped 512x512 RM_LiquidTank canvas, validate it, check its two end pipe
ports, and draw the judge panels (true scale at 64 px/cell beside a vanilla human and the accepted Scrapper tank, plus a
32 px/cell play-zoom strip).

    process_tanks.py [NAME ...]     -> generated/options/<name>.png, generated/panels/, generated/report.json
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
SKILL = REPO / "skills/generating-rimworld-sprites/scripts"
SCRAPPER = REPO / "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks/Tank/Scrapper/RM_LiquidTank.png"
sys.path.insert(0, str(HERE.parent))
import judge_panels  # noqa: E402

RAW, OPT, PAN = HERE / "raw", HERE / "options", HERE / "panels"


def ports(png):
    """The shipped tanks carry one pipe port centred on each end cap: solid alpha within 6 px of the left and right
    canvas edges, in the middle band of the subject's height. Returns (left_ok, right_ok, rows)."""
    a = np.asarray(Image.open(png).convert("RGBA"))[..., 3]
    ys = np.where(a.max(axis=1) > 128)[0]
    top, bot = ys.min(), ys.max()
    band = slice(top + (bot - top) // 4, bot - (bot - top) // 4)
    left = (a[band, :6] > 128).any(axis=1)
    right = (a[band, -6:] > 128).any(axis=1)
    return bool(left.any()), bool(right.any()), [int(top), int(bot)]


def alpha_board(png, out):
    """The PNG over a grey checkerboard, uncomposited, so real alpha (no backdrop, halo or shadow) is visible."""
    im = Image.open(png).convert("RGBA")
    bg = Image.new("RGBA", im.size)
    px = bg.load()
    for y in range(im.height):
        for x in range(im.width):
            px[x, y] = (200, 200, 200, 255) if ((x // 16) + (y // 16)) % 2 else (150, 150, 150, 255)
    bg.alpha_composite(im)
    bg.save(out)


def play_zoom(png, out):
    """The tank at 32 px/cell (64 px) and 64 px/cell (128 px) on desert ground beside the Scrapper tank."""
    T = (124, 100, 72, 255)
    W = Image.new("RGBA", (64 + 64 + 128 + 128 + 50, 140), T)
    x = 10
    for p, s in ((SCRAPPER, 64), (png, 64), (SCRAPPER, 128), (png, 128)):
        im = Image.open(p).convert("RGBA").resize((s, s), Image.LANCZOS)
        W.alpha_composite(im, (x, 136 - s)); x += s + 10
    W.save(out)


FIDELITY = ("subject height", "subject width", "subject aspect", "subject origin", "exceeds the reference")


def check(out):
    """The restyle gate on a conformed PNG. A restyle is a new drawing, so the reference-fidelity family (span, aspect,
    origin, height past the reference) is the wrong check (generating-rimworld-sprites SKILL; the shipped Industrial,
    Modern and Futuristic tanks fail it against Scrapper too). Every other REJECT (canvas, alpha, corners, fringe,
    mid-alpha, identity) blocks, and both end ports must be present. validate_sprite prints findings on stderr."""
    v = subprocess.run([sys.executable, str(SKILL / "validate_sprite.py"), "--reference", str(SCRAPPER),
                        "--candidate", str(out), "--drawsize", "2"], capture_output=True, text=True)
    lines = [s.strip() for s in (v.stdout + v.stderr).splitlines() if s.strip()]
    blocking = [s for s in lines if s.startswith("REJECT") and not any(f in s for f in FIDELITY)]
    l, r, span = ports(out)
    return {"validate_rc": v.returncode, "restyle_blocking": blocking,
            "findings": [s for s in lines if s.startswith(("REJECT", "WARN"))],
            "port_left": l, "port_right": r, "subject_rows": span, "restyle_ok": (not blocking) and l and r}


def width_fit(raw, out, cy=262):
    """Fit the drawing so its end ports touch both canvas edges (x 1..510), the way the shipped tanks meet their
    neighbouring pipe cells. conform_sprite fits a reference's AREA, which leaves a taller-than-Scrapper design short of
    the edges. Scaled once from the raw drawing, premultiplied (no dark halo), centred on the Scrapper's centroid row."""
    im = Image.open(raw).convert("RGBA")
    a = np.asarray(im)[..., 3]
    ys, xs = np.where(a > 8)
    sub = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    w = 510
    h = round(sub.height * w / sub.width)
    if h > 500:
        raise SystemExit(f"{raw}: width-fit would be {h} px tall, past the canvas")
    sub = sub.convert("RGBa").resize((w, h), Image.LANCZOS).convert("RGBA")
    canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    canvas.alpha_composite(sub, (1, max(0, min(512 - h, cy - h // 2))))
    canvas.save(out)


def main(names):
    OPT.mkdir(exist_ok=True); PAN.mkdir(exist_ok=True)
    names = names or sorted(p.stem for p in RAW.glob("tank_*.png"))
    report = json.loads((HERE / "report.json").read_text()) if (HERE / "report.json").exists() else {}
    for n in names:
        out = OPT / f"{n}.png"
        subprocess.run([sys.executable, str(SKILL / "conform_sprite.py"), "--reference", str(SCRAPPER),
                        "--input", str(RAW / f"{n}.png"), "--out", str(out)], check=True, capture_output=True)
        report[n] = check(out)
        if not (report[n]["port_left"] and report[n]["port_right"]):
            width_fit(RAW / f"{n}.png", out)
            report[n] = check(out)
            report[n]["fit"] = "width_fit (conform left the end ports short of the edges)"
        judge_panels.tank_panel(out, 64, n.replace("tank_", "")).save(PAN / f"{n}__scale.png")
        play_zoom(out, PAN / f"{n}__zoom.png")
        judge_panels.tank_panel(out, 128, n.replace("tank_", "")).save(PAN / f"{n}__scale128.png")
        alpha_board(out, PAN / f"{n}__alpha.png")
        blocking, l, r, span = (report[n][k] for k in ("restyle_blocking", "port_left", "port_right", "subject_rows"))
        print(f"{n}: restyle_ok={report[n]['restyle_ok']} blocking={blocking} ports L={l} R={r} rows={span}")
    (HERE / "report.json").write_text(json.dumps(report, indent=1) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
