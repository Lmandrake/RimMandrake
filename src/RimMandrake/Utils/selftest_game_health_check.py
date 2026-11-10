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
    check("log: cap from logCapReached breaches; the sticky lower-bound flag alone is a fact, not a breach",
          "log.cap_reached" in {b["key"] for b in s6["breaches"]} and s6["metrics"]["log.errors_lower_bound"] is True
          and not {"log.errors_lower_bound", "log.play_evicted"} & {b["key"] for b in s6["breaches"]}, s6["breaches"])
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
    # attribution (OPS_GAME_HEALTH_DEBUG_PXQI): session e50b27df's shape, replayed. A bench run that loads a stale
    # save (+391 errors in one scan) and generates ever bigger maps (heap in steps, flat after) crosses the limits;
    # each breach must say so from the record, and attribution must never remove a breach.
    rp = session_rows(sid="9" * 32, heap0=3000, heap_rate_h=0, errs_per_min=0, minutes=180, ratio1=1.0)
    ci = 0
    for r in rp:
        if r["kind"] == "context":
            ci += 1
            big = ci > 90
            r["maps"] = [{"id": 5 if big else 0, "size": "924x924" if big else "250x250", "biome": "RM_Big" if big
                          else "RUT_Small", "pawns": 9, "things": 359876 if big else 3112}]
            r["heapMB"] = 9600.0 + (ci % 3) * 50 if big else 3600.0
            r["privateMB"] = 26000.0 if big else 18000.0
            r["logErr"] = 127 + (391 if ci > 40 else 0)
            r["logErrLowerBound"] = True
            r["logMsgs"] = 300 + ci * 2
    c40 = [r for r in rp if r["kind"] == "context"][39]
    rp.append(dict(c40, seq=99999, kind="game", game=2, save="BENCH_STALE_SAVE", mono=c40["mono"] + 30,
                   utc=utc(T0 + c40["mono"] + 30)))
    rp.append({"seq": 100000, "v": 2, "utc": utc(T0 + rp[-2]["mono"] + 1), "mono": rp[-2]["mono"] + 1,
               "session": "9" * 32, "kind": "log", "archived": "C:/x/Player_9.log"})
    s9 = G.summarize("9" * 32, [dict(r, _t=G.T._epoch(r["utc"])) for r in rp], 0, RULES, now=NOW)
    a9, k9 = s9["attribution"], {b["key"] for b in s9["breaches"]}
    check("attribution: replay still breaches heap peak, private peak and errors (the sticky flag is not a limit)",
          {"mem.managed_peak_mb", "mem.private_peak_mb", "log.errors"} <= k9 and "log.errors_lower_bound" not in k9,
          sorted(k9))
    check("attribution: every breach carries one", set(a9) == k9, (sorted(a9), sorted(k9)))
    mem = " | ".join(a9.get("mem.managed_peak_mb", []))
    check("attribution: heap names the largest map and its scale", "924x924 RM_Big" in mem and "13.7x" in mem, mem)
    check("attribution: heap growth on the last map set is measured and small (scale, not leak)",
          "managed growth after the last map change" in mem and "UNMEASURED" not in mem.split("managed growth")[1]
          .split("|")[0], mem)
    er = " | ".join(a9.get("log.errors", []))
    check("attribution: the error jump names the save loaded inside it",
          "+391" in er and "BENCH_STALE_SAVE" in er and "127 errors already counted" in er and "Player_9.log" in er, er)
    # the jump's cause is counted from the archived log, never assumed from the save loaded inside it (session ee0fbaa8:
    # "dead def names; no mod change fixes that" stood over 3476 chunk errors and 3200 Beer errors)
    check("attribution: an error jump asserts no cause it did not measure", "no mod change" not in er, er)
    check("attribution: an archive it cannot read says UNMEASURED, not nothing",
          "UNMEASURED" in er and "error classes" in er, er)
    census = getattr(G, "log_census", lambda *_: ["log_census is missing"])    # a failed check, not a crash, on older code
    with tempfile.TemporaryDirectory() as lg:
        plog = os.path.join(lg, "Player_c.log")
        with open(plog, "w") as fh:
            fh.write("Tried loading non-compressible thing as compressed thing: ChunkMarble\n" * 40
                     + "Could not load reference to Verse.ResearchProjectDef named Gone\n" * 3
                     + "Exception ticking RM_Tree123: System.NullReferenceException: x\n[Ref ABC]\n  at Verse.Foo ()\n"
                     + "Exception ticking RM_Tree456: System.NullReferenceException: x\n[Ref ABC]\n  at Verse.Foo ()\n"
                     + "Root level exception in Update(): System.NullReferenceException: x\n")
        cen = " | ".join(census(plog))
    check("log_census: counts the real classes, dead names apart from the rest, stack frames out",
          "40x Tried loading non-compressible" in cen and "3 'Could not load reference'" in cen
          and "2x Exception ticking RM_Tree#" in cen and "1x Root level exception" in cen and "Verse.Foo" not in cen,
          cen)
    check("log_census: no log, no claim", "UNMEASURED" in census(None)[0] and "UNMEASURED" in
          census("C:\\none\\Player.log")[0], census(None))
    # LOAD vs PLAY (owner by card 2026-11-09, "What should the limit judge? -> Two limits: load and play"). The cold
    # load overruns Verse.Log's queue before the first scan on every full-list session (the sticky flag rises there);
    # it is scored against LOAD (messages up to the first map), and only an overrun AFTER the load-end scan is PLAY.
    lp_dir = os.path.join(tmp, "lp")
    os.makedirs(lp_dir)

    def cold_log(name, n):
        pl = os.path.join(lp_dir, name)
        with open(pl, "w") as fh:
            fh.write("Mono path[0] = 'x'\n")                          # a Unity line, never a Verse.Log message
            for k in range(n):
                fh.write("Def error %d in SomeMod\n  at Verse.Foo ()\n" % k)   # message + a stack frame (not one)
            # the marker spelled out here, not taken from the code under test (GPT review 2026-11-09)
            fh.write("[RimBridge] Startup conditions satisfied after play-data load; initializing bridge services.\n")
            fh.write("after the bridge, not the cold load\n" * 50)
        return pl

    def lp_session(sid, plog, play_evict=None, tweak=None):
        rows = session_rows(sid=sid, heap_rate_h=0, errs_per_min=0, ratio1=1.0, minutes=40)
        cs = [r for r in rows if r["kind"] == "context"]
        for k, r in enumerate(cs):
            r.update(logErrLowerBound=True, logEvicted=(k == 0), logMsgs=400 + k * 20)   # full at the first read
        if play_evict == "flag":
            cs[20]["logEvicted"] = True
        elif play_evict == "rise":                     # an older companion: no logEvicted, a 1000+ rise between scans
            for r in cs:
                r.pop("logEvicted", None)
            for r in cs[20:]:
                r["logMsgs"] += 1500
        elif play_evict == "reset":                    # Log.Clear between two scans, then 1000+ since the reset
            for k, r in enumerate(cs):
                r["logMsgs"] = 400 + k * 60 if k < 20 else 1100 + (k - 20) * 10   # 1540 -> 1100: a reset, 1100 since
                r.pop("logEvicted", None)
        if tweak:
            rows = tweak(rows, cs)
        last = rows[-1]
        rows.append({"seq": last["seq"] + 1, "v": 2, "utc": last["utc"], "mono": last["mono"], "session": sid,
                     "kind": "log", "archived": plog})
        sm = G.summarize(sid, [dict(r, _t=G.T._epoch(r["utc"])) for r in rows], 0, RULES, now=NOW)
        return sm, {b["key"] for b in sm["breaches"]}

    lim = {x["key"]: x["value"] for x in RULES["limits"]}
    check("load/play: both limits live in the thresholds file with a why, and the old sticky limit is gone",
          isinstance(lim.get("log.load_messages"), int) and lim.get("log.play_evicted") is True
          and "log.errors_lower_bound" not in lim
          and all(x.get("why") for x in RULES["limits"] if x["key"] in ("log.load_messages", "log.play_evicted")), lim)
    sa, ka = lp_session("a1" * 16, cold_log("Player_a1.log", 3000))
    ma = sa["metrics"]
    check("load/play (a): a cold-load-only overrun does NOT breach PLAY",
          ma.get("log.play_evicted") is False and ma.get("log.play_evictions") == 0 and "log.play_evicted" not in ka
          and ma.get("log.errors_lower_bound") is True, (ma.get("log.play_evicted"), sorted(ka)))
    check("load/play (a): it is scored against LOAD: cold messages walked (frames and Unity lines out) + load-end scan",
          ma.get("log.cold_load_messages") == 3000 and ma.get("log.load_messages") == 3400
          and "log.load_messages" not in ka, (ma.get("log.cold_load_messages"), ma.get("log.load_messages"), sorted(ka)))
    lims = {x["key"]: x for x in RULES["limits"]}
    check("load/play: the LOAD limit is the ruled 4500 with '>' (loosening it must turn this red)",
          lims.get("log.load_messages", {}).get("value") == 4500 and lims["log.load_messages"].get("op") == ">"
          and lims.get("log.play_evicted", {}).get("op") == "==", lims.get("log.load_messages"))
    s45, k45 = lp_session("e1" * 16, cold_log("Player_e1.log", 4100))      # 4100 + 400 at the load-end scan = 4500
    check("load/play: exactly 4500 load messages passes LOAD", s45["metrics"].get("log.load_messages") == 4500
          and "log.load_messages" not in k45, (s45["metrics"].get("log.load_messages"), sorted(k45)))
    sb, kb = lp_session("b1" * 16, cold_log("Player_b1.log", 4101))       # 4501
    check("load/play (a): a cold load past the LOAD limit breaches LOAD, not PLAY, and says where the lines came from",
          "log.load_messages" in kb and "log.play_evicted" not in kb
          and "before RimBridge came up" in " | ".join(sb["attribution"].get("log.load_messages", [])), sorted(kb))
    for how in ("flag", "rise", "reset"):
        sc, kc = lp_session("c%s" % how[0] * 16, cold_log("Player_c%s.log" % how, 3000), play_evict=how)
        check("load/play (b): an in-play overrun DOES breach PLAY (%s)" % how,
              "log.play_evicted" in kc and sc["metrics"]["log.play_evictions"] >= 1 and "log.load_messages" not in kc
              and "after the load" in " | ".join(sc["attribution"].get("log.play_evicted", [])), sorted(kc))
    clean = cold_log("Player_f.log", 3000)

    def busy_end(rows, cs):              # the load-end walk was busy: the next walk's first-read verdict is the cold load
        cs[0].update(logScan="busy", logErrLowerBound=None)
        cs[0].pop("logEvicted", None)
        cs[1]["logEvicted"] = True
        return rows
    sf, kf = lp_session("f1" * 16, clean, tweak=busy_end)
    check("load/play: a busy load-end walk moves the load end to the next walk; its first-read overrun is not PLAY",
          "log.play_evicted" not in kf and sf["metrics"].get("log.play_evicted") is False
          and sf["metrics"].get("log.load_messages") == 3420, (sorted(kf), sf["metrics"].get("log.load_messages")))

    def no_count(rows, cs):              # a later row with no count still carries the companion's eviction verdict
        cs[20]["logMsgs"] = None
        cs[20]["logEvicted"] = True
        return rows
    sg, kg = lp_session("g1" * 16, clean, tweak=no_count)
    check("load/play: an eviction verdict on a row with no logMsgs still breaches PLAY", "log.play_evicted" in kg,
          sorted(kg))

    def flag_false(rows, cs):            # the companion says no eviction although the count rose 1500 (repeats)
        for r in cs[20:]:
            r["logMsgs"] += 1500
        return rows
    sh, kh = lp_session("h1" * 16, clean, tweak=flag_false)
    check("load/play: the companion's per-scan verdict outranks a count rise", "log.play_evicted" not in kh
          and sh["metrics"].get("log.play_evicted") is False, sorted(kh))

    def one_scan(rows, cs):              # nothing after the load-end scan: PLAY was never observed
        drop = {id(r) for r in cs[1:]}
        return [r for r in rows if id(r) not in drop]
    si, ki = lp_session("i1" * 16, clean, tweak=one_scan)
    check("load/play: no scan after the load-end scan is PLAY UNMEASURED, not a pass",
          not G.is_m(si["metrics"].get("log.play_evicted")) and G.is_m(si["metrics"].get("log.load_messages")),
          (si["metrics"].get("log.play_evicted"), si["metrics"].get("log.load_messages")))
    sd, kd = lp_session("d1" * 16, "C:/nowhere/Player_d1.log")
    check("load/play: no readable archive is LOAD UNMEASURED (never 0), and PLAY is still judged",
          not G.is_m(sd["metrics"]["log.load_messages"]) and sd["metrics"]["log.play_evicted"] is False,
          sd["metrics"]["log.load_messages"])
    # explain verb (OPS_GAME_HEALTH_DEBUG_PXQI): re-reads a session from disk, so a row recorded before attribution
    # existed (history rows are never re-summarized) is still explained; it must print every breach's attribution.
    import contextlib
    import io
    rec9 = os.path.join(tmp, "tps9")
    os.makedirs(rec9)
    write_session(rec9, rp)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc9 = G.main(["explain", "--dir", rec9, "--session", "9999"])
    ex = buf.getvalue()
    check("explain: exit 0 and every breach key printed with its attribution lines",
          rc9 == 0 and all(("  %s\n" % k) in ex for k in k9) and ex.count("    - ") >= len(k9), (rc9, ex[-600:]))
    check("explain: names the largest map, the stale save and the archived log",
          "924x924 RM_Big" in ex and "BENCH_STALE_SAVE" in ex and "Player_9.log" in ex, ex[-600:])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rcx = G.main(["explain", "--dir", rec9, "--session", "0123"])
    check("explain: an unknown session is exit 1, not an empty PASS", rcx == 1 and "FAIL" in buf.getvalue(),
          (rcx, buf.getvalue()))
    clean = session_rows(sid="8" * 32, heap_rate_h=0, errs_per_min=0, ratio1=1.0)
    s8 = G.summarize("8" * 32, [dict(r, _t=G.T._epoch(r["utc"])) for r in clean], 0, RULES, now=NOW)
    check("attribution: a session with no breach attributes nothing", s8["breaches"] == [] and s8["attribution"] == {},
          (s8["breaches"], s8["attribution"]))
    # fields verb (the live proof); the deployed-DLL preflight is pointed at an absent file so the host's game folder
    # never decides a selftest
    os.environ["RM_GAME_HEALTH_COMPANION_DLL"] = os.path.join(tmp, "absent.dll")
    old = G.T.record_dir
    G.T.record_dir = lambda: rec2
    try:
        check("fields: exit 0 on a session carrying the companion fields", G.main(["fields"]) == 0)
    finally:
        G.T.record_dir = old
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rcf = G.main(["fields", "--dir", rec, "--session", "c" * 32])
    check("fields: an old-companion session (no health field at all) is UNMEASURED exit 2, not FAIL",
          rcf == 2 and buf.getvalue().startswith("UNMEASURED:") and "FAIL" not in buf.getvalue(), (rcf, buf.getvalue()))
    stale = os.path.join(tmp, "stale.dll")
    with open(stale, "wb") as f:
        f.write(b"MZ\x90\x00" + "upS heapMB".encode("utf-16-le"))
    fresh = os.path.join(tmp, "fresh.dll")
    with open(fresh, "wb") as f:
        f.write(b"MZ\x90\x00" + "privateMB".encode("utf-16-le"))
    old = G.T.record_dir
    G.T.record_dir = lambda: rec2
    try:
        os.environ["RM_GAME_HEALTH_COMPANION_DLL"] = stale
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rcs = G.main(["fields"])
        check("fields: a deployed DLL without the health literal is UNMEASURED exit 2 even on a good session",
              rcs == 2 and buf.getvalue().startswith("UNMEASURED:") and "lacks" in buf.getvalue(), (rcs, buf.getvalue()))
        os.environ["RM_GAME_HEALTH_COMPANION_DLL"] = fresh
        check("fields: a deployed DLL serving the literal passes the preflight", G.main(["fields"]) == 0)
    finally:
        G.T.record_dir = old
        os.environ.pop("RM_GAME_HEALTH_COMPANION_DLL", None)
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
    ax = (hb.get("x") or {}).get("attribution") or {}
    check("ops_watch: the alarm carries the newest row's attribution, one entry per breach key",
          set(ax) == set((hb.get("x") or {}).get("keys") or ["?"]) and all(isinstance(v, str) and v for v in ax.values())
          and ax == {k: "; ".join(v)[:600] for k, v in (a.get("attribution") or {}).items()}, (ax, a.get("attribution")))
    # forwarding on the e50b27df replay: four breaches, four attributions reach tps.health_breaches
    def fake9(cmd, **k):
        verb = "latest" if "latest" in cmd else "record"
        return types.SimpleNamespace(returncode=0, stdout=json.dumps(s9 if verb == "latest" else {}), stderr="")
    OW.subprocess.run = fake9
    try:
        g9 = OW.game_health(NOW)
    finally:
        OW.subprocess.run = real
    x9 = (g9.get("tps.health_breaches") or {}).get("x") or {}
    check("ops_watch: replay alarm forwards an attribution for every breach (heap names the map, errors the save)",
          set(x9.get("attribution") or {}) == k9 and "924x924 RM_Big" in x9["attribution"].get("mem.managed_peak_mb", "")
          and "BENCH_STALE_SAVE" in x9["attribution"].get("log.errors", ""), x9)
    check("ops_watch: game off still reads the health check (5 rows: the torn line is not a session)", out.get("tps.ratio_median", {}).get("m") == "UNMEASURED"
          and out.get("tps.health_sessions", {}).get("v") == 5, out.get("tps.health_sessions"))
    tg = [t for t in OW.load_rules()["targets"] if t.get("key") == "tps.health_breaches"]
    check("ops_watch rules: the breach count alarms as OPS_GAME_HEALTH_DEBUG",
          tg and tg[0].get("alarm") is True and tg[0].get("name") == "OPS_GAME_HEALTH_DEBUG", tg)
    check("ops_watch: health keys are machine health (blind roles see them)",
          {"tps.health_breaches", "tps.health_age_h", "tps.health_sessions"} <= OW.BLIND_KEYS)

    # a debugged session stops ringing (OPS_GAME_HEALTH_DEBUG_PXQI gen 5): the alarm re-rang 19 times on the SAME
    # session e50b27df after its breaches were explained, since nothing could clear a finished session but a newer one.
    # A breach whose (session, key) is in the committed debugged record is carried as `debugged`, not counted; an
    # un-acked key, or any other session, still rings. The limits are untouched.
    h9 = os.path.join(tmp, "h9")
    os.makedirs(h9, exist_ok=True)
    with open(os.path.join(h9, "history.jsonl"), "w") as fh:
        fh.write(json.dumps(s9) + "\n")
    acks = os.path.join(tmp, "debugged.json")
    os.environ["RM_GAME_HEALTH_ACKS"] = acks
    old_dir = os.environ.get("RM_GAME_HEALTH_DIR")
    os.environ["RM_GAME_HEALTH_DIR"] = h9
    os.environ["RM_GAME_HEALTH_TPS_DIR"] = os.path.join(tmp, "empty_rec")
    os.makedirs(os.environ["RM_GAME_HEALTH_TPS_DIR"], exist_ok=True)

    def ring(ack_rows):
        with open(acks, "w") as fh:
            json.dump({"debugged": ack_rows}, fh)
        OW.subprocess.run = fake
        try:
            return OW.game_health(NOW).get("tps.health_breaches") or {}
        finally:
            OW.subprocess.run = real

    def verb(args):
        try:
            return G.main(args)
        except SystemExit as e:          # an absent verb must FAIL the check, not crash the test
            return "SystemExit %s" % e.code
    allk = sorted(k9)
    hb0 = ring([])
    check("debugged: with no record, the replay rings every breach", hb0.get("v") == len(k9), hb0)
    hb1 = ring([{"session": "9" * 32, "keys": allk, "item": "X_ITEM", "why": "bench maps"}])
    x1 = hb1.get("x") or {}
    check("debugged: a session whose every breach is debugged rings nothing (MEASURED 0)",
          hb1.get("m") == "MEASURED" and hb1.get("v") == 0, hb1)
    check("debugged: the debugged keys stay visible on the reading, with the item that debugged them",
          sorted((x1.get("debugged") or {})) == allk and all("X_ITEM" in str(v) for v in (x1.get("debugged") or {}).values()),
          x1)
    hb2 = ring([{"session": "9" * 32, "keys": [k for k in allk if k != "log.errors"], "item": "X_ITEM", "why": "w"}])
    check("debugged: an un-acked key still rings, alone", hb2.get("v") == 1 and (hb2.get("x") or {}).get("keys") ==
          ["log.errors"], hb2)
    hb3 = ring([{"session": "8" * 32, "keys": allk, "item": "X_ITEM", "why": "w"}])
    check("debugged: an ack for another session clears nothing", hb3.get("v") == len(k9), hb3)
    hb4 = ring([{"session": "9" * 8, "keys": allk, "item": "X_ITEM", "why": "w"}])
    check("debugged: a session prefix of 8 hex is enough (explain prints 8)", hb4.get("v") == 0, hb4)
    with open(acks, "w") as fh:
        json.dump({"debugged": []}, fh)
    check("debugged verb: refuses a session not in the history (exit 1)",
          verb(["debugged", "--session", "7" * 8, "--item", "X_ITEM", "--why", "w"]) == 1)
    rc = verb(["debugged", "--session", "9" * 8, "--item", "X_ITEM", "--why", "bench maps"])
    rows = (json.load(open(acks)).get("debugged") or []) if rc == 0 else []
    check("debugged verb: writes one row naming the full session, every current breach key, item and why",
          rc == 0 and len(rows) == 1 and rows[0].get("session") == "9" * 32 and sorted(rows[0].get("keys") or []) == allk
          and rows[0].get("item") == "X_ITEM" and rows[0].get("why") == "bench maps", (rc, rows))
    check("debugged verb: refuses an empty why (exit 2)",
          verb(["debugged", "--session", "9" * 8, "--item", "X_ITEM", "--why", " "]) == 2)
    lat = None
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        verb(["latest", "--json"])
    try:
        lat = json.loads(buf.getvalue())
    except ValueError:
        pass
    check("latest --json: carries open_breaches [] and every key under debugged once the session is acked",
          isinstance(lat, dict) and lat.get("open_breaches") == [] and sorted(lat.get("debugged") or {}) == allk,
          (lat or {}).get("open_breaches"))
    shipped = json.load(open(os.path.join(HERE, "game_health_debugged.json"))) if os.path.exists(
        os.path.join(HERE, "game_health_debugged.json")) else {}
    e50 = [r for r in shipped.get("debugged") or [] if str(r.get("session", "")).startswith("e50b27df")]
    check("shipped record: e50b27df is debugged, all five keys, by this item",
          len(e50) == 1 and set(e50[0].get("keys") or []) == {"mem.managed_peak_mb", "mem.managed_growth_mb_per_h",
                                                            "mem.private_peak_mb", "log.errors", "log.errors_lower_bound"}
          and e50[0].get("item") == "OPS_GAME_HEALTH_DEBUG_PXQI", e50)
    with open(acks, "w") as fh:
        fh.write("{not json")
    OW.subprocess.run = fake
    try:
        hb5 = OW.game_health(NOW).get("tps.health_breaches") or {}
    finally:
        OW.subprocess.run = real
    check("debugged: a corrupt record debugs nothing, every breach still rings", hb5.get("v") == len(k9), hb5)
    os.environ.pop("RM_GAME_HEALTH_ACKS", None)
    if old_dir is not None:
        os.environ["RM_GAME_HEALTH_DIR"] = old_dir

print("\n%d failed" % len(FAILS) if FAILS else "\nALL PASS")
sys.exit(1 if FAILS else 0)
