#!/usr/bin/env python3
"""selftest_arena_eventlog.py - arena_eventlog.py + arena_v3_adapter.py, each criterion proven by FORCED FAILURE.

ARENA_EVENTLOG_BUILD_AGENTS_MAY_NOT_WRITE criteria, and the failure planted for each:
  agent write   control: harness-written lines are accepted. Then a hand-appended unsigned line, a line signed with a
                wrong token, a replayed (duplicated) line, a line whose body was edited, a deleted line (the next
                line's chain breaks) are each REJECTED and absent from report(); a writer with no token, or with a
                token file inside an arm-readable root, refuses to be built
  schema        unknown event, build_end without builder, card without unblocked list, test_start without tester
  adapter       adapter's done-count for 2026-10-24 equals rimflow_metrics.compute's flow["done"] for that day on the
                REAL ledger (both printed, nonzero and not round-checked); then one close dropped from the adapter
                input makes the numbers differ (the comparison can fail); testq results become test_start/test_end
  same agent    tester == builder is flagged (stamped by the writer AND recomputed by flagged_same_agent); different
                tester is not; a build_end with no different-agent test_start is listed untested
  owner         owner minutes per arm; output with and without owner-unblocked tasks differ exactly by those tasks
  fix round 1   (tester report D1-D8) D1 arm process (RM_ARM / cwd in a clone), loose-mode or /mnt token refused; a
                re-signed history (leaked token) passes crypto but is refused by the local anchor, and by a
                ledger-published anchor once the local store is wiped. D2 tail / whole-file deletion refused. D3 partial
                tail quarantined. D4 case/space builder ids flagged; blank/numeric refused. D5 adapter write twice = 0
                new. D6 bad minutes refused. D8 last verdict rules; duplicate card once. D7 stranded lines recoverable.
Writes only under a temp dir (ARENA_ROOT / ARENA_EVENT_TOKEN_FILE point there). The real-ledger read is read-only.
"""
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import arena_eventlog as L  # noqa: E402
import arena_tasks as A  # noqa: E402
import arena_v3_adapter as V  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def raises(exc, fn, *a, **k):
    try:
        fn(*a, **k)
    except exc as e:
        return str(e)
    return None


def fresh(tmp, name, writer=True):
    root = tmp / name
    os.environ["ARENA_ROOT"] = str(root)
    os.environ["ARENA_CLONES"] = str(root / "clones")
    os.environ["ARENA_EVENT_TOKEN_FILE"] = str(tmp / (name + "_secret") / "event_token")
    os.environ["ARENA_ANCHOR_FILE"] = str(tmp / (name + "_secret") / "anchors.jsonl")   # never an inherited store
    os.environ["ARENA_WITNESS"] = str(tmp / (name + "_secret") / "witness.jsonl")   # stand-in for journald
    p = A.paths()
    assert A._inside(L.anchor_path(p), tmp) and A._inside(L.token_path(p), tmp)
    L.init_token(p)
    return p, (L.HarnessWriter(p) if writer else None)


def t_agent_write(tmp):
    p, w = fresh(tmp, "aw")
    kw = dict(lane="L1", run_id="r1")
    w.emit("ralph_a", "assign", task="T1", **kw)
    w.emit("ralph_a", "build_end", task="T1", sha="abc", detail={"builder": "A1"}, **kw)
    w.emit("ralph_a", "judge", task="T1", verdict="accept", **kw)
    v = L.verify(p, "ralph_a")
    check(len(v["accepted"]) == 3 and not v["rejected"], "control: 3 harness-written lines all accepted, 0 rejected")
    f = L.arm_file(p, "ralph_a")
    good = f.read_text().splitlines()
    forged = json.dumps({"ts": "2026-10-30T00:00:00Z", "arm": "ralph_a", "lane": "L1", "run_id": "r1",
                         "task": "T9", "event": "judge", "verdict": "accept"}, sort_keys=True)
    with open(f, "a") as fh:
        fh.write(forged + "\n")
    v = L.verify(p, "ralph_a")
    check(len(v["accepted"]) == 3 and len(v["rejected"]) == 1, "hand-appended unsigned judge line is REJECTED")
    check(all(r.get("task") != "T9" for r in v["accepted"]), "forged T9 absent from accepted records")
    # signed with a wrong token
    bad = L.HarnessWriter(p, token="f" * 64)
    f2 = L.arm_file(p, "other")
    bad.emit("other", "stop", lane="L", run_id="r")
    check(len(L.verify(p, "other")["accepted"]) == 0 and len(L.verify(p, "other")["rejected"]) == 1,
          "a line signed with a wrong token is rejected")
    # replay
    f.write_text("\n".join(good + [good[2]]) + "\n")
    v = L.verify(p, "ralph_a")
    check(len(v["accepted"]) == 3 and len(v["rejected"]) == 1, "a replayed copy of a signed line is rejected")
    # edit body
    edited = json.loads(good[2]); edited["verdict"] = "reject"
    f.write_text("\n".join(good[:2] + [json.dumps(edited, sort_keys=True)]) + "\n")
    v = L.verify(p, "ralph_a")
    check(len(v["accepted"]) == 2 and len(v["rejected"]) == 1, "an edited signed line is rejected")
    # delete line 2: line 3 no longer chains
    f.write_text("\n".join([good[0], good[2]]) + "\n")
    v = L.verify(p, "ralph_a")
    check(len(v["accepted"]) == 1 and len(v["rejected"]) == 1, "a deleted line breaks the chain: the next line is rejected")
    # report ignores rejected, and the harness can keep writing past junk
    f.write_text("\n".join(good + [forged]) + "\n")
    w.emit("ralph_a", "stop", **kw)
    r = L.report(p)["ralph_a"]
    check(r["accepted"] == 4 and r["rejected"] == 1, "report counts 4 accepted / 1 rejected; harness still writes after junk")
    # no token / token inside arm-readable root
    os.environ["ARENA_EVENT_TOKEN_FILE"] = str(tmp / "nonexistent" / "tok")
    check(raises(L.Rejected, L.HarnessWriter, p) is not None, "writer without a token file refuses to be built")
    os.environ["ARENA_EVENT_TOKEN_FILE"] = str(p["events"] / "token")
    check(raises(L.Rejected, L.init_token, p) is not None, "token inside the arm-readable events dir is refused")
    check(raises(L.Rejected, L.HarnessWriter, p, "a" * 64) is not None, "writer with token path in a readable root refused")
    # schema
    p, w = fresh(tmp, "sc")
    kw = dict(lane="L", run_id="r")
    for name, args in (("unknown event", ("bogus", {})), ("build_end without builder", ("build_end", {"task": "T"})),
                       ("test_start without tester", ("test_start", {"task": "T"})),
                       ("card without unblocked list", ("card", {"minutes": 2, "detail": {"card_id": "c", "unblocked": "T"}})),
                       ("bad arm name", None)):
        if args is None:
            err = raises(L.Rejected, w.emit, "../x", "stop", **kw)
        else:
            err = raises(L.Rejected, w.emit, "a", args[0], **kw, **args[1])
        check(err is not None, "schema rejects " + name)
    check(raises(L.Rejected, w.emit, "a", "stop", lane="L", run_id="r", bogus_field=1) is not None, "unknown field rejected")


def _metrics_close_done(M, ev, lo, hi):
    """Independent close count: done transitions per rimflow_metrics.timelines in [lo, hi), attributed to the
    close verb when the raw ledger events of that item in that second include a close and no other done verb."""
    _, tl = M.timelines(ev)
    trans = set()
    for iid, rows in tl.items():
        for (t, st, *_), prev in zip(rows[1:], rows[:-1]):
            if st != prev[1] and st == "done" and lo <= t < hi:
                trans.add((iid, t))
    verbs = {}
    for e in ev:
        k = (e.get("id"), L.ts_epoch(e["ts"]))
        if k in trans:
            verbs.setdefault(k, set()).add(e.get("event"))
    close = sum(1 for k in trans if "close" in verbs.get(k, ()) and not verbs[k] & {"verify", "implemented"})
    amb = sum(1 for k in trans if "close" in verbs.get(k, ()) and verbs[k] & {"verify", "implemented"})
    return close, amb


def t_adapter(tmp):
    sys.path.insert(0, str(HERE.parent))
    sys.path.insert(0, str(HERE.parent.parent))
    import rimflow_metrics as M
    from rimflow import model
    ev = model.read()
    recs = V.translate_ledger(ev)
    day = "2026-10-24"
    d0 = model.epoch(day + "T00:00:00Z")
    f = lambda now: M.compute(ev, now=now, window_days=1, mods={}, heat=None)["flow"].get("done", 0)
    # metrics' window is t >= now-1d (no upper bound), so the UTC day [d0, d0+86400) = f(d0+86400) - f(d0+2*86400)
    hi = d0 + 86400
    met = f(hi) - f(hi + 86400)
    ad = V.done_count(recs, d0, hi)
    ad_close = V.done_count(recs, d0, hi, "close")
    met_close, amb = _metrics_close_done(M, ev, d0, hi)
    print("      %s UTC [00:00, 24:00): rimflow_metrics flow.done=%d adapter done=%d | close verb: metrics timelines=%d "
          "adapter=%d (ambiguous same-second=%d)" % (day, met, ad, met_close, ad_close, amb))
    check(met > 10 and ad == met, "R2-8 adapter done-count equals rimflow_metrics flow.done for UTC %s (%d = %d)"
          % (day, ad, met))
    check(met_close > 10 and ad_close == met_close and amb == 0,
          "R2-8 adapter close-verb done-count equals the close count from rimflow_metrics.timelines (%d = %d)"
          % (ad_close, met_close))
    # forced failure: drop one close-verb done-making build_end: BOTH comparisons break
    drop = next(r for r in recs if r["detail"].get("done") and r["detail"].get("via") == "close"
                and d0 <= L.ts_epoch(r["ts"]) < hi)
    short = [r for r in recs if r is not drop]
    check(V.done_count(short, d0, hi) != met and V.done_count(short, d0, hi, "close") != met_close,
          "dropping one close from the adapter output breaks both the done and the close match")
    # records are schema-valid and carry task/sha
    bad = 0
    for r in recs[:2000]:
        try:
            L.validate_record(dict(r, detail=r.get("detail") or {}))
        except L.Rejected:
            bad += 1
    check(bad == 0, "first 2000 adapter records pass validate_record")
    # writes through the harness writer
    p, w = fresh(tmp, "ad")
    sample = [r for r in recs if r["ts"].startswith(day)][:50]
    check(V.write(w, sample) == len(sample) and len(L.verify(p, "v3")["accepted"]) == len(sample),
          "adapter writes %d records via the token writer; all verify" % len(sample))
    # testq
    jobs = {"J1": {"id": "J1", "item": "ITEM_A", "lane": "stevedesktop", "schema": "testq.job/1", "requested_by": "BENCH"}}
    res = [{"schema": "testq.result/1", "job": "J1", "host": "stevedesktop", "started": "2026-10-29T10:00:00Z",
            "finished": "2026-10-29T10:20:00Z", "outcome": "DONE", "counts": {"PASS": 3}},
           {"job": "J-unknown", "host": "h", "started": "2026-10-29T10:00:00Z"}]
    t = V.translate_testq(res, jobs)
    check([r["event"] for r in t] == ["test_start", "test_end"] and t[0]["task"] == "ITEM_A"
          and t[0]["detail"]["tester"] == "BENCH" and t[0]["detail"]["runner"] == "testq:stevedesktop"
          and t[1]["verdict"] == "DONE",
          "testq result -> test_start + test_end, tester = submitting seat, runner = testq:<host>; no item: not invented")


