#!/usr/bin/env python3
"""Offline selftest of the proof cost ledger and its throughput report (PROOF_COST_MEASURE_BEFORE_THE_ESTIMATES).

Synthetic runs only, no game, no bridge, no store: the split's arithmetic, the report's arithmetic (rows/hour, verdict
counts, staging p50/p95, tokens per measured row, proof-busy share, the window's edges), a 0-run window reading
UNMEASURED and never 0, and the three writers: relentless_live.run (a PASS run under a fake clock, a NOT_ADMITTED one,
the broker's source and queue wait), relentless_game.steve_cost (one row per job and clause, never twice) and an
unwritable ledger costing the run nothing.
"""
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import proof_cost as P          # noqa: E402
import relentless_live as L     # noqa: E402
import relentless_game as G     # noqa: E402
import selftest_relentless_live as TL   # noqa: E402  its FakeFx / ScriptFx

FAILS = []
T0 = 1_800_000_000.0            # 2027-01-15T08:00:00Z


def check(name, cond, detail=""):
    if not cond:
        FAILS.append((name, detail))


def row(end_off, verdict, staging=None, proving=None, held=None, tokens=None, source="round"):
    """A synthetic cost row ending T0 + end_off seconds."""
    return {"at": P.iso(T0 + end_off - 60), "ended": P.iso(T0 + end_off), "source": source, "item": "X", "clause": "A1",
            "verdict": verdict, "outcome": verdict, "staging_s": staging, "proving_s": proving, "held_s": held,
            "idle_s": None if held is None else held - (staging or 0) - (proving or 0), "tokens": tokens}


def t_split():
    s = P.split({"start": 100.0, "queued": 40.0, "taken": 160.0, "proof_start": 200.0, "proof_s": 90.0,
                 "released": 300.0, "ended": 301.0})
    check("split: queue from the broker entry", s["queue_s"] == 120.0, s)
    check("split: staging taken -> proof start", s["staging_s"] == 40.0, s)
    check("split: proving the proof's own wall time", s["proving_s"] == 90.0, s)
    check("split: held taken -> released, idle the rest", s["held_s"] == 140.0 and s["idle_s"] == 10.0, s)
    s = P.split({"start": 100.0, "queued": 140.0, "taken": 160.0, "released": 170.0, "ended": 171.0})
    check("split: a queue entry after the start is not the origin", s["queue_s"] == 60.0, s)
    check("split: held with no proof is all staging (health/site), proving None", s["staging_s"] == 10.0
          and s["proving_s"] is None and s["idle_s"] == 0.0, s)
    s = P.split({"start": 100.0, "ended": 130.0})
    check("split: never took the bridge -> held 0.0 (measured), the rest None", s["held_s"] == 0.0
          and s["queue_s"] == 30.0 and s["staging_s"] is None and s["proving_s"] is None, s)
    s = P.split({"start": 100.0, "ended": 130.0, "held_unknown": True})
    check("split: testq held is unknown, not 0", s["held_s"] is None, s)
    try:
        P.make_row("bogus", "X", "A1", "s", None, "PASS", {"start": 1.0})
        check("make_row refuses an unknown source", False)
    except ValueError:
        pass
    r = P.make_row("round", "X", "A1", "s", None, "REFUSED", {"start": T0, "ended": T0 + 5})
    check("REFUSED reads UNMEASURED, outcome kept", r["verdict"] == "UNMEASURED" and r["outcome"] == "REFUSED", r)


