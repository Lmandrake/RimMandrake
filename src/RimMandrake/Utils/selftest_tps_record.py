#!/usr/bin/env python3
"""Offline selftest of the TPS record (BRIDGE_TPS_CAPTURE_FIXES_1 criteria C1 and C2).

    python3 src/RimMandrake/Utils/selftest_tps_record.py            Python checks + C# parity
    python3 src/RimMandrake/Utils/selftest_tps_record.py --no-cs    Python checks only

1. C1 - the window accumulator replayed over synthetic FRAME TRACES that mimic the engine
   (TickManagerUpdate credits the frame's real time only when unpaused, ticks at the multiplier
   it reads that frame, caps at 2 x mult per frame): healthy play, a partial pause, a Superfast
   12x/6x flip, a forced-normal change inside the tick loop, an autosave long event, a recovered
   90 s stall, a stall while paused, and genuinely slow ticking. Hand-worked expectations.
2. C2 - the reader: --at/--tz, --since/--until, concurrent segment rotation, future timestamps,
   malformed rows, stale vs performance verdicts, contiguous sustained warnings.
3. The PRODUCTION C# (JawaBenchTpsMath.cs) built on Windows via winbuild staging into
   bridgetools/TpsMathSelfTest and fed the same traces and vectors: every answer must match the
   Python port line for line, constants included. Without dotnet.exe this half FAILS loudly
   (exit 1) rather than passing on half the evidence; --no-cs accepts Python-only explicitly.
"""
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import tps_record as T  # noqa: E402

FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)


# ---- frame traces (C1) ------------------------------------------------------------------------

def num(x):
    """A number as the trace line carries it; both sides parse the same string."""
    return ("%.6f" % x).rstrip("0").rstrip(".") if isinstance(x, float) else str(x)


class Sim:
    """A crude engine: frames of `fps`, ticks = 60 x mult x credited time x factor, capped at 2 x mult."""
    def __init__(self, fps=60.0):
        self.t, self.ticks, self.fps, self.rows = 0.0, 0, fps, []
        self.debt = 0.0

    def frame(self, dt, paused, mult, factor=1.0, explained=0.0, mult_after=None, sim=0.002):
        self.t += dt
        before = self.ticks
        if not paused:
            self.debt += 60.0 * mult * min(dt, 1.0 / 3.0) * factor  # Unity clamps deltaTime
            n = min(int(self.debt + 1e-9), int(2 * mult))
            self.debt = 0.0 if n == int(2 * mult) else self.debt - n
            self.ticks += n
        self.rows.append((round(self.t, 6), 1 if paused else 0, mult, before, explained,
                          mult if mult_after is None else mult_after, self.ticks, sim))

    def run(self, seconds, paused=False, mult=1, factor=1.0):
        for _ in range(int(round(seconds * self.fps))):
            self.frame(1.0 / self.fps, paused, mult, factor)


def traces():
    out = {}
    s = Sim(); s.run(12.05); out["healthy1"] = s.rows
    s = Sim(); s.run(1.5); s.run(2.0, paused=True); s.run(2.0); s.run(0.2); out["partialpause"] = s.rows
    s = Sim(fps=30); s.run(3.0, mult=12); s.run(2.5, mult=6); s.run(0.2, mult=6); out["superflip"] = s.rows
    s = Sim(); s.run(2.0, mult=6); s.frame(1 / 60, False, 6, mult_after=1); s.run(3.2, mult=1); out["forcednormal"] = s.rows
    s = Sim()
    for _ in range(160):   # forced normal flips inside the tick loop every frame: ambiguous -> mixed
        s.frame(1 / 60, False, 6, mult_after=1); s.frame(1 / 60, False, 1, mult_after=6)
    s.run(0.2, mult=6); out["flipflop"] = s.rows
    s = Sim(); s.run(1.0); s.frame(12.0, False, 1, explained=12.0); s.run(5.2); out["autosave"] = s.rows
    s = Sim(); s.run(1.0, mult=3); s.frame(90.0, False, 3); s.run(5.2, mult=3); out["stall90"] = s.rows
    s = Sim(); s.run(1.0, paused=True); s.frame(15.0, True, 1); s.run(1.0, paused=True); out["pausedstall"] = s.rows
    s = Sim(); s.run(10.1, mult=3, factor=0.5); out["slow"] = s.rows
    # MUST 5: a 90 s unexplained gap ACROSS a speed change (1x before, 3x after) must stay in expected ticks
    s = Sim(); s.run(1.0, mult=1); s.frame(90.0, False, 3); s.run(5.2, mult=3); out["stallflip"] = s.rows
    # ... and across a pause -> run change
    s = Sim(); s.run(1.0, paused=True); s.frame(90.0, False, 1); s.run(5.2); out["stallunpause"] = s.rows
    # MUST 3: a 40 s CURRENT invocation (DoSingleTick) at the cadence boundary: the next prefix is 40 s later
    s = Sim(); s.run(5.0); s.frame(1 / 60, False, 1, sim=40.0); s.frame(40.0 + 1 / 60, False, 1); s.run(5.2)
    out["longtick"] = s.rows
    # MUST 3/34: the tick counter goes BACKWARDS (a new game under the same accumulator)
    s = Sim(); s.run(3.0); s.ticks = 10; s.run(3.0); s.run(0.2); out["tickreset"] = s.rows
    return out


