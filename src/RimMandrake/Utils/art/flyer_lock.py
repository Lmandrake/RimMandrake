#!/usr/bin/env python3
"""flyer_lock.py — lock a flyer's body so it is pixel-identical in every flight frame.

FLYER_STABLE_BODY_GATE_1; design: Transient/sketto_design_2026-10-08.md §4 stage D and §6.
A painterly generator can't hold a body still across frames (our regen frames measured
0.006–0.036 locked share, the donor 0.4–0.6). So the body comes from ONE plate per facing, and
this script pastes that same plate into every frame. Only the wings come from the generator.
Output is the 1.6 whole-body directional flip-book, `<prefix><N>_<facing>.png`. It is not a
render-tree.

Three verbs (each exits 0 = pass, 1 = a gate failed, 2 = bad input):

  lock     --plate P --frame F1 --frame F2 --frame F3 --facing east --prefix Sketto_Flying_ --out DIR
           The Sketto recipe. P is the wingless body plate. Fk are generated whole frames, one per wing
           pose (up, level, down), each edited from the same master. For each frame it:
             1. aligns the frame to the plate by translation (search ±--search px);
             2. GATES re-posing: the frame must be opaque over ≥ --min-cover of the plate's silhouette,
                or it is rejected (a moved body leaves plate pixels bare; a wing over the body does not);
             3. classes a frame pixel as WING when it is opaque and lies outside the plate, or differs
                from the plate by RGB L1 > --wing-l1. Wing pixels inside the plate count only when
                they connect to wing outside it that reaches > --wing-far (4) px from the body, and only
                within --wing-depth (12) px of that wing (option C), so re-shading speckle and the frame's
                own head/tusks/legs are not re-admitted;
             4. writes the plate's exact RGBA everywhere else.
           Frames are ping-ponged: k poses -> 2k-2 frames (3 -> 1,2,3,4 = 2, byte copy).
  compose  --body B --wing W1 --wing W2 --wing W3 --facing east --order over|under --prefix .. --out DIR
           The layer recipe (flyer study §3.1). B is the wingless body and Wk are wing-only RGBA layers.
           over = wings painted over the body, under = body over wings. Ping-pong as above.
  check    --dir DIR --prefix Sketto_Flying_ --facing east [--plate P] [--min-share X]
           The acceptance metric (design §3/§6) on any finished flip-book. LOCKED SHARE = pixels opaque
           (alpha > 128) in every frame and within RGB L1 ≤ 40 of frame 1 in every frame, divided by the
           mean opaque area of one frame. Floors (donor Sketto -> design §6): east 0.45, south 0.25,
           north 0.25 (lowered from the donor's 0.38: Sketto's wings are ~2/3 of a front/back frame, so the
           ceiling is 0.338 S / 0.318 N and plate A + rule C measure 0.279 S / 0.260 N).
           With --plate it also requires plate pixels that are never under a wing to be
           byte-identical in every frame (1.0 means the lock ran). It also checks: 256-px square RGBA,
           ≥ 6 px margin, the last frame copies its ping-pong partner, and no other neighbours are
           identical.

`lock` and `compose` run `check` on what they wrote and exit by its verdict. `--report PATH` writes
the JSON. Nothing here touches src/ Textures. Install is a separate, owner-gated step.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

OPAQUE = 128          # alpha > OPAQUE counts as body/wing (the engine's animal shader is a cutout)
LOCK_TOL = 40         # design §3: "within RGB L1 ≤ 40 of frame 1"
WING_L1 = 60          # design §4 D: a wing pixel differs from the plate by L1 > 60
WING_FAR = 4          # option C: an outside-plate wing must reach more than this many px from the body
WING_DEPTH = 12       # option C: wing pixels inside the plate count only within this many px of that wing
MIN_COVER = 0.92      # design §4 C: re-posed bodies are rejected below this
FLOORS = {"east": 0.45, "west": 0.45, "south": 0.25, "north": 0.25}   # design §6.3; S/N lowered 0.38 -> 0.25 (owner card 2026-10-09)
MARGIN = 6


def load(p) -> np.ndarray:
    return np.asarray(Image.open(p).convert("RGBA")).astype(np.int16)


def save(a: np.ndarray, p: Path) -> None:
    Image.fromarray(a.astype(np.uint8), "RGBA").save(p)


def shift(a: np.ndarray, dx: int, dy: int) -> np.ndarray:
    """Translate by (dx, dy) and fill the exposed edge with transparent pixels."""
    out = np.zeros_like(a)
    h, w = a.shape[:2]
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    out[yd, xd] = a[ys, xs]
    return out


def l1(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.abs(a[..., :3] - b[..., :3]).sum(-1)


def align(plate: np.ndarray, frame: np.ndarray, search: int = 8) -> tuple[int, int]:
    """Shift (dx, dy) of FRAME that best puts its body on the plate. The score counts plate-opaque pixels the
    shifted frame matches (opaque and L1 <= WING_L1). Ties go to the smallest shift."""
    pm = plate[..., 3] > OPAQUE
    best, best_s = (0, 0), -1
    for r in range(search + 1):          # rings outward, so ties keep the smaller shift
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if max(abs(dx), abs(dy)) != r:
                    continue
                f = shift(frame, dx, dy)
                s = int((pm & (f[..., 3] > OPAQUE) & (l1(f, plate) <= WING_L1)).sum())
                if s > best_s:
                    best, best_s = (dx, dy), s
    return best


def _dilate(m: np.ndarray) -> np.ndarray:
    o = m.copy()
    o[1:] |= m[:-1]; o[:-1] |= m[1:]; o[:, 1:] |= m[:, :-1]; o[:, :-1] |= m[:, 1:]
    return o


def reconstruct(seed: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Pixels of MASK that are 4-connected to SEED (geodesic reconstruction)."""
    cur = seed & mask
    while True:
        nxt = _dilate(cur) & mask
        if (nxt == cur).all():
            return cur
        cur = nxt


