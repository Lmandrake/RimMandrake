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
import helper_capture as HC  # noqa: E402

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
    # BENCH B2: a span's end is INCLUSIVE (a call stamped exactly at pass_end is the task's, not overhead)
    d = SP.attribute({"trio": {"recs": recs}}, [("trio", cc(5100, **{"in": 13}))], [])
    check(d["arms"].get("trio", {}).get("C", {}).get("claude", {}).get(OPUS, {}).get("input") == 13,
          "B2: a call exactly at pass_end belongs to the task (span end inclusive)", d)
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
    # r2#1: equal timestamps keep signed (file) order: end@150 then start@150 is two executions
    rr2 = [{"ts": iso(100), "run_id": "r", "task": "A", "event": "pass_start"},
           {"ts": iso(150), "run_id": "r", "task": "A", "event": "pass_end"},
           {"ts": iso(150), "run_id": "r", "task": "A", "event": "pass_start"},
           {"ts": iso(200), "run_id": "r", "task": "A", "event": "pass_end"}]
    sp = SP.spans_of(rr2)
    check(sp == [(100.0, 150.0, "A"), (150.0, 200.0, "A")], "r2#1: an end and a new start at the same second keep "
          "their signed order (two executions, the call at 175 is the task's)", sp)
    # r2#4: an explicit null count is invalid, not zero; GPT with no real tokens needs its estimates
    d = SP.attribute({"trio": {"recs": recs}}, [("trio", cc(5050, **{"in": None, "out": 9}))], [])
    check(d["arms"]["trio"]["C"].get("invalid_calls") == 1, "r2#4: a Claude call with in=null is invalid",
          d["arms"]["trio"]["C"])
    for g, ok in (({"tokens_used": None}, False), ({}, False), ({"tokens_used": None, "in_tok_est": None,
                                                                "out_tok_est": 3}, False),
                  ({"tokens_used": None, "in_tok_est": 40, "out_tok_est": 10}, True)):
        d = SP.attribute({"trio": {"recs": recs}}, [("trio", cc(5050, **{"in": 100}))], [("trio", dict(g, t=5070))])
        row = d["arms"]["trio"]["C"]
        check((row.get("invalid_calls") == 0) == ok, "r2#4: GPT call %r is %s" % (g, "valid" if ok else "invalid"),
              row)
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
    for cl in ([], [1], "x", 0, None):
        try:
            tok, why = AA.task_tokens({"claude": cl, "gpt": {"tokens": 50}}, AA.default_conv())
        except Exception as e:                              # noqa: BLE001
            tok, why = "crash", repr(e)
        check(tok is None, "r1#7: claude=%r is refused" % (cl,), (tok, why))
    tok, why = AA.task_tokens({"claude": {OPUS: {"input": 10}}, "gpt": None}, AA.default_conv())
    check(tok is None, "r2#5: an explicit gpt=null section is refused", (tok, why))
    # r2#2: Claude spend under the arena root that the meter could not put on one arm is blocking; spend outside
    # the arena root (an unrelated session) stays overhead
    nots = [r for r in recs if r["event"] != "test_start"]
    real = S.claude_spend_by_arm
    for reasons, blocks in (({"unlisted": 5.0}, True), ({"ambiguous": 5.0}, True), ({"outside": 5.0}, False),
                            ({"tester_outside": 5.0}, True), ({"sandbox_foreign": 5.0}, True)):
        S.claude_spend_by_arm = lambda *a, _r=reasons, **k: {S.UNATTRIBUTED: {"ite": 5.0, "calls": 1, "reasons": _r}}
        try:
            d = SP.meter({"trio": {"recs": nots}}, projects="/nonexistent", clones_root="/nonexistent",
                         gpt_log="/nonexistent/g.jsonl", helpers="/nonexistent", sandbox_root="/nonexistent")
        finally:
            S.claude_spend_by_arm = real
        check(bool(d["blocking"]) == blocks, "r2#2: UNATTRIBUTED Claude spend for reason %s is %s" % (
            next(iter(reasons)), "blocking" if blocks else "overhead only"), d["blocking"])
    # (3) meter diagnostics are blocking, not report-only flags
    real = S.claude_spend_by_arm
    for key, val in (("unreadable_files", ["x.jsonl: boom"]), ("id_conflicts", {"m1": ["trio", "v3"]}),
                     ("cwd_mismatch", ["x"]), ("bad_lines", {"x.jsonl": 2})):
        def fake(*a, diag=None, sink=None, _k=key, _v=val, **k):
            diag[_k] = _v
            return {}
        S.claude_spend_by_arm = fake
        try:
            d = SP.meter({"trio": {"recs": nots}}, projects="/nonexistent", clones_root="/nonexistent",
                         gpt_log="/nonexistent/g.jsonl", helpers="/nonexistent", sandbox_root="/nonexistent")
        finally:
            S.claude_spend_by_arm = real
        prob = AA.spend_doc_problem(d, {"trio": {"recs": nots}})
        check(any(key in b for b in d.get("blocking", ())) and prob and key in prob,
              "r1#3: meter %s is blocking and the analysis refuses the spend doc" % key, (d.get("blocking"), prob))


