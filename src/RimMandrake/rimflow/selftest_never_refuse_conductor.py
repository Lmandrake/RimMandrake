#!/usr/bin/env python3
"""selftest_never_refuse_conductor.py — the seven refusals the Conductor met on 2026-11-20/21, replayed, and the one
helper (principal.py) every gate of form asks first. Item RIMMANDRAKE_NEVER_REFUSE_THE_CONDUCTOR_SEVEN_REFUSALS_ONE_NIGHT.
Page: design/specs/2026-11-21-never-refuse-the-conductor/boundary.md; each promise there has a test of its own name here.

Every replay runs the real tool on a throwaway ledger, store or repo: the real `cli.py` as a subprocess under
RIMFLOW_LEDGER, control.py on its own RM_CONTROL_DB, maturation_hands on its own state dir, detached_helper with a fake
runner. Nothing reaches the real launcher, the real ledger, systemd or git's remote; the real ledger shards are checked
unchanged at the end. The Conductor is seat BENCH with no RM_ROLE_UNIT; a helper is the same seat WITH one.
"""
import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CLI = os.path.join(HERE, "cli.py")
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="selftest-never-refuse-")
os.environ["RM_CONTROL_DB"] = os.path.join(TMP, "control.db")
os.environ["RM_CONTROL_MODS"] = "Graffiti"
os.environ["RM_CONTROL_TICK_UNIT"] = ""
os.environ["RM_CONTROL_CONCEPTS"] = os.path.join(TMP, "concepts")
os.makedirs(os.environ["RM_CONTROL_CONCEPTS"])
REAL_EVENTS = os.path.join(REPO, "infrastructure", "state", "ledger", "events")
FAILS = []
HELPER_UNIT = "rm-detached-selftest-never-refuse-helper"
DROP = ("RM_ROLE_UNIT", "RM_DETACHED_UNIT", "RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "RIMFLOW_GITINDEX")


def check(cond, what, detail=""):
    print(("ok    " if cond else "FAIL  ") + what + ("" if cond else "  [%s]" % str(detail)[-400:]))
    if not cond:
        FAILS.append(what)


def conductor_env(**extra):
    env = {k: v for k, v in os.environ.items() if k not in DROP}
    env.update(RIMFLOW_SEAT="BENCH", AGENT_SEAT="BENCH")
    env.update(extra)
    return env


def helper_env(**extra):
    return conductor_env(RM_ROLE_UNIT=HELPER_UNIT, **extra)


@contextlib.contextmanager
def as_caller(env):
    """os.environ is `env` for the block (an in-process tool reads the caller from it)."""
    old = dict(os.environ)
    os.environ.clear()
    os.environ.update(env)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old)


class Ledger:
    """A throwaway ledger; `run` is the real cli.py on it."""

    def __init__(self, name):
        self.dir = os.path.join(TMP, name)
        os.makedirs(os.path.join(self.dir, "items", "closed"))

    def run(self, *args, env=None):
        env = dict(env or conductor_env(), RIMFLOW_LEDGER=os.path.join(self.dir, "events.jsonl"),
                   RIMFLOW_ITEMS=os.path.join(self.dir, "items"), RIMFLOW_PROBE="no-reading", PYTHONDONTWRITEBYTECODE="1")
        r = subprocess.run([sys.executable, CLI, *args], cwd=REPO, env=env, capture_output=True, text=True, timeout=180)
        return r.returncode, r.stdout + r.stderr

    def events(self):
        out = []
        d = os.path.join(self.dir, "events")
        for n in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            with open(os.path.join(d, n), encoding="utf-8") as f:
                out += [json.loads(x) for x in f if x.strip()]
        return out


def _digest_real_shards():
    h = hashlib.sha256()
    for n in sorted(os.listdir(REAL_EVENTS)):
        with open(os.path.join(REAL_EVENTS, n), "rb") as f:
            h.update(n.encode() + b"\0" + f.read())
    return h.hexdigest()


# ------------------------------------------------------------------ the one helper