def reconstruct_n(seed: np.ndarray, mask: np.ndarray, n: int) -> np.ndarray:
    """Like reconstruct, but grows at most N pixels from SEED."""
    cur = seed & mask
    for _ in range(n):
        nxt = _dilate(cur) & mask
        if (nxt == cur).all():
            break
        cur = nxt
    return cur


def lock_frame(plate: np.ndarray, frame: np.ndarray, search: int = 8, wing_l1: int = WING_L1,
               min_cover: float = MIN_COVER, keep_isolated: bool = False,
               wing_far: int = WING_FAR, wing_depth: int = WING_DEPTH) -> tuple[np.ndarray, dict]:
    dx, dy = align(plate, frame, search)
    f = shift(frame, dx, dy)
    pm, fo = plate[..., 3] > OPAQUE, f[..., 3] > OPAQUE
    n_plate = max(int(pm.sum()), 1)
    alpha_cover = float((pm & fo).sum()) / n_plate
    body_cover = float((pm & fo & (l1(f, plate) <= wing_l1)).sum()) / n_plate   # design's literal metric, info
    cand = fo & (~pm | (l1(f, plate) > wing_l1))
    if keep_isolated:
        wing = cand
    else:
        # Option C. Outside the plate: a wing must join something reaching > wing_far px from the body.
        # Inside the plate: only pixels within wing_depth px of that wing, so a frame's own head, tusks and
        # legs (differing from the plate only by outline jitter) are never re-admitted as "wing".
        out_c = cand & ~pm
        near = pm.copy()
        for _ in range(wing_far):
            near = _dilate(near)
        wing_out = reconstruct(out_c & ~near, out_c) if wing_far else out_c
        wing = wing_out | (reconstruct_n(wing_out, cand, wing_depth) & pm)
    out = np.where(wing[..., None], f, plate)
    info = {"shift": [dx, dy], "alpha_cover": round(alpha_cover, 4), "body_cover": round(body_cover, 4),
            "wing_px": int(wing.sum()), "body_px_as_wing": int((wing & pm).sum()), "speckle_dropped": int((cand & ~wing).sum()),
            "rejected": alpha_cover < min_cover}
    return out, info


def pingpong(frames: list) -> list:
    """k poses -> 1..k then k-1..2 (3 -> [1,2,3,2])."""
    return list(frames) + list(frames[-2:0:-1])


