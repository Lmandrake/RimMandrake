#!/usr/bin/env python3
"""selftest_arena_spend.py - the REAL writers feed arena_analysis.py a measured verdict; dropping one makes it
UNMEASURED.

    python3 src/RimMandrake/Utils/arena/selftest_arena_spend.py

No model calls. Writes only under a temp dir (ARENA_ROOT, the event token, anchors, witness, judge work, private arm
map, fake transcripts and a fake gpt call log all point there).

  units      arena_spend.spans_of / attribute: a call inside one task's span is that task's (raw per-model counts and
             raw GPT tokens kept apart), inside two tasks' spans it is ambiguous (counted, tokens on neither), inside
             none it is overhead; gate/judge events never stretch a span; a meter bucket with no log is overhead.
  e2e        two arms x 20 tasks: the loop events are signed by arena_eventlog.HarnessWriter; T000 of each arm is judged
             by the real arena_judge.judge() (bwrap sandbox, hidden check, fake judges) with the recorder main() uses
             (arena_judge.record_judge_event), the rest through that same recorder; arena_judge.main()'s own wiring
             is driven once (gate-fail path, no sandbox); fake Claude transcripts under <clones>/<arm> slugs and a fake
             gpt call log go through the real meter (spend_census) via arena_spend.meter(); arena_analysis reads the
             signed logs through ledger anchors and DECIDES (not UNMEASURED); the CLI pair (arena_spend.py ->
             arena_analysis.py run) agrees.
  mutations  no judge recorder -> UNMEASURED; meter sinks dropped -> UNMEASURED; no spend file -> UNMEASURED (exit 3);
             the derived claude_ite alone (raw counts dropped) -> UNMEASURED.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import math
import os
import random
import shutil
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "sim"))
sys.path.insert(0, str(HERE.parent))
import arena_analysis as AA  # noqa: E402
import arena_eventlog as L  # noqa: E402
import arena_judge as J  # noqa: E402
import arena_spend as SP  # noqa: E402
import arena_tasks as A  # noqa: E402
import selftest_arena_judge as SJ  # noqa: E402   fixtures only (make_clone, task_for, hidden_for, Fake, ans)
import spend_census as S  # noqa: E402

FAILS = []
OPUS = "claude-opus-5-5"
N = 20
ARMS = ("trio", "v3")
T0 = int(time.time()) - 3 * 86400          # loop events in the past; judge events are stamped at write time (now)


def check(ok, msg, detail=""):
    print(("PASS  " if ok else "FAIL  ") + msg + ("" if ok else "  [%s]" % (detail,)))
    if not ok:
        FAILS.append(msg)


def iso(e):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(e))


# ------------------------------------------------------------------ units

def t_units():
    recs = [{"ts": iso(1000), "run_id": "r.0", "task": "A", "event": "pass_start"},
            {"ts": iso(1100), "run_id": "r.0", "task": "A", "event": "test_start"},
            {"ts": iso(1900), "run_id": "r.0", "task": "A", "event": "gate"},          # harness: no stretch
            {"ts": iso(2000), "run_id": "r.0", "task": "A", "event": "judge"},         # harness: no stretch
            {"ts": iso(1050), "run_id": "r.1", "task": "B", "event": "pass_start"},    # overlaps A
            {"ts": iso(1300), "run_id": "r.1", "task": "B", "event": "pass_end"},
            {"ts": iso(5000), "run_id": "r.2", "task": "C", "event": "pass_start"},
            {"ts": iso(5100), "run_id": "r.2", "task": "C", "event": "pass_end"},
            {"ts": iso(9000), "run_id": "x", "event": "switch"}]
    sp = SP.spans_of(recs)
    check(sp == [(1000.0, 1100.0, "A"), (1050.0, 1300.0, "B"), (5000.0, 5100.0, "C")],
          "spans: [first, last] per (run_id, task); gate/judge events and task-less events do not stretch them", sp)

    def cc(t, **kw):
        c = {"t": t, "model": OPUS, "in": 0, "cr": 0, "c5": 0, "c1": 0, "out": 0, "ite": 0.0}
        c.update(kw)
        return c
    claude = [("trio", cc(5050, **{"in": 100, "cr": 1000, "c5": 8, "c1": 5, "out": 10}, ite=270.0)),
              ("trio", cc(5060, model="claude-sonnet-4-5", **{"in": 1000}, ite=600.0)),
              ("trio", cc(1070, **{"in": 7})),            # inside A and B: ambiguous
              ("trio", cc(3000, **{"in": 9})),            # between tasks: overhead
              ("HARNESS", cc(5050, **{"in": 11}))]        # the judge's own spend: never a task's
    gpt = [("trio", {"t": 5070, "arm": "trio", "tokens_used": 50}),
           ("trio", {"t": 5080, "arm": "trio", "in_tok_est": 40, "out_tok_est": 10})]
    doc = SP.attribute({"trio": {"recs": recs}, "v3": {"unmeasured": "x"}}, claude, gpt)
    c = doc["arms"]["trio"].get("C", {})
    check(c.get("claude", {}).get(OPUS) == {"input": 100, "cache_read": 1000, "cache_write_5m": 8,
                                            "cache_write_1h": 5, "output": 10}
          and c["claude"].get("claude-sonnet-4-5", {}).get("input") == 1000,
          "raw Claude counts are kept PER MODEL, unweighted", c.get("claude"))
    check(c.get("gpt") == {"tokens": 50.0, "in_est": 40.0, "out_est": 10.0, "calls": 2, "est_calls": 1},
          "raw GPT tokens (real total and in/out estimates) kept apart from Claude", c.get("gpt"))
    check(c.get("claude_ite") == 870.0, "claude_ite is carried only as the derived column", c.get("claude_ite"))
    tok, why = AA.task_tokens(c, AA.default_conv())
    check(tok == 270 + 600 + 50 + 90, "the analysis weights the raw row itself: 270 + 600 + 50 + 90 = 1010", (tok, why))
    a, b = doc["arms"]["trio"].get("A", {}), doc["arms"]["trio"].get("B", {})
    check(a.get("ambiguous_calls") == 1 and b.get("ambiguous_calls") == 1 and not a.get("claude")
          and not b.get("claude"), "a call inside two tasks' spans is ambiguous on both, its tokens on neither",
          (a, b))
    check(AA.task_tokens(a, AA.default_conv())[0] is None, "the analysis refuses an ambiguous task")
    check(doc["overhead"].get("trio", {}).get("claude", {}).get(OPUS, {}).get("input") == 9
          and doc["overhead"].get("HARNESS", {}).get("claude", {}).get(OPUS, {}).get("input") == 11,
          "calls in no span, and harness spend, are overhead", doc["overhead"])
    check(any("ambiguous" in f for f in doc["flags"]) and any("v3" in f and "UNMEASURED" in f for f in doc["flags"]),
          "ambiguity and an UNMEASURED arm log are flagged", doc["flags"])
    t_units_r1(recs, cc)


def t_units_r1(recs, cc):
    """GPT review r1 findings 2, 3, 5, 7 at unit level."""
    # (2) a reused (run_id, task) is two executions: a span closes at pass_end
    rr = [{"ts": iso(100), "run_id": "r", "task": "A", "event": "pass_start"},
          {"ts": iso(150), "run_id": "r", "task": "A", "event": "pass_end"},
          {"ts": iso(300), "run_id": "r", "task": "A", "event": "pass_start"},
          {"ts": iso(350), "run_id": "r", "task": "A", "event": "pass_end"}]
    sp = SP.spans_of(rr)
    check(sp == [(100.0, 150.0, "A"), (300.0, 350.0, "A")], "r1#2: a reused (run_id, task) gives one span per "
          "execution (closed at pass_end), not one span across the idle gap", sp)
    d = SP.attribute({"trio": {"recs": rr}}, [("trio", cc(250, **{"in": 5})), ("trio", cc(120, **{"in": 3}))], [])
    check(d["overhead"].get("trio", {}).get("claude", {}).get(OPUS, {}).get("input") == 5
          and d["arms"]["trio"]["A"]["claude"][OPUS]["input"] == 3,
          "r1#2: a call in the idle gap between two executions is overhead", d)
    # (5) every per-call count is validated BEFORE it is summed
    for name, bad in (("bool", True), ("negative", -20), ("float", 1.5), ("nan", float("nan")), ("str", "7")):
        d = SP.attribute({"trio": {"recs": recs}},
                         [("trio", cc(5050, **{"in": 100})), ("trio", cc(5060, **{"in": bad}))], [])
        row = d["arms"]["trio"]["C"]
        tok, why = AA.task_tokens(row, AA.default_conv())
        check(row.get("invalid_calls") == 1 and tok is None and "invalid" in (why or ""),
              "r1#5: a %s Claude count in one call marks the task invalid_calls and the analysis refuses it" % name,
              (row, why))
    for name, g in (("tokens_used bool", {"tokens_used": True}), ("tokens_used neg", {"tokens_used": -5}),
                    ("est neg", {"in_tok_est": 40, "out_tok_est": -10}), ("est bool", {"in_tok_est": True})):
        d = SP.attribute({"trio": {"recs": recs}}, [("trio", cc(5050, **{"in": 100}))], [("trio", dict(g, t=5070))])
        row = d["arms"]["trio"]["C"]
        check(row.get("invalid_calls") == 1 and AA.task_tokens(row, AA.default_conv())[0] is None,
              "r1#5: a GPT call with %s marks the task invalid" % name, row)
    d = SP.attribute({"trio": {"recs": recs}}, [("trio", {"model": OPUS, "in": 5})], [])
    check(d.get("blocking"), "r1#5: a metered call with no time is blocking, not silent overhead", d.get("blocking"))
    # (7) a present Claude section that is not a dict is refused, never ignored and never a crash
    for cl in ([], [1], "x", 0):
        try:
            tok, why = AA.task_tokens({"claude": cl, "gpt": {"tokens": 50}}, AA.default_conv())
        except Exception as e:                              # noqa: BLE001
            tok, why = "crash", repr(e)
        check(tok is None, "r1#7: claude=%r is refused" % (cl,), (tok, why))
    # (3) meter diagnostics are blocking, not report-only flags
    real = S.claude_spend_by_arm
    for key, val in (("unreadable_files", ["x.jsonl: boom"]), ("id_conflicts", {"m1": ["trio", "v3"]}),
                     ("cwd_mismatch", ["x"]), ("bad_lines", {"x.jsonl": 2})):
        def fake(*a, diag=None, sink=None, _k=key, _v=val, **k):
            diag[_k] = _v
            return {}
        S.claude_spend_by_arm = fake
        try:
            d = SP.meter({"trio": {"recs": recs}}, projects="/nonexistent", clones_root="/nonexistent",
                         gpt_log="/nonexistent/g.jsonl")
        finally:
            S.claude_spend_by_arm = real
        prob = AA.spend_doc_problem(d, {"trio": {"recs": recs}})
        check(any(key in b for b in d.get("blocking", ())) and prob and key in prob,
              "r1#3: meter %s is blocking and the analysis refuses the spend doc" % key, (d.get("blocking"), prob))


# ------------------------------------------------------------------ e2e

def setup_env(tmp, name):
    root = tmp / name
    env = dict(ARENA_ROOT=str(root / "arena"), ARENA_CLONES=str(root / "clones"), ARENA_PRIVATE=str(root / "private"),
               ARENA_JUDGE_WORK=str(root / "work"), ARENA_EVENT_TOKEN_FILE=str(root / "secret" / "event_token"),
               ARENA_ANCHOR_FILE=str(root / "secret" / "anchors.jsonl"),
               ARENA_WITNESS=str(root / "secret" / "witness.jsonl"), ARENA_JUDGE_OPUS_MODEL="fake-model-for-selftest",
               RM_GPT_CALL_LOG=str(root / "gpt_calls.jsonl"))
    os.environ.update(env)
    for k in ("ARENA_ROOT", "ARENA_CLONES", "ARENA_JUDGE_WORK"):
        Path(env[k]).mkdir(parents=True)
    p = A.paths()
    L.init_token(p)
    return root, p


def tasks_spec():
    return {"T%03d" % i: {"kind": A.KINDS[i % 2], "size": (1, 2, 4)[i % 3]} for i in range(N)}


def task_cost():
    rng = random.Random(11)
    return {"T%03d" % i: math.exp(math.log(1e5) + rng.gauss(0, 1.0)) for i in range(N)}


def build(tmp, name, *, judge_writer=True, sinks=True, raw_counts=True, pending=False, id_conflict=False,
          stale=False, since_cut=False):
    """One miniature arena run through the real writers. -> dict with the analysis report and paths."""
    root, p = setup_env(tmp, name)
    w = L.HarnessWriter(p)                                  # the selftest's implicit harness pass
    rec = (lambda arm, base, head: (lambda r: J.record_judge_event(w, arm=arm, base=base, head=head, rec=r))) \
        if judge_writer else (lambda arm, base, head: None)
    cost, specs = task_cost(), tasks_spec()
    clones_root = Path(os.environ["ARENA_CLONES"])
    projects = root / "projects"
    heads, judged = {}, {}
    for arm in ARMS:
        c, base, head = SJ.make_clone(clones_root / "repl", arm, 2, plant=False)
        heads[arm] = (c, base, head)
    gpt_lines, tr = [], {}
    for arm in ARMS:
        off = 0 if arm == "trio" else 7
        for i in range(N):
            task = "T%03d" % i
            t = T0 + off + i * 600
            sha = heads[arm][2] if i == 0 else hashlib.sha1(("%s/%s" % (arm, task)).encode()).hexdigest()
            rid, b = "%s.%d" % (arm, i), "b-%s-%d" % (arm, i)
            for ev, dt_, more in (("assign", 0, {}), ("pass_start", 10, {"detail": {"role": "build", "agent": b}}),
                                  ("build_end", 100, {"sha": sha, "detail": {"builder": b, "build_id": "bid%d" % i}}),
                                  ("test_start", 110, {"detail": {"tester": "q-%s-%d" % (arm, i),
                                                                  "build_id": "bid%d" % i}}),
                                  ("pass_end", 150, {"sha": sha, "verdict": "pass"}),
                                  ("gate", 200, {"sha": sha, "verdict": "pass", "detail": {"steps": {"scope": "PASS"}}})):
                w.emit(arm, ev, lane="build", run_id=rid, ts=iso(t + dt_), task=task, **more)
            tok = cost[task] * (0.25 if arm == "trio" else 1.0)
            tr.setdefault(arm, []).append({"type": "assistant", "timestamp": iso(t + 50),
                                           "message": {"id": "m-%s-%d" % (arm, i), "model": OPUS,
                                                       "usage": {"input_tokens": int(tok), "output_tokens": 0}}})
            tr[arm].append({"type": "assistant", "timestamp": iso(t + 400),          # between tasks: overhead
                            "message": {"id": "o-%s-%d" % (arm, i), "model": OPUS,
                                        "usage": {"input_tokens": 999, "output_tokens": 0}}})
            gpt_lines.append({"t": t + 60, "arm": arm, "tokens_used": 100})
    for arm in ARMS:
        (clones_root / arm).mkdir(exist_ok=True)          # the meter lists the clones root to name arms
        d = projects / S.path_slug(str(clones_root / arm))
        d.mkdir(parents=True)
        lines = tr[arm] + ([tr["trio"][10]] if (id_conflict and arm == "v3") else [])   # one id under two arms
        (d / "s.jsonl").write_text("".join(json.dumps(x) + "\n" for x in lines))
    Path(os.environ["RM_GPT_CALL_LOG"]).write_text("".join(json.dumps(x) + "\n" for x in gpt_lines))
    # judging: T000 of each arm through the real judge(), the rest through the same recorder main() uses
    for arm in ARMS:
        c, base, head = heads[arm]
        fk = [SJ.Fake(SJ.ans("accept")) for _ in range(3)]
        r = J.judge(task=SJ.task_for("T000"), hidden=SJ.hidden_for("T000"), clone=c, base=base, head=head, arm=arm,
                    gate=dict(SJ.GATE, arm=arm), judges=J.Judges(*fk), p=p, record=rec(arm, base, head))
        judged[arm] = r["verdict"]
        for i in range(1, N):
            task = "T%03d" % i
            sha = hashlib.sha1(("%s/%s" % (arm, task)).encode()).hexdigest()
            fn = rec(arm, "base", sha)
            if fn:
                fn({"task": task, "verdict": "accept"})
        if pending and arm == "trio":     # r1#6: a re-judgment started, its verdict never appended
            J.record_judge_event(w, arm=arm, base="base", head=hashlib.sha1(b"trio/T005").hexdigest(),
                                 rec={"task": "T005", "verdict": "invalid"}, pending=True)
    anchors = [w._cap.last_anchor[a] for a in ARMS if a in w._cap.last_anchor]
    ext = L.ledger_anchors([{"event": "note", "text": L.anchor_note_text(anchors)}])
    logs = AA.load_verified(p, None, ext)
    real_census = (S.claude_spend_by_arm, S.gpt_spend_by_arm)
    if not sinks:                                            # mutation: the meter no longer feeds the attribution
        S.claude_spend_by_arm = lambda *a, sink=None, **k: real_census[0](*a, **k)
        S.gpt_spend_by_arm = lambda *a, sink=None, **k: real_census[1](*a, **k)
    try:
        doc = SP.meter(logs, projects=str(projects), clones_root=str(clones_root), gpt_log=None,
                       since=(T0 + 30) if since_cut else None)   # cuts no call: only the window check can see it
    finally:
        S.claude_spend_by_arm, S.gpt_spend_by_arm = real_census
    if not raw_counts:                                       # mutation: only the derived column survives
        for rows in doc["arms"].values():
            for row in rows.values():
                row.pop("claude", None)
                row.pop("gpt", None)
    if stale:                                                # r1#4: the log moved on after the spend was metered
        w.emit("trio", "pass_start", lane="build", run_id="trio.retry", ts=iso(T0 + N * 600 + 50), task="T003")
        anchors = [w._cap.last_anchor[a] for a in ARMS if a in w._cap.last_anchor]
        ext = L.ledger_anchors([{"event": "note", "text": L.anchor_note_text(anchors)}])
        logs = AA.load_verified(p, None, ext)
    rep = AA.analyse_spend_doc(logs, specs, doc, draws=2000)
    return {"root": root, "p": p, "logs": logs, "doc": doc, "rep": rep, "judged": judged, "specs": specs,
            "projects": projects, "clones_root": clones_root}


def t_e2e(tmp):
    r = build(tmp, "base")
    check(r["judged"] == {"trio": "accept", "v3": "accept"},
          "control: the real judge() accepted T000 in both arms (sandbox + hidden check ran)", r["judged"])
    for arm in ARMS:
        recs = r["logs"].get(arm, {}).get("recs", [])
        js = [x for x in recs if x["event"] == "judge"]
        check(len(js) == N and all(x.get("lane") == "judge" and x.get("verdict") == "accept" and x.get("sha")
                                   for x in js),
              "%s: %d signed judge events, verdict + sha, from the recorder" % (arm, N), (len(js), r["logs"].get(arm)))
        blob = json.dumps(js)
        check("votes" not in blob and "arm_guess" not in blob and "judge_id" not in blob,
              "%s: judge events carry no judge_id, votes or arm guesses" % arm, blob[:300])
    rows = r["doc"]["arms"]
    check(all(len(rows.get(a, {})) == N for a in ARMS), "the meter attributed spend to every task of both arms",
          {a: len(rows.get(a, {})) for a in ARMS})
    one = rows.get("trio", {}).get("T005", {})
    check(set(one.get("claude", {})) == {OPUS} and one["claude"][OPUS]["input"] == int(task_cost()["T005"] * 0.25)
          and one["gpt"]["tokens"] == 100 and one.get("ambiguous_calls") == 0,
          "a task row holds the raw per-model Claude input and the raw GPT tokens of that task only", one)
    check(r["doc"]["overhead"].get("trio", {}).get("claude", {}).get(OPUS, {}).get("input") == 999 * N,
          "calls between tasks land in the arm's overhead, not in a task", r["doc"]["overhead"].get("trio"))
    check(r["doc"].get("schema") == "arena_task_spend/2" and r["doc"].get("blocking") == []
          and set(r["doc"].get("logs", {})) == set(ARMS) and AA.spend_doc_problem(r["doc"], r["logs"]) is None,
          "the spend doc is schema /2, binds each arm's analysed log and has no blocking problem",
          (r["doc"].get("schema"), r["doc"].get("blocking"), r["doc"].get("logs")))
    v = r["rep"]["final"]["verdict"]
    check(v == "DECIDE_FOR_trio", "analysis on the real writers' output is MEASURED and decides (cheaper arm wins)",
          r["rep"]["final"])
    # the CLI pair, untrusted mode (no ledger here): arena_spend.py -> SPEND.json -> arena_analysis.py run
    td = r["root"] / "tasks_dir"
    td.mkdir()
    for t, s in r["specs"].items():
        (td / (t + ".json")).write_text(json.dumps(dict(s, id=t)))
    out = r["root"] / "spend.json"
    with contextlib.redirect_stdout(io.StringIO()):
        rc1 = SP.main(["--out", str(out), "--allow-untrusted", "--projects", str(r["projects"]),
                       "--clones-root", str(r["clones_root"])])
        rc2 = AA.main(["run", "--spend", str(out), "--tasks-dir", str(td), "--allow-untrusted", "--draws", "2000",
                       "--out", str(r["root"] / "rep.json")])
        rc3 = AA.main(["run", "--spend", str(r["root"] / "missing.json"), "--tasks-dir", str(td),
                       "--allow-untrusted", "--draws", "2000"])
    rep2 = json.loads((r["root"] / "rep.json").read_text()) if (r["root"] / "rep.json").is_file() else {}
    check(rc1 == 0 and json.loads(out.read_text()).get("schema") == AA.SPEND_SCHEMA, "CLI: arena_spend.py writes the "
          "schema file", rc1)
    check(rc2 == 0 and rep2.get("final", {}).get("verdict") == "DECIDE_FOR_trio"
          and rep2.get("spend_overhead", {}).get("trio"),
          "CLI: arena_analysis.py run on it decides, and reports the overhead", (rc2, rep2.get("final")))
    check(rc3 == 3, "mutation: no spend file -> UNMEASURED, exit 3", rc3)


def t_main_wiring(tmp):
    """arena_judge.main() itself opens the signed writer and passes the recorder (gate-fail path: no sandbox)."""
    root, p = setup_env(tmp, "mainw")
    c, base, head = SJ.make_clone(Path(os.environ["ARENA_CLONES"]), "trio", 2, plant=False)
    gate = root / "gate.json"
    gate.write_text(json.dumps(dict(SJ.GATE, verdict="fail", arm="trio")))
    real = J.judge_task
    J.judge_task = lambda tid, **kw: J.judge(task=SJ.task_for(tid), hidden=None, **kw)   # no frozen task store here
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            rc = J.main(["judge", "--task", "T042", "--clone", str(c), "--base", base, "--head", head, "--arm", "trio",
                         "--gate", str(gate)])
    finally:
        J.judge_task = real
    recs = L.verify(p, "trio")["accepted"]
    js = [x for x in recs if x["event"] == "judge"]
    check(rc == 0 and len(js) == 2 and js[0].get("detail", {}).get("pending") is True
          and js[-1]["task"] == "T042" and js[-1]["verdict"] == "reject" and js[-1]["sha"] == head
          and not js[-1].get("detail", {}).get("pending"),
          "arena_judge.main() writes a signed PENDING judge event before judging, then the verdict (task, sha=head)",
          (rc, js))
    # r1#6: the verdict append fails -> the pending marker stays last -> the analysis refuses the arm
    real_rec = J.record_judge_event
    calls = []

    def flaky(w, **kw):
        calls.append(kw.get("pending"))
        if not kw.get("pending"):
            raise L.EventLogError("disk full (selftest)")
        return real_rec(w, **kw)
    J.record_judge_event, J.judge_task = flaky, (lambda tid, **kw: J.judge(task=SJ.task_for(tid), hidden=None, **kw))
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            try:
                rc = J.main(["judge", "--task", "T042", "--clone", str(c), "--base", base, "--head", head,
                             "--arm", "trio", "--gate", str(gate)])
            except L.EventLogError:
                rc = "raised"
    finally:
        J.record_judge_event, J.judge_task = real_rec, real
    js = [x for x in L.verify(p, "trio")["accepted"] if x["event"] == "judge"]
    check(rc != 0 and js and js[-1].get("detail", {}).get("pending") is True,
          "r1#6: a failed verdict append leaves the pending marker last (command fails)", (rc, js[-1:]))
    recs = L.verify(p, "trio")["accepted"]
    out, prob = AA.completions(recs, {"T042": {"kind": A.KINDS[0], "size": 1}}, {}, AA.default_conv())
    check(prob and "pending" in prob, "r1#6: a task whose last judge event is pending makes the arm a problem", prob)


def t_mutations(tmp):
    r = build(tmp, "nojudge", judge_writer=False)
    check(r["rep"]["final"]["verdict"] == "UNMEASURED",
          "mutation: judge recorder dropped -> UNMEASURED", r["rep"]["final"])
    r = build(tmp, "nosink", sinks=False)
    check(r["rep"]["final"]["verdict"] == "UNMEASURED" and not any(r["doc"]["arms"].values()),
          "mutation: meter sinks dropped -> no per-task spend -> UNMEASURED", r["rep"]["final"])
    for kw, what in (({"pending": True}, "r1#6 judge append failed after an earlier accept (pending marker last)"),
                     ({"id_conflict": True}, "r1#3 one message id under two arm folders"),
                     ({"stale": True}, "r1#4 the log moved on after the spend was metered"),
                     ({"since_cut": True}, "r1#4 the meter window cut the start of the log")):
        r = build(tmp, "m_" + next(iter(kw)), **kw)
        check(r["rep"]["final"]["verdict"].startswith("UNMEASURED"), "mutation: %s -> UNMEASURED" % what,
              r["rep"]["final"])
    r = build(tmp, "noraw", raw_counts=False)
    check(r["rep"]["final"]["verdict"] == "UNMEASURED",
          "mutation: raw counts dropped (derived claude_ite only) -> UNMEASURED", r["rep"]["final"])


def main():
    if not shutil.which("bwrap"):
        print("FAIL  bwrap not installed: the real judge cannot run")
        return 1
    keys = ("ARENA_ROOT", "ARENA_CLONES", "ARENA_PRIVATE", "ARENA_JUDGE_WORK", "ARENA_JUDGE_OPUS_MODEL",
            "ARENA_EVENT_TOKEN_FILE", "ARENA_ANCHOR_FILE", "ARENA_WITNESS", "RM_GPT_CALL_LOG", "ARENA_ARMS",
            "ARENA_ARM_TOKENS", "ANTHROPIC_DEFAULT_OPUS_MODEL")
    saved = {k: os.environ.get(k) for k in keys}
    tmp = Path(tempfile.mkdtemp(prefix="arena_spend_st_"))
    try:
        for k in ("ARENA_ARMS", "ARENA_ARM_TOKENS"):
            os.environ.pop(k, None)
        t_units()
        t_e2e(tmp)
        t_main_wiring(tmp)
        t_mutations(tmp)
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(tmp, ignore_errors=True)
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
