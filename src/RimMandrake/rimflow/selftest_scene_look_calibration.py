#!/usr/bin/env python3
"""selftest_scene_look_calibration.py - scene_look_calibration.py, the scene_look_judge_brief row's model_check
(RIMMANDRAKE_SEED_SCENE_LOOK_CALIBRATION_BRIM_PIT_PAIR). A mock runner stands in for `claude -p`: no model, no network.

The registry row runs it and plants the brim-pit pair both ways; the cases go through judge_cli's own pass-1 and pass-2
prompts; a right pair is CALIBRATED, one wrong answer FAILED, a dead call or a crop off its pin did not run (UNTESTED,
never a pass), COULD NOT SEE and UNJUDGEABLE are not as planted, an unreadable answer is malformed, and the unplanted
1 m open look is recorded without deciding the status."""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import refusal_contract as RC  # noqa: E402
import scene_look_calibration as SL  # noqa: E402

FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def env(text, err=False):
    return json.dumps({"type": "result", "is_error": err, "result": text})


def open_answer(look):
    return env('I see a pit of water with a ladder.\n{"look": "%s", "where": "the north rim", '
               '"first_noticed": "only the ladder hooks show"}' % look)


def bar_answer(v):
    return env('{"verdict": "%s", "why": "the ladder above the water line"}' % v)


RIGHT = {("crop_pit6.png", 1): open_answer("WRONG"), ("crop_pit6.png", 2): bar_answer("NO"),
         ("crop_pit3.png", 2): bar_answer("YES"), ("crop_pit3.png", 1): open_answer("ODD")}


def but(key, answer):
    """RIGHT with one answer changed."""
    a = dict(RIGHT)
    a[key] = answer
    return a


def mock(answers, seen):
    def runner(prompt_for, image):
        prompt = prompt_for(image)
        k = 1 if prompt == SL.JC.OPEN_PROMPT.format(image=image) else 2
        seen.append((os.path.basename(image), k, prompt))
        a = answers[(os.path.basename(image), k)]
        return (False, a[1]) if isinstance(a, tuple) else (True, a)
    return runner


def status_of(answers, pins=None):
    seen, lines = [], []
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "results.json")
        old = os.environ.get(RC.RESULTS_ENV)
        os.environ[RC.RESULTS_ENV] = p
        try:
            code = SL.run(mock(answers, seen), pins=pins, out=lines.append)
        finally:
            if old is None:
                os.environ.pop(RC.RESULTS_ENV, None)
            else:
                os.environ[RC.RESULTS_ENV] = old
        with open(p, encoding="utf-8") as f:
            res = json.load(f)
    st, why = RC.judge_cases(SL.planted(), res)
    return st, why, res, seen, lines, code


