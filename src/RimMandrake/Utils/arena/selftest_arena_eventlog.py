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


def fresh(tmp, name):
    root = tmp / name
    os.environ["ARENA_ROOT"] = str(root)
    os.environ["ARENA_CLONES"] = str(root / "clones")
    os.environ["ARENA_EVENT_TOKEN_FILE"] = str(tmp / (name + "_secret") / "event_token")
    p = A.paths()
    L.init_token(p)
    return p, L.HarnessWriter(p)


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
    # metrics' window has a lower bound only (t >= now-1d); one day = the difference of two windows [d0-1, d0+86399)
    met = f(d0 + 86399) - f(d0 + 2 * 86400 - 1)
    ad = V.done_count(recs, d0 - 1, d0 + 86398)
    ad_close = V.done_count(recs, d0, d0 + 86399, "close")
    print("      %s: rimflow_metrics flow.done=%d  adapter done=%d (of which close verb=%d)" % (day, met, ad, ad_close))
    check(met > 10 and ad == met, "adapter done-count equals rimflow_metrics flow.done for %s (%d)" % (day, met))
    check(0 < ad_close < ad, "close-verb share is a proper part (close=%d of %d; the rest verify/implemented)" % (ad_close, ad))
    # forced failure: drop one done-making build_end
    drop = next(r for r in recs if r["detail"].get("done") and d0 <= A._epoch(r["ts"]) < d0 + 86400)
    short = [r for r in recs if r is not drop]
    check(V.done_count(short, d0 - 1, d0 + 86398) != met, "dropping one close from the adapter output breaks the match")
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
    jobs = {"J1": {"id": "J1", "item": "ITEM_A", "lane": "stevedesktop", "schema": "testq.job/1"}}
    res = [{"schema": "testq.result/1", "job": "J1", "host": "stevedesktop", "started": "2026-10-29T10:00:00Z",
            "finished": "2026-10-29T10:20:00Z", "outcome": "DONE", "counts": {"PASS": 3}},
           {"job": "J-unknown", "host": "h", "started": "2026-10-29T10:00:00Z"}]
    t = V.translate_testq(res, jobs)
    check([r["event"] for r in t] == ["test_start", "test_end"] and t[0]["task"] == "ITEM_A"
          and t[0]["detail"]["tester"] == "testq:stevedesktop" and t[1]["verdict"] == "DONE",
          "testq result -> test_start + test_end by 'testq:<host>'; a result with no item is not invented")


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


def main():
    tmp = Path(tempfile.mkdtemp(prefix="arena_eventlog_st_"))
    saved = {k: os.environ.get(k) for k in ("ARENA_ROOT", "ARENA_CLONES", "ARENA_EVENT_TOKEN_FILE")}
    try:
        t_agent_write(tmp)
        t_same_agent(tmp)
        t_owner(tmp)
        t_adapter(tmp)
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
