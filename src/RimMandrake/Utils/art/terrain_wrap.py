#!/usr/bin/env python3
"""terrain_wrap.py - does a terrain texture repeat without a visible line, and repair it when it does not.

The game repeats a terrain file edge to edge across the map. Our regenerated terrain renders of 2026-11 carried a 1-px
dark frame on all four edges (none of the donor files did), which draws a thin grid line at every repeat, and some had
a content step at the wrap. Measured on the 15 Alpha Biomes polluted grounds (RIMMANDRAKE_JUDGE_THIRTY_TWO_ALPHA_
RENDERS_THEIR_MAKER_PASSED_BY_EYE): edge rows 3-26 levels darker than their neighbours; wrap step up to 6x the
interior pixel step. Donor textures: frame 0-2, wrap 1.0-1.2x.

    terrain_wrap.py check <png>...              exit 1 when any file has a frame or a wrap step (prints why)
    terrain_wrap.py heal <in.png> <out.png>     remove the frame and cross-fade the wrap (same size and mode)
    terrain_wrap.py manifest <json>             exit 1 unless every row's live bytes are the recorded bytes, the
                                                verdict is KEEP, and a terrain row passes `check` (a row on a mod the
                                                owner holds passes unmeasured when it names its stored repair).
                                                Exit 1 also when the manifest is missing; 2 when a picture cannot be read

The checks see only the frame and the wrap join. A line the repair itself draws INSIDE the file (the 2026-11-26 first
repair blended toward a half-shifted copy and drew the old wrap seam at the midline of each border band) is not seen:
look at a 2x2 tile of a repair before you install it.

`heal`: the outer row and column take their inner neighbours, then on each axis the last B px (B = width / 8) are
cross-faded onto the first B px with a contrast-preserving blend ((1-s)(a1-mu) + s(a2-mu) over sqrt((1-s)^2 + s^2)),
giving a file B px shorter that wraps by construction, resized back with Lanczos (a 12.5 % upscale).
"""
import hashlib
import io
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

FRAME_MAX = 2.0   # luminance levels an edge row/column may sit below its neighbour (donors: 0-2; our frames: 3-26)
WRAP_MAX = 1.5    # wrap step over the interior neighbour step (donors 0.97-1.22; repaired 0.97-1.23; broken 1.6-6.2)


def _lum(p):
    return np.asarray(Image.open(p).convert("RGB")).astype(float).mean(axis=2)


def frame_step(a):
    edges = (a[0], a[-1], a[:, 0], a[:, -1])
    inner = (a[1], a[-2], a[:, 1], a[:, -2])
    return max(i.mean() - e.mean() for e, i in zip(edges, inner))


def wrap_ratio(a):
    w = (abs(a[:, 0] - a[:, -1]).mean() + abs(a[0] - a[-1]).mean()) / 2
    inner = (abs(np.diff(a, axis=1)).mean() + abs(np.diff(a, axis=0)).mean()) / 2
    return w / inner if inner else 0.0


def problems(p):
    a = _lum(p)
    out = []
    f, r = frame_step(a), wrap_ratio(a)
    if f > FRAME_MAX:
        out.append("frame: edge rows %.1f levels darker than their neighbours (max %.1f)" % (f, FRAME_MAX))
    if r > WRAP_MAX:
        out.append("wrap: step at the join %.2fx the interior step (max %.2f)" % (r, WRAP_MAX))
    return out


def _axis_fade(a, B):
    W = a.shape[1] - B
    mu = a.reshape(-1, a.shape[-1]).mean(0)
    s = (np.arange(B) + 0.5) / B
    s = (s * s * (3 - 2 * s)).reshape((1, B, 1))
    a1, a2 = a[:, W:W + B], a[:, :B]
    out = a[:, :W].copy()
    out[:, :B] = mu + ((1 - s) * (a1 - mu) + s * (a2 - mu)) / np.sqrt((1 - s) ** 2 + s ** 2)
    return out


def heal(src, dst):
    im = Image.open(src)
    mode, (w, h) = im.mode, im.size
    a = np.asarray(im.convert("RGBA" if "A" in mode else "RGB")).astype(float).copy()
    a[0], a[-1] = a[1].copy(), a[-2].copy()
    a[:, 0], a[:, -1] = a[:, 1].copy(), a[:, -2].copy()
    B = max(8, w // 8)
    b = _axis_fade(a, B)
    b = np.swapaxes(_axis_fade(np.swapaxes(b, 0, 1), max(8, h // 8)), 0, 1)
    b = np.clip(b, 0, 255)
    chans = [np.asarray(Image.fromarray(b[..., i].astype(np.float32), "F").resize((w, h), Image.LANCZOS))
             for i in range(b.shape[2])]
    out = np.clip(np.stack(chans, -1) + 0.5, 0, 255).astype(np.uint8)
    Image.fromarray(out, "RGBA" if "A" in mode else "RGB").convert(mode).save(dst, optimize=True)


class Unreadable(Exception):
    pass


def _bytes(root, rel):
    """The live bytes of a repo picture: the working file, else the blob at HEAD (a slim clone has no media on disk;
    git fetches the blob on demand). -> bytes, or raises Unreadable."""
    p = os.path.join(root, rel)
    if os.path.exists(p):
        with open(p, "rb") as f:
            return f.read()
    r = subprocess.run(["git", "-C", root, "cat-file", "blob", "HEAD:" + rel], capture_output=True, timeout=300)
    if r.returncode:
        raise Unreadable("%s: not on disk and not in git HEAD (%s)" % (rel, r.stderr.decode(errors="replace").strip()))
    return r.stdout


def check_manifest(path, root=None):
    """-> [problem lines]. Rows: {path, sha256, verdict, terrain, held?, repair_store_sha?}; paths relative to root."""
    root = root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))))
    with open(path, encoding="utf-8") as f:
        rows = json.load(f)["rows"]
    out = []
    for r in rows:
        data = _bytes(root, r["path"])
        if hashlib.sha256(data).hexdigest() != r["sha256"]:
            out.append("%s: live bytes are not the judged bytes %s" % (r["path"], r["sha256"][:12]))
            continue
        if r.get("verdict") != "KEEP":
            out.append("%s: verdict %s" % (r["path"], r.get("verdict")))
        if r.get("terrain"):
            if r.get("held"):
                if not r.get("repair_store_sha"):
                    out.append("%s: held (%s) with no stored repair" % (r["path"], r["held"]))
                continue
            out += ["%s: %s" % (r["path"], x) for x in problems(io.BytesIO(data))]
    return out


def main(argv):
    if argv[:1] == ["check"] and argv[1:]:
        bad = 0
        for p in argv[1:]:
            pr = problems(p)
            bad += bool(pr)
            print("%s  %s" % ("BAD " if pr else "OK  ", p) + ("".join("\n      " + x for x in pr)))
        return 1 if bad else 0
    if argv[:1] == ["heal"] and len(argv) == 3:
        heal(argv[1], argv[2])
        print("; ".join(problems(argv[2])) or "OK  %s" % argv[2])
        return 0
    if argv[:1] == ["manifest"] and len(argv) == 2:
        if not os.path.exists(argv[1]):
            print("no manifest: %s" % argv[1])
            return 1
        try:
            out = check_manifest(argv[1])
        except Unreadable as e:
            print("UNMEASURED: %s" % e)
            return 2
        print("\n".join(out) or "OK  every row: judged bytes live, KEEP, terrain repeats clean")
        return 1 if out else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
