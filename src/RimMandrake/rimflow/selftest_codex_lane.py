#!/usr/bin/env python3
"""selftest_codex_lane.py: the promises of design/specs/2026-11-27-codex-lane/boundary.md, one test each.

Item RIMMANDRAKE_BUILD_CODEX_LANE_WHEN_CLAUDE_ROOM_IS_SHORT. Every test drives the real codex_lane functions and the
real list_dispatch.tick with a fake notice, a fake Codex advice, a fake Codex, a fake check and fake launchers. No test
reads the live account plan, sends a Codex job or starts a unit.
"""
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

os.environ.setdefault("RM_UNDER_SELFTEST", "1")
_TMP = tempfile.mkdtemp(prefix="selftest_codex_lane_")
os.environ["RM_LIST_DISPATCH_DIR"] = os.path.join(_TMP, "list_dispatch")

import codex_lane as CL  # noqa: E402
import list_dispatch as LD  # noqa: E402

NOW = 1795800000.0
CHECK = "cmd:python3 src/RimMandrake/rimflow/selftest_some_tool.py"


def notice(why="system live at 79% (line 5%): it stays. Next: none (no account can take over: it waits for a reset)",
           state="none", account_end=False, age_s=60, **more):
    import account_plan as AP
    return dict({"state": state, "at": AP.iso(NOW - age_s), "account": "system", "line": 5, "pct_left": 79.0,
                 "why": why, "drain": False, "account_end": account_end}, **more)


AMPLE = notice(why="system live at 79% (line 5%): it stays. Next: lukas at about 3 PM PST")
OK_ADV = {"state": "OK", "why": "yes: codex has 80% left, over its 25% line"}


def item(**kw):
    d = {"state": "open", "effect": CHECK, "verdict": "fails", "out": "FAIL t_x", "title": "Fix the tool",
         "mod_work": {"mod": None}, "mod": None, "off": False, "held": False, "blocked": False, "wait_until": None,
         "claimed": None, "home": "pipeline:tools", "events": 3, "depth": 0, "needs": "offline"}
    d.update(kw)
    return d


def cfg(**lane):
    c = LD.load_cfg()
    c["codex_lane"] = dict(c.get("codex_lane") or {}, enabled=True, **lane)
    c["hosts"] = {}
    return c


def facts(items):
    return {"items": items, "runs": {}, "other_live": 0, "systems": None, "onboard": None, "load": 1.0,
            "cores": 14, "recent": None, "hosts": {}, "pool": None}


class Fx(object):
    """The fakes of one tick: what was launched, sent and noted."""
    def __init__(self, room=None, adv=None):
        self.claude, self.codex, self.landers, self.notes = [], [], [], []
        self.room = room if room is not None else notice()
        self.adv = adv if adv is not None else OK_ADV

    def tick_fx(self, items):
        return {"facts": lambda st: facts(items), "account": lambda: (True, ""),
                "launch": lambda *a, **k: (self.claude.append(a[0]) or (0, "DETACHED u-%s" % a[0], "u-%s" % a[0])),
                "codex_notice": lambda: self.room, "codex_advice": lambda: self.adv,
                "codex_launch": lambda iid, job: (self.codex.append(iid) or (0, "ok", "rm-codex-lane-%s" % iid)),
                "codex_alive": lambda unit: True,
                "codex_lander": lambda iid, brief: (self.landers.append((iid, brief)) or (0, "DETACHED l", "l-" + iid)),
                "need": lambda *a, **k: None}


def fresh_state():
    d = os.environ["RM_LIST_DISPATCH_DIR"]
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)


def tick(items, fxo, **lane):
    fresh_state()
    return LD.tick(cfg(**lane), True, fx=fxo.tick_fx(items), now=NOW)


# ---- the promises ---------------------------------------------------------------------------------------------------

def t_room_short_sends_a_proven_ticket_to_codex():
    for why, kw in (("no account can take over", {}),
                    ("the fleet is stopped", {"state": "stop", "why": "hard stop"}),
                    ("the live account is at its line", {"state": "soft", "account_end": True, "why": "at its line"})):
        fxo = Fx(room=notice(**kw))
        rd = tick({"A": item()}, fxo)
        assert fxo.codex == ["A"], (why, fxo.codex, rd["items"])
        assert fxo.claude == [], (why, "the Claude lane launched it too", fxo.claude)
        assert rd["items"]["A"]["decision"] == "codex_sent", (why, rd["items"]["A"])
    # a dry tick sends nothing and says what it would do
    fresh_state()
    fxo = Fx()
    rd = LD.tick(cfg(), False, fx=fxo.tick_fx({"A": item()}), now=NOW)
    assert fxo.codex == [] and rd["items"]["A"]["decision"] == "would_codex", rd["items"]["A"]
    # the same item, check by an acceptance script
    fxo = Fx()
    tick({"B": item(effect="cmd:python3 design/specs/x/thing_accept.py")}, fxo)
    assert fxo.codex == ["B"], fxo.codex
    # the room reading is what the account plan writes: the phrase it matches stays in account_plan.py
    with open(os.path.join(REPO, "src", "RimMandrake", "Utils", "account_plan.py"), encoding="utf-8") as f:
        assert CL.NO_TAKEOVER in f.read(), "account_plan.py no longer says %r: codex_lane.room reads it" % CL.NO_TAKEOVER


