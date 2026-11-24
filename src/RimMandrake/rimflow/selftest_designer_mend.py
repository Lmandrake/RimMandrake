#!/usr/bin/env python3
"""Selftest of the Designer's mend in its own session (design/specs/2026-11-24-designer-mends-in-its-session/boundary.md):
after the coverage judge's refusal the next Designer run resumes the session that holds the design. Driven through
role_launch.decide_roles, launch_role, launch_argv and _supervise_one; temp dirs, no systemd, no git."""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    import selftest_dispatcher as SD
    import designer_mend as DM
except ImportError as e:
    print("FAIL cannot import: %s" % e)
    sys.exit(1)

RL = SD.RL
FAILS = []
T = SD.at_local("13:00")
S5 = "55555555-2222-3333-4444-555555555555"
S3 = "33333333-2222-3333-4444-555555555555"
S4 = "44444444-2222-3333-4444-555555555555"
GAP = {"gid": "g1", "what": "the winch bar asks for no proof", "where": "tree", "ids": ["winch_side"], "return_to": 3}


def check(ok, msg):
    print("%s %s" % ("ok  " if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


class World:
    """One concept returned from stage 5, its three Designer runs and their transcripts."""

    def __init__(self, to=3, by=None, verdict=None, results=None, stage=None, ages=None, ctx=100000,
                 model="claude-opus-5-5"):
        self.model = model
        self.tmp = tempfile.mkdtemp(prefix="mend_")
        self.concept = os.path.join(self.tmp, "concepts", "ModOne")
        self.projects = os.path.join(self.tmp, "projects")
        os.makedirs(self.concept)
        ret = {"stage": 5, "outcome": "return", "to": to, "run": "U5", "decision": "g1"}
        if by:
            ret["by"] = by
        self.st = {"mod": "ModOne", "stage": to if stage is None else stage, "status": "ready", "results": results or [
            {"stage": 3, "outcome": "done", "run": "U3"}, {"stage": 4, "outcome": "done", "run": "U4"}, ret]}
        self.write("stage.json", self.st)
        self.write("coverage_verdict.json", verdict or {"verdict": "not_covered", "gaps": [GAP], "judge": "J"})
        ages = dict({"U5": 60, "U3": 1200, "U4": 600}, **(ages or {}))
        mid = None      # as every role run records it on a machine that names no opus id (measured 2026-11-24)
        self.runs = []
        for u, sid in (("U3", S3), ("U4", S4), ("U5", S5)):
            if u == "U5" and by:
                self.transcript(sid, T - ages[u], ctx)
                self.runs.append({"unit": u, "state": "done", "concept": self.concept, "at": T - ages[u] - 300,
                                  "session": sid, "runner": "claude", "by": by, "tokens": 0, "model_id": mid})
                continue
            self.runs.append({"unit": u, "state": "done", "concept": self.concept, "at": T - ages[u] - 300, "session": sid,
                              "runner": "claude", "tokens": 50000, "model_id": mid})
            self.transcript(sid, T - ages[u], ctx)

    def write(self, name, obj):
        with open(os.path.join(self.concept, name), "w", encoding="utf-8") as f:
            json.dump(obj, f)

    def transcript(self, sid, mtime, ctx):
        d = os.path.join(self.projects, "p")
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, sid + ".jsonl")
        with open(p, "w", encoding="utf-8") as f:
            f.write(json.dumps({"type": "assistant", "message": {"id": "m", "model": self.model, "usage": {
                "input_tokens": 10, "cache_read_input_tokens": ctx, "cache_creation_input_tokens": 0,
                "output_tokens": 0}}}) + "\n" if ctx is not None else json.dumps({"message": {"model": self.model}}) + "\n")
        os.utime(p, (mtime, mtime))
        return p

    def run(self, unit):
        return next(r for r in self.runs if r["unit"] == unit)

    def launch(self, cfg=None, pre=None, stage_open=None, req=None):
        st = SD.fresh()
        st["roles"] = {"Arbiter": {"done": {}, "runs": self.runs, "run_now": dict(
            {"at": T, "by": "Dispatcher", "mode": "run", "concept": self.concept, "why": "chain"}, **(req or {}))}}
        ro = SD.robs(SD.ops_status(T))
        ro["stage_open"] = stage_open or (lambda c, u, b: ("PACKET", b))
        ro["coverage_pre"] = lambda c: pre
        ro["projects"] = self.projects
        self.role = dict(dict(SD.arbiter(enabled=False), model="opus"), **(cfg or {}))
        acts = SD.role_acts(SD.rdecide([self.role], st, ro, T + 60))
        got = [a for a in acts if a["do"] == "role_launch"]
        check(len(got) == 1, "one launch (%r)" % [a.get("why") for a in acts])
        return got[0] if got else {}

    def done(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


def t_a_refusal_resumes_the_session_that_read_it():
    w = World()
    a = w.launch()
    check(a.get("resume") == S5 and a.get("resume_of") == "U5", "the returning stage-5 run's session: %r" % a.get("resume"))
    m = a.get("message") or ""
    check(GAP["what"] in m and "PACKET" in m, "the gaps and the packet are in the message")
    check("resumes session" in a.get("why", ""), "the launch says it resumes: %s" % a.get("why"))
    role = RL.launch_role(w.role, a)
    argv = RL.launch_argv(role, a["unit"], m, "o", "e", "/x/claude", session="NEW")
    check("--resume" in argv and argv[argv.index("--resume") + 1] == S5 and "--session-id" not in argv,
          "the argv resumes it")
    check(not any(w_ in m.lower() for w_ in ("budget of", "spent", "token cap")), "no spend figure in the mend head")
    w.done()


def t_a_program_return_resumes_the_writer():
    w = World(by="program")
    a = w.launch()
    check(a.get("resume") == S3 and a.get("resume_of") == "U3", "the stage-3 run: %r" % a.get("resume"))
    w.done()


def t_a_cold_or_large_session_starts_fresh():
    def fresh(w, word, label, **kw):
        a = w.launch(**kw)
        check(not a.get("resume") and word in a.get("why", "") and "RESUMED" not in a.get("message", ""),
              "%s: fresh, said (%s)" % (label, a.get("why")))
        w.done()
    fresh(World(ages={"U5": 55 * 60, "U3": 9000}), "cold", "55 min old")
    fresh(World(ctx=400000), "ceiling", "a context at the ceiling")
    fresh(World(ctx=None), "context", "an unreadable context")
    fresh(World(model="claude-fable-5-2"), "model", "another tier")
    fresh(World(), "model", "a launch pinned to another model", cfg={"model": "sonnet"})
    for key, val, word in (("runner", "codex", "codex"),
                           ("state", "running", "running"), ("session", None, "session")):
        w = World()
        for r in w.runs:
            r[key] = val
        if key == "state":      # a live run of the role holds the launch itself: only the plan is read
            p = DM.plan(w.runs, w.concept, w.st, {"verdict": "not_covered", "gaps": [GAP]}, T, "opus",
                        projects=w.projects)
            check(not p.get("session") and word in p["why"], "a live run: fresh (%s)" % p.get("why"))
            w.done()
            continue
        fresh(w, word, key)
    w = World()
    shutil.rmtree(w.projects)
    fresh(w, "transcript", "no transcript")
    fresh(World(), "codex", "a Codex launch", req={"runner": "codex"})
    w = World(ages={"U5": 53 * 60})
    check(w.launch().get("resume") == S5, "54 min old at the launch still resumes")
    w.done()


def t_the_exam_and_the_judge_never_resume():
    w = World(to=4)
    a = w.launch()
    check(not a.get("resume"), "a return to the exam is fresh")
    w.done()
    w = World(by="program", ages={"U3": 9000})
    check(not w.launch().get("resume"), "a warm stage-4 run is never resumed")
    w.done()
    w = World(stage=5)
    a = w.launch(pre=[["python3", "judge"]])
    check(not a.get("resume") and a.get("pre_launch"), "a stage-5 launch carries no resume and keeps its judge step")
    w.done()
    w = World()
    a = w.launch(pre=[["python3", "judge"]])
    check(not a.get("resume"), "a launch with a pre-step is never resumed over it")
    w.done()


def t_only_the_return_resumes():
    base = [{"stage": 3, "outcome": "done", "run": "U3"}, {"stage": 5, "outcome": "return", "to": 3, "run": "U5"}]
    for label, kw in (("a rejected mend", {"results": base + [{"stage": 3, "outcome": "rejected", "run": "U6"}]}),
                      ("a done stage", {"results": base[:1], "stage": 4}),
                      ("a covered verdict", {"verdict": {"verdict": "covered", "gaps": []}}),
                      ("a concept moved on from the return", {"to": 2, "stage": 3}),
                      ("no gaps", {"verdict": {"verdict": "not_covered", "gaps": []}})):
        w = World(**kw)
        a = w.launch()
        check(not a.get("resume") and "mend" not in a.get("why", ""), "%s: nothing resumed, nothing said" % label)
        w.done()
    w = World()
    p = DM.plan(w.runs, w.concept, w.st, {"verdict": "not_covered", "gaps": [GAP], "tree": "old"}, T,
                "opus", projects=w.projects, tree="new")
    check(not p.get("owed"), "a verdict on another tree owes no mend")
    other = dict(w.run("U5"), concept="/elsewhere/ModTwo")
    p = DM.plan([other], w.concept, w.st, {"verdict": "not_covered", "gaps": [GAP]}, T, "opus",
                projects=w.projects)
    check(p.get("owed") and not p.get("session"), "another concept's run is never resumed")
    w.done()


def t_a_resumed_run_is_charged_its_own_part():
    def harvest(total, earlier, **extra):
        mid = "claude-opus-5-5"
        rs = {"runs": [{"unit": "U5", "state": "done", "concept": "/c", "at": T - 900, "session": S5, "tokens": earlier},
                       dict({"unit": "U6", "state": "running", "concept": "/c", "at": T - 600, "session": S5, "mode": "run",
                             "resume_of": "U5", "budget": 900, "item": "X", "scope": "S.scope", "marker": "M",
                             "day": RL.day_of(T)}, **extra)]}
        closed = []
        obs = {"unit_state": lambda u: "inactive", "result": lambda r: SD.cli(SD.usage(input_tokens=total), mid,
                                                                             subtype="success"),
               "procs": lambda *a, **k: [], "stage_close": lambda c, u, t: (closed.append(t), (True, []))[1],
               "stage_land": lambda c, u: None, "stage_turn": lambda c: None, "program_closed": lambda c, u: None,
               "stage_status": lambda c: {"stage": 4, "status": "waiting_owner"}}
        RL._supervise_one("Designer", rs, dict(RL.ROLE_DEFAULTS, name="Designer", model="opus"), obs, T,
                          lambda **k: None, set())
        return next(r for r in rs["runs"] if r["unit"] == "U6"), closed
    run, closed = harvest(80000, 50000)
    check(run["tokens"] == 30000 and run.get("session_tokens") == 80000 and closed == [30000],
          "its own part: %r, closed %r" % (run.get("tokens"), closed))
    check(run["state"] == "done" and "model_usage" not in run and run.get("session_model_usage"),
          "the session's usage is not filed as the run's own")
    run, closed = harvest(80000, None)
    check(run["tokens"] is None and run["state"] == "done" and closed == [None], "no earlier total: UNMEASURED, still done")
    run, closed = harvest(80000, 50000, resume_of=None)
    check(run["tokens"] == 80000, "a run that resumed nothing is charged whole")


def t_a_mend_that_cannot_look_launches_fresh():
    w = World()
    with open(os.path.join(w.concept, "coverage_verdict.json"), "w", encoding="utf-8") as f:
        f.write("{not json")
    a = w.launch()
    check(not a.get("resume") and "could not look" in a.get("why", ""), "an unreadable verdict: fresh, said (%s)" % a.get(
        "why"))
    w.done()


def main():
    print("-- t_a_refusal_resumes_the_session_that_read_it")
    t_a_refusal_resumes_the_session_that_read_it()
    print("-- t_a_program_return_resumes_the_writer")
    t_a_program_return_resumes_the_writer()
    print("-- t_a_cold_or_large_session_starts_fresh")
    t_a_cold_or_large_session_starts_fresh()
    print("-- t_the_exam_and_the_judge_never_resume")
    t_the_exam_and_the_judge_never_resume()
    print("-- t_only_the_return_resumes")
    t_only_the_return_resumes()
    print("-- t_a_resumed_run_is_charged_its_own_part")
    t_a_resumed_run_is_charged_its_own_part()
    print("-- t_a_mend_that_cannot_look_launches_fresh")
    t_a_mend_that_cannot_look_launches_fresh()
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
