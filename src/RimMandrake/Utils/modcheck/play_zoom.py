"""Capture a cell rect at a measured px-per-cell ("play zoom"), for screenshots a judge must read.

Why (GRAFFITI_NORTHSTAR_GREEN_FULL_1, live 2026-11-05): `rimworld/screenshot_cell_rect` with no rootSize
captures at the CURRENT camera zoom (rootSize 24 = 19.7 px per cell), and the judge called 7 Graffiti bars
UNJUDGEABLE ("marks repeat about every 20 px", "the crop is too small"). The bar wants ~64 px per cell,
measured on the PNG (Graffiti_trial_plan.md 3.9), so the zoom here is MEASURED, never assumed:

  * px per cell is inversely proportional to rootSize, so K = ppc * rootSize is one number per window.
    K comes from the tool's own reply: clipRect px / paddedRect cells, times appliedRootSize.
  * The first rect shot of a context probes at the current zoom to learn K (and how many cells tall the
    screen is per unit rootSize, from cameraDuringCapture.viewRect); every shot after reuses it.
  * Each real shot is taken with rootSize = K / ppc and its measured ppc is checked (TOL); off by more,
    K is re-learned from that reply and the shot retaken once; still off -> UNMEASURED.
  * A rect taller than one screen at that zoom is shot in bands (no padding between them) and stitched
    into ONE image, so a component keeps its single judged shot (judge_cli judges a component's LAST shot).
  * A rect wider than one screen is shot in columns too and stitched side by side (Pyrelands visit 9, 2026-11-24: the game
    window had been resized to 1458 px, and a 23-cell front crop lost the whole watched day as UNMEASURED).

`shoot()` raises `fail("UNMEASURED: ...")`: the caller passes its ExpectationFailed (no circular import).
"""
import math
import os

TOL = 0.05              # 640 +/- 32 px per 10 cells (Graffiti_trial_plan.md 3.9)
MARGIN_CELLS = 1        # cells kept off the screen edge per band


class Calibration(object):
    def __init__(self):
        self.k = None           # px per cell * rootSize
        self.tall = None        # visible cells tall per unit rootSize
        self.wide = None        # visible cells wide per unit rootSize

    def learn(self, r):
        ppc, root = measured_ppc(r), _num((r or {}).get("appliedRootSize"))
        if not ppc or not root:
            return False
        self.k = ppc * root
        cam = (r or {}).get("cameraDuringCapture") or (r or {}).get("cameraBefore") or {}
        vr, croot = cam.get("viewRect") or {}, _num(cam.get("rootSize"))
        if croot and _num(vr.get("height")) and _num(vr.get("width")):
            self.tall = float(vr["height"]) / croot
            self.wide = float(vr["width"]) / croot
        return True


def _num(v):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    return v if v > 0 else None


def measured_ppc(r):
    """px per cell of a screenshot_cell_rect reply, from the crop it wrote; None when unreadable."""
    r = r or {}
    clip = r.get("clipRect") or {}
    cells = r.get("paddedRect") or r.get("requestedRect") or {}
    vals = [_num(clip.get(a)) / _num(cells.get(a)) for a in ("width", "height")
            if _num(clip.get(a)) and _num(cells.get(a))]
    return sum(vals) / len(vals) if vals else None


def bands(z, h, max_h):
    """Split rows [z, z+h) into the fewest near-equal bands of at most max_h rows, low z first."""
    n = max(1, int(math.ceil(float(h) / max_h)))
    base, extra = divmod(h, n)
    out, zz = [], z
    for i in range(n):
        bh = base + (1 if i < extra else 0)
        out.append((zz, bh))
        zz += bh
    return out


def local_path(p):
    """A Windows path the game wrote, openable from this interpreter (python.exe or WSL)."""
    if not p or os.path.exists(p):
        return p
    if len(p) > 2 and p[1] == ":" and os.name != "nt":
        return "/mnt/%s/%s" % (p[0].lower(), p[3:].replace("\\", "/"))
    return p


