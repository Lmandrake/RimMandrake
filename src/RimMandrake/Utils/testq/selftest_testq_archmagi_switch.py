#!/usr/bin/env python3
"""selftest_testq_archmagi_switch.py - the section 2 trial switch for the Archmagi backfill (ARCHMAGI_BACKFILL_WIRE_TRIAL_SWITCH).

Spec: design/RimMandrake/work_allocation_framework_2026-10-26.md section 2. Offline: a pure part on archmagi_switch.decide,
then testq.py itself on the temp rig of selftest_testq_archmagi.py (fake ssh, local worker, mock modcheck). Proves:
  S1: ON only when useful (non-filler) ready work waited > 30 min or exceeds 60 lane-min, held 60 min, Steve INVALID
      share under 20%, the bridge gate open; filler work alone never; OFF when the queue drains or the bridge is taken.
  S2: ON when SteveDesktop is unavailable > 30 min with fix jobs ready; not before 30 min; not without a fix job;
      OFF when Steve is healthy again.
  cooldown: no ON for 30 min after any OFF, forced or not.
  latch: 2 consecutive INVALID attempts on Archmagi latch it OFF; only a ledger close of the latch item after the latch
      clears it, and the INVALIDs before the clear do not latch again.
  S3: filler, guard and sweep never; a job needing a deploy only as part of a train worth twice the load.
  tick: not forced and not saturated -> nothing admitted, closed reason stored; S2 from a 40-min ssh outage plus a fix
      job -> admitted; a bridge take mid-run -> the attempt yields at its next row boundary (validation_core.row), the
      measured rows are kept on the job and dropped from its selector, the switch turns OFF and the take is recorded;
      the cooldown then holds even forced; latch from two archmagi INVALID results, unlatched by a ledger close.
  report: archmagi-report prices load and displaced minutes at Steve's verified items per lane-hour.
"""
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import archmagi_switch as SW  # noqa: E402
import selftest_testq_archmagi as BASE  # noqa: E402

FAILS = []
UTILS = os.path.abspath(os.path.join(HERE, ".."))


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def busy(**kw):
    """Inputs of a saturated SteveDesktop with the gate open."""
    d = {"useful_oldest_wait_s": 2400, "useful_lane_s": 1200, "fix_ready": 0, "steve_invalid_share": 0.05,
         "steve_unavailable_s": None, "gate_ok": True, "gate_why": "free", "bridge_holder": None,
         "arch_invalid_streak": 0, "latch_closed_at": None, "force": False}
    d.update(kw)
    return d


def run(seq, state=None, t0=1_000_000.0, step=60):
    """Feed decide() a list of inputs one minute apart -> (final state, all events, per-step on flags)."""
    st, evs, ons = state or {}, [], []
    for i, inp in enumerate(seq):
        st, e = SW.decide(inp, st, t0 + i * step)
        evs += e
        ons.append(st["on"])
    return st, evs, ons


