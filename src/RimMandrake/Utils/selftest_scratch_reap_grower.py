#!/usr/bin/env python3
"""selftest_scratch_reap_grower.py -- the pressure tick names what fills the root disk while it fills
(ROOT_DISK_FIX_NIGHT_GROWTH_OUTRUNS_REAPER).

The instance: 2026-11-04 10:40-12:52Z root free fell 578 -> 140 GB at ~3.3 GB/min with the pool and scratch flat,
then recovered in one step; nothing named the grower and its evidence went with it. Cases, on a fake /proc:
  A. a fast fall names the process whose write_bytes grew (GB, unit, cwd, command), lists the big file it holds open
     (deleted included), and writes a GROWER line to alarms.log;
  B. a pid reused by a new process is counted from its own start, never as a negative or a lifetime;
  C. a slow fall above the line captures nothing and names nobody;
  D. under the pressure line with no fall it captures, saying why;
  E. the first tick (no previous sample) ranks nobody;
  F. the real /proc is readable: this very process is in the sample (the instrument can see);
  G. pressure_check writes the growth row even when it has nothing else to do, and a grower that raises still lets
     the pressure check finish, leaving an error row.
"""
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent / "rimflow")]
import disk_grower as G  # noqa: E402

FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def fake_pid(proc: Path, pid: int, start: int, wbytes: int, unit: str, cwd: Path, cmd: str, fds=()):
    d = proc / str(pid)
    (d / "fd").mkdir(parents=True, exist_ok=True)
    (d / "stat").write_text(f"{pid} (py thon) S 1 {pid} {pid} 0 -1 4194304 1 0 0 0 0 0 0 0 20 0 1 0 {start} 0 0\n")
    (d / "io").write_text(f"rchar: 1\nwchar: {wbytes}\nsyscr: 1\nsyscw: 1\nread_bytes: 0\nwrite_bytes: {wbytes}\n"
                          "cancelled_write_bytes: 0\n")
    (d / "cgroup").write_text(f"0::/user.slice/user@1000.service/app.slice/{unit}\n")
    (d / "cmdline").write_text(cmd.replace(" ", "\0") + "\0")
    if (d / "cwd").is_symlink():
        (d / "cwd").unlink()
    (d / "cwd").symlink_to(cwd)
    for i, target in enumerate(fds):
        link = d / "fd" / str(3 + i)
        if link.is_symlink():
            link.unlink()
        link.symlink_to(target)


def lines(p: Path) -> list[dict]:
    return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []


def case_fast_fall(td: Path):
    proc, sd, data = td / "procA", td / "sdA", td / "dataA"
    data.mkdir(parents=True)
    big = data / "runaway.log (deleted)"        # what readlink shows for a deleted file still held open
    big.write_bytes(os.urandom(64 * 1024))
    small = data / "small.txt"
    small.write_text("x")
    os.environ.update(DISK_GROWER_PROC=str(proc), DISK_GROWER_BIG_GB="0.00001")
    t0 = 1_800_000_000.0
    fake_pid(proc, 100, 5000, 1 * 10 ** 9, "rm-relentless-work-abc-g1.service", data, "python3 copy_tree.py", [big, small])
    fake_pid(proc, 101, 6000, 2 * 10 ** 6, "rm-metronome.service", data, "python3 metronome.py")
    r1 = G.tick(sd, 500.0, 420.0, root=str(data), now=t0)
    check(r1["captured"] is False, "A0 a steady first tick captures nothing")
    fake_pid(proc, 100, 5000, 51 * 10 ** 9, "rm-relentless-work-abc-g1.service", data, "python3 copy_tree.py", [big, small])
    fake_pid(proc, 101, 6000, 3 * 10 ** 6, "rm-metronome.service", data, "python3 metronome.py")
    r2 = G.tick(sd, 460.0, 420.0, root=str(data), now=t0 + 600)
    check(r2["captured"] and r2["fall_gb"] == 40.0, f"A1 a 40 GB fall in 10 min captures (row {r2})")
    cap = json.loads((sd / "growth_capture.json").read_text())
    w = cap["writers"][0] if cap["writers"] else {}
    check(w.get("pid") == 100 and w.get("gb") == 50.0 and w.get("unit") == "rm-relentless-work-abc-g1.service"
          and w.get("cwd") == str(data) and "copy_tree.py" in w.get("cmd", ""),
          f"A2 the top writer is pid 100, 50 GB, its unit, cwd and command ({w})")
    check(w.get("gb_per_min") == 5.0, f"A3 its rate is 5 GB/min ({w.get('gb_per_min')})")
    ob = cap["open_big"]
    check(len(ob) == 1 and ob[0]["deleted"] and ob[0]["pids"] == [100] and ob[0]["path"].endswith("runaway.log"),
          f"A4 the big open file is listed once, deleted, held by pid 100; the small one is not ({ob})")
    al = (sd / "alarms.log").read_text()
    check("GROWER pid 100 wrote 50.0 GB" in al and "pid 101" not in al, "A5 alarms.log names pid 100 and not pid 101")
    check(r2.get("named") == [{"pid": 100, "gb": 50.0, "unit": "rm-relentless-work-abc-g1.service"}],
          f"A6 the growth row names the grower ({r2.get('named')})")
    check(len(lines(sd / "growth.jsonl")) == 2 and len(lines(sd / "growth_captures.jsonl")) == 1,
          "A7 one growth row per tick, one capture appended")
    # B: pid 100 exits and the pid is reused by a new process with a small count
    fake_pid(proc, 100, 9999, 3 * 10 ** 9, "rm-other.service", data, "python3 other.py")
    r3 = G.tick(sd, 425.0, 420.0, root=str(data), now=t0 + 1200)
    cap = json.loads((sd / "growth_capture.json").read_text())
    w = {x["pid"]: x for x in cap["writers"]}
    check(r3["captured"] and w.get(100, {}).get("gb") == 3.0 and all(x["gb"] > 0 for x in cap["writers"]),
          f"B1 a reused pid counts from its own start: 3 GB, never 3-51 ({cap['writers']})")


