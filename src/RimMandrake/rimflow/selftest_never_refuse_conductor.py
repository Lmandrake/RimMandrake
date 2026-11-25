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
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "dispatcher")
os.environ["RM_DETACHED_POOL"] = os.path.join(TMP, "pool")
os.environ["RM_CONDUCTOR_LOG"] = os.path.join(TMP, "conductor.md")
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


class FakeSys:
    """A fake runner for detached_helper: origin/main is a list of event lines that `./publish` extends with the local
    shard's; systemd and git answer as a quiet host does. `calls` keeps every argv. Nothing real runs."""

    def __init__(self, origin_lines=(), shards=None):
        self.origin, self.shards, self.calls = list(origin_lines), dict(shards or {}), []

    def __call__(self, argv, **kw):
        self.calls.append(list(argv))
        out = ""
        if argv[:2] == ["git", "grep"]:
            needle = argv[argv.index("-e") + 1]
            hits = [ln for ln in self.origin if needle in ln]
            return subprocess.CompletedProcess(argv, 0 if hits else 1, "\n".join(hits), "")
        if argv and argv[0] == "./publish":
            for path in argv[3:]:
                self.origin += self.shards.get(path, [])
            out = "PUBLISHED 0123456789abcdef"
        if argv[:3] == ["systemctl", "--user", "show"]:
            out = "inactive"
        return subprocess.CompletedProcess(argv, 0, out, "")

    def published(self):
        return [c for c in self.calls if c and c[0] == "./publish"]


def _det_repo(name, item):
    import detached_helper as DH
    repo = os.path.join(TMP, name)
    ev = os.path.join(repo, *DH.EVENTS_REL.split("/"))
    os.makedirs(ev)
    line = json.dumps({"seat": "OWNER", "event": "file", "id": item, "title": "t", "for": "BENCH"})
    with open(os.path.join(ev, "OWNER.jsonl"), "w") as f:
        f.write(line + "\n")
    return repo, {DH.EVENTS_REL + "/OWNER.jsonl": [line]}


@contextlib.contextmanager
def _det_repo_bound(repo):
    import detached_helper as DH
    real = DH.REPO
    DH.REPO = repo
    try:
        yield DH
    finally:
        DH.REPO = real


def t_replay_launch_publishes_the_ledger_shard():
    item = "RIMMANDRAKE_PROBE_FILED_UNDER_A_RULING_NOT_PUBLISHED"
    repo, shards = _det_repo("launch_pub", item)
    clone = os.path.join(TMP, "launch_pub_clone")
    os.makedirs(clone)
    os.makedirs(os.path.join(clone, "src", "RimMandrake", "Utils"), exist_ok=True)   # a clone a unit can start in
    open(os.path.join(clone, "src", "RimMandrake", "Utils", "claude_bounded.sh"), "w").close()
    with _det_repo_bound(repo) as DH:
        fake = FakeSys(shards=shards)
        with as_caller(helper_env()):
            rc, text = DH.launch("BENCH", item, "Build.", "sonnet", None, 0, runner=fake, known={item}, clone=clone,
                                 skip_launch_checks="selftest")
        check(rc == 2 and "is not on origin/main" in text and not fake.published(),
              "launch replay: a helper's launch of an unpublished item is refused as before, nothing published", text)
        fake = FakeSys(shards=shards)
        with as_caller(conductor_env()), contextlib.redirect_stderr(io.StringIO()) as err:
            rc, text = DH.launch("BENCH", item, "Build.", "sonnet", None, 0, runner=fake, known={item}, clone=clone,
                                 skip_launch_checks="selftest")
        pub = fake.published()
        check(rc == 0 and pub and pub[0][3:] == [DH.EVENTS_REL + "/OWNER.jsonl", "--ledger"] and "publishes" in err.getvalue()
              and any(c[:1] == ["systemd-run"] for c in fake.calls),
              "launch replay: the Conductor's launch publishes the ledger shard itself, noted, and goes on", (rc, text, pub))


class FakeSysPublishRefuses(FakeSys):
    """`./publish` answers rc 1 "REFUSED: nothing to publish" (the shard reached origin by another publish, or by this one)
    and extends origin with the shard's lines only when `landed`; false = the item is truly absent."""

    def __init__(self, landed, **kw):
        super().__init__(**kw)
        self.landed = landed

    def __call__(self, argv, **kw):
        if argv and argv[0] == "./publish":
            self.calls.append(list(argv))
            if self.landed:
                for path in argv[3:]:
                    self.origin += self.shards.get(path, [])
            return subprocess.CompletedProcess(argv, 1, "", "REFUSED: nothing to publish: HEAD is already on origin/main\n")
        return super().__call__(argv, **kw)


def t_replay_launch_continues_when_the_item_is_already_published():
    item = "RIMMANDRAKE_PROBE_PUBLISH_FOUND_NOTHING_TO_LAND"
    repo, shards = _det_repo("launch_pub_landed", item)
    clone = os.path.join(TMP, "launch_pub_landed_clone")
    os.makedirs(os.path.join(clone, "src", "RimMandrake", "Utils"), exist_ok=True)
    open(os.path.join(clone, "src", "RimMandrake", "Utils", "claude_bounded.sh"), "w").close()
    with _det_repo_bound(repo) as DH:
        fake = FakeSysPublishRefuses(True, shards=shards)
        with as_caller(conductor_env()), contextlib.redirect_stderr(io.StringIO()) as err:
            rc, text = DH.launch("BENCH", item, "Build.", "sonnet", None, 0, runner=fake, known={item}, clone=clone,
                                 skip_launch_checks="selftest")
        check(rc == 0 and any(c[:1] == ["systemd-run"] for c in fake.calls) and "already" in err.getvalue(),
              "launch landed: the own publish says nothing to publish yet the item is on origin: the launch goes on, noted",
              (rc, text, err.getvalue()[-200:]))
        fake = FakeSysPublishRefuses(False, shards=shards)
        with as_caller(conductor_env()), contextlib.redirect_stderr(io.StringIO()):
            rc, text = DH.launch("BENCH", item, "Build.", "sonnet", None, 0, runner=fake, known={item}, clone=clone,
                                 skip_launch_checks="selftest")
        check(rc == 2 and "nothing to publish" in text and not any(c[:1] == ["systemd-run"] for c in fake.calls),
              "launch landed: an item truly absent still refuses, with the publish's own reason", text)


