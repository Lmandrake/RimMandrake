#!/usr/bin/env python3
"""progress_guard ends a silent child, and never one that is slow and alive. exit 0 all pass, 1 a promise is broken.

Page: design/specs/2026-11-24-progress-guard/boundary.md. Each case has its opposite: a guard that ends everything fails
`slow-writer-lives`, a guard that ends nothing fails `silent-child-ends`.
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import progress_guard as G  # noqa: E402

PY = sys.executable
BAD = []
BURN = "import time\nt = time.monotonic()\nwhile time.monotonic() - t < 9: pass"


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        BAD.append(what)


def hung(argv, **kw):
    t = time.monotonic()
    try:
        G.run(argv, **kw)
        return None, time.monotonic() - t
    except G.Hung as e:
        return e, time.monotonic() - t


def t_ended_child_keeps_its_result():
    r = G.run([PY, "-c", "import sys; print('out'); print('err', file=sys.stderr); sys.exit(3)"], silence_s=30)
    check((r.returncode, r.stdout, r.stderr) == (3, "out\n", "err\n"), "ended-child-keeps-its-result: rc, out and err")
    r = G.run([PY, "-c", "import sys; sys.stdout.write('x' * 3000000)"], silence_s=30)
    check(len(r.stdout) == 3000000, "ended-child-keeps-its-result: 3 MB of output, whole")


def t_silent_child_ends():
    e, s = hung([PY, "-c", "import time; time.sleep(600)"], silence_s=3)
    check(e is not None and "no CPU time" in e.why and s < 120, "silent-child-ends: a sleep is ended (%s)" % e)
    check(isinstance(e, subprocess.TimeoutExpired), "silent-child-ends: an old `except TimeoutExpired` still catches it")


def t_slow_writer_lives():
    r = G.run([PY, "-u", "-c", "import time\nfor i in range(12): print(i); time.sleep(0.5)"], silence_s=4)
    check(r.returncode == 0 and r.stdout.split()[-1] == "11", "slow-writer-lives: 6 s of slow output, silence 4 s")


def t_silent_worker_lives():
    r = G.run([PY, "-c", BURN], silence_s=4)
    check(r.returncode == 0, "silent-worker-lives: 9 s of CPU with no output, silence 4 s")
    r = G.run(["bash", "-c", "%s -c '%s'; exit 4" % (PY, BURN)], silence_s=4)
    check(r.returncode == 4, "silent-worker-lives: the CPU time is a grandchild's")


def t_spinning_child_ends_at_the_backstop():
    e, s = hung([PY, "-c", "while True: pass"], silence_s=60, cap_s=4)
    check(e is not None and "backstop" in e.why and s < 120, "spinning-child-ends-at-the-backstop (%s)" % e)


def t_run_kills_the_session():
    mark = "pg_selftest_%d" % os.getpid()
    hung(["bash", "-c", "exec -a %s sleep 600 & sleep 600" % mark], silence_s=3)
    time.sleep(0.5)
    left = [p for p in os.listdir("/proc") if p.isdigit() and mark in _cmd(p)]
    check(not left, "run-kills-the-session: no grandchild is left")


def t_could_not_look_is_not_a_hang():
    p = subprocess.Popen([PY, "-c", "import time; time.sleep(5)"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def blind(_pid):
        raise G.waitalive.CouldNotLook("planted")
    G.communicate(p, silence_s=2, poll_s=0.2, cpu=blind)
    check(p.returncode == 0, "could-not-look-is-not-a-hang: an unreadable process tree ends nothing")


def t_a_left_behind_process_does_not_hold_the_result():
    keep, G.LEFT_OPEN_S = G.LEFT_OPEN_S, 2
    t = time.monotonic()
    r = G.run(["bash", "-c", "sleep 60 & echo done; exit 5"], silence_s=40)
    G.LEFT_OPEN_S = keep
    check((r.returncode, r.stdout) == (5, "done\n") and time.monotonic() - t < 35,
          "a-left-behind-process-does-not-hold-the-result")


def main():
    G.communicate.__defaults__ = tuple(0.2 if d == G.POLL_S else d for d in G.communicate.__defaults__)
    for t in (t_ended_child_keeps_its_result, t_silent_child_ends, t_slow_writer_lives, t_silent_worker_lives,
              t_spinning_child_ends_at_the_backstop, t_run_kills_the_session, t_could_not_look_is_not_a_hang,
              t_a_left_behind_process_does_not_hold_the_result):
        t()
    print("RESULT: %s" % ("FAIL %d" % len(BAD) if BAD else "PASS"))
    return 1 if BAD else 0


def _cmd(pid):
    try:
        return open("/proc/%s/cmdline" % pid, "rb").read().decode("utf-8", "replace")
    except OSError:
        return ""


if __name__ == "__main__":
    sys.exit(main())
