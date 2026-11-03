#!/usr/bin/env python3
"""selftest_flier_body_stabilize.py - the body localiser must recover a known body shift AND rotation while the
wings flap, and must call a static body LOCKED.

Fixture (in memory, deterministic): a 160 px canvas; a textured elliptical body with an outline, an eye and a tail
(the BODY annotation is a polygon around it); two textured wings turned about the shoulders by a different angle
every frame (+25, 0, -25, 0 deg).
  STATIC   body pixels identical in every frame: verdict LOCKED, every estimator <= 0.05 px / 0.05 deg
  MOVED    frame 3's body translated (+3, -2) px and turned 4 deg about its centre: ECC and FEATURES recover the
           motion at the body centre within 1 px and 0.5 deg of the truth; PARTS within 1.5 px / 1 deg; verdict DRIFT
  REPOSED  frame 3's body replaced by a different drawing: verdict APPEARANCE CHANGED (residual evidence: no
           alignment tried brings the body back)
  LINES    the owner's eye-line / shoulder-line check: LEVEL on the static body; a +3 px bob of frame 3's body is
           seen as dy 3 on both lines (MOVING); the whole flier turned 4 deg is seen as a 4 deg (+/-1.5) angle change on both lines
           (2026-11-02, GPT A3 P1) both eyes slid +3 px sideways, or spread 2 px apart along their row, keep the
           midpoint height and the angle (the old gate's only inputs) and are MOVING by the per-endpoint 2D gate and
           the length change; a head bob onto a still torso is seen as an eye-to-shoulder distance change
  GPT-REVIEW (2026-10-21) cases the old code got wrong, each naming the old result: estimator failure on an unchanged
           body (UNMEASURED, was RE-POSED); ECC region as templateMask at a 20 px shift; head-only protect with a
           moving torso (coverage fails; plate region sees DRIFT); exported-PNG body equality (a post-build edit is
           CHANGED 9 px; a near wing over the body is excused and counted); wing motion (identical copies are WINGS
           STILL although the body reads LOCKED).
The MOVED, REPOSED and LINES bob/turn cases are the sanity probe: the instrument is shown able to fail.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import flier_body_stabilize as S  # noqa: E402  (re-execs under the OpenCV venv when needed)
import cv2  # noqa: E402

FAILS = []
N = 160
BODY_POLY = [[62, 30], [98, 30], [104, 120], [92, 150], [68, 150], [56, 120]]


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + (f"  {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)


def texture(seed, shape):
    r = np.random.default_rng(seed).random(shape).astype(np.float32)
    return cv2.GaussianBlur(r, (0, 0), 1.2)


def body_layer(seed=1):
    a = np.zeros((N, N, 4), np.uint8)
    m = np.zeros((N, N), np.uint8)
    cv2.ellipse(m, (80, 80), (16, 40), 0, 0, 360, 255, -1)
    cv2.circle(m, (80, 40), 12, 255, -1)                       # head
    cv2.line(m, (80, 115), (80, 145), 255, 5)                  # tail
    t = texture(seed, (N, N))
    col = np.stack([90 + 120 * t, 70 + 80 * t, 40 + 60 * t], -1)
    a[..., :3] = col.clip(0, 255).astype(np.uint8)
    a[..., 3] = m
    edge = cv2.morphologyEx(m, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0
    a[edge, :3] = 20
    cv2.circle(a, (74, 38), 3, (250, 240, 60, 255), -1)        # eye
    a[..., 3] = m
    return a


def wing_layer(side, deg):
    a = np.zeros((N, N, 4), np.uint8)
    hx, hy = (66, 70) if side < 0 else (94, 70)
    tip = (hx + side * 60, hy - 10)
    poly = np.int32([[hx, hy - 6], tip, (hx + side * 50, hy + 22), (hx, hy + 14)])
    m = np.zeros((N, N), np.uint8)
    cv2.fillPoly(m, [poly], 255)
    t = texture(7 if side < 0 else 8, (N, N))
    a[..., 0], a[..., 1], a[..., 2] = (200 * t + 40), (180 * t + 40), (90 * t + 30)
    a[..., 3] = m
    R = cv2.getRotationMatrix2D((hx, hy), -side * deg, 1.0)
    return cv2.warpAffine(a, R, (N, N), flags=cv2.INTER_LINEAR)


def over(b, t):
    al = t[..., 3:4].astype(np.float32) / 255
    out = b.astype(np.float32) * (1 - al) + t.astype(np.float32) * al
    out[..., 3] = np.maximum(b[..., 3], t[..., 3])
    return out.astype(np.uint8)


def frames(body_for):
    out = []
    for k, deg in enumerate((25, 0, -25, 0)):
        f = np.zeros((N, N, 4), np.uint8)
        f = over(f, wing_layer(-1, deg))
        f = over(f, wing_layer(1, deg))
        out.append(over(f, body_for(k)))
    return out


def run(fr):
    mask = S.FC.poly_mask((N, N), [BODY_POLY]) & (fr[0][..., 3] > 128)
    return S.measure_facing(fr, mask)


def gpt_review_cases(B):
    """Cases the tool got wrong before the 2026-10-21 GPT review (design/RimMandrake/
    flier_authoring_architecture_2026-10-21.md). Each says what the old code did."""
    import tempfile
    from PIL import Image
    # (b) estimator failure on an UNCHANGED body is low confidence, not anatomy. Old: any ECC/feature failure was
    # RE-POSED. The failure is forced (SIFT reports too few inliers) so the classification is tested, not luck.
    real = S.est_features
    S.est_features = lambda ref, frm, mask: ({"ok": False, "inliers": 3, "keypoints": 50} if frm is not ref
                                             else real(ref, frm, mask))
    try:
        r = run(frames(lambda k: B))
    finally:
        S.est_features = real
    check("ESTIMATOR FAIL on an unchanged body -> UNMEASURED (old: RE-POSED)", r["verdict"] == "UNMEASURED",
          f"{r['verdict']} {r['why']}")

    # (a) ECC region in TEMPLATE coordinates. Old call put the reference mask in findTransformECC's inputMask
    # (input-image coords): at a 20 px body shift it read 0.23 px off at rho 0.918 (measured 2026-10-21).
    mv = cv2.warpAffine(B, np.float32([[1, 0, 20], [0, 1, 0]]), (N, N), flags=cv2.INTER_NEAREST)
    fr = frames(lambda k: mv if k == 2 else B)
    mask = S.FC.poly_mask((N, N), [BODY_POLY]) & (fr[0][..., 3] > 128)
    e = S.est_ecc(fr[0], fr[2], mask, np.float32([[1, 0, 21], [0, 1, -1]]))
    err = math.hypot(e.get("dx", 99) - 20, e.get("dy", 99)) if e.get("M") is not None else 99
    check("ECC templateMask: 20 px shift within 0.1 px, rho >= 0.95 (old inputMask: 0.23 px, rho 0.918)",
          err <= 0.1 and e.get("rho", 0) >= 0.95, f"err {err:.3f} rho {e.get('rho')}")

    # (c) head-only protect (the east annotations): the body is the PLATE region, so a torso that moves under a still
    # head is seen. Old body_mask_from = protect only: the head, LOCKED.
    fc = {"protect": [[[64, 24], [96, 24], [96, 54], [64, 54]]],                  # head box only
          "wings": [{"poly": [[0, 40], [66, 40], [66, 112], [0, 112]], "hinge": [66, 70]},
                    {"poly": [[94, 40], [160, 40], [160, 112], [94, 112]], "hinge": [94, 70]}]}
    lower = B.copy()
    lower[56:] = np.roll(B, 3, axis=0)[56:]                                       # torso and tail down 3 px
    fr = frames(lambda k: lower if k == 2 else B)
    old_mask = S.FC.poly_mask((N, N), fc["protect"]) & (fr[0][..., 3] > 128)
    new_mask = S.body_mask_from(fc, fr[0])
    cov_old, cov_new = S.coverage(fc, "south", old_mask), S.coverage(fc, "south", new_mask)
    check("COVERAGE head-only mask fails (wing roots / torso not covered)", not cov_old["ok"], str(cov_old))
    check("COVERAGE plate-region mask passes", cov_new["ok"], str(cov_new))
    r_blind = S.measure_facing(fr, old_mask, None, None)
    check("HEAD-ONLY mask without the coverage check reads LOCKED (the old blind spot, shown)",
          r_blind["verdict"] == "LOCKED", r_blind["verdict"])
    r_old = S.measure_facing(fr, old_mask, None, cov_old)
    r_new = S.measure_facing(fr, new_mask, None, cov_new)
    check("HEAD-ONLY protect + moving torso: head-only mask is UNMEASURED (old: LOCKED)", r_old["verdict"] == "UNMEASURED",
          r_old["verdict"])
    check("HEAD-ONLY protect + moving torso: plate-region mask sees it (DRIFT/APPEARANCE CHANGED)",
          r_new["verdict"] in ("DRIFT", "APPEARANCE CHANGED"), f"{r_new['verdict']} {r_new['why']}")

    # (d) body equality on EXPORTED PNGs. Old: flyer_cutout's plate_identical compared in-memory frames, so a
    # post-build step (Uvak_cleanup.py) touching the body was invisible.
    fcx = {"protect": [BODY_POLY], "order": "under",
           "wings": [{"poly": [[0, 20], [62, 20], [60, 120], [0, 120]], "hinge": [62, 70], "cycle": {"amp": 25}},
                     {"poly": [[98, 20], [160, 20], [160, 120], [100, 120]], "hinge": [98, 70], "sign": -1,
                      "cycle": {"amp": 25}}]}
    master = frames(lambda k: B)[1]
    comp, _plate, _cov = S.FC.compose_facing(master, fcx, 4)
    with tempfile.TemporaryDirectory() as td:
        paths = [Path(td) / f"F_{i + 1}_south.png" for i in range(4)]
        for p, a in zip(paths, comp):
            Image.fromarray(a, "RGBA").save(p)
        eq = S.exported_body_equality(paths, fcx, 0)
        check("EXPORTED body IDENTICAL on a clean cut-out bake", eq["verdict"] == "IDENTICAL", str(eq)[:200])
        a = np.asarray(Image.open(paths[2]).convert("RGBA")).copy()
        a[125:128, 79:82, :3] = 255 - a[125:128, 79:82, :3]                    # a "cleanup" touches 9 body px
        Image.fromarray(a, "RGBA").save(paths[2])
        eq = S.exported_body_equality(paths, fcx, 0)
        check("EXPORTED body CHANGED 9 px after a post-build edit (old: invisible)", eq["changed_px"] == 9,
              f"{eq['verdict']}")
        a = np.asarray(Image.open(paths[1]).convert("RGBA")).copy()
        a[100:102, 75:77, 3] = 0                                                 # 4 interior body px erased
        Image.fromarray(a, "RGBA").save(paths[1])
        eq = S.exported_body_equality(paths, fcx, 0)
        check("EXPORTED body: 4 erased interior px are CHANGED too (not dropped as 'soft rim')", eq["changed_px"] == 13,
              f"{eq['verdict']} holes {eq.get('interior_holes_px')}")
        # a near ("over") wing crossing the body is excused inside its swept envelope, and counted
        fco = json.loads(json.dumps(fcx))
        fco["falloff"] = 0
        fco["wings"][0].update(order="over", cycle={"amp": 25, "bias": 165})       # swung over onto the body
        comp, _p, _c = S.FC.compose_facing(master, fco, 4)
        for p, a in zip(paths, comp):
            Image.fromarray(a, "RGBA").save(p)
        eq = S.exported_body_equality(paths, fco, 0)
        check("EXPORTED body: near wing over the body is excused and counted, not CHANGED",
              eq["verdict"] == "IDENTICAL" and eq["excused_under_near_wing_px"] > 0, str(eq)[:200])

    # (e) wing-motion gate. Old: a set of identical copies passed every body gate (the Beldon lesson).
    still = frames(lambda k: B)
    still = [still[1]] * 4
    fcw = {"protect": [BODY_POLY], "wings": fcx["wings"]}
    wm = S.wing_motion(still, fcw, 0)
    check("WINGS identical copies -> WINGS STILL (old: LOCKED and nothing else)", wm["verdict"] == "WINGS STILL", str(wm))
    check("WINGS identical copies are LOCKED on the body (why a separate gate is needed)",
          run(still)["verdict"] == "LOCKED")
    wm = S.wing_motion(frames(lambda k: B), fcw, 0)
    check("WINGS flapping fixture -> FLAPS", wm["verdict"] == "FLAPS", str(wm))


def near_wing(k):
    """A side view's near wing: a textured blade drawn OVER the body, sweeping across its lower half."""
    a = np.zeros((N, N, 4), np.uint8)
    hx, hy = 80, 70
    poly = np.int32([[hx - 6, hy], [hx + 6, hy], (hx + 30, hy + 75), (hx - 30, hy + 75)])
    m = np.zeros((N, N), np.uint8)
    cv2.fillPoly(m, [poly], 255)
    t = texture(11, (N, N))
    a[..., 0], a[..., 1], a[..., 2] = (60 * t + 20), (200 * t + 30), (220 * t + 20)
    a[..., 3] = m
    R = cv2.getRotationMatrix2D((hx, hy), (40, 0, -40, 0)[k], 1.0)
    return cv2.warpAffine(a, R, (N, N), flags=cv2.INTER_LINEAR)


