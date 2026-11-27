#!/usr/bin/env python3
"""selftest_card_note.py: the promises of design/specs/2026-11-27-card-note/boundary.md (each t_ function is one
promise, by name). Offline: a fake card store, a temp ledger and temp items dir, an empty transcript dir. The real
ledger and the real card store are never touched (RIMFLOW_LEDGER and RM_CARDS_STORE are set for every child).
Written before card_note.py; seen failing on the base (the tool absent).

    python3 src/RimMandrake/rimflow/selftest_card_note.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CLI = os.path.join(HERE, "cli.py")
TOOL = os.path.join(HERE, "card_note.py")
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
ITEM = "RIMMANDRAKE_CARD_NOTE_PROBE_FIXTURE"
SENTENCE = "He picked the giant at body size 9, so Pyrelands needs bigger art."


def card(key, ago_s, *qas):
    """A store card answered ago_s seconds ago. qas: (question, header, picked label, its description)."""
    import card_capture as cc
    qs = [{"question": q, "header": h, "multiSelect": False,
           "options": [{"label": lab, "description": desc}, {"label": "Not this", "description": "the other way"}]}
          for q, h, lab, desc in qas]
    when = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() - ago_s))
    return cc.from_result(qs, {q: lab for q, h, lab, desc in qas}, answered=when, session="s", key=key)


def world(cards, item=True):
    tmp = tempfile.mkdtemp(prefix="cardnote_")
    store = os.path.join(tmp, "cards", "cards.jsonl")
    os.makedirs(os.path.dirname(store))
    with open(store, "w", encoding="utf-8") as f:
        for c in cards:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    env = {k: v for k, v in os.environ.items()
           if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID", "RM_ROLE_UNIT")}
    env.update(RIMFLOW_LEDGER=os.path.join(tmp, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(tmp, "items"),
               RIMFLOW_PROBE="no-reading", RIMFLOW_SEAT="BUILD", RM_CARDS_STORE=store,
               RM_CARDS_TRANSCRIPTS=os.path.join(tmp, "transcripts"), RM_FULLTEXT_DIR=os.path.join(tmp, "fulltext"))
    if item:
        p = subprocess.run([sys.executable, CLI, "file", ITEM, "--for", "BUILD", "--title", "t"], capture_output=True,
                           text=True, env=env, cwd=REPO, timeout=120)
        assert p.returncode == 0, "fixture item not filed: " + (p.stderr or p.stdout)[-300:]
    return tmp, env


def tool(env, *args):
    assert os.path.exists(TOOL), "no card_note tool: %s does not exist" % TOOL
    p = subprocess.run([sys.executable, TOOL] + list(args), capture_output=True, text=True, env=env, cwd=REPO,
                       timeout=120)
    return p.returncode, p.stdout, p.stderr


def notes(tmp):
    out = []
    for dp, _, fs in os.walk(tmp):
        if os.sep + "cards" in dp or "transcripts" in dp:
            continue
        for f in sorted(fs):
            if f.endswith(".jsonl"):
                with open(os.path.join(dp, f), encoding="utf-8") as fh:
                    out += [e for e in (json.loads(l) for l in fh if l.strip()) if e.get("event") == "note"]
    return out


def two_question_card(key="K2", ago=600):
    return card(key, ago, ("Which size should the giant have?", "Furnace size", "Body size 9", "Why: it reads as a giant."),
                ("Who draws the new art?", "Art", "Generate it", "Why: no hand art is on file."))


def t_note_carries_the_whole_card():
    tmp, env = world([two_question_card()])
    try:
        rc, out, err = tool(env, ITEM, SENTENCE)
        assert rc == 0, "rc %s: %s" % (rc, (err or out)[-300:])
        ns = notes(tmp)
        assert len(ns) == 1, "wanted ONE note, got %d" % len(ns)
        n = ns[0]
        assert n.get("id") == ITEM and n.get("seat") == "OWNER", n
        assert "ownerSaid" not in n and not n.get("ownerSaid"), "a card label must never be his words: %s" % n
        by = n.get("byCard") or ""
        assert "Body size 9" in by and "Generate it" in by, "byCard lacks a question of the card: %r" % by
        qs = (n.get("card") or {}).get("questions") or []
        assert len(qs) == 2, "the stamped card holds %d of 2 questions" % len(qs)
        assert any("it reads as a giant" in (o.get("description") or "") for q in qs for o in q.get("picked") or []), \
            "the picked option's description is not on the event"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_bare_call_takes_the_card_answered_last():
    old = card("OLD", 3000, ("Keep the old wall?", "Wall", "Keep it", "Why: cheap."))
    new = card("NEW", 100, ("Raise the ceiling?", "Ceiling", "Raise it", "Why: room."))
    mid = card("MID", 1500, ("Paint the door?", "Door", "Paint it", "Why: looks."))
    tmp, env = world([new, old, mid])          # the newest is NOT the last line: answered time decides
    try:
        rc, out, err = tool(env, ITEM, SENTENCE)
        assert rc == 0, "rc %s: %s" % (rc, (err or out)[-300:])
        n = notes(tmp)[0]
        assert "Raise it" in (n.get("byCard") or ""), "took the wrong card: %r" % n.get("byCard")
        assert "NEW" in ((n.get("card") or {}).get("key") or ""), n.get("card")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_no_card_in_the_store_is_refused_by_name():
    tmp, env = world([])
    try:
        rc, out, err = tool(env, ITEM, SENTENCE)
        assert rc != 0, "an empty store was accepted"
        assert env["RM_CARDS_STORE"] in err, "the refusal does not name the store: %s" % err[-300:]
        assert not notes(tmp), "a refused call wrote a note"
        # a --card that matches nothing names what it looked for
        shutil.rmtree(tmp, ignore_errors=True)
        tmp, env = world([two_question_card()])
        rc, out, err = tool(env, ITEM, SENTENCE, "--card", "zebra stampede")
        assert rc != 0 and "zebra stampede" in err and env["RM_CARDS_STORE"] in err, err[-300:]
        assert not notes(tmp), "a refused call wrote a note"
        # a store that cannot be read is a different answer from a store with no card
        env["RM_CARDS_STORE"] = os.path.join(tmp, "cards")          # a directory
        rc, out, err = tool(env, ITEM, SENTENCE)
        assert rc != 0 and "could not read" in err.lower() and env["RM_CARDS_STORE"] in err, err[-300:]
        assert not notes(tmp), "a refused call wrote a note"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_the_consequence_sentence_is_the_note_text():
    tmp, env = world([two_question_card()])
    try:
        rc, out, err = tool(env, ITEM, SENTENCE)
        assert rc == 0, (err or out)[-300:]
        n = notes(tmp)[0]
        assert n.get("text") == SENTENCE, "note text is %r" % n.get("text")
        # an empty sentence is refused: the note is the one thing the model owes
        rc, out, err = tool(env, ITEM, "  ")
        assert rc != 0 and len(notes(tmp)) == 1, "an empty consequence wrote a note"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_a_card_is_named_by_key_or_words_and_two_fits_are_refused():
    other = card("OTHER", 900, ("Which size should the wall have?", "Wall size", "Body size 4", "Why: small."))
    tmp, env = world([two_question_card(), other])
    try:
        rc, out, err = tool(env, ITEM, SENTENCE, "--card", "Art")          # names ONE question of the two-question card
        assert rc == 0, (err or out)[-300:]
        qs = (notes(tmp)[0].get("card") or {}).get("questions") or []
        assert len(qs) == 1 and "Generate it" in qs[0].get("answer", ""), qs
        rc, out, err = tool(env, ITEM, SENTENCE, "--card", "which size")      # fits two cards: refuse, list both keys
        assert rc != 0 and "K2" in err and "OTHER" in err and len(notes(tmp)) == 1, err[-300:]
        rc, out, err = tool(env, ITEM, SENTENCE, "--card", "OTHER")           # a key is exact
        assert rc == 0 and "Body size 4" in (notes(tmp)[-1].get("byCard") or ""), (err or out)[-300:]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_a_cli_past_its_deadline_reads_unmeasured():
    """A note write that does not end in time is UNMEASURED (it may stand written and not landed), never 'not written';
    the deadline is at least 10 x the measured need of a published ledger write (over 120 s seen 2026-11-27)."""
    import io
    import contextlib
    import card_note as CN
    assert CN.NOTE_DEADLINE_S >= 1800, "NOTE_DEADLINE_S %s is under 10 x a published note write" % CN.NOTE_DEADLINE_S
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        rc = CN.run_note([sys.executable, "-c", "import time; time.sleep(30)"], deadline_s=1)
    assert rc == 5, "a cli past its deadline exits %r, not 5 (could not look)" % rc
    assert "UNMEASURED" in err.getvalue() and "rimflow show" in err.getvalue(), err.getvalue()


def main():
    failed = 0
    TESTS = [t_note_carries_the_whole_card, t_bare_call_takes_the_card_answered_last,
             t_no_card_in_the_store_is_refused_by_name, t_the_consequence_sentence_is_the_note_text,
             t_a_card_is_named_by_key_or_words_and_two_fits_are_refused,
             t_a_cli_past_its_deadline_reads_unmeasured]
    for t in TESTS:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001 - a promise whose test cannot run is a FAIL, never a crash
            failed += 1
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, str(e)[:400]))
    print("FAILED %d of %d" % (failed, len(TESTS)) if failed else "ALL PASS (%d)" % len(TESTS))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