def t_principal_is_the_conductor_window_or_the_owner():
    import principal as PR
    check(PR.who(conductor_env()) == "conductor", "principal: seat BENCH, no RM_ROLE_UNIT -> the Conductor")
    check(PR.who(conductor_env(RIMFLOW_SEAT="CONDUCTOR", AGENT_SEAT="CONDUCTOR")) == "conductor",
          "principal: seat typed CONDUCTOR -> the Conductor")
    check(PR.who(conductor_env(RIMFLOW_SEAT="OWNER", AGENT_SEAT="OWNER")) == "owner", "principal: seat OWNER -> the owner")
    check(PR.who(helper_env()) is None, "principal: any RM_ROLE_UNIT -> neither (a launched run gains nothing)")
    check(PR.who(conductor_env(RIMFLOW_SEAT="DISPATCHER", AGENT_SEAT="DISPATCHER")) is None,
          "principal: another seat -> neither")
    check(PR.who(helper_env(), seat="BENCH") is None, "principal: an explicit --seat BENCH in a launched run -> neither")
    import mod_owner_hold
    check(mod_owner_hold.conductor_window(conductor_env(AGENT_SEAT="CONDUCTOR", RIMFLOW_SEAT=""))[0],
          "principal: mod_owner_hold.conductor_window answers through it (CONDUCTOR typed is BENCH)")


def t_a_planted_form_gate_waives_for_the_conductor_only():
    """A new gate of form on a covered tool, planted here: it goes through principal.form, so it cannot refuse the
    Conductor (the act goes on, noted) and still refuses a helper run exactly as before."""
    import principal as PR

    def planted_gate(text, env):
        ev = {"event": "note", "text": text}
        if not text.endswith("."):          # the planted fault of form: a sentence must end with a full stop
            buf = io.StringIO()
            try:
                PR.form("text ends without a full stop", "REFUSED: end the text with a full stop", event=ev, env=env,
                        stream=buf)
            except SystemExit as e:
                return "refused %s" % e.code, ev
        return "done", ev

    with contextlib.redirect_stderr(io.StringIO()) as err:
        got, ev = planted_gate("no stop", conductor_env())
    check(got == "done" and ev.get("form_notes") == ["text ends without a full stop"],
          "planted gate: the Conductor's act goes on, the missing piece noted on the event", (got, ev))
    with contextlib.redirect_stderr(io.StringIO()) as err:
        got, ev = planted_gate("no stop", helper_env())
    check(got == "refused 2" and "end the text with a full stop" in err.getvalue() and "form_notes" not in ev,
          "planted gate: a helper run is refused the ordinary way", (got, err.getvalue()))
    with contextlib.redirect_stderr(io.StringIO()):
        got, _ = planted_gate("fine.", helper_env())
    check(got == "done", "planted gate: a well-formed act from a helper goes as before")
    check(PR.form("x", env=helper_env()) is None, "planted gate: ask-only form() answers None for a helper")


# ------------------------------------------------------------------ the seven replays

def t_replay_close_no_code_free_text():
    L = Ledger("close")
    iid = "RIMMANDRAKE_OWE_SANDBOX_THING_FOR_TEST"
    rc, out = L.run("file", iid, "--for", "BENCH", "--kind", "owed", "--title", "t", "--why", "sandbox")
    check(rc == 0, "close replay: an owed item is filed", out)
    said = "measured the clone count at 1:02 AM PST, it reads 3"
    rc, out = L.run("close", iid, "--no-code", said, "--why", "x", env=helper_env())
    check(rc == 2 and "holds none of the four shapes" in out, "close replay: a helper's free-text close is refused as "
          "before", out)
    rc, out = L.run("close", iid, "--no-code", said, "--why", "x")
    ev = [e for e in L.events() if e.get("event") == "close" and e.get("id") == iid]
    check(rc == 0 and ev and any("evidence form: free text" in n for n in ev[-1].get("form_notes", [])),
          "close replay: the Conductor's free-text close goes through, noted `evidence form: free text`", out)