def t_same_agent(tmp):
    p, w = fresh(tmp, "sa")
    kw = dict(lane="L", run_id="r")
    w.emit("trio", "build_end", task="T1", ts="2026-10-30T01:00:00Z", detail={"builder": "agent-7"}, **kw)
    s1 = w.emit("trio", "test_start", task="T1", ts="2026-10-30T01:05:00Z", detail={"tester": "agent-7"}, **kw)
    w.emit("trio", "build_end", task="T2", ts="2026-10-30T02:00:00Z", detail={"builder": "agent-7"}, **kw)
    s2 = w.emit("trio", "test_start", task="T2", ts="2026-10-30T02:10:00Z", detail={"tester": "agent-9"}, **kw)
    w.emit("trio", "build_end", task="T3", ts="2026-10-30T03:00:00Z", detail={"builder": "agent-7"}, **kw)
    check(s1.get("rule") == L.FLAG_SAME_AGENT, "writer stamps tester==builder test_start as tester_is_builder")
    check(s2.get("rule") is None, "control: a different tester is not stamped")
    recs = L.verify(p, "trio")["accepted"]
    fl = L.flagged_same_agent(recs)
    check([r["task"] for r in fl] == ["T1"], "flagged_same_agent returns exactly the T1 test_start (recomputed)")
    check(sorted(r["task"] for r in L.untested_builds(recs)) == ["T1", "T3"],
          "untested builds: T1 (only self-tested) and T3 (no test_start) listed, T2 not")
    check([round(x) for x in L.latency_minutes(recs)] == [10], "latency build_end -> different-agent test_start = 10 min (T2 only)")
    r = L.report(p)["trio"]
    check(r["flagged_same_agent"] == 1, "report shows 1 flagged")


def t_owner(tmp):
    p, w = fresh(tmp, "ow")
    kw = dict(lane="L", run_id="r")
    for arm, cards in (("ralph_a", [(5, ["T1"]), (3, [])]), ("trio", [(2, ["T1", "T2"])])):
        for i, (m, un) in enumerate(cards):
            w.emit(arm, "card", minutes=m, detail={"card_id": "%s-c%d" % (arm, i), "unblocked": un}, **kw)
        for t in ("T1", "T2", "T3"):
            w.emit(arm, "judge", task=t, verdict="accept", **kw)
    w.emit("trio", "owner_touch", minutes=1, **kw)
    w.emit("ralph_a", "judge", task="T4", verdict="reject", **kw)
    rep = L.report(p)
    a, t = rep["ralph_a"], rep["trio"]
    check(a["owner_minutes"] == 8 and t["owner_minutes"] == 3, "owner minutes per arm: ralph_a 8, trio 3 (2 card + 1 touch)")
    check(a["points_with_unblocked"] == 3 and a["points_without_unblocked"] == 2 and a["owner_unblocked_accepted"] == ["T1"],
          "ralph_a output 3 with / 2 without owner-unblocked work (T1); rejected T4 never counts")
    check(t["points_with_unblocked"] == 3 and t["points_without_unblocked"] == 1,
          "trio output 3 with / 1 without (T1,T2 unblocked)")
    check(abs(a["minutes_per_point_with"] - 8 / 3) < 1e-9 and abs(a["minutes_per_point_without"] - 4.0) < 1e-9,
          "minutes per point reported both ways (8/3 and 8/2)")
    check(a["points_with_unblocked"] != a["points_without_unblocked"], "forced: the two outputs differ when a card unblocked work")


# ---------------------------------------------------------------- fix round 1: one forced failure per tester defect

def _three(w, arm="ralph_a"):
    kw = dict(lane="L1", run_id="r1")
    w.emit(arm, "assign", task="T1", **kw)
    w.emit(arm, "build_end", task="T1", sha="abc", detail={"builder": "A1"}, **kw)
    w.emit(arm, "test_start", task="T1", detail={"tester": "B2"}, **kw)
    w.emit(arm, "judge", task="T1", verdict="accept", **kw)
    return L.arm_file(w.p, arm)


def t_d1_token(tmp):
    p, w = fresh(tmp, "d1")
    os.environ["RM_ARM"] = "ralph_a"
    try:
        check(raises(L.Rejected, L.HarnessWriter, p) is not None, "D1 RM_ARM set: an arm process cannot build a writer")
        check(raises(L.Rejected, L.verify, p, "ralph_a") is not None, "D1 RM_ARM set: an arm process cannot read the token")
    finally:
        os.environ.pop("RM_ARM", None)
    clone = Path(os.environ["ARENA_CLONES"]) / "ralph_a"
    clone.mkdir(parents=True, exist_ok=True)
    old = os.getcwd()
    os.chdir(clone)
    try:
        check(raises(L.Rejected, L.HarnessWriter, p) is not None, "D1 cwd inside an arm clone: writer refused")
    finally:
        os.chdir(old)
    tp = L.token_path(p)
    os.chmod(tp, 0o644)
    check(raises(L.Rejected, L.HarnessWriter, p) is not None, "D1 token with group/other mode bits (drvfs shows 777) refused")
    os.chmod(tp, 0o600)
    saved = os.environ["ARENA_EVENT_TOKEN_FILE"]
    check(raises(L.Rejected, L._check_token_location, Path("/mnt/d/ClaudeWork/rimmandrake/arena_x/event_token"), p)
          is not None, "D1 token location on a Windows drive (/mnt/*) refused")
    os.environ.pop("ARENA_EVENT_TOKEN_FILE")
    dflt = str(L.token_path(p))
    os.environ["ARENA_EVENT_TOKEN_FILE"] = saved
    check(not dflt.startswith("/mnt/") and not A._inside(dflt, p["root"]) and dflt.startswith(str(Path.home())),
          "D1 default token path is on the ext4 home, outside D: and the arena root (%s)" % dflt)
    # a token that DID leak: the agent re-signs a rewritten history. Crypto accepts it; the anchors catch it.
    f = _three(w)
    tok = L.token_path(p).read_text().strip()
    recs = [json.loads(l) for l in f.read_text().splitlines()]
    published = L.anchor_note_text([L.make_anchor("ralph_a", recs, tok)])   # what the harness put in the ledger
    recs[3]["verdict"] = "reject"          # rewrite the judge, re-sign the whole chain
    prev, out = L.GENESIS, []
    for r in recs:
        r = {k: v for k, v in r.items() if k != "sig"}
        r["sig"] = L._sign(tok, prev, r); prev = r["sig"]; out.append(json.dumps(r, sort_keys=True))
    f.write_text("\n".join(out) + "\n")
    v = L.verify(p, "ralph_a")
    check(len(v["accepted"]) == 4 and not v["rejected"], "D1 control: a re-signed forged history passes the crypto check")
    r = L.report(p)["ralph_a"]
    check(bool(r.get("refused")) and "points_with_unblocked" not in r,
          "D1 local anchor: report REFUSES the re-signed arm (%s)" % (r.get("refused"),))
    # the forger also wipes the local anchor store; a ledger-published anchor still catches it
    honest = L.make_anchor("ralph_a", [json.loads(l) for l in out[:3]], tok)   # unchanged prefix: no violation
    ap = L.anchor_path(p)
    assert A._inside(ap, tmp), ap                # R2-9: the selftest only ever deletes its own temp store
    ap.unlink()
    r = L.report(p)["ralph_a"]
    check(bool(r.get("refused")) and "UNMEASURED" not in r["refused"][0],
          "R3 local anchors deleted: the witness still REFUSES the re-signed arm (%s)" % (r.get("refused"),))
    Path(os.environ["ARENA_WITNESS"]).unlink()    # selftest stand-in: a journald witness cannot be deleted
    r = L.report(p)["ralph_a"]
    check(bool(r.get("refused")) and "UNMEASURED" in r["refused"][0] and "points_with_unblocked" not in r,
          "R2-2 local anchors deleted, log non-empty: report FAILS CLOSED (UNMEASURED), the forgery is not reported")
    ext = L.ledger_anchors([{"event": "note", "id": "X", "text": published}, {"event": "note", "id": "Y", "text": "chat"}])
    check(bool(L.report(p, external=ext)["ralph_a"].get("refused")), "D1 ledger-published anchor refuses it again")
    ext2 = L.ledger_anchors([{"event": "note", "text": L.anchor_note_text([honest])}])
    check(not L.report(p, external=ext2)["ralph_a"].get("refused"), "D1 control: a matching ledger anchor is not a violation")
    cmd = L.anchor_note_command(p)
    check(cmd.startswith("python3 src/RimMandrake/rimflow/cli.py note ") and "ARENA_ANCHOR ralph_a:4:" in cmd,
          "D1 anchor-note prints a rimflow note command carrying arm:n:head")