def t_census(tmp):
    """spend_census pins (BENCH B13) and helper_capture's refusals, at unit level."""
    pj = tmp / "census" / "projects" / "-x"
    pj.mkdir(parents=True)
    mine = "/arena/replay/trio/T005"
    owner = "T005-%s-%s" % (hashlib.sha256(mine.encode()).hexdigest()[:8], "0" * 16)
    check(S._owns(owner, mine + "/src") and not S._owns(owner, "/arena/replay/v3/T005")
          and not S._owns(owner, "/elsewhere"), "sandbox owner: a scratch HOME is owned by its clone path (basename AND "
          "path hash); another arm's clone of the same task is not the owner", owner)
    line = lambda t, mid: json.dumps({"type": "assistant", "timestamp": iso(t), "message": {   # noqa: E731
        "id": mid, "model": OPUS, "usage": {"input_tokens": 10, "output_tokens": 0}}}) + "\n"
    (pj / "s.jsonl").write_text(line(1000, "in") + line(3000, "late"))
    seen = []
    S.claude_spend_by_arm(projects=str(pj.parent), arena_root="/nonexistent", since=500, until=2000,
                          sink=lambda a, c: seen.append(c["t"]))
    check(seen == [1000.0], "B13: the census sink sees only calls inside the window (filter before the sink)", seen)
    # capture: a symlinked projects dir / a symlinked HOME/.claude is never followed, and is reported as skipped
    rec = {"arm": "trio", "run_id": "r", "task": "T", "ts": iso(1000), "event": "test_start",
           "detail": {"tester": "x"}}
    base = tmp / "census" / "helpers"
    outside = tmp / "census" / "foreign"
    write_tester(outside, outside / "g", 1000, "trio", 0)
    for what, plant in (("projects", lambda h: (h / ".claude").mkdir(parents=True) or
                         (h / ".claude" / "projects").symlink_to(outside / ".claude" / "projects")),
                        (".claude", lambda h: h.mkdir(parents=True) or (h / ".claude").symlink_to(outside / ".claude"))):
        h = tmp / "census" / ("home_" + what)
        plant(h)
        HC.capture(rec, home=h, gpt_dir=None, base=base)
        man, d = HC.load(rec, base)
        check(man and man["skipped"] and not man["claude_files"] and not list((d / "claude").rglob("*.jsonl")),
              "capture: a symlinked %s is skipped (reported), its target never copied" % what, man)
    lane = dict(rec, arm="ralph_c", detail={"tester": "runner-1", "model": False})
    _e, _g, blk = SP.tester_captures({"ralph_c": {"recs": [lane]}}, base, 0, float("inf"))
    _e, _g, blk2 = SP.tester_captures({"ralph_c": {"recs": [dict(lane, detail={"tester": "runner-1"})]}}, base, 0,
                                      float("inf"))
    check(blk == [] and len(blk2) == 1, "a test_start marked model:false (ralph_c lane runner, no model) needs no "
          "capture; the same record without the mark blocks", (blk, blk2))
    man, why = HC.load(dict(rec, ts=iso(1001)), base)
    check(man is None and "no capture" in why, "capture: another test_start (other ts) has no capture", why)
    (HC.cdir(rec, base) / "manifest.json").write_text(json.dumps(dict(json.loads(
        (HC.cdir(rec, base) / "manifest.json").read_text()), tester="y")))
    man, why = HC.load(rec, base)
    check(man is None and "does not match" in why, "capture: a manifest naming another tester is refused", why)
    # GPT r1: a session that STARTS elsewhere and later works in a tester root is still tester_outside
    pj2 = tmp / "census" / "projects2" / "-home-u-elsewhere"
    pj2.mkdir(parents=True)
    l2 = lambda t, mid, cwd: json.dumps({"type": "assistant", "timestamp": iso(t), "cwd": cwd, "message": {  # noqa: E731
        "id": mid, "model": OPUS, "usage": {"input_tokens": 10, "output_tokens": 0}}}) + "\n"
    (pj2 / "s.jsonl").write_text(l2(1000, "a", "/home/u/elsewhere") + l2(1001, "b", "/tmp/rt-abcdefgh/tree"))
    out = S.claude_spend_by_arm(projects=str(pj2.parent), arena_root="/nonexistent", since=500, until=2000)
    rs = (out.get(S.UNATTRIBUTED) or {}).get("reasons", {})
    check("tester_outside" in rs, "census: a session whose LATER cwd is a tester root is tester_outside", rs)
    # GPT r2: in an arm-written root (sandbox HOME / capture) a symlinked or unreadable dir blocks (unreadable_files)
    ar = tmp / "census" / "armroot"
    (ar / "-s").mkdir(parents=True)
    (ar / "-s" / "ok.jsonl").write_text(l2(1000, "c", "/x"))
    (ar / "-lnk").symlink_to(pj2)
    (ar / "-ro").mkdir()
    os.chmod(ar / "-ro", 0)
    try:
        dg = {}
        S.claude_spend_by_arm(projects=str(tmp / "census" / "none"), arena_root="/nonexistent", since=500, until=2000,
                              diag=dg, extra=[(str(ar), "trio", None)])
        uf = dg.get("unreadable_files") or []
        check(any("-lnk" in x for x in uf) and (any("-ro" in x for x in uf) or os.access(ar / "-ro", os.R_OK)),
              "census: a symlinked / unreadable dir in an arm-written transcript root is unreadable_files (blocking)",
              uf)
    finally:
        os.chmod(ar / "-ro", 0o755)
    # GPT r2: an arm session whose LATER cwd leaves the arm's clone is cwd_mismatch (every cwd checked)
    cr = tmp / "census" / "clones"
    pj3 = tmp / "census" / "projects3" / S.path_slug(str(cr / "trio"))
    pj3.mkdir(parents=True)
    (pj3 / "s.jsonl").write_text(l2(1000, "d", str(cr / "trio")) + l2(1001, "e", "/tmp/rt-abcdefgh/tree"))
    dg = {}
    out = S.claude_spend_by_arm(projects=str(pj3.parent), arms=["trio"], arena_root=str(cr), since=500, until=2000,
                                diag=dg)
    check(dg.get("cwd_mismatch") and "trio" not in out, "census: an arm session that later works outside its clone "
          "is cwd_mismatch, not charged to the arm", (dg.get("cwd_mismatch"), dict(out)))
    # GPT r2: HOME itself a symlink is never followed (fd walk from the tester root, O_NOFOLLOW at every component)
    hr = tmp / "census" / "troot"
    hr.mkdir()
    (hr / "home").symlink_to(outside)
    HC.capture(dict(rec, ts=iso(1003)), home=hr / "home", gpt_dir=None, base=base)
    man, _ = HC.load(dict(rec, ts=iso(1003)), base)
    check(man and man["skipped"] and not man["claude_files"], "capture: a symlinked HOME is skipped, never followed",
          man)
    # a symlinked SUBDIR under a real projects dir is skipped (reported), its target's transcripts never copied
    hs = tmp / "census" / "home_subdir"
    (hs / ".claude" / "projects").mkdir(parents=True)
    tgt = next(p for p in (outside / ".claude" / "projects").iterdir() if p.is_dir())
    (hs / ".claude" / "projects" / "-lnk").symlink_to(tgt)
    HC.capture(dict(rec, ts=iso(1004)), home=hs, gpt_dir=None, base=base)
    man, d = HC.load(dict(rec, ts=iso(1004)), base)
    check(man and any("symlinked dir" in x and "-lnk" in x for x in man["skipped"]) and not man["claude_files"]
          and not list((d / "claude").rglob("*.jsonl")), "capture: a symlinked projects subdir is skipped, its "
          "target never copied", man)
    # GPT r1: an unreadable directory under the tester's projects is reported as skipped, not silently lost
    h = tmp / "census" / "home_unreadable"
    write_tester(h, h / "g", 1000, "trio", 0)
    locked = h / ".claude" / "projects" / "-locked"
    locked.mkdir()
    (locked / "x.jsonl").write_text("{}\n")
    os.chmod(locked, 0)
    try:
        man = None
        if not os.access(locked, os.R_OK):              # root ignores modes: then the probe cannot see, say so
            HC.capture(dict(rec, ts=iso(1002)), home=h, gpt_dir=None, base=base)
            man, _ = HC.load(dict(rec, ts=iso(1002)), base)
        check(man is not None and any("-locked" in x for x in man["skipped"]) and man["claude_files"],
              "capture: an unreadable transcript dir is a blocking skip (os.walk errors are not swallowed)", man)
    finally:
        os.chmod(locked, 0o755)
    # GPT r1: a tester that started shortly BEFORE the window still needs its capture; one far before does not
    old = dict(rec, ts=iso(1000 - 60), detail={"tester": "pre"})
    _e, _g, b1 = SP.tester_captures({"trio": {"recs": [old]}}, base, 1000, 2000)
    _e, _g, b2 = SP.tester_captures({"trio": {"recs": [dict(old, ts=iso(1000 - SP.PRE_WINDOW_S - 60))]}}, base,
                                    1000, 2000)
    check(len(b1) == 1 and b2 == [], "a tester started just before the window is metered (missing capture blocks); "
          "one PRE_WINDOW_S earlier is not", (b1, b2))
    # GPT r1: a symlinked sandbox HOME component blocks instead of vanishing
    sb = tmp / "census" / "sandbox"
    (sb / "c-00000000-x" / "build").mkdir(parents=True)
    (sb / "c-00000000-x" / "build" / "home").symlink_to(outside)
    homes, hb = SP.sandbox_homes(sb)
    check(homes == [] and len(hb) == 1 and "symlinked" in hb[0], "a symlinked sandbox HOME is blocking", (homes, hb))
    empty = tmp / "census" / "empty_projects"
    empty.mkdir()
    (tmp / "census" / "gpt_empty.jsonl").write_text("")
    doc = SP.meter({"trio": {"recs": [{"event": "assign", "arm": "trio", "task": "T", "run_id": "r", "lane": "build",
                                       "ts": iso(1000)}]}}, projects=str(empty), clones_root="/nonexistent",
                   gpt_log=str(tmp / "census" / "gpt_empty.jsonl"), helpers=base, sandbox_root=sb)
    check(any("symlinked" in x for x in doc["blocking"]), "meter: the sandbox-home blocking reaches the doc",
          doc["blocking"])


