#!/usr/bin/env python3
"""selftest_wake_words.py: the promises of design/specs/2026-11-23-wake-his-words/boundary.md, one test each.

All in a temp dir: a throwaway clone (ledger shards, stage records), a throwaway ~/.claude (transcripts) and a throwaway
dispatcher state. No window is read, killed or launched. Exit 0 all pass, 1 a promise broke.
"""
import contextlib
import io
import json
import os
import sys
import tempfile
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_wake_words_")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["CLAUDE_CONFIG_DIR"] = os.path.join(TMP, "claude")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import seat_restart as SR  # noqa: E402
import wake_words as WW  # noqa: E402

FAILS = []
T0 = 1795400000.0          # 2026-11-22 ~6:13 PM PST


def check(ok, what, got=None):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)
        if got is not None:
            print("   got: %s" % str(got)[:3000])


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def clone(name, owner=(), bench=(), mods=None):
    c = os.path.join(TMP, name)
    ev = os.path.join(c, WW.SHARDS)
    os.makedirs(ev, exist_ok=True)
    for shard, rows in (("OWNER", owner), ("BENCH", bench)):
        with open(os.path.join(ev, shard + ".jsonl"), "w") as f:
            for r in rows:
                f.write((r if isinstance(r, str) else json.dumps(r)) + "\n")
    for m, rec in (mods or {}).items():
        d = os.path.join(c, WW.CONCEPTS, m, "version")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "stage_record.json"), "w") as f:
            json.dump(rec, f)
    return c


def said(t, item, words, ev="note", card=None):
    e = {"seat": "OWNER", "event": ev, "id": item, "ts": iso(t), "tsn": int(t * 1e9)}
    if words:
        e["ownerSaid"] = words
    if card:
        e["byCard"] = card
    return e


def stage(mod, st, version="0.1.0", moves=()):
    return {"mod": mod, "version": version, "stage": st, "since": "2026-11-22T00:00:00-08:00", "moves": list(moves)}


def cfg_for(c):
    return {"kind": "conductor", "clone": c, "session_name": "CONDUCTOR"}


def u(t, text):
    return {"type": "user", "timestamp": iso(t), "uuid": "u%d" % int(t), "message": {"role": "user", "content": text},
            "origin": {"kind": "human"}, "promptSource": "typed"}


def transcript(c, sid, recs, raw_tail=""):
    p = SR.transcript_path(c, sid)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    head = [{"type": "custom-title", "customTitle": "CONDUCTOR", "sessionId": sid},
            {"type": "user", "timestamp": iso(recs[0]["_t"] if recs and "_t" in recs[0] else T0), "entrypoint": "cli",
             "isMeta": True, "message": {"role": "user", "content": "meta"}}]
    with open(p, "w") as f:
        for r in head + [dict((k, v) for k, v in r.items() if k != "_t") for r in recs]:
            f.write(json.dumps(r) + "\n")
        f.write(raw_tail)
    return p


def wake(c, rec=None, me=None, old_tx=None, holds=None, now=None):
    h = dict(holds or {})
    WW.read_holds = lambda: (h, None)       # the fixture's holds, for this Wake's sections too (never the live list)
    return WW.Wake("BENCH", cfg_for(c), rec or {}, me or {}, root=os.path.join(TMP, "state_" + os.path.basename(c)),
                   old_tx=old_tx, now=now)


def text(w):
    return "\n".join(w.first() + w.sections())


# ---- promises ---------------------------------------------------------------------------------------------------------

def t_pass_is_the_first_line():
    c = clone("pass", owner=[said(T0 + 600, "ITEM_GSS", "GSS walk full pass. Looks great!")],
              mods={"GimmeSomeSlack": stage("GimmeSomeSlack", "passed", "0.1.1", [
                  {"from": "his_walk", "to": "passed", "at": "2026-11-22T22:00:00-08:00", "by": "CONDUCTOR",
                   "why": "his walk passed"}]),
                    "Older": stage("Older", "passed", "0.1.0", [
                        {"from": "his_walk", "to": "passed", "at": "2026-11-01T10:00:00-08:00", "by": "CONDUCTOR",
                         "why": "old pass"}])})
    old = transcript(c, "old-pass", [u(T0, "hello")])
    w = wake(c, old_tx=old)
    first = w.first()
    check(first and first[0].startswith("== PASSED SINCE THE PREVIOUS WAKE: GimmeSomeSlack 0.1.1"),
          "pass-is-the-first-line: a pass since the previous wake is line 1", first)
    check(not any("Older" in x for x in first), "pass-is-the-first-line: a pass before the previous wake is not", first)
    c2 = clone("nopass", mods={"Pyrelands": stage("Pyrelands", "in_game")})
    w2 = wake(c2, old_tx=transcript(c2, "old-np", [u(T0, "hi")]))
    check(w2.first()[0].startswith("== PASSES SINCE THE PREVIOUS WAKE") and "looked: none" in w2.first()[0],
          "pass-is-the-first-line: no pass reads looked: none", w2.first())
    w3 = wake(c2)                                   # no stamp, no old transcript
    check("UNMEASURED" in w3.first()[0], "pass-is-the-first-line: no previous-wake time reads UNMEASURED", w3.first())