def t_pure():
    st, _e, ons = run([busy()] * 61)
    check(not any(ons[:60]) and ons[60] and st["rule"] == "S1", "S1: ON only after 60 min of held pressure (%s)" %
          ons.index(True) if True in ons else "never")
    st, _e, ons = run([busy(useful_oldest_wait_s=600, useful_lane_s=4000)] * 61)
    check(ons[60], "S1: > 60 lane-min of ready useful work counts as pressure too")
    seq = [busy()] * 30 + [busy(useful_oldest_wait_s=None, useful_lane_s=0)] + [busy()] * 40
    _st, _e, ons = run(seq)
    check(not any(ons), "S1: a break in the pressure restarts the 60-minute clock")
    _st, _e, ons = run([busy(useful_oldest_wait_s=None, useful_lane_s=0)] * 90)
    check(not any(ons), "S1: no useful ready work (filler only) -> never ON")
    st, _e, ons = run([busy(steve_invalid_share=0.25)] * 70)
    check(not any(ons) and "INVALID share" in st["closed_why"], "S1: Steve INVALID share >= 20%% -> no ON: %s" %
          st["closed_why"])
    st, _e, ons = run([busy(gate_ok=False, gate_why="bridge used 30 s ago")] * 70)
    check(not any(ons) and "bridge gate" in st["closed_why"], "S1: bridge gate closed -> no ON")
    st, _e, _o = run([busy()] * 61)
    st2, ev, _o = run([busy(useful_oldest_wait_s=None, useful_lane_s=0)], state=st, t0=2_000_000)
    check(not st2["on"] and ev and "drained" in ev[0]["why"], "S1: OFF when the ready queue drains")
    st2, ev, _o = run([busy(bridge_holder="CONDUCTOR")], state=st, t0=2_000_000)
    check(not st2["on"] and "bridge taken" in ev[0]["why"], "S1: OFF on a bridge take")
    # cooldown: after OFF, even with everything open (and forced), no ON for 30 min
    st3, _e, ons = run([busy(force=True)] * 31, state=st2, t0=2_000_060)
    check(not any(ons[:29]) and ons[-1], "cooldown: no ON for 30 min after OFF, forced or not; then ON (%s)" % ons)
    # S2
    s2 = busy(useful_oldest_wait_s=None, useful_lane_s=0, steve_unavailable_s=1500, fix_ready=2)
    st, _e, ons = run([s2])
    check(not ons[0] and "needs >" in st["closed_why"], "S2: Steve unavailable 25 min -> not yet: %s" % st["closed_why"])
    st, _e, ons = run([dict(s2, steve_unavailable_s=2000, fix_ready=0)])
    check(not ons[0] and "no fix-purpose" in st["closed_why"], "S2: no fix job ready -> no ON")
    st, _e, ons = run([dict(s2, steve_unavailable_s=2000)])
    check(ons[0] and st["rule"] == "S2", "S2: unavailable > 30 min with fix jobs ready -> ON at once")
    st2, ev, _o = run([dict(s2, steve_unavailable_s=None)], state=st, t0=2_000_000)
    check(not st2["on"] and "healthy" in ev[0]["why"], "S2: OFF when Steve is healthy again")
    st2, ev, _o = run([dict(s2, steve_unavailable_s=2100, bridge_holder="RELENTLESS")], state=st, t0=2_000_000)
    check(not st2["on"] and "bridge taken" in ev[0]["why"], "S2: OFF on a bridge take")
    # latch
    st, _e, _o = run([busy()] * 61)
    st, ev, _o = run([busy(arch_invalid_streak=2)], state=st, t0=3_000_000)
    check(not st["on"] and st["latch"] and [e["kind"] for e in ev] == ["latch", "off"],
          "latch: 2 consecutive archmagi INVALID -> latched and OFF (%s)" % [e["kind"] for e in ev])
    st, _e, ons = run([busy(arch_invalid_streak=0, force=True)] * 120, state=st, t0=3_000_060)
    check(not any(ons) and "latched" in st["closed_why"], "latch: holds past the cooldown, forced or not")
    st, _e, ons = run([busy(latch_closed_at=2_000_000)], state=st, t0=4_000_000)
    check(st["latch"], "latch: a close of the item BEFORE the latch does not clear it")
    st, ev, ons = run([busy(latch_closed_at=3_500_000)], state=st, t0=4_000_000)
    check(not st["latch"] and st.get("latch_cleared_at") == 4_000_000 and ev[0]["kind"] == "unlatch",
          "latch: a ledger close of %s after the latch clears it" % SW.LATCH_ITEM)
    # S2 not met: S1 still applies (a backed-up queue behind a short outage)
    st, _e, ons = run([busy(steve_unavailable_s=600)] * 61)
    check(ons[60] and st["rule"] == "S1", "S2 not met (10 min outage): S1 still turns it ON on held pressure")
    # the 60-minute clock wants readings 'running': a 2-hour gap in the ticks restarts it
    st, _e, _o = run([busy()] * 30)
    st, _e, ons = run([busy()] * 31, state=st, t0=1_000_000 + 30 * 60 + 7200)
    check(not any(ons), "S1: a 2-hour gap in the readings restarts the 60-minute clock")
    st, _e, _o = run([busy()])
    check(st.get("latch_cleared_at") == 1_000_000, "the first reading starts the trial clean (latch_cleared_at = now)")
    # S3
    j = {"purpose": "fix", "requested_by": "BENCH", "deploy": []}
    check(SW.s3_refusal(j) is None, "S3: a fix job with no deploy may run")
    check("filler" in (SW.s3_refusal(dict(j, requested_by=SW.FILLER)) or ""), "S3: filler never")
    check("guard" in (SW.s3_refusal(dict(j, purpose="guard")) or ""), "S3: guard never")
    check("sweep" in (SW.s3_refusal(dict(j, purpose="sweep")) or ""), "S3: sweep never")
    d = dict(j, deploy=["OtherMod"])
    check(SW.s3_refusal(d, 1700) is not None and SW.s3_refusal(d, 1800) is None,
          "S3: a deploy/load job only when the queued value is >= twice the load (900 s)")


