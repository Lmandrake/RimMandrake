#!/usr/bin/env python3
"""Selftest for oom_attribution.py: real kernel line shapes, every class, and the zero that must not read as clean."""
import contextlib
import io
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oom_attribution as oa  # noqa: E402

FAILS = []
U = "/user.slice/user-1000.slice/user@1000.service/"
GB = 1 << 30


def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def kill_block(at, memcg, limit_kb, anon, shmem, task="python3", pid=7):
    p = at + "-08:00 Archmagi kernel: "
    return [p + "memory: usage %dkB, limit %dkB, failcnt 9" % (limit_kb, limit_kb),
            p + "swap: usage 0kB, limit 0kB, failcnt 0",
            p + "anon %d" % anon, p + "file %d" % shmem, p + "shmem %d" % shmem,
            p + "oom-kill:constraint=CONSTRAINT_MEMCG,nodemask=(null),cpuset=/,mems_allowed=0,oom_memcg=%s,task_memcg=%s,task=%s,pid=%d,uid=1000"
            % (U + memcg, U + memcg, task, pid),
            p + "Memory cgroup out of memory: Killed process %d (%s) total-vm:1kB, anon-rss:116608kB, file-rss:7044kB, shmem-rss:0kB, UID:1000" % (pid, task)]


BOMB = "rm.slice/rm-harness.slice/rm-harness-11-2.scope"
PLAIN = "rm.slice/rm-harness.slice/rm-harness-12-4.scope"
TOOL = "claude.slice/claude-seats.slice/claude-seat-BENCH-rm-relentless-work-aa-g3.scope/claude-code-bash"
lines = (["2026-11-03T14:48:48-08:00 Archmagi systemd[290]: Started rm-harness-11-2.scope - [systemd-run] /usr/bin/python3 /t/run_selftests.py --_harness-child -- /usr/bin/python3 /t/bomb.py."]
         + kill_block("2026-11-03T14:48:48", BOMB, 131072, 120 << 20, 0, pid=1)
         + kill_block("2026-11-03T14:49:00", PLAIN, 3145728, 3 * GB, 0, pid=2)
         + kill_block("2026-11-03T14:50:00", TOOL, 6291456, 150 << 20, 6 * GB - (150 << 20), task="git", pid=3)
         + kill_block("2026-11-03T14:51:00", TOOL, 6291456, 4 * GB, 2 * GB, pid=4)
         + kill_block("2026-11-03T14:52:00", "claude.slice/claude-seats.slice", 25165824, 20 * GB, 4 * GB, pid=5)
         + kill_block("2026-11-03T14:53:00", "rm.slice/rm-harness.slice", 25165824, 24 * GB, 0, pid=6)
         + ["2026-11-03T14:54:00-08:00 Archmagi kernel: oom-kill:constraint=CONSTRAINT_NONE,nodemask=(null),cpuset=/,mems_allowed=0,global_oom,task_memcg=/x,task=java,pid=8,uid=1000",
            "2026-11-03T14:54:00-08:00 Archmagi kernel: Out of memory: Killed process 8 (java) total-vm:1kB, anon-rss:1kB, file-rss:1kB, shmem-rss:0kB, UID:1000"])
kills, bombs = oa.parse(lines)
got = [k["class"] for k in kills]
ok(got == ["planted_fixture", "harness_test", "seat_tool_tmpfs", "seat_tool_anon", "SLICE", "SLICE", "HOST"], "every class: %s" % got)
ok(bombs == {"rm-harness-11-2.scope"}, "a bomb scope is known by its Started line")
ok(kills[2]["limit_kb"] == 6291456 and kills[2]["shmem"] > 5 * GB and kills[2]["task"] == "git", "limit, shmem and task reach the kill")

# Planted break: the fixture must not be recognised by its small limit alone.
no_start = [ln for ln in lines if "Started" not in ln]
ok(oa.parse(no_start)[0][0]["class"] == "harness_test", "with no Started line a 128 MiB kill is not called a fixture")

rep = oa.report(kills)
ok(rep[-1] == "slice-limit kills: 2  whole-host kills: 1", "the verdict line counts slice and host: %s" % rep[-1])
rep0 = oa.report(kills[:1])
ok(rep0[-1] == "slice-limit kills: 0  whole-host kills: 0", "a measured zero is still printed")

kept = [ln for ln in lines if oa.keep_line(ln)]
ok([k["class"] for k in oa.parse(kept)[0]] == got, "an extract classifies the same as the full journal")
ok(not oa.keep_line("2026-11-03T14:48:48-08:00 Archmagi systemd[290]: Started rm-harness-1-1.scope - /x/selftest_a.py."), "an ordinary scope start stays out of the extract")

with tempfile.TemporaryDirectory() as tmp:
    src, out = os.path.join(tmp, "k.txt"), os.path.join(tmp, "x.txt")
    Path(src).write_text("\n".join(lines) + "\n")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = oa.main(["--kern", src, "--extract", out])
    ok(rc == 0 and "planted_fixture=1" in buf.getvalue(), "main classifies a saved file")
    ok(Path(out).read_text().count("oom-kill:") == 7, "main writes the extract")
    empty = os.path.join(tmp, "e.txt")
    Path(empty).write_text("nothing here\n")
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        rc = oa.main(["--kern", empty])
    ok(rc == 2 and "UNMEASURED" in err.getvalue(), "no kill line is UNMEASURED, exit 2, never a clean zero")

print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