def t_his_walk_words_on_top():
    c = clone("walk", owner=[said(T0 + 600, "RIMMANDRAKE_STAGE_SLACK_LOOK", "GSS walk full pass. Looks great!"),
                             said(T0 - 3600 * 5, "RIMMANDRAKE_STAGE_SLACK_LOOK", "old words before the wake")],
              mods={"GimmeSomeSlack": stage("GimmeSomeSlack", "his_walk", "0.1.1")})
    w = wake(c, old_tx=transcript(c, "old-walk", [u(T0, "hi")]))
    top = "\n".join(w.first())
    check("GSS walk full pass. Looks great!" in top and "AT HIS WALK" in top,
          "his-walk-words-on-top: his words on a Stage 8 mod are at the top, word for word", top)
    check("old words before the wake" not in top, "his-walk-words-on-top: words before the previous wake are not", top)
    c2 = clone("walk2", owner=[said(T0 + 600, "ITEM_X", "Pyrelands looks fine")],
               mods={"Pyrelands": stage("Pyrelands", "in_game")})
    w2 = wake(c2, old_tx=transcript(c2, "old-walk2", [u(T0, "hi")]))
    check(not any("AT HIS WALK" in x for x in w2.first()), "his-walk-words-on-top: a mod not at Stage 8 is not raised",
          w2.first())


def t_every_word_since_the_wake():
    owner = [said(T0 - 7200, "ITEM_OLD", "BEFORE_THE_WAKE words"),
             said(T0 + 60, "ITEM_A", "first words, whole and long " + "x " * 400 + "END_OF_LONG"),
             said(T0 + 120, "ITEM_B", None, ev="answer", card="Which colour? → Blue (Recommended)"),
             said(T0 + 180, "ITEM_A", "third words"),
             '{"seat":"OWNER","event":"note","ownerSaid":"TORN']
    c = clone("words", owner=owner)
    w = wake(c, old_tx=transcript(c, "old-w", [u(T0, "hi")]))
    s = "\n".join(w._his_words())
    check("BEFORE_THE_WAKE" not in s, "every-word-since-the-wake: no event from before the previous wake", s)
    check("END_OF_LONG" in s and "Which colour? → Blue (Recommended)" in s and "third words" in s,
          "every-word-since-the-wake: owner-said and by-card printed whole", s[-600:])
    check(s.index("first words") < s.index("Which colour") < s.index("third words"),
          "every-word-since-the-wake: oldest first", s[:400])
    check("ITEM_A" in s and "PST" in s or "PDT" in s, "every-word-since-the-wake: item id and Pacific time on each", s)
    check("UNMEASURED line: OWNER.jsonl line 5" in s, "every-word-since-the-wake: a line that does not parse is named", s)
    many = [said(T0 + 10 + i, "ITEM_%d" % (i % 3), "word number %d" % i) for i in range(WW.GROUP_AT + 5)]
    c2 = clone("many", owner=many)
    s2 = "\n".join(wake(c2, old_tx=transcript(c2, "old-m", [u(T0, "hi")]))._his_words())
    check(all('"word number %d"' % i in s2 for i in range(WW.GROUP_AT + 5)) and "- ITEM_0 (" in s2,
          "every-word-since-the-wake: above %d it groups by item and prints every one" % WW.GROUP_AT, s2[:500])