def frame_paths(d: Path, prefix: str, facing: str) -> list[Path]:
    out, n = [], 1
    while (d / f"{prefix}{n}_{facing}.png").is_file():
        out.append(d / f"{prefix}{n}_{facing}.png")
        n += 1
    return out


def locked_share(frames: list[np.ndarray], tol: int = LOCK_TOL) -> float:
    al = [a[..., 3] > OPAQUE for a in frames]
    core = np.logical_and.reduce(al)
    for a in frames[1:]:
        core &= l1(a, frames[0]) <= tol
    mean_area = float(np.mean([m.sum() for m in al])) or 1.0
    return float(core.sum()) / mean_area


def check(frames: list[np.ndarray], facing: str, plate: np.ndarray | None = None,
          min_share: float | None = None) -> dict:
    fails, r = [], {"facing": facing, "n_frames": len(frames)}
    if len(frames) < 2:
        return {**r, "pass": False, "fails": ["fewer than 2 frames"]}
    shapes = {a.shape for a in frames}
    if len(shapes) != 1:
        return {**r, "pass": False, "fails": [f"frame sizes differ: {sorted(shapes)}"]}
    h, w, _ = frames[0].shape
    if (h, w) != (256, 256):
        fails.append(f"canvas {w}x{h}, want 256x256")
    share = locked_share(frames)
    floor = FLOORS.get(facing, 0.25) if min_share is None else min_share
    r.update(locked_share=round(share, 4), floor=floor)
    if share < floor:
        fails.append(f"locked share {share:.3f} < floor {floor}")
    for i, a in enumerate(frames, 1):
        ys, xs = np.nonzero(a[..., 3] > 0)
        if len(ys) and min(ys.min(), xs.min(), h - 1 - ys.max(), w - 1 - xs.max()) < MARGIN:
            fails.append(f"frame {i}: margin under {MARGIN}px")
    n = len(frames)
    if n >= 4 and not np.array_equal(frames[-1], frames[1]):   # pingpong: the last frame copies frame 2
        fails.append(f"frame {n} is not a byte copy of frame 2 (ping-pong)")
    for i in range(n):
        j = (i + 1) % n
        if np.array_equal(frames[i], frames[j]):
            fails.append(f"frames {i + 1} and {j + 1} are identical")
    if plate is not None:
        pm = plate[..., 3] > 0
        if plate.shape != frames[0].shape:
            fails.append("plate size differs from frames")
        else:
            same = np.logical_and.reduce([(a == plate).all(-1) for a in frames])
            # "under a wing" uses lock_frame's own wing rule, so body noise under L1 60 is NOT excused
            ever_wing = np.logical_or.reduce([(a[..., 3] > OPAQUE) & ((plate[..., 3] <= OPAQUE)
                                              | (l1(a, plate) > WING_L1)) for a in frames]) & pm
            free = pm & ~ever_wing
            ident = float((same & free).sum()) / max(int(free.sum()), 1)
            r.update(plate_free_identical=round(ident, 4), plate_px=int(pm.sum()),
                     plate_never_under_wing=int(free.sum()))
            if ident < 1.0:
                fails.append(f"plate pixels never under a wing are only {ident:.4f} identical (lock did not run)")
    r.update({"pass": not fails, "fails": fails})
    return r


def _write(frames: list[np.ndarray], out: Path, prefix: str, facing: str) -> list[str]:
    out.mkdir(parents=True, exist_ok=True)
    stale = frame_paths(out, prefix, facing)
    if stale:
        raise SystemExit(f"refusing to overwrite {len(stale)} existing frame(s) in {out}; use a fresh --out")
    paths = []
    for i, a in enumerate(frames, 1):
        p = out / f"{prefix}{i}_{facing}.png"
        save(a, p)
        paths.append(str(p))
    return paths


