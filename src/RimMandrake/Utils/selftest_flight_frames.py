#!/usr/bin/env python3
"""selftest_flight_frames - the flapping-bird judge (flight_frames.py) on hand-made series. No game, no picture.

RIMMANDRAKE_BUILD_FLIGHT_PROBES_STATE_AND_FRAME_NO_PICTURES. Eight checks:
  1. a full flight passes (the series is read through the track names that scene_cond.flight() records);
  2. a skipped state fails;
  3. a flip-book that repeats one frame fails;
  4. a frame held for the wrong number of ticks fails;
  5. a landing that keeps a flying picture fails;
  6. a bird still in the air at the limit is not judged (and does not spoil another bird's pass);
  7. "no bird took off" is an allowed miss;
  8. the asset audit names a missing texture.
Checks 2 to 5 and 8 are planted faults: each must be seen red. The hold pattern below is written out by hand from the
game's code (frame 0 for 1 tick, each middle frame for tpf ticks, the last frame for 3*tpf-1), not computed by the
module under test. Exit 0 all pass, 1 a failure.

    python3 src/RimMandrake/Utils/selftest_flight_frames.py
"""
import copy
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import flight_frames as F  # noqa: E402
import scene_cond  # noqa: E402

FAILS = []
PREFIX = "Things/Pawn/Animal/Chicken/Chicken_Flying_"
CHICKEN = {"prefix": PREFIX, "frames": 8, "tpf": 2}
# one loop of the Chicken fly animation (8 frames, 2 ticks a frame, 18 ticks), anim tick 0..17
LOOP_TPF2 = [0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 7, 7, 7]
# the same 8 frames at 3 ticks a frame (27 ticks): what a wrong tpf would show
LOOP_TPF3 = [0] + [1] * 3 + [2] * 3 + [3] * 3 + [4] * 3 + [5] * 3 + [6] * 3 + [7] * 8


