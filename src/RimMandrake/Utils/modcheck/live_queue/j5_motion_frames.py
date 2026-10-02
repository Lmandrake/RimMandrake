"""J5 (STUB): FlowWorks motion frames -- capture a frame SEQUENCE of a canal filling from a limitless source.

Bars this feeds (FlowWorks north star, all about CHANGE, which one still frame cannot show):
canal_fill_front_watchable, canal_fill_spreads_along_itself. The other motion bars (reservoir_fill_visibly_drops,
reservoir_shoreline_recedes, tar_fill_front_lags_water, pawn_lowers_on_deeper_cell) reuse this capture loop
with their own plot setup once this one has run live.

CAPTURE ONLY. The frame-sequence JUDGE is deferred by the owner's 2026-09-17 ruling recorded in
NORTHSTAR_MOTION_FRAMES_1 ("file it as TBD ... until we can play with it live first"): this job grades nothing
visual. It produces a manifest (frames + ticks + the engine's own fill vector per frame) for him to look at.

Setup is plot C of src/RimMandrake/FlowWorks/validation.py, called through its own helpers so the geometry
cannot drift from the suite: a 1x10 D=1 channel dug from a limitless WaterDeep body, depth engine running.
Then N frames, one per engine pulse, of the same cell rect.

Checks (each can FAIL): N valid PNG frames; frames are not all byte-identical; the channel's fill vector moved
between the first and last frame (the engine's state is the motion witness, not the pixels); the run did not
abort on a surprise.
"""
import importlib.util
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, call, main   # noqa: E402

N_FRAMES = 8


def load_flowworks():
    path = os.path.join(ROOT, "src", "RimMandrake", "FlowWorks", "validation.py")
    spec = importlib.util.spec_from_file_location("lq_flowworks_validation", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def body(s, job):
    import helpers as H
    from surprise import png_info
    from suite import TestContext
    from watch import Watch, SurpriseAbort
    ax, az, _d = H.safe_anchor(s)
    w = Watch(s, (ax, az), os.path.join(job.outdir, "surprises"), mod="FlowWorks", chain="motion_frames",
              policy="abort", resurrect=True)
    frames, aborted = [], None
    with w:
        t = TestContext(s, anchor=(ax, az), watch=w)
        try:
            if job.dry_run:
                fill = [0] * 10

                def step(i):
                    w.wait(None, 250)
                    for k in range(min(10, i + 1)):
                        fill[k] = 1
                    r = call(s, "rimworld/take_screenshot", fileName="motion_%02d" % i)
                    return r.get("path"), [(1, f) for f in fill]
            else:
                fw = load_flowworks()
                x0, z0 = fw._prep_plot(t, "C")
                fw._limitless_source(t, "C")
                cells = fw._channel_from(x0 + 10, z0 + 6, 10)
                fw._dig_run(t, cells, 1)
                rect = (x0, z0 + 2, 22, 10)
                job.note("rect", rect)

                def step(i):
                    fw._wait(t, fw.PULSE)
                    return fw._frame(t, *rect, name="motion_%02d" % i), fw._state(t, cells)
            for i in range(N_FRAMES):
                path, state = step(i)
                info = png_info(path) if path else {"ok": False, "why": "no path"}
                tick = call(s, "jawa/time_clock").get("ticksGame")
                frames.append({"i": i, "tick": tick, "png": path, "ok": info.get("ok"), "md5": info.get("md5"),
                               "fill": [f for _, f in state]})
        except SurpriseAbort as e:
            aborted = e.summary()
    manifest = os.path.join(job.outdir, "motion_manifest.json")
    with open(manifest, "w", encoding="utf-8") as f:
        json.dump({"bars": ["canal_fill_front_watchable", "canal_fill_spreads_along_itself"], "frames": frames,
                   "aborted": aborted, "judge": "DEFERRED (owner 2026-09-17, NORTHSTAR_MOTION_FRAMES_1)"}, f, indent=1)
    job.note("manifest", os.path.relpath(manifest, ROOT))
    job.note("frames", frames)
    job.check("the capture ran without a surprise abort", aborted is None, aborted)
    good = [fr for fr in frames if fr["ok"]]
    job.check("%d valid PNG frames captured" % N_FRAMES, len(good) >= N_FRAMES, [fr.get("png") for fr in frames if not fr["ok"]])
    job.check("frames are not all byte-identical", len({fr["md5"] for fr in good}) > 1, len({fr["md5"] for fr in good}))
    moved = len(frames) >= 2 and sum(x or 0 for x in frames[-1]["fill"]) > sum(x or 0 for x in frames[0]["fill"])
    job.check("the channel fill vector advanced between first and last frame (engine state = motion witness)",
              moved, [fr["fill"] for fr in frames[:1] + frames[-1:]])


def fake_world():
    import common
    from rimdrive.fake import FakeWorld, pawn_row
    w = FakeWorld(pawns=[pawn_row("Col1"), pawn_row("Col2", x=103)])
    w.shot_dir = os.path.join(common.DRY_OUTDIR, "J5_fake_shots")
    os.makedirs(w.shot_dir, exist_ok=True)
    return w


if __name__ == "__main__":
    sys.exit(main("J5_motion_frames", body, fake_builder=fake_world))