def t_each_unheld_mod_with_his_newest_words():
    c = clone("mods", owner=[said(T0 - 86400, "RIMMANDRAKE_FIX_FLOW_WORKS_PIPE", "older flow words"),
                             said(T0 + 60, "RIMMANDRAKE_FIX_FLOW_WORKS_PIPE", "newest flow words"),
                             said(T0 + 90, "RIMMANDRAKE_GRAFFITI_IDEA", "held mod words")],
              mods={"FlowWorks": stage("FlowWorks", "in_game"), "Graffiti": stage("Graffiti", "blind_challenge"),
                    "Stillsand": stage("Stillsand", "designer")})
    w = wake(c, old_tx=transcript(c, "old-mods", [u(T0, "hi")]), holds={"Graffiti": {"mod": "Graffiti"}})
    s = "\n".join(w._mods_now())
    line = [x for x in s.splitlines() if x.startswith("- FlowWorks")]
    check(line and "Stage 6, in-game acceptance" in line[0] and "NEW since the previous wake" in line[0]
          and "newest flow words" in s and "older flow words" not in s,
          "each-unheld-mod-with-his-newest-words: stage and newest words, marked NEW", s)
    check("Graffiti" not in s, "each-unheld-mod-with-his-newest-words: a held mod is not listed", s)
    check("- Stillsand 0.1.0: Stage 1, the Designer" in s and "looked: none" in s,
          "each-unheld-mod-with-his-newest-words: a mod with no words of his says looked: none", s)


def t_homeless_message_printed_whole():
    c = clone("home", owner=[said(T0 + 70, "ITEM_GSS", "GSS walk full pass. Looks great!"),
                             said(T0 + 130, "ITEM_T", "Thin outline")])
    old = transcript(c, "old-home", [u(T0 - 7200, "BEFORE_WAKE unrecorded message"), u(T0, "hello"),
                                     u(T0 + 60, "GSS walk full pass. Looks great!"),
                                     u(T0 + 120, "Thin outlien"),
                                     u(T0 + 200, "Please move the SteveDesktop lane to run live games tonight, "
                                                 "this is an order he never saw recorded")])
    w = wake(c, old_tx=old)
    s = "\n".join(w._homeless())
    check("Please move the SteveDesktop lane to run live games tonight, this is an order he never saw recorded" in s,
          "homeless-message-printed-whole: an unrecorded message is printed whole", s)
    check("GSS walk full pass" not in s.split("\n", 1)[1] and "Thin outlien" not in s,
          "homeless-message-printed-whole: a recorded message (a typo fix included) is not printed", s)
    check("BEFORE_WAKE" not in s, "homeless-message-printed-whole: a message before the previous wake is not read", s)


def t_four_answers_apart():
    c = clone("four", owner=[said(T0 + 60, "ITEM", "words")])
    tx = transcript(c, "old-four", [u(T0, "hello")])
    w = wake(c, old_tx=tx)
    os.chmod(tx, 0)
    try:
        unreadable = os.geteuid() == 0 or open(tx).close()
    except OSError:
        unreadable = True
    s = "\n".join(w._homeless())
    os.chmod(tx, 0o600)
    check(unreadable and "UNMEASURED" in s and tx in s and "looked: none" not in s,
          "four-answers-apart: an unreadable transcript is UNMEASURED with its path, never none", s)
    c2 = clone("noshard")
    os.remove(os.path.join(c2, WW.SHARDS, "OWNER.jsonl"))
    w2 = wake(c2, old_tx=transcript(c2, "old-ns", [u(T0, "hi")]))
    s2 = "\n".join(w2._his_words())
    check("UNMEASURED: no OWNER shard" in s2, "four-answers-apart: a missing OWNER shard is UNMEASURED by name", s2)
    c3 = clone("zero", owner=[said(T0 - 9999, "ITEM", "old")])
    w3 = wake(c3, old_tx=transcript(c3, "old-z", [u(T0, "hello")]))
    s3 = "\n".join(w3._his_words())
    check("looked: none" in s3, "four-answers-apart: nothing since the wake is looked: none", s3)
    real = w3._mods_now
    w3._mods_now = lambda: 1 / 0
    try:
        s4 = "\n".join(w3.sections())
    finally:
        w3._mods_now = real
    check("FAILED (ZeroDivisionError" in s4 and "HIS WORDS SINCE" in s4 and "HIS TYPED MESSAGES" in s4,
          "four-answers-apart: a section that raises is FAILED and the others still print", s4)


