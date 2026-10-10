#!/usr/bin/env python3
"""Offline selftest of the standing health observer (GAME_OBSERVER_BUILD_OUTSIDE_LOOKING_IN).

    python3 src/RimMandrake/Utils/selftest_health_observer.py

Runs on either OS. The Windows probes themselves are only exercised under python.exe (the last
check); everything else drives the collector with injected probes, so the CONTRACTS are tested:
an unavailable or failed source never reads as zero, a switched-off source is never probed, seq
orders the stream across segments, the log tail survives truncation and rotation without
rereading, a game identity is pid + creation time, and the joined reader states evidence without
verdicts.
"""
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

FAILS = []


def check(name, ok, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  -- %s" % detail))
    if not ok:
        FAILS.append(name)


def main():
    try:
        import health_observer as H
    except ImportError as e:
        check("health_observer imports", False, e)
        return 1
    tmp = tempfile.mkdtemp(prefix="hobs_")

    # 1. stable source ids, each with a question and a default switch
    need = {"obs.heartbeat", "game.identity", "game.cpu", "game.mainthread", "game.memory", "sys.memory",
            "log.growth", "log.milestones"}
    check("every required source id is registered", need <= set(H.SOURCES), sorted(need - set(H.SOURCES)))
    check("every source states the question it answers",
          all(isinstance(v.get("question"), str) and len(v["question"]) > 10 for v in H.SOURCES.values()))

    # 2. statuses: unavailable / failed / off are never a value, ok carries a measured cost
    called = []

    def p_none(ctx):
        return None

    def p_boom(ctx):
        raise OSError("access denied")

    def p_ok(ctx):
        return {"x": 1}

    def p_spy(ctx):
        called.append(1)
        return {"y": 2}

    probes = {"game.cpu": p_none, "game.memory": p_boom, "sys.memory": p_ok, "log.growth": p_spy}
    c = H.Collector(os.path.join(tmp, "s2"), probes=probes, switches={"log.growth": False}, interval=5)
    r = c.sample()
    s = r["sources"]
    check("a probe returning None is 'unavailable', with no value", s["game.cpu"]["status"] == "unavailable"
          and "value" not in s["game.cpu"], s["game.cpu"])
    check("a probe that raises is 'failed', with its error and no value", s["game.memory"]["status"] == "failed"
          and "access denied" in s["game.memory"].get("error", "") and "value" not in s["game.memory"],
          s["game.memory"])
    check("a switched-off source reads 'off' and is never probed", s["log.growth"]["status"] == "off" and not called,
          (s["log.growth"], called))
    check("an ok source carries its value and a measured costUs", s["sys.memory"]["status"] == "ok"
          and s["sys.memory"]["value"] == {"x": 1} and isinstance(s["sys.memory"].get("costUs"), (int, float)),
          s["sys.memory"])
    hb = s["obs.heartbeat"]["value"]
    check("the heartbeat counts the failed probe per source", hb["failedProbes"].get("game.memory") == 1, hb)
    check("the heartbeat carries the collector's own CPU and per-source cumulative cost",
          "collectorCpuS" in hb and "costMsTotal" in hb and "sys.memory" in hb["costMsTotal"], hb)
    check("the row names its collector identity and schema", r.get("collector", {}).get("id")
          and r.get("v") == H.SCHEMA and r.get("kind") == "sample", r)

    # 3. settings file switches a source; an unknown id is reported, not fatal
    sd = os.path.join(tmp, "s3")
    os.makedirs(sd)
    with open(os.path.join(sd, H.SETTINGS_NAME), "w") as f:
        json.dump({"sources": {"sys.memory": False, "no.such": True}}, f)
    c3 = H.Collector(sd, probes=probes)
    r3 = c3.sample()
    check("the settings file switches a source off", r3["sources"]["sys.memory"]["status"] == "off",
          r3["sources"]["sys.memory"])
    check("an unknown id in settings is reported on the start row", "no.such" in json.dumps(c3.start_row), c3.start_row)

    # 4. seq strictly increases across segment rotation; the reader reads every row back and counts junk
    sd = os.path.join(tmp, "s4")
    c4 = H.Collector(sd, probes={"sys.memory": p_ok}, segment_bytes=600)
    for _ in range(12):
        c4.sample()
    segs = [n for n in os.listdir(sd) if n.endswith(".jsonl")]
    check("small segments rotate into several files", len(segs) >= 3, segs)
    with open(os.path.join(sd, sorted(segs)[0]), "a") as f:
        f.write("{torn\n")
    rd = H.read_stream(sd)
    seqs = [x["seq"] for x in rd["rows"] if x["collector"]["id"] == c4.ident["id"]]
    check("seq is 0..n without gaps across segments", seqs == list(range(len(seqs))) and len(seqs) >= 13, seqs)
    check("a torn line is counted as malformed, not dropped silently", rd["malformed"] == 1, rd["malformed"])

    # 5. log tail: growth, truncation, rotation, read cap (never rereads the whole file)
    lp = os.path.join(tmp, "Player.log")
    with open(lp, "wb") as f:
        f.write(b"a" * 1000 + b"\n")
    t = H.LogTail(lp, read_cap=4096, first_read_cap=8192)
    a = t.poll(100.0)
    with open(lp, "ab") as f:
        f.write(b"b" * 499 + b"\n")
    b = t.poll(110.0)
    check("growth is bytes since last poll and bytes/s", b["grewBytes"] == 500 and abs(b["bytesPerS"] - 50) < 1e-6, b)
    with open(lp, "wb") as f:
        f.write(b"new\n")
    c_ = t.poll(120.0)
    check("a shrink in place is reported as truncation, and the tail restarts at 0", c_["truncated"]
          and c_["newBytes"] == 4 and c_["grewBytes"] is None, c_)
    with open(lp + ".new", "wb") as f:
        f.write(b"rotated content line\n")
    os.replace(lp + ".new", lp)
    d = t.poll(130.0)
    check("a replaced file is reported as rotation and read from its start", d["rotated"]
          and d["newBytes"] == len(b"rotated content line\n"), d)
    with open(lp, "ab") as f:
        f.write(b"x" * 20000 + b"\n")
    e = t.poll(140.0)
    check("a burst over the read cap is skipped and counted, not reread", e["skippedBytes"] > 0
          and e["newBytes"] <= 4096 and t.offset == os.path.getsize(lp), e)
    check("bytes/s is still the real growth even when reading was capped", e["grewBytes"] == 20001, e)
    os.remove(lp)
    g = t.poll(150.0)
    check("a missing log is 'missing', not zero growth", g.get("missing") and g["grewBytes"] is None, g)
    check("the very first poll reports no rate (no baseline)", a["bytesPerS"] is None, a)
    with open(lp, "wb") as f:
        f.write(b"q" * 50000)
    t2 = H.LogTail(lp, read_cap=4096, first_read_cap=8192)
    f2 = t2.poll(1.0)
    check("first sight reads at most first_read_cap and skips the rest", f2["newBytes"] == 8192
          and f2["skippedBytes"] == 50000 - 8192, f2)

    # 6. milestones: line split across reads seen once; the cap line says activity is unknown
    m = H.Milestones()
    ev = m.feed(b"Mono path[0] = 'C:/x'\r\nInitialize engine ver", 0)
    ev += m.feed(b"sion: 2022.3.35f1 (011206c7a712)\r\nRimWorld 1.6.4871 rev591\r\n", 50)
    ev += m.feed(b"Initialize engine version: again\r\n", 200)
    ids = [x["id"] for x in ev]
    check("milestones found once each, across a split line", ids == ["engine.mono", "engine.init", "game.version"],
          ids)
    ev = m.feed(b"Reached max messages limit. Stopping logging to avoid spam.\n", 300)
    check("the Verse.Log cap is a milestone saying emission suppressed, activity unknown",
          ev and ev[0]["id"] == "log.cap-reached" and "error activity unknown" in ev[0]["meaning"], ev)
    m.reset()
    ev = m.feed(b"Initialize engine version: 2\n", 0)
    check("a rotated log resets milestones (a new launch is seen afresh)", [x["id"] for x in ev] == ["engine.init"], ev)
    big = H.Milestones()
    big.feed(b"z" * 300000, 0)
    check("an endless line does not grow the carry buffer without bound", len(big.carry) <= H.Milestones.CARRY_MAX,
          len(big.carry))

    # 7. CPU rate identity: a reused pid is a different process; a clock that runs backwards gives no rate
    p0 = {"ident": (42, 1000), "cpuS": 10.0, "mono": 100.0}
    check("same process: cores = cpu delta / mono delta", H.cores(p0, {"ident": (42, 1000), "cpuS": 15.0,
                                                                        "mono": 110.0}) == (0.5, None))
    check("same pid, different creation time: no rate (pid reuse)",
          H.cores(p0, {"ident": (42, 2000), "cpuS": 1.0, "mono": 110.0}) == (None, "identity-changed"))
    check("mono going backwards: no rate", H.cores(p0, {"ident": (42, 1000), "cpuS": 11.0, "mono": 90.0})[0] is None)
    check("no previous sample: no rate", H.cores(None, p0) == (None, "no-baseline"))

    # 8. main thread rule: earliest-created thread, labelled as an assumption
    tid, rule = H.pick_main_thread([(7, 500), (3, 100), (9, 100.5)])
    check("main thread = earliest-created thread of the process", tid == 3 and "assumed" in rule, (tid, rule))
    check("no threads: no main thread", H.pick_main_thread([])[0] is None)

    # 9. single instance
    ld = os.path.join(tmp, "lock")
    os.makedirs(ld)
    l1 = H.acquire_lock(ld)
    l2 = H.acquire_lock(ld)
    check("a second collector cannot take the lock while the first holds it", l1 is not None and l2 is None)
    H.release_lock(l1)
    l3 = H.acquire_lock(ld)
    check("the lock is free again once released", l3 is not None)
    H.release_lock(l3)

    # 10. joined reader: evidence, uncertainty, no verdicts
    rows = [
        {"kind": "sample", "utc": "2026-10-10T15:00:00.000Z", "sources": {
            "game.cpu": {"status": "ok", "value": {"procs": [{"pid": 5, "startUtc": "S", "cores": 1.02}]}},
            "game.mainthread": {"status": "unavailable", "reason": "thread not identified"},
            "game.memory": {"status": "ok", "value": {"procs": [{"pid": 5, "startUtc": "S", "privateMB": 9000,
                                                                 "workingSetMB": 7000}]}},
            "sys.memory": {"status": "ok", "value": {"availPhysMB": 1200, "commitHeadroomMB": 800}},
            "log.growth": {"status": "ok", "value": {"bytesPerS": 52000.0}},
            "obs.heartbeat": {"status": "ok", "value": {"lateS": 0}}}, "collector": {"id": "c"}, "seq": 0},
    ]
    inc = [{"_t": H.epoch("2026-10-10T15:00:03.000Z"), "kind": "incident", "type": "stall", "gapS": 40}]
    lines = H.join_incidents(inc, rows, window_s=30)
    text = "\n".join(lines)
    check("the join prints observed values beside the incident", "1.02" in text and "52000" in text and "9000" in text,
          text)
    check("an unavailable source reads 'unavailable', never 0", "main thread unavailable" in text, text)
    check("the join states no cause", not any(w in text.lower() for w in ("because", "caused", "blame", "tight loop",
                                                                            "spinning")), text)
    none = H.join_incidents(inc, [], window_s=30)
    check("an incident with no observer sample says NO OBSERVER COVERAGE", "NO OBSERVER COVERAGE" in "\n".join(none),
          none)

    # 10b. tps_record --health prints the observer section (empty TPS record: coverage is stated, not invented)
    import contextlib
    import io
    import tps_record
    hd = os.path.join(tmp, "s10")
    c10 = H.Collector(hd, probes={"sys.memory": p_ok})
    c10.sample()
    try:
        import zoneinfo
        zoneinfo.ZoneInfo("UTC")
        have_tz = True
    except Exception:                                           # noqa: BLE001
        have_tz = False             # Windows python without tzdata: tps_record cannot parse zoned times at all
    buf = io.StringIO()
    if not have_tz:
        print("SKIP  tps_record --health join (no tzdata on this interpreter; tps_record refuses zones here)")
    else:
      with contextlib.redirect_stdout(buf):
          rc = tps_record.main(["--dir", os.path.join(tmp, "no_tps"), "--since", "2000-01-01T00:00:00Z",
                                "--until", "2100-01-01T00:00:00Z", "--tz", "UTC", "--health", "--health-dir", hd])
      out = buf.getvalue()
      check("tps_record --health joins the observer stream", rc == 0 and "external observer" in out
            and "1 samples in range" in out, out[-600:])

    # 11. the real probes on this OS: off-Windows every Windows source is unavailable, never zero
    real = H.Collector(os.path.join(tmp, "s11"), log_path=os.path.join(tmp, "absent.log"))
    rr = real.sample()["sources"]
    if os.name != "nt":
        bad = {k: v for k, v in rr.items() if k.startswith(("game.", "sys.")) and v["status"] == "ok"}
        check("off Windows the Windows probes report unavailable", not bad, bad)
    else:
        check("on Windows sys.memory reads real numbers", rr["sys.memory"]["status"] == "ok"
              and rr["sys.memory"]["value"]["availPhysMB"] > 0, rr["sys.memory"])
        check("on Windows game.identity probes (ok, with a process list)", rr["game.identity"]["status"] == "ok",
              rr["game.identity"])
    print("%d failed" % len(FAILS) if FAILS else "all passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
