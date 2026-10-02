#!/usr/bin/env python3
"""Selftest for NORTHSTAR_MOTION_FRAMES_1 -- a `(change)` must-show line is
judged on an ORDERED frame sequence, not on the last screenshot (spec §4b).

Offline and deterministic: the judge runs through its `runner=` injection
point with a FAKE judge that actually looks at the frames -- it reads the
frame paths out of the prompt, in order, and answers NO when every frame is
byte-identical. So a static sequence must FAIL a 'moves' bar and a changing one
must pass: the check is shown able to fail, not merely able to pass.

Run: python3 src/RimMandrake/Utils/modcheck/selftest_motion_frames.py
"""

import json
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import judge          # noqa: E402
import northstar      # noqa: E402
import runner         # noqa: E402
import suite as suite_mod  # noqa: E402

FAILED = []


def ok(cond, label):
    print("%-4s %s" % ("ok" if cond else "FAIL", label))
    if not cond:
        FAILED.append(label)


WALK = """\
# Demo -- validation walk

## north star
state: DRAFT
validated-hash:

### the experience  (OWNER'S WORDS)
The boundary travels.

### must show
- [ ] `boundary_visible` -- two areas are visibly separate
- [ ] `boundary_moves` (change) -- the boundary is seen to travel between frames,
      not merely to exist
- [ ] `stays_lit` (state) -- the reference light is lit

### cannot show
- [ ] `never_frozen` (change) -- the scene is identical in every frame

## must be true
- x
"""

_FRAME = re.compile(r"^Frame (\d+) of (\d+).*read the image at: (.+)$", re.M)


def seeing_judge(prompts):
    """A fake judge that LOOKS: NO if every frame is byte-identical, YES if any
    differs. A single-image prompt answers YES (state lines are not under test
    here). Records each prompt so order can be asserted."""
    def run(prompt):
        prompts.append(prompt)
        frames = _FRAME.findall(prompt)
        if not frames:
            return True, json.dumps({"verdict": "YES", "why": "state"})
        blobs = [open(p.strip(), "rb").read() for _, _, p in frames]
        changed = any(b != blobs[0] for b in blobs[1:])
        if "never_frozen" in prompt:
            # cannot-show line: TRUE of a static sequence
            return True, json.dumps({"verdict": "NO" if changed else "YES", "why": "fake"})
        return True, json.dumps({"verdict": "YES" if changed else "NO", "why": "fake"})
    return run


def _frames(tmp, tag, contents):
    out = []
    for i, c in enumerate(contents):
        p = os.path.join(tmp, "%s_%d.png" % (tag, i))
        with open(p, "wb") as fh:
            fh.write(c)
        out.append(p)
    return out


def test_parse_kind_tag():
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "Demo.md")
        open(p, "w").write(WALK)
        ns = northstar.parse(p)
        ok(ns["kinds"] == {"boundary_visible": "state", "boundary_moves": "change",
                           "stays_lit": "state", "never_frozen": "change"},
           "`(change)`/`(state)`/bare id parse to the right kinds: %r" % ns["kinds"])
        ok(ns["must_show_text"]["boundary_moves"].startswith("the boundary is seen"),
           "the `(change)` tag is stripped from the prose the judge reads")
        ok(ns["must_show"] == ["boundary_visible", "boundary_moves", "stays_lit"],
           "ids unchanged by the tag")
        ok(northstar.kinds_for(p) == {}, "a DRAFT section yields no kinds")
        northstar.record_validation(p)
        ok(northstar.kinds_for(p).get("boundary_moves") == "change",
           "a VALIDATED section yields its kinds")


def test_static_fails_and_changing_passes():
    text = {"boundary_moves": "the boundary is seen to travel"}
    kinds = {"boundary_moves": "change"}
    with tempfile.TemporaryDirectory() as tmp:
        static = _frames(tmp, "static", [b"A", b"A", b"A"])
        moving = _frames(tmp, "moving", [b"A", b"B", b"C"])

        prompts = []
        r = judge.judge_component({"shows": ["boundary_moves"], "screenshots": static,
                                   "sequences": [{"paths": static, "ticks": [0, 60, 120]}]},
                                  text, runner=seeing_judge(prompts), kinds=kinds)
        ok(r[0]["verdict"] == "NO" and not r[0]["pass"],
           "a STATIC sequence FAILS a 'moves' bar: %s" % r[0]["verdict"])

        prompts = []
        r = judge.judge_component({"shows": ["boundary_moves"], "screenshots": moving,
                                   "sequences": [{"paths": moving, "ticks": [0, 60, 120]}]},
                                  text, runner=seeing_judge(prompts), kinds=kinds)
        ok(r[0]["verdict"] == "YES" and r[0]["pass"],
           "a CHANGING sequence passes the same bar: %s" % r[0]["verdict"])
        seen = [p.strip() for _, _, p in _FRAME.findall(prompts[0])]
        ok(seen == moving, "the judge is shown every frame, in capture order")
        ok("tick offset +60" in prompts[0], "frame tick offsets reach the prompt")
        ok(len(prompts) == 1, "the whole sequence is ONE judgement, not one per frame")

        # Same changing frames, judged the OLD way (state, last frame only):
        # the judge never sees a sequence. This is the defect §4b names.
        prompts = []
        judge.judge_component({"shows": ["boundary_moves"], "screenshots": moving},
                              text, runner=seeing_judge(prompts), kinds={})
        ok(not _FRAME.findall(prompts[0]) and moving[-1] in prompts[0],
           "a bare (state) line is still judged on shots[-1] alone")


