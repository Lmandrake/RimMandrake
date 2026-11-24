#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_PASTE_ITEM_HISTORY_INTO_BRIEFS_1503_SHOWS_CUT (rank 6 of one_page.md).

Contract: a new module src/RimMandrake/rimflow/item_packet.py
  packet(item, facts, budget_chars=12000) -> {"text": str, "left_out": [str], "could_not_look": [str]}
      facts = {"state", "title", "prose", "notes": [{"ts", "seat", "text", "owner_said"?}], "runs": [{"ts", "result",
      "evidence"}], "linked": [{"id", "state", "title"}], "commits": [{"sha", "subject"}], "as_of": text}. A part that is
      None could not be read; [] was read and is empty. Notes are oldest first. Over the budget, the packet drops the
      oldest routine notes first and keeps: the last note, every note with owner words, every LEFT OPEN:, PROGRESS:, RULING
      and REFUSED note, and every fail run. left_out names each dropped part; the text says how many, and the command
      `rimflow show <item>`-equivalent that prints them.
  gather(item, clone) -> facts
  detached_helper.brief_message(brief, item, seat, clone, max_s=None) holds the packet's text (if the filled-commands
      item built brief_message first, use it).
Expected when built: PASS 16/16."""
import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _harness as H  # noqa: E402

IP = H.load("item_packet")
IT = "RIMMANDRAKE_SOME_ITEM_FOR_THIS_TEST_ONLY"


def n(text, i=0, **k):
    return dict({"ts": "2026-11-2%dT00:00:00Z" % i, "seat": "BENCH", "text": text}, **k)


def facts(**k):
    f = {"state": "doing", "title": "a title", "prose": "## spec\nbuild it", "notes": [n("first note"), n("last note", 3)],
         "runs": [], "linked": [], "commits": [{"sha": "abc1234", "subject": "a commit"}], "as_of": "8:00 PM PST 11-23"}
    f.update(k)
    return f


def pk(budget=12000, **k):
    return H.need(IP).packet(IT, facts(**k), budget)


BIG = [n("routine %03d " % i + "z" * 400) for i in range(100)]
H.check("the packet holds state, prose, notes and commits", lambda: all(
    s in pk()["text"] for s in ("doing", "build it", "first note", "last note", "abc1234")))
H.check("it says when it was read (a stale packet is seen)", lambda: "8:00 PM PST 11-23" in pk()["text"])
H.check("nothing dropped: left_out is empty", lambda: pk()["left_out"] == [])
H.check("over the budget: the last note is whole", lambda: "THE LAST " + "q" * 900 in pk(
    budget=8000, notes=BIG + [n("THE LAST " + "q" * 900, 3)])["text"])
for word in ("LEFT OPEN: finish the second half", "PROGRESS: theory: the lock | next: read it", "RULING: never do x",
             "REFUSED: the judge named one hole"):
    H.check("over the budget: the decisive note survives among 100 routine ones (%s)" % word.split(":")[0],
            lambda word=word: word in pk(budget=8000, notes=[n(word)] + BIG)["text"])
H.check("over the budget: a note with his words survives", lambda: "do it the first way" in pk(
    budget=8000, notes=[n("do it the first way", owner_said="do it the first way")] + BIG)["text"])
H.check("over the budget: it counts what it left out and names the command that shows it", lambda: (
    lambda r: len(r["left_out"]) > 0 and str(len(r["left_out"])) in r["text"] and "show " + IT in r["text"])(
        pk(budget=8000, notes=BIG)))
H.check("empty: no notes reads looked and found none", lambda: (
    lambda r: r["could_not_look"] == [] and "no notes" in r["text"].lower())(pk(notes=[])))
H.check("unreadable: notes None reads could not look, never no notes", lambda: (
    lambda r: any("notes" in c for c in r["could_not_look"]) and "could not look" in r["text"].lower()
    and "no notes" not in r["text"].lower())(pk(notes=None)))
H.check("no spend of an old note reaches the agent", lambda: H.no_spend(pk(
    notes=[n("The run used $21.6 of the $30 budget. The fix is in foo.py.")])["text"]))


def no_item():
    try:
        H.need(IP).packet("", facts())
    except ValueError:
        return True
    return False


H.check("no item is a ValueError", no_item)


def carried():
    import detached_helper as DH
    msg = DH.brief_message("Do the work.", IT, "BENCH", H.REPO)
    return "Do the work." in msg and IT in msg and "item_packet" in inspect.getsource(DH.brief_message) \
        and "brief_message(" in inspect.getsource(DH._launch_locked)


H.check("every detached launch carries the packet", carried)
H.check("the page names its promises and the selftest runs at ./publish", lambda: H.page(
    "design/specs/2026-11-23-item-packet/boundary.md", "decisive-notes-are-kept", "left-out-is-counted",
    "could-not-look-is-said") and H.listed("src/RimMandrake/rimflow/selftest_item_packet.py"))
H.done(16)