def t_room_ample_sends_none():
    for room in (AMPLE, notice(age_s=3600), {}, None, notice(could_not_look=True)):
        fxo = Fx(room=room if room is not None else {})
        if room is None:
            fxo.room = None
        rd = tick({"A": item()}, fxo)
        assert fxo.codex == [], (room, fxo.codex)
        assert fxo.claude == ["A"], (room, "the Claude lane keeps it", fxo.claude, rd["items"]["A"])
    st, _w = CL.room(AMPLE, NOW)
    assert st == CL.AMPLE, st
    st, w = CL.room(notice(age_s=3600), NOW)
    assert st == CL.COULD_NOT_LOOK and "min" in w, (st, w)


def t_a_mod_ticket_is_never_sent():
    cases = {"M1": item(mod_work={"mod": "FlowWorks"}), "M2": item(mod="FlowWorks"),
             "M3": item(home="mod:FlowWorks"), "M4": item(mod_work={"mod": None, "unreadable": "no mod list"})}
    for iid, it in cases.items():
        fxo = Fx()
        tick({iid: it}, fxo)
        assert fxo.codex == [], (iid, fxo.codex)
    ok, why = CL.eligible(item(home="mod:FlowWorks"), CL.check_rx(cfg()), NOW)
    assert not ok and "mod" in why, why
    # and the other tickets the lane never offers: a check that is not a test, a parked one, a game check
    for it in (item(effect="path-has:design/x.md::y"), item(blocked=True), item(wait_until=NOW + 3600),
               item(needs="game-up"), item(off=True), item(verdict="holds"), item(claimed="doing under X")):
        assert not CL.eligible(it, CL.check_rx(cfg()), NOW)[0], it


def _job(tmp, effect=CHECK):
    job = os.path.join(tmp, "job")
    os.makedirs(job, exist_ok=True)
    with open(os.path.join(job, "job.json"), "w", encoding="utf-8") as f:
        json.dump({"item": "A", "effect": effect, "title": "Fix the tool", "out": "FAIL t_x"}, f)
    return job


def _work_fx(tmp, verdict, diff="diff --git a/x b/x\n+fix\n", gate=0, codex_err=False):
    clone = os.path.join(tmp, "clone")
    os.makedirs(clone, exist_ok=True)
    seen = {"notes": [], "codex": 0, "env": None}

    def codex(cwd, prompt, result, events, spend):
        seen["codex"] += 1
        seen["env"] = {k: os.environ.get(k) for k in CL.SANDBOX_KEYS}
        seen["prompt"] = prompt
        return {"is_error": codex_err, "result": "Codex TRANSPORT (no route)" if codex_err else "done"}
    return seen, {"gate": lambda: gate, "clone": lambda iid, job: clone, "codex": codex,
                  "diff": lambda c, p: (open(p, "w").write(diff), diff)[1],
                  "check": lambda effect, root: (verdict, "out of the check"),
                  "note": lambda iid, text: seen["notes"].append(text) or 0}


def t_a_result_that_fails_its_check_is_not_landed():
    tmp = tempfile.mkdtemp(dir=_TMP)
    job = _job(tmp)
    seen, wfx = _work_fx(tmp, "fails")
    res = CL.work(job, wfx)
    assert res["state"] == "failed" and "check" in res["why"], res
    assert seen["notes"] and "not landed" in seen["notes"][0], seen["notes"]
    # an empty diff is no result either
    tmp2 = tempfile.mkdtemp(dir=_TMP)
    res2 = CL.work(_job(tmp2), _work_fx(tmp2, "holds", diff="")[1])
    assert res2["state"] == "failed" and "nothing" in res2["why"], res2
    # the next tick reads the failed result: no lander, and the Claude lane takes the item again
    fresh_state()
    st = {"codex_lane": {"items": {"A": {"state": "sent", "job": job, "unit": "u", "at": NOW - 60}}}}
    LD._write(os.path.join(LD.sdir(), "state.json"), st)
    fxo = Fx()
    rd = LD.tick(cfg(), True, fx=fxo.tick_fx({"A": item()}), now=NOW)
    assert fxo.landers == [], fxo.landers
    assert fxo.codex == [] and fxo.claude == ["A"], (fxo.codex, fxo.claude, rd["items"]["A"])