def t_report_arithmetic():
    rows = [row(600, "PASS", staging=60, proving=120, held=200, tokens=1000),
            row(1200, "FAIL", staging=120, proving=60, held=200),
            row(1800, "UNMEASURED", staging=180, held=200, tokens=500),
            row(2400, "PASS", staging=240, proving=30, held=300, source="broker"),
            row(3000, "UNMEASURED", held=0.0),                          # NOT_ADMITTED: held nothing
            row(7300, "PASS", staging=1, proving=1, held=2),            # outside [T0, T0 + 2 h)
            row(-10, "FAIL", staging=1, proving=1, held=2)]             # before the window
    rep = P.throughput(rows, T0, T0 + 7200, {"utilization": 0.0654, "held_min": 120.0})
    check("report: rows in the window by end stamp", rep["rows"] == 5, rep)
    check("report: verdict counts", rep["by_verdict"] == {"PASS": 2, "FAIL": 1, "UNMEASURED": 2}, rep["by_verdict"])
    check("report: measured rows/hour = (PASS+FAIL) / hours", rep["measured"] == 3 and rep["rows_per_hour"] == 1.5, rep)
    check("report: by source", rep["by_source"] == {"broker": 1, "round": 4}, rep["by_source"])
    check("report: held minutes summed", rep["held_min"] == round(900 / 60.0, 2), rep["held_min"])
    # busy = (60+120) + (120+60) + (180+0) + (240+30) = 810 over held 900 (the 0-held row adds nothing)
    check("report: proof-busy share of our holds", rep["proof_busy_share"] == 0.9, rep["proof_busy_share"])
    # staging minutes 1, 2, 3, 4: nearest-rank p50 = 2, p95 = 4
    check("report: staging p50 / p95 nearest rank", rep["staging_min_p50"] == 2.0 and rep["staging_min_p95"] == 4.0, rep)
    check("report: tokens over carrying rows / measured rows", rep["tokens_per_measured_row"] == 500.0
          and rep["tokens_rows"] == 2, rep)
    check("report: the bridge-driven share is bridge_utilization's", rep["bridge_driven_share"] == 0.0654, rep)
    check("pct: nearest rank on 20 values", P.pct(list(range(1, 21)), 95) == 19 and P.pct([7], 50) == 7)


def t_empty_window_is_unmeasured():
    rep = P.throughput([row(-10, "PASS", staging=1, proving=1, held=2)], T0, T0 + 3600, None)
    for k in ("rows_per_hour", "held_min", "proof_busy_share", "staging_min_p50", "staging_min_p95",
              "tokens_per_measured_row", "bridge_driven_share"):
        check("0-run window: %s reads UNMEASURED, not 0" % k, rep[k] == P.UNMEASURED, rep[k])
    check("0-run window: zero rows", rep["rows"] == 0 and rep["measured"] == 0, rep)
    check("0-run window: the line says UNMEASURED", "UNMEASURED measured rows/h" in P.line(rep), P.line(rep))
    rep = P.throughput([row(60, "UNMEASURED", held=0.0)], T0, T0 + 3600, {"unread": "no ledger"})
    check("rows but none measured: 0.0 rows/h (a rate it did measure)", rep["rows_per_hour"] == 0.0, rep)
    check("rows but none measured: tokens per measured row UNMEASURED", rep["tokens_per_measured_row"] == P.UNMEASURED)
    check("an unread bridge share is UNMEASURED with its why", rep["bridge_driven_share"] == P.UNMEASURED
          and rep.get("bridge_driven_unread") == "no ledger", rep)
    try:
        P.throughput([], T0, T0)
        check("a window that ends where it starts is refused", False)
    except ValueError:
        pass


def t_reading_window_starts_at_the_ledger():
    root = tempfile.mkdtemp(prefix="pc_read_")
    for k in range(3):      # the ledger began 2 h ago: 3 PASS rows, so 1.5/h over its 2 h, not 3/24 over a day
        P.append(root, row(k * 1800 + 60, "PASS", staging=1, proving=1, held=2) | {"at": P.iso(T0 + k * 1800)})
    ln = P.reading_line(root, T0 + 7200, hours=24.0, repo="/nonexistent")
    # first end T0+60 -> window 7140 s, 3 rows: 3 / 1.9833 h = 1.51/h
    check("reading: the window starts at the ledger's first row's end", "1.51 measured rows/h" in ln
          and "01-15T08:01.." in ln, ln)
    young = tempfile.mkdtemp(prefix="pc_read_")
    P.append(young, row(60, "PASS", staging=1, proving=1, held=2))
    P.append(young, row(120, "PASS", staging=1, proving=1, held=2))
    ln = P.reading_line(young, T0 + 600, hours=24.0, repo="/nonexistent")
    check("reading: a ledger under an hour old has no hourly rate", "UNMEASURED measured rows/h (2 rows" in ln, ln)
    check("reading: an unreadable bridge share is UNMEASURED in the line", "bridge driven UNMEASURED" in ln, ln)
    ln = P.reading_line(tempfile.mkdtemp(prefix="pc_read_"), T0, hours=24.0, repo="/nonexistent")
    check("reading: an empty ledger reads UNMEASURED over the full window", "UNMEASURED measured rows/h" in ln
          and "01-14T08:00.." in ln, ln)


