#!/usr/bin/env python3
"""Selftest for memwatch.py against a FAKE cgroup tree (no real cgroup, no toast).

Planted breaks it must catch: an oom_kill increment in a seat's tool cgroup, a shmem
crossing, a first-run baseline that must stay silent, a new seat scope compared against
zero, edge-triggering (no repeat while over, re-arm after dropping), and harness-slice
events recorded but never toastable.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import memwatch  # noqa: E402

GB = 1024 ** 3
FAILS = []


def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def make_cg(d: Path, oom_kill=0, mx=0, shmem=0, anon=1000):
    d.mkdir(parents=True, exist_ok=True)
    (d / "memory.events").write_text(f"low 0\nhigh 0\nmax {mx}\noom {oom_kill}\noom_kill {oom_kill}\noom_group_kill 0\n")
    (d / "memory.current").write_text(f"{anon + shmem}\n")
    (d / "memory.peak").write_text(f"{anon + shmem}\n")
    (d / "memory.max").write_text("max\n")
    (d / "memory.swap.current").write_text("0\n")
    (d / "memory.stat").write_text(f"anon {anon}\nfile {shmem}\nshmem {shmem}\nfile_dirty 0\nfile_writeback 0\n")
    (d / "memory.pressure").write_text("some avg10=1.50 avg60=0 avg300=0 total=0\nfull avg10=0.00 avg60=0 avg300=0 total=0\n")


def host_tests():
    """Windows host sampling with a mocked powershell call."""
    GBk = 1024 ** 3
    good = json.dumps({"committed": 40 * GBk, "limit": 100 * GBk, "avail_mb": 20000, "total_kb": 64 * 1024 * 1024,
                       "free_kb": 20 * 1024 * 1024, "rw_ws": 10 * GBk, "rw_private": 12 * GBk,
                       "rw_peak_ws": 11 * GBk, "vmmem_ws": 8 * GBk})
    h = memwatch.host_sample(lambda ps: "\r" + good + "\r")
    ok(h.get("committed") == 40 * GBk and h["rw_peak_ws"] == 11 * GBk, "host sample parses (CR stripped by runner contract)")
    bad = memwatch.host_sample(lambda ps: None)
    ok("unmeasured" in bad and "committed" not in bad, "failed powershell -> UNMEASURED marker, no zeros")
    ok("unmeasured" in memwatch.host_sample(lambda ps: "garbage"), "non-JSON output -> UNMEASURED")
    ok("unmeasured" in memwatch.host_sample(lambda ps: "{}"), "JSON without counters -> UNMEASURED")
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        seats = t / "claude-seats.slice"
        make_cg(seats)
        state = t / "state"
        calls = []
        def fn(ps):
            calls.append(1)
            return good
        memwatch.check([seats], [], state, 2.0, False, now=1000.0, host_fn=fn)
        ok(len(calls) == 1, "first run samples host")
        memwatch.check([seats], [], state, 2.0, False, now=1060.0, host_fn=fn)
        ok(len(calls) == 2, "RimWorld running -> sampled again after 60 s")
        st = json.loads((state / "state.json").read_text())["host"]
        ok(st["peak_committed"] == 40 * GBk and st["peak_rw_ws"] == 11 * GBk and st["min_headroom"] == 60 * GBk, "peaks and headroom in state.json")
        lines = (state / "samples.jsonl").read_text().splitlines()
        ok(all("host" in json.loads(x) for x in lines), "host block in each sample line")
        down = json.dumps({**json.loads(good), "rw_ws": None, "rw_private": None, "rw_peak_ws": None, "committed": 30 * GBk})
        memwatch.check([seats], [], state, 2.0, False, now=1120.0, host_fn=lambda ps: down)
        st = json.loads((state / "state.json").read_text())["host"]
        ok(st["rw_running"] is False and st["peak_committed"] == 40 * GBk, "RimWorld stopped: peak kept, running False")
        memwatch.check([seats], [], state, 2.0, False, now=1180.0, host_fn=fn)
        ok(len(calls) == 2, "RimWorld not running -> no sample after 60 s")
        memwatch.check([seats], [], state, 2.0, False, now=1500.0, host_fn=lambda ps: None)
        st = json.loads((state / "state.json").read_text())["host"]
        ok(st["peak_committed"] == 40 * GBk and st["latest"]["committed"] == 30 * GBk, "failed sample leaves peaks and latest untouched")
        summ = memwatch.host_summary({"host": st})
        ok("headroom" in summ and "PEAKS" in summ, "host summary has headroom and peaks")
        ok(memwatch.main(["host", "--state-dir", str(state)]) == 0, "host subcommand runs")


def main():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        seats = t / "claude-seats.slice"
        harness = t / "rm-harness.slice"
        tmpfs = t / "fake_tmp"
        (tmpfs / "sub").mkdir(parents=True)
        (tmpfs / "sub" / "big.bin").write_bytes(b"x" * 300_000)
        (tmpfs / "small.txt").write_bytes(b"x" * 10)
        state = t / "state"
        scope = seats / "claude-seat-BENCH-111.scope"
        make_cg(seats, oom_kill=24)
        make_cg(scope, oom_kill=5)
        make_cg(scope / "claude-code-bash", oom_kill=5)
        make_cg(scope / "seat")
        make_cg(harness, oom_kill=3)
        roots, mounts = [seats, harness], [str(tmpfs)]

        ev = memwatch.check(roots, mounts, state, 2.0, False)
        ok(ev == [], "first run baselines silently despite historical counts")
        ok((state / "state.json").exists() and (state / "samples.jsonl").exists(), "state and sample written")

        ev = memwatch.check(roots, mounts, state, 2.0, False)
        ok(ev == [], "no change -> no events")

        make_cg(scope / "claude-code-bash", oom_kill=6, mx=10)
        make_cg(scope, oom_kill=6, mx=10)
        make_cg(seats, oom_kill=25, mx=10)
        ev = memwatch.check(roots, mounts, state, 2.0, False)
        kills = [e for e in ev if e["kind"] == "oom_kill"]
        ok(len(kills) == 3 and all(e["delta"] == 1 and e["toast"] for e in kills),
           f"oom_kill +1 seen on tool cgroup, scope and slice, all toastable ({len(kills)})")
        ok(any(e["cgroup"].endswith("/claude-code-bash") and e["seat"] == "BENCH" for e in kills),
           "tool cgroup event names seat BENCH")
        maxes = [e for e in ev if e["kind"] == "max"]
        ok(maxes and not any(e["toast"] for e in maxes), "max increments recorded, not toasted")
        top = kills[0].get("top_tmpfs") or []
        ok(top and top[0]["path"].endswith("sub/big.bin"), f"largest tmpfs file named first ({top[:1]})")

        make_cg(scope, oom_kill=6, mx=10, shmem=3 * GB)
        ev = memwatch.check(roots, mounts, state, 2.0, False)
        sh = [e for e in ev if e["kind"] == "shmem"]
        ok(len(sh) == 1 and sh[0]["shmem_gb"] == 3.0 and sh[0]["toast"], "shmem crossing 2 GB alerts once")
        ev = memwatch.check(roots, mounts, state, 2.0, False)
        ok(not [e for e in ev if e["kind"] == "shmem"], "shmem still over -> no repeat (edge-triggered)")
        make_cg(scope, oom_kill=6, mx=10, shmem=0)
        memwatch.check(roots, mounts, state, 2.0, False)
        make_cg(scope, oom_kill=6, mx=10, shmem=3 * GB)
        ev = memwatch.check(roots, mounts, state, 2.0, False)
        ok(len([e for e in ev if e["kind"] == "shmem"]) == 1, "re-armed after dropping below")

        new = seats / "claude-seat-FOUNDRY-222.scope"
        make_cg(new, oom_kill=1)
        ev = memwatch.check(roots, mounts, state, 2.0, False)
        ok(any(e["cgroup"].endswith("FOUNDRY-222.scope") and e["kind"] == "oom_kill" for e in ev),
           "new seat scope compared against zero")

        make_cg(harness, oom_kill=4)
        ev = memwatch.check(roots, mounts, state, 2.0, False)
        h = [e for e in ev if e["cgroup"] == "rm-harness.slice"]
        ok(h and not any(e["toast"] for e in h), "harness oom_kill recorded, never toasted")

        lines = (state / "events.jsonl").read_text().splitlines()
        ok(all(json.loads(x)["ts"] for x in lines), f"events.jsonl parses ({len(lines)} lines)")

        ok(memwatch.main(["--root", str(seats), "--tmpfs", str(tmpfs), "--state-dir", str(state), "--no-toast"]) == 0,
           "CLI runs")
    host_tests()
    print(f"{'FAIL' if FAILS else 'PASS'} selftest_memwatch: {len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