def replay_py(rows):
    acc, lines = T.FrameAccumulator(), []
    for r in rows:
        f = [float(num(x)) if i in (0, 2, 4, 5, 7) else int(x) for i, x in enumerate(r)]
        g = acc.pre(f[0], bool(f[1]), f[2], f[3], f[4])
        if g is not None:
            lines.append('G "type":"%s",' % T.gap_kind(g) + T.gap_fields(g))
        w = acc.take_closed()
        if w is not None:
            lines.append("W " + T.window_fields(w))
        acc.post(f[5], f[6], f[7])
    return lines


def parse(line):
    return json.loads("{" + line[2:] + "}")


def trace_checks(tr):
    res = {k: replay_py(v) for k, v in tr.items()}
    W = lambda k: [parse(x) for x in res[k] if x.startswith("W ")]  # noqa: E731
    G = lambda k: [parse(x) for x in res[k] if x.startswith("G ")]  # noqa: E731

    w = W("healthy1")
    check(len(w) == 2 and all(x["state"] == "run" and abs(x["ratio"] - 1) < 0.02 for x in w), "healthy speed 1: %r" % w)
    w = W("partialpause")[0]
    check(w["state"] == "run" and abs(w["ratio"] - 1) < 0.03 and 0.3 < w["pausedFrac"] < 0.45,
          "a 40%% partial pause must not read slow (old model: ratio ~0.6): %r" % w)
    w = W("superflip")[0]
    check(w["state"] == "run" and abs(w["ratio"] - 1) < 0.03 and w["multMin"] == 6 and w["multMax"] == 12,
          "Superfast 12x->6x integrated per frame, ratio ~1: %r" % w)
    w = W("forcednormal")[0]
    check(w["ambigS"] > 0 and w["state"] == "run", "one mid-loop multiplier change is flagged, not judged mixed: %r" % w)
    w = W("flipflop")[0]
    check(w["state"] == "mixed", "repeated mid-loop flips -> mixed, never judged: %r" % w)
    g, w = G("autosave"), W("autosave")
    check(len(g) == 1 and g[0]["type"] == "longevent" and g[0]["gapS"] == 12, "autosave gap is a longevent incident: %r" % g)
    check(w and w[0]["state"] == "longevent" and w[0]["explainedS"] == 12, "autosave window is longevent: %r" % w)
    check(len(w) > 1 and w[1]["state"] == "run" and abs(w[1]["ratio"] - 1) < 0.03, "after the save, healthy again: %r" % w)
    g, w = G("stall90"), W("stall90")
    check(len(g) == 1 and g[0]["type"] == "stall" and g[0]["unexplainedS"] == 90, "90 s stall is an incident: %r" % g)
    check(w and w[0]["state"] == "stall" and w[0]["dReal"] > 90 and w[0]["ratio"] < 0.05,
          "90 s stall window is KEPT (no 60 s discard) and never subtracted from expected: %r" % w)
    g, w = G("pausedstall"), W("pausedstall")
    check(len(g) == 1 and g[0]["type"] == "stall" and g[0]["pausedAfter"] is True and w and w[0]["state"] == "stall",
          "a freeze while paused is still a stall incident: %r %r" % (g, w))
    w = W("slow")
    check(w and all(x["state"] == "run" and abs(x["ratio"] - 0.5) < 0.05 for x in w), "half-speed ticking -> 0.5: %r" % w)
    w = W("longtick")
    check(w and all(x["simShare"] <= 1.0 for x in w),
          "MUST 3: tick work is placed in the window whose real time contains it (simShare <= 1): %r"
          % [(x["state"], x["dReal"], x["simMs"], x["simShare"]) for x in w])
    check(any(x["dReal"] > 40 and x["simMs"] >= 40000 for x in w),
          "MUST 3: the 40 s tick and the 40 s gap it caused are in the SAME window: %r"
          % [(x["state"], x["dReal"], x["simMs"]) for x in w])
    for k in ("healthy1", "longtick", "autosave"):
        ws = W(k)
        check(all("monoStart" in x and "monoEnd" in x and abs(x["monoEnd"] - x["monoStart"] - x["dReal"]) < 0.002
                  for x in ws), "MUST 3: every window carries its explicit [monoStart, monoEnd] (%s): %r" % (k, ws[:1]))
        check(all(abs(b.get("monoStart", -9) - a.get("monoEnd", 9)) < 1e-6 for a, b in zip(ws, ws[1:])),
              "MUST 3: consecutive windows abut exactly (%s)" % k)
    ws, fr = W("healthy1"), tr["healthy1"]
    end = [f for f in fr if ws and abs(f[0] - ws[-1].get("monoEnd", -1)) < 0.0006]
    check(ws and abs(ws[0].get("monoStart", -1) - fr[0][0]) < 0.0006 and end
          and sum(x["dTicks"] for x in ws) == end[0][3] - fr[0][3],
          "MUST 3/6: windows start at the first observed prefix and count every tick from there to the last "
          "boundary, first frame included: %r" % [(x.get("monoStart"), x["dTicks"]) for x in ws])
    w = W("tickreset")
    check(any(x.get("tickReset") for x in w) and all(x["dTicks"] >= 0 for x in w),
          "MUST 3: a tick counter that goes backwards is flagged tickReset, never a silent clamp: %r"
          % [(x["dTicks"], x.get("tickReset")) for x in w])
    w = W("stallflip")
    check(w and w[0]["state"] == "stall" and w[0]["runS"] > 90 and w[0]["ratio"] is not None and w[0]["ratio"] < 0.05
          and w[0].get("expectedLo") is not None and w[0]["expectedLo"] <= w[0]["expected"],
          "MUST 5: a 90 s gap across a speed change stays in expected ticks (ratio < 0.05, range lo..hi): %r" % w[:1])
    w = W("stallunpause")
    check(w and w[0]["state"] == "stall" and w[0]["ratio"] is not None and w[0]["ratio"] < 0.05
          and w[0].get("ratioHi") is None,
          "MUST 5: a 90 s gap across pause->run keeps the gap (expected hi), lo = 0 so ratioHi is null: %r" % w[:1])
    return res