def near_wing_cases(B):
    """2026-11-03: a near wing sweeping over the body dragged the PARTS fit (Hawkbat east 2.3 px, Bogwing east 10.9 px)
    while ECC, features and the exported pixels read 0. The occluder (every pixel the near wing paints) leaves the
    parts templates; it must not hide a body that really moves."""
    env = np.zeros((N, N), bool)
    for k in range(4):
        env |= near_wing(k)[..., 3] > 0
    for _ in range(2):
        env = S.FC._dilate8(env)

    def fr_for(body_for):
        return [over(f, near_wing(k)) for k, f in enumerate(frames(body_for))]
    fr = fr_for(lambda k: B)
    mask = S.FC.poly_mask((N, N), [BODY_POLY]) & (fr[0][..., 3] > 128)
    blind = S.measure_facing(fr, mask)
    r = S.measure_facing(fr, mask, None, None, env)
    check("NEAR WING static body with the occluder -> LOCKED", r["verdict"] == "LOCKED", f"{r['verdict']} {r['worst']}")
    check("NEAR WING occluder leaves parts <= 0.5 px", r["worst"]["parts_px"] <= 0.5,
          f"with {r['worst']['parts_px']} px, without {blind['worst']['parts_px']} px")
    M = cv2.getRotationMatrix2D((80, 80), 4.0, 1.0)
    M[0, 2] += 3
    moved = cv2.warpAffine(B, M, (N, N), flags=cv2.INTER_CUBIC)
    fr = fr_for(lambda k: moved if k == 2 else B)
    r = S.measure_facing(fr, mask, None, None, env)
    check("NEAR WING moving body with the occluder still -> DRIFT", r["verdict"] in ("DRIFT", "APPEARANCE CHANGED"),
          f"{r['verdict']} {r['worst']}")
    p = r["rows"][2]["parts"]
    check("NEAR WING occluded parts still see the 4 deg turn", p.get("deg") is not None and abs(abs(p["deg"]) - 4.0) < 1.0,
          str(p))


