#!/usr/bin/env python3
"""selftest_card_brief_spend: a by-card item's card text reaches a launched agent with no spend, token or account
sentence, and with every "needs X" (RIMMANDRAKE_STRIP_SPEND_TALK_FROM_CARD_BRIEFS_HAND_CUT, 2026-11-17: on the
Explosive Knockback rescue a helper cut two sentences by hand, and "keeps the accounts alive to Wednesday" still went
through; owner 2026-11-16: no launched agent is told its spend).

Hermetic: a temp repo whose ledger shard holds one event with a fixture card. Reads the three places card text enters
a brief: `card_capture.py show` (what the refusal tells the Conductor to paste), stop_resume.with_card_text (what a
resume or continuation adds), and detached_helper.card_refusal (which text the launch insists on).
"""
import contextlib
import io
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("RM_UNDER_SELFTEST", "1")
import card_capture  # noqa: E402
import detached_helper as DH  # noqa: E402
import stop_resume as SR  # noqa: E402

FAILS = []
ITEM = "RIMMANDRAKE_PROBE_CARD_SPEND_TALK_FIXTURE"
TALK = re.compile(r"weighted tokens|\d+\s*% left|accounts alive|\$\d", re.I)
CARD = {"answered": "2026-11-17T09:40:00Z", "questions": [{
    "question": "Rescue Knockback past its ceiling? The rescue costs about 400,000 weighted tokens. Steven is at 52% left.",
    "picked": [{"label": "Rescue it now", "description":
                "Why: cycle six is one fix from passing. It keeps the accounts alive to Wednesday. It needs a live "
                "visit, and it needs the throw art redrawn. About 300,000 weighted tokens, with lukas at 40% left."}],
    "others": ["Park it (saves ~200,000 weighted tokens; system at 61% left)", "Hand it to the owner"],
    "his_words": ""}]}


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (": " + str(detail)[:400] if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


REPO = tempfile.mkdtemp(prefix="card_brief_spend_")
EV_DIR = os.path.join(REPO, DH.EVENTS_REL)


def show(*extra):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        try:
            rc = card_capture.main(["show", ITEM, "--events", EV_DIR] + list(extra))
        except SystemExit as e:     # an option show does not know
            rc = e.code
    return rc, out.getvalue()


def t_show_gives_the_brief_text_without_spend():
    rc, shown = show()
    check("show-gives-the-brief-text-without-spend: no spend, token or account sentence",
          rc == 0 and not TALK.search(shown), shown)
    check("show-gives-the-brief-text-without-spend: the rest of the card stays", "cycle six is one fix from passing"
          in shown and "Hand it to the owner" in shown and "Rescue it now" in shown, shown)


def t_show_whole_keeps_the_whole_card():
    rc, shown = show("--whole")
    check("show-whole-keeps-the-whole-card", rc == 0 and "accounts alive" in shown and "52% left" in shown, shown)


def t_with_card_text_adds_no_spend_sentence():
    brief = SR.with_card_text(ITEM, "Rescue Explosive Knockback.\n", REPO)
    check("with-card-text-adds-no-spend-sentence", "What the card said" in brief and not TALK.search(brief), brief)


def t_every_needs_x_reaches_the_brief():
    _, shown = show()
    brief = SR.with_card_text(ITEM, "Rescue Explosive Knockback.\n", REPO)
    for where, text in (("show", shown), ("with_card_text", brief)):
        check("every-needs-x-reaches-the-brief: %s" % where, "needs a live visit" in text
              and "needs the throw art redrawn" in text, text)


def t_the_launch_asks_only_for_spend_free_text():
    brief = SR.with_card_text(ITEM, "Rescue Explosive Knockback.\n", REPO)
    check("the-launch-asks-only-for-spend-free-text: the spend-free brief launches",
          DH.card_refusal(ITEM, brief, events_dir=EV_DIR) is None, DH.card_refusal(ITEM, brief, events_dir=EV_DIR))
    why = DH.card_refusal(ITEM, "Rescue Explosive Knockback.", events_dir=EV_DIR)
    check("the-launch-asks-only-for-spend-free-text: a refusal quotes spend-free text",
          bool(why) and "needs a live visit" in why and not TALK.search(why), why)


def main():
    os.makedirs(EV_DIR)
    with open(os.path.join(EV_DIR, "OWNER.jsonl"), "w", encoding="utf-8") as f:
        f.write(json.dumps({"event": "file", "id": ITEM, "tsn": 1, "card": CARD}) + "\n")
    for t in (t_show_gives_the_brief_text_without_spend, t_show_whole_keeps_the_whole_card,
              t_with_card_text_adds_no_spend_sentence, t_every_needs_x_reaches_the_brief,
              t_the_launch_asks_only_for_spend_free_text):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            check(t.__name__ + " raised", False, "%s: %s" % (type(e).__name__, e))
    print("selftest_card_brief_spend: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
