#!/usr/bin/env python3
"""selftest_steve_worker_windows_tree.py - a stopped or killed attempt leaves no Windows process of its own alive
(RIMMANDRAKE_KILL_WINDOWS_CHILD_ON_TESTQ_CANCEL_ORPHAN_DROVE_STEVE2).

The fault: `testq cancel --running` of J20261125T083122Z-dedc8e ended the worker, but thirst_live.py (Windows pid 11336),
started by live_session.py's python.exe, drove Steve2 for 20 minutes more. A killpg reaches the WSL shim and the shim's
own python.exe, never that python.exe's Windows children (measured on Archmagi 2026-11-26).

The fake Windows: `python.exe` on PATH is python3; the attempt's root spawns a child in its own session, which no
killpg of the attempt reaches, as no killpg reaches a Windows grandchild; the Windows process table (TESTQ_CMD_WINPS)
lists this machine's python processes from /proc; the kill (TESTQ_CMD_WINKILL) is kill -9. What must hold:
  tag_windows_python: each command-starting python.exe carries `-X testq_attempt=<aid>`; an argument word is left alone;
  windows_tree: the tagged roots and their descendants; .a1 is not .a10; a pid-reuse child (older than its parent) is
    not followed; the game and Steam, and what they started, are never in it;
  worker stop of a running attempt: the fake Windows grandchild is seen dead (red on the base: it lived on);
  a hung command killed at its deadline (kill_child): the fake Windows grandchild is seen dead.
--real-windows runs both scenes on this machine's real Windows instead (exit 3: could not look).
"""
import os
import shutil
import stat
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
HOME = tempfile.mkdtemp(prefix="testq_wintree_home_")
os.environ["TESTQ_HOME"] = HOME     # never the real queue, even when the caller's environment names one
import worker as W  # noqa: E402

FAILS = []


