#!/usr/bin/env python3
"""selftest_facing_view_fit.py — new S/N facings are fitted by facing_scale_lint's own rule, never to east's height.

A long, low body drawn from a high camera (the Dragonsnake case) keeps its size and goes to the judge raw; a uniform
oversize that the lint calls a pure scale problem is rescaled by the lint's factor; an in-band or too-small facing is
untouched; the driver check tells the old norm_view (private east-height target) from one that delegates here.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import facing_scale_lint as L  # noqa: E402
import facing_view_fit as V  # noqa: E402

FAILS = []


def check(cond, msg, detail=""):
    print(("PASS " if cond else "FAIL ") + msg + ("" if cond else f"  [{str(detail)[:400]}]"))
    if not cond:
        FAILS.append(msg)


def body(w, h, canvas=200, legs=True):
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, y1 = (canvas - w) // 2, canvas - 10
    bb = y1 - (h // 3 if legs else 0)
    d.rectangle([x0, y1 - h, x0 + w - 1, bb], fill=(120, 80, 40, 255))
    if legs:
        d.rectangle([x0, bb, x0 + 8, y1], fill=(120, 80, 40, 255))
        d.rectangle([x0 + w - 9, bb, x0 + w - 1, y1], fill=(120, 80, 40, 255))
    return im


OLD_NORM_VIEW = '''
def norm_view(imgs, new, out_dir, tol=0.05):
    hts = {f: d[3][3] - d[3][1] + 1 for f, d in data.items()}
    target = hts['east']
    k = target / hts[f]
    return out, rep


def base_spec(k, v):
    pass
'''
NEW_NORM_VIEW = '''
def norm_view(imgs, new, out_dir, tol=0.05, kind=None):
    """Delegates to the repo's facing_view_fit (facing_scale_lint's own size rule)."""
    import facing_view_fit as FV
    return FV.fit_new_views(imgs, new, out_dir, kind=kind)


def base_spec(k, v):
    pass
'''


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)

        def save(name, im):
            p = t / f"{name}.png"
            im.save(p)
            return str(p)

        # 1. the snake: east long and low, a high-camera rear view 3.75x as tall — the old rule shrank it to 0.27
        e = save("snake_e", body(180, 24, legs=False))
        n = save("snake_n", body(60, 90, legs=False))
        out, rep = V.fit_new_views({"east": e, "north": n}, ["north"], t / "snake", plan="serpent")
        hn = L.measure_file(out["north"])["h"]
        check(abs(hn - L.measure_file(n)["h"]) < 0.01, "high-camera north of a long low body keeps its own height", rep)
        check(Path(out["north"]).read_bytes() == Path(n).read_bytes(), "it goes to the judge raw (byte copy)", rep)
        check("north" in rep["kept_raw"] and not rep["scaled"], "the report names why it was kept raw", rep)
        check(hn > 0.65 * L.measure_file(n)["h"], "no facing shrinks below MIN_SHRINK (the peas case)", hn)
        # the same pair with no plan (unclassified, no feet): the lint's top-down depth model — still never peas
        out, rep = V.fit_new_views({"east": e, "north": n}, ["north"], t / "snake2")
        check(L.measure_file(out["north"])["h"] >= L.MIN_SHRINK * L.measure_file(n)["h"] - 0.01,
              "unclassified long low body: never shrunk past MIN_SHRINK", rep)

        # 2. a uniform 1.5x oversize on a quadruped: the lint calls it pure scale -> its rescale factor
        e = save("q_e", body(160, 60))
        n = save("q_n", body(90, 90))
        s = save("q_s", body(90, 61))
        out, rep = V.fit_new_views({"east": e, "south": s, "north": n}, ["north"], t / "quad", plan="quadruped")
        j = L.judge({f: L.measure_file(p) for f, p in (("east", e), ("south", s), ("north", n))}, L.load_cal(),
                    "elevation", "quadruped")
        want = j["fixes"]["north"]["scale"]
        check(rep["scaled"].get("north") == round(want, 3) and 0.65 <= want < 1, "pure-scale oversize gets the lint's factor",
              (rep, j["fixes"]))
        after = {f: L.measure_file(p) for f, p in (("east", e), ("south", s), ("north", out["north"]))}
        check(not [x for x in L.judge(after, L.load_cal(), "elevation", "quadruped")["flags"] if x["facing"] == "north"],
              "after the fit the lint no longer flags the north", L.judge(after, L.load_cal(), "elevation", "quadruped"))
        check(out["south"] == s, "an installed facing that is not new is not touched", out)

        # 3. in band, and too small: untouched (never enlarged here)
        for name, h in (("inband", 63), ("small", 30)):
            n2 = save(f"q_n_{name}", body(90, h))
            out, rep = V.fit_new_views({"east": e, "north": n2}, ["north"], t / name, plan="quadruped")
            check(Path(out["north"]).read_bytes() == Path(n2).read_bytes() and not rep["scaled"],
                  f"a {name} north is passed on unchanged", rep)

    # 4. the driver check
    ok, why = V.driver_delegates(OLD_NORM_VIEW)
    check(not ok, "the old norm_view (east-height target) reads NOT FIXED", why)
    ok, why = V.driver_delegates(NEW_NORM_VIEW)
    check(ok, "a norm_view that delegates reads OK", why)
    ok, _ = V.driver_delegates(NEW_NORM_VIEW.replace("return FV", "target = hts['east']\n    return FV"))
    check(not ok, "a delegating norm_view that keeps a private east target reads NOT FIXED")

    print(f"{'FAIL' if FAILS else 'PASS'} selftest_facing_view_fit ({len(FAILS)} failed)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
