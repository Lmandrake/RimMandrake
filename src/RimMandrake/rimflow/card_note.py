#!/usr/bin/env python3
"""card_note.py: one ledger note, by card, on a named item. The model gives the item and the consequence sentence;
this tool finds the card in the card store and runs `cli.py note <ITEM> --text <sentence> --by-card "<question → option>"`,
so cli and card_capture stamp the whole card (question, picked option and its description, his words, other options).

    card_note.py <ITEM> "<consequence sentence>" [--card <key or question words>] [--seat S] [--publish] [--dry-run]

A bare call takes the card answered last in the store. A refusal names the store and what was looked for. The note is
never --owner-said: a card label is our text. Boundary page: design/specs/2026-11-27-card-note/boundary.md.
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
CLI = os.path.join(HERE, "cli.py")


# budget: danger=a hung cli.py holds the helper with no end; a published ledger write ran past 120 s on 2026-11-27 (a claim
# budget: --publish, SteveDesktop) and a publish waited 581 s for a tree-check slot (script-candidates one_page.md); 1800 s
NOTE_DEADLINE_S = 1800


def run_note(cmd, deadline_s=None):
    """-> the exit of `cli.py note`. Past the deadline: 5, UNMEASURED. The note may stand written and not landed."""
    deadline_s = NOTE_DEADLINE_S if deadline_s is None else deadline_s
    try:
        return subprocess.run(cmd, timeout=deadline_s).returncode
    except subprocess.TimeoutExpired:
        item = cmd[3] if len(cmd) > 3 else "the item"
        sys.stderr.write("card_note: UNMEASURED: `cli.py note` did not end in %d s (NOTE_DEADLINE_S), so the note may "
                         "stand written and not landed. Look with: rimflow show %s\n" % (deadline_s, item))
        return 5


class Refused(Exception):
    pass


def read_store(path):
    """-> the cards in the store. A store that cannot be read raises Refused('could not read'); an empty one returns []."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except OSError as e:
        raise Refused("could not read the card store %s (%s: %s). Nothing was written." % (path, type(e).__name__, e))
    out = []
    for ln in lines:
        try:
            c = json.loads(ln)
        except ValueError:
            continue
        if isinstance(c, dict) and c.get("questions"):
            out.append(c)
    return out


def _words(card):
    import card_capture as cc
    parts = [card.get("key", "")]
    for q in card.get("questions") or []:
        parts += [q.get("question", ""), q.get("header", ""), q.get("answer", "")]
        parts += [o.get("label", "") for o in q.get("picked") or []]
    return cc.norm(" ".join(parts))


def _line(card):
    qs = card.get("questions") or []
    return "%s (answered %s): %s" % (card.get("key", "?"), card.get("answered", "?"),
                                     " | ".join((q.get("header") or q.get("question", ""))[:50] for q in qs))


def choose(cards, path, spec=""):
    """-> (card, the questions the note names). Refuses by name when nothing matches or the words fit several cards."""
    import card_capture as cc
    if not cards:
        raise Refused("no answered card in the store %s. Looked for: %s. Nothing was written."
                      % (path, "the card answered last" if not spec else repr(spec)))
    cards = sorted(cards, key=lambda c: c.get("answered") or "")
    if not spec.strip():
        return cards[-1], cards[-1]["questions"]
    s = cc.norm(spec)
    hits = [c for c in cards if c.get("key", "").casefold() == s or (len(s) >= 6 and c.get("key", "").casefold().startswith(s))]
    if not hits:
        want = [w for w in s.split() if len(w) >= 3]
        hits = [c for c in cards if want and all(w in _words(c) for w in want)]
    if not hits:
        raise Refused("no answered card in the store %s matches --card %r. Nothing was written." % (path, spec))
    if len(hits) > 1:
        raise Refused("--card %r fits %d cards in the store %s; name one by its key:\n  %s"
                      % (spec, len(hits), path, "\n  ".join(_line(c) for c in hits[-8:])))
    card = hits[0]
    named = [q for q in card["questions"] if all(w in cc.norm(q.get("question", "") + " " + q.get("header", ""))
                                                 for w in s.split() if len(w) >= 3)]
    if len(card["questions"]) > 1 and len(named) == 1:      # the words name one question of a many-question card
        return card, named
    return card, card["questions"]


def label(questions):
    return "; ".join("%s → %s" % (q.get("header") or q.get("question", "")[:80],
                                  ", ".join(o.get("label", "") for o in q.get("picked") or []) or q.get("answer", ""))
                     for q in questions)


def build_argv(item, sentence, by_card, seat="", publish=False):
    argv = [sys.executable, CLI, "note", item, "--text", sentence, "--by-card", by_card]
    if seat:
        argv += ["--seat", seat]
    if publish:
        argv.append("--publish")
    return argv


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("item", help="the ledger item the note is on")
    ap.add_argument("sentence", help="the consequence sentence: what the card's answer means for this item")
    ap.add_argument("--card", default="", help="a card key, or words of its question or answer (default: answered last)")
    ap.add_argument("--seat", default="", help="passed to rimflow note --seat")
    ap.add_argument("--publish", action="store_true", help="passed to rimflow note --publish")
    ap.add_argument("--dry-run", action="store_true", help="print the rimflow argv; write nothing")
    a = ap.parse_args(argv)
    try:
        if not a.sentence.strip():
            raise Refused("the consequence sentence is empty. Give what the card's answer means for %s." % a.item)
        import card_capture as cc
        try:
            path = cc.store_path()
        except RuntimeError as e:
            raise Refused("could not find the card store (%s). Nothing was written." % e)
        card, qs = choose(read_store(path), path, a.card)
        t = cc._epoch(card.get("answered"))
        if t is None or time.time() - t > cc.WINDOW_S:
            raise Refused("the card %s was answered %s: cli reads only cards answered in the last %d days, so the note "
                          "would not carry the whole card. Nothing was written."
                          % (card.get("key", "?"), card.get("answered") or "at an unknown time", cc.WINDOW_S // 86400))
    except Refused as e:
        sys.stderr.write("card_note: %s\n" % e)
        return 2
    cmd = build_argv(a.item, a.sentence.strip(), label(qs), a.seat, a.publish)
    if a.dry_run:
        print(" ".join(repr(x) if " " in x or "→" in x else x for x in cmd[1:]))
        return 0
    return run_note(cmd)

if __name__ == "__main__":
    sys.exit(main())