def t_replay_long_names_file_spawn_namecheck():
    L = Ledger("names")
    long_ = "RIMMANDRAKE_A_VERY_LONG_NAME_THAT_HAS_FAR_TOO_MANY_WORDS_IN_IT_TO_PASS_THE_GRAMMAR_CHECK_AT_ALL"
    rc, out = L.run("file", long_, "--for", "BENCH", "--title", "t", "--why", "x")
    check(rc == 0 and "NAME NOTE" in out, "names replay: `file` takes a 95-char name with a NAME NOTE", out)
    rc, out = L.run("spawn", "--from", long_, "--for", "BENCH", "--name", long_ + "_TWO", "--title", "t", "--why", "x")
    check(rc == 0 and "NAME NOTE" in out, "names replay: `spawn` takes it with a NAME NOTE", out)
    rc, out = L.run("namecheck", long_ + "_THREE")
    check(rc == 0 and "REFUSED" in out and "waived for the Conductor" in out,
          "names replay: `namecheck` says what is wrong and exits 0 for the Conductor (a script's && goes on)", out)
    rc, out = L.run("namecheck", long_ + "_THREE", env=helper_env())
    check(rc == 1, "names replay: `namecheck` still exits 1 for a helper run", out)


def t_replay_note_positional_text():
    L = Ledger("note")
    iid = "RIMMANDRAKE_NOTE_SANDBOX_TWO_FOR_TEST"
    L.run("file", iid, "--for", "BENCH", "--title", "t", "--why", "x")
    rc, out = L.run("note", iid, "the text, given positionally", "--why", "x")
    rc2, out2 = L.run("note", iid, "--text", "the text, given by flag", "--why", "x", env=helper_env())
    texts = [e.get("text") for e in L.events() if e.get("event") == "note"]
    check(rc == 0 and "the text, given positionally" in texts, "note replay: a positional text is taken", out)
    check(rc2 == 0 and "the text, given by flag" in texts, "note replay: --text still works", out2)
    rc, out = L.run("note", iid, "--why", "x")
    check(rc == 2 and "needs its text" in out, "note replay: no text at all is still a usage error", out)


def _live_run(C, unit):
    """A started run in the test store, as a launched unit's would be (no systemd)."""
    C.admit({"family": "detached", "unit": unit, "mod": "Graffiti", "item": "RIMMANDRAKE_PROBE_X"})
    with C.txn() as c:
        c.execute("UPDATE runs SET state='started', started_at=? WHERE unit=?", (time.time(), unit))


def t_replay_pipe_undo_stop_and_on_unit():
    import control as C
    C.init(os.environ["RM_CONTROL_DB"])
    nokill = dict(killer=lambda us: [], reaper=lambda *a, **k: None, escalator=lambda *a, **k: "no timer in test")
    _live_run(C, "rm-probe-undo-1")
    r = C.stop("rm-probe-undo-1", "at_easy_spot", "easy-spot test", **nokill)
    act = r["act"]["id"]
    u = C.undo(act, "the Conductor withdraws its own stop")
    row = C._q("SELECT * FROM stops WHERE unit='rm-probe-undo-1'", one=True)
    check(u["ok"] and row["state"] == "withdrawn", "pipe replay: `undo` withdraws a stop order the run has not read", u)
    check(C.hook(unit="rm-probe-undo-1") == (0, ""), "pipe replay: the run's hook then delivers nothing")
    # read but not obeyed: withdrawn, and the run is told once
    _live_run(C, "rm-probe-undo-2")
    act2 = C.stop("rm-probe-undo-2", "at_easy_spot", "easy-spot test 2", **nokill)["act"]["id"]
    code, _ = C.hook(unit="rm-probe-undo-2")
    u2 = C.undo(act2, "withdraw after it was read")
    told = C.hook(unit="rm-probe-undo-2")
    check(code == 2 and u2["ok"] and told[0] == 2 and "WITHDRAWN" in told[1] and C.hook(unit="rm-probe-undo-2") == (0, ""),
          "pipe replay: a read order is withdrawn and the run is told so, once", (u2, told))
    # obeyed (its run ended): says so and names the resume command
    _live_run(C, "rm-probe-undo-3")
    act3 = C.stop("rm-probe-undo-3", "at_easy_spot", "easy-spot test 3", **nokill)["act"]["id"]
    with C.txn() as c:
        c.execute("UPDATE stops SET state='done' WHERE act=?", (act3,))
    u3 = C.undo(act3, "too late")
    check(not u3["ok"] and "already obeyed" in u3["why"] and "--resume" in u3["why"],
          "pipe replay: an obeyed stop says so and prints the resume command", u3)
    # his stop binds: only his word withdraws it
    _live_run(C, "rm-probe-undo-4")
    act4 = C.stop("rm-probe-undo-4", "at_easy_spot", "his stop", owner_said="stop it", **nokill)["act"]["id"]
    u4 = C.undo(act4, "the Conductor tries")
    check(not u4["ok"] and "his stop" in u4["why"], "pipe replay: his stop (--owner-said) is not withdrawn by another", u4)
    # `on unit:<u>` is a scope, and it withdraws the unit's pending order
    _live_run(C, "rm-probe-undo-5")
    C.stop("rm-probe-undo-5", "at_easy_spot", "easy-spot test 5", **nokill)
    try:
        sc = C.scope_of("unit:rm-probe-undo-5")
        r5 = C.switch(sc, False, "on again")
        st5 = C._q("SELECT state FROM stops WHERE unit='rm-probe-undo-5'", one=True)["state"]
        ok5 = sc == "unit:rm-probe-undo-5" and st5 == "withdrawn" and r5.get("withdrawn")
    except C.Refused as e:
        ok5, r5 = False, str(e)
    check(ok5, "pipe replay: `pipe on unit:<unit>` is accepted and withdraws the unit's stop order", r5)
    check(C.scope_of("rm-probe-undo-5.service") == "unit:rm-probe-undo-5", "pipe replay: a bare unit name is a scope too")