def cmd_lock(a) -> dict:
    plate = load(a.plate)
    locked, infos = [], []
    for fp in a.frame:
        fr = load(fp)
        if fr.shape != plate.shape:
            raise SystemExit(f"{fp}: size {fr.shape[:2]} differs from plate {plate.shape[:2]}")
        out, info = lock_frame(plate, fr, a.search, a.wing_l1, a.min_cover, a.keep_isolated,
                              a.wing_far, a.wing_depth)
        infos.append({"frame": str(fp), **info})
        locked.append(out)
    rej = [i["frame"] for i in infos if i["rejected"]]
    rep = {"verb": "lock", "plate": str(a.plate), "frames_in": infos}
    if rej:
        return {**rep, "pass": False, "fails": [f"re-posed (alpha cover < {a.min_cover}): {rej}"]}
    frames = pingpong(locked)
    rep["written"] = _write(frames, Path(a.out), a.prefix, a.facing)
    rep["check"] = check(frames, a.facing, plate, a.min_share)
    rep["pass"] = rep["check"]["pass"]
    return rep


def cmd_compose(a) -> dict:
    body = load(a.body)
    frames = []
    for wp in a.wing:
        wing = load(wp)
        if wing.shape != body.shape:
            raise SystemExit(f"{wp}: size differs from body")
        top, bot = (wing, body) if a.order == "over" else (body, wing)
        t = Image.fromarray(top.astype(np.uint8), "RGBA")
        b = Image.fromarray(bot.astype(np.uint8), "RGBA")
        frames.append(np.asarray(Image.alpha_composite(b, t)).astype(np.int16))
    frames = pingpong(frames)
    rep = {"verb": "compose", "body": str(a.body), "wings": [str(w) for w in a.wing], "order": a.order}
    rep["written"] = _write(frames, Path(a.out), a.prefix, a.facing)
    # body pixels never under a wing must be the body exactly, so the body is the plate for the check
    rep["check"] = check(frames, a.facing, body, a.min_share)
    rep["pass"] = rep["check"]["pass"]
    return rep


def cmd_check(a) -> dict:
    paths = frame_paths(Path(a.dir), a.prefix, a.facing)
    frames = [load(p) for p in paths]
    rep = check(frames, a.facing, load(a.plate) if a.plate else None, a.min_share)
    return {"verb": "check", "frames": [str(p) for p in paths], **rep}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="verb", required=True)
    for name in ("lock", "compose", "check"):
        s = sub.add_parser(name)
        s.add_argument("--facing", required=True, choices=("east", "west", "south", "north"))
        s.add_argument("--prefix", required=True, help="e.g. Sketto_Flying_  ->  Sketto_Flying_<N>_<facing>.png")
        s.add_argument("--min-share", type=float, default=None, help="override the per-facing floor")
        s.add_argument("--report", type=Path, help="write the JSON report here")
        if name == "lock":
            s.add_argument("--plate", required=True, type=Path)
            s.add_argument("--frame", required=True, action="append", type=Path, help="one per pose, in order")
            s.add_argument("--search", type=int, default=8)
            s.add_argument("--wing-l1", type=int, default=WING_L1)
            s.add_argument("--min-cover", type=float, default=MIN_COVER)
            s.add_argument("--wing-far", type=int, default=WING_FAR, help="outside wing must reach > N px from the body")
            s.add_argument("--wing-depth", type=int, default=WING_DEPTH, help="inside-plate wing only within N px of the outside wing")
            s.add_argument("--keep-isolated", action="store_true", help="keep wing speckle not joined to a wing")
        if name == "compose":
            s.add_argument("--body", required=True, type=Path)
            s.add_argument("--wing", required=True, action="append", type=Path, help="one per pose, in order")
            s.add_argument("--order", required=True, choices=("over", "under"))
        if name in ("lock", "compose"):
            s.add_argument("--out", required=True, type=Path)
        else:
            s.add_argument("--dir", required=True, type=Path)
            s.add_argument("--plate", type=Path)
    a = ap.parse_args(argv)
    try:
        rep = {"lock": cmd_lock, "compose": cmd_compose, "check": cmd_check}[a.verb](a)
    except (FileNotFoundError, OSError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2
    txt = json.dumps(rep, indent=1)
    if a.report:
        a.report.write_text(txt + "\n")
    c = rep.get("check", rep)
    print(f"{'PASS' if rep['pass'] else 'FAIL'} {a.verb} {a.facing}: locked_share={c.get('locked_share')} "
          f"floor={c.get('floor')} plate_identical={c.get('plate_free_identical')}"
          + ("" if rep["pass"] else f"  fails={rep.get('fails') or c.get('fails')}"))
    return 0 if rep["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