# ---- scalar vectors ---------------------------------------------------------------------------
M_VECTORS = [[], [5], [3, 1, 2], [4, 1, 3, 2], [60, 59.5, 12, 61]]
S_VECTORS = [[0.5] * 5, [0.5] * 6, [1.0] + [0.4] * 6, [0.4] * 5 + [0.9], [1.3] * 6, [1.0] * 8, [0.6] * 6]
# MUST 7: the sampler's streak is judged on the value the disk carries (3 decimals), so C# and the reader agree
Q_VECTORS = [[0.5996] * 6, [1.1504] * 6, [0.5994] * 6]
R_VECTORS = [(0, 3_000_000), (2_097_000, 100), (2_097_100, 100), (2_097_152, 1), (10, 10)]
N_VECTORS = [(1_791_640_000, "0123456789abcdef0123456789abcdef", 4242, 0), (0, "ab", 1, 17)]
X_VECTORS = [  # (bytes, ageDays, current) ..., cap
    ([(100, 8.0, 0), (100, 1.0, 0), (100, 0.1, 1)], 10_000),
    ([(100, 9.0, 1), (100, 3.0, 0)], 10_000),
    ([(400, 3.0, 0), (400, 2.0, 0), (400, 1.0, 0), (400, 0.0, 1)], 1000),
    ([], 5),
]


def const_line():
    return "K " + " ".join([
        T.F(T.CADENCE_SECONDS, 4), T.F(T.GAP_SECONDS, 4), T.F(T.EXPLAINED_SHARE, 4), T.F(T.TICKS_PER_SECOND_AT_SPEED1, 4),
        T.F(T.PAUSED_SHARE, 4), T.F(T.STALL_SHARE, 4), T.F(T.LONG_EVENT_SHARE, 4), T.F(T.MIXED_SHARE, 4),
        T.F(T.FRAME_BUDGET_SECONDS, 4), str(T.MAX_GAPS_PER_WINDOW), str(T.SEGMENT_BYTES), T.F(T.RETENTION_DAYS, 4),
        str(T.RETENTION_BYTES), str(T.LOG_RETENTION_BYTES), str(T.QUEUE_CAPACITY), T.F(T.SILENCE_SECONDS, 4),
        T.F(T.SILENCE_REPEAT_SECONDS, 4), str(T.RING_CAPACITY), str(T.SUSTAINED_SAMPLES), T.F(T.LOW_RATIO, 4),
        T.F(T.HIGH_RATIO, 4)])


def py_lines(tr, res):
    out = [const_line()]
    for k in tr:
        out.append("A " + k)
        out += res[k]
    out += ["M " + T.F(T.median(xs), 3) for xs in M_VECTORS]
    out += ["S " + T.sustained(xs) for xs in S_VECTORS]
    out += ["Q " + T.sustained([float(T.F(x, 3)) for x in xs]) for xs in Q_VECTORS]
    out += ["R %d" % (1 if T.should_rotate(c, n) else 0) for c, n in R_VECTORS]
    out += ["N " + T.segment_name(*v) for v in N_VECTORS]
    for items, cap in X_VECTORS:
        d = T.plan_retention([i[0] for i in items], [i[1] for i in items], [bool(i[2]) for i in items], cap)
        out.append("X " + ",".join(str(i) for i in d))
    return out


def cs_input(tr):
    rows = ["K"]
    for k, frames in tr.items():
        rows.append("A " + k)
        rows += ["F " + " ".join(num(x) for x in f) for f in frames]
    rows += ["M " + " ".join(str(x) for x in xs) for xs in M_VECTORS]
    rows += ["S " + " ".join(str(x) for x in xs) for xs in S_VECTORS]
    rows += ["Q " + " ".join(str(x) for x in xs) for xs in Q_VECTORS]
    rows += ["R %d %d" % v for v in R_VECTORS]
    rows += ["N %d %s %d %d" % v for v in N_VECTORS]
    rows += ["X " + " ".join("%d:%s:%d" % i for i in items) + " %d" % cap for items, cap in X_VECTORS]
    rows += ["U"]
    return "\n".join(rows) + "\n"


