#!/usr/bin/env python3
"""fake_two_games.py - a machine with RimWorlds on it and no Windows, for the second-game selftests.

Fake games are real Linux processes, so "the other game lives" is a fact about a process, not about a mock. Shims named
powershell.exe, taskkill.exe and tasklist.exe go FIRST on PATH: they list, stop and start only those processes. The
taskkill shim does what the real one does, /IM takes every game, so a site that regresses to killing by name really does
take both. It refuses any pid that is not a fake game, and World() asserts its shims resolve before anything runs: a Linux
pid handed to the real taskkill could name an unrelated Windows process.
"""
import json
import os
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

FAKE_GAME = r'''#!/usr/bin/env python3
# A game: writes its bridge line to -logfile, records the environment it got, sleeps. --ignore-term survives a graceful stop.
import json, os, signal, sys, time
a = sys.argv[1:]
if "--ignore-term" in a:
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
if "-logfile" in a:
    with open(a[a.index("-logfile") + 1].replace("\\", "/"), "w") as f:
        p = os.environ.get("FAKE_GAME_PORT") or os.environ.get("GABP_SERVER_PORT")
        f.write("[RimBridge] %s\n" % (("GABP server connected to GABS on port %s" % p) if p else "Failed to start server"))
for x in a:
    if x.startswith("-savedatafolder="):
        with open(os.path.join(x.split("=", 1)[1], "game_saw.json"), "w") as f:
            json.dump({"argv": a, "port": os.environ.get("GABP_SERVER_PORT"), "token": os.environ.get("GABP_TOKEN")}, f)
time.sleep(600)
'''

SHIM_LIB = r'''
import os, re, signal, subprocess, sys
FAKE = os.environ["FAKE_GAME_SCRIPT"]
def games():
    out = []
    for d in os.listdir("/proc"):
        if d.isdigit():
            try:
                with open("/proc/%s/cmdline" % d, "rb") as f:
                    argv = f.read().decode("utf-8", "replace").split("\0")[:-1]
            except OSError:
                continue
            if len(argv) >= 2 and argv[1] == FAKE:
                out.append((int(d), argv[2:]))
    return sorted(out)
def log(line):
    with open(os.environ["FAKE_KILL_LOG"], "a") as f:
        f.write(line + "\n")
def start_ms(pid):
    with open("/proc/%d/stat" % pid) as f:
        ticks = int(f.read().rsplit(")", 1)[1].split()[19])
    with open("/proc/stat") as f:
        btime = [int(ln.split()[1]) for ln in f if ln.startswith("btime")][0]
    return int((btime + ticks / os.sysconf("SC_CLK_TCK")) * 1000)
'''

POWERSHELL = "#!/usr/bin/env python3\n" + SHIM_LIB + r"""
script = sys.argv[-1]
mode = os.environ.get("FAKE_PS_MODE", "")
log("PS " + script.replace("\n", " "))
if mode == "fail":
    sys.stderr.write("fake powershell: failed\n"); sys.exit(1)
if mode == "silent":
    sys.exit(0)
m = re.search(r"Get-Process -Id (\d+)", script)
if "Filter 'Name=''RimWorldWin64.exe'''" in script or "Filter 'Name=''" in script:
    for pid, argv in games():
        cmd = '' if mode == "unreadable" else ' '.join(['"C:\\Game\\RimWorldWin64.exe"'] + [a for a in argv if a != "--ignore-term"])
        print("%d|%d|%s" % (pid, start_ms(pid), cmd))
    print("GAME-LIST-OK")
elif "Get-NetTCPConnection" in script:
    wanted = re.search(r"LocalPort (\d+)", script).group(1)
    for pid, argv in games():
        if any(a.startswith("-savedatafolder=") for a in argv) == (wanted != "5174"):
            print(pid)
elif "Get-Process steam" in script:
    if not os.environ.get("FAKE_NO_STEAM"):
        print(4242)
elif "Start-Process" in script:
    log("START " + script)
    env = dict(os.environ)
    for k, v in re.findall(r"\$env:(\w+)='([^']*)'", script):
        env[k] = v
    args = re.findall(r"'([^']*)'", script[script.index("-ArgumentList"):]) if "-ArgumentList" in script else []
    subprocess.Popen([sys.executable, FAKE] + args, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, start_new_session=True)
elif m:
    alive = [p for p, _ in games() if p == int(m.group(1))]
    print(os.environ.get("FAKE_PS_PROCESS_REPLY", "PROCESS %d" % alive[0]) if alive else "")
elif "Get-CimInstance Win32_Process -Filter 'ProcessId=" in script:
    print("fake cmdline")
else:
    print(os.environ.get("FAKE_PS_REPLY", ""))
"""