def t_his_codex_share_is_left():
    for adv in ({"state": "LINE", "why": "NO: codex has 24% left, at or under its 25% line"},
                {"state": "UNMEASURED", "why": "COULD NOT LOOK: no timed pass has read codex"}):
        fxo = Fx(adv=adv)
        rd = tick({"A": item()}, fxo)
        assert fxo.codex == [], (adv, fxo.codex)
        assert fxo.claude == ["A"], (adv, fxo.claude, rd["items"]["A"])
    # the work unit asks the gate again at send time: a line reached meanwhile sends no job
    tmp = tempfile.mkdtemp(dir=_TMP)
    seen, wfx = _work_fx(tmp, "holds", gate=4)
    res = CL.work(_job(tmp), wfx)
    assert seen["codex"] == 0 and res["state"] == "void", (seen, res)
    # the lane's own gate: a blind line sends nothing, the line refuses, over the line goes
    import codex_advice
    real = codex_advice.advice
    try:
        for state, want in (("UNMEASURED", 2), ("OK", 0)):
            codex_advice.advice = lambda s=state: {"state": s, "why": "fake %s" % s}
            assert CL.gate() == want, (state, CL.gate())
        codex_advice.advice = lambda: {"state": "LINE", "why": "fake line"}
        real_rec = codex_advice._record
        codex_advice._record = lambda *a: None
        try:
            assert CL.gate() == codex_advice.EXIT_LINE
        finally:
            codex_advice._record = real_rec
    finally:
        codex_advice.advice = real
    # a review asks the same gate
    sent = []
    r = CL.review(["src/RimMandrake/rimflow/codex_lane.py"], {"gate": lambda: 4, "consult": lambda *a: sent.append(a)})
    assert r["state"] == "refused" and not sent, r


def t_a_passing_result_gets_one_sonnet_lander():
    tmp = tempfile.mkdtemp(dir=_TMP)
    job = _job(tmp)
    seen, wfx = _work_fx(tmp, "holds")
    res = CL.work(job, wfx)
    assert res["state"] == "built", res
    fresh_state()
    st = {"codex_lane": {"items": {"A": {"state": "sent", "job": job, "unit": "u", "at": NOW - 60}}}}
    LD._write(os.path.join(LD.sdir(), "state.json"), st)
    fxo = Fx()
    rd = LD.tick(cfg(), True, fx=fxo.tick_fx({"A": item()}), now=NOW)
    assert len(fxo.landers) == 1 and fxo.claude == [] and fxo.codex == [], (fxo.landers, fxo.claude, fxo.codex)
    brief = fxo.landers[0][1]
    for want in (os.path.join(job, "patch.diff"), CHECK, "roles/code_review.md", "./publish"):
        assert want in brief, want
    assert rd["items"]["A"]["decision"] == "codex_landing", rd["items"]["A"]
    # the next tick launches no second lander
    fxo2 = Fx()
    LD.tick(cfg(), True, fx=fxo2.tick_fx({"A": item()}), now=NOW + 600)
    assert fxo2.landers == [], fxo2.landers
    assert CL.LANDER_MODEL == "sonnet"
    # a built result whose ticket closed meanwhile gets no lander
    fresh_state()
    st = {"codex_lane": {"items": {"A": {"state": "built", "job": job, "unit": "u", "at": NOW - 60}}}}
    LD._write(os.path.join(LD.sdir(), "state.json"), st)
    fxo3 = Fx()
    LD.tick(cfg(), True, fx=fxo3.tick_fx({}), now=NOW)
    assert fxo3.landers == [], fxo3.landers


def t_one_try_per_ticket():
    fresh_state()
    st = {"codex_lane": {"items": {"A": {"state": "failed", "job": "/nope", "at": NOW - 900}}}}
    LD._write(os.path.join(LD.sdir(), "state.json"), st)
    fxo = Fx()
    LD.tick(cfg(), True, fx=fxo.tick_fx({"A": item()}), now=NOW)
    assert fxo.codex == [] and fxo.claude == ["A"], (fxo.codex, fxo.claude)
    # a unit that died with no result: void, no try spent, sent again
    fresh_state()
    st = {"codex_lane": {"items": {"A": {"state": "sent", "job": os.path.join(_TMP, "none"), "unit": "dead",
                                         "at": NOW - 900}}}}
    LD._write(os.path.join(LD.sdir(), "state.json"), st)
    fxo = Fx()
    fx = fxo.tick_fx({"A": item()})
    fx["codex_alive"] = lambda unit: False
    LD.tick(cfg(), True, fx=fx, now=NOW)
    assert fxo.codex == [] and fxo.claude == [], ("voided this tick, sent next", fxo.codex, fxo.claude)
    fxo = Fx()
    LD.tick(cfg(), True, fx=fxo.tick_fx({"A": item()}), now=NOW + 600)
    assert fxo.codex == ["A"], fxo.codex
    # two system failures in a row: the lane stops trying and says so
    cst = {"items": {"A": {"state": "void", "voids": 2, "why": "unit gone"}}}
    out = CL.plan(cfg(), cst, facts({"A": item()}), NOW, (CL.SHORT, ""), (True, ""), (True, ""), lambda u: True)
    assert "A" not in out["send"] and "A" not in out["take"], out
    # max_live: a third ticket waits for a Codex slot and is not given to Claude
    fresh_state()
    fxo = Fx()
    rd = LD.tick(cfg(max_live=2), True, fx=fxo.tick_fx({"A": item(), "B": item(), "C": item()}), now=NOW)
    assert sorted(fxo.codex) == ["A", "B"] and fxo.claude == [], (fxo.codex, fxo.claude)
    assert rd["items"]["C"]["decision"] == "codex_waits", rd["items"]["C"]