def t_d2_tail(tmp):
    p, w = fresh(tmp, "d2")
    f = _three(w)
    lines = f.read_text().splitlines()
    f.write_text("\n".join(lines[:-1]) + "\n")
    r = L.report(p)["ralph_a"]
    check(r["accepted"] == 3 and r["rejected"] == 0 and bool(r.get("refused")),
          "D2 last line deleted: 3 accepted / 0 rejected, and report REFUSES the arm (anchor says 4)")
    # the TT probe: agent deletes its own test_start (line 3 + 4), harness then writes again
    f.write_text("\n".join(lines[:2]) + "\n")
    w.emit("ralph_a", "stop", lane="L1", run_id="r1")
    r = L.report(p)["ralph_a"]
    check(r["rejected"] == 0 and bool(r.get("refused")), "D2 tail deleted then harness writes again: still refused")
    f2 = _three(w, "trio")
    f2.unlink()
    r = L.report(p).get("trio") or {}
    check(bool(r.get("refused")) and r["accepted"] == 0, "D2 whole file deleted: anchored arm is reported, refused")
    p3, w3 = fresh(tmp, "d2c")
    _three(w3)
    check(not L.report(p3)["ralph_a"].get("refused"), "D2 control: an untouched log is not refused")


def t_d3_partial(tmp):
    p, w = fresh(tmp, "d3")
    f = _three(w)
    with open(f, "a") as fh:
        fh.write('{"arm":"ralph_a","event":"judge","task":"T9"')          # no newline
    w.emit("ralph_a", "judge", task="T2", verdict="accept", lane="L1", run_id="r1")
    v = L.verify(p, "ralph_a")
    check(len(v["accepted"]) == 5 and len(v["rejected"]) == 1 and v["accepted"][-1]["task"] == "T2",
          "D3 partial last line is quarantined (1 rejected) and the next harness record is accepted")


def t_d4_ids(tmp):
    p, w = fresh(tmp, "d4")
    kw = dict(lane="L", run_id="r")
    w.emit("trio", "build_end", task="T1", detail={"builder": "AGENTX"}, **kw)
    s1 = w.emit("trio", "test_start", task="T1", detail={"tester": "agentX"}, **kw)
    w.emit("trio", "build_end", task="T2", detail={"builder": " agentX "}, **kw)
    w.emit("trio", "test_start", task="T2", detail={"tester": "agentx"}, **kw)
    recs = L.verify(p, "trio")["accepted"]
    check(s1.get("rule") == L.FLAG_SAME_AGENT, "D4 writer stamps AGENTX vs agentX as tester_is_builder")
    check(sorted(r["task"] for r in L.flagged_same_agent(recs)) == ["T1", "T2"], "D4 case/space variants are flagged")
    check(sorted(r["task"] for r in L.untested_builds(recs)) == ["T1", "T2"], "D4 and they do not count as tested")
    for bad in ("  ", 7, "7", True, None):
        check(raises(L.Rejected, w.emit, "trio", "build_end", task="T3", detail={"builder": bad}, **kw) is not None,
              "D4 builder id %r refused" % (bad,))
    check(raises(L.Rejected, w.emit, "trio", "test_start", task="T3", detail={"tester": " "}, **kw) is not None,
          "D4 blank tester refused")


def t_d5_idem(tmp):
    from rimflow import model
    ev = model.read()
    recs = [r for r in V.translate_ledger(ev) if r["ts"].startswith("2026-10-25")]
    check(len(recs) > 50 and all(r["detail"].get("src") for r in recs), "D5 every adapter record carries detail.src")
    check(len({r["detail"]["src"] for r in recs}) == len(recs), "D5 source ids are unique (%d)" % len(recs))
    p, w = fresh(tmp, "d5")
    n1 = V.write(w, recs)
    n2 = V.write(w, recs)
    acc = L.verify(p, "v3")["accepted"]
    check(n1 == len(recs) and n2 == 0 and len(acc) == len(recs), "D5 --apply twice: %d then %d written, log %d"
          % (n1, n2, len(acc)))
    t = V.translate_testq([{"job": "J1", "host": "h", "started": "2026-10-29T10:00:00Z",
                            "finished": "2026-10-29T10:05:00Z", "outcome": "DONE"}], {"J1": {"item": "I"}})
    check(V.write(w, t) == 2 and V.write(w, t) == 0, "D5 testq records are idempotent too")


def t_d6_minutes(tmp):
    p, w = fresh(tmp, "d6")
    kw = dict(lane="L", run_id="r")
    for m in (True, -30, float("nan"), float("inf"), "5"):
        check(raises(L.Rejected, w.emit, "a", "owner_touch", minutes=m, **kw) is not None,
              "D6 owner_touch minutes %r refused" % (m,))
        check(raises(L.Rejected, w.emit, "a", "card", minutes=m, detail={"card_id": "c", "unblocked": []}, **kw)
              is not None, "D6 card minutes %r refused" % (m,))
    check(w.emit("a", "owner_touch", minutes=0, **kw)["minutes"] == 0, "D6 control: zero minutes accepted")


def t_d8_verdict(tmp):
    p, w = fresh(tmp, "d8")
    kw = dict(lane="L", run_id="r")
    w.emit("a", "card", minutes=5, detail={"card_id": "C1", "unblocked": ["T1"]}, **kw)
    w.emit("a", "card", minutes=5, detail={"card_id": "C1", "unblocked": ["T1"]}, **kw)
    for t, v in (("T1", "accept"), ("T2", "accept"), ("T6", "accept"), ("T6", "reject"), ("T7", "reject"),
                 ("T7", "accept")):
        w.emit("a", "judge", task=t, verdict=v, **kw)
    r = L.report(p)["a"]
    check(r["owner_minutes"] == 5, "D8 a card sent twice (same card_id) counts once: 5 minutes, not 10")
    check(r["points_with_unblocked"] == 3 and r["points_without_unblocked"] == 2,
          "D8 last verdict rules: T6 accept->reject not counted, T7 reject->accept counted (3 with / 2 without)")
    check(raises(L.Rejected, w.emit, "a", "card", minutes=1, detail={"card_id": "C2"}, **kw) is not None,
          "D8 card with no unblocked key refused")


def t_d7_recover(tmp):
    p, w = fresh(tmp, "d7")
    f = _three(w)
    lines = f.read_text().splitlines()
    f.write_text("\n".join(lines[1:]) + "\n")
    v = L.verify(p, "ralph_a")
    check(len(v["accepted"]) == 0 and len(v["rejected"]) == 3, "D7 first line deleted: nothing accepted (detected)")
    check([n for n, _ in v["recoverable"]] == [2, 3] and v["recoverable"][-1][1]["event"] == "judge",
          "D7 the later lines that still chain are listed recoverable (2 of 3; the one after the gap cannot be)")
    r = L.report(p)["ralph_a"]
    check(r["recoverable"] == 2 and bool(r.get("refused")), "D7 report shows recoverable=2 and refuses the arm")


# ---------------------------------------------------------------- fix round 2: one forced failure per GPT finding

def t_r2_1_capability(tmp):
    p, _ = fresh(tmp, "r21", writer=False)
    kw = dict(lane="L", run_id="r")
    real_entry, real_code, real_sel = L._entrypoint, L._main_code_ok, L._gate_runner_sel
    L._gate_runner_sel = lambda cmdline=None, env=None: None   # these tests swap the entry NAME: not under the gate runner
    L._main_code_ok = lambda e: None     # this test swaps the entry NAME; the code-shape check has its own R3 test
    try:
        # GPT's attack: RM_ARM cleared, cwd outside every clone, token readable, library imported from an agent script
        check(not os.environ.get("RM_ARM") and not A._inside(os.getcwd(), os.environ["ARENA_CLONES"]),
              "R2-1 setup: RM_ARM unset and cwd outside the clone root (the env/cwd checks pass)")
        L._entrypoint = lambda: str(Path(os.environ["ARENA_CLONES"]) / "ralph_a" / "forge.py")
        check(raises(L.Rejected, L.HarnessWriter, p) is not None, "R2-1 library use from an agent script: no writer")
        check(raises(L.Rejected, L.harness_pass, p) is not None, "R2-1 an agent script cannot open a pass capability")
        L._entrypoint = lambda: ""
        check(raises(L.Rejected, L.harness_pass, p) is not None, "R2-1 python3 -c / REPL cannot open a pass")
        L._entrypoint = lambda: str(L.HERE / "my_tool.py")
        check(raises(L.Rejected, L.harness_pass, p) is not None, "R2-1 a non-allowlisted script in the arena dir refused")
        L._entrypoint = lambda: str(L.HERE / "arena_v3_adapter.py")
        with L.harness_pass(p) as cap:
            w = L.HarnessWriter(p)
            rec = w.emit("ralph_a", "judge", task="T1", verdict="accept", **kw)
            pv = rec["prov"]
            st = os.stat(cap.path)
            check(pv["pid"] == os.getpid() and isinstance(pv["pid_start"], int) and pv["chain"][0][0] == os.getpid()
                  and len(pv["chain"]) >= 2 and len(pv["env_sha"]) == 16 and pv["entry"] == "arena_v3_adapter.py"
                  and pv["cap"] == cap.cap_id and pv["uid"] == os.getuid(),
                  "R2-1 signed record carries prov: pid, pid start, parent chain (%d), uid, entry, env_sha, cap id"
                  % len(pv["chain"]))
            check(st.st_mode & 0o777 == 0o600 and os.stat(cap.path.parent).st_mode & 0o777 == 0o700
                  and A._inside(cap.path, L.token_path(p).parent) and cap._nonce not in cap.path.read_text(),
                  "R2-1 capability file 0600 in a 0700 dir beside the token; the nonce itself is never on disk")
            check(raises(L.Rejected, w.emit, "ralph_a", "stop", prov={"pid": 1}, **kw) is not None,
                  "R2-1 a caller cannot pass its own prov")
            cap.path.unlink()
            check(raises(L.Rejected, w.emit, "ralph_a", "stop", **kw) is not None,
                  "R2-1 capability file deleted mid-pass: emit refused")
        check(raises(L.Rejected, w.emit, "ralph_a", "stop", **kw) is not None and not cap.path.exists(),
              "R2-1 after pass end the capability is gone and the writer refuses")
        with L.harness_pass(p) as cap2:
            w2 = L.HarnessWriter(p)
            body = cap2.path.read_bytes()
            cap2.path.write_bytes(body.replace(b'"pid"', b'"pjd"'))
            check(raises(L.Rejected, w2.emit, "ralph_a", "stop", **kw) is not None, "R2-1 capability content edited: refused")
        with L.harness_pass(p) as cap3:
            w3 = L.HarnessWriter(p)
            cap3.pid += 1
            check(raises(L.Rejected, w3.emit, "ralph_a", "stop", **kw) is not None, "R2-1 capability of another pid refused")
        with L.harness_pass(p, ttl_s=-1) as cap4:
            check(raises(L.Rejected, L.HarnessWriter, p, cap=cap4) is not None, "R2-1 expired capability refused")
        # selftest entrypoints: only with a temp, non-default token
        L._entrypoint = lambda: str(L.HERE / "selftest_arena_x.py")
        real_dflt = L._default_token_path
        L._default_token_path = lambda: L.token_path(p)
        try:
            check(raises(L.Rejected, L.harness_pass, p) is not None, "R2-1 a selftest entrypoint may not use the real token")
        finally:
            L._default_token_path = real_dflt
        saved = os.environ["ARENA_EVENT_TOKEN_FILE"]
        os.environ["ARENA_EVENT_TOKEN_FILE"] = str(Path.home() / ".local" / "state" / "rm_st_none" / "event_token")
        try:
            check(raises(L.Rejected, L.harness_pass, p) is not None, "R2-1 a selftest entrypoint with a non-temp token refused")
        finally:
            os.environ["ARENA_EVENT_TOKEN_FILE"] = saved
    finally:
        L._entrypoint, L._main_code_ok, L._gate_runner_sel = real_entry, real_code, real_sel
    # RESIDUAL, shown not hidden: the raw token + _sign() still forges a valid line; prov makes it visible only
    f = L.arm_file(p, "ralph_a")
    acc = L.verify(p, "ralph_a")["accepted"]
    tok = L.token_path(p).read_text().strip()
    forged = {"ts": "2026-10-30T00:00:00Z", "arm": "ralph_a", "lane": "L", "run_id": "r", "event": "judge",
              "task": "FAKE", "verdict": "accept"}
    forged["sig"] = L._sign(tok, acc[-1]["sig"], forged)
    with open(f, "a") as fh:
        fh.write(json.dumps(forged, sort_keys=True) + "\n")
    v = L.verify(p, "ralph_a")
    check(v["accepted"][-1]["task"] == "FAKE", "R2-1 RESIDUAL (not closed): a same-uid token reader calling _sign() "
          "directly still writes a verifying line")
    r = L.report(p)["ralph_a"]
    check(r["unprovenanced"] == 1 and not r["trusted"], "R2-1 ... and report shows it as unprovenanced=1, arm untrusted")