# ------------------------------------------------------------------ e2e

def setup_env(tmp, name):
    root = tmp / name
    env = dict(ARENA_ROOT=str(root / "arena"), ARENA_CLONES=str(root / "clones"), ARENA_PRIVATE=str(root / "private"),
               ARENA_JUDGE_WORK=str(root / "work"), ARENA_EVENT_TOKEN_FILE=str(root / "secret" / "event_token"),
               ARENA_ANCHOR_FILE=str(root / "secret" / "anchors.jsonl"),
               ARENA_WITNESS=str(root / "secret" / "witness.jsonl"), ARENA_JUDGE_OPUS_MODEL="fake-model-for-selftest",
               RM_GPT_CALL_LOG=str(root / "gpt_calls.jsonl"), ARENA_METER_HELPERS=str(root / "helpers"),
               RM_ARM_SANDBOX_SCRATCH=str(root / "sandbox"))
    os.environ.update(env)
    for k in ("ARENA_ROOT", "ARENA_CLONES", "ARENA_JUDGE_WORK"):
        Path(env[k]).mkdir(parents=True)
    p = A.paths()
    L.init_token(p)
    return root, p


def tasks_spec():
    # chrono: the era gate's key (arena_analysis ERA GATE). N - i puts the newest era FIRST so the gate is open from
    # the first look; the order is not what this suite tests (selftest_arena_analysis.t_era_gate does)
    return {"T%03d" % i: {"kind": A.KINDS[i % 2], "size": (1, 2, 4)[i % 3], "chrono": N - i} for i in range(N)}