TASKKILL = "#!/usr/bin/env python3\n" + SHIM_LIB + r'''
a = sys.argv[1:]
log("taskkill " + " ".join(a))
sig = signal.SIGKILL if "/F" in a else signal.SIGTERM
live = [p for p, _ in games()]
if "/IM" in a:
    targets = live
elif "/PID" in a:
    want = int(a[a.index("/PID") + 1])
    if want not in live:
        sys.stderr.write("fake taskkill: pid %d is no fake game\n" % want); sys.exit(128)
    targets = [want]
else:
    sys.exit(1)
for p in targets:
    os.kill(p, sig)
'''

CMD = "#!/usr/bin/env python3\n" + SHIM_LIB + r'''
log("cmd " + " ".join(sys.argv[1:]))    # steam:// goes no further than this line
'''

PYTHON_EXE = "#!/bin/sh\necho pong\n"

TASKLIST = "#!/usr/bin/env python3\n" + SHIM_LIB + r'''
live = games()
for p, _ in live:
    print('"RimWorldWin64.exe","%d","Console","1","1,000 K"' % p)
if not live:
    print("INFO: No tasks are running which match the specified criteria.")
'''


class World:
    """One temp machine: shims on PATH, game a's folder, an instances root, a game install with steam_appid.txt."""

    def __init__(self, repo=REPO):
        self.repo = repo
        self.tmp = tempfile.mkdtemp(prefix="fake_two_games_")
        self.bin = os.path.join(self.tmp, "bin")
        os.makedirs(self.bin)
        self.game_script = os.path.join(self.tmp, "fake_game.py")
        with open(self.game_script, "w") as f:
            f.write(FAKE_GAME)
        for name, body in (("powershell.exe", POWERSHELL), ("taskkill.exe", TASKKILL), ("tasklist.exe", TASKLIST),
                           ("cmd.exe", CMD), ("python.exe", PYTHON_EXE)):
            p = os.path.join(self.bin, name)
            with open(p, "w") as f:
                f.write(body)
            os.chmod(p, os.stat(p).st_mode | stat.S_IEXEC)
        self.kill_log = os.path.join(self.tmp, "kills.log")
        self.a_dir = os.path.join(self.tmp, "a_data")
        self.root = os.path.join(self.tmp, "instances")
        self.b_dir = os.path.join(self.root, "b")
        self.steamapps = os.path.join(self.tmp, "steamapps")
        self.game_dir = os.path.join(self.steamapps, "common", "RimWorld")
        os.makedirs(os.path.join(self.a_dir, "Config"))
        os.makedirs(self.game_dir)
        with open(os.path.join(self.game_dir, "steam_appid.txt"), "w") as f:
            f.write("294100")
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith(("GABP_", "RM_GAME_", "RIMFLOW_", "RM_HOST", "WSLENV"))}
        self.env.update(PATH=self.bin + os.pathsep + os.environ["PATH"], RM_INSTANCES_ROOT=self.root,
                        RM_STEAMAPPS=self.steamapps, RM_GAME_USERDATA=self.a_dir, RM_GAME_LOGDIR=self.a_dir,
                        FAKE_GAME_SCRIPT=self.game_script, FAKE_KILL_LOG=self.kill_log, PYTHONDONTWRITEBYTECODE="1",
                        RM_DATA_ROOT=os.path.join(self.tmp, "data"))
        for tool in ("powershell.exe", "taskkill.exe", "tasklist.exe", "cmd.exe", "python.exe"):
            found = shutil.which(tool, path=self.env["PATH"])
            assert found and found.startswith(self.bin), "the %s shim does not resolve first: %s" % (tool, found)
        self.children = []

    def start(self, *args):
        p = subprocess.Popen([sys.executable, self.game_script] + list(args), stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.children.append(p)
        for _ in range(100):      # the shim lists /proc: wait until the fake game is really there
            if alive(p.pid):
                return p.pid
            time.sleep(0.02)
        raise AssertionError("fake game did not start")

    def start_a(self):
        return self.start("-disable-compute-shaders")

    def start_b(self):
        os.makedirs(self.b_dir, exist_ok=True)
        return self.start("-savedatafolder=" + self.b_dir)

    def run(self, argv, instance=None, timeout=60, cwd=None, **extra):
        env = dict(self.env, **extra)
        if instance:
            env["RM_GAME_INSTANCE"] = instance
        return subprocess.run(argv, env=env, capture_output=True, text=True, timeout=timeout, cwd=cwd or self.tmp,
                              stdin=subprocess.DEVNULL)

    def gi(self, *args, instance=None, **extra):
        return self.run([sys.executable, os.path.join(self.repo, "src/RimMandrake/Utils/game_instance.py")] + list(args),
                        instance=instance, **extra)

    def py(self, code, instance=None, **extra):
        """Run code with Utils and rimflow importable -> CompletedProcess; the code's last stdout line is its answer."""
        head = ("import sys; sys.path[:0] = [%r, %r, %r]\n"
                % (os.path.join(self.repo, "src/RimMandrake/Utils"), os.path.join(self.repo, "src/RimMandrake/rimflow"),
                   os.path.join(self.repo, "src/RimMandrake")))
        return self.run([sys.executable, "-c", head + code], instance=instance, **extra)

    def kills(self):
        try:
            with open(self.kill_log) as f:
                return [ln.strip() for ln in f if ln.startswith("taskkill")]
        except OSError:
            return []

    def log_lines(self, prefix):
        try:
            with open(self.kill_log) as f:
                return [ln.strip() for ln in f if ln.startswith(prefix)]
        except OSError:
            return []

    def clear(self):
        """Every fake game down, by pid, whoever started it; the kill log emptied."""
        for pid in list_fakes(self.game_script):
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
        for p in self.children:
            p.wait(timeout=10)
        self.children = []
        for _ in range(200):
            if not list_fakes(self.game_script):
                break
            time.sleep(0.02)
        if os.path.exists(self.kill_log):
            os.remove(self.kill_log)

    def saw(self):
        with open(os.path.join(self.b_dir, "game_saw.json")) as f:
            return json.load(f)

    def close(self):
        self.clear()
        shutil.rmtree(self.tmp, ignore_errors=True)


def alive(pid):
    """A live process; a zombie's /proc/<pid>/cmdline reads empty."""
    try:
        with open("/proc/%d/cmdline" % pid, "rb") as f:
            return bool(f.read())
    except OSError:
        return False


def wait_dead(pid, s=5.0):
    t0 = time.time()
    while alive(pid) and time.time() - t0 < s:
        time.sleep(0.02)
    return not alive(pid)


def list_fakes(script):
    out = []
    for d in os.listdir("/proc"):
        if d.isdigit():
            try:
                with open("/proc/%s/cmdline" % d, "rb") as f:
                    argv = f.read().split(b"\0")
            except OSError:
                continue
            if len(argv) >= 2 and argv[1].decode("utf-8", "replace") == script:
                out.append(int(d))
    return out