def t_r2_2_trust(tmp):
    p, w = fresh(tmp, "r22")
    _three(w)
    r = L.report(p)
    check(not r["ralph_a"].get("refused") and r["ralph_a"]["trusted"] is False and r["_trust"]["trusted"] is False
          and "trust_note" in r["ralph_a"], "R2-2 local anchors only: reported but NOT trusted")
    tok = L.token_path(p).read_text().strip()
    ext = L.ledger_anchors([{"event": "note", "text": L.anchor_note_text(
        [L.make_anchor("ralph_a", L.verify(p, "ralph_a")["accepted"], tok)])}])
    r = L.report(p, external=ext)
    check(r["ralph_a"]["trusted"] and r["_trust"]["trusted"], "R2-2 a ledger anchor covering the whole log: trusted")
    w.emit("ralph_a", "stop", lane="L1", run_id="r1")
    r = L.report(p, external=ext)["ralph_a"]
    check(not r["trusted"] and r["external_anchored_upto"] == 4 and r["accepted"] == 5,
          "R2-2 a record after the newest ledger anchor makes the arm untrusted again (4 of 5 covered)")
    # the token holder deletes the anchor store and writes a fresh, validly signed one: still never trusted
    L.anchor_path(p).unlink()
    L.append_anchor(p, L.make_anchor("ralph_a", L.verify(p, "ralph_a")["accepted"], tok))
    r = L.report(p)["ralph_a"]
    check(not r.get("refused") and not r["trusted"], "R2-2 a re-made local anchor store passes but is not trusted")
    L.anchor_path(p).unlink()
    Path(os.environ["ARENA_WITNESS"]).unlink()
    r = L.report(p)
    check(bool(r["ralph_a"].get("refused")) and not r["_trust"]["trusted"],
          "R2-2 anchor store missing + non-empty log: refused UNMEASURED")


def t_r2_3_v3_output(tmp):
    from rimflow import model
    recs = [r for r in V.translate_ledger(model.read()) if r["detail"].get("done") and r["detail"].get("via") == "close"][:1]
    p, w = fresh(tmp, "r23")
    V.write(w, recs)
    r = L.report(p)["v3"]
    check(r["ledger_done"] == 1 and r["output_comparable"] is False and r["points_with_unblocked"] is None
          and "arena_judge" in r["output_note"],
          "R2-3 one accepted v3 close: ledger_done=1, output NOT COMPARABLE (points None), never a silent 0")
    w.emit("v3", "judge", task=recs[0]["task"], verdict="accept", lane="v3", run_id="j")
    r = L.report(p)["v3"]
    check(r["output_comparable"] and r["points_with_unblocked"] == 1, "R2-3 control: once judged, v3 scores 1 point")


def t_r2_4_build_id(tmp):
    p, w = fresh(tmp, "r24")
    kw = dict(lane="L", run_id="r")
    w.emit("trio", "build_end", task="T", sha="s1", ts="2026-10-30T01:00:00Z", detail={"builder": "A"}, **kw)
    w.emit("trio", "build_end", task="T", sha="s2", ts="2026-10-30T01:10:00Z", detail={"builder": "B"}, **kw)
    s = w.emit("trio", "test_start", task="T", sha="s2", ts="2026-10-30T01:20:00Z", detail={"tester": "B"}, **kw)
    recs = L.verify(p, "trio")["accepted"]
    check(s.get("rule") == L.FLAG_SAME_AGENT and len(L.flagged_same_agent(recs)) == 1,
          "R2-4 B testing its own build s2 is flagged")
    check(sorted(r["sha"] for r in L.untested_builds(recs)) == ["s1", "s2"] and L.latency_minutes(recs) == [],
          "R2-4 that test does NOT clear build s1 (A's): both untested, no latency credited")
    w.emit("trio", "test_start", task="T", sha="s1", ts="2026-10-30T01:30:00Z", detail={"tester": "C"}, **kw)
    recs = L.verify(p, "trio")["accepted"]
    check([r["sha"] for r in L.untested_builds(recs)] == ["s2"] and [round(x) for x in L.latency_minutes(recs)] == [30],
          "R2-4 control: C testing s1 clears s1 only, latency 30 min from s1's build")
    w.emit("trio", "build_end", task="U", ts="2026-10-30T02:00:00Z", detail={"builder": "A", "build_id": "b9"}, **kw)
    w.emit("trio", "test_start", task="U", ts="2026-10-30T02:05:00Z", detail={"tester": "A"}, **kw)
    check(len(L.flagged_same_agent(L.verify(p, "trio")["accepted"])) == 2,
          "R2-4 a test naming no build falls back to the latest build of the task")


def t_r2_5_order(tmp):
    p, w = fresh(tmp, "r25")
    t = [{"arm": "v3", "lane": "v3", "run_id": "J", "event": "test_start", "task": "T", "ts": "2026-10-30T10:05:00Z",
          "detail": {"tester": "A", "src": "x:1"}}]
    b = [{"arm": "v3", "lane": "v3", "run_id": "J", "event": "build_end", "task": "T", "ts": "2026-10-30T10:00:00Z",
          "detail": {"builder": "A", "src": "x:2"}}]
    V.write(w, t)
    V.write(w, b)                               # a later import of the EARLIER build
    r = L.report(p)["v3"]
    check(r["flagged_same_agent"] == 1 and r["out_of_order"] == 1 and r["untested_builds"] == 1,
          "R2-5 late import of an earlier build: time order restored, self-test flagged, out_of_order=1")
    t2 = [dict(t[0], task="U", ts="2026-10-30T11:00:00Z", detail={"tester": "B", "src": "x:3"})]
    b2 = [dict(b[0], task="U", ts="2026-10-30T11:30:00Z", detail={"builder": "A", "src": "x:4"})]
    V.write(w, t2 + b2)
    r = L.report(p)["v3"]
    check(r["test_before_build"] == 1 and r["untested_builds"] == 2,
          "R2-5 a test that happened before its build is test_before_build=1 and does not clear the build")


def t_r2_6_schema(tmp):
    p, w = fresh(tmp, "r26")
    kw = dict(lane="L", run_id="r")
    for name, args in (("list card_id", ("card", {"minutes": 1, "detail": {"card_id": ["C"], "unblocked": []}})),
                       ("unblocked=[{}]", ("card", {"minutes": 1, "detail": {"card_id": "C", "unblocked": [{}]}})),
                       ("unblocked=['']", ("card", {"minutes": 1, "detail": {"card_id": "C", "unblocked": [""]}})),
                       ("blank card_id", ("card", {"minutes": 1, "detail": {"card_id": " ", "unblocked": []}})),
                       ("naive ts", ("stop", {"ts": "2026-10-30T10:00:00"})),
                       ("garbage ts", ("stop", {"ts": "yesterday"})),
                       ("numeric task", ("judge", {"task": 5, "verdict": "accept"})),
                       ("list verdict", ("judge", {"task": "T", "verdict": ["accept"]})),
                       ("bad minutes on any event", ("defect", {"minutes": "5"})),
                       ("NaN inside detail", ("defect", {"detail": {"x": float("nan")}})),
                       ("blank build_id", ("build_end", {"task": "T", "detail": {"builder": "A", "build_id": ""}}))):
        check(raises(L.Rejected, w.emit, "a", args[0], **kw, **args[1]) is not None, "R2-6 schema rejects " + name)
    w.emit("a", "stop", ts="2026-10-30T12:00:00+02:00", **kw)
    check(L.ts_epoch(L.verify(p, "a")["accepted"][-1]["ts"]) == L.ts_epoch("2026-10-30T10:00:00Z"),
          "R2-6 control: an offset ts is accepted and compared in UTC")
    old = [{"event": "card", "minutes": 1, "detail": {"card_id": ["C"], "unblocked": []}},
           {"event": "card", "minutes": 1, "detail": {"card_id": "D", "unblocked": [{}]}},
           {"event": "card", "minutes": 2, "detail": {"card_id": "E", "unblocked": ["T"]}}]
    om = raises(Exception, L.owner_minutes, old)
    check(om is None and L.owner_minutes(old)["malformed_cards"] == 2 and L.owner_minutes(old)["minutes"] == 2,
          "R2-6 malformed cards already in a log are skipped and counted, owner_minutes does not crash")