def main():
    reg = RC.load_calibration(os.path.join(REPO, RC.CALIBRATION_REL))
    row = reg["families"].get(SL.FAMILY) or {}
    check("the scene_look_judge_brief row runs scene_look_calibration.py as its model_check",
          row.get("model_check") == ["python3", "src/RimMandrake/rimflow/scene_look_calibration.py", "run"],
          row.get("model_check"))
    check("the row plants the brim-pit pair both ways, as the module does",
          sorted((c["id"], c["expect"]) for c in row.get("planted") or []) == sorted(
              (c["id"], c["expect"]) for c in SL.planted())
          and {c["expect"] for c in SL.planted()} == {"pass", "refuse"}, row.get("planted"))
    check("the row's brief files include the judge's two prompts' homes",
          {"design/RimMandrake/scene_look_judge_brief.md", "src/RimMandrake/Utils/northstar_driver/judge_cli.py",
           "src/RimMandrake/Utils/modcheck/judge.py"} <= set(row.get("brief") or []), row.get("brief"))
    check("both crops are in the corpus on their pins", all(SL.image_problem(n) is None for n in SL.PINS),
          [SL.image_problem(n) for n in SL.PINS])

    st, why, res, seen, lines, code = status_of(dict(RIGHT))
    check("the planted pair answered right -> CALIBRATED", st == "CALIBRATED" and code == 0, (st, why))
    check("four calls: each crop through each pass exactly once",
          sorted((i, k) for i, k, _p in seen) == [("crop_pit3.png", 1), ("crop_pit3.png", 2), ("crop_pit6.png", 1),
                                                  ("crop_pit6.png", 2)], [s[:2] for s in seen])
    check("the success line counts the three planted cases, not the recorded one", why.startswith("3 planted"), why)
    check("pass 1 is judge_cli's OPEN_PROMPT, bar-blind",
          all(p == SL.JC.OPEN_PROMPT.format(image=os.path.join(SL.CORPUS, i)) and SL.BAR not in p
              for i, k, p in seen if k == 1), [p[:80] for i, k, p in seen if k == 1])
    check("pass 2 is modcheck/judge.py's statement prompt with the bar",
          all(p == SL.judge._PROMPT.format(image=os.path.join(SL.CORPUS, i), req_id=SL.BAR_ID,
                                           req_text="the north ladder is drawn in front of the pit wall, down to the water",
                                           framing=SL.judge._FRAMING[SL.judge.MUST]) for i, k, p in seen if k == 2),
          [p[:80] for i, k, p in seen if k == 2])
    check("the unplanted 1 m open look is recorded (ODD, on crop_pit3) and decides nothing",
          any(c["id"] == "one_m_pit_open_look" and c["got"] == "refuse" and c.get("look") == "ODD"
              and c.get("image") == "crop_pit3.png" for c in res["cases"]), res["cases"])

    st, why, *_ = status_of(but(("crop_pit6.png", 2), bar_answer("YES")))
    check("one wrong answer (the brim ladder bar YES) -> FAILED", st == "FAILED" and "brim_pit_ladder_bar" in why,
          (st, why))
    st, why, *_ = status_of(but(("crop_pit3.png", 2), bar_answer("NO")))
    check("the 1 m cell refused -> FAILED", st == "FAILED" and "one_m_pit_ladder_bar" in why, (st, why))
    st, why, *_ = status_of(but(("crop_pit6.png", 1), open_answer("EXPECTED")))
    check("pass 1 missing the brim fault (EXPECTED) -> FAILED", st == "FAILED", (st, why))

    st, why, res, _s, lines, code = status_of(but(("crop_pit6.png", 2), (False, "claude -p timed out")))
    check("a dead call -> not CALIBRATED: did not run, never a pass and never FAILED",
          st == "UNTESTED" and "brim_pit_ladder_bar" in why and code == 0, (st, why))
    check("the dead call is printed as did not run, with its cause",
          any("DID NOT RUN" in x and "timed out" in x for x in lines), lines)
    st, why, *_ = status_of(but(("crop_pit6.png", 2), env("API Error: 429 rate limit", True)))
    check("a throttled call did not run", st == "UNTESTED", (st, why))
    st, why, *_ = status_of(but(("crop_pit6.png", 2), env("the session ended", True)))
    check("an error envelope on pass 2 did not run (never UNJUDGEABLE)", st == "UNTESTED", (st, why))
    st, why, *_ = status_of(but(("crop_pit6.png", 1), env("the judge errored")))
    check("an unreadable pass-1 answer is malformed, not as planted -> FAILED", st == "FAILED", (st, why))
    st, why, *_ = status_of(but(("crop_pit6.png", 1), open_answer("COULD NOT SEE")))
    check("COULD NOT SEE on the brim cell -> unsure, not as planted -> FAILED", st == "FAILED", (st, why))
    st, why, *_ = status_of(but(("crop_pit3.png", 2), bar_answer("UNJUDGEABLE")))
    check("UNJUDGEABLE on the 1 m bar -> unsure -> FAILED", st == "FAILED", (st, why))

    st, why, res, seen, lines, _c = status_of(dict(RIGHT), pins=dict(SL.PINS, **{"crop_pit6.png": "0" * 64}))
    check("a crop off its pin: its cases did not run, no judge asked for them, UNTESTED",
          st == "UNTESTED" and not any(i == "crop_pit6.png" for i, _k, _p in seen), (st, why))
    with tempfile.TemporaryDirectory() as tmp:
        saved = SL.CORPUS
        SL.CORPUS = tmp
        try:
            shutil.copy(os.path.join(saved, "crop_pit3.png"), tmp)
            st, why, *_ = status_of(dict(RIGHT))
        finally:
            SL.CORPUS = saved
    check("a crop missing from the corpus: did not run, UNTESTED", st == "UNTESTED", (st, why))
    saved = SL.sha256

    def unreadable(path):
        raise PermissionError("case: no read")
    SL.sha256 = unreadable
    try:
        st, why, res, seen, lines, code = status_of(dict(RIGHT))
    except Exception as e:  # noqa: BLE001
        st, why, code = "raised", e, None
    finally:
        SL.sha256 = saved
    check("an unreadable crop: did not run (exit 0, UNTESTED), never a crash read as FAILED",
          st == "UNTESTED" and code == 0 and any("could not be read" in x for x in lines), (st, why))
    print("selftest_scene_look_calibration: %s" % ("PASS" if not FAILS else "FAIL (%d)" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