def t_the_codex_child_reads_no_real_state():
    tmp = tempfile.mkdtemp(dir=_TMP)
    job = _job(tmp)
    seen, wfx = _work_fx(tmp, "holds")
    CL.work(job, wfx)
    for k in CL.SANDBOX_KEYS:
        v = seen["env"].get(k)
        assert v and v.startswith(os.path.join(job, "sandbox")), (k, v)
    assert "./publish" in seen["prompt"] and "Never" in seen["prompt"], seen["prompt"][:400]
    # the scratch clone is made under the lane's seat, never UNKNOWN (seen on Archmagi 2026-11-27 12:51 PM PST)
    calls = []
    real = CL.subprocess.run
    try:
        class R(object):
            returncode, stdout, stderr = 1, "", "fake"
        CL.subprocess.run = lambda argv, **kw: calls.append(kw.get("env") or {}) or R()
        try:
            CL.make_clone("A", job)
        except RuntimeError:
            pass
    finally:
        CL.subprocess.run = real
    assert calls and calls[0].get("RM_SEAT") == "BENCH", calls


def t_review_goes_by_code_review_brief():
    sent, judged = [], []

    def consult(argv):
        sent.append(argv)
        out = argv[argv.index("--out") + 1]
        with open(out, "w", encoding="utf-8") as f:
            f.write('{"id": "x", "class": "polish"}\n')
        return 0, "ANSWERED"
    r = CL.review(["src/RimMandrake/rimflow/codex_lane.py"],
                  {"gate": lambda: 0, "consult": consult, "lander": lambda iid, brief: judged.append(brief) or (0, "", "u"),
                   "jobs": os.path.join(_TMP, "reviews")})
    assert r["state"] == "judging", r
    argv = sent[0]
    files = [argv[i + 1] for i, a in enumerate(argv) if a == "-f"]
    assert "src/RimMandrake/rimflow/codex_lane.py" in files, files
    assert "design/specs/2026-11-27-codex-lane/boundary.md" in files, files
    with open(argv[argv.index("--prompt-file") + 1], encoding="utf-8") as f:
        prompt = f.read()
    assert "A Problem: a significant finding" in prompt, "the prompt carries roles/code_review.md"
    assert len(judged) == 1 and "code_review.md" in judged[0] and r["out"] in judged[0], judged


TESTS = (t_room_short_sends_a_proven_ticket_to_codex, t_room_ample_sends_none, t_a_mod_ticket_is_never_sent,
         t_a_result_that_fails_its_check_is_not_landed, t_his_codex_share_is_left,
         t_a_passing_result_gets_one_sonnet_lander, t_one_try_per_ticket, t_the_codex_child_reads_no_real_state,
         t_review_goes_by_code_review_brief)


def main():
    bad = 0
    saved = {k: os.environ.get(k) for k in CL.SANDBOX_KEYS}
    try:
        for t in (t_room_short_sends_a_proven_ticket_to_codex, t_room_ample_sends_none, t_a_mod_ticket_is_never_sent,
                  t_a_result_that_fails_its_check_is_not_landed, t_his_codex_share_is_left,
                  t_a_passing_result_gets_one_sonnet_lander, t_one_try_per_ticket,
                  t_the_codex_child_reads_no_real_state, t_review_goes_by_code_review_brief):
            try:
                t()
                print("PASS %s" % t.__name__)
            except Exception as e:  # noqa: BLE001 - each test reports its own failure
                bad += 1
                print("FAIL %s: %s: %s" % (t.__name__, type(e).__name__, e))
            finally:
                for k, v in saved.items():
                    if v is None:
                        os.environ.pop(k, None)
                    else:
                        os.environ[k] = v
    finally:
        shutil.rmtree(_TMP, ignore_errors=True)
    print("%d of %d pass" % (len(TESTS) - bad, len(TESTS)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
