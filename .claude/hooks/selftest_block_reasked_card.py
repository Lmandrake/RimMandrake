#!/usr/bin/env python3
"""Selftest for block_reasked_card.py and card_reask.py (OWNER_CARDS_HARDEN_DECISION_RECEIPTS).

The fixture (block_reasked_card_fixture.json) is real cards from the card store, verbatim: the 2026-11-19 Gate order
answer, the Judge order card three hours later that said "you have never ruled on it", and a Graffiti card asked twice
because the first was not answered. Each promise of design/specs/2026-11-25-card-reask-gate/boundary.md is one check of
the same name.

    python3 .claude/hooks/selftest_block_reasked_card.py
"""
import calendar
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "block_reasked_card.py")
CENSUS = os.path.join(HERE, "..", "..", "src", "RimMandrake", "rimflow", "card_reask.py")
FX = json.load(open(os.path.join(HERE, "block_reasked_card_fixture.json"), encoding="utf-8"))
TMP = tempfile.mkdtemp(prefix="selftest_reasked_card_")
FAILS = []


def check(name, ok, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  -- " + detail) if not ok and detail else ""))
    if not ok:
        FAILS.append(name)


def store(cards, name):
    p = os.path.join(TMP, name)
    with open(p, "w", encoding="utf-8") as f:
        for c in cards:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    return p


def card(*qs):
    return {"tool_name": "AskUserQuestion", "tool_input": {"questions": [
        dict(q, options=[{"label": "A", "description": "one"}, {"label": "B", "description": "two"}]) for q in qs]}}


def hook(payload, store_path):
    env = dict(os.environ, RM_CARDS_STORE=store_path)
    data = payload if isinstance(payload, str) else json.dumps(payload)
    r = subprocess.run([sys.executable, HOOK], input=data, capture_output=True, text=True, env=env, timeout=60)
    return r.returncode, r.stderr


def census(store_path, days=14):
    r = subprocess.run([sys.executable, CENSUS, "census", "--days", str(days), "--store", store_path],
                       capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


REASK = {k: FX["reask"][k] for k in ("header", "question")}
OTHER = {"header": "Smoke", "question": "On your walk you named the choking smoke weather. Which biomes should it come to?"}


def answered():
    return store([FX["prior_answered"]], "answered.jsonl")


def t_a_reask_of_an_answered_card_is_refused():
    """the real 03:14Z card, against the store as it stood before it"""
    rc, _err = hook(card(REASK), answered())
    check("a-reask-of-an-answered-card-is-refused", rc == 2, "exit %d" % rc)


def t_the_refusal_shows_his_answer_and_the_path_to_pass():
    _rc, err = hook(card(REASK), answered())
    check("the-refusal-shows-his-answer-and-the-path-to-pass",
          "HE ANSWERED: Retake only what changed" in err and "[revision:" in err and FX["prior_answered"]["key"] in err, err)


def t_a_revision_marker_passes():
    rev = dict(REASK, question=REASK["question"] + " [revision: the build found the coverage judge is skipped on a failed exam]")
    check("a-revision-marker-passes", hook(card(rev), answered())[0] == 0)


def t_a_bare_marker_is_refused():
    bare = dict(REASK, question=REASK["question"] + " [revision: new]")
    check("a-bare-marker-is-refused", hook(card(bare), answered())[0] == 2)


def t_owner_asked_passes():
    asked = dict(REASK, question="[owner-asked] " + REASK["question"])
    check("owner-asked-passes", hook(card(asked), answered())[0] == 0)


def t_one_reask_among_new_questions_refuses_the_card():
    rc, err = hook(card(OTHER, REASK), answered())
    check("one-reask-among-new-questions-refuses-the-card", rc == 2 and "[Smoke]" not in err, "exit %d" % rc)


def t_an_unrelated_question_passes():
    check("an-unrelated-question-passes", hook(card(OTHER), answered())[0] == 0)


def t_an_unanswered_card_is_not_a_ruling():
    """Graffiti 01:22Z (not answered), then 01:24Z (the same text)"""
    unans = store([FX["prior_unanswered"]], "unanswered.jsonl")
    fol = {k: FX["unanswered_followup"][k] for k in ("header", "question")}
    check("an-unanswered-card-is-not-a-ruling", hook(card(fol), unans)[0] == 0)


def t_an_unreadable_store_lets_the_card_through_and_says_so():
    rc, err = hook(card(REASK), os.path.join(TMP, "missing.jsonl"))
    check("an-unreadable-store-lets-the-card-through-and-says-so", rc == 0 and "could not read the card store" in err, err)


def t_an_unparseable_payload_passes():
    check("an-unparseable-payload-passes", hook("not json", answered())[0] == 0)


def _census_cards():
    now = time.time()
    ruled = dict(FX["prior_answered"], answered=iso(now - 3600), key="k-ruled",
                 questions=[dict(FX["reask"])])                  # his real words: "I have ruled on this multiple times"
    plain = dict(FX["prior_answered"], answered=iso(now - 3600), key="k-plain")
    old = dict(FX["prior_answered"], answered=iso(now - 30 * 86400), key="k-old", questions=[dict(FX["reask"])])
    return ruled, plain, old


def t_census_counts_an_already_ruled_answer():
    ruled, plain, _old = _census_cards()
    rc, out = census(store([ruled, plain], "census_hit.jsonl"))
    check("census-counts-an-already-ruled-answer", rc == 1 and "RE-ASKED" in out and "1 of 2" in out, "%d %s" % (rc, out))


def t_census_reads_zero_when_no_answer_says_so():
    _ruled, plain, _old = _census_cards()
    rc, out = census(store([plain], "census_clean.jsonl"))
    check("census-reads-zero-when-no-answer-says-so", rc == 0 and "0 of 1" in out, "%d %s" % (rc, out))


def t_census_could_not_look_with_no_answer_in_the_window():
    _ruled, _plain, old = _census_cards()
    rc, out = census(store([old], "census_old.jsonl"))
    check("census-could-not-look-with-no-answer-in-the-window", rc == 2 and "COULD NOT LOOK" in out, "%d %s" % (rc, out))


def t_census_could_not_look_on_an_unreadable_store():
    rc, out = census(os.path.join(TMP, "missing.jsonl"))
    check("census-could-not-look-on-an-unreadable-store", rc == 2 and "COULD NOT LOOK" in out, "%d %s" % (rc, out))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    only = set(argv[argv.index("--only") + 1:]) if "--only" in argv else None
    for t in (t_a_reask_of_an_answered_card_is_refused, t_the_refusal_shows_his_answer_and_the_path_to_pass,
              t_a_revision_marker_passes, t_a_bare_marker_is_refused, t_owner_asked_passes,
              t_one_reask_among_new_questions_refuses_the_card, t_an_unrelated_question_passes,
              t_an_unanswered_card_is_not_a_ruling, t_an_unreadable_store_lets_the_card_through_and_says_so,
              t_an_unparseable_payload_passes, t_census_counts_an_already_ruled_answer,
              t_census_reads_zero_when_no_answer_says_so, t_census_could_not_look_with_no_answer_in_the_window,
              t_census_could_not_look_on_an_unreadable_store):
        if only is not None and t.__name__ not in only:
            continue
        try:
            t()
        except Exception as e:      # noqa: BLE001
            check(t.__name__, False, "raised %s: %s" % (type(e).__name__, e))
    if FAILS:
        print("FAILED %d: %s" % (len(FAILS), "; ".join(FAILS)))
        return 1
    print("PASS selftest_block_reasked_card")
    return 0


if __name__ == "__main__":
    sys.exit(main())