def scalar_checks():
    check(T.median([4, 1, 3, 2]) == 2.5 and T.median([]) is None, "median")
    check([T.sustained(x) for x in S_VECTORS] == ["unknown", "low", "low", "ok", "high", "ok", "ok"], "sustained")
    check(T.should_rotate(2_097_100, 100) and not T.should_rotate(0, 3_000_000), "rotation (never an empty segment)")
    check(T.plan_retention([100, 100, 100], [8, 1, 0.1], [False, False, True], 10_000) == [0], "retention: >7 days goes")
    check(T.plan_retention([100], [9], [True], 10) == [], "retention never deletes the current session")
    check(T.plan_retention([400, 400, 400, 400], [3, 2, 1, 0], [False, False, False, True], 1000) == [0, 1],
          "byte cap deletes oldest first")
    check(T.F(0.0005, 3) == "0.001" and T.F(-0.0, 2) == "0" and T.F(None, 2) == "null", "F rounding")


# ---- the reader (C2) --------------------------------------------------------------------------

def reader_checks():
    import zoneinfo
    tz = zoneinfo.ZoneInfo("America/Los_Angeles")
    # 2026-10-09 15:00 Pacific = 22:00Z
    t15 = 1791583200.0
    check(T.parse_when("2026-10-09 15:00", "America/Los_Angeles") == t15, "--at local time + --tz -> epoch: %r" %
          T.parse_when("2026-10-09 15:00", "America/Los_Angeles"))
    check(T.parse_when("2026-10-09T22:00:00Z", "America/Los_Angeles") == t15, "an explicit Z ignores --tz")
    _ = tz

    def iso(ep):
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ep))

    def sample(ep, seq, ratio=1.0, state="run", session="aaaa", dreal=5.0, speed="Normal", target=60):
        return {"kind": "sample", "utc": iso(ep), "session": session, "seq": seq, "state": state, "ratio": ratio,
                "tps": ratio * target, "tpsWall": ratio * target, "target": target, "dReal": dreal, "speed": speed,
                "simShare": 0.2, "fps": 60, "gapMaxMs": 20}

    with tempfile.TemporaryDirectory() as d:
        a = os.path.join(d, T.segment_name(t15 - 600, "aaaa", 10, 0))
        b = os.path.join(d, T.segment_name(t15 - 600, "aaaa", 10, 1))
        rows = [sample(t15 - 300 + 5 * i, i + 1, ratio=0.4 if i >= 40 else 1.0) for i in range(80)]
        with open(a, "w") as fh:
            fh.write(json.dumps({"kind": "session", "utc": iso(t15 - 600), "session": "aaaa", "seq": 0, "pid": 10}) + "\n")
            for r in rows[:50]:
                fh.write(json.dumps(r) + "\n")
        with open(b, "w") as fh:
            for r in rows[50:]:
                fh.write(json.dumps(r) + "\n")
            fh.write(json.dumps({"kind": "incident", "utc": iso(t15 + 30), "session": "aaaa", "seq": 81, "type": "stall",
                                 "gapS": 90.0, "phase": "tick:Normal"}) + "\n")
            fh.write(json.dumps(sample(t15 + 99999, 82)) + "\n")       # a future timestamp
            fh.write("not json\n")
            fh.write('{"kind":"sample","utc":"2026-10-09T22:00:00Z","session":"aaaa"')  # torn last line, no newline
        rec = T.read_record(d, now=t15 + 120)
        check(rec["future"] == 1 and rec["malformed"] == 2, "future + malformed rows counted, not used: %r" %
              {k: rec[k] for k in ("future", "malformed", "invalid")})
        check([r["seq"] for r in rec["rows"] if r.get("kind") == "sample"] == list(range(1, 81)),
              "rows ordered by session/seq across segments")
        tl = T.timeline(rec["rows"], t15 - 60, t15 + 60)
        check(len([r for r in tl["rows"] if r.get("kind") == "sample"]) == 26 and tl["incidents"] == 1,
              "--at 15:00 --span 2m bounds the timeline: %d rows, %d incidents" % (len(tl["rows"]), tl["incidents"]))
        check(tl["sustained"] == "low", "contiguous low run windows -> sustained low: %r" % tl["sustained"])
        out = T.render_timeline(tl, "America/Los_Angeles")
        check("15:00:00" in out and "stall" in out, "timeline prints local times and incidents")

        # concurrent rotation: a segment vanishes between listing and opening
        real_open = open
        victims = {a}

        def flaky_open(p, *aa, **kw):
            if p in victims:
                victims.discard(p)
                raise FileNotFoundError(p)
            return real_open(p, *aa, **kw)
        T._open = flaky_open
        try:
            rec2 = T.read_record(d, now=t15 + 120)
        finally:
            T._open = real_open
        check(rec2["vanished"] == 1 and len([r for r in rec2["rows"] if r.get("kind") == "sample"]) == 30,
              "a segment deleted mid-read is counted, the rest still read: %r" % rec2["vanished"])

    # the external observer (item 2): heartbeat age + process exit, seen from outside the game
    with tempfile.TemporaryDirectory() as d:
        def hb(name, sess, pid, silent, age):
            p = os.path.join(d, name)
            with open(p, "w") as fh:
                json.dump({"pid": pid, "session": sess, "utc": "x", "silentS": silent, "phase": "tl:Normal"}, fh)
            os.utime(p, (time.time() - age, time.time() - age))
        hb("hb_aaa.json", "aaa", 11, 42.0, 2)       # fresh heartbeat, main thread silent 42 s
        hb("hb_bbb.json", "bbb", 22, 0.0, 120)      # stale heartbeat, pid 22 still running
        hb("hb_ccc.json", "ccc", 33, 0.0, 600)      # stale, pid gone, no shutdown line
        hb("hb_ddd.json", "ddd", 44, 0.0, 600)      # stale, pid gone, shut down cleanly
        rows = [{"kind": "shutdown", "session": "ddd", "utc": "2026-10-09T22:00:00Z", "_t": 0}]
        f = {x["session"]: x for x in T.observe(rows, T.read_heartbeats(d), 22)}
        check(f.get("aaa", {}).get("finding") == "silent" and f["aaa"]["level"] == "WARN", "fresh hb + silence -> silent WARN: %r" % f.get("aaa"))
        check(f.get("bbb", {}).get("finding") == "frozen", "running pid with a dead heartbeat -> frozen: %r" % f.get("bbb"))
        check(f.get("ccc", {}).get("finding") == "exited-without-shutdown" and f["ccc"]["new"],
              "pid gone without shutdown -> exited-without-shutdown: %r" % f.get("ccc"))
        check("ddd" not in f, "a clean shutdown yields no finding")
        T.record_observation(f["ccc"], d)
        rec = T.read_record(d)
        again = {x["session"]: x for x in T.observe(rec["rows"], T.read_heartbeats(d), 22)}
        check(not again["ccc"]["new"] and any(r.get("kind") == "observer" for r in rec["rows"]),
              "an observer finding is written once and read back into the record")

    # MUST 3: placement uses the window's explicit boundaries, not the enqueue time
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, T.segment_name(t15 - 600, "cccc", 12, 0))
        late = dict(sample(t15, 5, ratio=0.2), mono=1000.0, monoStart=990.0, monoEnd=995.0)   # enqueued 5 s late
        inc = {"kind": "incident", "utc": iso(t15 + 200), "session": "cccc", "seq": 6, "type": "stall", "gapS": 300.0}
        with open(p, "w") as fh:
            fh.write(json.dumps(late) + "\n" + json.dumps(inc) + "\n")
        rec = T.read_record(d, now=t15 + 400)
        r0 = [r for r in rec["rows"] if r.get("kind") == "sample"]
        check(r0 and abs(r0[0]["_t"] - (t15 - 5)) < 0.01 and abs(r0[0].get("_t0", 0) - (t15 - 10)) < 0.01,
              "MUST 3: a window is placed at [utc-(mono-monoStart), utc-(mono-monoEnd)]: %r"
              % [(r.get("_t0"), r["_t"]) for r in r0])
        tl = T.timeline(rec["rows"], t15 + 20, t15 + 40)    # inside the 300 s stall, away from its endpoint
        check(tl["incidents"] == 1, "MUST 3/A30: an incident is selected by OVERLAP with its gap interval: %r" % tl["incidents"])

    # MUST 10: the observer reports main-thread progress and watchdog progress separately
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "hb_abc.json"), "w") as fh:
            json.dump({"pid": 5, "session": "abc", "utc": "2026-10-10T15:00:30.000Z", "silentS": 30.0,
                       "mainBeatUtc": "2026-10-10T15:00:00.000Z", "watchdogUtc": "2026-10-10T15:00:30.000Z"}, fh)
        os.utime(os.path.join(d, "hb_abc.json"), (time.time() - 600, time.time() - 600))
        f = T.observe([], T.read_heartbeats(d), [])
        check(f and f[0].get("lastMainProgressUtc") == "2026-10-10T15:00:00.000Z"
              and f[0].get("lastWatchdogUtc") == "2026-10-10T15:00:30.000Z",
              "MUST 10: observer separates last main-thread progress from the last watchdog write: %r" % f)

    # sustained needs CONTIGUOUS fresh windows
    gap_rows = [sample(t15 + 5 * i, i, ratio=0.3) for i in range(3)] + \
               [sample(t15 + 600 + 5 * i, 10 + i, ratio=0.3) for i in range(3)]
    check(T.sustained_from_rows(gap_rows) == "unknown", "6 low windows split by a 10-minute hole are not sustained")
    paused_mid = [sample(t15 + 5 * i, i, ratio=0.3, state="paused" if i == 3 else "run") for i in range(7)]
    check(T.sustained_from_rows(paused_mid) == "unknown", "a paused window breaks the streak")
    two_sess = [sample(t15 + 5 * i, i, ratio=0.3, session="s1" if i < 3 else "s2") for i in range(6)]
    check(T.sustained_from_rows(two_sess) == "unknown", "a new session breaks the streak")

    # MUST 7: continuity is the window boundaries, a game/menu/error/silence row or a dropped seq breaks it
    def mono_run(n, start_seq=1, t_start=t15, mono0=100.0, ratio=0.3, game=1, skip=None):
        out, m = [], mono0
        for i in range(n):
            if skip is not None and i == skip:
                m += 5.0                       # one whole window missing
                continue
            r = dict(sample(t_start + (m - mono0) + 5, start_seq + i, ratio=ratio), mono=m + 5, monoStart=m,
                     monoEnd=m + 5, game=game)
            out.append(r)
            m += 5.0
        return out
    check(T.sustained_from_rows(mono_run(7, skip=3)) == "unknown",
          "MUST 7: ONE missing window (10 s apart) breaks the streak: %r" % T.sustained_from_rows(mono_run(7, skip=3)))
    g1 = mono_run(3, start_seq=1, game=1)
    ev = [{"kind": "game", "utc": iso(t15 + 16), "session": "aaaa", "seq": 4, "game": 2}]
    g2 = mono_run(3, start_seq=5, t_start=t15 + 15, mono0=115.0, game=2)
    for r in ev:
        T.place(r)
    check(T.sustained_from_rows(g1 + ev + g2) == "unknown",
          "MUST 7: three low windows before a game replacement and three after are NOT one streak")
    er = [{"kind": "error", "utc": iso(t15 + 16), "session": "aaaa", "seq": 4}]
    T.place(er[0])
    g2b = mono_run(3, start_seq=5, t_start=t15 + 15, mono0=115.0, game=1)
    check(T.sustained_from_rows(g1 + er + g2b) == "unknown", "MUST 7: an error row breaks the streak")
    dropped = mono_run(3, start_seq=1) + mono_run(3, start_seq=6, t_start=t15 + 15, mono0=115.0)  # seq 4,5 lost
    check(T.sustained_from_rows(dropped) == "unknown", "MUST 7: a seq gap (dropped rows) breaks the streak")
    check(T.sustained_from_rows(mono_run(6)) == "low", "MUST 7: six abutting low windows ARE sustained low")

    # MUST 13: strict row validation - every bad row counted, none crashes or slips through
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, T.segment_name(t15 - 600, "dddd", 13, 0))
        good = sample(t15, 1)
        bad = ['{"kind":"sample","kind":"incident","utc":"%s","session":"dddd","seq":2,"state":"run"}' % iso(t15),
               json.dumps(dict(sample(t15, 3), ratio=float("nan")), allow_nan=True),
               json.dumps(dict(sample(t15, 4), ratio=True)),
               json.dumps(dict(sample(t15, 5), state="bogus")),
               json.dumps(dict(sample(t15, 6), dReal=-5)),
               json.dumps(dict(sample(t15, 7), session=["x"])),
               json.dumps({"kind": "zzz-unknown", "utc": iso(t15), "session": "dddd", "seq": 8}),
               json.dumps(dict(sample(t15, 9), seq="9"))]
        with open(p, "wb") as fh:
            fh.write((json.dumps(good) + "\n").encode())
            for b in bad:
                fh.write((b + "\n").encode())
            fh.write(b'{"kind":"sample","utc":"' + iso(t15).encode() + b'","session":"dd\xffdd","seq":10,"state":"run"}\n')
        try:
            rec = T.read_record(d, now=t15 + 60)
            n_bad = rec["malformed"] + rec["invalid"]
            check(len(rec["rows"]) == 1 and n_bad == len(bad) + 1,
                  "MUST 13: 1 good row kept, %d bad rows counted; got %d rows, %d malformed, %d invalid"
                  % (len(bad) + 1, len(rec["rows"]), rec["malformed"], rec["invalid"]))
        except Exception as e:                                   # noqa: BLE001
            check(False, "MUST 13: read_record crashed on a malformed row: %r" % e)
    # MUST 4: a replayed row (same session+seq) is read ONCE; a conflicting duplicate is counted
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, T.segment_name(t15 - 600, "ffff", 14, 0))
        rows4 = [sample(t15 + 5 * i, i + 1, ratio=0.3, session="ffff") for i in range(4)]
        with open(p, "w") as fh:
            for r in rows4 + rows4[:2]:                       # rows 1,2 replayed after a retry
                fh.write(json.dumps(r) + "\n")
            fh.write(json.dumps(dict(rows4[3], ratio=0.9)) + "\n")   # seq 4 again, different content
        rec = T.read_record(d, now=t15 + 60)
        seqs = [r["seq"] for r in rec["rows"] if r.get("kind") == "sample"]
        check(seqs == [1, 2, 3, 4] and rec.get("replayed") == 2 and rec.get("conflicts") == 1,
              "MUST 4: replay is idempotent at the reader (seqs %r, replayed %r, conflicts %r)"
              % (seqs, rec.get("replayed"), rec.get("conflicts")))

    # segment numbers >= 1000 are still segments, ordered numerically
    names = [T.segment_name(t15, "eeee", 1, n) for n in (999, 1000, 2)]
    with tempfile.TemporaryDirectory() as d:
        for n in names:
            open(os.path.join(d, n), "w").close()
        got = [os.path.basename(x) for x in T.list_files(d)]
        check(got == [names[2], names[0], names[1]], "MUST 13: segment 1000 is listed and sorted after 999: %r" % got)
    # heartbeat files that are not objects, or carry junk, never crash the observer
    with tempfile.TemporaryDirectory() as d:
        for n, body in (("hb_a.json", "[1,2]"), ("hb_b.json", '"x"'),
                        ("hb_c.json", json.dumps({"pid": 1, "session": "c", "silentS": "abc", "utc": "x"}))):
            with open(os.path.join(d, n), "w") as fh:
                fh.write(body)
        try:
            hbs = T.read_heartbeats(d)
            T.observe([], hbs, None)
            check(all(isinstance(h, dict) for h in hbs) and len(hbs) == 1,
                  "MUST 13: non-object heartbeats are skipped, junk fields tolerated: %r" % hbs)
        except Exception as e:                                   # noqa: BLE001
            check(False, "MUST 13: a malformed heartbeat crashed the observer: %r" % e)

    # MUST 8: two game processes are analysed SEPARATELY
    now8 = t15 + 5000
    b_fresh = [dict(sample(now8 - 5 * (12 - i), 100 + i, ratio=1.0, session="bbbb"), monoStart=50.0 + 5 * i,
                    monoEnd=55.0 + 5 * i, mono=55.0 + 5 * i, game=1) for i in range(12)]
    a_stale = [dict(sample(now8 - 200 - 5 * (8 - i), 10 + i, ratio=0.3, session="aaaa"), monoStart=900.0 + 5 * i,
                    monoEnd=905.0 + 5 * i, mono=905.0 + 5 * i, game=1) for i in range(8)]
    for r in b_fresh + a_stale:
        T.place(r)
    mixed_rows = b_fresh + a_stale       # session order: the reader groups by session start, B first
    sm = T.summarise(mixed_rows, now=now8)
    v = T.verdict(sm)
    check(v[0] == "OK" and sm.get("session", "").startswith("bbbb"),
          "MUST 8: a fresh healthy session is judged on its OWN windows, not the stale session listed after it: %r %r"
          % (v, sm.get("session")))
    check(len(sm.get("sessions") or []) == 2 and any(x["session"] == "aaaa" and x["coverage"] == "STALE"
                                                    for x in sm.get("sessions") or []),
          "MUST 8: every session in the window is summarised on its own: %r" % sm.get("sessions"))
    tl8 = T.timeline(sorted(mixed_rows, key=lambda r: r["_o"] if "_o" in r else 0), now8 - 300, now8)
    check(all(h["to"] >= h["from"] for h in tl8["holes"]),
          "MUST 8: overlapping sessions never produce backwards coverage holes: %r" % tl8["holes"])
    check([r["_t"] for r in tl8["rows"]] == sorted(r["_t"] for r in tl8["rows"]),
          "MUST 8: the merged timeline is chronological")

    # verdicts: coverage separate from performance
    now = t15 + 1000
    fresh_low = [sample(now - 5 * (8 - i), i, ratio=0.3) for i in range(8)]
    v = T.verdict(T.summarise(fresh_low, now=now))
    check(v[0] == "WARN" and "SUSTAINED LOW" in v[1], "fresh contiguous low -> WARN: %r" % (v,))
    stale_low = [sample(now - 3000 - 5 * (8 - i), i, ratio=0.3) for i in range(8)]
    v = T.verdict(T.summarise(stale_low, now=now))
    check(v[0] == "INFO" and "STALE" in v[1], "stale low record is a COVERAGE line, never a performance WARN: %r" % (v,))
    v = T.verdict(T.summarise([], now=now))
    check(v[0] == "UNKNOWN" and "MISSING" in v[1], "empty record -> MISSING coverage: %r" % (v,))
    v = T.verdict(T.summarise([sample(now - 10, 1)], now=now, writer={"werr": 3, "lastError": "IOException"}))
    check("ERROR" in v[1], "writer errors are reported as coverage ERROR: %r" % (v,))
    mixed = [sample(now - 5 * (8 - i), i, ratio=1.0, speed="Normal" if i % 2 else "Fast",
                    target=60 if i % 2 else 180) for i in range(8)]
    s = T.summarise(mixed, now=now)
    check(set(s["byTarget"]) == {"60", "180"}, "TPS reported per target, never one mixed median: %r" % s["byTarget"])