def check(ok, what, detail=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", what, (": " + str(detail)) if detail and not ok else ""))
    if not ok:
        FAILS.append(what)


def row(tick, state, lerp=0, anim="", start=-99999, graphic="", texpath="", facing="east"):
    return {"tick": tick, "state": state, "lerp": lerp, "height": 0.0 if state == "Grounded" else 0.5, "anim": anim, "start": start, "graphic": graphic,
            "texpath": texpath, "facing": facing}


def flight(t0=100, ground_before=5, flying=60, ground_after=4, loop=LOOP_TPF2, anim="ChickenFlyEast"):
    """A whole natural flight: Grounded, TakingOff lerp 0..49, Flying, Landing lerp 0..49, Grounded."""
    rows, t = [], t0
    for _ in range(ground_before):
        rows.append(row(t, "Grounded"))
        t += 1
    start = t
    plan = [("TakingOff", i) for i in range(50)] + [("Flying", 0)] * flying + [("Landing", i) for i in range(50)]
    for state, lerp in plan + [("Grounded", 0)]:        # the first Grounded row still carries the animation
        i = loop[(t - start) % len(loop)]
        rows.append(row(t, state, lerp, anim, start, "%s_%d" % (anim, i), "%s%d_east" % (PREFIX, i + 1)))
        t += 1
    for _ in range(ground_after - 1):
        rows.append(row(t, "Grounded"))
        t += 1
    return rows


def codes(v):
    return sorted({f["code"] for f in v["faults"]})


def t_a_full_flight_passes():
    """a full flight passes, read through the names that c.flight() records"""
    good = flight()
    tracks = scene_cond.flight("thing:Chicken101")
    names = [t.name for t in tracks]
    frames = [(r["tick"], {t.name: {"st": "ok", "v": r[f]} for t, f in zip(tracks, F.FIELDS)}, {}) for r in good]
    probes_ok = all(isinstance(t, scene_cond.ProbeTrack) and t.probe["pawn"] == "Chicken101" for t in tracks) \
        and sorted(t.probe["p"] for t in tracks) == sorted(F.PROBE_OF.values())
    v1 = F.judge_bird(F.series_from_frames(frames, "Chicken101"), CHICKEN)
    check(probes_ok and len(set(names)) == 8 and v1["verdict"] == F.PASS and F.outcome({"b": v1}) == "SUCCESS",
          "a full flight passes", (names, v1["verdict"], v1["faults"][:2]))


def t_a_skipped_state_fails():
    """a skipped state fails: the bird drops from Flying straight to Grounded (Landing never happens)"""
    s2 = flight()
    for r in s2:
        if r["state"] == "Landing":
            r["state"], r["lerp"] = "Flying", 0
    v2 = F.judge_bird(s2, CHICKEN)
    check(v2["verdict"] == F.FAIL and "STATE_SKIP" in codes(v2) and F.outcome({"b": v2}) == "MOD FAILURE",
          "a skipped state fails", (v2["verdict"], codes(v2)))


def t_a_flip_book_that_repeats_one_frame_fails():
    """a flip-book that repeats one frame fails (the animation shows frame 0 on every tick)"""
    s3 = flight()
    for r in s3:
        if r["anim"]:
            r["graphic"], r["texpath"] = r["anim"] + "_0", PREFIX + "1_east"
    v3 = F.judge_bird(s3, CHICKEN)
    check(v3["verdict"] == F.FAIL and "FROZEN" in codes(v3), "a flip-book that repeats one frame fails", codes(v3))


def t_a_frame_held_for_the_wrong_number_of_ticks_fails():
    """a frame held for the wrong number of ticks fails (3 ticks a frame where the def says 2); every frame is shown"""
    s4 = flight(loop=LOOP_TPF3)
    v4 = F.judge_bird(s4, CHICKEN)
    check(v4["verdict"] == F.FAIL and "FRAME" in codes(v4) and "FROZEN" not in codes(v4),
          "a frame held for the wrong number of ticks fails", codes(v4))


def t_a_landing_that_keeps_a_flying_picture_fails():
    """a landing that keeps a flying picture fails (the animation is never cleared on the ground)"""
    s5 = flight()
    last_air = max(i for i, r in enumerate(s5) if r["anim"])
    for r in s5[last_air + 1:]:
        r.update(anim=s5[last_air]["anim"], start=s5[last_air]["start"], graphic=s5[last_air]["graphic"],
                 texpath=s5[last_air]["texpath"])
    v5 = F.judge_bird(s5, CHICKEN)
    check(v5["verdict"] == F.FAIL and "LANDED_FLYING" in codes(v5), "a landing that keeps a flying picture fails", codes(v5))


def t_a_bird_still_in_the_air_at_the_limit_is_not_judged():
    """a bird still in the air at the limit is not judged, and is no miss: alone, the run has no reading; beside a"""
    #    bird that passed, the run is a SUCCESS
    s6 = [r for r in flight() if r["tick"] < 100 + 5 + 50 + 30]
    v6 = F.judge_bird(s6, CHICKEN)
    check(v6["verdict"] == F.NOT_JUDGED and not v6["faults"] and F.outcome({"a": v6}) == "COULD NOT LOOK"
          and F.outcome({"a": v6, "b": F.judge_bird(flight(), CHICKEN)}) == "SUCCESS", "a bird still in the air at the limit is not judged",
          (v6["verdict"], v6.get("flights")))


def t_no_bird_took_off_is_an_allowed_miss():
    """"no bird took off" is an allowed miss"""
    s7 = [row(t, "Grounded") for t in range(100, 400)]
    v7 = F.judge_bird(s7, CHICKEN)
    check(v7["verdict"] == F.NO_FLIGHT and F.outcome({"a": v7, "b": copy.deepcopy(v7)}) == "RANDOM MISS",
          "\"no bird took off\" is an allowed miss", v7["verdict"])


def t_the_asset_audit_names_a_missing_texture():
    """the asset audit names a missing texture (planted), passes the full set, and passes a real flyer of ours"""
    with tempfile.TemporaryDirectory() as tmp:
        kind = {"prefix": "Things/Pawn/Animal/RM_Test/RM_Test_Flying_", "frames": 4, "tpf": 3}
        for i in range(1, 5):
            for d in ("east", "north", "south"):
                p = os.path.join(tmp, "%s%d_%s.png" % (kind["prefix"], i, d))
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, "wb").close()
        full = F.audit(kind, [tmp])
        os.remove(os.path.join(tmp, kind["prefix"] + "3_north.png"))
        miss = F.audit(kind, [tmp])
    real = F.kind_of("RM_Skiralim")
    real_miss = F.audit(real, F.textures_roots(real["mod"])) if real else ["RM_Skiralim not found"]
    check(full == [] and miss == ["Things/Pawn/Animal/RM_Test/RM_Test_Flying_3_north.png"] and real_miss == [],
          "the asset audit names a missing texture", (full, miss, real_miss))


def main():
    t_a_full_flight_passes()
    t_a_skipped_state_fails()
    t_a_flip_book_that_repeats_one_frame_fails()
    t_a_frame_held_for_the_wrong_number_of_ticks_fails()
    t_a_landing_that_keeps_a_flying_picture_fails()
    t_a_bird_still_in_the_air_at_the_limit_is_not_judged()
    t_no_bird_took_off_is_an_allowed_miss()
    t_the_asset_audit_names_a_missing_texture()
    print("flight frames selftest: %s" % ("FAIL %d" % len(FAILS) if FAILS else "8 checks passed"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