def t_since_is_the_previous_wake():
    c = clone("since", owner=[said(T0 + 60, "ITEM", "a")])
    old = transcript(c, "old-s", [u(T0, "hello")])
    w = wake(c, old_tx=old, now=T0 + 1000)
    check(w.since == T0 and "start of the old window" in w.since_how,
          "since-is-the-previous-wake: with no stamp, the old window's first record", (w.since, w.since_how))
    check(w.stamp() is False, "since-is-the-previous-wake: a wake with no named session writes no stamp")
    me_tx = transcript(c, "w1", [u(T0 + 900, "hi"),
                                 {"type": "assistant", "timestamp": iso(T0 + 1100),
                                  "message": {"role": "assistant", "stop_reason": "end_turn",
                                              "content": [{"type": "text", "text": "done"}]}}])
    real = SR.transcript_for
    SR.transcript_for = lambda me, cfg: me_tx
    try:
        w1 = wake(c, old_tx=old, me={"sessionId": "w1"}, now=T0 + 1000)
        check(w1.stamp() is True, "since-is-the-previous-wake: a named window stamps")
        again = wake(c, me={"sessionId": "w1"}, now=T0 + 1500)
        check(again.since == T0, "since-is-the-previous-wake: a second run in the same window keeps its start",
              again.since)
        nxt = wake(c, me={"sessionId": "w2"}, now=T0 + 3000)
        ended = SR._turn_ended_since(me_tx, T0 + 1000)
        check(ended and nxt.since == T0 + 1000, "since-is-the-previous-wake: the next window reads from the stamp",
              (ended, nxt.since))
        SR.transcript_for = lambda me, cfg: os.path.join(TMP, "never_answered.jsonl")
        open(os.path.join(TMP, "never_answered.jsonl"), "w").write(json.dumps(u(T0 + 3001, "x")) + "\n")
        w2 = wake(c, me={"sessionId": "w2"}, now=T0 + 3000)
        w2.stamp()
        w3 = wake(c, me={"sessionId": "w3"}, now=T0 + 5000)
        check(w3.since == T0 + 1000, "since-is-the-previous-wake: a stamp whose window ended no turn carries back",
              w3.since)
    finally:
        SR.transcript_for = real


def t_sections_once_per_window():
    import argparse
    import doorbell
    c = clone("once", owner=[said(T0 + 60, "ITEM_ONCE", "ONCE_WORDS")])
    old = transcript(c, "old-once", [u(T0, "hello")])
    st = os.path.join(TMP, "state_once")
    os.makedirs(os.path.join(st, "restart"), exist_ok=True)
    SR._write_json(WW.stamp_path("BENCH", st), {"seat": "BENCH", "at": T0 + 500, "since": T0, "session": "w-once"})
    w = wake(c, old_tx=old, me={"sessionId": "w-once"})
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        SR._print_words(w)
    check(w.repeat and "printed in full by this window's wake" in out.getvalue() and "ONCE_WORDS" not in out.getvalue()
          and "seat_restart.py words --seat BENCH" in out.getvalue(),
          "sections-once-per-window: a second run in the same window prints one line with the command", out.getvalue())
    sch = {"seat_restart": {"enabled": True, "seats": {"BENCH": {"kind": "conductor"}}},
           "seats": {"BENCH": {"session_name": "CONDUCTOR", "clone": c}}}
    real = (SR._schedule, doorbell.claude_ancestor, SR.last_dead_window)
    SR._schedule = lambda: sch
    doorbell.claude_ancestor = lambda *a, **k: None
    SR.last_dead_window = lambda cfg, me=None: (old, "last words")
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            SR.cmd_last_reply(argparse.Namespace(seat="BENCH"))
            SR.cmd_words(argparse.Namespace(seat="BENCH"))
    finally:
        SR._schedule, doorbell.claude_ancestor, SR.last_dead_window = real
    got = out.getvalue()
    check(got.count("ONCE_WORDS") >= 2 and got.count("== HIS WORDS SINCE THE PREVIOUS WAKE") == 2,
          "sections-once-per-window: the fleet-launch wake (last-reply) and `words` print the sections", got[:1500])


TESTS = [t_pass_is_the_first_line, t_his_walk_words_on_top, t_every_word_since_the_wake,
         t_each_unheld_mod_with_his_newest_words, t_homeless_message_printed_whole, t_four_answers_apart,
         t_since_is_the_previous_wake, t_sections_once_per_window]


def main(argv=None):
    t_pass_is_the_first_line()
    t_his_walk_words_on_top()
    t_every_word_since_the_wake()
    t_each_unheld_mod_with_his_newest_words()
    t_homeless_message_printed_whole()
    t_four_answers_apart()
    t_since_is_the_previous_wake()
    t_sections_once_per_window()
    print("\n%s: %d failed" % ("FAIL" if FAILS else "ALL PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    with contextlib.redirect_stderr(io.StringIO()) if os.environ.get("QUIET") else contextlib.nullcontext():
        sys.exit(main())