# names of C# unit tests (Units*.cs, T_<name>) that MUST exist and pass: a test that silently disappears
# from the harness is a failure, not a pass.
CS_UNITS = ["IncidentRowComposition", "StagesSkipSafe", "StagesWorstTick", "StagesInvalidNesting", "LifecycleScopes", "SustainedStale", "SettingsStrict", "WriterReplayAfterPartialBatch", "WriterTornTail", "WriterBoundCountsInFlight", "HeartbeatSeparatesMainAndWatchdog"]


def unit_checks(lines):
    """The C# unit group: every `U name ok`, and the production-composed `J name <json>` lines, which must
    parse STRICTLY (no duplicate keys, no NaN/Infinity) - the way the reader parses the record."""
    units = {}
    for ln in lines:
        if ln.startswith("U-count "):
            continue
        if ln.startswith("U "):
            parts = ln.split(" ", 3)
            units[parts[1]] = parts[2] if len(parts) > 2 else "?"
            if len(parts) > 2 and parts[2] != "ok":
                FAILS.append("C# unit %s: %s" % (parts[1], ln[len("U " + parts[1]) + 1:][:400]))
    for name in CS_UNITS:
        if name not in units:
            FAILS.append("C# unit %s did not run" % name)
    js = [ln.split(" ", 2) for ln in lines if ln.startswith("J ")]
    JLINES.clear()
    for _, name, body in js:
        try:
            JLINES.setdefault(name, []).append(T.loads_strict(body))
        except ValueError as e:
            FAILS.append("C# composed line %s does not parse strictly: %s :: %s" % (name, e, body[:300]))
    for name, fn in J_CHECKS:
        fn(JLINES.get(name, []))
    print("C# units: %d run, %d failed" % (len(units), sum(1 for v in units.values() if v != "ok")))


