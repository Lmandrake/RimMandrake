#!/usr/bin/env python3
"""Graffiti's judged shots are captured at play zoom, ~64 px per cell (GRAFFITI_NORTHSTAR_GREEN_FULL_1, test pilot gen 19/21).

Live A2 2026-11-05 (D:\\ClaudeWork\\rimmandrake\\testpilot_GRAFFITI_NORTHSTAR_GREEN_FULL_1\\g19\\exp2b_rows.txt): every
functional row PASS, but the judge read 7 bars UNMEASURED/UNJUDGEABLE ("the marks repeat about every 20 px", "the 138x99 crop
is too small"). `rimworld/screenshot_cell_rect` with no rootSize shoots at the CURRENT zoom: rootSize 24 = 19.7 px per cell
(g19/zt_0.txt); rootSize 7.35 gave 64.3 (g19/zt_7.35.txt). The bar asks for ~64 px per cell measured on the PNG
(Graffiti_trial_plan.md 3.9). A HARNESS defect: the mod was never shown at the zoom it is judged at.

S1  every validation.py screenshot inside a component that claims a judged bar passes ppc=PLAY_PPC (64 +/- 5%), except
    spree_variety (44 cells wide, judged fine at the current zoom); red on the held code (no ppc anywhere).
S2  play_zoom.shoot against a simulated camera (px per cell = 472.8 / rootSize, the live constant; screen 2304x985 px):
    a probe learns K, the shot is taken at rootSize K/64 and measures 64 px per cell.
S3  a gallery page (22 x 24 + padding) is taller than one 64-ppc screen: it is shot in bands that are each fully visible,
    and stitched into ONE image of (24 x 64) x (26 x 64) px, top band = highest z.
S4  mutant camera that ignores rootSize (always the current zoom): UNMEASURED, never a 20-px image handed to the judge.
S5  a reply with fullyVisible false, or a rect wider than one screen: UNMEASURED.
S6  Suite.screenshot with ppc routes through play_zoom (records the one path); without ppc it sends no rootSize (unchanged).
S7  the two LIVE replies of 2026-11-05 (g19/zt_0.txt at the current zoom, g19/zt_7.35.txt explicit), their fields inlined:
    the K learned from the rootSize-24 reply predicts the explicit shot's measured px per cell within 5%.
"""
import ast
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for p in (UTILS, os.path.join(UTILS, "modcheck"), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

FAILS = []


def check(name, ok, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  -- " + str(detail)[:400]))
    if not ok:
        FAILS.append(name)


class Unmeasured(Exception):
    pass


class Camera(object):
    """screenshot_cell_rect as the live tool answers it (g19/zt_*.txt): clipRect = cells x px-per-cell, writes a PNG."""
    K = 472.8                       # 19.7 px/cell x rootSize 24, live
    SCREEN = (2304, 985)

    def __init__(self, outdir, ignore_root=False, never_visible=False):
        self.outdir, self.ignore_root, self.never_visible = outdir, ignore_root, never_visible
        self.current = 24.0
        self.calls = []

    def call(self, tool, **kw):
        if tool != "rimworld/screenshot_cell_rect":
            return {"success": True}
        self.calls.append(kw)
        root = self.current if (self.ignore_root or "rootSize" not in kw) else float(kw["rootSize"])
        ppc = self.K / root
        vw, vh = self.SCREEN[0] / ppc, self.SCREEN[1] / ppc
        w, h = kw["width"], kw["height"]
        visible = (w <= vw and h <= vh) and not self.never_visible
        cw, ch = int(round(w * ppc)), int(round(h * ppc))
        path = os.path.join(self.outdir, kw["fileName"] + "__cell_rect.png")
        from PIL import Image
        Image.new("RGB", (max(1, cw), max(1, ch)), (int(kw["z"]) % 256, 80, 80)).save(path)
        return {"success": True, "path": path, "clipRect": {"x": 0, "y": 0, "width": cw, "height": ch},
                "paddedRect": {"x": kw["x"], "z": kw["z"], "width": w, "height": h},
                "fullyVisible": visible, "appliedRootSize": root,
                "cameraDuringCapture": {"rootSize": root, "viewRect": {"width": int(vw), "height": int(vh)}}}


def _judged_shots(path):
    """-> [(component, has_judged_bar, ppc_arg_src)] for every t.screenshot inside a `with t.component(...)`."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    out = []

    def comp_of(w):
        for item in w.items:
            c = item.context_expr
            if isinstance(c, ast.Call) and getattr(c.func, "attr", "") == "component":
                name = ast.unparse(c.args[0]) if c.args else "?"
                shows = [k for k in c.keywords if k.arg == "shows"]
                return name, bool(shows)
        return None

    def walk(node, comp):
        if isinstance(node, ast.With):
            comp = comp_of(node) or comp
        if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "screenshot" and comp:
            ppc = [ast.unparse(k.value) for k in node.keywords if k.arg == "ppc"]
            out.append((comp[0], comp[1], ppc[0] if ppc else None))
        for ch in ast.iter_child_nodes(node):
            walk(ch, comp)
    walk(tree, None)
    return out


def s1_validation():
    import validation as V
    shots = _judged_shots(os.path.join(HERE, "validation.py"))
    judged = [s for s in shots if s[1] and "spree_variety" not in s[0]]
    bad = [s for s in judged if s[2] != "PLAY_PPC"]
    check("S1 every judged Graffiti shot passes ppc=PLAY_PPC (%d shots)" % len(judged), judged and not bad, bad)
    ppc = getattr(V, "PLAY_PPC", None)
    check("S1 PLAY_PPC is 64 px per cell +/- 5%% (got %r)" % ppc, ppc is not None and abs(ppc - 64) <= 3.2)


def s2_s3_s4_s5():
    import play_zoom as PZ
    with tempfile.TemporaryDirectory() as d:
        cam = Camera(d)
        cal = PZ.Calibration()
        p = PZ.shoot(cam, cal, (100, 100, 22, 3), 0, 64, "closeup", Unmeasured)
        from PIL import Image
        im = Image.open(p)
        last = cam.calls[-1]
        check("S2 probe first (no rootSize), then the shot at rootSize K/64 = %.2f" % (Camera.K / 64),
              "rootSize" not in cam.calls[0] and abs(float(last.get("rootSize", 0)) - Camera.K / 64) < 0.01, cam.calls)
        check("S2 the closeup PNG measures 64 px per cell (%dx%d for 22x3)" % im.size,
              abs(im.size[0] / 22.0 - 64) <= 3.2 and abs(im.size[1] / 3.0 - 64) <= 3.2, im.size)
        n0 = len(cam.calls)
        PZ.shoot(cam, cal, (100, 100, 17, 4), 0, 64, "beauty", Unmeasured)
        check("S2 a calibrated context takes ONE call per shot (no second probe)", len(cam.calls) - n0 == 1, cam.calls[n0:])

        n0 = len(cam.calls)
        p = PZ.shoot(cam, cal, (100, 90, 22, 24), 1, 64, "gallery_page_0", Unmeasured)
        band_calls = cam.calls[n0:]
        im = Image.open(p)
        check("S3 the gallery page is shot in >= 2 bands, each fully inside one screen (%d bands)" % len(band_calls),
              len(band_calls) >= 2 and all(c["height"] * 64 <= Camera.SCREEN[1] for c in band_calls), band_calls)
        check("S3 bands tile the padded rect exactly (z 89..114, no gap, no overlap)",
              sorted((c["z"], c["height"]) for c in band_calls)[0][0] == 89
              and sum(c["height"] for c in band_calls) == 26
              and all(c["width"] == 24 for c in band_calls), band_calls)
        check("S3 ONE stitched image of 24x26 cells at 64 px (%dx%d)" % im.size,
              p.endswith("_stitched__cell_rect.png") and abs(im.size[0] - 24 * 64) <= 24 and abs(im.size[1] - 26 * 64) <= 26,
              (p, im.size))
        top = Image.open(p).getpixel((5, 5))[0]
        hi = max(c["z"] for c in band_calls) % 256
        check("S3 the top of the stitched image is the highest-z band", top == hi, (top, hi))

        def unmeasured(fn):
            try:
                fn()
            except Unmeasured as ex:
                return str(ex).startswith("UNMEASURED")
            return False
        check("S4 mutant camera ignoring rootSize -> UNMEASURED, never a 20-px image",
              unmeasured(lambda: PZ.shoot(Camera(d, ignore_root=True), PZ.Calibration(), (100, 100, 22, 3), 0, 64,
                                          "m", Unmeasured)))
        check("S5 fullyVisible false -> UNMEASURED",
              unmeasured(lambda: PZ.shoot(Camera(d, never_visible=True), PZ.Calibration(), (100, 100, 7, 5), 0, 64,
                                          "v", Unmeasured)))
        check("S5 a rect wider than one screen at 64 px -> UNMEASURED",
              unmeasured(lambda: PZ.shoot(Camera(d), PZ.Calibration(), (100, 100, 44, 7), 0, 64, "w", Unmeasured)))


def s6_suite():
    import suite as S
    with tempfile.TemporaryDirectory() as d:
        cam = Camera(d)
        t = S.TestContext.__new__(S.TestContext)
        t.session, t.anchor, t._current = cam, (100, 100), None
        t._guard = lambda: True

        class C(object):
            name = "wall_closeup"
            screenshots = []
        t._current = C()
        p = S.TestContext.screenshot(t, rect=(100, 100, 11, 7), padding=0, ppc=64)
        check("S6 Suite.screenshot(ppc=64) records the play-zoom path",
              C.screenshots == [p] and abs(float(cam.calls[-1]["rootSize"]) - Camera.K / 64) < 0.01, (p, cam.calls))
        cam2 = Camera(d)
        t.session = cam2
        S.TestContext.screenshot(t, rect=(100, 100, 11, 7), padding=0)
        check("S6 without ppc no rootSize is sent (unchanged behaviour)",
              cam2.calls and "rootSize" not in cam2.calls[-1], cam2.calls)


LIVE_ZT0 = {"success": True, "clipRect": {"x": 1054, "y": 421, "width": 138, "height": 99},
            "paddedRect": {"x": 118, "z": 124, "width": 7, "height": 5}, "fullyVisible": True, "appliedRootSize": 24.0,
            "cameraDuringCapture": {"rootSize": 24.0, "viewRect": {"width": 117, "height": 51}}}
LIVE_ZT735 = {"success": True, "clipRect": {"x": 898, "y": 310, "width": 450, "height": 321},
              "paddedRect": {"x": 118, "z": 124, "width": 7, "height": 5}, "fullyVisible": True, "appliedRootSize": 7.35,
              "cameraDuringCapture": {"rootSize": 7.35, "viewRect": {"width": 39, "height": 17}}}


def s7_live_replay():
    import play_zoom as PZ
    cal = PZ.Calibration()
    check("S7 the live rootSize-24 reply calibrates (19.7 px per cell)",
          cal.learn(LIVE_ZT0) and abs(PZ.measured_ppc(LIVE_ZT0) - 19.76) < 0.05, vars(cal))
    predicted = cal.k / 7.35
    got = PZ.measured_ppc(LIVE_ZT735)
    check("S7 it predicts the live rootSize-7.35 shot: %.1f vs measured %.1f px per cell" % (predicted, got),
          abs(predicted - got) <= PZ.TOL * got)
    check("S7 a 22x26 gallery page needs >= 2 bands at the live screen (%.1f cells tall at 64 px)"
          % (cal.tall * cal.k / 64), cal.tall * cal.k / 64 < 26)


def main():
    for fn in (s1_validation, s2_s3_s4_s5, s6_suite, s7_live_replay):
        try:
            fn()
        except Exception as ex:           # noqa: BLE001 - a crash is a red row, not a pass
            check("%s ran" % fn.__name__, False, "%s: %s" % (type(ex).__name__, ex))
    print("selftest graffiti play zoom: %s (%d failure(s))" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