def t_legacy_runs():
    runs = [{"at": P.iso(T0 + 10), "outcome": "PASS", "item": "X", "criterion": "A1"},
            {"at": P.iso(T0 + 20), "outcome": "NOT_ADMITTED"},
            {"at": P.iso(T0 + 30), "outcome": "FAIL", "source": "testq"},
            {"item": "X", "sha": "s", "void": True, "at": P.iso(T0 + 40)}]
    rows = P.from_runs(runs)
    rep = P.throughput(rows, T0, T0 + 1800, None)
    check("legacy: a void row is not a run", rep["rows"] == 3, rep)
    check("legacy: 2 measured in half an hour = 4/h", rep["rows_per_hour"] == 4.0, rep)
    check("legacy: no split, so staging UNMEASURED", rep["staging_min_p50"] == P.UNMEASURED, rep)


class Clock(object):
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t


class TimedFx(TL.ScriptFx):
    """Each health check costs 20 s, each proof 30 s, the take 5 s, the release 3 s, on a fake clock."""
    def __init__(self, clock, codes, **kw):
        TL.ScriptFx.__init__(self, codes, **kw)
        self.clock = clock

    def health(self, files, sha, timeout):
        self.clock.t += 20
        return TL.ScriptFx.health(self, files, sha, timeout)

    def run_proof(self, proof, log, timeout):
        self.clock.t += 30
        return TL.ScriptFx.run_proof(self, proof, log, timeout)

    def rimflow(self, *args, timeout=120):
        if args[:2] == ("bridge", "take"):
            self.clock.t += 5
        elif args[:2] == ("bridge", "release"):
            self.clock.t += 3
        return TL.ScriptFx.rimflow(self, *args, timeout=timeout)


def _ledger(root):
    return P.read(os.path.join(root, P.LEDGER))