def t_replay_resume_takes_a_fresh_clone_and_restores_the_bundle():
    import detached_helper as DH
    item = "RIMMANDRAKE_PROBE_RESUME_AFTER_A_KEPT_CLONE"
    session = "0f1e2d3c-4b5a-6978-8796-a5b4c3d2e1f0"
    pool = os.environ["RM_DETACHED_POOL"]
    old = os.path.join(pool, "clones", item + ".det")
    os.makedirs(os.path.join(old, ".git"))
    bundle = os.path.join(TMP, "bundle_of_the_first_run")
    os.makedirs(bundle)
    projects = os.path.join(TMP, "projects")
    os.makedirs(os.path.join(projects, "-some-old-clone"))
    with open(os.path.join(projects, "-some-old-clone", session + ".jsonl"), "w") as f:
        f.write('{"type":"user"}\n')
    DH.write_record({"unit": "rm-detached-bench-probe-resume-first", "seat": "BENCH", "item": item, "clone": old,
                     "clone_how": "made " + old, "status": "finished", "at": time.time() - 600, "budget_usd": 0.0,
                     "session": session, "bundle": bundle, "return_steps": ["bundle failed: kept"]})
    made, restored = [], []

    def fake_take(item_, runner=None, name=None, **_kw):
        dest = os.path.join(pool, "clones", name or item_ + ".det")
        os.makedirs(os.path.join(dest, ".git"), exist_ok=True)
        made.append(dest)
        return dest, "made " + dest

    real_take, real_restore = DH.take_clone, getattr(DH, "restore_session_bundle", None)
    DH.take_clone = fake_take
    if real_restore:        # (absent on the base: the replay then shows the base's own refusal)
        DH.restore_session_bundle = lambda i, s, c, restorer=None, root=None: real_restore(
            i, s, c, restorer=lambda it, b, cl: restored.append((b, cl)) or [], root=root)
    try:
        fake = FakeSys(origin_lines=[json.dumps({"event": "file", "id": item})])
        with as_caller(helper_env()):       # as the base did: refused on the held clone (helpers too gain the repair)
            rc, text = DH.launch("BENCH", item, "Carry on.", "sonnet", None, 0, runner=fake, known={item},
                                 resume_session=session, projects=projects, skip_launch_checks="selftest")
    finally:
        DH.take_clone = real_take
        if real_restore:
            DH.restore_session_bundle = real_restore
    fresh = made[0] if made else ""
    rec = {}
    for r in DH.all_records():
        if r.get("resume_session") == session:
            rec = r
    check(rc == 0 and fresh and fresh != old and os.path.basename(fresh).startswith(item + ".r"),
          "resume replay: a resume on a clone a finished run holds takes a fresh pool clone, not that one", (rc, text))
    check(restored == [(bundle, fresh)] and "restored the work of run" in rec.get("clone_how", ""),
          "resume replay: the fresh clone takes the bundle from the run's finish record, and the record says so",
          (restored, rec.get("clone_how")))
    check(str(rec.get("resume_transcript") or "").startswith(projects) and os.path.exists(rec["resume_transcript"]),
          "resume replay: the transcript is carried to the fresh clone",
          rec.get("resume_transcript"))
    check(DH.owns_clone(dict(rec, clone=fresh)), "resume replay: the fresh clone is the run's own, so its return gives "
          "it back to the pool", rec.get("clone_how"))
    # a live run on the clone still refuses a resume (two runs, one clone)
    DH.write_record({"unit": "rm-detached-bench-probe-resume-live", "seat": "BENCH", "item": item, "clone": old,
                     "clone_how": "made " + old, "status": "running", "at": time.time(), "budget_usd": 0.0})
    check(DH.resume_fresh_clone(item, old, FakeSys()) is None, "resume replay: a clone a LIVE run holds gets no "
          "fresh twin (the resume waits or refuses as before)")


BEFORE = []


def t_real_ledger_unchanged():
    check(BEFORE and _digest_real_shards() == BEFORE[0], "the real ledger shards are unchanged by this test")


def main():
    BEFORE.append(_digest_real_shards())
    import control
    control.init(os.environ["RM_CONTROL_DB"])     # the test's own store (admission reads it on every launch)
    tests = [t_principal_is_the_conductor_window_or_the_owner, t_a_planted_form_gate_waives_for_the_conductor_only,
             t_replay_close_no_code_free_text, t_replay_long_names_file_spawn_namecheck, t_replay_note_positional_text,
             t_replay_pipe_undo_stop_and_on_unit, t_replay_fold_before_the_act_is_recorded,
             t_replay_launch_publishes_the_ledger_shard,
             t_replay_launch_continues_when_the_item_is_already_published, t_replay_resume_takes_a_fresh_clone_and_restores_the_bundle,
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
