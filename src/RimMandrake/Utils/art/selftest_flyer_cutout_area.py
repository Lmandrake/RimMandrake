#!/usr/bin/env python3
"""selftest_flyer_cutout_area.py - the promises of design/specs/2026-11-26-flyer-cutout-area/boundary.md, one test each.

Offline, synthetic frames in a temp dir. A wing of 1 px rows in two far-apart colours is the planted fault's material:
point sampling under |sy| 0.5 skips rows and turns it to specks. The byte-identity of every set that does not opt in is
also read by selftest_flyer_tier_two.py and selftest_flyer_tier_three.py (installed frames == bake).
Exit 0 = all pass, 1 = a test failed.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import flyer_cutout as FC  # noqa: E402

TOOL = HERE / "flyer_eye_checks.py"
CUT = HERE / "flyer_cutout.py"
PREFIX = "Striped_Flying_"
N = 5
SIZE = 128
WING = {"poly": [[0, 28], [54, 28], [54, 102], [0, 102]], "hinge": [54, 64], "sign": 1,
        "poses": [[0, 1, 1.0], [0, 1, 0.7], [0, 1, -0.1], [0, 1, 0.7], [0, 1, 1.0]]}
EAST = {"master": 1, "falloff": 0, "protect": [[[54, 40], [80, 40], [80, 90], [54, 90]]], "wings": [WING]}


def striped() -> Image.Image:
    im = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([54, 40, 80, 90], fill=(90, 90, 90, 255))
    for y in range(30, 100):
        d.line([(6, y), (53, y)], fill=(250, 240, 230, 255) if y % 2 else (20, 10, 60, 255))
    return im


def seed(t: Path) -> Path:
    src = t / "src"
    src.mkdir(exist_ok=True)
    m = striped()
    m.save(src / "master.png")
    for k in range(1, N + 1):
        m.save(src / f"{PREFIX}{k}_east.png")
    return src


def tool(t: Path, cfg: dict, *args) -> tuple[int, str]:
    path = t / "cfg.json"
    path.write_text(json.dumps(cfg))
    r = subprocess.run([sys.executable, str(TOOL), args[0], str(path), *args[1:]], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def cfg(**east) -> dict:
    return {"set": "Striped", "prefix": PREFIX, "facings": {"east": dict(EAST, **east)}}


def t_a_facing_without_area_bakes_as_before(t: Path) -> list[str]:
    layer = np.asarray(striped())
    body = np.zeros(layer.shape[:2], bool)
    body[40:91, 54:81] = True
    bad = [f"area off is not one sample per pixel at sy {sy}" for sy in (1.0, 0.7, 0.45, -0.1)
           if FC.area_rows(sy, False) != 1
           or not np.array_equal(FC.bend(layer, body, (54, 64), 3, 1, sy, 8),
                                 FC.bend(layer, body, (54, 64), 3, 1, sy, 8, False))]
    bad += [f"area on at sy {sy} took {FC.area_rows(sy, True)} rows" for sy in (1.0, 0.7, 0.5) if FC.area_rows(sy, True) != 1]
    return bad


def t_a_squashed_pose_with_area_reads_every_row(t: Path) -> list[str]:
    src = seed(t)
    out = []
    rc, txt = tool(t, cfg(), "alias", "--src", str(src))
    if not (rc == 1 and "ALIAS   Striped: RED" in txt):
        out.append("point-sampled squash is not RED: " + txt)
    rc, txt = tool(t, cfg(area=True), "alias", "--src", str(src))
    if not (rc == 0 and "ALIAS   Striped: GREEN" in txt):
        out.append("area-sampled squash is not GREEN: " + txt)
    return out


def t_the_squash_row_honours_area(t: Path) -> list[str]:
    src = seed(t)
    out = []
    for c, want in ((cfg(), "SQUASH  RED, east wing 0: frame 3 sy -0.1"), (cfg(area=True), "SQUASH  GREEN")):
        (t / "sq.json").write_text(json.dumps(c))
        r = subprocess.run([sys.executable, str(TOOL), "audit", str(src), "--prefix", PREFIX, "--n", str(N),
                            "--config", str(t / "sq.json")], capture_output=True, text=True)
        if want not in r.stdout:
            out.append(f"want {want!r}: {r.stdout[-300:]}")
    return out


def t_build_re_bakes_from_the_recorded_source(t: Path) -> list[str]:
    src = seed(t)
    spec = {"path": str(src / "master.png"), "rev": None, "pad": 0}
    c = cfg(area=True, source=spec, master=3)        # frame 3 of src is not the master: the source must win
    Image.new("RGBA", (SIZE, SIZE), (255, 0, 0, 255)).save(src / f"{PREFIX}3_east.png")
    (t / "b.json").write_text(json.dumps(dict(c, folder=str(src))))
    out_dir = t / "built"
    r = subprocess.run([sys.executable, str(CUT), "build", str(t / "b.json"), "--src", str(src), "--out", str(out_dir)],
                       capture_output=True, text=True)
    want, _, _ = FC.compose_facing(FC.source_master(spec, SIZE), c["facings"]["east"], N)
    got = [np.asarray(Image.open(out_dir / f"{PREFIX}{k}_east.png").convert("RGBA")) for k in range(1, N + 1)] \
        if (out_dir / f"{PREFIX}1_east.png").exists() else []
    if len(got) != N or not all(np.array_equal(a, b) for a, b in zip(got, want)):
        return [f"build did not bake from the source (rc {r.returncode}): {r.stdout[-200:]}{r.stderr[-300:]}"]
    soft = np.array(striped())
    soft[60, 70, 3] = 251                            # a resampled body pixel
    Image.fromarray(soft, "RGBA").save(src / "soft.png")
    m = FC.source_master({"path": str(src / "soft.png"), "rev": None, "pad": 0, "opaque_from": 250}, SIZE)
    if m[60, 70, 3] != 255 or m[0, 0, 3] != 0:
        return [f"opaque_from 250 did not make alpha 251 solid (got {m[60, 70, 3]}) or touched clear pixels"]
    return []


def t_the_baked_row_reads_the_shipped_frames(t: Path) -> list[str]:
    src = seed(t)
    spec = {"path": str(src / "master.png"), "rev": None, "pad": 0}
    c = cfg(area=True, source=spec)
    baked, _, _ = FC.compose_facing(FC.source_master(spec, SIZE), c["facings"]["east"], N)
    good = t / "baked"
    good.mkdir(exist_ok=True)
    for k, fr in enumerate(baked, 1):
        Image.fromarray(fr, "RGBA").save(good / f"{PREFIX}{k}_east.png")
    out = []
    rc, txt = tool(t, c, "alias", "--src", str(good))
    if not (rc == 0 and "BAKED   Striped east: GREEN" in txt):
        out.append("the area bake does not read BAKED GREEN: " + txt)
    bad = np.array(baked[2])
    bad[64, 20] = (255, 0, 0, 255)
    Image.fromarray(bad, "RGBA").save(good / f"{PREFIX}3_east.png")
    rc, txt = tool(t, c, "alias", "--src", str(good))
    if not (rc == 1 and "BAKED   Striped east: RED, frames [3]" in txt):
        out.append("one changed pixel does not read BAKED RED: " + txt)
    return out


def t_a_facing_it_cannot_read_is_unmeasured(t: Path) -> list[str]:
    (t / "empty").mkdir(exist_ok=True)
    rc, txt = tool(t, cfg(), "alias", "--src", str(t / "empty"))
    return [] if rc == 2 and "UNMEASURED" in txt and "GREEN" not in txt else ["an unreadable facing is not UNMEASURED: " + txt]


def bellied() -> Image.Image:
    """A body with a pale belly that bulges past the protect box into a brown wing's polygon (the Porg rip)."""
    im = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([20, 30, 60, 100], fill=(110, 80, 50, 255))                      # brown wing, folded at the side
    d.ellipse([44, 30, 100, 100], fill=(200, 196, 190, 255))                       # pale belly, wider than the box
    return im


