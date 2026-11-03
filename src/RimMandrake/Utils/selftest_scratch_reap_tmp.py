#!/usr/bin/env python3
# selftest-timeout: 600
"""selftest_scratch_reap_tmp.py — scratch_reap's /tmp backstop (sweep_tmp, TMP_SCRATCH_ENFORCE_MUTANTS_CLEAN_UP).

Every path is a temp root named through SCRATCH_REAP_TMP; the real /tmp is only READ (one mount-table question).
Proves: an idle loose file and an idle dir go; a dir with a fresh file inside stays (newest-inside, not the dir's own
stamp); a protected name, a socket, another uid's entry, a selftest fixture, a clone and a used dir stay; a dry run
removes nothing; a crash's pin goes; the deadline defers; the run records the sweep (last_run.json, tmp_runs.jsonl, the
manifest); the /tmp tmpfs's own mount is not an alias; and the pressure check fires on /tmp alone.
"""
import copy
import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
FAILS = []
IDLE = 15           # seconds: long enough that a "young" entry stays young through every sweep below


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def main():
    td = Path(tempfile.mkdtemp(prefix="selftest_scratch_reap_tmp_"))
    roots, tmp = td / "roots", td / "tmp"
    roots.mkdir()
    tmp.mkdir()
    (td / "transcripts").mkdir()
    (td / "archive").mkdir()
    os.environ.update(SCRATCH_REAP_ROOTS=os.pathsep.join([str(roots), str(tmp)]), SCRATCH_REAP_TMP=str(tmp),
                      SCRATCH_REAP_SCAN=os.pathsep.join([str(roots), str(tmp)]), SCRATCH_REAP_CORPUS=str(td / "corpus"),
                      SCRATCH_REAP_STATE=str(td / "state"), SCRATCH_REAP_TRANSCRIPTS=str(td / "transcripts"),
                      SCRATCH_REAP_MIRRORS=str(td / "nomirror"), SCRATCH_REAP_RM_SCRATCH="/nonexistent",
                      LEFTOVERS_ARCHIVE_ROOT=str(td / "archive"), SCRATCH_REAP_TMP_IDLE_HOURS=str(IDLE / 3600),
                      RM_RUN_TMP_ROOT=str(td / "runs"))
    os.environ.pop("SCRATCH_REAP_UNIT", None)
    import scratch_reap as s
    procs = []
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))     # a killed run still runs the finally: no leaked sleeps
    try:
        (tmp / "loose.txt").write_text("x" * 100)
        (tmp / "olddir" / "sub").mkdir(parents=True)
        (tmp / "olddir" / "sub" / "f").write_text("y" * 50)
        (tmp / "freshinside" / "deep").mkdir(parents=True)
        (tmp / "tmux-1000").mkdir()
        (tmp / "systemd-private-abc").mkdir()
        (tmp / "clone" / ".git").mkdir(parents=True)
        (tmp / "save").mkdir()
        (tmp / "save" / "a.rws").write_text("<savegame/>")
        (tmp / "selftest_fixture_x").mkdir()
        (tmp / "used").mkdir()
        (tmp / ".reaping-1-crashed").mkdir()
        (tmp / "link").symlink_to("/nonexistent-target")
        (tmp / "rescue.rws").write_text("<savegame/>")                  # a loose save is work, not scratch
        for sub in ("objects", "refs"):
            (tmp / "bare.git" / sub).mkdir(parents=True)                # a bare repo: no .git inside, still work
        (tmp / "bare.git" / "HEAD").write_text("ref: refs/heads/main\n")
        (tmp / "important").mkdir()                                     # named in SCRATCH_REAP_PROTECTED
        os.environ["SCRATCH_REAP_PROTECTED"] = str(tmp / "important")
        (tmp / "selftest_rescue" / ".git").mkdir(parents=True)          # a selftest_ name in /tmp proves nothing
        (tmp / "racer").mkdir()
        (tmp / ".reaping-1-orighold").mkdir()                          # a crash's pin whose ORIGINAL name a process names
        sk = socket.socket(socket.AF_UNIX)
        sk.bind(str(tmp / "agent.s0"))
        time.sleep(IDLE + 0.5)
        (tmp / "freshinside" / "deep" / "new").write_text("now")
        (tmp / "young.txt").write_text("now")
        fut = time.time() + 86400                       # young by mtime however slow the sweeps below run (ctime is now)
        for f in (tmp / "freshinside" / "deep" / "new", tmp / "young.txt"):
            os.utime(f, (fut, fut))
        procs.append(subprocess.Popen(["sh", "-c", "sleep 300", str(tmp / "orighold")]))
        procs.append(subprocess.Popen(["sleep", "300"], cwd=str(tmp / "used")))
        time.sleep(0.3)

        ctx = s.Ctx(time.time())
        out, rows = s.sweep_tmp(ctx, False, 0)
        paths = {Path(r["path"]).name for r in rows}
        ok(paths == {"loose.txt", "olddir", ".reaping-1-crashed", "link", "racer"}, "dry run picks exactly the idle unheld entries: %s %s" % (sorted(paths), out["errors"][:2]))
        ok((tmp / "loose.txt").exists() and (tmp / "olddir").exists(), "a dry run removes nothing")
        ok(out["work"] == 4, "a clone, a saves dir, a loose .rws and a bare repo are the clone judgment's (work=%s)" % out["work"])
        lk = tmp / "link"
        ok(out["held"] == 2, "a dir a process works in, and a pin whose original name a process names, are held (held=%s; link: %s %s %s)" % (
            out["held"], ctx.mounted(lk), ctx.live.users(lk), ctx.borrows.of(lk)))
        ok(out["young"] == 2, "a fresh file, and a dir whose own stamp is old but whose inside is fresh, are young (%s)" % out["young"])
        ok(out["skipped"] >= 5, "protected names, a socket, a fixture and a SCRATCH_REAP_PROTECTED path are skipped (%s)" % out["skipped"])
        later = copy.copy(ctx)                          # the same /proc look, two days on (a Ctx costs a /proc walk)
        later.now = time.time() + 2 * 86400
        fx = s.sweep_fixtures(later, False, 0)
        ok(fx["held"] >= 1 and fx["removed"] == 1, "a /tmp/selftest_ dir holding a repo is held; only the empty fixture would go (%s)" % fx)

        # the post-rename look: a process that entered an entry after the judgment's /proc look is seen under the pin
        ctx = s.Ctx(time.time())
        pin = tmp / (".reaping-%d-racer" % os.getpid())
        os.rename(tmp / "racer", pin)
        procs.append(subprocess.Popen(["sleep", "300"], cwd=str(pin)))
        time.sleep(0.3)
        o2, d2 = {"held": 0, "removed": 0, "bytes": 0, "errors": []}, []
        s._tmp_flush(ctx, [(tmp / "racer", pin, tmp / "racer", True, {"kind": "tmp"}, 0)], o2, d2)
        ok((tmp / "racer").is_dir() and o2["held"] == 1 and not d2, "an entry used after the look goes back under its name (%s)" % o2)
        procs[-1].kill()
        procs[-1].wait()
        pin3 = tmp / (".reaping-%d-racer3" % os.getpid())
        pin3.mkdir()
        (tmp / "racer3").mkdir()                        # the name was made again while the old entry sat pinned
        (tmp / "racer3" / "new").write_text("fresh")
        user = subprocess.Popen(["sleep", "300"], cwd=str(pin3))
        time.sleep(0.3)
        o3 = {"held": 0, "removed": 0, "bytes": 0, "errors": []}
        s._tmp_flush(ctx, [(tmp / "racer3", pin3, tmp / "racer3", True, {"kind": "tmp"}, 0)], o3, [])
        ok(pin3.is_dir() and (tmp / "racer3" / "new").exists() and o3["held"] == 1 and o3["errors"],
           "a restore never lands on a new entry made under the name (%s)" % o3)
        user.kill()
        user.wait()
        subprocess.run(["rm", "-rf", str(pin3), str(tmp / "racer3")])
        os.utime(tmp / "racer", (fut, fut))             # the rename made it young; keep it so for the apply below
        procs[0].kill()                                 # the original name's user ends: its pin is free to go
        procs[0].wait()

        out, rows = s.sweep_tmp(ctx, True, time.time() - 1)
        ok(out["deferred"] > 0 and out["removed"] == 0, "past the deadline nothing is started")

        ctx = s.Ctx(time.time())
        out, rows = s.sweep_tmp(ctx, True, 0)
        left = set(os.listdir(tmp))
        ok(not ({"loose.txt", "olddir", ".reaping-1-crashed", "link", ".reaping-1-orighold"} & left), "apply removes the idle entries (left %s)" % sorted(left))
        ok(all(r["verdict"] == "DELETED" for r in rows) and out["removed"] == 5 and out["bytes"] >= 150,
           "each removal is a DELETED row with its bytes (%s)" % out)
        ok({"tmux-1000", "systemd-private-abc", "clone", "save", "selftest_fixture_x", "used", "freshinside", "young.txt",
            "agent.s0", "rescue.rws", "bare.git", "important", "selftest_rescue", "racer"} <= left, "everything held, young, protected or special stays (%s)" % sorted(left))
        ok(not any(n.startswith(".reaping-") for n in left), "no pin is left behind")

        real = os.getuid
        os.getuid = lambda: real() + 4242
        try:
            (tmp / "foreign.txt").write_text("z")
            time.sleep(IDLE + 0.2)
            ctx.now = time.time()                       # nothing of another uid's is judged, so no fresh look is needed
            out, rows = s.sweep_tmp(ctx, True, 0)
        finally:
            os.getuid = real
        ok((tmp / "foreign.txt").exists() and out["removed"] == 0, "another uid's entry is never judged")

        os.environ["SCRATCH_REAP_TMP"] = "/tmp"
        os.environ["SCRATCH_REAP_ROOTS"] = os.pathsep.join([str(roots), "/tmp"])
        m = s.Ctx.mounted(ctx, Path("/tmp/selftest-no-such-entry"))
        ok(m == [], "the /tmp tmpfs's own mount is the filesystem, not an alias (%s)" % m)
        os.environ["SCRATCH_REAP_TMP"] = str(tmp)
        m = s.Ctx.mounted(ctx, Path("/tmp/selftest-no-such-entry"))
        ok(bool(m), "a mount above a candidate in a root that is not the tmp root still refuses")
        os.environ["SCRATCH_REAP_ROOTS"] = os.pathsep.join([str(roots), str(tmp)])

        (tmp / "loose2.txt").write_text("q" * 10)
        time.sleep(IDLE + 0.2)
        rc = subprocess.run([sys.executable, str(Path(s.__file__)), "--apply"], capture_output=True, text=True,
                            timeout=300, env=dict(os.environ, SCRATCH_REAP_TMP_IDLE_HOURS=str(IDLE / 3600)))
        rec = json.loads((td / "state" / "last_run.json").read_text())
        ok(rec.get("tmp", {}).get("removed", 0) >= 1 and rec["tmp"].get("before") is not None,
           "the run records the /tmp sweep and the tmpfs reading (rc %d %s)" % (rc.returncode, (rc.stdout + rc.stderr)[-600:]))
        ok(not (tmp / "loose2.txt").exists(), "the run removed the idle file")
        ok((td / "state" / "tmp_runs.jsonl").exists(), "the removals are rowed in tmp_runs.jsonl")
        mans = list((td / "archive").rglob("*.manifest.json"))
        ok(mans and any(r["kind"] == "tmp" for r in json.loads(mans[0].read_text())), "the manifest lists the /tmp removal")
        ok("run_tmp" in rec, "the run swept the per-run TMPDIR root too (%s)" % rec.get("run_tmp"))

        env = dict(os.environ, SCRATCH_REAP_PRESSURE_GB="0", SCRATCH_REAP_TMP_PRESSURE_GB="0",
                   SCRATCH_REAP_TMP_PRESSURE_PCT="101", SCRATCH_REAP_COOLDOWN_MIN="0")
        r = subprocess.run([sys.executable, str(Path(s.__file__)), "--pressure-check"], capture_output=True, text=True, timeout=60, env=env)
        ok("nothing to do" in r.stdout, "no pressure, no start")
        env.update(SCRATCH_REAP_TMP_PRESSURE_PCT="-1", SCRATCH_REAP_UNIT="rm-selftest-no-such-unit.service")
        r = subprocess.run([sys.executable, str(Path(s.__file__)), "--pressure-check"], capture_output=True, text=True, timeout=60, env=env)
        lines = (td / "state" / "pressure.jsonl").read_text().splitlines()
        ok(lines and json.loads(lines[-1]).get("tmp_low") is True, "a full /tmp alone starts a run")
        sk.close()
    finally:
        for p in procs:
            p.kill()
            p.wait()
        subprocess.run(["rm", "-rf", str(td)])
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