JLINES = {}


def _j_incident(rows):
    check(len(rows) == 1, "MUST 1: one production-composed incident row: %r" % rows)
    for r in rows:
        check(r.get("kind") == "incident" and r.get("type") == "stall",
              "MUST 1: a recovered incident stays kind=incident (type=stall): %r" % r)
        check(r.get("multAfter") == 6 and r.get("mult") == 1,
              "MUST 1: multiplier after the gap (multAfter 6) and the cached one before it (mult 1) are distinct: %r"
              % {k: r.get(k) for k in ("mult", "multAfter")})


def _j_silence(rows):
    check(len(rows) == 1 and rows[0].get("kind") == "silence", "MUST 1: silence row composes: %r" % rows)


def _j_worst(rows):
    w = (rows[0].get("worst") or [{}])[0] if rows else {}
    check(rows and w.get("tg") == 777 and w.get("ms") == 50 and rows[0]["attr"]["tick"][1] == 50,
          "SHOULD 1: the worst tick names its own tick id and the SAME duration as the tick total: %r" % rows)
    st = w.get("stages") if isinstance(w, dict) else None
    check(isinstance(st, dict) and st.get("tl:Normal") == 40 and st.get("tickOther") == 10,
          "SHOULD 1: the worst tick keeps its numeric per-stage breakdown (ms), not only a `top` string: %r" % w)
    check(rows and rows[0].get("attrValid") is True, "valid nesting reads attrValid true: %r" % rows)


