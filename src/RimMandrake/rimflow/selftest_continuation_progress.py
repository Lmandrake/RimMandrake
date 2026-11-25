#!/usr/bin/env python3
"""selftest_continuation_progress: resume or start fresh, the token estimate, and the pilot's agent launch
(RIMMANDRAKE_STOP_RESUME_REWRITING_CONTEXT_A_MILLION_AT_ONCE, 2026-11-21: three resumes wrote their whole 252k-362k
context again in their first request, 0.72M-1.20M weighted_v2 each).
Page: design/specs/2026-11-21-live-sitting-context-burn/boundary.md; one check per promise, of the same name.
Offline: a temp state dir, fake transcripts, a fake launch. No claude, no systemd, no game.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_left_open_continue as B  # noqa: E402  its fixtures: temp state dir, make_run, fake_launch, transcripts
from selftest_left_open_continue import DH, LOC, T0, SID, PROJECTS, LAUNCHES, check  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PROG = "PROGRESS: theory: the raid path skips the moat | experiment: one raid, moat open | reading: 3 of 3 swam | next: close the moat"
BIG, SMALL = 300000, 100000


def pnote(text, ts, item):
    return {"event": "note", "id": item, "ts": DH.iso(ts), "text": text}


def cont(rec, notes, now, capped=False):
    """plan at finish with these item notes, then the step at `now`. -> (plan, result, the launch)."""
    B.clear_continuations()
    del LAUNCHES[:]
    got = {"state": "claimed", "notes": notes}
    p = LOC.plan(rec, got, {}, now=rec["ended"] + 60, gates=B.Gates().as_dict())
    r = DH.read_record(rec["unit"])
    r["continue_plan"] = p
    DH.write_record(r)
    res = LOC.run(rec["unit"], now=now, launch_fn=B.fake_launch, gates=B.Gates().as_dict(), reader=B.open_reader(),
                  projects=PROJECTS)
    return p, res, (LAUNCHES[-1] if LAUNCHES else {})


def run_with(ctx, left=True, **kw):
    """A finished run on an item of its own whose session holds `ctx` tokens (None: unreadable)."""
    B.plant_session(context=ctx)
    rec = B.resumable(session=SID, **kw)
    notes = [pnote(B.LEFT, T0 + 300, rec["item"])] if left else []
    return rec, notes


def t_a_small_session_resumes():
    for name, now in (("1 min after", T0 + 660), ("2 h after", T0 + 600 + 7200)):
        rec, notes = run_with(SMALL, left=False)
        notes.append(pnote(PROG, T0 + 200, rec["item"]))
        rec2 = dict(DH.read_record(rec["unit"]))
        _, res, L = cont(rec2, notes + [pnote(B.LEFT, T0 + 300, rec["item"])], now)
        check("small (%s): resumed" % name, L.get("resume_session") == SID, str((res, L.get("extra")))[:300])
    rec, notes = run_with(SMALL)
    _, res, L = cont(rec, [], T0 + 660)     # nothing said, no progress: owed kind, still a resume
    check("small, no progress record: resumed", L.get("resume_session") == SID, str((res, L.get("extra")))[:300])


def t_a_large_session_with_a_progress_record_starts_fresh():
    rec, notes = run_with(BIG)
    notes.append(pnote(PROG, T0 + 250, rec["item"]))
    _, res, L = cont(rec, notes, T0 + 660)
    ex, br = L.get("extra") or {}, L.get("brief") or ""
    check("large+progress: continued", res.get("act") == "continued", str(res))
    check("large+progress: no resume_session", L and not L.get("resume_session"), str(L.get("resume_session")))
    check("large+progress: brief carries the progress record whole", PROG in br and B.LEFT in br, br[:400])
    check("large+progress: progress comes oldest first", br.find(PROG) < br.find("> " + B.LEFT) or br.count(B.LEFT) > 1,
          br[:600])
    check("large+progress: brief carries the previous brief", "the previous run's brief" in br and
          "five-step split" in br, br[-300:])
    why = str(ex.get("continue_fresh_why"))
    check("large+progress: continue_how fresh, why names context and threshold",
          ex.get("continue_how") == "fresh" and "300000" in why.replace(",", "") and "150000" in why.replace(",", ""),
          str(ex))


def t_a_large_session_without_a_progress_record_resumes():
    rec, _ = run_with(BIG, left=False)
    B.clear_continuations()
    del LAUNCHES[:]
    # a lane hand-off continues with no LEFT OPEN note; no PROGRESS note either
    rec = B.resumable(session=SID, brief=B.LANE_BRIEF)
    got = {"state": "done", "notes": []}
    p = LOC.plan(rec, got, {B.LANE[0]: "done", B.LANE[1]: "claimed"}, now=T0 + 700, gates=B.Gates().as_dict())
    r = DH.read_record(rec["unit"]); r["continue_plan"] = p; DH.write_record(r)
    LOC.run(rec["unit"], now=T0 + 700, launch_fn=B.fake_launch, gates=B.Gates().as_dict(), reader=B.open_reader(),
            projects=PROJECTS)
    L = LAUNCHES[-1] if LAUNCHES else {}
    ex = L.get("extra") or {}
    check("large, no progress: resumed", L.get("resume_session") == SID, str(L.get("extra"))[:300])
    check("large, no progress: continue_resume_why names the missing record",
          "progress record" in str(ex.get("continue_resume_why")), str(ex))


def t_an_unmeasured_context_counts_as_large():
    rec, notes = run_with(None)
    _, _, L = cont(rec, notes, T0 + 660)
    check("unmeasured+progress (LEFT OPEN): fresh", L and not L.get("resume_session"), str(L.get("extra")))
    B.plant_session(context=None)
    B.clear_continuations()
    del LAUNCHES[:]
    rec = B.resumable(session=SID, brief=B.LANE_BRIEF)
    p = LOC.plan(rec, {"state": "done", "notes": []}, {B.LANE[0]: "done", B.LANE[1]: "claimed"}, now=T0 + 700,
                 gates=B.Gates().as_dict())
    r = DH.read_record(rec["unit"]); r["continue_plan"] = p; DH.write_record(r)
    LOC.run(rec["unit"], now=T0 + 700, launch_fn=B.fake_launch, gates=B.Gates().as_dict(), reader=B.open_reader(),
            projects=PROJECTS)
    L = LAUNCHES[-1] if LAUNCHES else {}
    check("unmeasured, no progress: resumed", L.get("resume_session") == SID, str(L.get("extra")))


def t_a_lost_session_starts_fresh():
    B.plant_session(context=BIG)
    rec = B.resumable(session="99999999-8888-7777-6666-555555555555")
    _, res, L = cont(rec, [pnote(PROG, T0 + 200, rec["item"])], T0 + 660)
    ex = L.get("extra") or {}
    check("lost: fresh", res.get("act") == "continued" and not L.get("resume_session"), str(res))
    check("lost: why names the transcript", "transcript" in str(ex.get("continue_fresh_why")), str(ex))
    check("lost: the progress record rides in the brief", PROG in (L.get("brief") or ""))
    # the vanished-transcript retry
    rec, notes = run_with(SMALL)
    calls = []

    def gone(seat, item, brief, model, max_s, budget, **kw):
        calls.append(kw.get("resume_session"))
        if kw.get("resume_session"):
            return 2, "REFUSED: session %s has no transcript under x; the holder starts from the packet" % SID
        return B.fake_launch(seat, item, brief, model, max_s, budget, **kw)
    B.clear_continuations()
    p = LOC.plan(rec, {"state": "claimed", "notes": notes}, {}, now=T0 + 700, gates=B.Gates().as_dict())
    r = DH.read_record(rec["unit"]); r["continue_plan"] = p; DH.write_record(r)
    res = LOC.run(rec["unit"], now=T0 + 660, launch_fn=gone, gates=B.Gates().as_dict(), reader=B.open_reader(),
                  projects=PROJECTS)
    check("lost: a refused resume is retried fresh once", calls == [SID, None] and res.get("act") == "continued",
          str((calls, res)))


def t_a_progress_record_is_a_progress_or_left_open_note_since_the_chain_began():
    item = "RIMMANDRAKE_PROGRESS_RECORD_CASE"
    notes = [pnote("PROGRESS: before the chain", T0 - 100, item), pnote(PROG, T0 + 10, item),
             pnote("progress: lower-case counts", T0 + 20, item), pnote("state: no prefix", T0 + 30, item),
             pnote("LEFT OPEN: the rest", T0 + 40, item), pnote("PROGRESS: another item", T0 + 50, "OTHER_ITEM_X"),
             {"event": "close", "id": item, "ts": DH.iso(T0 + 60), "text": "PROGRESS: not a note"}]
    got = LOC.progress_record(notes, [item], T0)
    texts = [n["text"] for n in got]
    check("progress: PROGRESS and LEFT OPEN notes since the start, oldest first",
          texts == [PROG, "progress: lower-case counts", "LEFT OPEN: the rest"], str(texts))
    root = B.make_run(item=item, at=T0 - 5000)
    later = B.make_run(item=item, at=T0, continue_root=root["unit"], continue_root_item=item)
    check("progress: the chain's first run sets the start", LOC.chain_start(later) == T0 - 5000,
          str(LOC.chain_start(later)))
    check("progress: the chain's first item counts too",
          [n["text"] for n in LOC.progress_record([pnote("PROGRESS: on the root", T0 + 1, "ROOT_ITEM_Y")],
                                                  ["LANE_TICKET_Z", "ROOT_ITEM_Y"], T0)] == ["PROGRESS: on the root"])


def t_a_capped_continuation_follows_the_same_rule():
    for ctx, prog, want_resume in ((BIG, True, False), (BIG, False, True), (SMALL, True, True)):
        B.plant_session(context=ctx)
        rec = B.resumable(session=SID, result="exit-code/claude-error (exited 1)", out=B.capped_out(),
                          continue_on_cap=1)
        notes = [pnote(PROG, T0 + 200, rec["item"])] if prog else []
        _, res, L = cont(rec, notes, T0 + 660, capped=True)
        name = "capped %dk %s" % (ctx // 1000, "with progress" if prog else "no progress")
        check(name + ": continued", res.get("act") == "continued", str(res))
        check(name + (": resumed" if want_resume else ": fresh"), bool(L.get("resume_session")) == want_resume,
              str(L.get("extra"))[:300])


class FakeLaunch(object):
    def __init__(self):
        self.calls = []

    def __call__(self, seat, item, brief, model, max_s, budget, **kw):
        self.calls.append(dict(kw, seat=seat, item=item, brief=brief, model=model, budget=budget))
        return 0, "DETACHED rm-detached-bench-fake-1"


def conductor_main(argv, notes):
    fake, saved = FakeLaunch(), (DH.launch, DH.read_item, LOC.CONDUCTOR_PROJECTS)
    DH.launch, DH.read_item, LOC.CONDUCTOR_PROJECTS = fake, (lambda clone, item: {"state": "claimed", "notes": notes}), PROJECTS
    try:
        import io
        import contextlib
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            try:
                rc = DH.main(argv)
            except SystemExit as e:     # argparse refused the argv
                rc = e.code
        return rc, out.getvalue(), fake.calls[-1] if fake.calls else {}
    finally:
        DH.launch, DH.read_item, LOC.CONDUCTOR_PROJECTS = saved


def t_the_conductors_resume_follows_the_same_rule():
    item, sid = "RIMMANDRAKE_CONDUCTOR_RESUME_CASE", "22222222-3333-4444-5555-666666666666"
    B.plant_session(sid=sid, context=BIG)
    B.make_run(item=item, at=T0, session=sid, brief="# The original pilot brief\n\nSit with the moat.")
    B.make_run(item=item, at=T0 + 900, session=sid, brief="Carry on (an earlier resume's short prompt).")
    base = ["launch", "--seat", "BENCH", "--item", item, "--brief", "Carry on.", "--budget-usd", "30", "--resume", sid]
    rc, out, L = conductor_main(base, [pnote(PROG, T0 + 100, item)])
    br = L.get("brief") or ""
    check("conductor large+progress: launched fresh", rc == 0 and L and not L.get("resume_session"), str(L)[:300])
    check("conductor large+progress: brief = given + progress + previous brief",
          br.startswith("Carry on.") and PROG in br and "Sit with the moat." in br, br[:500])
    check("conductor large+progress: first line says fresh and why", out.splitlines()[0].startswith("FRESH")
          and "150" in out.splitlines()[0], out[:300])
    check("conductor large+progress: record says fresh", (L.get("extra") or {}).get("continue_how") == "fresh",
          str(L.get("extra")))
    rc, out, L = conductor_main(base, [])
    check("conductor large, no progress: resumed", L.get("resume_session") == sid and L.get("brief") == "Carry on.",
          str(L)[:300])
    fake, saved = FakeLaunch(), (DH.launch, DH.read_item, LOC.CONDUCTOR_PROJECTS)
    DH.launch, DH.read_item, LOC.CONDUCTOR_PROJECTS = fake, (lambda clone, i: None), PROJECTS
    try:
        import io
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            DH.main(base)
    finally:
        DH.launch, DH.read_item, LOC.CONDUCTOR_PROJECTS = saved
    L = fake.calls[-1] if fake.calls else {}
    check("conductor large, notes unreadable: resumed, the cause said as UNMEASURED",
          L.get("resume_session") == sid and "UNMEASURED" in str((L.get("extra") or {}).get("continue_resume_why")),
          str(L)[:300])
    B.plant_session(sid=sid, context=SMALL)
    rc, out, L = conductor_main(base, [pnote(PROG, T0 + 100, item)])
    check("conductor small: resumed", L.get("resume_session") == sid, str(L)[:300])


def t_the_briefs_require_a_progress_note():
    import testpilot_route as TR
    role = open(os.path.join(REPO, "src", "RimMandrake", "rimflow", "roles", "builder.md"), encoding="utf-8").read()
    sit = TR.brief({"id": "X_ITEM_FOR_A_SIT", "why": "w"}, None, detached=True, agent=True)
    for name, text in (("FOOTER", DH.FOOTER), ("pilot sitting brief", sit), ("roles/builder.md", role)):
        ok = "PROGRESS:" in text and all(w in text.lower() for w in ("theory", "experiment", "reading", "next"))
        check("progress note asked in " + name, ok)


def t_the_token_estimate_is_the_measured_ratio():
    import modledger as ML
    check("tokens: 18 chars = 10", ML.tokens("a" * 18) == 10, str(ML.tokens("a" * 18)))
    check("tokens: 19 chars = 11 (rounded up)", ML.tokens("a" * 19) == 11, str(ML.tokens("a" * 19)))
    check("tokens: counts characters, not bytes", ML.tokens("é" * 18) == 10, str(ML.tokens("é" * 18)))
    cfg = ML.config()
    v = cfg.pop("chars_per_token", None)
    try:
        ML.tokens("abc")
        check("tokens: a config without chars_per_token fails by name", False, "no error")
    except Exception as e:  # noqa: BLE001
        check("tokens: a config without chars_per_token fails by name", "chars_per_token" in str(e), str(e))
    finally:
        if v is not None:
            cfg["chars_per_token"] = v


def t_the_packet_bound_counts_real_tokens():
    import modledger as ML
    ev = []
    for i in range(400):        # a ledger of closed findings, far past any budget
        ev.append({"kind": "finding.open", "subject": "finding:F%03d" % i, "writer": "JUDGE.r1", "mod": "FlowWorks",
                   "ts": "2026-11-21T00:00:%02dZ" % (i % 60), "id": "e%d" % i,
                   "body": {"class": "problem", "bars": ["b1"], "text": "x" * 200, "proposed_fix": "y" * 100,
                            "accept": "python3 t.py"}})
    try:
        text, info = ML.packet_from("FlowWorks", ev, budget=15000)
        check("packet: at budget 15000 it holds at most 27,000 characters (or says OVER BUDGET)",
              len(text) <= 27000 or info["over_budget"], "%d chars, %s" % (len(text), info))
    except Exception as e:  # noqa: BLE001
        check("packet: built", False, "%s: %s" % (type(e).__name__, e))
    real = [m for m in ML.mods_with_ledgers(REPO)]
    for m in real:
        t, i = ML.packet_from(m, ML.read(REPO, m), budget=15000)
        check("packet %s: at most 27,000 chars at 15000, or OVER BUDGET" % m, len(t) <= 27000 or i["over_budget"],
              "%d chars" % len(t))


def t_a_pilot_sitting_launches_with_its_agent():
    import testpilot_route as TR
    import maturation_autonomy as MA
    sit = TR.brief({"id": "X_ITEM_FOR_A_SIT", "why": "w"}, None, detached=True, agent=True)
    check("agent brief: says the role file is the system prompt", "system prompt" in sit, sit[:300])
    check("agent brief: asks for no Read of the agent file", "Read `.claude/agents/rm-testpilot.md` in full" not in sit)
    check("agent brief: names the one builder role and its setting", "src/RimMandrake/rimflow/roles/builder.md" in sit
          and "Sitting" in sit, sit[:300])
    check("tick pilot brief uses the agent text", "system prompt" in MA.pilot_brief(REPO, "X_ITEM", "FlowWorks", "w"))
    check("tick pilot env names the agent", MA.pilot_env({"RM_CONTROL_MOD": "FlowWorks"}).get(DH.AGENT_ENV)
          == "rm-testpilot", str(MA.pilot_env({})))
    rec = {"clone": REPO, "unit": "u1", "seat": "BENCH", "item": "X_ITEM", "model": "opus", "max_s": None,
           "budget_usd": 0.0, "out": "/tmp/o", "err": "/tmp/e", "state": B.STATE, "env": {DH.AGENT_ENV: "rm-testpilot"}}
    argv = DH.launch_argv(rec, "brief", "/usr/bin/claude")
    check("launch_argv passes --agent rm-testpilot", "--agent" in argv and argv[argv.index("--agent") + 1]
          == "rm-testpilot", " ".join(argv)[-400:])
    rec2 = dict(rec, env={})
    check("launch_argv without an agent passes none", "--agent" not in DH.launch_argv(rec2, "b", "/usr/bin/claude"))
    fake, saved = FakeLaunch(), DH.launch
    DH.launch = fake
    try:
        import io
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            DH.main(["launch", "--seat", "BENCH", "--item", "X_ITEM", "--brief", "b", "--budget-usd", "0", "--agent",
                     "rm-testpilot"])
    finally:
        DH.launch = saved
    check("launch --agent sets the env", fake.calls and (fake.calls[-1].get("env") or {}).get(DH.AGENT_ENV)
          == "rm-testpilot", str(fake.calls)[:300])


def t_a_missing_agent_file_is_repaired_not_refused():
    import tempfile
    clone = tempfile.mkdtemp(prefix="agentless_clone_")
    rec = {"env": {DH.AGENT_ENV: "rm-nosuchagent", "RM_CONTROL_MOD": "FlowWorks"}}
    msg = DH.agent_repair(rec, clone, "the brief")
    check("missing agent: dropped from the env", DH.AGENT_ENV not in rec["env"] and rec["env"].get("RM_CONTROL_MOD"),
          str(rec))
    check("missing agent: record carries agent_dropped with the cause", "rm-nosuchagent" in str(rec.get("agent_dropped")),
          str(rec))
    check("missing agent: brief names the role file", ".claude/agents/rm-nosuchagent.md" in msg, msg)
    rec = {"env": {DH.AGENT_ENV: "rm-testpilot"}}
    msg = DH.agent_repair(rec, REPO, "the brief")
    check("present agent: kept, brief unchanged", rec["env"].get(DH.AGENT_ENV) == "rm-testpilot" and msg == "the brief",
          str(rec))


def t_a_continuation_keeps_the_agent():
    rec, notes = run_with(SMALL, env={DH.AGENT_ENV: "rm-testpilot", "RM_CONTROL_MOD": "FlowWorks"})
    _, _, L = cont(rec, notes, T0 + 660)
    check("continuation carries RM_CLAUDE_AGENT", (L.get("env") or {}).get(DH.AGENT_ENV) == "rm-testpilot",
          str(L.get("env")))


def t_a_holder_resume_is_not_turned_fresh():
    item, sid = "RIMMANDRAKE_HOLDER_RESUME_CASE", "33333333-4444-5555-6666-777777777777"
    B.plant_session(sid=sid, context=BIG)
    B.make_run(item=item, at=T0, session=sid, brief="# Holder run")
    argv = ["launch", "--seat", "BENCH", "--item", item, "--brief", "You are the holder, resumed.", "--budget-usd",
            "30", "--resume", sid, "--planned-resume"]
    rc, out, L = conductor_main(argv, [pnote(PROG, T0 + 100, item)])
    check("holder (--planned-resume) large+progress: still resumed", L.get("resume_session") == sid and
          L.get("brief") == "You are the holder, resumed.", str(L)[:300])
    import maturation_autonomy as MA
    seen = {}

    def runner(a, **kw):
        seen["argv"] = a

        class R(object):
            returncode, stdout, stderr = 0, "DETACHED rm-detached-bench-x\n", ""
        return R()
    MA.launch_brief("X_ITEM", "brief", "opus", 5, runner=runner, session=sid)
    a = seen.get("argv") or []
    check("holder launch_brief passes --planned-resume with --resume", "--resume" in a and "--planned-resume" in a,
          str(a[-6:]))
    MA.launch_brief("X_ITEM", "brief", "opus", 5, runner=runner)
    check("a launch_brief without a session passes neither", "--planned-resume" not in (seen.get("argv") or []))


def main():
    for t in (t_a_small_session_resumes, t_a_large_session_with_a_progress_record_starts_fresh,
              t_a_large_session_without_a_progress_record_resumes, t_an_unmeasured_context_counts_as_large,
              t_a_lost_session_starts_fresh, t_a_progress_record_is_a_progress_or_left_open_note_since_the_chain_began,
              t_a_capped_continuation_follows_the_same_rule, t_the_conductors_resume_follows_the_same_rule,
              t_the_briefs_require_a_progress_note, t_the_token_estimate_is_the_measured_ratio,
              t_the_packet_bound_counts_real_tokens, t_a_pilot_sitting_launches_with_its_agent,
              t_a_missing_agent_file_is_repaired_not_refused, t_a_continuation_keeps_the_agent,
              t_a_holder_resume_is_not_turned_fresh):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(t.__name__ + " raised", False, "%s: %s" % (type(e).__name__, e))
    print("selftest_continuation_progress: %s (%d failed)" % ("FAIL" if B.FAILS else "PASS", len(B.FAILS)))
    return 1 if B.FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
