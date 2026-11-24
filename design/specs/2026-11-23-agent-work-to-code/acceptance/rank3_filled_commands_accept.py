#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_FILL_COMMANDS_INTO_BRIEFS_HELP_ASKED_2807_TIMES (rank 3 of one_page.md).

Contract: a new module src/RimMandrake/rimflow/brief_commands.py
  filled(item, seat, parsers=None) -> {"text": str, "could_not_look": [str]}
      One command line per verb, filled in with the item and the seat, made from the tool's own argparse parser at call
      time. `parsers` is {"rimflow": an ArgumentParser} for a test; None means cli.build_parser().
      Verbs at least: note, wait, close, verify, file, plus lines for maturation.py red-seen, lessons.py add, ./publish.
      A verb that the parser does not have, or a parser that cannot be read, is named in could_not_look AND in the text.
  detached_helper.brief_message(brief, item, seat, clone, max_s=None) -> the whole text the run is given; it holds
      filled()["text"]. _launch_locked builds its message with it (if the item-history item built it first, use it).
Expected when built: PASS 15/15."""
import argparse
import inspect
import os
import re
import shlex
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _harness as H  # noqa: E402

BC = H.load("brief_commands")
IT = "RIMMANDRAKE_SOME_ITEM_FOR_THIS_TEST_ONLY"
VERBS = ("note", "wait", "close", "verify", "file")


def text(**k):
    return H.need(BC).filled(IT, "BENCH", **k)["text"]


def subs(parser):
    return next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction)).choices


def line_of(verb, t):
    for ln in t.splitlines():
        m = re.search(r"python3 \S*cli\.py %s\b.*" % verb, ln)
        if m:
            return m.group(0).strip().strip("`")
    raise RuntimeError("no filled line for %s" % verb)


def parses(verb):
    import cli
    sp = subs(cli.build_parser())[verb]
    words = shlex.split(line_of(verb, text()))
    words = words[words.index(verb) + 1:]
    opts = [w for w in words if w.startswith("--")]
    bad = [o for o in opts if o not in sp._option_string_actions]
    owed = [a.option_strings[-1] for a in sp._actions if a.option_strings and a.required
            and not set(a.option_strings) & set(opts)]
    if bad or owed:
        raise RuntimeError("%s: not a flag %s; required and absent %s" % (verb, bad, owed))
    return IT in words and "--seat" in opts and "--publish" in opts


def fake(drop=None, extra=None):
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd")
    for v in VERBS + ("claim",):
        if v == drop:
            continue
        q = sp.add_parser(v)
        q.add_argument("id")
        for o in ("--seat", "--why"):
            q.add_argument(o)
        q.add_argument("--publish", action="store_true")
        if v == "close" and extra:
            q.add_argument(extra, required=True)
    return p


class Broken:
    def __getattr__(self, n):
        raise RuntimeError("parser cannot be read")


for v in VERBS:
    H.check("the %s line parses: every flag exists, every required flag is there, item and seat are filled in" % v,
            lambda v=v: parses(v))
H.check("publish, red-seen and lessons lines are there",
        lambda: all(s in text() for s in ("./publish -m", "maturation.py red-seen", "lessons.py add")))
H.check("stale: a new required flag in the parser shows in the text with no edit of the module",
        lambda: "--zz-new" in text(parsers={"rimflow": fake(extra="--zz-new")}))
H.check("missing: a verb the parser lost is named as could not look, not left out in silence", lambda: (
    lambda r: any("note" in c for c in r["could_not_look"]) and "could not look" in r["text"].lower())(
        H.need(BC).filled(IT, "BENCH", parsers={"rimflow": fake(drop="note")})))
H.check("unreadable: a parser that cannot be read is could not look, never an empty or a guessed text", lambda: (
    lambda r: bool(r["could_not_look"]) and "--help" in r["text"])(
        H.need(BC).filled(IT, "BENCH", parsers={"rimflow": Broken()})))


def empty():
    for bad in ("", None):
        try:
            H.need(BC).filled(bad, "BENCH")
        except ValueError:
            continue
        return False
    return True


H.check("empty: no item is a ValueError, never a line with an empty name", empty)
H.check("the text states no spend", lambda: H.no_spend(text()))
H.check("the text fits 12,000 characters (it stays in the context for every turn)", lambda: 0 < len(text()) <= 12000)


def carried():
    import detached_helper as DH
    msg = DH.brief_message("Do the work.", IT, "BENCH", "/tmp/clone")
    return "Do the work." in msg and text() in msg and "brief_message(" in inspect.getsource(DH._launch_locked)


H.check("every detached launch carries the text (brief_message, and _launch_locked calls it)", carried)
H.check("the page names its promises", lambda: H.page(
    "design/specs/2026-11-23-brief-commands/boundary.md", "lines-come-from-the-parser",
    "could-not-look-is-said", "no-spend-in-the-text"))
H.check("its selftest runs at ./publish", lambda: H.listed("src/RimMandrake/rimflow/selftest_brief_commands.py"))
H.done(15)
