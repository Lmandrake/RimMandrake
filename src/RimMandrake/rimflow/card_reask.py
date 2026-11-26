#!/usr/bin/env python3
"""card_reask.py — a card never asks him again a question he has already answered on a card (OWNER_CARDS_HARDEN_DECISION_RECEIPTS).

2026-11-19: three cards in three sessions asked him the same question ("which order: the Designer exam or the coverage
judge first?"). He answered at 00:34Z ("Retake only what changed"); at 03:14Z a card from another window said "you have
never ruled on it", and he answered: "Actually I have ruled on this multiple times. I'm not sure why you keep losing the
ruling." The answered card was in the card store (card_capture.py) the whole time; nothing read it before asking.

  match     the answered questions in the card store that a new question resembles: Jaccard similarity of the content
            words of header + question, at least THRESHOLD. A prior question he did not answer is not a ruling.
            Measured on the store 2026-11-25 (437 questions): 9 reach 0.25; both re-asks of the "Judge order" question
            are among them (0.27, 0.43); the other 7 are follow-ups that a `[revision: ...]` marker states.
  the gate  .claude/hooks/block_reasked_card.py (PreToolUse/AskUserQuestion) refuses a card with a question that
            matches, shows his earlier answer, and passes the question once it carries `[revision: <what changed>]`
            or `[owner-asked]` (he asked to be asked).
  census    the need: how many card answers in the last N days say he had already ruled. Exit 0 none, 1 some (each
            printed), 2 could not look (the store could not be read, or he answered no card in those days).

    python3 src/RimMandrake/rimflow/card_reask.py census [--days 14] [--store PATH]
    python3 src/RimMandrake/rimflow/card_reask.py match "<question text>" [--header H] [--store PATH]
"""
import argparse
import calendar
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

THRESHOLD = 0.25
REVISION = re.compile(r"\[revision:\s*([^\]]{12,})\]", re.I)   # 12+ characters: a reason, not a bare marker
OWNER_ASKED = re.compile(r"\[owner-asked\]", re.I)
UNANSWERED = re.compile(r"^\s*\[User did not answer", re.I)
# His words when a card re-asks a ruling. From the retired v3_vs_v2 rule (owner messages 10-05..10-24) plus the
# 2026-11-19 answer ("I have ruled on this multiple times ... you keep losing the ruling").
ALREADY_RULED = re.compile(
    r"already (ruled|answered|told|said|decided|asked|gave|gone over|covered)"
    r"|i('ve| have)? (just )?(already )?(ruled|told you|answered)"
    r"|i (said|ruled|told you) (this|that) (before|already)"
    r"|asked (and|&) answered|why (are you|am i) (asking|being asked) (me )?again"
    r"|keep losing the (ruling|decision|answer)|(second|third|fourth) time (this|you|i)", re.I)
STOP = set("this that with from have what which should would your there their they them when then than were been into "
           "only also does more most other each some such about after before because could every these those over "
           "under very will just like make made want need needs today".split())
STAMP = re.compile(r"\b(mon|tue|wed|thu|fri|sat|sun)\w*\s+\w+\s+\d+,?\s+\d+:\d+\s*[ap]m\s*p[sd]t\.?", re.I)


def words(header, question):
    t = STAMP.sub("", "%s %s" % (header or "", question or ""))
    return {w for w in re.findall(r"[a-z][a-z0-9'-]{3,}", t.lower()) if w not in STOP}


def jaccard(a, b):
    return len(a & b) / len(a | b) if (a or b) else 0.0


def store_path(arg=None):
    if arg:
        return arg
    import card_capture as CC
    return CC.store_path()


def read_store(path):
    """-> list of cards. Raises OSError when the store cannot be read: that is not 'no cards'."""
    out = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                c = json.loads(line)
            except ValueError:
                continue
            if isinstance(c, dict):
                out.append(c)
    return out


def answered_questions(cards):
    """(card, index, question) for every question he answered (a skipped question is not a ruling)."""
    for c in cards:
        for i, q in enumerate(c.get("questions") or []):
            if not isinstance(q, dict):
                continue
            ans = str(q.get("answer") or "").strip()
            if not ans or UNANSWERED.match(ans):
                continue
            yield c, i, q


def match(header, question, cards, threshold=THRESHOLD):
    """Prior answered questions that this one resembles, best first: [(score, card, index, question)]."""
    w = words(header, question)
    if len(w) < 3:
        return []
    hits = []
    for c, i, q in answered_questions(cards):
        s = jaccard(w, words(q.get("header"), q.get("question")))
        if s >= threshold:
            hits.append((s, c, i, q))
    hits.sort(key=lambda h: -h[0])
    return hits


def exempt(question_obj):
    text = " ".join(str(question_obj.get(k) or "") for k in ("header", "question"))
    return bool(REVISION.search(text) or OWNER_ASKED.search(text))


def pst(iso):
    try:
        t = calendar.timegm(time.strptime((iso or "")[:19], "%Y-%m-%dT%H:%M:%S"))
    except ValueError:
        return iso or "unknown time"
    return time.strftime("%a %b %d, %I:%M %p %Z", time.localtime(t))


def answered_within(cards, days, now=None):
    """How many questions he answered in the last `days`: 0 means the census saw no chance to see a re-ask."""
    now = now or time.time()
    n = 0
    for c, _i, _q in answered_questions(cards):
        try:
            t = calendar.timegm(time.strptime(str(c.get("answered") or "")[:19], "%Y-%m-%dT%H:%M:%S"))
        except ValueError:
            continue
        n += now - t <= days * 86400
    return n


def census(cards, days, now=None):
    """Answers in the last `days` whose text says he had already ruled: [(answered, header, his text)]."""
    now = now or time.time()
    out = []
    for c, _i, q in answered_questions(cards):
        try:
            t = calendar.timegm(time.strptime(str(c.get("answered") or "")[:19], "%Y-%m-%dT%H:%M:%S"))
        except ValueError:
            continue
        if now - t > days * 86400:
            continue
        said = " ".join(str(q.get(k) or "") for k in ("his_words", "answer"))
        if ALREADY_RULED.search(said):
            out.append((c.get("answered"), q.get("header"), (q.get("his_words") or q.get("answer") or "").strip()))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("census", help="card answers in the last N days that say he had already ruled")
    c.add_argument("--days", type=float, default=14)
    c.add_argument("--store")
    m = sub.add_parser("match", help="the answered questions a question resembles")
    m.add_argument("question")
    m.add_argument("--header", default="")
    m.add_argument("--store")
    a = ap.parse_args(argv)
    try:
        path = store_path(a.store)
        cards = read_store(path)
    except (OSError, RuntimeError) as e:
        print("COULD NOT LOOK: the card store could not be read (%s)" % e)
        return 2
    if a.cmd == "census":
        seen = answered_within(cards, a.days)
        if not seen:
            print("COULD NOT LOOK: no card in %s was answered in the last %g days (%d cards read): a stopped capture "
                  "hook and a quiet fortnight both read so" % (path, a.days, len(cards)))
            return 2
        hits = census(cards, a.days)
        for when, header, said in hits:
            print("RE-ASKED  %s  [%s]  he said: %s" % (pst(when), header, said))
        print("%d of %d card answers in the last %g days say he had already ruled (store %s)"
              % (len(hits), seen, a.days, path))
        return 1 if hits else 0
    for s, card, i, q in match(a.header, a.question, cards):
        print("%.2f  %s  [%s] %s -> %s" % (s, pst(card.get("answered")), q.get("header"), (q.get("question") or ""),
                                           q.get("answer")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
