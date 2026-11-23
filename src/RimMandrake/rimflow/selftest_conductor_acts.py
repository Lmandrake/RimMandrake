#!/usr/bin/env python3
"""Selftest of conductor_acts.py (owner 2026-11-19: only five acts stay his; the Conductor may do the rest, mindfully).
Page: design/specs/2026-11-19-conductor-acts/boundary.md; each promise is a test of its own name. Pure: no ledger."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import conductor_acts as CA  # noqa: E402

FAILS = []
WINDOW = {"AGENT_SEAT": "BENCH"}
HELPER = {"AGENT_SEAT": "BENCH", "RM_ROLE_UNIT": "rm-detached-bench-x-1"}
OTHER_SEAT = {"AGENT_SEAT": "OPERATIONS"}
WHY = "certify Pyrelands first touch: the spec reads clear and the Designer pass is complete"
MINDFUL_WHY = ("he left the game held for a staged look; lost: his staged look may be cut short; undo: re-stage the "
               "saved look when he sits down")


def check(ok, msg):
    print("%s %s" % ("ok  " if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


def t_five_acts_refused():
    for act in CA.KEPT:
        ok, txt = CA.check(act, WHY + " " + MINDFUL_WHY, env=WINDOW)
        check(not ok and "stays his" in txt, "the Conductor window is refused the kept act %r" % act)
        ok, _ = CA.is_conductor_event(_event(), act=act)
        check(not ok, "a recorded Conductor act never stands for the kept act %r" % act)
    check(len(CA.KEPT) == 5, "exactly five kept acts")


def t_only_the_window():
    for env, label in ((HELPER, "a launched helper"), (OTHER_SEAT, "another seat"), ({}, "no seat")):
        ok, _ = CA.check("first-touch certify", WHY, env=env)
        check(not ok, "%s is refused a Conductor act" % label)
        ok, _ = CA.cli_gate(WHY, env=env)
        check(not ok, "%s is refused --per-ruling %s at the cli" % (label, CA.RULING))
    ok, txt = CA.check("first-touch certify", WHY, env=WINDOW)
    check(ok, "the Conductor window may certify a first touch (%s)" % txt)
    sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
    import broadcast as B
    benv = {"RIMFLOW_PER_RULING": CA.RULING, "RIMFLOW_WHY": "the game is up after the reboot I ran myself"}
    check(B.conductor_broadcast(dict(WINDOW, **benv)), "broadcast: the Conductor window may message windows")
    check(not B.conductor_broadcast(dict(HELPER, **benv)), "broadcast: a launched helper stays stamp-only")
    check(not B.conductor_broadcast(dict(WINDOW, RIMFLOW_WHY=benv["RIMFLOW_WHY"])),
          "broadcast: the Conductor without the ruling stays stamp-only")


def t_why_states_act_and_reason():
    for why in ("", "   ", "ok", "certify it now"):
        ok, _ = CA.check("first-touch certify", why, env=WINDOW)
        check(not ok, "a why of %r is refused" % why)
        ok, _ = CA.cli_gate(why, env=WINDOW)
        check(not ok, "a why of %r is refused at the cli" % why)
    ok, _ = CA.check("first-touch certify", CA.tagged(WHY), env=WINDOW)
    check(ok, "an already tagged why is read by its own words")


def t_mindful_names_loss_and_undo():
    for act in CA.MINDFUL:
        ok, _ = CA.check(act, WHY, env=WINDOW)
        check(not ok, "%r is refused without lost: and undo:" % act)
        ok, _ = CA.check(act, "x y z w; lost: it; undo: redo", env=WINDOW)
        check(not ok, "%r is refused with one-word lost: and undo:" % act)
        ok, txt = CA.check(act, MINDFUL_WHY, env=WINDOW)
        check(ok, "%r passes with lost: and undo: (%s)" % (act, txt))
    ok, _ = CA.cli_gate("take the bridge hold he left, the sitting ended an hour ago", env=WINDOW)
    check(not ok, "the cli asks lost/undo of a why that names the bridge hold")
    ok, _ = CA.cli_gate("loosen the pyrelands heat bar per the blind judge", env=WINDOW)
    check(not ok, "the cli asks lost/undo of a why that names loosening a bar")
    ok, _ = CA.cli_gate(WHY, env=WINDOW)
    check(ok, "a plain act passes the cli with a four-word why")


def _event(**kw):
    ev = {"seat": "OWNER", "event": "note", "id": "X", "tsn": "1", "perRuling": CA.RULING,
          "why": CA.tagged(WHY, "first-touch certify"), "ranBy": "BENCH"}
    ev.update(kw)
    return ev


def t_recorded_as_conductor_not_his_words():
    t = CA.tagged(WHY, "first-touch certify")
    check(t.startswith("delegated: conductor act: first-touch certify: "), "the why is tagged with the act: %r" % t[:60])
    check(CA.tagged(t, "first-touch certify") == t, "tagging is idempotent")
    try:
        sys.path.insert(0, os.path.join(HERE, ".."))
        from contracts import blind
        check(blind.class_of(t) == "conductor act", "the digest classes it `conductor act` (got %r)" % blind.class_of(t))
    except Exception as e:  # noqa: BLE001
        check(False, "the digest class could not be read: %s" % e)


def t_event_check():
    ok, txt = CA.is_conductor_event(_event())
    check(ok, "a Conductor-window event is accepted (%s)" % txt)
    for kw, label in (({"perRuling": "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM"}, "another ruling"),
                      ({"role_unit": "rm-detached-bench-x"}, "a launched run"),
                      ({"ranBy": "OPERATIONS"}, "another seat's hands"), ({"ranBy": ""}, "no hands recorded"),
                      ({"why": WHY}, "an untagged why"), ({"ownerSaid": "yes"}, "his words on it")):
        ok, _ = CA.is_conductor_event(_event(**kw))
        check(not ok, "an event with %s is refused" % label)
    ok, _ = CA.is_conductor_event(_event(), act="loosen a bar")
    check(not ok, "a recorded loosening without lost/undo is refused")
    ok, _ = CA.is_conductor_event(_event(why=CA.tagged(MINDFUL_WHY)), act="loosen a bar")
    check(ok, "a recorded loosening with lost/undo is accepted")


class _R:
    def __init__(self, rc):
        self.returncode, self.stdout, self.stderr = rc, "", "boom"


def t_digest_note_written_first():
    seen = []
    CA.digest_note("ITEM", "re-freeze", "re-froze the dump", WHY, run=lambda argv, **k: seen.append(argv) or _R(0))
    argv = seen[0]
    check("--per-ruling" in argv and argv[argv.index("--per-ruling") + 1] == CA.RULING, "the note cites the ruling")
    check(argv[argv.index("--why") + 1].startswith(CA.WHY_PREFIX), "the note's why is tagged")
    check("--owner-said" not in argv and "--by-card" not in argv, "the note carries no words of his")
    try:
        CA.digest_note("ITEM", "re-freeze", "x", WHY, run=lambda argv, **k: _R(1))
        check(False, "a note that was not written raises")
    except RuntimeError:
        check(True, "a note that was not written raises")


def t_bridge_cut_only_mindful():
    import subprocess
    import tempfile
    T = tempfile.mkdtemp(prefix="conductor_acts_bridge_")
    base = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "RM_ROLE_UNIT",
                                                             "RM_DETACHED_UNIT", "RIMFLOW_RAN_BY")}
    base.update(RIMFLOW_LEDGER=os.path.join(T, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(T, "items"),
                RIMFLOW_PROBE="no-reading", RIMFLOW_DRIVER_LOCK="", RM_HOST="archmagi",
                RIMFLOW_BRIDGE_LOCK=os.path.join(T, "b.lock"), RIMFLOW_SCHEDULE=os.path.join(T, "none.json"),
                # its own wrap-up register: a release here once replayed the real register's live debts onto ArchBig
                # (RIMMANDRAKE_HOLD_WRAPUP_RESTORE_OFF_A_LIVE_OWNERS_DEBT)
                RM_WRAPUP_DIR=os.path.join(T, "wrapup"), RM_UNDER_SELFTEST="1")
    cli = os.path.join(HERE, "cli.py")

    def run(env, *a):
        e = dict(base, **env)
        r = subprocess.run([sys.executable, cli] + list(a), env=e, capture_output=True, text=True, timeout=120)
        return r.returncode, r.stdout + r.stderr
    win, helper = {"AGENT_SEAT": "BENCH"}, {"AGENT_SEAT": "BENCH", "RM_ROLE_UNIT": "rm-detached-bench-x-1"}
    for i in ("SOME_RULING_ITEM_FOR_TEST", CA.RULING):
        run(win, "file", i, "--title", "fixture", "--for", "BENCH", "--why", "fixture item")
    him = {"RIMFLOW_OWNER_TERMINAL": "1", "CLAUDECODE": ""}
    rc, out = run(him, "bridge", "take", "--seat", "OWNER", "--owner-said", "I am taking the bridge for my walk now",
                  "--for", "his walk")
    check(rc == 0, "fixture: he takes the bridge (%s)" % out.strip()[-80:])
    rc, out = run(helper, "bridge", "take", "--per-ruling", "SOME_RULING_ITEM_FOR_TEST", "--why",
                  "take it from him now please", "--for", "a test")
    check(rc != 0, "a helper's --per-ruling of another ruling no longer cuts his fresh hold")
    rc, out = run(win, "bridge", "release", "--per-ruling", "SOME_RULING_ITEM_FOR_TEST", "--why", "release his hold now")
    check(rc != 0, "the Conductor's --per-ruling of another ruling does not release his fresh hold")
    rc, out = run(win, "bridge", "take", "--per-ruling", CA.RULING, "--why",
                  "take the bridge hold he left, he walked away", "--for", "a test")
    check(rc != 0 and "lost:" in out, "the Conductor's cut without lost:/undo: is refused")
    rc, out = run(win, "bridge", "take", "--per-ruling", CA.RULING, "--why", MINDFUL_WHY, "--for", "fly the skarrin")
    check(rc != 0 and "flyer" in out, "the Conductor never cuts his hold for a flyer's flight")
    rc, out = run(win, "bridge", "take", "--per-ruling", CA.RULING, "--why", MINDFUL_WHY, "--for", "the Pyrelands visit")
    check(rc == 0, "the Conductor window's mindful cut takes his fresh hold (%s)" % out.strip()[-120:])
    rc, out = run(win, "bridge", "release", "--per-ruling", CA.RULING, "--why", "release the take for the visit, done")
    check(rc != 0, "his own take still counts: a plain release inside his 45 min is refused again")


def main():
    for t in (t_five_acts_refused, t_only_the_window, t_why_states_act_and_reason, t_mindful_names_loss_and_undo,
              t_recorded_as_conductor_not_his_words, t_event_check, t_bridge_cut_only_mindful,
              t_digest_note_written_first):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