def _j_invalid(rows):
    check(rows and rows[0].get("attrValid") is False and isinstance(rows[0].get("attrOverMs"), (int, float))
          and rows[0]["attrOverMs"] > 0,
          "MUST 2/A12: children exceeding their parent flag attrValid false with the excess (never a silent clamp): %r"
          % rows)


def _j_heartbeat(rows):
    from datetime import datetime as _dt
    h = rows[0] if rows else {}

    def ep(x):
        try:
            return _dt.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
        except (TypeError, ValueError):
            return None
    m, w = ep(h.get("mainBeatUtc")), ep(h.get("watchdogUtc"))
    check(m is not None and w is not None and 29 <= w - m <= 31,
          "MUST 10: the heartbeat carries the main thread's last progress (mainBeatUtc) ~30 s before the watchdog's "
          "write (watchdogUtc): %r" % {k: h.get(k) for k in ("utc", "mainBeatUtc", "watchdogUtc")})
    check(isinstance(h.get("hbSeq"), int) and isinstance(h.get("mainBeatMono"), (int, float))
          and isinstance(h.get("watchdogMono"), (int, float)) and h.get("ticksGame") == 4242
          and "hbErrors" in h and "procStartUtc" in h,
          "MUST 10: hbSeq, mainBeatMono, watchdogMono, ticksGame, hbErrors, procStartUtc present: %r" % sorted(h))