def t_r2_7_testq(tmp):
    p, w = fresh(tmp, "r27")
    kw = dict(lane="v3", run_id="v3-ledger")
    for t in ("I1", "I2", "I3"):
        w.emit("v3", "build_end", task=t, ts="2026-10-30T09:00:00Z", detail={"builder": "FOUNDRY", "src": "b" + t}, **kw)
    jobs = {"J1": {"item": "I1", "requested_by": "FOUNDRY"}, "J2": {"item": "I2", "requested_by": "BENCH"},
            "J3": {"item": "I3"}}
    res = [{"job": j, "host": "stevedesktop", "started": "2026-10-30T10:00:00Z"} for j in ("J1", "J2", "J3")]
    recs = V.translate_testq(res, jobs)
    check([r["detail"]["tester"] for r in recs] == ["FOUNDRY", "BENCH", "unattributed:testq:stevedesktop"]
          and all(r["detail"]["runner"] == "testq:stevedesktop" for r in recs)
          and [r["detail"]["submitted_by"] for r in recs] == ["FOUNDRY", "BENCH", None],
          "R2-7 testq tester = submitting seat; runner host and submitter both recorded")
    V.write(w, recs)
    acc = L.verify(p, "v3")["accepted"]
    check([r["task"] for r in L.flagged_same_agent(acc)] == ["I1"],
          "R2-7 builder FOUNDRY running its own testq is flagged (was cleared as 'testq:<host>')")
    check(sorted(r["task"] for r in L.untested_builds(acc)) == ["I1", "I3"],
          "R2-7 only BENCH's run clears a build; an unattributed run never counts as a different agent")


def t_r2_8_window(tmp):
    d0 = L.ts_epoch("2026-10-24T00:00:00Z")
    mk = lambda ts: {"ts": ts, "detail": {"done": True, "via": "close"}}
    recs = [mk("2026-10-23T23:59:59Z"), mk("2026-10-24T00:00:00Z"), mk("2026-10-24T23:59:59Z"),
            mk("2026-10-25T00:00:00Z"), mk("2026-10-24T01:30:00+02:00")]   # the last is 23:30 on the 23rd UTC
    check(V.done_count(recs, d0, d0 + 86400) == 2 and V.done_count(recs, d0, d0 + 86400, "close") == 2,
          "R2-8 day window is half-open UTC [00:00, 24:00): boundary seconds land on exactly one day, offsets in UTC")


def t_r2_9_anchor_neg(tmp):
    p, w = fresh(tmp, "r29")
    _three(w)
    ext = L.ledger_anchors([{"event": "note", "tsn": 7, "text": "ARENA_ANCHOR ralph_a:-1:%s ralph_a:0:%s" % ("a" * 64, "b" * 64)}])
    crash = raises(Exception, L.report, p, external=ext)
    r = L.report(p, external=ext)["ralph_a"] if crash is None else {}
    check(crash is None and len(r.get("anchor_errors", [])) == 2 and not r.get("refused") and not r["trusted"],
          "R2-9 negative / inconsistent external anchors: report does not crash, both listed in anchor_errors, unused")
    check(raises(Exception, L.check_anchors, [], [{"n": -1, "head": "x"}]) is None,
          "R2-9 check_anchors([], n=-1) (the partial-log probe) does not raise")


# ---------------------------------------------------------------- fix round 3: one forced failure per tester finding

def _mk(w, arm, n):
    for i in range(n):
        w.emit(arm, "judge", lane="l", run_id="r", task="J%d" % i, verdict="accept", ts="2026-10-21T00:%02d:00Z" % i)
    return L.verify(w.p, arm)["accepted"]


def _trim_anchors(p, keep):
    af = L.anchor_path(p)
    al = [l for l in af.read_text().splitlines() if l.strip()]
    af.write_text("".join(l + "\n" for l in al if keep(json.loads(l))))


def t_r3_b1_tail(tmp):
    p, w = fresh(tmp, "r3b1")
    tok = L.token_path(p).read_text().strip()
    acc = _mk(w, "b", 8)
    ext = L.ledger_anchors([{"event": "note", "tsn": 1, "text": L.anchor_note_text([L.make_anchor("b", acc[:5], tok)])}])
    fb = L.arm_file(p, "b")
    fb.write_text("".join(l + "\n" for l in fb.read_text().splitlines()[:5]))
    _trim_anchors(p, lambda a: not (a["arm"] == "b" and a["n"] > 5))
    r = L.report(p, external=ext)
    check(r["b"]["accepted"] == 5 and r["b"].get("refused") and not r["b"]["trusted"] and not r["_trust"]["trusted"],
          "R3-B1 tokenless: tail past the newest ledger anchor deleted + local anchors trimmed -> REFUSED by the "
          "witness (%s)" % (r["b"].get("refused"),))
    os.environ["ARENA_WITNESS"] = "off"
    r = L.report(p, external=ext)["b"]
    check(not r["trusted"] and "witness off" in r.get("trust_note", ""),
          "R3-B1 witness off: never trusted (fails closed), says why")


def t_r3_b2_forged_note(tmp):
    p, w = fresh(tmp, "r3b2")
    tok = L.token_path(p).read_text().strip()
    acc = _mk(w, "c", 6)
    good = L.anchor_note_text([L.make_anchor("c", acc, tok)])
    r = L.report(p, external=L.ledger_anchors([{"event": "note", "tsn": 1, "text": good}]))
    check(r["c"]["trusted"] and r["_trust"]["trusted"], "R3-B2 control: a harness-signed note covering the log: trusted")
    head = acc[5]["sig"]
    for name, text in (("unsigned", "ARENA_ANCHOR c:6:%s" % head),
                       ("bad hmac", "ARENA_ANCHOR c:6:%s:%s" % (head, "0" * 64)),
                       ("lsig of another anchor", "ARENA_ANCHOR c:6:%s:%s" % (head, L.make_anchor("c", acc[:2], tok)["lsig"]))):
        ext = L.ledger_anchors([{"event": "note", "id": "SOME_UNRELATED_ITEM", "seat": "ARM_AGENT", "tsn": 2, "text": text}])
        r = L.report(p, external=ext)["c"]
        check(not r["trusted"] and len(r.get("anchor_errors", [])) == 1 and "ARM_AGENT" in r["anchor_errors"][0]
              and r["external_anchored_upto"] == 0,
              "R3-B2 forged ARENA_ANCHOR (%s) from another seat/item: listed in anchor_errors, confers no trust" % name)


def t_r3_b3_roster(tmp):
    p, w = fresh(tmp, "r3b3")
    tok = L.token_path(p).read_text().strip()
    _mk(w, "b", 2)
    _mk(w, "d", 3)
    ext = L.ledger_anchors([{"event": "note", "tsn": 1, "text": L.anchor_note_command(p).split("--text '")[1].rstrip("'")}])
    r = L.report(p, external=ext)
    check(r["_trust"]["trusted"] and r["_trust"]["rostered_arms"] == ["b", "d"],
          "R3-B3 control: both arms rostered, signed note incl. @roster: trusted")
    L.arm_file(p, "d").unlink()
    _trim_anchors(p, lambda a: a["arm"] != "d")
    r = L.report(p, external=ext)
    check("d" in r and r["d"].get("refused") and not r["_trust"]["trusted"] and "d" in r["_trust"]["untrusted_arms"],
          "R3-B3 tokenless: rostered arm d deleted (log + anchors): still reported, REFUSED, _trust False")
    rf = L.roster_path(p)
    rl = rf.read_text().splitlines()
    rf.write_text(rl[0] + "\n")                                  # drop d's roster line too
    r = L.report(p, external=ext)
    check(not r["_trust"]["trusted"] and r["_trust"].get("roster_problems") and r.get("d", {}).get("refused"),
          "R3-B3 roster line removed as well: witness + published @roster still name d (%s)" % r["_trust"].get("roster_problems"))
    rf.write_text(rl[1] + "\n")                                  # drop the FIRST line: chain break
    check(L.read_roster(p, tok)["bad"] and not L.report(p, external=ext)["_trust"]["trusted"],
          "R3-B3 a middle/first roster line removed: chain break listed, untrusted")


def t_r3_b4_note_tokens(tmp):
    p, w = fresh(tmp, "r3b4")
    acc = _mk(w, "b", 5)
    h = acc[-1]["sig"]
    for k, t in (("5.0", "ARENA_ANCHOR b:5.0:%s" % h), ("5e0", "ARENA_ANCHOR b:5e0:%s" % h),
                 ("extra colon", "ARENA_ANCHOR b:5:%s:x" % h), ("arabic digit", "ARENA_ANCHOR b:\u0665:%s" % h),
                 ("leading space", " ARENA_ANCHOR b:99:%s" % h), ("fullwidth digit", "ARENA_ANCHOR b:\uff15:%s:%s" % (h, h))):
        r = L.report(p, external=L.ledger_anchors([{"event": "note", "tsn": 9, "text": t}]))["b"]
        check(len(r.get("anchor_errors", [])) == 1 and not r.get("refused") and not r["trusted"],
              "R3-B4 anchor note token %s: listed in anchor_errors, not dropped, not applied" % k)


