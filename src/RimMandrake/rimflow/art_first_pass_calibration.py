#!/usr/bin/env python3
"""art_first_pass_calibration.py - the art-eval first pass's planted cases
(RIMMANDRAKE_CALIBRATE_FIRST_PASS_AND_SCENE_LOOK_BRIEFS_READ_UNTESTED).

The `model_check` of the `art_eval_first_pass` row in infrastructure/state/judge_calibration.json. Page:
design/specs/2026-11-24-first-pass-calibration/boundary.md. Each regression row (infrastructure/state/art_eval/
regression.jsonl, less his `taste` rows) goes to one fresh Opus through production's own card, prompt, schema check and
policy (src/RimMandrake/Utils/art_eval: cards, runner, policy), as race.py judges a row: the picture alone, no
kept-art routing. The band is the answer: GOOD pass, REALLY_BAD refuse, WEAK "second look". It spends (one Opus call
per case): it runs only from `refusal_contract.py calibrate --model art_eval_first_pass`, never on a schedule.

    python3 src/RimMandrake/rimflow/art_first_pass_calibration.py run
"""
import json
import os
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "art_eval"))
import refusal_contract as RC  # noqa: E402
import cards as C  # noqa: E402
import policy as P  # noqa: E402
import runner as R  # noqa: E402

REGRESSION = os.path.join(REPO, "infrastructure", "state", "art_eval", "regression.jsonl")
EXPECT = {"ACCEPT": "pass", "NOT_ACCEPT": "refuse"}
GOT = {"GOOD": "pass", "REALLY_BAD": "refuse", "WEAK": "second look"}
PARALLEL = 5


def rows(path=None):
    with open(path or REGRESSION, encoding="utf-8") as f:
        out = [json.loads(l) for l in f if l.strip()]
    return [r for r in out if not str(r.get("taste") or "").strip()]


def spec_of(row):
    s = C.pilot_spec(row["pilot"]) if row.get("pilot") else C.load_spec(Path(REPO) / row["spec"])
    C.apply_brief(s)
    s.pop("depends_on", None)
    s["owner_kept"] = False        # the picture is judged, never the kept-art routing (race.spec_of)
    return s


def case_id(spec):
    return "first_pass_%s_%s" % (spec["subject"], spec.get("candidate") or "live")


def cases(path=None):
    return [{"id": case_id(s), "expect": EXPECT[r["expect"]], "spec": s}
            for r, s in ((r, spec_of(r)) for r in rows(path))]


def planted(path=None):
    """The registry row's `planted` list (refusal_contract.judge_cases)."""
    return [{"id": c["id"], "expect": c["expect"]} for c in cases(path)]


def ask_opus(prompt, card_dir):
    return R.call_claude(prompt, card_dir, "opus")   # production's own first-reviewer call


def judge(case, card_dir, ask):
    """-> (got, detail). got None = the case did not run (a picture is missing, or the judge call failed)."""
    spec = case["spec"]
    absent = [p for p, f in C.source_files(spec).items() if not Path(f).is_file()]
    if absent:
        return None, {"error": "missing picture(s): %s" % ", ".join(absent)}
    tpl = P.load_template(spec["template"])
    card = C.build_card(spec, card_dir)
    policy, facts = P.load_policy(), P.card_facts(card)
    pre = P.pre_route(card, tpl, None)
    if pre:
        return None, {"error": "production does not judge this card: %s" % pre}
    items = P.checklist_for(tpl, card.get("module", ""), facts)
    base = R.opus_prompt(card, tpl, items, policy, card_dir)
    reply, _raws, metas, err = R.ask_validated(
        lambda extra: ask(base + (("\n\n# Your previous reply was rejected\n\n" + extra) if extra else ""), card_dir),
        lambda r: P.validate_opus(r, items),
        "{err}. Return the JSON object exactly as specified, every checklist id answered.")
    if reply is None:
        if any(m.get("error") for m in metas):
            return None, {"error": "the judge could not run: %s" % err}
        return "malformed", {"error": err}
    band, d = P.opus_band(reply, items, facts, policy)
    return GOT[band], {"band": band, "overall": reply.get("overall"), "unreadable": d["incomplete"],
                       "blocking": [[f["code"], f.get("confidence")] for f in d["blocking"] + d["gross"]]}


def run(ask=ask_opus, path=None, out=print):
    cs = cases(path)
    with tempfile.TemporaryDirectory(prefix="rm-first-pass-cal-") as root:
        def one(c):
            try:
                return judge(c, Path(root) / c["id"], ask)
            except Exception as e:  # noqa: BLE001 - a staging error: the case did not run, never a verdict
                return None, {"error": "%s: %s" % (type(e).__name__, e)}
        with ThreadPoolExecutor(PARALLEL) as ex:
            got = list(ex.map(one, cs))
    results = [dict({"id": c["id"], "expect": c["expect"], "got": g}, **d) for c, (g, d) in zip(cs, got) if g]
    path_out = os.environ.get(RC.RESULTS_ENV)
    if path_out:
        with open(path_out, "w", encoding="utf-8") as f:
            json.dump({"cases": results}, f, indent=1)
    for c, (g, d) in zip(cs, got):
        out("%-34s expect %-6s %s" % (c["id"], c["expect"], "got %-11s band %s, model said %s, blocking %s" % (
            g, d.get("band"), d.get("overall"), d.get("blocking")) if g else "DID NOT RUN: %s" % d["error"]))
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["run"]:
        return run()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
