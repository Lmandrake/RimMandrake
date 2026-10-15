#!/usr/bin/env python3
"""Offline selftest of the two observer-side spike metrics (design/RimMandrake/game_health_record.md):

  spike.early-load  health_earlyload.py  -- where a cold load went quiet before the companion existed
  spike.minidump    health_minidump.py   -- one small dump per incident, headroom checked, retention capped

    python3 src/RimMandrake/Utils/selftest_health_spikes.py

Pure logic only: no game, no dump is written, no process is opened. Written failing-first (2026-10-14).
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

FAILS = []
N = [0]


def check(name, ok, detail=""):
    N[0] += 1
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  -- %s" % detail))
    if not ok:
        FAILS.append(name)


def sample(t, size=None, status="ok", procs=1, grew=None):
    lg = {"status": status}
    if status == "ok":
        lg["value"] = {"size": size, "grewBytes": grew, "missing": size is None}
    return {"kind": "sample", "_t": t, "utc": "t%s" % t,
            "sources": {"log.growth": lg, "game.identity": {"status": "ok", "value": {"procs": [{"pid": 1}] * procs}}}}


def milestone(t, mid):
    return {"kind": "event", "event": "milestone", "id": mid, "_t": t, "utc": "t%s" % t}


def early_load():
    try:
        import health_earlyload as E
    except Exception as e:                                       # noqa: BLE001
        check("earlyload_imports", False, repr(e))
        return
    check("earlyload_imports", True)
    # sizes: growing to t=20, flat from 20 to 120 (100 s silence), growing again at 125
    rows = [sample(0, 100), sample(5, 200, grew=100), sample(10, 300, grew=100), sample(15, 400, grew=100),
            sample(20, 500, grew=100)]
    rows += [sample(t, 500, grew=0) for t in range(25, 125, 5)]
    rows += [sample(125, 900, grew=400)]
    s = E.silences(rows, min_s=30)
    check("one_silence_found", len(s) == 1, s)
    if s:
        check("silence_bounds", s[0]["fromT"] == 20 and s[0]["toT"] == 125 and s[0]["open"] is False and s[0]["sizeAt"] == 500, s[0])
    check("short_quiet_ignored", E.silences(rows, min_s=200) == [])
    # an unavailable sample is a coverage gap, never silence
    gap = [sample(0, 100), sample(5, 200, grew=100)] + [sample(t, status="unavailable") for t in range(10, 100, 5)] + [sample(100, 200, grew=0)]
    sg = E.silences(gap, min_s=30)
    check("unavailable_is_not_silence", sg == [], sg)
    check("coverage_gaps_reported", len(E.coverage_gaps(gap, min_s=30)) == 1, E.coverage_gaps(gap, min_s=30))
    # still quiet at the end -> open silence
    op = [sample(0, 100), sample(5, 200, grew=100)] + [sample(t, 200, grew=0) for t in range(10, 80, 5)]
    so = E.silences(op, min_s=30)
    check("open_silence", len(so) == 1 and so[0]["open"] is True, so)
    # no game process -> not a load silence
    dead = [sample(0, 100, procs=0), sample(5, 100, grew=0, procs=0)] + [sample(t, 100, grew=0, procs=0) for t in range(10, 100, 5)]
    check("no_process_no_silence", E.silences(dead, min_s=30) == [])
    # phase from the last milestone before the silence
    ms = [milestone(1, "engine.mono"), milestone(3, "engine.init"), milestone(200, "rimbridge.startup")]
    check("phase_before_bridge", E.phase_at(ms, 20).startswith("mod and def loading"), E.phase_at(ms, 20))
    check("phase_after_companion", "TPS record" in E.phase_at(ms + [milestone(250, "jawabench.ready")], 300))
    check("phase_unknown_without_milestones", E.phase_at([], 20).startswith("unknown"))
    # last complete line before an offset
    data = b"line one\nline two\npartial thr"
    check("last_line_complete", E.last_line(data, len(data)) == "line two", E.last_line(data, len(data)))
    check("last_line_at_boundary", E.last_line(b"a\nb\n", 4) == "b")
    check("last_line_empty", E.last_line(b"", 0) is None)
    txt = E.describe({"fromT": 20, "toT": 125, "open": False, "sizeAt": 500, "durS": 105}, "mod and def loading", "Loading Defs...", lambda t: "T%s" % t)
    check("wording_is_not_a_verdict", "not proven to be where the load stalled" in txt and "Loading Defs" in txt and "caused" not in txt, txt)
    check("wording_unknown_line", "unavailable" in E.describe({"fromT": 1, "toT": 2, "open": True, "sizeAt": 5, "durS": 1}, "x", None, str))


def minidump():
    try:
        import health_minidump as D
    except Exception as e:                                       # noqa: BLE001
        check("minidump_imports", False, repr(e))
        return
    check("minidump_imports", True)
    GB = 1024 ** 3
    ok, why = D.headroom_ok(free_bytes=50 * GB, working_set_bytes=8 * GB)
    check("headroom_ok_when_ample", ok, why)
    ok, why = D.headroom_ok(free_bytes=2 * GB, working_set_bytes=8 * GB)
    check("headroom_refused_when_short", not ok and "free" in why, why)
    ok, why = D.headroom_ok(free_bytes=None, working_set_bytes=8 * GB)
    check("headroom_unknown_refuses", not ok and "unavailable" in why, why)
    d = tempfile.mkdtemp()
    check("first_capture_allowed", D.incident_claim(d, "stall-2026-10-14T03:00Z") is None)
    again = D.incident_claim(d, "stall-2026-10-14T03:00Z")
    check("one_capture_per_incident", again is not None and "already" in again, again)
    check("incident_key_sanitised", D.incident_claim(d, "../../evil") is None and os.path.exists(os.path.join(d, "incident_.._.._evil.claim")) is False
          and any(n.startswith("incident_") for n in os.listdir(d)))
    files = [("a.dmp", 100, 1.0), ("b.dmp", 100, 2.0), ("c.dmp", 100, 3.0), ("d.dmp", 100, 4.0)]
    check("retention_keeps_newest", D.to_prune(files, keep=2, cap_bytes=10 ** 9) == ["a.dmp", "b.dmp"], D.to_prune(files, keep=2, cap_bytes=10 ** 9))
    check("retention_cap_bytes", D.to_prune(files, keep=10, cap_bytes=250) == ["a.dmp", "b.dmp"], D.to_prune(files, keep=10, cap_bytes=250))
    check("dump_type_is_small", D.DUMP_FLAGS & D.MiniDumpWithFullMemory == 0 and D.DUMP_FLAGS & D.MiniDumpWithThreadInfo)
    check("never_automatic", D.AUTOMATIC is False)


def main():
    early_load()
    minidump()
    bad = len(FAILS)
    print("health spikes: %d/%d passed" % (N[0] - bad, N[0]))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