def t_r3_entrypoint(tmp):
    import subprocess
    import __main__
    p, _ = fresh(tmp, "r3ep", writer=False)
    saved = (getattr(__main__, "__file__", None), sys.argv[0], L._ENTRY)
    try:
        __main__.__file__ = str(L.HERE / "arena_eventlog.py")
        sys.argv[0] = str(L.HERE / "arena_v3_adapter.py")
        L._ENTRY = None
        e = L._entrypoint()
    finally:
        __main__.__file__, sys.argv[0], L._ENTRY = saved
    want_entry = "gate_runner.py" if L._gate_runner_sel() else "selftest_arena_eventlog.py"   # under the gate the runner is __main__
    check(os.path.basename(e) == want_entry,
          "R3-A2 forging __main__.__file__ / sys.argv[0] does not change the entrypoint (%s)" % os.path.basename(e))
    forge = ("import sys, __main__; sys.path.insert(0, %r); __main__.__file__ = %r; sys.argv[0] = __main__.__file__\n"
             "import arena_eventlog as L, arena_tasks as A\n"
             "try:\n    L.harness_pass(A.paths()); print('OPENED')\nexcept L.Rejected as e:\n    print('REFUSED', e)\n"
             % (str(L.HERE), str(L.HERE / "arena_eventlog.py")))
    env = dict(os.environ)
    out = subprocess.run([sys.executable, "-c", forge], capture_output=True, text=True, env=env, cwd=str(tmp), timeout=120)
    check(out.stdout.startswith("REFUSED"), "R3-A2 `python3 -c` with forged __main__.__file__ cannot open a pass (%s)"
          % (out.stdout.strip() or out.stderr.strip())[-120:])
    sc = tmp / "arena_eventlog.py"
    sc.write_text(forge)
    out = subprocess.run([sys.executable, str(sc)], capture_output=True, text=True, env=env, cwd=str(tmp), timeout=120)
    check(out.stdout.startswith("REFUSED"), "R3-A2 a script NAMED arena_eventlog.py outside the arena dir is refused (%s)"
          % (out.stdout.strip() or out.stderr.strip())[-120:])
    out = subprocess.run([sys.executable, str(sc)], capture_output=True, text=True, env=dict(env, PWD=str(L.HERE)),
                         cwd=str(tmp), timeout=120)
    check(out.stdout.startswith("REFUSED"), "R3-A2 ... also with PWD spoofed to the arena dir (%s)"
          % (out.stdout.strip() or out.stderr.strip())[-120:])


def t_r3_a4c_fd_reuse(tmp):
    p, _ = fresh(tmp, "r3a4", writer=False)
    cap = L.harness_pass(p)
    w = L.HarnessWriter(p, cap=cap)
    cap.close(); L._ACTIVE.discard(cap)
    cap.closed = False
    fd = os.open(str(cap.path), os.O_RDWR | os.O_CREAT, 0o600)
    os.write(fd, cap._body)
    try:
        check(raises(L.Rejected, w.emit, "a", "stop", lane="l", run_id="r") is not None,
              "R3-A4c cap file recreated on fd %d (was %d) after pass end: emit refused" % (fd, cap._fd))
    finally:
        os.close(fd); os.unlink(cap.path); cap.closed = True


def t_r3_testq_real(tmp):
    fx = HERE / "fixtures" / "testq_done"
    res, jobs = V.load_testq(fx)
    recs = V.translate_testq(res, jobs)
    check(len(list(fx.glob("*.json"))) == 5 and len(res) == 5 and len(jobs) == 5,
          "R3-T1 5 real wrapped done records {job, result, attempts}: 5 results + 5 jobs parsed (was 0)")
    check(len(recs) == 6 and sorted({r["detail"]["tester"] for r in recs}) == ["BENCH", "FOUNDRY"]
          and all(r["detail"]["src"].startswith("testq:J") and ".a" in r["detail"]["src"] for r in recs),
          "R3-T1 the 3 records with an item -> 6 records, tester = seat, src per attempt (item-less canary jobs skip)")
    rerun = [j for j in jobs.values() if j["requested_by"] == "BENCH.filler"]
    check(rerun and V.seat_of("BENCH.filler") == "BENCH" and any(r.get("attempt", "").endswith(".a2") for r in res),
          "R3-T1 fixture holds a BENCH.filler job and a 2-attempt job; BENCH.filler -> seat BENCH")


def t_r3_testq_attempts(tmp):
    p, w = fresh(tmp, "r3d3")
    kw = dict(lane="v3", run_id="v3-ledger")
    w.emit("v3", "build_end", task="I1", ts="2026-10-30T09:00:00Z", detail={"builder": "BENCH", "src": "b1"}, **kw)
    jobs = {"J1": {"id": "J1", "item": "I1", "requested_by": "BENCH.filler"}}
    res = [{"job": "J1", "attempt": "J1.a1", "host": "h", "started": "2026-10-30T10:00:00Z", "finished": "2026-10-30T10:05:00Z", "outcome": "FAIL"},
           {"job": "J1", "attempt": "J1.a2", "host": "h", "started": "2026-10-30T11:00:00Z", "finished": "2026-10-30T11:05:00Z", "outcome": "PASS"}]
    check(V.write(w, V.translate_testq(res, jobs)) == 4, "R3-D3 a testq re-run (attempt a2) is kept: 4 records written, not 2")
    acc = L.verify(p, "v3")["accepted"]
    check(len(L.flagged_same_agent(acc)) == 2 and len(L.untested_builds(acc)) == 1,
          "R3-D4 BENCH.filler testing a BENCH build: flagged as the builder's own seat, build stays untested")


def _B(ts, who, sha=None, d=None):
    return {"ts": ts, "event": "build_end", "task": "T", "sha": sha, "detail": dict(d or {}, builder=who)}


def _T(ts, who, sha=None, d=None):
    return {"ts": ts, "event": "test_start", "task": "T", "sha": sha, "detail": dict(d or {}, tester=who)}


def t_r3_analysis(tmp):
    cases = (("C2 test names the sha of a build that has build_id", [_B("2026-10-29T10:00:00Z", "X", "s1", {"build_id": "b1"}), _T("2026-10-29T10:10:00Z", "X", "s1")]),
             ("C3 test names a nonexistent build_id", [_B("2026-10-29T10:00:00Z", "X", d={"build_id": "b1"}), _T("2026-10-29T10:10:00Z", "X", d={"build_id": "nope"})]),
             ("C3b build has no id, test names one", [_B("2026-10-29T10:00:00Z", "X"), _T("2026-10-29T10:10:00Z", "X", d={"build_id": "b1"})]),
             ("C4 test 30 s before its build (skew)", [_B("2026-10-29T10:00:30Z", "X"), _T("2026-10-29T10:00:00Z", "X")]),
             ("C5 test earlier in UTC via +02:00", [_B("2026-10-29T10:00:00Z", "X"), _T("2026-10-29T11:30:00+02:00", "X")]),
             ("C6 equal ts, test line first", [_T("2026-10-29T10:00:00Z", "X"), _B("2026-10-29T10:00:00Z", "X")]),
             ("C7 zero-width tester", [_B("2026-10-29T10:00:00Z", "agentx"), _T("2026-10-29T10:10:00Z", "agentx\u200b")]),
             ("C7 fullwidth tester", [_B("2026-10-29T10:00:00Z", "agentx"), _T("2026-10-29T10:10:00Z", "\uff41gentx")]))
    for name, recs in cases:
        check(len(L.flagged_same_agent(recs)) == 1, "R3 %s: same-agent test flagged" % name)
    c2 = cases[0][1]
    check(len(L.untested_builds(c2)) == 1 and len(L.untested_builds(cases[1][1])) == 1,
          "R3 a same-agent test of a non-matching id earns no 'tested' credit")
    check(len(L.ambiguous_order(cases[3][1])) == 1 and len(L.ambiguous_order(cases[5][1])) == 1
          and not L.ambiguous_order(c2), "R3 C4/C6 clock skew / equal ts reported as ambiguous_order")
    other = [_B("2026-10-29T10:00:00Z", "X", "s1", {"build_id": "b1"}), _T("2026-10-29T10:10:00Z", "Y", "s1")]
    check(not L.flagged_same_agent(other) and not L.untested_builds(other),
          "R3 control: a DIFFERENT agent naming the sha tests the build (credited, not flagged)")


def t_r3_cards(tmp):
    mk = lambda ts, cid, m, un: {"ts": ts, "event": "card", "minutes": m, "detail": {"card_id": cid, "unblocked": un}}
    recs = [mk("2026-10-29T12:00:00Z", "C1", 9, ["T9"]), mk("2026-10-29T10:00:00Z", "c1 ", 5, [" T1 "]),
            mk("2026-10-29T11:00:00Z", "C\u200b1", 5, ["T1"])]
    om = L.owner_minutes(recs)
    check(om["cards"] == 1 and om["card_minutes"] == 5 and om["unblocked_tasks"] == ["T1"] and om["card_conflicts"] == 1,
          "R3-C9 card ids C1 / 'c1 ' / C<zwsp>1 are one card; the EARLIEST by time wins; conflicting dup counted (%s)" % om)
    check(not L._minutes_ok(10 ** 309) and raises(L.Rejected, L.validate_record, {
        "ts": "2026-10-29T10:00:00Z", "arm": "a", "lane": "l", "run_id": "r", "event": "owner_touch", "minutes": 10 ** 309}) is not None,
          "R3-C9 minutes = 10**309 refused (Rejected), not an OverflowError crash")