MOCK_ROWS = r'''
import json, os, sys, time
sys.path.insert(0, %r)
import validation_core as V
rows = []
for i in range(1, 4):
    V.row(rows, "r%%d" %% i, "PASS", "MOD", "ok")
    time.sleep(float(os.environ.get("MOCK_ROW_SLEEP") or 0))
name = "Mock_%%d" %% int(time.time() * 1000000)
comps = [{"name": r["id"], "verdict": r["status"], "detail": "ok"} for r in rows]
json.dump({"mod": "Mock", "summary": {"chains": [{"name": "c1", "components": comps}]}},
          open(os.path.join(os.environ["TESTQ_SHEET_DIR"], name + ".json"), "w"))
print("sheet Transient/modcheck/%%s.html" %% name)
''' % UTILS


def sw_state(r):
    try:
        return json.load(open(r.p("queue", "archmagi_state.json"))).get("switch") or {}
    except (OSError, ValueError):
        return {}


def submit(r, purpose="commission", rows="r1", lane="archmagi"):
    if not hasattr(r, "sha"):
        r.job("seed")
        r.clear()
    rc, o = r.tq("submit", "Mock", "--purpose", purpose, "--by", "BENCH", "--sha", r.sha, "--rows", rows,
                 "--lane", lane, "--profile", "full-list", "--for-item", "SOME_ITEM_FIX_IT")
    try:
        return json.loads(o.strip().splitlines()[-1])["job"]
    except (ValueError, IndexError, KeyError):
        raise RuntimeError("submit failed: %s" % o[-300:])


def write_done(r, jid, host, outcome, finished_ago, lane_s=600, load_s=0, rows=("PASS",), item=None):
    fin = time.time() - finished_ago
    ts = lambda t: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))     # noqa: E731
    rec = {"job": {"id": jid, "selector": {"item": [item]} if item else {"rows": ["r1"]}, "purpose": "fix"},
           "result": {"attempt": jid + ".a1", "outcome": outcome, "cause": "HARNESS" if outcome == "INVALID" else None,
                      "started": ts(fin - lane_s), "finished": ts(fin), "phase_s": {"load": load_s},
                      "rows": [{"id": "r%d" % i, "status": s} for i, s in enumerate(rows)]}}
    if host != "stevedesktop":
        rec["host"] = host
    json.dump(rec, open(r.p("queue", "done", jid + ".json"), "w"))


