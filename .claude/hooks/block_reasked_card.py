#!/usr/bin/env python3
"""PreToolUse/AskUserQuestion hook - refuse a card that asks him again what he already answered on a card.

Item OWNER_CARDS_HARDEN_DECISION_RECEIPTS. 2026-11-19: "Judge order" was carded three times in three windows (the third
said "you have never ruled on it"; he: "I have ruled on this multiple times. I'm not sure why you keep losing the
ruling"), and "Rounds" 40 minutes after "Review loop" (he: "I already answered this"). Every answer was already in the
card store that card_capture.py writes. The store is the receipt; this hook reads it before he is asked.

Per question (the logic and the measured threshold: src/RimMandrake/rimflow/card_reask.py): an answered question
with Jaccard >= card_reask.THRESHOLD on header + question words is a re-ask. No model read: on 2026-11-25 a Sonnet read
of the 3 closest lower-scoring answered questions missed the Rounds re-ask and refused 1 of 30 sampled questions that
were right to ask (a card he had asked to be reworded), so it was removed. A re-ask in other words goes through
(design/specs/2026-11-25-card-reask-gate/boundary.md).
A question passes when it carries `[revision: <what changed since his answer>]` (12+ characters) or `[owner-asked]`.
The refusal shows each earlier question and his answer, so the asker acts on the ruling or states what is new.
Exit 2 refuses; anything unparseable exits 0.

    python3 .claude/hooks/selftest_block_reasked_card.py
"""
import json
import os
import sys

RIMFLOW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src", "RimMandrake", "rimflow")
sys.path.append(RIMFLOW)  # appended: shadows nothing
import card_reask as R  # noqa: E402


def questions(payload):
    qs = ((payload or {}).get("tool_input") or {}).get("questions")
    if not isinstance(qs, list) or not all(isinstance(q, dict) for q in qs):
        return []
    return qs


def judge(q, cards):
    """-> (how, (score, card, index, question)) for a re-ask, or None."""
    if R.exempt(q):
        return None
    hits = R.match(q.get("header"), q.get("question"), cards)
    return ("word match", hits[0]) if hits else None


def verdict(payload, cards):
    qs = questions(payload)
    if not qs or not cards:
        return []
    return [(q, r) for q, r in ((q, judge(q, cards)) for q in qs) if r]


def message(found):
    lines = ["Blocked: this card asks the owner again something he already answered on a card (the card store "
             "that card_capture.py writes; the match is card_reask.py)."]
    for q, (how, (s, card, i, pq)) in found:
        lines.append("  - your [%s] %s" % (q.get("header") or "", (q.get("question") or "")))
        lines.append("    matches (%s, %.2f) his answer of %s, card %s question %d:" % (how, s, R.pst(card.get("answered")),
                                                                                  card.get("key"), i))
        lines.append("      [%s] %s" % (pq.get("header") or "", (pq.get("question") or "")))
        lines.append("      HE ANSWERED: %s" % (pq.get("his_words") or pq.get("answer") or ""))
    lines.append("Path to pass: act on his answer (log it `--by-card \"<question> → <his answer>\"` or `--per-ruling`) and "
                 "drop the question. If something material changed since his answer, say what in the question text as "
                 "`[revision: <what changed since his answer of <date>>]` and ask again. If he asked to be asked, put "
                 "[owner-asked] in the question text. A wrong match costs one marker; the read can be wrong.")
    return "\n".join(lines)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict) or (payload.get("tool_name") or "AskUserQuestion") != "AskUserQuestion":
        return 0
    try:
        cards = R.read_store(R.store_path(os.environ.get("RM_CARDS_STORE") or None))
        found = verdict(payload, cards)
    except Exception as e:  # noqa: BLE001 - an unread store lets the card through, and says so
        sys.stderr.write("block_reasked_card: could not read the card store (%s); the card was not checked\n" % e)
        return 0
    if found:
        sys.stderr.write(message(found) + "\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
