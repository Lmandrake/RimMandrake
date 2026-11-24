#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_TIE_LIFE_SIGN_TO_PROCESS_484_HAND_NOTES (rank 10 of one_page.md).

Contract: a new module src/RimMandrake/rimflow/run_alive.py
  decide(f, beat_s=1200, silence_s=7500) -> {"act": "renew"|"wait"|"lapse"|"blind", "why": str}
      f = {"unit_state": "active"|"inactive"|"unknown", "proc_alive": bool|None, "silent_s": s since the transcript grew
      or None (could not read), "child_running": bool|None, "since_beat_s": float|None (no beat yet)}.
      lapse: the process is gone, or it is silent past silence_s with no child command running (hung: the why says so).
      blind: any of the facts that decide it could not be read. A blind beat renews nothing and lapses nothing.
  line(unit, last_text, commits, now) -> "ALIVE: ..." from the run's own last message and its commits. last_text "" reads
      "no message yet (looked)"; None reads "could not look". It states no theory, no reading and no spend.
  renew(rec, append) -> "renewed" | "no lease" | "refused: <why>"     append(mod, writer, token) is called once when rec's
      env names RM_MODLEDGER_WRITER, RM_MODLEDGER_TOKEN and a mod; a raise is "refused", never "renewed".
  detached_helper.FOOTER no longer asks for a note every 20 minutes; it keeps the PROGRESS: note after an experiment.
  src/RimMandrake/Utils/systemd/rm-run-alive.timer drives it (operational: the close carries --live).
Expected when built: PASS 20/20."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _harness as H  # noqa: E402

RA = H.load("run_alive")


def act(**k):
    f = {"unit_state": "active", "proc_alive": True, "silent_s": 30.0, "child_running": False, "since_beat_s": 1300.0}
    f.update(k)
    return H.need(RA).decide(f)["act"]


H.check("alive and due: renew", lambda: act() == "renew")
H.check("alive, no beat yet: renew", lambda: act(since_beat_s=None) == "renew")
H.check("alive, not due: wait", lambda: act(since_beat_s=100.0) == "wait")
H.check("the process is gone: lapse", lambda: act(proc_alive=False) == "lapse")
H.check("the unit is gone: lapse", lambda: act(unit_state="inactive") == "lapse")
H.check("hung (silent, nothing running): lapse, and the why says hung", lambda: "hung" in H.need(RA).decide(
    {"unit_state": "active", "proc_alive": True, "silent_s": 9000.0, "child_running": False, "since_beat_s": 1300.0})
    ["why"].lower() and act(silent_s=9000.0) == "lapse")
H.check("a long wait (silent, its command runs): renew, not hung", lambda: act(silent_s=9000.0, child_running=True) == "renew")
H.check("unit unreadable: blind, never a lapse", lambda: act(unit_state="unknown") == "blind")
H.check("process unreadable: blind", lambda: act(proc_alive=None) == "blind")
H.check("transcript unreadable: blind, never alive", lambda: act(silent_s=None) == "blind")
H.check("silent and the child unreadable: blind, never hung", lambda: act(silent_s=9000.0, child_running=None) == "blind")


def ln(t, commits=("abc1234 fix the lock",)):
    return H.need(RA).line("rm-detached-x", t, list(commits), 1795492604)


H.check("the line starts ALIVE: and holds the last message and the commit", lambda: ln("reading the log").startswith("ALIVE:")
        and "reading the log" in ln("reading the log") and "abc1234" in ln("reading the log"))
H.check("empty and unreadable read differently", lambda: "no message yet (looked)" in ln("")
        and "could not look" in ln(None).lower() and "no message yet" not in ln(None))
H.check("the line states no spend", lambda: H.no_spend(ln("I used $21.6 of the $30 budget. Reading the log.")))
H.check("the line claims no theory and no reading", lambda: not any(
    w in ln("reading the log").lower() for w in ("theory:", "experiment:", "reading:", "next:")))
LEASE = {"env": {"RM_MODLEDGER_WRITER": "HOLDER.run-A", "RM_MODLEDGER_TOKEN": "4", "RM_CONTROL_MOD": "M"}}


def renewals():
    got = []
    ok = H.need(RA).renew(LEASE, lambda *a: got.append(a)) == "renewed" and len(got) == 1
    return ok and H.need(RA).renew({"env": {}}, lambda *a: got.append(a)) == "no lease" and len(got) == 1


H.check("a lease is renewed once; a run with no lease renews nothing", renewals)


def stale(*a):
    raise ValueError("stale token 4")


H.check("a refused renewal reads refused with its cause, never renewed", lambda: (
    lambda r: r.startswith("refused") and "stale token" in r)(H.need(RA).renew(LEASE, stale)))


def footer():
    import detached_helper as DH
    return "at least every 20 minutes" not in DH.FOOTER and "PROGRESS:" in DH.FOOTER


H.check("the footer asks for no 20-minute note and keeps the PROGRESS: note", footer)
H.check("the timer unit exists and the page names its promises", lambda: os.path.isfile(os.path.join(
    H.UTILS, "systemd", "rm-run-alive.timer")) and H.page(
    "design/specs/2026-11-23-run-alive/boundary.md", "a-dead-run-loses-its-lease", "a-hung-run-loses-its-lease",
    "a-blind-beat-changes-nothing"))
H.check("its selftest runs at ./publish", lambda: H.listed("src/RimMandrake/rimflow/selftest_run_alive.py"))
H.done(20)