def t_replay_fold_before_the_act_is_recorded():
    import maturation_hands as MH
    os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "dispatcher")
    real = MH._sdir
    sdir = os.path.join(TMP, "hands")
    os.makedirs(sdir)
    MH._sdir = lambda: sdir
    try:
        fx = {"known": lambda: {"RIMMANDRAKE_PROBE_FOLLOW_UP_ITEM"}}
        rc, text = MH.fold(REPO, "clear-Graffiti-1795250000", item="RIMMANDRAKE_PROBE_FOLLOW_UP_ITEM", why="x", fx=fx)
        check(rc == 0 and "KEPT" in text, "fold replay: a fold of an act the tick has not recorded yet is kept", text)
        MH._append(MH.ACTS, MH._act("clear-Graffiti-1795250000", time.time(), "clear", "Graffiti", "cleared"))
        open_ = [a for a in MH.read_acts() if a["id"] not in MH.read_folds()]
        check(not open_, "fold replay: once the tick records it, the act reads folded", open_)
        rc, text = MH.fold(REPO, "clear-Graffiti-1795250001", item="RIMMANDRAKE_NOT_ON_THE_LEDGER", fx=fx)
        check(rc == 2 and "not an item on the ledger" in text, "fold replay: an item off the ledger is still refused",
              text)
    finally:
        MH._sdir = real


BEFORE = []


def t_real_ledger_unchanged():
    check(BEFORE and _digest_real_shards() == BEFORE[0], "the real ledger shards are unchanged by this test")


def main():
    BEFORE.append(_digest_real_shards())
    tests = [t_principal_is_the_conductor_window_or_the_owner, t_a_planted_form_gate_waives_for_the_conductor_only,
             t_replay_close_no_code_free_text, t_replay_long_names_file_spawn_namecheck, t_replay_note_positional_text,
             t_replay_pipe_undo_stop_and_on_unit, t_replay_fold_before_the_act_is_recorded,
             t_real_ledger_unchanged]
    only = sys.argv[1:]
    for t in tests:
        if only and t.__name__ not in only and t is not t_real_ledger_unchanged:
            continue
        try:
            t()
        except Exception as e:  # noqa: BLE001  a test that raises is a FAIL with its cause, never a crash of the rest
            check(False, "%s raised" % t.__name__, "%s: %s" % (type(e).__name__, e))
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