def t_r4_small(tmp):
    check(V.seat_of("BENCH\uff0efiller") == "BENCH" and V.seat_of("BENCH.filler") == "BENCH" and V.seat_of(" ") is None,
          "R4-a fullwidth-dot submitter 'BENCH<U+FF0E>filler' is seat BENCH (NFKC before the split)")
    jobs = {"J1": {"item": "I1", "requested_by": "BENCH\uff0efiller"}}
    r = V.translate_testq([{"job": "J1", "host": "h", "started": "2026-10-30T10:00:00Z"}], jobs)
    check(r[0]["detail"]["tester"] == "BENCH", "R4-a translate_testq tester is BENCH for a fullwidth-dot submitter")
    # b: judge task key is stripped like card tasks
    mk = lambda ts, task, v: {"ts": ts, "event": "judge", "task": task, "verdict": v}
    acc = L.accepted_tasks([mk("2026-10-29T10:00:00Z", "T1", "reject"), mk("2026-10-29T11:00:00Z", " T1 ", "accept")])
    check(acc == {"T1"}, "R4-b judge task ' T1 ' is task T1 (later accept wins over an earlier reject)")
    cards = [{"ts": "2026-10-29T09:00:00Z", "event": "card", "minutes": 5, "detail": {"card_id": "C", "unblocked": ["T1"]}},
             mk("2026-10-29T11:00:00Z", "T1 ", "accept")]
    check(L.output_report(cards)["owner_unblocked_accepted"] == ["T1"], "R4-b padded judge task still counts as owner-unblocked")
    b = {"ts": "2026-10-29T10:00:00Z", "event": "build_end", "task": "T ", "detail": {"builder": "X"}}
    t = {"ts": "2026-10-29T10:10:00Z", "event": "test_start", "task": "T", "detail": {"tester": "Y"}}
    check(not L.untested_builds([b, t]), "R4-b a padded build task matches its test")
    # c: unattributed builder never makes a different agent
    ub = {"ts": "2026-10-29T10:00:00Z", "event": "build_end", "task": "T", "detail": {"builder": "unattributed:ledger"}}
    check(len(L.untested_builds([ub, t])) == 1, "R4-c unattributed builder + tester Y: build stays untested")
    check(len(L.untested_builds([dict(ub, detail={"builder": "  "}), t])) == 1, "R4-c blank builder: build stays untested")
    # d: invalid UTF-8 append costs one line
    p, w = fresh(tmp, "r4d")
    for i in range(2):
        w.emit("a", "build_end", task="T%d" % i, ts="2026-10-30T09:0%d:00Z" % i, detail={"builder": "X", "src": "s%d" % i}, lane="l", run_id="r")
    f = L.arm_file(p, "a")
    with open(f, "ab") as fh:
        fh.write(b'{"bad": "\xff\xfe"}\n')
    L.init_roster(p, ["a"]) if hasattr(L, "init_roster") else None
    try:
        rep = L.report(p)
        check(rep["a"]["accepted"] == 2 and rep["a"]["undecodable_lines"] == 1 and rep["a"]["rejected"] == 1,
              "R4-d invalid UTF-8 line: report() survives, 2 accepted, 1 rejected, undecodable_lines=1")
    except UnicodeDecodeError:
        check(False, "R4-d report() crashed on invalid UTF-8")
    # e: synthetic wrapper with attempts (id strings) + result: latest result ingested
    d = Path(tmp) / "r4e"; d.mkdir()
    (d / "x.json").write_text(json.dumps({"job": {"schema": "testq.job/1", "id": "J9", "item": "I9"},
        "result": {"schema": "testq.result/1", "job": "J9", "attempt": "J9.a2", "host": "h"}, "attempts": ["J9.a1", "J9.a2"]}))
    res, jobs = V.load_testq(d)
    check(len(res) == 1 and res[0]["attempt"] == "J9.a2" and "J9" in jobs,
          "R4-e wrapper with attempts=[ids] + result: the one real result is ingested (attempts hold no results)")


def _stat(path):
    try:
        s = os.stat(path)
        return (s.st_size, s.st_mtime_ns)
    except OSError:
        return None


def _gate_probe():
    """Run only when RM_EVLOG_GATE_PROBE is set (by t_gate_runner, under a real gate runner command line)."""
    try:
        L.harness_pass(A.paths())
        print("OPENED entry=%s" % L._entry_name())
    except L.Rejected as e:
        print("REFUSED", e)
    return 0


def t_gate_runner(tmp):
    import hashlib
    import subprocess
    import arena_gate as G
    sha = G.runner_sha256()
    rd = tmp / "gr"
    rd.mkdir(exist_ok=True)
    runner = rd / G.GATE_RUNNER_NAME
    runner.write_text(G.RUNNER_SRC, encoding="utf-8")
    sel = str(L.HERE / "selftest_arena_eventlog.py")
    base = dict(os.environ, RM_EVLOG_GATE_PROBE="1", ARENA_EVENT_TOKEN_FILE=str(tmp / "gr_token"))
    # a DUMMY token of our own: absent, it trips the fail-closed same-file compare against the real harness token
    # whenever that exists (ARENA_EVLOG_SELFTEST_FIX_GRA_TOKEN_UNREAD). The real token is never read or touched.
    (tmp / "gr_token").write_text("f" * 64, encoding="utf-8")
    os.chmod(tmp / "gr_token", 0o600)
    base.pop("RM_ARM", None)
    base.pop("RM_GATE_RUNNER", None)   # when this selftest itself runs under the gate runner the marker is inherited

    def launch(env, rpath=runner, target=sel):
        r, w = os.pipe()
        try:
            pr = subprocess.run([sys.executable, "-I", str(rpath), str(w), target], capture_output=True, text=True,
                                input="0123456789abcdef0123456789abcdef\nENTRIES main\n", env=env, cwd=str(tmp),
                                timeout=120, pass_fds=(w,))
        finally:
            os.close(w)
            os.close(r)
        return pr.stdout.strip() or pr.stderr.strip()
    out = launch(dict(base, RM_GATE_RUNNER=sha))
    check(out.startswith("OPENED") and "entry=selftest_arena_eventlog.py" in out,
          "GR-a the real gate runner command line + env marker passes the entrypoint check (%s)" % out[-110:])
    out = launch(base)
    check("REFUSED" in out and "OPENED" not in out, "GR-b1 no env marker: refused (%s)" % out[-110:])
    out = launch(dict(base, RM_GATE_RUNNER="0" * 64))
    check("REFUSED" in out and "OPENED" not in out, "GR-b2 wrong sha in the env marker: refused (%s)" % out[-110:])
    alt = rd / "alt"
    alt.mkdir(exist_ok=True)
    (alt / G.GATE_RUNNER_NAME).write_text(G.RUNNER_SRC + "\n# edited copy\n", encoding="utf-8")
    out = launch(dict(base, RM_GATE_RUNNER=sha), rpath=alt / G.GATE_RUNNER_NAME)
    check("REFUSED" in out and "OPENED" not in out, "GR-b3 a runner copy that is not byte-identical: refused (%s)" % out[-110:])
    out = launch(dict(base, RM_GATE_RUNNER=hashlib.sha256((G.RUNNER_SRC + "\n# edited copy\n").encode()).hexdigest()),
                 rpath=alt / G.GATE_RUNNER_NAME)
    check("REFUSED" in out and "OPENED" not in out, "GR-b3b ... even with the marker set to the copy's own sha (%s)" % out[-110:])
    (rd / "cp").mkdir(exist_ok=True)
    cp = rd / "cp" / "selftest_arena_eventlog.py"
    shutil.copyfile(sel, cp)
    out = launch(dict(base, RM_GATE_RUNNER=sha), target=str(cp))
    check("OPENED" not in out, "GR-b4 the selftest copied outside the arena dir does not open a pass (%s)" % out[-110:])
    forge = ("import sys, __main__; sys.path.insert(0, %r); __main__.__file__ = %r; sys.argv[0] = __main__.__file__\n"
             "import arena_eventlog as L, arena_tasks as A\n"
             "try:\n    L.harness_pass(A.paths()); print('OPENED')\nexcept L.Rejected as e:\n    print('REFUSED', e)\n"
             % (str(L.HERE), sel))
    pr = subprocess.run([sys.executable, "-c", forge], capture_output=True, text=True,
                        env=dict(base, RM_GATE_RUNNER=sha), cwd=str(tmp), timeout=120)
    check(pr.stdout.startswith("REFUSED"), "GR-b5 a spoofed __main__.__file__ with the marker set is refused (%s)"
          % (pr.stdout.strip() or pr.stderr.strip())[-120:])
    saved = L._gate_runner_sel
    try:
        for bad, why in ((str(L.HERE / "arena_eventlog.py"), "name outside the selftest_arena_ prefix"),
                         (str(L.HERE / "arena_gate.py"), "a harness module that is not a selftest"),
                         (str(tmp / "selftest_arena_x.py"), "right prefix, wrong dir")):
            L._gate_runner_sel = lambda cmdline=None, env=None, b=bad: b
            try:
                L._check_entrypoint(A.paths())
                got = "accepted"
            except L.Rejected as e:
                got = "rejected: %s" % str(e)[:60]
            check(got.startswith("rejected"), "GR-b6 gate says %s: %s" % (why, got))
    finally:
        L._gate_runner_sel = saved


def t_switch_entry(tmp):
    import subprocess
    p, _ = fresh(tmp, "sw", writer=False)
    kw = dict(lane="none", run_id="switch-1")
    det = {"from": "ralph_a", "to": "stopped", "stopped": ["ralph_a"], "waited_s": 1.0}
    real_entry, real_code, real_sel = L._entrypoint, L._main_code_ok, L._gate_runner_sel
    L._gate_runner_sel = lambda cmdline=None, env=None: None   # these tests swap the entry NAME: not under the gate runner
    L._main_code_ok = lambda e: None
    try:
        L._entrypoint = lambda: str(L.HERE / "arena.py")
        with L.harness_pass(p) as cap:
            rec = L.HarnessWriter(p, cap=cap).emit("stopped", "switch", detail=det, **kw)
        L.validate_record(rec)
        check(rec["prov"]["entry"] == "arena.py", "SW-1 arena.py's entry path signs a valid switch event")
        for nm, ent in (("other name", L.HERE / "arena_x.py"), ("other dir", tmp / "arena.py"),
                        ("subdir copy", L.HERE / "sub" / "arena.py")):
            L._entrypoint = lambda e=ent: str(e)
            check(raises(L.Rejected, L.harness_pass, p) is not None, "SW-2 %s: refused" % nm)
    finally:
        L._entrypoint, L._main_code_ok, L._gate_runner_sel = real_entry, real_code, real_sel
    # a real copy of arena.py outside the arena dir, and a spoofed __main__.__file__, run as real processes
    forge = ("import sys, __main__; sys.path.insert(0, %r); __main__.__file__ = %r; sys.argv[0] = __main__.__file__\n"
             "import arena_eventlog as L, arena_tasks as A\n"
             "try:\n    L.harness_pass(A.paths()); print('OPENED')\nexcept L.Rejected as e:\n    print('REFUSED', e)\n"
             % (str(L.HERE), str(L.HERE / "arena.py")))
    out = subprocess.run([sys.executable, "-c", forge], capture_output=True, text=True, env=dict(os.environ),
                         cwd=str(tmp), timeout=120)
    check(out.stdout.startswith("REFUSED"), "SW-3 spoofed __main__.__file__ = arena.py refused (%s)"
          % (out.stdout.strip() or out.stderr.strip())[-100:])
    cp = tmp / "arena.py"
    cp.write_text(forge)
    out = subprocess.run([sys.executable, str(cp)], capture_output=True, text=True, env=dict(os.environ),
                         cwd=str(tmp), timeout=120)
    check(out.stdout.startswith("REFUSED"), "SW-4 a copy named arena.py in another dir refused (%s)"
          % (out.stdout.strip() or out.stderr.strip())[-100:])
    base = {"ts": "2026-10-29T00:00:00Z", "arm": "stopped", "event": "switch", "lane": "none", "run_id": "r"}
    check(raises(L.Rejected, L.validate_record, dict(base, detail=det)) is None, "SW-5 a complete switch validates")
    for k in ("from", "to"):
        check(raises(L.Rejected, L.validate_record, dict(base, detail={a: b for a, b in det.items() if a != k}))
              is not None, "SW-6 switch missing detail.%s rejected" % k)
    check(raises(L.Rejected, L.validate_record, dict(base)) is not None, "SW-6 switch with no detail rejected")
    check(raises(L.Rejected, L.validate_record, dict(base, detail=dict(det, stopped="ralph_a"))) is not None,
          "SW-6 switch with non-list stopped rejected")