def t_live_run_writes_its_row():
    real = time.time
    clock = Clock(T0)
    time.time = clock
    old = os.environ.pop("RELENTLESS_PROOF_SOURCE", None)
    try:
        root = tempfile.mkdtemp(prefix="pc_live_")
        fx = TimedFx(clock, {"python3 ": (0, "PASS")})
        r = L.run(fx, root, "ROT_X", "A2", "python3 probe.py", "--compose biomes", {}, now=T0)
        rows = _ledger(root)
        check("live run: one cost row per run", len(rows) == 1, rows)
        c = rows[0] if rows else {}
        check("live run: source round, its item/clause/sha/verdict", c.get("source") == "round"
              and c.get("item") == "ROT_X" and c.get("clause") == "A2" and c.get("sha") == TL.SHA
              and c.get("verdict") == "PASS" and r["outcome"] == "PASS", c)
        check("live run: queue = start -> taken (the 5 s take)", c.get("queue_s") == 5.0, c)
        check("live run: staging = the 20 s health check", c.get("staging_s") == 20.0, c)
        check("live run: proving = the 30 s proof", c.get("proving_s") == 30.0, c)
        check("live run: held = 20 + 30 + the 3 s release, idle 3", c.get("held_s") == 53.0 and c.get("idle_s") == 3.0, c)
        check("live run: tokens unattributed (None), never a made-up 0", c.get("tokens") is None, c)
        # NOT_ADMITTED: the running load cannot serve it, no bridge
        root = tempfile.mkdtemp(prefix="pc_live_")
        fx = TimedFx(clock, {"python3 ": (0, "PASS")}, gap="the running load lacks TheRot")
        r = L.run(fx, root, "ROT_X", "A2", "python3 probe.py", "--compose biomes", {}, now=clock.t)
        c = (_ledger(root) or [{}])[0]
        check("NOT_ADMITTED: a row, held 0.0, UNMEASURED", r["outcome"] == L.NOT_ADMITTED and c.get("held_s") == 0.0
              and c.get("verdict") == "UNMEASURED" and c.get("outcome") == L.NOT_ADMITTED, c)
        # the broker's round: source broker, queue from queued_at
        root = tempfile.mkdtemp(prefix="pc_live_")
        os.makedirs(os.path.join(root, "store", "broker"))
        with open(os.path.join(root, "store", "broker", "queue.json"), "w") as f:
            json.dump({"items": {"ROT_X": {"queued_at": clock.t - 600, "state": "running"}}}, f)
        os.environ["RELENTLESS_PROOF_SOURCE"] = "broker"
        fx = TimedFx(clock, {"python3 ": (1, "FAIL: the comp is missing")})
        L.run(fx, root, "ROT_X", "A2", "python3 probe.py", "--compose biomes", {}, now=clock.t)
        c = (_ledger(root) or [{}])[0]
        check("broker: source broker, queue from the entry (600 + the 5 s take)", c.get("source") == "broker"
              and c.get("queue_s") == 605.0, c)
        end1 = P.epoch(c.get("ended"))
        clock.t += 100      # the round's second clause of the same item starts 100 s after the first ended
        L.run(fx, root, "ROT_X", "A2", "python3 probe.py", "--compose biomes", {}, now=clock.t)
        c2 = (_ledger(root) or [{}, {}])[1]
        check("broker: a second clause waits from the first's end (100 s + the 5 s take), not the queue entry",
              end1 is not None and c2.get("queue_s") == 105.0, (c2, end1))
        os.environ.pop("RELENTLESS_PROOF_SOURCE", None)
        # a proof that raised still spent its time proving
        root = tempfile.mkdtemp(prefix="pc_live_")

        class Raises(TimedFx):
            def run_proof(self, proof, log, timeout):
                self.clock.t += 30
                raise OSError("proof would not start")
        L.run(Raises(clock, {}), root, "ROT_X", "A2", "python3 probe.py", "--compose biomes", {}, now=clock.t)
        c = (_ledger(root) or [{}])[0]
        check("a raising proof: proving 30 s, UNMEASURED", c.get("proving_s") == 30.0 and c.get("verdict") == "UNMEASURED", c)
        # an unwritable ledger: the run keeps its verdict and says so
        root = tempfile.mkdtemp(prefix="pc_live_")
        os.makedirs(os.path.join(root, "live"))
        os.makedirs(os.path.join(root, P.LEDGER))       # a directory where the file must go
        fx = TimedFx(clock, {"python3 ": (0, "PASS")})
        r = L.run(fx, root, "ROT_X", "A2", "python3 probe.py", "--compose biomes", {}, now=clock.t)
        with open(os.path.join(root, "live", "runs.jsonl")) as f:
            rr = [json.loads(x) for x in f]
        check("unwritable ledger: PASS stands, runs.jsonl names it", r["outcome"] == "PASS" and rr
              and "cost_unwritten" in rr[0], rr)
    finally:
        time.time = real
        os.environ.pop("RELENTLESS_PROOF_SOURCE", None)
        if old is not None:
            os.environ["RELENTLESS_PROOF_SOURCE"] = old


def t_steve_cost():
    root = tempfile.mkdtemp(prefix="pc_steve_")
    jb = {"submitted": T0, "job": "q1"}
    rec = {"job": {"id": "q1"}}
    judged = {"A1": {"outcome": "PASS"}}
    dud = {"A2": "the load was not the tier"}
    G.steve_cost(root, jb, rec, "X", "s", "ratchet_pilot", judged, dud, T0 + 900)
    G.steve_cost(root, jb, rec, "X", "s", "ratchet_pilot", judged, dud, T0 + 1200)     # the same job read again
    rows = _ledger(root)
    check("testq: one row per (job, clause), never twice", sorted(r["clause"] for r in rows) == ["A1", "A2"], rows)
    a1 = next((r for r in rows if r["clause"] == "A1"), {})
    a2 = next((r for r in rows if r["clause"] == "A2"), {})
    check("testq: source, tier, verdicts", a1.get("source") == "testq" and a1.get("tier") == "ratchet_pilot"
          and a1.get("verdict") == "PASS" and a2.get("verdict") == "UNMEASURED", rows)
    check("testq: queue = submitted -> read, held unknown", a1.get("queue_s") == 900.0 and a1.get("held_s") is None, a1)


def main():
    for t in (t_split, t_report_arithmetic, t_empty_window_is_unmeasured, t_reading_window_starts_at_the_ledger, t_legacy_runs, t_live_run_writes_its_row,
              t_steve_cost):
        try:
            t()
        except Exception as e:     # noqa: BLE001  a crash is a red, named
            FAILS.append((t.__name__, "crashed: %s: %s" % (type(e).__name__, e)))
    if FAILS:
        print(json.dumps(FAILS, default=str)[:3000])
    print("selftest_proof_cost:", "FAIL" if FAILS else "OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