def t_tick(r):
    r.clear()
    r.tq("list")
    off = dict(TESTQ_ARCHMAGI_SWITCH=None)
    j = submit(r)
    r.tq("tick", **off)
    st = sw_state(r)
    check(r.state(j) == "pending" and not st.get("on") and st.get("closed_why"),
          "not forced, nothing saturated: nothing admitted; closed reason stored: %s" % st.get("closed_why"))
    check("switch off" in r.qlog(), "the tick log names the switch as the closed gate")
    # S2: SteveDesktop unreachable 40 min (the probe not due), a fix job ready
    now = time.time()
    json.dump({"down_since": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - 2400)), "last_probe": now},
              open(r.p("queue", "ssh_state.json"), "w"))
    r.clear()
    json.dump({"down_since": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - 2400)), "last_probe": now},
              open(r.p("queue", "ssh_state.json"), "w"))
    open(r.p("mock_rows.py"), "w").write(MOCK_ROWS)
    rowsmock = "%s %s" % (sys.executable, r.p("mock_rows.py"))
    j = submit(r, purpose="fix", rows="r1,r2,r3")
    env = dict(off, TESTQ_ARCHMAGI_CMD_RUN=rowsmock, MOCK_ROW_SLEEP="4", TESTQ_ARCHMAGI_YIELD_GRACE_S="120")
    rc, o = r.tq("tick", **env)
    st = sw_state(r)
    aid, host = BASE.admitted(r, j)
    check(st.get("on") and st.get("rule") == "S2" and r.state(j) == "running" and host == "archmagi",
          "S2: 40 min of Steve outage + a fix job -> ON, admitted (%s, %s) %s" % (st.get("rule"), st.get("closed_why"),
                                                                                 o[-200:]))
    # a take mid-run: the attempt yields at its next row boundary
    time.sleep(2)
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    json.dump({"holder": "CONDUCTOR", "since": stamp, "touched": stamp, "purpose": "debugging"},
              open(r.p("BRIDGE_SHARED.json"), "w"))
    r.tq("tick", **env)
    check(os.path.exists(r.p("yield.json")) and r.rec(j).get("yield") and not r.rec(j).get("stop_sent"),
          "a take mid-run: yield requested, no stop sent inside the grace")
    st = sw_state(r)
    check(not st.get("on") and any(e["kind"] == "off" and "bridge taken" in e["why"] for e in st.get("history", [])),
          "the switch turned OFF on the take")
    res = r.wait_result("arch_home", aid, limit=40)
    check(res and res["outcome"] != "DONE", "the attempt ended at a row boundary, before its last row: %s" %
          str(res and (res["outcome"], res["cause"])))
    r.tq("tick", **env)
    rec = r.rec(j)
    arch = json.load(open(r.p("queue", "archmagi_state.json")))
    prog = ((arch.get("progress") or {}).get(j) or [{}])[-1]
    kept = [x["id"] for x in prog.get("rows") or []]
    check("archmagi_progress" not in rec, "the job dict stays schema-clean (progress lives in archmagi_state.json)")
    check(r.state(j) == "pending" and kept and kept[0] == "r1",
          "the yielded job is back in pending with the rows it measured kept: %s" % kept)
    check(rec["selector"]["rows"] == [x for x in ["r1", "r2", "r3"] if x not in kept],
          "and its selector drops them, so nothing is redone: %s" % rec["selector"]["rows"])
    arch = json.load(open(r.p("queue", "archmagi_state.json")))
    check(arch.get("takes") and arch["takes"][-1]["holder"].startswith("CONDUCTOR") and arch["takes"][-1]["released"],
          "the take is recorded and closed when the attempt handed back: %s" % (arch.get("takes") or [None])[-1])
    os.remove(r.p("BRIDGE_SHARED.json"))
    r.tq("tick", TESTQ_ARCHMAGI_SWITCH="force")
    st = sw_state(r)
    check(not st.get("on") and "cooling down" in (st.get("closed_why") or ""),
          "after the OFF, even forced, the cooldown holds: %s" % st.get("closed_why"))
    os.remove(r.p("queue", "ssh_state.json"))
    open(r.p("down"), "w").close()


def t_latch(r):
    r.clear()
    r.tq("list")
    write_done(r, "J20261105T000000Z-999999", "archmagi", "INVALID", 900)
    write_done(r, "J20261105T000009Z-888888", "archmagi", "INVALID", 800)
    st = r.call("testq.switch_step(False, True, 'free')", TESTQ_ARCHMAGI_SWITCH="force")
    check(not st.get("latch"), "two INVALIDs from before the switch first ran do not latch it (the trial starts clean)")
    write_done(r, "J20261105T000001Z-aaaaaa", "archmagi", "INVALID", -2)
    write_done(r, "J20261105T000002Z-bbbbbb", "archmagi", "INVALID", -2)
    time.sleep(3)
    st = r.call("testq.switch_step(False, True, 'free')", TESTQ_ARCHMAGI_SWITCH="force")
    check(st.get("latch") and not st.get("on"), "two archmagi INVALID results latch the switch: %s" % st.get("closed_why"))
    check("archmagi switch LATCH" in r.qlog(), "the latch is logged")
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 5))
    with open(r.p("ledger", "RELENTLESS.jsonl"), "w") as f:
        f.write(json.dumps({"seat": "RELENTLESS", "event": "close", "id": SW.LATCH_ITEM, "ts": stamp}) + "\n")
    time.sleep(6)
    st = r.call("testq.switch_step(False, True, 'free')", TESTQ_ARCHMAGI_SWITCH="force")
    check(not st.get("latch") and st.get("latch_cleared_at"), "a ledger close of %s after the latch clears it" %
          SW.LATCH_ITEM)
    st = r.call("testq.switch_step(False, True, 'free')", TESTQ_ARCHMAGI_SWITCH="force")
    check(not st.get("latch"), "the INVALIDs before the clear do not latch it again")
    os.remove(r.p("ledger", "RELENTLESS.jsonl"))