def test_one_frame_change_line_is_unjudgeable():
    with tempfile.TemporaryDirectory() as tmp:
        one = _frames(tmp, "one", [b"A"])
        calls = []
        r = judge.judge_component({"shows": ["boundary_moves"], "screenshots": one},
                                  {"boundary_moves": "travels"},
                                  runner=lambda p: (calls.append(p), (True, '{"verdict":"YES","why":"x"}'))[1],
                                  kinds={"boundary_moves": "change"})
        ok(r[0]["verdict"] == judge.UNJUDGEABLE and not r[0]["pass"],
           "a (change) line with one frame is UNJUDGEABLE, never a partial pass")
        ok(not calls, "and the judge is not even asked")


def test_screenshots_fallback_when_no_sequence():
    with tempfile.TemporaryDirectory() as tmp:
        moving = _frames(tmp, "mv", [b"A", b"B"])
        prompts = []
        r = judge.judge_component({"shows": ["boundary_moves"], "screenshots": moving},
                                  {"boundary_moves": "travels"},
                                  runner=seeing_judge(prompts),
                                  kinds={"boundary_moves": "change"})
        ok(r[0]["verdict"] == "YES" and len(_FRAME.findall(prompts[0])) == 2,
           "without capture_frames, all screenshots in order are the sequence")


def test_cannot_show_change_line_polarity():
    with tempfile.TemporaryDirectory() as tmp:
        static = _frames(tmp, "s", [b"A", b"A"])
        moving = _frames(tmp, "m", [b"A", b"B"])
        cannot = {"never_frozen": "the scene is identical in every frame"}
        kinds = {"never_frozen": "change"}
        r = judge.judge_component({"shows": ["never_frozen"], "screenshots": static},
                                  {}, cannot, runner=seeing_judge([]), kinds=kinds)
        ok(not r[0]["pass"], "a static sequence trips a (change) cannot-show line")
        r = judge.judge_component({"shows": ["never_frozen"], "screenshots": moving},
                                  {}, cannot, runner=seeing_judge([]), kinds=kinds)
        ok(r[0]["pass"], "a changing sequence clears it")


def test_apply_judgement_carries_kinds():
    with tempfile.TemporaryDirectory() as tmp:
        static = _frames(tmp, "s", [b"A", b"A"])
        s = {"chains": [{"components": [{"name": "c", "verdict": "PASS",
                                         "shows": ["boundary_moves"],
                                         "screenshots": static}]}],
             "all_green": True}
        runner.apply_judgement(s, {"boundary_moves": "travels"}, {},
                               judge_runner=seeing_judge([]),
                               kinds={"boundary_moves": "change"})
        ok(s["state_all_green"] and not s["all_green"],
           "state green + static frames on a change bar is NOT green")


class _Stub(object):
    """Just enough of TestContext for capture_frames: no bridge."""
    def __init__(self):
        self._current = suite_mod.Component("c", None, False, ["boundary_moves"])
        self.log = []

    def _guard(self):
        return True

    def wait_ticks(self, n):
        self.log.append(("wait", n))

    def screenshot(self, name=None, rect=None, padding=1):
        self.log.append(("shot", name))
        path = "%s.png" % name
        self._current.screenshots.append(path)
        return path


def test_capture_frames_helper():
    st = _Stub()
    paths = suite_mod.TestContext.capture_frames(st, 3, 250, name="b")
    ok(paths == ["b_f1.png", "b_f2.png", "b_f3.png"], "capture_frames returns N ordered frames")
    ok([k for k, _ in st.log] == ["shot", "wait", "shot", "wait", "shot"],
       "frames are separated by wait_ticks, none before the first")
    ok(st._current.sequences == [{"paths": paths, "ticks": [0, 250, 500]}],
       "the sequence is recorded with tick offsets")
    ok(judge.evidence_frames(st._current.as_dict())[2] == {"path": "b_f3.png", "tick": 500},
       "the judge reads the recorded sequence")
    try:
        suite_mod.TestContext.capture_frames(st, 1, 250)
        ok(False, "capture_frames(n=1) refuses")
    except ValueError:
        ok(True, "capture_frames(n=1) refuses")


def main():
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print("\n%d failure(s)" % len(FAILED))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