def era_repo(root):
    """A git repo of N empty commits; -> (repo, {task: base_sha}) with T000 on the NEWEST commit (as tasks_spec), so
    arena_analysis.py run --era-repo computes the same chronology from base_sha as the in-process specs carry."""
    import subprocess
    repo = Path(root) / "era_repo"
    repo.mkdir()
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")
    subprocess.run(["git", "init", "-q", str(repo)], check=True, env=env)
    shas = []
    for i in range(N):
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "--allow-empty", "-m", "c%d" % i], check=True, env=env)
        shas.append(subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, env=env,
                                   capture_output=True, text=True).stdout.strip())
    return repo, {"T%03d" % i: shas[N - 1 - i] for i in range(N)}


def task_cost():
    rng = random.Random(11)
    return {"T%03d" % i: math.exp(math.log(1e5) + rng.gauss(0, 1.0)) for i in range(N)}


TESTER_IN, TESTER_GPT, SANDBOX_IN = 500, 7, 300


def write_tester(home, gdir, t, arm, i, *, transcript=True, tokens=TESTER_IN):
    """What an arm tester leaves in its private root: a Claude transcript under HOME, a GPT record under
    RM_GPT_CALL_LOG=<root>/gpt/ (tagged with the WRONG arm: the capture's place decides, never the record)."""
    if transcript:
        d = Path(home) / ".claude" / "projects" / "-tmp-rt-x-tree"
        d.mkdir(parents=True, exist_ok=True)
        (d / "t.jsonl").write_text(json.dumps({"type": "assistant", "timestamp": iso(t), "cwd": "/tmp/rt-x/tree",
                                               "message": {"id": "q-%s-%d" % (arm, i), "model": OPUS,
                                                           "usage": {"input_tokens": tokens, "output_tokens": 0}}})
                                   + "\n")
    Path(gdir).mkdir(parents=True, exist_ok=True)
    (Path(gdir) / "c1.jsonl").write_text(json.dumps({"t": t + 5, "arm": "someone-else", "tokens_used": TESTER_GPT})
                                        + "\n")