def check(ok, msg):
    print("%s %s" % ("PASS" if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


# The Windows process table, faked from /proc: every python process, as pid|ppid|created|name|cmdline.
FAKE_PS = r'''
import os
btime = next(int(l.split()[1]) for l in open("/proc/stat") if l.startswith("btime"))
hz = os.sysconf("SC_CLK_TCK")
for d in os.listdir("/proc"):
    if not d.isdigit():
        continue
    try:
        st = open("/proc/%s/stat" % d).read()
        cmd = open("/proc/%s/cmdline" % d, "rb").read().replace(b"\0", b" ").decode(errors="replace").strip()
    except OSError:
        continue
    name, rest = st[st.index("(") + 1:st.rindex(")")], st[st.rindex(")") + 2:].split()
    if rest[0] == "Z" or not name.startswith("python"):
        continue
    print("%s|%s|%d|%s.exe|%s" % (d, rest[1], btime + int(rest[19]) // hz, name, cmd))
'''

# The attempt's root python.exe: starts a child in its own session (the Windows grandchild no killpg reaches), writes
# the child's pid, and waits.
ROOT = r'''
import subprocess, sys, time
c = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"], start_new_session=True)
open(sys.argv[1], "a").write("%d\n" % c.pid)
time.sleep(120)
'''


def alive(pid):
    try:
        with open("/proc/%d/stat" % pid) as f:
            return f.read().rsplit(")", 1)[1].split()[0] != "Z"
    except (OSError, IndexError):
        return False


def wait_pids(path, n, limit=20):
    t = time.time()
    while time.time() - t < limit:
        try:
            pids = [int(x) for x in open(path).read().split()]
            if len(pids) >= n:
                return pids
        except (OSError, ValueError):
            pass
        time.sleep(0.1)
    return []


def gone_soon(pids, limit=5):
    t = time.time()
    while time.time() - t < limit and any(alive(p) for p in pids):
        time.sleep(0.1)
    return [p for p in pids if alive(p)]


def attempt(aid, d):
    a = W.Attempt.__new__(W.Attempt)
    a.aid, a.d, a.child = aid, d, None
    a.log = open(os.path.join(d, "worker.log"), "a", encoding="utf-8")
    return a


def t_python_exe_carries_the_attempt_tag():
    f = getattr(W, "tag_windows_python", None)
    check(callable(f), "tag_windows_python exists")
    if callable(f):
        got = f("python.exe a.py && X=1 python.exe -X faulthandler b.py; python.exe c.py | python.exe d.py", "J1.a1")
        want = ("python.exe -X testq_attempt=J1.a1 a.py && X=1 python.exe -X testq_attempt=J1.a1 -X faulthandler b.py; "
                "python.exe -X testq_attempt=J1.a1 c.py | python.exe -X testq_attempt=J1.a1 d.py")
        check(got == want, "every command-starting python.exe is tagged: %r" % got)
        got = f("export A=1 WSLENV=${WSLENV:+$WSLENV:}A; python.exe x.py --py python.exe2 --note 'python.exe later'", "J1.a1")
        check(got == "export A=1 WSLENV=${WSLENV:+$WSLENV:}A; python.exe -X testq_attempt=J1.a1 x.py --py python.exe2 "
              "--note 'python.exe later'", "after an export, tagged; argument words left alone: %r" % got)
        check(f("python3 x.py && taskkill.exe /F", "J1.a1") == "python3 x.py && taskkill.exe /F", "no python.exe: unchanged")


def t_windows_tree_is_the_attempts_own():
    t = getattr(W, "windows_tree", None)
    check(callable(t), "windows_tree exists")
    if callable(t):
        rows = [(10, 1, 100, "python.exe", "python.exe -X testq_attempt=J1.a1 live_session.py"),
                (11, 10, 101, "python.exe", "python.exe thirst_live.py"),
                (12, 11, 102, "powershell.exe", "powershell.exe -Command x"),
                (13, 12, 103, "RimWorldWin64.exe", "RimWorldWin64.exe"),
                (14, 13, 104, "CrashHandler.exe", "crash"),
                (15, 10, 50, "notepad.exe", "an older process whose dead parent's pid 10 was reused"),
                (20, 1, 100, "python.exe", "python.exe -X testq_attempt=J1.a10 other.py"),
                (21, 20, 101, "python.exe", "python.exe other_child.py"),
                (30, 1, 100, "python.exe", "python.exe unrelated.py")]
        check(t(rows, "J1.a1") == [10, 11, 12], "roots and descendants; not .a10, not a reused pid, not the game: %s"
              % t(rows, "J1.a1"))
        check(t(rows, "J1.a10") == [20, 21], ".a10's own tree: %s" % t(rows, "J1.a10"))
        check(t(rows, "J9.a1") == [], "an attempt with no Windows process: empty")
        check(t([(5, 5, 1, "python.exe", "python.exe -X testq_attempt=J1.a1 x")], "J1.a1") == [5],
              "a process that is its own parent (pid 0 on Windows) ends the walk")


def fake_windows(tmp):
    """PATH's python.exe, the fake table and kill; -> the root script's path."""
    bindir = os.path.join(tmp, "bin")
    os.makedirs(bindir)
    exe = os.path.join(bindir, "python.exe")
    with open(exe, "w") as f:
        f.write('#!/bin/sh\nexec %s "$@"\n' % sys.executable)
    os.chmod(exe, os.stat(exe).st_mode | stat.S_IEXEC)
    fake_ps, root = os.path.join(tmp, "fake_ps.py"), os.path.join(tmp, "root.py")
    open(fake_ps, "w").write(FAKE_PS)
    open(root, "w").write(ROOT)
    os.environ["PATH"] = bindir + os.pathsep + os.environ.get("PATH", "")
    os.environ["TESTQ_CMD_WINPS"] = "%s %s" % (sys.executable, fake_ps)
    os.environ["TESTQ_CMD_WINKILL"] = "kill -9"
    # a sanity probe: the fake table must see a tagged process at all, or a dead child proves nothing
    import subprocess
    # budget: danger=a hung /proc read holds the test; longest=1s (one measured run on Archmagi 2026-11-26)
    table = subprocess.run([sys.executable, fake_ps], capture_output=True, text=True, timeout=60).stdout
    check(any(line.startswith("%d|" % os.getpid()) for line in table.splitlines()),
          "the fake Windows table sees this python: %d lines" % len(table.splitlines()))
    return root


def t_stop_ends_the_windows_grandchild(tmp, root):
    """worker stop of a running attempt: what testq cancel --running sends."""
    aid = "J20261126T000000Z-wintre.a1"
    d = os.path.join(HOME, "attempts", aid)
    os.makedirs(d)
    W.S.dump({"phase": "run"}, os.path.join(d, "state.json"))   # no unit, no pid: the stop's Windows step alone acts
    a = attempt(aid, d)
    pidfile = os.path.join(tmp, "kids_stop")
    out = {}
    # budget: fixture
    th = threading.Thread(target=lambda: out.update(r=a.sh("python.exe %s %s" % (root, pidfile), timeout=60)))
    th.start()
    kids = wait_pids(pidfile, 1)
    check(len(kids) == 1 and alive(kids[0]), "the fake Windows grandchild runs before the stop: %s" % kids)
    W.cmd_stop(aid)
    left = gone_soon(kids)
    check(kids and not left, "worker stop: the cancelled job's fake Windows grandchild is seen dead: alive %s" % left)
    th.join(30)
    check(not th.is_alive() and out.get("r", (0,))[0] is not None,
          "the stopped root ended too, so the attempt's command returned: %r" % (out.get("r"),))
    for p in left:
        os.kill(p, 9)


def t_a_killed_command_ends_its_windows_grandchild(tmp, root):
    """a hung command killed at its deadline (kill_child), as the Stopped (SIGTERM) path kills it."""
    aid = "J20261126T000000Z-wintre.a2"
    d = os.path.join(HOME, "attempts", aid)
    os.makedirs(d)
    a = attempt(aid, d)
    pidfile = os.path.join(tmp, "kids_hang")
    # budget: fixture
    rc, _ = a.sh("python.exe %s %s" % (root, pidfile), timeout=3)
    kids = wait_pids(pidfile, 1, limit=1)
    left = gone_soon(kids)
    check(rc is None and kids and not left, "a hung command's kill: its fake Windows grandchild is seen dead: rc=%s alive %s"
          % (rc, left))
    for p in left:
        os.kill(p, 9)
    log = open(os.path.join(d, "worker.log"), encoding="utf-8").read()
    check("-X testq_attempt=%s " % aid in log and "windows children: ended" in log,
          "the log shows the tagged command and the Windows kill: %s" % log[-300:])


def win_exe(name, fallback):
    return shutil.which(name) or (fallback if os.path.exists(fallback) else None)


def real_windows_left(token):
    """-> the pids of live Windows processes whose command line holds token, read apart from the worker's own table
    code; None when the table could not be read."""
    import subprocess
    ps = win_exe("powershell.exe", "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe")
    if not ps:
        return None
    q = ("Get-CimInstance Win32_Process -Filter \"CommandLine like '%%%s%%' and not Name like 'powershell%%'\" | "
         "ForEach-Object { 'PID ' + $_.ProcessId }" % token)
    # budget: danger=a hung powershell (WSL interop) holds the test; longest=2s (one measured run on Archmagi 2026-11-26)
    r = subprocess.run([ps, "-NoProfile", "-NonInteractive", "-Command", q], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        return None
    return [int(x.split()[1]) for x in r.stdout.splitlines() if x.startswith("PID ")]


def real_windows():
    """--real-windows: the same two scenes on this machine's real Windows (python.exe, the real process table and
    taskkill). Exit 0 both grandchildren seen dead, 1 one lived on, 3 could not look (no Windows here)."""
    if not (shutil.which("python.exe") and real_windows_left("rmwintree_probe") is not None):
        print("COULD NOT LOOK: no python.exe or powershell.exe on this host")
        return 3
    for k in ("TESTQ_CMD_WINPS", "TESTQ_CMD_WINKILL"):
        os.environ.pop(k, None)
    token = "rmwintree%d" % os.getpid()
    code = ("import subprocess,sys,time; subprocess.Popen([sys.executable,'-c','import time; time.sleep(100)  # %s']); "
            "time.sleep(100)" % token)
    for n, how in ((1, "stop"), (2, "kill")):
        aid = "J20261126T000000Z-realwn.a%d" % n
        d = os.path.join(HOME, "attempts", aid)
        os.makedirs(d)
        W.S.dump({"phase": "run"}, os.path.join(d, "state.json"))
        a = attempt(aid, d)
        # budget: fixture
        th = threading.Thread(target=lambda: a.sh('python.exe -c "%s"' % code, timeout=90 if how == "stop" else 8))
        th.start()
        seen, t = [], time.time()
        while time.time() - t < 30 and len(seen) < 2:     # the root python.exe and its child
            seen = real_windows_left(token) or []
            time.sleep(0.5)
        if len(seen) < 2:
            print("COULD NOT LOOK: the real Windows python.exe and its child never both showed in the table: %s" % seen)
            return 3
        if how == "stop":
            W.cmd_stop(aid)
        th.join(60)
        time.sleep(2)
        left = real_windows_left(token)
        if left is None:
            print("COULD NOT LOOK: the Windows table could not be read after the %s" % how)
            return 3
        check(not left, "real Windows, %s: the python.exe and its child %s are seen dead: alive %s" % (how, seen, left))
        tk = win_exe("taskkill.exe", "/mnt/c/Windows/System32/taskkill.exe")
        if left and tk:     # leave no test process behind on a red run
            import subprocess
            # budget: danger=a hung taskkill (WSL interop) holds the test; longest=1s (one measured run on Archmagi 2026-11-26)
            subprocess.run([tk, "/F"] + [x for pid in left for x in ("/PID", str(pid))], capture_output=True, timeout=120)
    print("FAILED %d" % len(FAILS) if FAILS else "selftest_steve_worker_windows_tree --real-windows: all passed")
    return 1 if FAILS else 0


def main():
    if "--real-windows" in sys.argv[1:]:
        try:
            return real_windows()
        finally:
            shutil.rmtree(HOME, ignore_errors=True)
    tmp = tempfile.mkdtemp(prefix="testq_wintree_")
    try:
        t_python_exe_carries_the_attempt_tag()
        t_windows_tree_is_the_attempts_own()
        root = fake_windows(tmp)
        t_stop_ends_the_windows_grandchild(tmp, root)    # runs on the base too: there the grandchild lives on
        t_a_killed_command_ends_its_windows_grandchild(tmp, root)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(HOME, ignore_errors=True)
    print("FAILED %d" % len(FAILS) if FAILS else "selftest_steve_worker_windows_tree: all passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