def t_candidates_s3(r):
    r.clear()
    a = submit(r, purpose="fix")
    g = submit(r, purpose="guard")
    c = [x["id"] for x in r.call("testq.archmagi_candidates(True, False)")]
    check(a in c and g not in c, "S3 in the candidates: a guard job is never offered to archmagi: %s" % c)


def t_progress_fail(r):
    r.clear()
    json.dump({"rows": [{"id": "a", "status": "FAIL"}, {"id": "b", "status": "PASS"}]},
              open(r.p("yield.json") + ".rows.json", "w"))
    job = {"id": "J20261105T000020Z-121212", "selector": {"rows": ["a", "b", "c"]}}
    out = r.call("testq.record_yield_progress(%r, {'attempt': 'x.a1'})" % job)
    check(out.get("selector", {}).get("rows") == ["a", "c"],
          "a yield drops only PASSED rows: the FAIL row stays selected, so the final result carries it: %s" %
          out.get("selector"))


def t_report(r):
    r.clear()
    r.tq("list")
    write_done(r, "J20261105T000003Z-cccccc", "archmagi", "DONE", 3600, lane_s=1800, load_s=900, item="ITEM_A")
    write_done(r, "J20261105T000004Z-dddddd", "archmagi", "DONE", 7200, lane_s=1800, load_s=0, item="ITEM_B",
               rows=("PASS", "FAIL"))
    write_done(r, "J20261105T000005Z-eeeeee", "archmagi", "INVALID", 9000, lane_s=600)
    for i in range(4):     # Steve: 4 verified items in 4 lane-hours -> 1 item per lane-hour
        write_done(r, "J20261105T00001%dZ-ffff0%d" % (i, i), "stevedesktop", "DONE", 3600 * (i + 1), lane_s=3600,
                   item="STEVE_%d" % i)
    arch = json.load(open(r.p("queue", "archmagi_state.json"))) if os.path.exists(
        r.p("queue", "archmagi_state.json")) else {}
    arch["takes"] = [{"at": time.time() - 4000, "holder": "CONDUCTOR", "released": time.time() - 4000 + 1800}]
    json.dump(arch, open(r.p("queue", "archmagi_state.json"), "w"))
    rep = r.call("testq.archmagi_report(days=1.0)")
    check(rep.get("verified_items") == 1 and rep.get("archmagi_jobs") == 3 and rep.get("archmagi_invalid") == 1,
          "report: one verified item (a FAIL row does not verify), 3 jobs, 1 INVALID: %s" % rep)
    check(rep.get("load_h") == 0.25 and rep.get("displaced_interactive_min") == 30.0,
          "report: load 0.25 h and 30 displaced interactive min")
    rc0, o0 = r.tq("archmagi-report", "--days", "0")
    check(rc0 == 2 and "REFUSED" in o0, "archmagi-report --days 0 is refused, not a ZeroDivisionError")
    check(rep.get("steve_items_per_lane_h") == 1.0 and rep.get("net_items_per_day") == 0.25,
          "report: net = (1 item - 0.75 charged h x 1 item/h) / 1 day = 0.25: %s" % rep.get("net_items_per_day"))
    rc, o = r.tq("archmagi-report", "--days", "1")
    check(rc == 0 and "net 0.25 items/day" in o, "the archmagi-report verb prints it: %s" % o.strip().splitlines()[-1])


def main():
    t_pure()
    tmp = tempfile.mkdtemp(prefix="rf_testq_archsw_")
    try:
        r = BASE.Rig(tmp)
        for t in (t_tick, t_latch, t_candidates_s3, t_progress_fail, t_report):
            try:
                t(r)
            except Exception as ex:     # noqa: BLE001 - reported; the next test still runs
                check(False, "%s raised %s: %s" % (t.__name__, type(ex).__name__, ex))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%d failure(s)" % (len(FAILS) + len(BASE.FAILS)))
    return 1 if FAILS or BASE.FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