def scratch_home(clone, role="build"):
    """An arm_sandbox private HOME's projects dir for `clone` (arm_sandbox.scratch_dir's naming)."""
    c = os.path.realpath(str(clone))
    name = "%s-%s-%s" % (os.path.basename(c), hashlib.sha256(c.encode()).hexdigest()[:8], "0123456789abcdef")
    return Path(os.environ["RM_ARM_SANDBOX_SCRATCH"]) / name / role / "home" / ".claude" / "projects"


def build(tmp, name, *, judge_writer=True, sinks=True, raw_counts=True, pending=False, id_conflict=False,
          stale=False, since_cut=False, capture="ok", foreign=False, tester_out=False):
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
    gpt_lines, tr, starts = [], {}, []
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
                er = w.emit(arm, ev, lane="build", run_id=rid, ts=iso(t + dt_), task=task, **more)
                if ev == "test_start":
                    starts.append((arm, i, t, er))
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
    # every tester the logs say ran is captured (helper_capture.py) the way the loops do it before the rmtree
    for arm, i, t, er in starts:
        troot = Path(tempfile.mkdtemp(prefix="rt-", dir=str(root)))
        odd = arm == "trio" and i == 4
        write_tester(troot / "home", troot / "gpt", t + 120, arm, i, transcript=not (odd and capture == "empty"))
        if odd and capture == "symlink":
            pj = troot / "home" / ".claude" / "projects" / "-tmp-rt-x-tree"
            (pj / "t.jsonl").rename(troot / "elsewhere.jsonl")
            (pj / "t.jsonl").symlink_to(troot / "elsewhere.jsonl")
        if not (odd and capture == "missing"):
            HC.capture(er, home=troot / "home", gpt_dir=troot / "gpt", rc=0)
        shutil.rmtree(troot)
    # trio's builder ran in arm_sandbox: its transcripts live in the clone's private scratch HOME, not ~/.claude
    sh = scratch_home(clones_root / "trio")
    sl = sh / S.path_slug(os.path.realpath(str(clones_root / "trio")))
    sl.mkdir(parents=True)
    lines = [{"type": "assistant", "timestamp": iso(T0 + i * 600 + 70), "cwd": os.path.realpath(str(clones_root / "trio")),
              "message": {"id": "sb-trio-%d" % i, "model": OPUS, "usage": {"input_tokens": SANDBOX_IN, "output_tokens": 0}}}
             for i in range(N)]
    if foreign:          # a session of the v3 clone planted in trio's scratch HOME: not trio's to carry
        lines.append(dict(lines[0], cwd=os.path.realpath(str(clones_root / "v3")),
                          message=dict(lines[0]["message"], id="foreign-1")))
    (sl / "s.jsonl").write_text("".join(json.dumps(x) + "\n" for x in lines))
    if tester_out:       # BENCH bfeed d1: a 10M-token tester session written outside every arena path, in T003's span
        d = projects / S.path_slug("/tmp/rt-x/tree")
        d.mkdir(parents=True)
        (d / "o.jsonl").write_text(json.dumps({"type": "assistant", "timestamp": iso(T0 + 3 * 600 + 120),
                                               "cwd": "/tmp/rt-x/tree", "message": {
                                                   "id": "d1", "model": OPUS,
                                                   "usage": {"input_tokens": 10 ** 7, "output_tokens": 0}}}) + "\n")
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
          + TESTER_IN + SANDBOX_IN and one["gpt"]["tokens"] == 100 + TESTER_GPT and one.get("ambiguous_calls") == 0,
          "a task row holds the raw per-model Claude input (builder from its sandbox HOME + captured tester) and the "
          "raw GPT tokens (arm log + captured tester log, on the capture's arm) of that task only", one)
    v5 = rows.get("v3", {}).get("T005", {})
    check(v5.get("claude", {}).get(OPUS, {}).get("input") == int(task_cost()["T005"]) + TESTER_IN
          and v5.get("gpt", {}).get("tokens") == 100 + TESTER_GPT,
          "v3's captured tester spend is v3's (no sandbox HOME for v3 here)", v5)
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
    erepo, bases = era_repo(r["root"])
    for t, s in r["specs"].items():
        (td / (t + ".json")).write_text(json.dumps(dict({k: v for k, v in s.items() if k != "chrono"}, id=t,
                                                        base_sha=bases[t])))
    out = r["root"] / "spend.json"
    with contextlib.redirect_stdout(io.StringIO()):
        rc1 = SP.main(["--out", str(out), "--allow-untrusted", "--projects", str(r["projects"]),
                       "--clones-root", str(r["clones_root"])])
        rc2 = AA.main(["run", "--spend", str(out), "--tasks-dir", str(td), "--allow-untrusted", "--draws", "2000",
                       "--era-repo", str(erepo), "--out", str(r["root"] / "rep.json")])
        rc3 = AA.main(["run", "--spend", str(r["root"] / "missing.json"), "--tasks-dir", str(td),
                       "--allow-untrusted", "--draws", "2000"])
    rep2 = json.loads((r["root"] / "rep.json").read_text()) if (r["root"] / "rep.json").is_file() else {}
    check(rc1 == 0 and json.loads(out.read_text()).get("schema") == AA.SPEND_SCHEMA, "CLI: arena_spend.py writes the "
          "schema file", rc1)
    check(rc2 == 0 and rep2.get("final", {}).get("verdict") == "DECIDE_FOR_trio"
          and rep2.get("spend_overhead", {}).get("trio"),
          "CLI: arena_analysis.py run on it decides, and reports the overhead", (rc2, rep2.get("final")))
    check(rep2.get("era_gate", {}).get("status") == "MEASURED" and not rep2["era_gate"].get("no_chrono"),
          "CLI: the era gate's chronology is computed from base_sha in --era-repo", rep2.get("era_gate"))
    check(rc3 == 3, "mutation: no spend file -> UNMEASURED, exit 3", rc3)
    with contextlib.redirect_stdout(io.StringIO()):
        rc4 = SP.main(["--out", str(out), "--allow-untrusted", "--projects", str(r["projects"]),
                       "--clones-root", str(r["clones_root"]), "--helpers", str(r["root"] / "nohelpers"),
                       "--sandbox-root", str(r["root"] / "nosandbox")])
    d4 = json.loads(out.read_text())
    check(rc4 == 0 and any("not captured" in b for b in d4.get("blocking", ())),
          "CLI --helpers is honoured: an empty capture dir blocks every tester", (rc4, d4.get("blocking", [])[:2]))


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
    # r2#3: judge precedence must not depend on a clock that ran backwards
    spec = {"T1": {"kind": A.KINDS[0], "size": 1}}

    def jr(ts, verdict, pending=False):
        return {"ts": iso(ts), "arm": "trio", "lane": "judge", "run_id": "judge", "task": "T1", "event": "judge",
                "sha": "a" * 40, "verdict": verdict, "detail": dict({"base": "b"}, **({"pending": True} if pending
                                                                                      else {}))}
    # a complete meter row (the reader refuses a missing field: ARENA_SPEND_ROW_HARDEN_MISSING_GPT_FIELD)
    row = {"T1": {"claude": {OPUS: dict({k: 0 for k in AA.CLAUDE_TOKEN_WEIGHT}, input=10)},
                  "gpt": {k: 0 for k in AA.GPT_FIELDS}}}
    for seq, ok, what in (([jr(200, "accept"), jr(190, "invalid", True)], False,
                           "an earlier accept, then a pending re-judgment stamped EARLIER (clock back) and never "
                           "recorded"),
                          ([jr(100, "invalid", True), jr(90, "reject")], False,
                           "a verdict stamped before its own pending marker (clock back)"),
                          ([jr(200, "reject"), jr(190, "accept")], False,
                           "a later-appended verdict stamped earlier (clock back), no pending involved"),
                          ([jr(100, "invalid", True), dict(jr(150, "accept"), lane="L1")], False,
                           "the last-appended live judge event is pending, a later-stamped import does not cover it"),
                          ([jr(100, "invalid", True), jr(100, "reject")], True, "pending then verdict, same second")):
        out, prob = AA.completions(seq, spec, row, AA.default_conv())
        check((prob is None) == ok, "r2#3: %s -> %s" % (what, "measured" if ok else "arm problem"), (out, prob))


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
    for kw, what, needle in (({"capture": "missing"}, "a tester ran and was never captured", "not captured"),
                             ({"capture": "empty"}, "a tester capture holds no transcript", "no Claude transcript"),
                             ({"capture": "symlink"}, "a tester planted a symlinked transcript", "skipped"),
                             ({"foreign": True}, "another clone's session in an arm's sandbox HOME", "sandbox_foreign"),
                             ({"tester_out": True}, "BENCH d1: a 10M tester session outside every arena path",
                              "tester_outside")):
        r = build(tmp, "c_" + needle, **kw)
        check(r["rep"]["final"]["verdict"].startswith("UNMEASURED")
              and any(needle in b for b in r["doc"]["blocking"]),
              "tester spend: %s -> blocking (%s), UNMEASURED" % (what, needle), (r["rep"]["final"], r["doc"]["blocking"]))
    r = build(tmp, "noraw", raw_counts=False)
    check(r["rep"]["final"]["verdict"] == "UNMEASURED",
          "mutation: raw counts dropped (derived claude_ite only) -> UNMEASURED", r["rep"]["final"])


def main():
    if not shutil.which("bwrap"):
        print("FAIL  bwrap not installed: the real judge cannot run")
        return 1
    keys = ("ARENA_ROOT", "ARENA_CLONES", "ARENA_PRIVATE", "ARENA_JUDGE_WORK", "ARENA_JUDGE_OPUS_MODEL",
            "ARENA_EVENT_TOKEN_FILE", "ARENA_ANCHOR_FILE", "ARENA_WITNESS", "RM_GPT_CALL_LOG", "ARENA_ARMS",
            "ARENA_ARM_TOKENS", "ANTHROPIC_DEFAULT_OPUS_MODEL", "ARENA_METER_HELPERS", "RM_ARM_SANDBOX_SCRATCH")
    saved = {k: os.environ.get(k) for k in keys}
    tmp = Path(tempfile.mkdtemp(prefix="arena_spend_st_"))
    try:
        for k in ("ARENA_ARMS", "ARENA_ARM_TOKENS"):
            os.environ.pop(k, None)
        t_units()
        t_census(tmp)
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