def case_slow_fall(td: Path):
    proc, sd, data = td / "procC", td / "sdC", td / "dataC"
    data.mkdir(parents=True)
    os.environ["DISK_GROWER_PROC"] = str(proc)
    t0 = 1_800_000_000.0
    fake_pid(proc, 300, 100, 10 ** 9, "rm-a.service", data, "a")
    G.tick(sd, 560.0, 420.0, root=str(data), now=t0)
    fake_pid(proc, 300, 100, 2 * 10 ** 9, "rm-a.service", data, "a")
    r = G.tick(sd, 555.0, 420.0, root=str(data), now=t0 + 600)
    check(not r["captured"] and not (sd / "growth_capture.json").exists() and not (sd / "alarms.log").exists(),
          f"C1 a 5 GB fall above the line captures nothing and names nobody ({r})")
    check(r["top_writer_gb"] == 1.0, f"C2 the row still carries the top writer's GB ({r['top_writer_gb']})")
    # D: under the line, no fall
    r = G.tick(sd, 400.0, 420.0, root=str(data), now=t0 + 4000)
    cap = json.loads((sd / "growth_capture.json").read_text()) if (sd / "growth_capture.json").exists() else {}
    check(r["captured"] and any("under the 420.0 GB line" in x for x in cap.get("why", [])),
          f"D1 under the line captures and says why ({cap.get('why')})")


def case_first_tick(td: Path):
    proc, sd, data = td / "procE", td / "sdE", td / "dataE"
    data.mkdir(parents=True)
    os.environ["DISK_GROWER_PROC"] = str(proc)
    fake_pid(proc, 400, 100, 900 * 10 ** 9, "rm-old.service", data, "old")
    r = G.tick(sd, 100.0, 420.0, root=str(data), now=1_800_000_000.0)
    cap = json.loads((sd / "growth_capture.json").read_text())
    check(r["captured"] and cap["writers"] == [] and not (sd / "alarms.log").exists(),
          f"E1 with no previous sample a lifetime count is ranked as nobody ({cap['writers']})")


def case_real_proc():
    os.environ.pop("DISK_GROWER_PROC", None)
    cur, blind = G.sample_io(G.proc_root())
    check(str(os.getpid()) in cur and len(cur) >= 1, f"F1 the real /proc sample sees this process ({len(cur)} readable, "
                                                    f"{blind} blind)")
    check(G.unit_of(Path("/proc"), str(os.getpid())) is not None or not Path("/proc/self/cgroup").exists(),
          "F2 this process's own unit is read from its cgroup")


def case_pressure_check(td: Path):
    import scratch_reap as R
    sd = td / "sdG"
    env = {"SCRATCH_REAP_STATE": str(sd), "SCRATCH_REAP_PRESSURE_GB": "0", "SCRATCH_REAP_ROOTS": "",
           "SCRATCH_REAP_TMP": "", "DISK_GROWER_PROC": str(td / "procG")}
    old = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    (td / "procG").mkdir()
    try:
        rc = R.pressure_check()
        rows = lines(sd / "growth.jsonl")
        check(rc == 0 and len(rows) == 1 and "free_gb" in rows[0] and "error" not in rows[0],
              f"G1 pressure_check writes one growth row with nothing else to do ({rows})")
        real = G.tick

        def boom(*a, **k):
            raise RuntimeError("mutant")
        G.tick = boom
        try:
            rc = R.pressure_check()
        finally:
            G.tick = real
        rows = lines(sd / "growth.jsonl")
        check(rc == 0 and "mutant" in rows[-1].get("error", ""),
              f"G2 a grower that raises leaves an error row and the pressure check still finishes ({rows[-1]})")
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def main() -> int:
    td = Path(tempfile.mkdtemp(prefix="grower_selftest_"))
    try:
        case_fast_fall(td)
        case_slow_fall(td)
        case_first_tick(td)
        case_real_proc()
        case_pressure_check(td)
    finally:
        shutil.rmtree(td, ignore_errors=True)
    print("FAIL" if FAILS else "OK", "selftest_scratch_reap_grower")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
