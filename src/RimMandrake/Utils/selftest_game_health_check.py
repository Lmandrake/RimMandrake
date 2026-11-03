#!/usr/bin/env python3
"""selftest_game_health_check.py - the standing game health check (HEALTH_CHECK_MONITOR_MEMORY_TPS_OVER_TIME).

Synthetic TPS-record sessions in a temp dir: full-list filter, curves over time, Theil-Sen growth, decay at the
dominant speed, long-event stalls kept out of the stall limit, UNMEASURED (never 0) for absent sources, breaches
against the shipped thresholds, idempotent record, open sessions held back, the live-proof `fields` verb, and the
ops_watch tps family reading a breach as a MEASURED count (what rings OPS_GAME_HEALTH_DEBUG). Offline, no game.
"""
import json
import os
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import game_health_check as G  # noqa: E402

FAILS = []


def check(name, ok, detail=None):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  :: %r" % (detail,)))
    if not ok:
        FAILS.append(name)


def utc(t):
    import datetime as D
    return D.datetime.fromtimestamp(t, D.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


T0 = 1793000000.0   # session start (epoch)
SID = "a" * 32


def session_rows(sid=SID, mods=321, minutes=120, heap0=3000.0, heap_rate_h=600.0, ratio0=1.0, ratio1=0.5,
                 live_fields=True, shutdown=True, longevent_stall=45.0, stall=3.0, errs_per_min=1):
    rows, seq = [], [0]

    def add(t, kind, **kw):
        seq[0] += 1
        r = {"seq": seq[0], "v": 2, "utc": utc(t), "mono": round(t - T0, 3), "session": sid, "kind": kind}
        r.update(kw)
        rows.append(r)

    add(T0, "session", pid=4242, build="b", engine="1.6", mods=mods, modDigest="d1")
    add(T0 + 10, "menu", programState="Entry")
    tg = T0 + 60
    add(tg, "game", game=1, save="SAVE_A", ticksGame=1, maps=1)
    add(tg + 60, "incident", type="stall", gapS=longevent_stall, unexplainedS=longevent_stall, longEvent=True)
    add(tg + 120, "incident", type="stall", gapS=stall, unexplainedS=stall, longEvent=False)
    for i in range(minutes):
        t = tg + i * 60.0
        frac = i / float(max(1, minutes - 1))
        ratio = ratio0 + (ratio1 - ratio0) * frac
        heap = heap0 + heap_rate_h * (i / 60.0) + (300 if i % 7 == 0 else 0)    # GC sawtooth outliers
        add(t + 5, "sample", state="run", ratio=round(ratio, 3), tps=round(60 * ratio, 1), mult=1, dReal=5.0,
            heapMB=heap)
        ctx = {"heapMB": heap, "workingSetMB": 0}
        if live_fields:
            ctx.update(privateMB=heap * 2 + 1000, unityReservedMB=2000 + i, unityAllocMB=1500 + i, gfxMB=0,
                       upS=round(900 + (t + 6 - T0), 1), logErr=i * errs_per_min, logWarn=i, logEnabled=True,
                       logMsgs=i * 3, logCapReached=False, logErrLowerBound=False)
        add(t + 6, "context", **ctx)
    if shutdown:
        add(tg + minutes * 60 + 1, "shutdown", phase="intent")
    return rows


def write_session(d, rows, start=T0, pid=4242):
    sid = rows[0]["session"]
    import datetime as D
    stamp = D.datetime.fromtimestamp(start, D.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    p = os.path.join(d, "tps_%s_%s_%d_000.jsonl" % (stamp, sid, pid))
    with open(p, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    return p


RULES = G.load_rules()
NOW = T0 + 13 * 3600     # past ended_after_min (12 h) for a session with no shutdown and no successor

with tempfile.TemporaryDirectory() as tmp:
    rec = os.path.join(tmp, "tps")
    os.makedirs(rec)
    hist = os.path.join(tmp, "h", "history.jsonl")
    # 1. a healthy-ish full-list session: grows 600 MB/h, ratio decays 1.0 -> 0.5 (50 % decay: a breach)
    write_session(rec, session_rows())
    # 2. a quicktest session (14 mods): never recorded
    write_session(rec, session_rows(sid="b" * 32, mods=14), start=T0 + 1)
    # 3. an old-companion full-list session: no live fields, heap only
    write_session(rec, session_rows(sid="c" * 32, live_fields=False, ratio1=1.0, heap_rate_h=0), start=T0 + 2)
    # 4. still running (no shutdown, newest row recent): held back as open
    write_session(rec, session_rows(sid="d" * 32, shutdown=False, minutes=20), start=T0 + 3)
    # sanity probe first: the instrument sees the sessions on disk
    check("probe: four sessions on disk by segment name", len(G.sessions_on_disk(rec)) == 4, G.sessions_on_disk(rec))
    res = G.record(directory=rec, rules=RULES, path=hist, now=T0 + 3 + 60 + 20 * 60 + 120)
    got = {r["session"][0]: r for r in res["recorded"]}
    check("record: the quicktest session is not full-list", res["notFullList"] == 1 and "b" not in got, res["notFullList"])
    check("record: the open session is held back, not recorded", [r["session"][0] for r in res["open"]] == ["d"],
          [r["session"] for r in res["open"]])
    check("record: two finished full-list sessions recorded", sorted(got) == ["a", "c"], sorted(got))
    a, c = got.get("a", {}), got.get("c", {})
    ma, mc = a.get("metrics", {}), c.get("metrics", {})
    check("load: reached menu and loaded a game", ma.get("load.reached_menu") is True and ma.get("load.game_loaded") is True)
    check("load: seconds carried back from upS to the menu row (900 s + 10 s)", ma.get("load.seconds") == 910.0,
          ma.get("load.seconds"))
    check("mem: managed growth ~600 MB/h despite GC outliers (Theil-Sen)",
          550 <= (ma.get("mem.managed_growth_mb_per_h") or 0) <= 650, ma.get("mem.managed_growth_mb_per_h"))
    check("mem: private peak read from privateMB", ma.get("mem.private_peak_mb", 0) > 6000, ma.get("mem.private_peak_mb"))
    check("mem: gfx 0 everywhere is UNMEASURED, never 0", not G.is_m(ma.get("mem.gfx_peak_mb")), ma.get("mem.gfx_peak_mb"))
    check("mem: curves are buckets of 10 min since load", [p[0] for p in a["curves"]["managed"]][:3] == [0, 10, 20],
          a.get("curves", {}).get("managed"))
    for cname, lo_hi in (("private", (6900, 7300, 9100, 9500)), ("native", (2000, 2010, 2105, 2115))):
        cv = a.get("curves", {}).get(cname) or []
        check("mem: %s-memory-vs-time curve is recorded, one [minute, median, max] point per 10-min bucket (120 min -> 12)"
              % cname, len(cv) == 12 and all(isinstance(p, list) and len(p) == 3 for p in cv)
              and [p[0] for p in cv] == [10 * k for k in range(12)], cv)
        check("mem: %s curve rises over time from the fixture's own values (max >= median per point)" % cname,
              len(cv) == 12 and lo_hi[0] <= cv[0][1] <= lo_hi[1] and lo_hi[2] <= cv[-1][1] <= lo_hi[3]
              and all(cv[k][1] < cv[k + 1][1] for k in range(11)) and all(p[2] >= p[1] for p in cv), cv)
    check("mem: gfx 0 everywhere draws no curve (0 is 'not read', never a flat line)",
          "gfx" not in a.get("curves", {}), sorted(a.get("curves", {})))
    check("mem: the old-companion session draws a managed curve but no private/native one",
          "managed" in c.get("curves", {}) and not ({"private", "native"} & set(c.get("curves", {}))),
          sorted(c.get("curves", {})))
    check("tps: decay first->last at the dominant speed ~ 45-50 %",
          40 <= (ma.get("tps.ratio_decay_pct") or 0) <= 50, ma.get("tps.ratio_decay_pct"))
    rc = a.get("curves", {}).get("ratio") or []
    check("tps: ratio-vs-time curve is recorded, one [minute, ratio, tps] point per 10-min bucket (120 min -> 12)",
          len(rc) == 12 and all(isinstance(p, list) and len(p) == 3 for p in rc)
          and [p[0] for p in rc] == [10 * k for k in range(12)], rc)
    check("tps: ratio curve falls 1.0 -> 0.5 over time and tps ~ 60 x ratio at each point",
          len(rc) == 12 and 0.95 <= rc[0][1] <= 1.0 and 0.5 <= rc[-1][1] <= 0.55
          and all(rc[k][1] > rc[k + 1][1] for k in range(11))
          and all(abs(p[2] - 60 * p[1]) <= 1.0 for p in rc), rc)
    check("tps: the long-event stall is reported apart and not judged",
          ma.get("tps.stall_max_s") == 3.0 and ma.get("tps.longevent_max_s") == 45.0,
          (ma.get("tps.stall_max_s"), ma.get("tps.longevent_max_s")))
    check("log: errors are the newest context count", ma.get("log.errors") == 119 and ma.get("log.cap_reached") is False,
          ma.get("log.errors"))
    bk = sorted(b["key"] for b in a.get("breaches", []))
    check("breach: decay over 30 % is the one breach", bk == ["tps.ratio_decay_pct"], bk)
    check("old companion: private/native/log/load are UNMEASURED with a reason",
          all(not G.is_m(mc.get(k)) and "predates" in mc[k]["why"] for k in
              ("mem.private_peak_mb", "mem.native_peak_mb", "log.errors", "load.seconds")), mc)
    check("old companion: managed still measured, flat (growth ~0), no breach",
          G.is_m(mc.get("mem.managed_peak_mb")) and abs(mc.get("mem.managed_growth_mb_per_h", 99)) < 20
          and c.get("breaches") == [], (mc.get("mem.managed_growth_mb_per_h"), c.get("breaches")))
    hrows = G.read_history(hist)
    check("history: two rows written", len(hrows) == 2, len(hrows))
    res2 = G.record(directory=rec, rules=RULES, path=hist, now=NOW)
    check("record: idempotent; the now-ended session joins, nothing repeats",
          [r["session"][0] for r in res2["recorded"]] == ["d"] and len(G.read_history(hist)) == 3,
          [r["session"] for r in res2["recorded"]])
    dmet = res2["recorded"][0]["metrics"] if res2["recorded"] else {}
    check("ended without shutdown: end.clean False, and not a breach (a kill looks the same)",
          dmet.get("end.clean") is False and "end.clean" not in [b["key"] for b in res2["recorded"][0]["breaches"]], dmet)
    # torn tail: an interrupted append must not glue the next row to it
    with open(hist, "a") as fh:
        fh.write('{"session": "torn')
    write_session(rec, session_rows(sid="9" * 32, minutes=40), start=T0 + 4)
    G.record(directory=rec, rules=RULES, path=hist, now=NOW)
    check("torn tail: the next row survives an interrupted one",
          any(r.get("session") == "9" * 32 for r in G.read_history(hist)), [r.get("session") for r in G.read_history(hist)])
    # superseded: no shutdown, quiet for minutes only, but a newer session exists -> ended
    rec3 = os.path.join(tmp, "tps3")
    os.makedirs(rec3)
    write_session(rec3, session_rows(sid="7" * 32, shutdown=False, minutes=40), start=T0)
    write_session(rec3, session_rows(sid="8" * 32, mods=14, minutes=5), start=T0 + 3000)
    r3 = G.record(directory=rec3, rules=RULES, path=os.path.join(tmp, "h4", "h.jsonl"), now=T0 + 3600, dry_run=True)
    check("superseded: a session with a newer one on disk is finished, not held open",
          [r["session"][0] for r in r3["recorded"]] == ["7"] and not r3["open"], (r3["recorded"], r3["open"]))
    # cap, lower bound and failed scans, from the fields the companion writes
    cap = session_rows(sid="6" * 32)
    for r in cap:
        if r["kind"] == "context" and r["mono"] > 3000:
            r["logCapReached"] = True
            r["logErrLowerBound"] = True
    s6 = G.summarize("6" * 32, [dict(r, _t=G.T._epoch(r["utc"])) for r in cap], 0, RULES, now=NOW)
    check("log: cap from logCapReached and a lower-bound count both breach",
          {"log.cap_reached", "log.errors_lower_bound"} <= {b["key"] for b in s6["breaches"]}, s6["breaches"])
    noscan = session_rows(sid="5" * 32)
    for r in noscan:
        if r["kind"] == "context":
            r.update(logErr=None, logWarn=None, logErrLowerBound=None, logScan="unreadable")
    s5 = G.summarize("5" * 32, [dict(r, _t=G.T._epoch(r["utc"])) for r in noscan], 0, RULES, now=NOW)
    check("log: no successful scan is UNMEASURED, never 0 errors",
          not G.is_m(s5["metrics"]["log.errors"]) and s5["metrics"]["log.cap_reached"] is False, s5["metrics"]["log.errors"])
    # growth needs the FIELD's own span: private bytes for 3 minutes of a 2-hour session is not a rate
    short = session_rows(sid="4" * 32)
    k = 0
    for r in short:
        if r["kind"] == "context":
            k += 1
            if k > 3:
                r.pop("privateMB", None)
    s4 = G.summarize("4" * 32, [dict(r, _t=G.T._epoch(r["utc"])) for r in short], 0, RULES, now=NOW)
    check("growth: 3 minutes of a field is UNMEASURED even in a long session",
          not G.is_m(s4["metrics"]["mem.private_growth_mb_per_h"]) and G.is_m(s4["metrics"]["mem.managed_growth_mb_per_h"]),
          s4["metrics"]["mem.private_growth_mb_per_h"])
    dry = G.record(directory=rec, rules=RULES, path=os.path.join(tmp, "h2", "x.jsonl"), dry_run=True, now=NOW)
    check("dry-run writes nothing", len(dry["recorded"]) == 4 and not os.path.exists(os.path.join(tmp, "h2")))
    # breaches on synthetic extremes, one per limit kind
    big = session_rows(sid="e" * 32, heap0=7000, heap_rate_h=1500, errs_per_min=10, ratio1=1.0)
    rec2 = os.path.join(tmp, "tps2")
    os.makedirs(rec2)
    write_session(rec2, big)
    r2 = G.record(directory=rec2, rules=RULES, path=os.path.join(tmp, "h3", "h.jsonl"), now=NOW, dry_run=True)
    bk2 = sorted(b["key"] for b in r2["recorded"][0]["breaches"])
    check("breach: heap peak, heap growth and errors over their limits",
          {"mem.managed_peak_mb", "mem.managed_growth_mb_per_h", "log.errors"} <= set(bk2), bk2)
    noload = [r for r in session_rows(sid="f" * 32) if r["kind"] in ("session",)]
    noload.append(dict(noload[0], seq=2, kind="shutdown", phase="intent"))
    s3 = G.summarize("f" * 32, [dict(r, _t=T0 + i) for i, r in enumerate(noload)], 0, RULES, now=NOW)
    check("breach: a session that never reached the menu is not loadable",
          [b["key"] for b in s3["breaches"]] == ["load.reached_menu"], s3["breaches"])
    # fields verb (the live proof)
    old = G.T.record_dir
    G.T.record_dir = lambda: rec2
    try:
        check("fields: exit 0 on a session carrying the companion fields", G.main(["fields"]) == 0)
    finally:
        G.T.record_dir = old
    check("fields: exit 1 on an old-companion session",
          G.main(["fields", "--dir", rec, "--session", "c" * 32]) == 1)
    # ops_watch tps family: a breach is a MEASURED count (the alarm target's input)
    os.environ["RM_GAME_HEALTH_DIR"] = os.path.join(tmp, "h")
    import ops_watch as OW
    real = OW.subprocess.run

    def fake(cmd, **k):
        if "game_health_check.py" in " ".join(map(str, cmd)):
            return real(cmd, **k)
        return types.SimpleNamespace(returncode=0, stdout=json.dumps({"summary": {"coverage": "STALE"}}), stderr="")
    OW.subprocess.run = fake
    try:
        hdir = os.path.join(tmp, "h")
        with open(os.path.join(hdir, "history.jsonl"), "a") as fh:
            fh.write(json.dumps(a) + "\n")          # newest row = session a, one breach
        os.environ["RM_GAME_HEALTH_TPS_DIR"] = rec     # every session there is already recorded: nothing new
        out = OW.c_tps(NOW, OW.load_rules(), {})
    finally:
        OW.subprocess.run = real
    hb = out.get("tps.health_breaches", {})
    check("ops_watch: tps.health_breaches is MEASURED 1 naming the key",
          hb.get("m") == "MEASURED" and hb.get("v") == 1 and "tps.ratio_decay_pct" in str(hb), hb)
    check("ops_watch: game off still reads the health check (5 rows: the torn line is not a session)", out.get("tps.ratio_median", {}).get("m") == "UNMEASURED"
          and out.get("tps.health_sessions", {}).get("v") == 5, out.get("tps.health_sessions"))
    tg = [t for t in OW.load_rules()["targets"] if t.get("key") == "tps.health_breaches"]
    check("ops_watch rules: the breach count alarms as OPS_GAME_HEALTH_DEBUG",
          tg and tg[0].get("alarm") is True and tg[0].get("name") == "OPS_GAME_HEALTH_DEBUG", tg)
    check("ops_watch: health keys are machine health (blind roles see them)",
          {"tps.health_breaches", "tps.health_age_h", "tps.health_sessions"} <= OW.BLIND_KEYS)

print("\n%d failed" % len(FAILS) if FAILS else "\nALL PASS")
sys.exit(1 if FAILS else 0)