def _call(session, rect, root, fname):
    x, z, w, h = rect
    kw = dict(x=x, z=z, width=w, height=h, paddingCells=0, fileName=fname, suppressMessage=True)
    if root:
        kw["rootSize"] = round(root, 3)
    return session.call("rimworld/screenshot_cell_rect", **kw) or {}


def _one(session, cal, rect, ppc, fname, fail):
    r = _call(session, rect, cal.k / ppc, fname)
    for attempt in (0, 1):
        got = measured_ppc(r)
        if not (r.get("success") and r.get("path")):
            raise fail(("UNMEASURED: play-zoom shot %s returned no image: %r" % (fname, dict(r)))[:300])
        if r.get("fullyVisible") is False:
            raise fail("UNMEASURED: play-zoom shot %s: rect %s not fully visible at rootSize %s"
                       % (fname, rect, r.get("appliedRootSize")))
        if got and abs(got - ppc) <= TOL * ppc:
            return r
        if attempt or not cal.learn(r):
            raise fail("UNMEASURED: play-zoom shot %s measured %s px per cell, wanted %d +/- %d%%"
                       % (fname, got, ppc, int(TOL * 100)))
        r = _call(session, rect, cal.k / ppc, fname)
    return r


def stitch(rows, out_path):
    """Crops -> one PNG. `rows`: top-down, each a path or a list of paths left to right."""
    from PIL import Image
    grid = [[Image.open(local_path(p)).convert("RGB") for p in (r if isinstance(r, (list, tuple)) else [r])] for r in rows]
    canvas = Image.new("RGB", (max(sum(i.width for i in r) for r in grid), sum(max(i.height for i in r) for r in grid)))
    y = 0
    for r in grid:
        x = 0
        for im in r:
            canvas.paste(im, (x, y))
            x += im.width
        y += max(i.height for i in r)
    canvas.save(local_path(out_path))
    return out_path


def shoot(session, cal, rect, padding, ppc, fname, fail):
    """-> path of ONE image of `rect` (+padding cells) at `ppc` px per cell, or raises fail('UNMEASURED: ...')."""
    session.call("jawa/clear_ui")
    p = int(padding or 0)
    x, z, w, h = rect[0] - p, rect[1] - p, rect[2] + 2 * p, rect[3] + 2 * p
    if cal.k is None:
        probe = _call(session, (x, z, w, h), None, fname + "_probe")
        if not cal.learn(probe):
            raise fail("UNMEASURED: play-zoom calibration: the probe reply carries no clipRect/rootSize: %r"
                       % (dict(probe or {}),))
    root = cal.k / ppc
    max_h = max(1, int(math.floor(cal.tall * root)) - 2 * MARGIN_CELLS) if cal.tall else h
    max_w = max(1, int(math.floor(cal.wide * root)) - 2 * MARGIN_CELLS) if cal.wide else w
    parts, cols = bands(z, h, max_h), bands(x, w, max_w)
    if len(parts) == 1 and len(cols) == 1:
        return _one(session, cal, (x, z, w, h), ppc, fname, fail)["path"]
    rows = []
    for i, (bz, bh) in enumerate(parts):
        rows.append([_one(session, cal, (bx, bz, bw, bh), ppc, "%s_b%d%s" % (fname, i, "c%d" % j if len(cols) > 1 else ""),
                          fail)["path"] for j, (bx, bw) in enumerate(cols)])
    rows.reverse()                        # screen-up is +z: the highest band goes on top
    first = rows[0][0]
    sep = "\\" if "\\" in first else "/"
    out = first.rsplit(sep, 1)[0] + sep + fname + "_stitched__cell_rect.png"
    try:
        return stitch(rows, out)
    except Exception as ex:                # noqa: BLE001 - a missing band or no PIL: the shot is unmeasured
        raise fail("UNMEASURED: play-zoom stitch of %d bands x %d columns failed: %s" % (len(parts), len(cols), ex))
