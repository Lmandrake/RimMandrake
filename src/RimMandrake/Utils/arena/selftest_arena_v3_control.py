#!/usr/bin/env python3
"""selftest_arena_v3_control.py - v3_control.py (ARENA_CONTROL_BUILD_V3_TESTER_AFTER_CLOSE), offline.

No real model, review, seat, bridge or game: the build helper, the tester helper and the GPT reviewer are fake
callables, the replay clone is a temp git repo, and the signed event log lives under a temp ARENA_ROOT.

Criterion 1 (v3c refuses a close without both a review record and a tester record bound to the sha) and criterion 2
(the v3 procedure briefs no new build before the tester helper's test_start) are each proved by FORCED FAILURE: the
scenario runs against the real module (must be green) and against a copy of its source with the guarding line
mutated (must go red). A mutation that leaves its scenario green is itself a failure of this selftest.
  G  done gate, from a real v3c run's signed records: refused with no review record, no tester record, the builder
     as tester, a tester test_end without test_start, a review of another sha, a newer tester fail, a newer review
     fail, an altered / missing record file, a stale sha, a short sha; accepted for the good sha.
  W  v3c end to end: a failing review never closes (every close logged refused, the task parks); a passing one is
     done; a tester FAIL never reaches the review.
  D  v3 refuses a build brief while a replay build_end has no test_start from a different agent (missing, or the
     builder testing itself), without invoking the model.
  O  v3 end to end with a tester FAIL: every build brief after a build_end comes after that build's test_start.
  P  production v3 records (arena_v3_adapter: run_id v3-ledger) do not block the replay procedure.
  S  a tester id equal to the builder's is refused before any test_start; a refused preflight logs no test_start.
  C  a helper whose CLOSED sha is not its commit (or with no commit) gets no build_end.
  RR a replace ref the builder plants does not change the tree the tester and the reviewer see (review r1).
  PIN the reviewer script runs only byte-identical to the harness checkout's committed HEAD (review r1).
  EA builder .gitattributes (export-ignore/-subst) do not change the tested tree (review r2).
  RT v3c's review() refuses a sha with no passing tester record bound to it (review r2).
  LK one lock per arm whatever --ctl is, so two procedures cannot interleave on one log (review r2).
  plus: the briefs, live task -> live_owed, the real signed HarnessWriter log.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import arena_eventlog as L  # noqa: E402
import arena_tasks as A  # noqa: E402
import ralph_a_loop as RA  # noqa: E402
import v3_control as V  # noqa: E402

FAILS = []
SRC = (HERE / "v3_control.py").read_text()
TBASE = [None]


def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def variant(muts=()):
    """v3_control, or a copy with each (old, new) applied (exec'd with the real __file__ so imports resolve)."""
    if not muts:
        return V
    src = SRC
    for old, new in muts:
        assert src.count(old) == 1, "mutation anchor not unique/absent: %r" % old
        src = src.replace(old, new)
    m = types.ModuleType("v3_control_mut")
    m.__file__ = str(HERE / "v3_control.py")
    exec(compile(src, m.__file__, "exec"), m.__dict__)
    return m


def sh(cwd, *a):
    return subprocess.run(list(a), cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()


TASK = {"id": "V3_ABSDIFF", "kind": "code", "size": "S", "area": "x", "live": "none", "base_sha": "",
        "prompt": "write absdiff(a, b) in mod.py returning |a - b|", "criteria": "absdiff(a, b) == |a - b| for all ints",
        "proof": "python3 -c 'import mod; assert mod.absdiff(5, 3) == 2'"}
GOOD = "def absdiff(a, b):\n    return abs(a - b)\n"
WEAK = "def absdiff(a, b):\n    return a - b\n"


def real_tester(prompt, cwd):
    r = subprocess.run([sys.executable, "-c", "import mod; assert mod.absdiff(3, 5) == 2, mod.absdiff(3, 5)"],
                       cwd=str(cwd), capture_output=True, text=True)
    return "ran absdiff(3, 5): %s\nVERDICT: %s" % (r.stderr.strip()[-200:] or "2", "PASS" if r.returncode == 0
                                                   else "FAIL")


class World:
    """A temp replay clone + ctl + fakes. builder(prompt) -> source | None; tester(prompt, cwd) -> text;
    reviewer(task, sha, diff) -> verdict."""

    def __init__(self, tmp, name, mod=V, arm="v3", builder=None, tester=None, reviewer=None, writer=None,
                 new_id=None, closed=None, preflight=None, task=TASK, lock_dir=None):
        self.d = tmp / name
        self.root, self.ctl = self.d / "clone", self.d / "ctl"
        self.root.mkdir(parents=True)
        for a in (("init", "-q", "-b", "main"), ("config", "user.email", "t@t"), ("config", "user.name", "t")):
            sh(self.root, "git", *a)
        (self.root / "README").write_text("x\n")
        sh(self.root, "git", "add", "README")
        sh(self.root, "git", "commit", "-q", "-m", "init")
        self.builder = builder or (lambda p: GOOD)
        self.tester = tester or real_tester
        self.reviewer_fn = reviewer or (lambda task, sha, diff: "pass")
        self.closed = closed
        self.calls, self.prompts, self.reviews = [], [], []
        self.writer = writer or RA.ListWriter()
        self.task = task
        if preflight:
            self.preflight = preflight
        self.p = mod.Procedure(arm, self.root, self.ctl, model=self, writer=self.writer, reviewer=self.reviewer,
                               runway=lambda: {"state": "MEASURED", "runway": 0.9}, new_id=new_id,
                               tester_tmp=TBASE[0], procs=None, lock_dir=lock_dir or self.d)

    def __call__(self, role, prompt, *, cwd, agent_id, run_id, timeout_s, log, sandbox=None):
        self.calls.append((role, agent_id))
        self.prompts.append((role, prompt))
        if role == "build":
            src = self.builder(prompt)
            if src is None:
                return {"rc": 0, "text": "NOTE: stuck, NEXT: think"}
            (Path(cwd) / "mod.py").write_text(src)
            sh(cwd, "git", "add", "mod.py")
            sh(cwd, "git", "commit", "-q", "--allow-empty", "-m", "build %d" % len(self.calls))
            head = sh(cwd, "git", "rev-parse", "HEAD")
            return {"rc": 0, "text": "built\nCLOSED: %s" % (self.closed(head) if self.closed else head)}
        return {"rc": 0, "text": self.tester(prompt, cwd)}

    def reviewer(self, task, sha, diff, *, log):
        self.reviews.append(sha)
        v = self.reviewer_fn(task, sha, diff)
        return {"verdict": v, "text": "review of %s\nVERDICT: %s" % (sha[:12], (v or "?").upper())}

    def recs(self):
        return self.writer.records()

    def ev(self, *names):
        return [r for r in self.recs() if r["event"] in names]


def seed_build(w, arm="v3", run_id=None, builder="old-builder", sha="a" * 40, task="OLD"):
    w.writer.emit(arm, "build_end", lane="replay", run_id=run_id or "%s.replay.0" % arm, task=task, sha=sha,
                  detail={"builder": builder, "build_id": "%s.%s" % (task, sha[:12])})


# ------------------------------------------------------------------------------------------------ G: the done gate
GATE_CASES = []      # (name, records/review_dir transform, mutation anchor that, reverted, lets it through)


def _good_v3c(tmp, name, mod):
    w = World(tmp, name, mod, arm="v3c")
    out = w.p.work(w.task)
    assert out["outcome"] == "done", out
    return w, out["sha"]


def gate(name, muts):
    """muts: the source edits that revert the guard(s) refusing this case; a str is one refusal turned to accept."""
    if isinstance(muts, str):
        muts = [(muts, muts.replace("return False,", "return True,"))]

    def deco(fn):
        GATE_CASES.append((name, fn, muts))
        return fn
    return deco


TESTER_HALF_REMOVED = [(
    "    ok, why, after, tester = tester_bound(recs, arm, task_id, sha)\n    if not ok:\n        return False, why",
    "    ok, why, after, tester = True, '', [(i, r) for i, r in enumerate(L.ordered(recs)) if r.get('sha') == sha], "
    "None")]


def _drop(recs, pred):
    return [r for r in recs if not pred(r)]


def _later(rec, **kw):
    r = dict(rec, ts="2099-01-01T00:00:00Z")
    r.update(kw)
    return r


@gate("no review record bound to the sha", 'return False, "refused: no review record bound')
def g_no_review(recs, w, sha):
    return _drop(recs, lambda r: r["event"] == "critic_round"), sha


@gate("no tester record bound to the sha", TESTER_HALF_REMOVED)
def g_no_tester(recs, w, sha):
    return _drop(recs, lambda r: r["event"] in ("test_start", "test_end")), sha


@gate("tester is the builder", [("_valid_tester(tkey(r), builders)]", "True]")])
def g_tester_is_builder(recs, w, sha):
    b = [r for r in recs if r["event"] == "build_end"][-1]["detail"]["builder"]
    out = []
    for r in recs:
        if r["event"] in ("test_start", "test_end"):
            r = dict(r, detail=dict(r["detail"], tester=b.upper()))      # case-folded: still the same agent
        out.append(r)
    return out, sha


@gate("tester test_end without test_start", [(
    '    if not any(r.get("event") == "test_start" and tkey(r) == tkey(end) and i < ei for i, r in after):',
    "    if False:")])
def g_no_start(recs, w, sha):
    return _drop(recs, lambda r: r["event"] == "test_start"), sha


@gate("review bound to another sha", 'return False, "refused: no review record bound')
def g_review_other_sha(recs, w, sha):
    return [dict(r, sha="b" * 40) if r["event"] == "critic_round" else r for r in recs], sha


@gate("a newer tester fail", [('    if end.get("verdict") != "pass":', "    if False:")])
def g_newer_test_fail(recs, w, sha):
    te = [r for r in recs if r["event"] == "test_end"][-1]
    return recs + [_later(te, verdict="fail")], sha


@gate("a newer review fail", 'return False, "refused: the latest review')
def g_newer_review_fail(recs, w, sha):
    cr = [r for r in recs if r["event"] == "critic_round"][-1]
    return recs + [_later(cr, verdict="fail")], sha


@gate("review record altered on disk", 'return False, "refused: review record %s does not hash')
def g_altered(recs, w, sha):
    f = w.p.reviews / [r for r in recs if r["event"] == "critic_round"][-1]["detail"]["record"]
    f.write_text(f.read_text().replace('"verdict": "pass"', '"verdict": "pass" '))
    return recs, sha


@gate("review record missing on disk", 'return False, "refused: review record %s is missing')
def g_missing(recs, w, sha):
    (w.p.reviews / [r for r in recs if r["event"] == "critic_round"][-1]["detail"]["record"]).unlink()
    return recs, sha


@gate("review record of another sha (rehashed)", 'return False, "refused: review record %s is not a pass')
def g_record_other(recs, w, sha):
    cr = [r for r in recs if r["event"] == "critic_round"][-1]
    f = w.p.reviews / cr["detail"]["record"]
    body = json.loads(f.read_text())
    body["sha"] = "c" * 40
    raw = json.dumps(body).encode()
    f.write_bytes(raw)
    return [dict(r, detail=dict(r["detail"], record_sha256=hashlib.sha256(raw).hexdigest())) if r is cr else r
            for r in recs], sha


@gate("a stale sha (not the latest build)", [
    ("    last = builds[-1]\n", '    last = [i for i in builds if seq[i].get("sha") == sha][-1]\n'),
    ('    if seq[last].get("sha") != sha:', "    if False:")])
def g_stale(recs, w, sha):
    be = [r for r in recs if r["event"] == "build_end"][-1]
    return recs + [_later(be, sha="d" * 40, detail=dict(be["detail"], build_id="x.d"))], sha


@gate("a short sha", [("    if not (isinstance(sha, str) and SHA40.fullmatch(sha)):", "    if False:")])
def g_short(recs, w, sha):
    """every record and the review record name the short sha (rehashed): only the 40-hex rule refuses it."""
    cr = [r for r in recs if r["event"] == "critic_round"][-1]
    f = w.p.reviews / cr["detail"]["record"]
    body = json.loads(f.read_text())
    body["sha"] = sha[:12]
    raw = json.dumps(body).encode()
    f.write_bytes(raw)
    out = []
    for r in recs:
        if r.get("sha") == sha:
            r = dict(r, sha=sha[:12])
        if r.get("event") == "critic_round":
            r = dict(r, detail=dict(r["detail"], record_sha256=hashlib.sha256(raw).hexdigest()))
        out.append(r)
    return out, sha[:12]


def sc_gate(tmp, mod, tag):
    """green: the good sha passes and every case refuses. A mutation is red when ITS case is let through."""
    w, sha = _good_v3c(tmp, "G" + tag, mod)
    recs = w.recs()
    ok, why = mod.done_gate(recs, "v3c", TASK["id"], sha, w.p.reviews)
    res = {"good": ok}
    for name, fn, _ in GATE_CASES:
        w2, sha2 = _good_v3c(tmp, "G%s_%s" % (tag, fn.__name__), mod)
        r2, s2 = fn(w2.recs(), w2, sha2)
        res[name] = mod.done_gate(r2, "v3c", TASK["id"], s2, w2.p.reviews)
    return res


# ------------------------------------------------------------------------------------------------ scenarios
def sc_review_fail_never_closes(tmp, mod, tag):
    w = World(tmp, "W1" + tag, mod, arm="v3c", reviewer=lambda t, s, d: "fail")
    out = w.p.work(w.task)
    closes = [r for r in w.ev("pass_end") if (r.get("detail") or {}).get("role") == "close"]
    return (out["outcome"] == "parked" and len(closes) == V.MAX_TRIES
            and all(r["verdict"] == "refused" for r in closes) and len(w.reviews) == V.MAX_TRIES)


def sc_review_pass_done(tmp, mod, tag):
    w = World(tmp, "W2" + tag, mod, arm="v3c")
    out = w.p.work(w.task)
    closes = [r for r in w.ev("pass_end") if (r.get("detail") or {}).get("role") == "close"]
    roles = [c[0] for c in w.calls]
    return out["outcome"] == "done" and [r["verdict"] for r in closes] == ["done"] and roles == ["build", "test"]


def sc_tester_fail_no_review(tmp, mod, tag):
    w = World(tmp, "W3" + tag, mod, arm="v3c", builder=lambda p: WEAK)
    out = w.p.work(w.task)
    return out["outcome"] == "parked" and w.reviews == [] and not any(
        r["verdict"] == "done" for r in w.ev("pass_end"))


def sc_refuses_untested(tmp, mod, tag):
    """D: an untested replay build, then one tested only by its builder: no brief, no model call."""
    got = []
    for how in ("missing", "self"):
        w = World(tmp, "D%s%s" % (how, tag), mod, arm="v3")
        seed_build(w)
        if how == "self":       # a different agent tested it too, so only the same-agent flag can refuse
            for t in ("other-tester", "Old-Builder"):
                w.writer.emit("v3", "test_start", lane="replay", run_id="v3.replay.0", task="OLD", sha="a" * 40,
                              detail={"tester": t, "build_id": "OLD.aaaaaaaaaaaa"})
        try:
            w.p.build(w.task, sh(w.root, "git", "rev-parse", "HEAD"))
            got.append(False)
        except V.NotTested:
            got.append(w.calls == [] and w.ev("pass_start") == [])
        except RA.NotTested:
            got.append(w.calls == [] and w.ev("pass_start") == [])
    return all(got)


def _ordered_ok(w):
    """Every build pass_start after a build_end comes after a different-agent test_start of that build."""
    seq = L.ordered(w.recs())
    for i, r in enumerate(seq):
        if r["event"] == "pass_start" and (r.get("detail") or {}).get("role") == "build":
            for j in range(i):
                if seq[j]["event"] == "build_end":
                    b = seq[j]
                    if not any(seq[k]["event"] == "test_start" and seq[k].get("sha") == b["sha"]
                               and seq[k]["detail"]["tester"] != b["detail"]["builder"] for k in range(j, i)):
                        return False
    return True


def sc_order(tmp, mod, tag):
    """O: v3 with a tester FAIL on the first close: build, test(fail), build, test(pass), all in that order."""
    w = World(tmp, "O" + tag, mod, arm="v3", builder=lambda p: GOOD if "FAIL" in p else WEAK)
    out = w.p.work(w.task)
    roles = [c[0] for c in w.calls]
    fed = any(role == "build" and "absdiff(3, 5)" in p for role, p in w.prompts[1:])
    return (out["outcome"] == "closed" and roles == ["build", "test", "build", "test"] and fed and _ordered_ok(w)
            and L.untested_builds(w.recs()) == [] and L.flagged_same_agent(w.recs()) == [])


def sc_production_does_not_block(tmp, mod, tag):
    """P: an arena_v3_adapter v3 close (run_id v3-ledger) with no test_start does not block the replay."""
    w = World(tmp, "P" + tag, mod, arm="v3")
    seed_build(w, run_id="v3-ledger")
    w.writer.emit("v3", "build_end", lane="v3", run_id="job-7", task="X", sha="e" * 40,
                  detail={"builder": "FOUNDRY", "build_id": "X.e"})
    pend, why = w.p.build(w.task, sh(w.root, "git", "rev-parse", "HEAD"))
    return pend is not None and w.calls[0][0] == "build"


def sc_same_id(tmp, mod, tag):
    """S: a constant id generator (builder == tester): refused, no test_start ever written."""
    w = World(tmp, "S" + tag, mod, arm="v3", new_id=lambda role: "agent-x")
    try:
        w.p.work(w.task)
    except (V.Refused, RA.Refused):
        pass
    return w.ev("test_start") == [] and [c[0] for c in w.calls] == ["build"]


def sc_refused_preflight(tmp, mod, tag):
    def pf(sandbox, cwd):
        raise RA.Refused("no bwrap")
    w = World(tmp, "R" + tag, mod, arm="v3", preflight=pf)
    try:
        w.p.work(w.task)
    except (V.Refused, RA.Refused):
        pass
    return w.ev("test_start") == [] and w.ev("build_end") != []


def sc_close_mismatch(tmp, mod, tag):
    """C: a CLOSED sha that is not HEAD, and a CLOSED with no commit: no build_end, the item comes back."""
    w = World(tmp, "C" + tag, mod, arm="v3", closed=lambda head: "0" * 40)
    pend, why = w.p.build(w.task, sh(w.root, "git", "rev-parse", "HEAD"))
    w2 = World(tmp, "C2" + tag, mod, arm="v3")
    head0 = sh(w2.root, "git", "rev-parse", "HEAD")
    w2.builder = lambda p: None
    w2.__class__ = type("NoCommit", (World,), {"__call__": lambda self, role, prompt, **k: (
        self.calls.append((role, k["agent_id"])) or {"rc": 0, "text": "CLOSED: %s" % head0})})
    pend2, why2 = w2.p.build(w2.task, head0)
    return pend is None and pend2 is None and w.ev("build_end") == [] and w2.ev("build_end") == []


MUTATIONS = [
    ("D require_tested removed from the build brief", sc_refuses_untested,
     [("require_tested(self.records(), self.arm)                  # HARD CHECK", "pass  # mut")]),
    ("D same-agent flag ignored", lambda t, m, g: sc_refuses_untested(t, m, g),
     [("    same = L.flagged_same_agent(mine)", "    same = []")]),
    ("O tester skipped and require_tested removed", sc_order,
     [("require_tested(self.records(), self.arm)                  # HARD CHECK", "pass  # mut"),
      ("verdict, text = self.test(task, pend)", "verdict, text = ('pass' if attempt > 1 else 'fail'), 'FAIL'")]),
    ("P replay scope (run_id prefix) removed", sc_production_does_not_block,
     [('and str(r.get("run_id", "")).startswith(pre)', "")]),
    ("S tester-id check removed", sc_same_id,
     [('if not RA.agent_key(tester) or RA.agent_key(tester) == RA.agent_key(pend["builder"]):', "if False:")]),
    ("R preflight after test_start", sc_refused_preflight,
     [("                if pf:\n                    pf(sandbox, work)\n", ""),
      ("timeout_s=self.timeout_s, log=self.log / (\"test.%d.%s.out\" % (self.n, tester)))",
       "timeout_s=self.timeout_s, log=self.log / (\"test.%d.%s.out\" % (self.n, tester))) if not pf(sandbox, work) "
       "else None")]),
    ("C CLOSED/HEAD match removed", sc_close_mismatch,
     [('elif not head.startswith(closed[-1].lower()):', "elif False:"),
      ('elif head == before:', "elif False:")]),
    ("W close gate bypassed in work()", sc_review_fail_never_closes,
     [('ok, why = self.close(task, pend["head"])', 'ok, why = True, "mut"')]),
    ("W tester verdict ignored before review", sc_tester_fail_no_review,
     [('                if verdict != "pass":\n', '                if False:\n')]),
]


def guarded(fn, tmp, mod, tag):
    try:
        return bool(fn(tmp, mod, tag))
    except Exception as e:  # noqa: BLE001
        print("     (%s raised %s: %s)" % (fn.__name__, type(e).__name__, str(e)[:200]))
        return False


def t_gate(tmp):
    res = sc_gate(tmp, V, "")
    check(res["good"], "G green: the good sha passes the done gate")
    for name, _, _ in GATE_CASES:
        ok, why = res[name]
        check(not ok and why.startswith("refused"), "G green: refused for %s (%s)" % (name, why[:90]))
    for i, (name, fn, muts) in enumerate(GATE_CASES):
        m = variant(muts)
        w, sha = _good_v3c(tmp, "Gm%d" % i, m)
        r2, s2 = fn(w.recs(), w, sha)
        ok, _ = m.done_gate(r2, "v3c", TASK["id"], s2, w.p.reviews)
        check(ok, "G mutation goes RED (the gate lets it through) when its refusal is reverted: " + name)


def t_briefs(tmp):
    w3 = World(tmp, "B3", V, arm="v3")
    w3c = World(tmp, "B3c", V, arm="v3c")
    b3, b3c = w3.p.brief(TASK, ""), w3c.p.brief(TASK, "why")
    check("gpt_consult.py" in b3 and "Do not run a GPT review yourself" in b3c and "{{" not in b3 + b3c
          and TASK["criteria"] in b3 and "CLOSED:" in b3 and "WHY THIS ITEM IS BACK" in b3c,
          "the v3 brief keeps today's review step, v3c's hands it to the program; spec and close line present")
    w = World(tmp, "BT", V, arm="v3")
    w.p.work(w.task)
    tp = [p for role, p in w.prompts if role == "test"][0]
    check("VERDICT: PASS" in tp and "## DIFF" in tp and "built\nCLOSED" not in tp,
          "the tester brief carries spec, plan and diff, and nothing the build helper wrote")


def t_live(tmp):
    w = World(tmp, "LV", V, arm="v3c", task=dict(TASK, live="lane"))
    out = w.p.work(w.task)
    check(out["outcome"] == "live_owed" and w.reviews == [] and [c[0] for c in w.calls] == ["build", "test"],
          "a live task stops at live_owed after its tester; v3c does not close it")


def t_signed_writer(tmp):
    root = tmp / "arena"
    os.environ["ARENA_ROOT"] = str(root)
    os.environ["ARENA_CLONES"] = str(root / "clones")
    os.environ["ARENA_EVENT_TOKEN_FILE"] = str(tmp / "secret" / "event_token")
    os.environ["ARENA_ANCHOR_FILE"] = str(tmp / "secret" / "anchors.jsonl")
    os.environ["ARENA_WITNESS"] = str(tmp / "secret" / "witness.jsonl")
    p = A.paths()
    L.init_token(p)
    check("v3_control.py" in L.ENTRYPOINTS, "v3_control.py may open a pass capability (arena_eventlog.ENTRYPOINTS)")
    for arm in V.ARMS:
        sw = V.SignedWriter(arm, p)
        w = World(tmp, "H" + arm, V, arm=arm, writer=sw, builder=lambda pr: GOOD if "FAIL" in pr else WEAK)
        out = w.p.work(w.task)
        acc = sw.records()
        ev = [r["event"] for r in acc if r["event"] in ("build_end", "test_start", "test_end")]
        check(out["outcome"] == ("closed" if arm == "v3" else "done") and L.untested_builds(acc) == []
              and L.flagged_same_agent(acc) == [] and ev == ["build_end", "test_start", "test_end"] * 2
              and all(r["run_id"].startswith(arm + ".replay.") and r["lane"] == "replay" for r in acc)
              and (arm == "v3" or V.done_gate(acc, arm, TASK["id"], out["sha"], w.p.reviews)[0]),
              "signed HarnessWriter log (%s): %s, every build tested by a different agent before the next" % (arm, ev))


def _replace_ref_world(tmp, name):
    """A clone whose HEAD (WEAK) carries a builder-installed replace ref to a GOOD commit."""
    w = World(tmp, name, V, arm="v3")
    (w.root / "mod.py").write_text(GOOD)
    sh(w.root, "git", "add", "mod.py")
    sh(w.root, "git", "commit", "-q", "-m", "good")
    good = sh(w.root, "git", "rev-parse", "HEAD")
    (w.root / "mod.py").write_text(WEAK)
    sh(w.root, "git", "commit", "-q", "-am", "weak")
    bad = sh(w.root, "git", "rev-parse", "HEAD")
    sh(w.root, "git", "replace", bad, good)
    return w, bad


def sc_replace_ref(tmp, mod, tag):
    """the tester's export and the reviewed diff of sha A are A's, whatever replace ref the builder planted."""
    w, bad = _replace_ref_world(tmp, "RR" + tag)
    dest = mod.export_tree(w.root, bad, tmp / ("RRx" + tag))
    diff = mod.safe_git(w.root, "show", "--no-ext-diff", "--no-textconv", bad)
    return (dest / "mod.py").read_text() == WEAK and "return a - b" in diff


def sc_pinned(tmp, mod, tag):
    """the reviewer script runs only as committed: a rewritten copy is refused."""
    h = tmp / ("PIN" + tag)
    (h / "src").mkdir(parents=True)
    for a in (("init", "-q", "-b", "main"), ("config", "user.email", "t@t"), ("config", "user.name", "t")):
        sh(h, "git", *a)
    (h / "src" / "rev.py").write_text("print('VERDICT: FAIL')\n")
    sh(h, "git", "add", "src/rev.py")
    sh(h, "git", "commit", "-q", "-m", "rev")
    saved = mod.HARNESS_REPO
    mod.HARNESS_REPO = h
    try:
        ok = mod.pinned_harness_file("src/rev.py") == h / "src" / "rev.py"
        (h / "src" / "rev.py").write_text("print('VERDICT: PASS')\n")
        try:
            mod.pinned_harness_file("src/rev.py")
            return False
        except (V.Refused, RA.Refused):
            return ok
    finally:
        mod.HARNESS_REPO = saved


def sc_export_attrs(tmp, mod, tag):
    """export-ignore / export-subst in the builder's .gitattributes do not change the tester's tree. Sanity: the
    same sha through `git archive` does lose the file (so the probe can see the trap)."""
    w = World(tmp, "EA" + tag, mod, arm="v3")
    (w.root / "mod.py").write_text(WEAK)
    (w.root / "v.txt").write_text("$Format:%H$\n")
    (w.root / ".gitattributes").write_text("mod.py export-ignore\nv.txt export-subst\n")
    sh(w.root, "git", "add", "mod.py", "v.txt", ".gitattributes")
    sh(w.root, "git", "commit", "-q", "-m", "attrs")
    sha = sh(w.root, "git", "rev-parse", "HEAD")
    names = subprocess.run(["git", "-C", str(w.root), "archive", "--format=tar", sha], capture_output=True).stdout
    import tarfile, io
    lost = "mod.py" not in tarfile.open(fileobj=io.BytesIO(names)).getnames()
    dest = mod.export_tree(w.root, sha, tmp / ("EAx" + tag))
    return (lost and (dest / "mod.py").read_text() == WEAK and (dest / "v.txt").read_text() == "$Format:%H$\n")


def sc_review_needs_tester(tmp, mod, tag):
    """v3c: review() of a built but untested sha is refused and the reviewer never runs."""
    w = World(tmp, "RT" + tag, mod, arm="v3c")
    pend, _ = w.p.build(w.task, sh(w.root, "git", "rev-parse", "HEAD"))
    try:
        w.p.review(w.task, pend)
        return False
    except (V.Refused, RA.Refused):
        return w.reviews == [] and w.ev("critic_round") == []


def sc_one_lock_per_arm(tmp, mod, tag):
    """two procedures of one arm with different --ctl share the lock: the second is refused."""
    import fcntl
    common = tmp / ("LK" + tag)
    common.mkdir(parents=True, exist_ok=True)
    held = open(common / "v3.lock", "w")
    fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        w = World(tmp, "LKw" + tag, mod, arm="v3", lock_dir=common)
        try:
            w.p.work(w.task)
            return False
        except (V.Refused, RA.Refused) as e:
            return "holds" in str(e) and w.calls == []
    finally:
        held.close()


def t_ordered_probe(tmp):
    """sanity: the ordering assertion sees a brief that comes before the tester's test_start."""
    w = World(tmp, "OP", V, arm="v3")
    seed_build(w, task=TASK["id"])
    w.writer.emit("v3", "pass_start", lane="replay", run_id="v3.replay.1", task=TASK["id"],
                  detail={"role": "build", "agent": "b2"})
    early = _ordered_ok(w)
    w.writer.recs.insert(1, dict(w.writer.recs[0], event="test_start", detail={"tester": "t1",
                                                                              "build_id": "x"}))
    check(not early and _ordered_ok(w), "the ordering probe flags a build brief before the test_start, and only "
                                        "then (instrument can see)")


MUTATIONS += [
    ("RT review without the tester record", sc_review_needs_tester,
     [("        if not ok:                                                # the review requires", "        if False:  #")]),
    ("LK lock follows --ctl", sc_one_lock_per_arm,
     [('self.lock_dir = Path(lock_dir or os.environ.get("V3_LOCK_DIR") or DEFAULT_CTL)', "self.lock_dir = self.ctl")]),
    ("RR replace refs honoured", sc_replace_ref, [('"GIT_NO_REPLACE_OBJECTS": "1", ', "")]),
    ("PIN reviewer pin removed", sc_pinned,
     [("    if want.returncode or have.returncode or want.stdout.strip() != have.stdout.strip():", "    if False:")]),
]


def main():
    tmp = Path(tempfile.mkdtemp(prefix="selftest_v3_control_"))
    TBASE[0] = Path(tempfile.mkdtemp(prefix="selftest_v3_control_rt_"))
    saved = {k: os.environ.get(k) for k in ("ARENA_ROOT", "ARENA_CLONES", "ARENA_EVENT_TOKEN_FILE",
                                             "ARENA_ANCHOR_FILE", "ARENA_WITNESS", "RM_ARM")}
    os.environ.pop("RM_ARM", None)
    try:
        for name, fn in (("W v3c failing review never closes", sc_review_fail_never_closes),
                         ("W v3c passing tester + review is done", sc_review_pass_done),
                         ("W v3c tester FAIL never reaches review", sc_tester_fail_no_review),
                         ("D brief refused without a different-agent test_start", sc_refuses_untested),
                         ("O no brief before the tester's test_start", sc_order),
                         ("P production v3 records do not block", sc_production_does_not_block),
                         ("S tester id never the builder's", sc_same_id),
                         ("R refused preflight logs no test_start", sc_refused_preflight),
                         ("C CLOSED must be the commit", sc_close_mismatch),
                         ("RR a planted replace ref does not change what is tested", sc_replace_ref),
                         ("PIN a rewritten reviewer script is refused", sc_pinned),
                         ("EA builder attributes do not change the tested tree", sc_export_attrs),
                         ("RT v3c review requires the tester record", sc_review_needs_tester),
                         ("LK one lock per arm", sc_one_lock_per_arm)):
            check(guarded(fn, tmp, V, ""), "green: " + name)
        for i, (name, fn, muts) in enumerate(MUTATIONS):
            check(not guarded(fn, tmp, variant(muts), "_m%d" % i), "mutation goes RED: " + name)
        for fn in (t_gate, t_briefs, t_live, t_ordered_probe, t_signed_writer):
            try:
                fn(tmp)
            except Exception as e:  # noqa: BLE001
                check(False, "%s crashed: %s: %s" % (fn.__name__, type(e).__name__, e))
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(TBASE[0], ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