def main() -> int:
    B = body_layer()
    r = run(frames(lambda k: B))
    w = r["worst"]
    check("STATIC verdict LOCKED", r["verdict"] == "LOCKED", f"{r['verdict']} {w}")
    check("STATIC <= 0.05 px/deg", max(w["ecc_px"], w["feat_px"], w["ecc_deg"], w["feat_deg"]) <= 0.05, str(w))

    M = cv2.getRotationMatrix2D((80, 80), 4.0, 1.0)
    M[0, 2] += 3
    M[1, 2] -= 2
    moved = cv2.warpAffine(B, M, (N, N), flags=cv2.INTER_CUBIC)
    r = run(frames(lambda k: moved if k == 2 else B))
    row = r["rows"][2]
    cx, cy = r["body_centre"]
    tx, ty = S.body_motion_at(M, cx, cy)
    tdeg = math.degrees(math.atan2(M[1, 0], M[0, 0]))
    for name in ("ecc", "features"):
        e = row["_ecc" if name == "ecc" else "_feat"]
        if e.get("M") is None:
            check(f"MOVED {name} estimated", False)
            continue
        ex, ey = S.body_motion_at(e["M"], cx, cy)
        err_px, err_deg = math.hypot(ex - tx, ey - ty), abs(e["deg"] - tdeg)
        check(f"MOVED {name} recovers shift < 1 px", err_px < 1.0, f"got ({ex:.2f},{ey:.2f}) truth ({tx:.2f},{ty:.2f})")
        check(f"MOVED {name} recovers angle < 0.5 deg", err_deg < 0.5, f"got {e['deg']:.2f} truth {tdeg:.2f}")
    p = row["parts"]
    check("MOVED parts angle within 1 deg", p.get("deg") is not None and abs(abs(p["deg"]) - 4.0) < 1.0, f"{p}")
    check("MOVED verdict DRIFT", r["verdict"] == "DRIFT", r["verdict"])

    other = body_layer(seed=99)
    other = np.ascontiguousarray(np.flipud(other))               # a different drawing / pose
    r = run(frames(lambda k: other if k == 2 else B))
    check("REPOSED verdict APPEARANCE CHANGED (residual evidence)", r["verdict"] == "APPEARANCE CHANGED",
          f"{r['verdict']} {r['why']}")
    gpt_review_cases(B)
    near_wing_cases(B)
    # Owner's line test: eye line and shoulder line must stay put on a static body and must SEE a bob and a turn.
    # the body annotation hugs the body here, as the real sets' do (BODY_POLY is loose and takes in wing pixels)
    fc = {"protect": [[[67, 30], [93, 30], [95, 80], [92, 150], [68, 150], [65, 80]]], "eyes": [[74, 38], [86, 38]],
          "wings": [{"poly": [[0, 10], [67, 10], [67, 110], [0, 110]], "hinge": [66, 70]},
                    {"poly": [[93, 10], [160, 10], [160, 110], [93, 110]], "hinge": [94, 70]}]}
    lc = S.line_check(frames(lambda k: B), fc, "south", 0)
    w = lc["worst"]
    check("LINES static LEVEL", lc["verdict"] == "LEVEL", f"{lc['verdict']} {w}")
    bob = cv2.warpAffine(B, np.float32([[1, 0, 0], [0, 1, 3]]), (N, N), flags=cv2.INTER_NEAREST)
    lc = S.line_check(frames(lambda k: bob if k == 2 else B), fc, "south", 0)
    for n in ("eye", "shoulder"):
        dy = lc["lines"][n]["rows"][2].get("dy")
        check(f"LINES bob +3 px seen on the {n} line", dy is not None and abs(dy - 3.0) < 0.5, f"dy {dy}")
    check("LINES bob verdict MOVING", lc["verdict"] == "MOVING", lc["verdict"])
    # a whole flier turned 4 deg (body and wing roots together); the angle resolution is ~0.5 px over the line's
    # length, so the probe uses lines of 20 px and more and asks for the turn within 1.5 deg
    fc["eyes"] = [[70, 40], [90, 40]]
    fr = frames(lambda k: B)
    fr[2] = cv2.warpAffine(fr[2], cv2.getRotationMatrix2D((80, 80), 4.0, 1.0), (N, N), flags=cv2.INTER_CUBIC)
    lc = S.line_check(fr, fc, "south", 0)
    for n in ("eye", "shoulder"):
        dd = lc["lines"][n]["rows"][2].get("ddeg")
        check(f"LINES 4 deg turn seen on the {n} line", dd is not None and abs(abs(dd) - 4.0) < 1.5, f"ddeg {dd}")
    check("LINES turn verdict MOVING", lc["verdict"] == "MOVING", lc["verdict"])
    # GPT gpt_flier A3 P1 (FLIER_LINE_CHECK_FIX_SIDEWAYS_UNSEEN): the old gate saw only the midpoint's height and the
    # angle, so a sideways slide of both eyes, or the eyes spreading apart along their row, read LEVEL.
    fc["eyes"] = [[74, 38], [86, 38]]
    lc = S.line_check(frames(lambda k: B), fc, "south", 0)
    check("LINES identical frames LEVEL (endpoint gate)", lc["verdict"] == "LEVEL",
          f"{lc['verdict']} {lc['worst']} {lc.get('eye_shoulder')}")
    side = cv2.warpAffine(B, np.float32([[1, 0, 3], [0, 1, 0]]), (N, N), flags=cv2.INTER_NEAREST)
    lc = S.line_check(frames(lambda k: side if k == 2 else B), fc, "south", 0)
    e = lc["lines"]["eye"]["rows"][2]
    check("LINES sideways +3 px: midpoint height and angle unchanged (old gate blind)",
          abs(e.get("dy", 9)) <= S.LINE_TOL_PX and abs(e.get("ddeg", 9)) <= lc["worst"]["eye"]["tol_deg"], str(e))
    check("LINES sideways +3 px seen as endpoint dx 3 on both eyes",
          all(abs(d[0] - 3.0) < 0.5 for d in e.get("end_d", [])) and len(e.get("end_d", [])) == 2, str(e.get("end_d")))
    check("LINES sideways verdict MOVING", lc["verdict"] == "MOVING", lc["verdict"])
    # eyes spread apart along their own row: each half of the head pulled 2 px outward (the line stays level, centred)
    spread = B.copy()
    spread[:, :78] = np.roll(B[:, :78], -2, axis=1)
    spread[:, 82:] = np.roll(B[:, 82:], 2, axis=1)
    spread[:, 78:82] = B[:, 78:82]
    lc = S.line_check(frames(lambda k: spread if k == 2 else B), fc, "south", 0)
    e = lc["lines"]["eye"]["rows"][2]
    check("LINES spread: midpoint height and angle unchanged (old gate blind)",
          abs(e.get("dy", 9)) <= S.LINE_TOL_PX and abs(e.get("ddeg", 9)) <= lc["worst"]["eye"]["tol_deg"], str(e))
    check("LINES spread seen as a length change ~4 px", abs(e.get("dlen", 0) - 4.0) < 1.0, f"dlen {e.get('dlen')}")
    check("LINES spread verdict MOVING", lc["verdict"] == "MOVING", lc["verdict"])
    # the length gate on its own (blind check at 8d60822a: the 2 px spread above is already caught by the endpoint
    # gate). The tracker is stubbed so frame 3 puts each eye 0.8 px outward along the row: every endpoint, the
    # midpoint, the angle and the eye-to-shoulder distance are within LINE_TOL_PX; only the length (+1.6 px) is not.
    # A 0.8 px slide of both eyes the same way is the control: same endpoint numbers, no length change, LEVEL.
    real_tp = S.track_point

    def stub(shift):
        def tp(g_ref, g, mmask, p, r, search):
            dx = shift(p) if g is moved_g[0] else 0.0
            return {"ok": True, "score": 1.0, "pt": (float(p[0]) + dx, float(p[1]))}
        return tp
    real_ge = S.grey_edges
    fr = frames(lambda k: B)
    moved_g = [None]

    def ge(f):
        g = real_ge(f)
        if f is fr[2]:
            moved_g[0] = g
        return g
    S.grey_edges = ge
    try:
        eye_x = sorted(p[0] for p in fc["eyes"])
        S.track_point = stub(lambda p: (-0.8 if p[0] <= eye_x[0] else 0.8) if p in fc["eyes"] or list(p) in fc["eyes"]
                             else 0.0)
        lc = S.line_check(fr, fc, "south", 0)
        w, e = lc["worst"]["eye"], lc["lines"]["eye"]["rows"][2]
        check("LINES sub-tol spread: endpoints, midpoint, angle, eye-to-shoulder all within LINE_TOL_PX",
              w["end_px"] <= S.LINE_TOL_PX and w["dy_px"] <= S.LINE_TOL_PX and w["ddeg"] <= w["tol_deg"]
              and lc["eye_shoulder"]["worst_change_px"] <= S.LINE_TOL_PX and lc["worst"]["shoulder"]["dlen_px"] == 0,
              f"{w} {lc.get('eye_shoulder')}")
        check("LINES sub-tol spread seen as a length change 1.6 px", abs(e.get("dlen", 0) - 1.6) < 0.05,
              f"dlen {e.get('dlen')}")
        check("LINES sub-tol spread verdict MOVING (length gate alone)", lc["verdict"] == "MOVING", lc["verdict"])
        S.track_point = stub(lambda p: 0.8 if p in fc["eyes"] or list(p) in fc["eyes"] else 0.0)
        lc = S.line_check(fr, fc, "south", 0)
        check("LINES sub-tol slide (control, no length change) verdict LEVEL", lc["verdict"] == "LEVEL",
              f"{lc['verdict']} {lc['worst']}")
    finally:
        S.track_point, S.grey_edges = real_tp, real_ge
    # eye-to-shoulder distance: the head bobbed 3 px down onto a still torso and still wing roots
    head = B.copy()
    head[:60] = np.roll(B[:60], 3, axis=0)
    lc = S.line_check(frames(lambda k: head if k == 2 else B), fc, "south", 0)
    es = lc["lines"]["eye"]["rows"][2].get("d_eye_shoulder")
    check("LINES head bob seen as eye-to-shoulder change ~3 px", es is not None and abs(abs(es) - 3.0) < 0.75, f"{es}")
    # proxy points are labelled as such: north's head-reference line is not an eye measurement
    lab = S.eye_points(fc, "north", B)[1]
    check("LINES north eye line labelled PROXY head-reference", lab.startswith("PROXY") and "not eyes" in lab, lab)
    many = {**fc, "wings": fc["wings"] + [{"poly": [[0, 110], [67, 110], [67, 150], [0, 150]], "hinge": [66, 120]}]}
    lab = S.shoulder_points(many, "south", B)[1]
    check("LINES three-wing shoulder line labelled PROXY first two", lab.startswith("PROXY first two of 3"), lab)
    lab = S.shoulder_points(fc, "south", B)[1]
    check("LINES two-wing shoulder line not a proxy", not lab.startswith("PROXY"), lab)
    print("FAIL" if FAILS else "PASS", "selftest_flier_body_stabilize", FAILS or "")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