J_CHECKS = [("heartbeat", _j_heartbeat), ("incident", _j_incident), ("silence", _j_silence), ("stages-worst", _j_worst),
            ("stages-invalid", _j_invalid)]   # assertions on production-composed lines


def cs_parity(tr, res):
    import winbuild
    proj = os.path.join(REPO, "src", "RimMandrake", "bridgetools", "TpsMathSelfTest")
    rc, rec = winbuild.stage_build(os.path.join(proj, "TpsMathSelfTest.csproj"), stage_name="TpsMathSelfTest")
    if rc:
        FAILS.append("C# parity harness build FAILED (rc %s)" % rc)
        return
    dll = winbuild.staged_win(rec, proj) + "\\bin\\Release\\net8.0\\TpsMathSelfTest.dll"
    p = subprocess.run([winbuild.dotnet_exe(), dll], input=cs_input(tr), capture_output=True, text=True,
                       cwd="/mnt/d/Luke/dev")
    allout = [ln.strip() for ln in p.stdout.splitlines() if ln.strip()]
    got = [ln for ln in allout if not ln.startswith(("U ", "J ", "U-count "))]
    want = [ln.strip() for ln in py_lines(tr, res)]
    unit_checks(allout)
    if p.returncode != 0:
        FAILS.append("C# harness exit %d: %s" % (p.returncode, p.stderr[-400:]))
    if len(got) != len(want):
        FAILS.append("C# answered %d lines, Python %d" % (len(got), len(want)))
    bad = [(i, g, w) for i, (g, w) in enumerate(zip(got, want)) if g != w]
    for i, g, w in bad[:5]:
        FAILS.append("C#/Python disagree on line %d:\n   C# %s\n   py %s" % (i, g, w))
    print("C# parity: %d/%d lines identical" % (len(want) - len(bad) if len(got) == len(want) else 0, len(want)))


def main(argv):
    tr = traces()
    res = trace_checks(tr)
    scalar_checks()
    reader_checks()
    print("python checks: %s" % ("PASS" if not FAILS else "FAIL"))
    if "--no-cs" in argv:
        print("C# parity: SKIPPED by --no-cs")
    elif not any(os.path.exists(c) for c in ["/mnt/c/Users/Mandrake/.dotnet/dotnet.exe",
                                               "/mnt/c/Program Files/dotnet/dotnet.exe"]):
        FAILS.append("C# parity UNMEASURED: no dotnet.exe on this machine (pass --no-cs to accept Python-only)")
    else:
        cs_parity(tr, res)
    for f in FAILS:
        print("FAIL " + f)
    print("selftest_tps_record: %s (%d failures)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
