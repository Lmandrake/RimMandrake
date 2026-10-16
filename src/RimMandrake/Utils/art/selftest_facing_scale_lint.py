#!/usr/bin/env python3
"""selftest_facing_scale_lint.py — facing_scale_lint measures silhouettes, judges facings against the vanilla
calibration, picks rescale vs regenerate, and rescales about the feet keeping the canvas.

Part 1, synthetic sprites (no game files). Part 2, SANITY PROBES on real art when the game install is visible:
vanilla Muffalo passes the top-down model; the owner-flagged Anooba male (fixed 2026-10-15) passes the elevation model
and its pre-fix N/S (an east with 1.5x-tall S/N) fails it.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import facing_scale_lint as F  # noqa: E402

FAILS = []


def check(cond, msg, detail=""):
    print(("PASS " if cond else "FAIL ") + msg + ("" if cond else f"  [{str(detail)[:400]}]"))
    if not cond:
        FAILS.append(msg)


def legged(w, h, canvas=200, legs=True):
    """A creature-ish block of w x h px standing on the canvas floor (two feet when legs)."""
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, y1 = (canvas - w) // 2, canvas - 10
    body_bottom = y1 - (h // 3 if legs else 0)
    d.rectangle([x0, y1 - h, x0 + w - 1, body_bottom], fill=(120, 80, 40, 255))
    if legs:
        d.rectangle([x0, body_bottom, x0 + 8, y1], fill=(120, 80, 40, 255))
        d.rectangle([x0 + w - 9, body_bottom, x0 + w - 1, y1], fill=(120, 80, 40, 255))
    return im


def main() -> int:
    cal = F.load_cal()
    s = F.silhouette(legged(120, 60))
    check(abs(s["h"] - 60 / 200) < 0.01 and abs(s["w"] - 120 / 200) < 0.01, "silhouette measures bbox as canvas fraction", s)
    check(s["feet"] == 2, "two separate feet are counted", s["feet"])
    check(F.silhouette(legged(120, 60, legs=False))["feet"] == 1, "a legless blob has one run at the bottom")
    from PIL import Image
    check(F.silhouette(Image.new("RGBA", (8, 8))) is None, "an empty picture has no silhouette")

    # elevation: S and N 1.5x as tall as E -> both flagged, rescale (uniform) to ~1.0
    m = {"east": F.silhouette(legged(160, 60)), "south": F.silhouette(legged(90, 90)),
         "north": F.silhouette(legged(90, 90))}
    j = F.judge(m, cal, "elevation", "quadruped")
    check({f["facing"] for f in j["flags"]} == {"south", "north"}, "elevation: 1.5x-tall S and N are flagged", j)
    check(all(x["action"] == "rescale" and 0.6 < x["scale"] < 0.8 for x in j["fixes"].values()),
          "uniform oversize -> rescale down to the band's inter-quartile edge", j["fixes"])
    check(not F.judge({"east": m["east"], "south": F.silhouette(legged(90, 62)), "north": F.silhouette(legged(90, 61))},
                      cal, "elevation", "quadruped")["flags"], "elevation: equal heights pass")
    # top-down model allows the same picture (vanilla's N/S stand taller by the foreshortened length)
    check(not F.judge(m, cal, "topdown", "quadruped")["flags"] or j["severity"] > F.judge(m, cal, "topdown", "quadruped")["severity"],
          "top-down model is more lenient than elevation for tall S/N")
    # both S and N too small -> shrink east instead of enlarging two facings
    small = {"east": F.silhouette(legged(160, 120)), "south": F.silhouette(legged(60, 60)),
             "north": F.silhouette(legged(60, 60))}
    js = F.judge(small, cal, "elevation", "quadruped")
    check("east" in js["fixes"] and js["fixes"]["east"]["scale"] < 1, "both S/N too small -> the fix shrinks east",
          js["fixes"])

    # rescale keeps canvas and the feet
    src = legged(90, 90)
    out = F.rescale(src, 0.5)
    a, b = F.silhouette(src), F.silhouette(out)
    check(out.size == src.size, "rescale keeps the canvas size")
    check(abs(a["y1"] - b["y1"]) <= 1 and abs(a["cx"] - b["cx"]) < 0.01, "rescale keeps the ground-contact point",
          (a, b))
    check(abs(b["h"] - a["h"] * 0.5) < 0.02, "rescale shrinks the silhouette by the factor", (a["h"], b["h"]))

    # calibration sanity
    q = cal["quantiles"]
    check(cal["n"] >= 100, "calibration covers >= 100 vanilla animals", cal["n"])
    check(q["d_south"]["p02.5"] < 1 < q["d_south"]["p97.5"], "vanilla depth-model band contains 1", q["d_south"])
    lo, hi = F.elevation_band(cal)
    check(0.8 < lo < 1 < hi < 1.25, "elevation band is a modest tolerance around 1", (lo, hi))

    # CALIBRATION (2026-10-16, ROSTER_FACINGS_SHRINK_FRONT_VIEWS_STAND_TALL): per-body-plan envelope bands
    check(cal.get("vanilla_flag_rate", 1) <= F.TARGET_FLAG_RATE,
          "calibration: vanilla flags <= 5% of itself (leave-one-out)", cal.get("vanilla_flag_rate"))
    check(cal["plans"]["quadruped"]["n"] >= 50 and cal["plans"]["flyer"]["n"] >= 15, "calibration: quadruped and flyer plans are populated")
    check(all(cal["plans"][p]["d_south"]["band"][0] < 1 < cal["plans"][p]["d_south"]["band"][1] for p in cal["plans"]),
          "calibration: every plan's south band contains the depth model's 1")
    import facing_body_plan as BP
    ft = lambda **k: dict({"legs": 0, "arms": 0, "wings": 0, "fins": 0, "insect": 0, "blobby": 0, "head": 1,  # noqa: E731
                           "shell": 0, "foot": 0, "claws": 0, "pads": 0}, **k)
    for name, feats, want in (("four paws", ft(legs=4, pads=4), "quadruped"), ("hooves", ft(legs=4, pads=4), "quadruped"),
                              ("claws no pads", ft(legs=4, claws=20), "lowslung"), ("shell", ft(legs=4, shell=2), "lowslung"),
                              ("2 legs 2 feet, no arms", ft(legs=2, foot=2), "flyer"), ("wings", ft(legs=2, wings=2), "flyer"),
                              ("2 legs and arms", ft(legs=2, arms=2), "biped"), ("no limbs, head", ft(), "serpent"),
                              ("no limbs, fins", ft(fins=4), "fish"), ("no limbs, tentacle", ft(blobby=3), "blob"),
                              ("six legs insect", ft(legs=6, insect=11), "insect"), ("legless larva", ft(insect=3), "serpent")):
        check(BP.plan_from_features(feats) == want, f"body plan: {name} -> {want}", BP.plan_from_features(feats))
    try:
        got = {k: BP.plan_of_kind(k)[0] for k in ("Cobra", "Iguana", "Chicken", "Horse", "Megascarab", "Tortoise")}
    except (OSError, KeyError, ImportError):
        got = None                                       # DefDump not visible on this machine
    if got:
        check(got == {"Cobra": "serpent", "Iguana": "lowslung", "Chicken": "flyer", "Horse": "quadruped",
                      "Megascarab": "insect", "Tortoise": "lowslung"}, "body plan: real vanilla races classify from their BodyDef", got)
    # the three owner-approved Pyrelands rescales: OLD art (git 3791e139ea^) must flag, the new art must pass
    fx = HERE / "fixtures" / "facing_known_positives"
    for kind, base, plan in (("FireWasp", "FireWasp", "insect"), ("Anooba male", "Anooba_m", "quadruped"),
                             ("Furnace beast", "FurnaceBeast_Giant", "quadruped")):
        res = {}
        for ver in ("old", "new"):
            mm = {f: F.measure_file(fx / ver / f"{base}_{f}.png") for f in ("east", "south", "north")}
            res[ver] = F.judge(mm, cal, "elevation", plan)
        check(bool(res["old"]["flags"]) and not res["new"]["flags"],
              f"known positive: {kind} flags on its old art and passes on the new", (res["old"]["ratios"], res["new"]["flags"]))

    # part 2: real art
    if F.GAME_DATA.is_dir():
        vf = F.vanilla_faces("Muffalo")
        if len(vf) == 3:
            mv = {f: F.measure_file(p) for f, p in vf.items()}
            check(not F.judge(mv, cal, "topdown", "quadruped")["flags"], "SANITY: vanilla Muffalo passes", F.judge(mv, cal)["ratios"])
        else:
            check(False, "SANITY: vanilla Muffalo textures are visible to the probe", vf)
        repo = HERE.parents[3]
        base = repo / "src/RimStarWars/SWBestiary/Textures/RimStarWars/SWBestiary/Anooba/Anooba_m_"
        if (base.parent / "Anooba_m_east.png").is_file():
            ma = {f: F.measure_file(f"{base}{f}.png") for f in ("east", "south", "north")}
            ja = F.judge(ma, cal, "elevation", "quadruped")
            check(not ja["flags"], "SANITY: the fixed Anooba male passes the elevation model", ja["ratios"])
            pre = {"east": ma["east"], **{f: dict(ma[f], h=ma[f]["h"] * 1.55) for f in ("south", "north")}}
            check(len(F.judge(pre, cal, "elevation", "quadruped")["flags"]) == 2, "SANITY: its pre-fix proportions (1.55x) fail")
    print(f"\n{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
