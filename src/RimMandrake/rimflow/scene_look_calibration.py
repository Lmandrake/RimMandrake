#!/usr/bin/env python3
"""scene_look_calibration.py - the scene-look judge brief's planted cases (RIMMANDRAKE_SEED_SCENE_LOOK_CALIBRATION_BRIM_PIT_PAIR).

The `model_check` of the `scene_look_judge_brief` row in infrastructure/state/judge_calibration.json, on the pattern of
art_calibration.py. Each case puts one owner-verdicted crop to a fresh `claude -p` through the north-star frame judge's
own prompts and parsers (src/RimMandrake/Utils/northstar_driver/judge_cli.py: pass 1 OPEN_PROMPT and parse_open; pass 2
modcheck/judge.py's _PROMPT and _parse_verdict, as judge_cli asks them) and its own runner (claude_runner), and writes
one {id, expect, got} row per case to $RM_CALIBRATION_RESULTS.

The crops are the 2026-11-12 pit-submerge matrix (D:\\ClaudeWork\\rimmandrake\\conductor\\scene_judge_20261112\\RESULT.md),
copied into CORPUS and pinned by sha256. The owner, 2026-11-12: "Looks great at 1m water depth, but 2m water depth put
the northern ladder behind the pit wall art for some reason, silly looking. Southern ladder works correctly."
  brim_pit_open_look    crop_pit6.png (the brim cell, his fault), pass 1  -> ODD or WRONG = refuse     (planted: refuse)
  brim_pit_ladder_bar   crop_pit6.png, pass 2 with BAR                    -> NO = refuse               (planted: refuse)
  one_m_pit_ladder_bar  crop_pit3.png (the 1 m cell, he called correct), pass 2 with BAR -> YES = pass (planted: pass)
  one_m_pit_open_look   crop_pit3.png, pass 1: RECORDED, not planted (the 2026-11-12 naive judges raised a doubt on
                        this cell; a doubt there is no calibration failure)

got: pass 1 EXPECTED -> pass, ODD/WRONG -> refuse, COULD NOT SEE -> unsure, an unreadable answer -> malformed; pass 2
YES -> pass, NO -> refuse, UNJUDGEABLE (including an unparseable reply) -> unsure. A judge that could not run (the runner
failed, a throttle) leaves its case out of the results, so the brief stays UNTESTED ("did not run"), never a pass and
never FAILED. A crop missing or off its pin is the same: did not run. It spends (four `claude -p` calls): it runs only
from `refusal_contract.py calibrate --model scene_look_judge_brief`, never on a schedule.

    python3 src/RimMandrake/rimflow/scene_look_calibration.py run
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import refusal_contract as RC  # noqa: E402
from northstar_driver import judge_cli as JC  # noqa: E402

judge = JC.judge
FAMILY = "scene_look_judge_brief"
CORPUS = os.path.join(REPO, "src", "RimMandrake", "rimflow", "calibration_corpus", "scene_look")
MODEL = "opus"
TIMEOUT_S = 240
BAR_ID = "calibration.pit_north_ladder"
BAR = "the north ladder is drawn in front of the pit wall, down to the water"
PINS = {"crop_pit6.png": "90b3c7081db2b0c2ef813889dac263bcabf4bde88638874dd1c523d2ca6eb93a",
        "crop_pit3.png": "14aaee22639141d4dd63a7fe4619fe7e6bc3a3966b4c3ed85227310e1904b6bc"}
CASES = (
    {"id": "brim_pit_open_look", "image": "crop_pit6.png", "pass": 1, "expect": "refuse"},
    {"id": "brim_pit_ladder_bar", "image": "crop_pit6.png", "pass": 2, "expect": "refuse"},
    {"id": "one_m_pit_ladder_bar", "image": "crop_pit3.png", "pass": 2, "expect": "pass"},
    {"id": "one_m_pit_open_look", "image": "crop_pit3.png", "pass": 1, "expect": "recorded"},   # not planted
)


def planted():
    """The registry's `planted` list: every case with a pass/refuse expectation."""
    return [{"id": c["id"], "expect": c["expect"]} for c in CASES if c["expect"] in RC.EXPECTS]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def image_problem(name, pins=None):
    """None when the crop is in CORPUS on its pin, else why the case cannot run."""
    p = os.path.join(CORPUS, name)
    if not os.path.isfile(p):
        return "crop %s is not in %s" % (name, CORPUS)
    want = (pins or PINS).get(name)
    try:
        got = sha256(p)
    except OSError as e:     # unreadable: the case did not run, never a FAILED check
        return "crop %s could not be read: %s" % (name, e)
    return None if got == want else "crop %s is off its pin (sha256 %s, pinned %s)" % (name, got[:12], str(want)[:12])


def pass1_prompt(path):
    return JC.OPEN_PROMPT.format(image=path)


def pass2_prompt(path):
    return judge._PROMPT.format(image=path, req_id=BAR_ID, req_text=BAR, framing=judge._FRAMING[judge.MUST])


def grade(case, ok, raw):
    """-> (got, detail). got None = the judge could not run (the case did not run)."""
    if not ok or JC.is_throttle(ok, raw) or JC._error_envelope(raw):
        return None, {"error": "the judge could not run: %s" % str(raw)}
    if case["pass"] == 1:
        look, where, first, cause = JC.parse_open(raw)
        if look is None:
            if cause and cause.startswith("the judge could not run"):
                return None, {"error": cause}
            return "malformed", {"error": cause}
        got = {"EXPECTED": "pass", "ODD": "refuse", "WRONG": "refuse"}.get(look, "unsure")
        return got, {"look": look, "where": where, "first_noticed": first}
    verdict, why = judge._parse_verdict(raw)
    got = {judge.YES: "pass", judge.NO: "refuse"}.get(verdict, "unsure")
    return got, {"verdict": verdict, "why": str(why)}


def run(runner=None, pins=None, out=print):
    """Judge every case. -> exit code (0: every case was put to a judge or reported did not run; the registry's
    judge_cases decides the status from the rows)."""
    runner = runner or JC.claude_runner(MODEL, TIMEOUT_S)
    rows, missed = [], []
    for c in CASES:
        why = image_problem(c["image"], pins)
        if why:
            missed.append((c, why))
            continue
        try:
            ok, raw = runner(pass1_prompt if c["pass"] == 1 else pass2_prompt, os.path.join(CORPUS, c["image"]))
        except Exception as e:  # noqa: BLE001 - a staging or subprocess error: the judge could not run
            ok, raw = False, "%s: %s" % (type(e).__name__, e)
        got, det = grade(c, ok, raw)
        if got is None:
            missed.append((c, det["error"]))
            continue
        rows.append(dict({"id": c["id"], "expect": c["expect"], "got": got, "pass": c["pass"], "image": c["image"]},
                         **det))
    path = os.environ.get(RC.RESULTS_ENV)
    if path:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"cases": rows}, f, indent=1)
    for c, why in missed:
        out("%-22s expect %-8s DID NOT RUN: %s" % (c["id"], c["expect"], why))
    for r in rows:
        out("%-22s expect %-8s got %-9s %s" % (r["id"], r["expect"], r["got"],
                                                r.get("look") or r.get("verdict") or r.get("error") or ""))
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["run"]:
        return run()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