BELLY_CFG = {"master": 1, "falloff": 0, "protect": [[[60, 30], [100, 30], [100, 100], [60, 100]]],
             "wings": [{"poly": [[0, 20], [60, 20], [60, 110], [0, 110]], "hinge": [58, 40], "sign": 1,
                        "poses": [[30, 1, 1.0]] * N}]}


def t_keep_pale_keeps_the_belly_in_the_plate(t: Path) -> list[str]:
    m = np.asarray(bellied())
    rule = {"min_value": 140, "max_sat": 0.16}
    _, w0 = FC.split(m, BELLY_CFG)
    plate, w1 = FC.split(m, dict(BELLY_CFG, keep_pale=rule))
    pale = (m[..., :3].min(-1) > 180) & (m[..., 3] > 0)
    before, after = int(((w0[0][..., 3] > 0) & pale).sum()), int(((w1[0][..., 3] > 0) & pale).sum())
    brown_kept = int(((w1[0][..., 3] > 0) & ~pale).sum()) == int(((w0[0][..., 3] > 0) & ~pale).sum())
    out = []
    if not (before > 100 and after == 0):
        out.append(f"belly in the wing layer: {before} px without keep_pale, {after} with it (want >100, then 0)")
    if not brown_kept:
        out.append("keep_pale moved brown wing pixels out of the wing layer")
    return out


def t_a_wing_layer_carrying_belly_is_red(t: Path) -> list[str]:
    src = t / "src"
    src.mkdir()
    for k in range(1, N + 1):
        bellied().save(src / f"{PREFIX}{k}_east.png")
    out = []
    for c, rc_want, word in ((BELLY_CFG, 1, "RED"), (dict(BELLY_CFG, keep_pale={"min_value": 140, "max_sat": 0.16}), 0, "GREEN")):
        rc, txt = tool(t, {"set": "Striped", "prefix": PREFIX, "facings": {"east": c}}, "belly", "--src", str(src))
        if rc != rc_want or f"east wing 0: {word}" not in txt:
            out.append(f"want {word} (exit {rc_want}), got exit {rc}: {txt}")
    rc, txt = tool(t, {"set": "Striped", "prefix": PREFIX, "facings": {"east": BELLY_CFG}}, "belly", "--src", str(t / "none"))
    if rc != 2 or "UNMEASURED" not in txt:
        out.append(f"no frames is not UNMEASURED: exit {rc}: {txt}")
    return out


def main() -> int:
    fails = 0
    for test in (t_a_facing_without_area_bakes_as_before, t_a_squashed_pose_with_area_reads_every_row,
                 t_the_squash_row_honours_area, t_build_re_bakes_from_the_recorded_source,
                 t_the_baked_row_reads_the_shipped_frames, t_a_facing_it_cannot_read_is_unmeasured,
                 t_keep_pale_keeps_the_belly_in_the_plate, t_a_wing_layer_carrying_belly_is_red):
        with tempfile.TemporaryDirectory() as d:
            errs = test(Path(d))
        print(("FAIL " if errs else "ok   ") + test.__name__ + "".join("\n     " + e for e in errs))
        fails += bool(errs)
    print(f"selftest_flyer_cutout_area: {'FAIL' if fails else 'PASS'} ({fails} failed)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
