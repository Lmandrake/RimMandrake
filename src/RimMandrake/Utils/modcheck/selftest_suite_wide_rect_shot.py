"""modcheck.selftest_suite_wide_rect_shot -- a framed capture too big for the screen is retaken in bands, never
replaced by a desktop grab (RIMMANDRAKE_FIT_SUITE_WIDE_RECT_SHOTS_NOT_A_DESKTOP_GRAB).

Measured (Pyrelands visit 6, 2026-11-22, ArchSmall): `rimworld/screenshot_cell_rect` refuses a rect that does not fit
the viewport at the current root size ("Requested cell rectangle does not fit in the viewport at the selected camera
root size."; a 48x48 sky frame and a 250x250 day-end frame both refused at root 24, where one screen is 94x50 cells).
TestContext.screenshot then took an OS desktop capture: on ArchSmall that is a picture of another window (his desktop
and the other game), filed as the row's capture. Visit 5 (ArchBig) had 30 such captures of 90.

The fake game here answers like the live tool: a rect that fits (rect + padding inside the view at the root size used)
is captured, with clipRect, paddedRect, appliedRootSize and cameraDuringCapture as the live reply carries them; else the
refusal above. The OS fallback is replaced by a recorder. Cases: a small rect (unchanged: one cell-rect call, no
fallback), a 48x48 and a 250x250 rect (a real image, no fallback; the 250 one is stitched from bands), and a game whose
every capture refuses (the fallback still runs: this change only adds the retake).

No socket, no game.   python3 src/RimMandrake/Utils/modcheck/selftest_suite_wide_rect_shot.py
"""
import os
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)
for p in (_HERE, _UTILS):
    if p not in sys.path:
        sys.path.insert(0, p)

import suite  # noqa: E402
from suite import TestContext  # noqa: E402

FAILURES = []
K = 19.7 * 24          # px per cell x root size, as measured live (root 24 = 19.7 px per cell)
TALL, WIDE = 50.0 / 24, 94.0 / 24   # visible cells per unit root size (viewRect 94x50 at root 24)
ROOT_MAX = 100.0
REFUSE = "Requested cell rectangle does not fit in the viewport at the selected camera root size."


def check(name, cond, detail=""):
    print("  ok   %s" % name if cond else "  FAIL %s  %s" % (name, detail))
    if not cond:
        FAILURES.append(name)


class FakeGame(object):
    def __init__(self, tmp, refuse_all=False):
        self.tmp, self.refuse_all, self.log = tmp, refuse_all, []

    def call(self, tool, **kw):
        self.log.append((tool, dict(kw)))
        if tool != "rimworld/screenshot_cell_rect":
            return {"success": True}
        root = float(kw.get("rootSize") or 24.0)
        p = int(kw.get("paddingCells") or 0)
        w, h = kw["width"] + 2 * p, kw["height"] + 2 * p
        if self.refuse_all or root > ROOT_MAX or w >= WIDE * root or h >= TALL * root:   # live: 50 rows at a 50-row view refused
            return {"success": False, "path": None, "message": REFUSE}
        ppc = K / root
        path = os.path.join(self.tmp, "%s__cell_rect.png" % kw["fileName"])
        try:
            from PIL import Image
            Image.new("RGB", (max(1, int(w * ppc)), max(1, int(h * ppc)))).save(path)
        except ImportError:
            open(path, "wb").close()
        return {"success": True, "path": path, "appliedRootSize": root, "fullyVisible": True,
                "clipRect": {"width": w * ppc, "height": h * ppc}, "paddedRect": {"width": w, "height": h},
                "cameraDuringCapture": {"rootSize": root, "viewRect": {"width": WIDE * root, "height": TALL * root}}}


def run(rect, refuse_all=False):
    tmp = tempfile.mkdtemp(prefix="wide_rect_shot_")
    game = FakeGame(tmp, refuse_all)
    t = TestContext(game, anchor=(125, 125))
    grabbed = []
    import subprocess
    orig = subprocess.run
    subprocess.run = lambda argv, **kw: grabbed.append(argv)   # the OS desktop capture, recorded instead of taken
    try:
        path = t.screenshot(name="shot", rect=rect)
    finally:
        subprocess.run = orig
    cells = [kw for tool, kw in game.log if tool == "rimworld/screenshot_cell_rect"]
    return path, grabbed, cells


def main():
    path, grabbed, cells = run((100, 100, 20, 20))
    check("small rect: one cell-rect call, its own image", len(cells) == 1 and path and path.endswith("__cell_rect.png"),
          "path %r, %d calls" % (path, len(cells)))
    check("small rect: no desktop grab", not grabbed, repr(grabbed))

    for side in (48, 250):
        path, grabbed, cells = run((0, 0, side, side))
        check("%dx%d rect: no desktop grab" % (side, side), not grabbed, "grabbed %r; path %r" % (grabbed, path))
        check("%dx%d rect: a cell-rect image of the rect" % (side, side),
              bool(path) and "fallback" not in path and os.path.exists(path), "path %r" % path)
        if side == 250:
            check("250x250 rect: stitched from bands", bool(path) and "stitched" in path and
                  sum(1 for kw in cells if kw.get("rootSize")) >= 2, "path %r, roots %r"
                  % (path, [kw.get("rootSize") for kw in cells]))

    path, grabbed, cells = run((0, 0, 250, 250), refuse_all=True)
    check("every capture refused: the old fallback still runs", len(grabbed) == 1 and "fallback" in str(path),
          "grabbed %r path %r" % (grabbed, path))

    print("selftest_suite_wide_rect_shot: %d FAIL" % len(FAILURES))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