def _calib_detail(**over):
    m = lambda k, n, thr: {"k": k, "n": n, "wilson95": [0.1, 0.6], "threshold": thr}
    d = {"critic": "critic_x", "set_sha256": "ab" * 32, "invalid": 0, "candidates": 39,
         "false_reject": m(2, 9, 0.25), "miss": m(8, 9, 0.5)}
    d.update(over)
    return d


def t_calib_entry(tmp):
    """ARENA_EVENTLOG_WIRE_CALIB_ENTRYPOINT: arena_critic_calib.py score, run as a real process, signs its counts and
    intervals as a `calib` event; an arm process cannot; the calibration arm is never analysed as a competing arm."""
    import subprocess
    import arena_analysis as AN
    import arena_critic_calib as CC
    p, _ = fresh(tmp, "cal", writer=False)
    run = "st-run"
    rd = CC.calib_root() / run
    rd.mkdir(parents=True)
    sha = CC.load_set()["set_sha256"]
    (rd / "run.json").write_text(json.dumps({"run": run, "critic": "critic_st", "critic_fingerprint": "f" * 16,
                                             "set_sha256": sha}))
    (rd / "results.jsonl").write_text("")
    script = str(L.HERE / "arena_critic_calib.py")
    out = subprocess.run([sys.executable, script, "score", "--run", run], capture_output=True, text=True,
                         env=dict(os.environ), cwd=str(tmp), timeout=300)
    acc = L.verify(p, L.CALIB_ARM)["accepted"]
    r = acc[-1] if acc else {}
    d = r.get("detail") or {}
    check(out.returncode == 0 and len(acc) == 1 and r.get("event") == "calib"
          and (r.get("prov") or {}).get("entry") == "arena_critic_calib.py",
          "CAL-1 arena_critic_calib.py score (real process) signs one calib event (rc %s, %d accepted; %s)"
          % (out.returncode, len(acc), (out.stderr.strip() or out.stdout.strip())[-160:]))
    sc = json.loads((rd / "score.json").read_text())
    check(r.get("verdict") == sc["reliability"]["verdict"] and d.get("set_sha256") == sha
          and d.get("critic") == "critic_st" and d.get("candidates") == sc["candidates"] > 0
          and d.get("invalid") == sc["invalid"]
          and all(d.get(k) == {f: sc[k][f] for f in ("k", "n", "wilson95", "threshold")}
                  for k in CC.CALIB_EVENT_RATES),
          "CAL-2 the signed counts/intervals/verdict equal score.json (%s, %d candidates)"
          % (r.get("verdict"), sc["candidates"]))
    out = subprocess.run([sys.executable, script, "score", "--run", run], capture_output=True, text=True,
                         env=dict(os.environ, RM_ARM="ralph_a"), cwd=str(tmp), timeout=300)
    check(out.returncode == 3 and "NOT SIGNED" in out.stderr and len(L.verify(p, L.CALIB_ARM)["accepted"]) == 1,
          "CAL-3 an arm process (RM_ARM) is refused loudly (rc 3) and signs nothing (rc %s)" % out.returncode)
    out = subprocess.run([sys.executable, script, "score", "--run", run, "--no-eventlog"], capture_output=True,
                         text=True, env=dict(os.environ, RM_ARM="ralph_a"), cwd=str(tmp), timeout=300)
    check(out.returncode == 0, "CAL-4 --no-eventlog writes score.json only (rc %s)" % out.returncode)
    # schema: the calib arm holds only calib events, a calib event lives only there, counts and intervals are sane
    base = {"ts": "2026-10-30T00:00:00Z", "arm": L.CALIB_ARM, "event": "calib", "lane": "calib", "run_id": "r",
            "verdict": "UNRELIABLE"}
    check(raises(L.Rejected, L.validate_record, dict(base, detail=_calib_detail())) is None,
          "CAL-5 a complete calib event validates")
    m = lambda **kw: dict({"k": 1, "n": 9, "wilson95": [0.1, 0.6], "threshold": 0.5}, **kw)
    bad = (("on another arm", dict(base, arm="ralph_a", detail=_calib_detail())),
           ("other event on the calib arm", dict(base, event="switch", detail={"from": "a", "to": "b"})),
           ("no verdict", {k: v for k, v in dict(base, detail=_calib_detail()).items() if k != "verdict"}),
           ("unknown verdict", dict(base, verdict="GOOD", detail=_calib_detail())),
           ("no critic", dict(base, detail=_calib_detail(critic=""))),
           ("no set", dict(base, detail=_calib_detail(set_sha256=None))),
           ("no miss", dict(base, detail={k: v for k, v in _calib_detail().items() if k != "miss"})),
           ("k > n", dict(base, detail=_calib_detail(miss=m(k=10)))),
           ("bool count", dict(base, detail=_calib_detail(miss=m(k=True)))),
           ("float count", dict(base, detail=_calib_detail(false_reject=m(n=9.0)))),
           ("lo > hi", dict(base, detail=_calib_detail(miss=m(wilson95=[0.7, 0.2])))),
           ("interval > 1", dict(base, detail=_calib_detail(miss=m(wilson95=[0.1, 1.2])))),
           ("no threshold", dict(base, detail=_calib_detail(miss=m(threshold=None)))),
           ("invalid > candidates", dict(base, detail=_calib_detail(invalid=40))))
    for nm, rec in bad:
        check(raises(L.Rejected, L.validate_record, rec) is not None, "CAL-6 calib %s rejected" % nm)
    # analysis: the calibration arm is verified and reported, never analysed as an arm
    real_entry, real_code, real_sel = L._entrypoint, L._main_code_ok, L._gate_runner_sel
    L._gate_runner_sel = lambda cmdline=None, env=None: None
    L._main_code_ok = lambda e: None
    try:
        L._entrypoint = lambda: str(L.HERE / "arena.py")
        with L.harness_pass(p) as cap:
            L.HarnessWriter(p, cap=cap).emit("stopped", "switch", lane="none", run_id="sw",
                                             detail={"from": "ralph_a", "to": "stopped"})
    finally:
        L._entrypoint, L._main_code_ok, L._gate_runner_sel = real_entry, real_code, real_sel
    rep = L.report(p)
    logs = AN.load_verified(p, allow_untrusted=True)
    check(L.CALIB_ARM in rep and rep[L.CALIB_ARM].get("accepted") == 1 and "stopped" in logs
          and L.CALIB_ARM not in logs,
          "CAL-7 report() verifies the calib arm; arena_analysis.load_verified skips it (arms %s)" % sorted(logs))
    raw = tmp / "cal_raw"
    raw.mkdir()
    shutil.copy(L.arm_file(p, L.CALIB_ARM), raw)
    shutil.copy(L.arm_file(p, "stopped"), raw)
    check(sorted(AN.load_raw(raw)) == ["stopped"], "CAL-8 arena_analysis.load_raw skips the calib arm too")


def main():
    if os.environ.get("RM_EVLOG_GATE_PROBE"):
        return _gate_probe()
    tmp = Path(tempfile.mkdtemp(prefix="arena_eventlog_st_"))
    keys = ("ARENA_ROOT", "ARENA_CLONES", "ARENA_EVENT_TOKEN_FILE", "ARENA_ANCHOR_FILE", "ARENA_WITNESS", "RM_ARM")
    saved = {k: os.environ.get(k) for k in keys}
    # R2-9: whatever anchor store this process inherited, and the real default one, must come out untouched. A
    # decoy stands in for an inherited ARENA_ANCHOR_FILE (round 1's selftest deleted whatever that pointed at).
    decoy_dir = Path(tempfile.mkdtemp(prefix="arena_eventlog_decoy_"))
    decoy = decoy_dir / "anchors.jsonl"
    decoy.write_text('{"decoy": true}\n')
    inherited = saved["ARENA_ANCHOR_FILE"]
    os.environ["ARENA_ANCHOR_FILE"] = str(decoy)
    os.environ.pop("ARENA_EVENT_TOKEN_FILE", None)
    dflt_anchor = L._default_token_path().parent / "anchors.jsonl"
    guard = {str(decoy): _stat(decoy), str(dflt_anchor): _stat(dflt_anchor)}
    if inherited:
        guard[inherited] = _stat(inherited)
    try:
        t_agent_write(tmp)
        t_same_agent(tmp)
        t_owner(tmp)
        t_adapter(tmp)
        for t in (t_d1_token, t_d2_tail, t_d3_partial, t_d4_ids, t_d5_idem, t_d6_minutes, t_d8_verdict, t_d7_recover,
                  t_r2_1_capability, t_r2_2_trust, t_r2_3_v3_output, t_r2_4_build_id, t_r2_5_order, t_r2_6_schema,
                  t_r2_7_testq, t_r2_8_window, t_r2_9_anchor_neg, t_r3_b1_tail, t_r3_b2_forged_note, t_r3_b3_roster,
                  t_r3_b4_note_tokens, t_r3_entrypoint, t_switch_entry, t_r3_a4c_fd_reuse, t_r3_testq_real, t_r3_testq_attempts,
                  t_r3_analysis, t_r3_cards, t_r4_small, t_gate_runner, t_calib_entry):
            try:
                t(tmp)
            except Exception as e:          # a crash is a failure of that test, not of the run
                check(False, "%s crashed: %s: %s" % (t.__name__, type(e).__name__, e))
        after = {k: _stat(k) for k in guard}
        check(after == guard and decoy.read_text() == '{"decoy": true}\n',
              "R2-9 the inherited anchor store (decoy) and the default store %s were never touched" % dflt_anchor)
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(decoy_dir, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
