#!/usr/bin/env python3
"""selftest_game_lock.py - the promises of design/specs/2026-11-21-one-game-lock/boundary.md, one test each.

Every case runs the real `game_lock.py` (and, for the doors, the real `rimflow` cli) against throwaway locks:
RIMFLOW_DRIVER_LOCK names game a's, RM_INSTANCES_ROOT holds game b's, RIMFLOW_LEDGER a throwaway ledger and
RM_CONTROL_DB a throwaway control store. Holders are real sleeping processes, named with RM_DRIVER_PID.
The query speed check uses the same throwaway state as the other cases.
"""
import atexit
from collections import Counter
import json
import os
import select
import shutil
import signal
import statistics
import subprocess
import sys
import tempfile
import time

TMP = tempfile.mkdtemp(prefix="st_game_lock_")
atexit.register(shutil.rmtree, TMP, True)
os.environ["TMPDIR"] = TMP
# The caller's game is not the test's: a detached game-b helper carries RM_GAME_INSTANCE=b and its live hold, and the
# in-process checks (os.environ.update(bx.env) adds, never removes) then read game b and fail; ./publish refused it
# (GSS in-game visit 3, 2026-11-21: 3 FAIL with RM_GAME_INSTANCE=b, 0 without).
for _k in ("RM_GAME_INSTANCE", "RM_GAME_USERDATA", "RM_GAME_LOGDIR", "RM_HOST_GUARD_GEN", "RM_DRIVER_PID", "RM_ROLE_UNIT",
           "GABP_SERVER_PORT", "GABP_TOKEN"):
    os.environ.pop(_k, None)
HERE = os.path.dirname(os.path.abspath(__file__))
GL = os.path.join(HERE, "game_lock.py")
CLI = os.path.join(HERE, "cli.py")
HG = os.path.join(HERE, "host_guard.py")
sys.path.insert(0, HERE)
FAILS = []
SLEEPERS = []


def check(cond, msg, detail=""):
    print(("ok   " if cond else "FAIL ") + msg + ("" if cond else "  %s" % (detail,))[:900])
    if not cond:
        FAILS.append(msg)
    return bool(cond)


class Box:
    """One throwaway world: game a's lock, game b's lock, a ledger, a control store."""
    n = 0

    def __init__(self):
        Box.n += 1
        self.d = os.path.join(TMP, "box%d" % Box.n)
        os.makedirs(os.path.join(self.d, "items"))
        os.makedirs(os.path.join(self.d, "instances", "b"))
        self.a = os.path.join(self.d, "DRIVER_LOCK.json")
        self.b = os.path.join(self.d, "instances", "b", "DRIVER_LOCK.json")
        keep = {k: v for k, v in os.environ.items() if k not in (
            "RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "RIMFLOW_BRIDGE_SEAT", "RM_GAME_INSTANCE",
            "RM_HOST_GUARD_GEN", "RM_DRIVER_PID", "RM_ROLE_UNIT", "MATURATION_BRIDGE_IDLE")}
        keep.update(RIMFLOW_DRIVER_LOCK=self.a, RM_INSTANCES_ROOT=os.path.join(self.d, "instances"),
                    RIMFLOW_LEDGER=os.path.join(self.d, "events.jsonl"), RIMFLOW_ITEMS=os.path.join(self.d, "items"),
                    RM_CONTROL_DB=os.path.join(self.d, "control.db"), 
                    RIMFLOW_OWNER_ACT_STAMP=os.path.join(self.d, "stamp.json"), RIMFLOW_PROBE="no-reading",
                    RIMFLOW_BRIDGE_LOCK=os.path.join(self.d, "bridge.lock"), RIMFLOW_SEAT="BENCH",
                    RM_HOST="archmagi")
        self.env = keep

    def gl(self, *args, pid=None, timeout=60, **env):
        e = dict(self.env, **env)
        if pid:
            e["RM_DRIVER_PID"] = str(pid)
        return subprocess.run([sys.executable, GL] + list(args), env=e, capture_output=True, text=True,
                              timeout=timeout)

    def rf(self, *args, pid=None, **env):
        e = dict(self.env, **env)
        if pid:
            e["RM_DRIVER_PID"] = str(pid)
        return subprocess.run([sys.executable, CLI] + list(args), env=e, capture_output=True, text=True, timeout=180)

    def lock(self, path=None):
        try:
            with open(path or self.a, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return None


def sleeper():
    p = subprocess.Popen(["sleep", "300"])
    SLEEPERS.append(p)
    time.sleep(0.05)
    return p


def ident_of(pid):
    import driver_lock as D
    return {"pid": pid, "start": D._proc_start(pid), "boot_id": D.current_boot_id(), "platform": "wsl",
            "host": __import__("socket").gethostname()}


def write_lock(path, seat, pid, purpose="planted", ago=0):
    t = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - ago))
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"seat": seat, "purpose": purpose, "identity": ident_of(pid), "acquired": t, "heartbeat": t,
                   "generation": 7}, f)


def kill(p):
    p.kill()
    p.wait()


# --- promises -----------------------------------------------------------------------------------------------------
def t_one_record_per_game():
    bx = Box()
    s = sleeper()
    r = bx.gl("claim", "b", "--for", "only b", pid=s.pid)
    check(r.returncode == 0, "claim b: exit 0", r.stdout + r.stderr)
    check(bx.lock(bx.b) and bx.lock(bx.b)["purpose"] == "only b" and bx.lock(bx.a) is None,
          "claim b writes game b's lock and nothing else", (bx.lock(bx.a), bx.lock(bx.b)))
    check(not os.path.exists(bx.env["RIMFLOW_LEDGER"]) and not os.path.isdir(os.path.join(bx.d, "events")),
          "a claim writes no ledger event (the ledger is history, written by the rimflow door)")
    q = bx.gl("query", "a")
    check(q.returncode == 0 and "ArchBig: FREE" in q.stdout, "game a reads FREE beside a held game b", q.stdout)
    kill(s)


def t_two_claimers_race_and_exactly_one_wins():
    bx = Box()
    holders = [sleeper() for _ in range(6)]
    procs = [subprocess.Popen([sys.executable, GL, "claim", "a", "--for", "racer %d" % i],
                              env=dict(bx.env, RM_DRIVER_PID=str(h.pid)), stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True) for i, h in enumerate(holders)]
    codes = [p.wait(timeout=120) for p in procs]
    outs = [p.stdout.read() for p in procs]
    check(codes.count(0) == 1 and codes.count(75) == 5, "six racers: exactly one wins (0), five read held (75)",
          (codes, outs))
    won = bx.lock()
    winner = [i for i, c in enumerate(codes) if c == 0]
    check(won and winner and won["purpose"] == "racer %d" % winner[0], "the lock names the one winner", won)
    for h in holders:
        kill(h)


def t_a_dead_holder_reads_free_at_once():
    bx = Box()
    s = sleeper()
    bx.gl("claim", "a", "--for", "will die", pid=s.pid)
    q = bx.gl("query", "a")
    check(q.returncode == 75 and "HELD by BENCH" in q.stdout, "a live holder reads HELD (75)", q.stdout)
    kill(s)
    t0 = time.time()
    q = bx.gl("query", "a", "--json")
    d = json.loads(q.stdout)
    check(q.returncode == 0 and d["state"] == "FREE" and "gone" in d.get("note", ""),
          "the moment its process is gone, the game reads FREE (0), naming the gone holder", q.stdout)
    s2 = sleeper()
    r = bx.gl("claim", "a", "--for", "next", pid=s2.pid)
    check(r.returncode == 0 and "broke a dead" in r.stdout, "the next claim takes it at once, no --force", r.stdout)
    check(time.time() - t0 < 30, "no 45-minute wait")
    kill(s2)


def t_an_unreadable_lock_is_could_not_look():
    bx = Box()
    with open(bx.a, "w") as f:
        f.write("{not json")
    old = time.time() - 60
    os.utime(bx.a, (old, old))
    for verb in (["query", "a"], ["claim", "a", "--for", "x"], ["release", "a"]):
        r = bx.gl(*verb)
        check(r.returncode == 2 and "COULD NOT LOOK" in r.stdout, "%s on a garbled lock: exit 2, COULD NOT LOOK"
              % verb[0], r.stdout + r.stderr)
    q = bx.gl("query", "all")
    check(q.returncode == 2, "query all with one game unreadable: exit 2", q.stdout)
    open(bx.a, "w").close()
    r = bx.gl("query", "a")
    # A child scheduled after the write grace sees an old empty file. Both readings must name the unreadable lock.
    check(r.returncode == 2 and "is UNREADABLE" in r.stdout, "an empty lock that stays empty: exit 2", r.stdout)
    os.remove(bx.a)
    r = bx.gl("query", "a", RIMFLOW_DRIVER_LOCK="")
    check(r.returncode == 2 and "no lock path" in r.stdout, "no lock path at all: exit 2, never free", r.stdout)
    import game_lock
    d = os.path.join(TMP, "ctl_dir_not_db")
    os.makedirs(d, exist_ok=True)
    r = bx.gl("query", "a", RM_CONTROL_DB=d)
    check(r.returncode == 2 and "control store could not be read" in r.stdout,
          "a control store that cannot be read: exit 2, his pipe hold not ruled out", r.stdout)
    check(game_lock.EX_BLIND == 2, "the exit code for could not look is 2")


def t_run_releases_on_exit_crash_and_sigterm():
    bx = Box()
    r = bx.gl("run", "a", "--for", "exit 7", "--", sys.executable, "-c", "import sys; sys.exit(7)")
    check(r.returncode == 7 and bx.lock() is None, "run: CMD's exit code comes back, the lock is gone",
          (r.returncode, r.stderr))
    r = bx.gl("run", "a", "--for", "crash", "--", sys.executable, "-c", "import os; os.abort()")
    check(r.returncode == 134 and bx.lock() is None, "run: a crash (SIGABRT) returns 134, the lock is gone",
          (r.returncode, r.stderr))
    child_probe = ("import subprocess,sys,json; r=subprocess.run([sys.executable,%r,'query','a','--json'],"
                   "capture_output=True,text=True); d=json.loads(r.stdout); sys.exit(0 if d.get('mine') else 9)" % GL)
    r = bx.gl("run", "a", "--for", "probe", "--", sys.executable, "-c", child_probe)
    check(r.returncode == 0, "run: a child reads the hold as its own process tree's", r.stderr)
    # Deliver the real signal at both startup boundaries. The stand-in CMD has no scheduler race of its own.
    startup_term = """
import os, signal, sys
import game_lock as G

class Child:
    def __init__(self):
        self.code = 7

    def poll(self):
        return None

    def send_signal(self, sig):
        self.code = -sig

    def wait(self):
        return self.code

claim = G.claim
def claim_and_signal(*args, **kwargs):
    result = claim(*args, **kwargs)
    os.kill(os.getpid(), signal.SIGTERM)
    return result

def spawn(*args, **kwargs):
    if sys.argv[1] == 'spawning CMD':
        os.kill(os.getpid(), signal.SIGTERM)
    return Child()

if sys.argv[1] == 'after claim':
    G.claim = claim_and_signal
G.subprocess.Popen = spawn
sys.exit(G.run('a', 'startup SIGTERM', ['fixture CMD']))
"""
    for when in ("after claim", "spawning CMD"):
        fixture = Box()
        r = subprocess.run([sys.executable, "-c", startup_term, when], cwd=HERE, env=fixture.env,
                           capture_output=True, text=True, timeout=60)
        check(r.returncode == 143 and fixture.lock() is None,
              "run: SIGTERM %s reaches CMD (143) and releases the lock" % when,
              (r.returncode, fixture.lock() is not None, r.stderr))
    # CMD announces readiness and waits for EOF, including when SIGKILL leaves it orphaned.
    ready_cmd = [sys.executable, "-c", "import sys; print('ready', flush=True); sys.stdin.read()"]
    for sig in (signal.SIGTERM, signal.SIGKILL):
        with subprocess.Popen([sys.executable, GL, "run", "a", "--for", sig.name, "--", *ready_cmd],
                              env=bx.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True) as p:
            try:
                ready, _, _ = select.select([p.stdout], [], [], 30)  # same hang guard as the signal wait
                if not check(ready and p.stdout.readline().strip() == "ready", "run: CMD ready for %s" % sig.name):
                    continue
                held = bx.gl("query", "a")
                p.send_signal(sig)
                rc = p.wait(timeout=30)
                if sig == signal.SIGTERM:
                    check(held.returncode == 75 and rc == 143 and bx.lock() is None,
                          "run: SIGTERM is forwarded, CMD ends (143), the lock is released",
                          (held.stdout, rc, bx.lock()))
                else:
                    q = bx.gl("query", "a")
                    check(held.returncode == 75 and rc == -sig and q.returncode == 0 and "FREE" in q.stdout,
                          "run killed outright (SIGKILL): the game reads FREE at once", (held.stdout, rc, q.stdout))
            finally:
                if p.poll() is None:
                    p.kill()


def t_his_hold_refuses_with_exit_3():
    bx = Box()
    import control as C
    C.init(bx.env["RM_CONTROL_DB"])
    C.switch("game:a", True, "his walk on game a", p=bx.env["RM_CONTROL_DB"])
    for verb in (["query", "a"], ["claim", "a", "--for", "x"]):
        r = bx.gl(*verb)
        check(r.returncode == 3 and "pipe off game:ArchBig" in r.stdout, "pipe off game:a: %s exits 3 naming it" % verb[0],
              r.stdout + r.stderr)
    r = bx.gl("query", "b")
    check(r.returncode == 0, "pipe off game:a leaves game b free", r.stdout)
    s = sleeper()
    args = ("claim", "ArchBig", "--for", "staging", "--despite-hold")
    r = bx.gl(*args, "", pid=s.pid)
    check(r.returncode == 3 and bx.lock() is None, "an empty --despite-hold reason leaves the claim refused",
          r.stdout + r.stderr)
    r = bx.gl(*args, "why", pid=s.pid)
    check(r.returncode == 0 and "acting anyway: why" in r.stderr,
          "claim ArchBig --despite-hold why exits 0 and records why", r.stdout + r.stderr)
    q = bx.gl("query", "ArchBig", "--json")
    d = json.loads(q.stdout)
    check(q.returncode == 3 and d.get("seat") == "BENCH" and (d.get("holder") or {}).get("pid") == s.pid
          and "his walk on game a" in d.get("pipe_hold", ""),
          "query names the driver while the pipe hold stays set", q.stdout)
    d_lock = bx.lock()
    r = bx.gl(*args, "why")
    check(r.returncode == 75 and bx.lock() == d_lock, "--despite-hold leaves another live driver's lock alone",
          r.stdout + r.stderr)
    write_lock(bx.a, "OWNER", s.pid, "his walk")
    owner_lock = bx.lock()
    r = bx.gl(*args, "why")
    check(r.returncode == 3 and "OWNER" in r.stdout and bx.lock() == owner_lock,
          "--despite-hold leaves his OWNER lock alone", r.stdout + r.stderr)
    r = bx.gl(*args, "why", RM_CONTROL_DB=bx.d)
    check(r.returncode == 2 and "COULD NOT LOOK" in r.stdout, "--despite-hold needs a readable control store",
          r.stdout + r.stderr)
    write_lock(bx.b, "OWNER", s.pid, "his walk")
    for verb in (["query", "b"], ["claim", "b", "--for", "x"]):
        r = bx.gl(*verb)
        check(r.returncode == 3 and "HIS HOLD" in r.stdout, "his live OWNER lock: %s exits 3" % verb[0],
              r.stdout + r.stderr)
    kill(s)
    r = bx.gl("query", "b")
    check(r.returncode == 3 and "takeability not measured" in r.stdout,
          "his OWNER lock with its process gone is still his hold to a query (his rule is not measured here)",
          r.stdout)
    os.remove(bx.b)
    for purpose, flags in (("fly the hawk over the dunes", []), ("staging", ["--flyer"])):
        r = bx.gl("claim", "b", "--for", purpose, *flags)
        check(r.returncode == 3 and "flight" in r.stdout, "a flyer's flight (%s): claim exits 3" % (flags or purpose),
              r.stdout)
    s = sleeper()
    r = bx.gl("claim", "b", "--for", "flyer flight with him", "--seat", "OWNER", "--flyer", pid=s.pid)
    check(r.returncode == 0, "his own claim for a flight passes", r.stdout + r.stderr)
    kill(s)


def t_an_old_style_hold_is_seen_and_an_old_style_release_frees_it():
    bx = Box()
    s = sleeper()
    ident = json.dumps(ident_of(s.pid))
    r = subprocess.run([sys.executable, HG, "take", "--seat", "BENCH", "--for", "old take", "--identity-json", ident],
                       env=bx.env, capture_output=True, text=True, timeout=60)
    check(r.returncode == 0, "host_guard.py take (an old door) takes", r.stdout + r.stderr)
    q = bx.gl("query", "a", "--json")
    d = json.loads(q.stdout)
    check(q.returncode == 75 and d["purpose"] == "old take", "game_lock sees the old-style hold", q.stdout)
    r = subprocess.run([sys.executable, HG, "release", "--seat", "BENCH", "--identity-json", ident],
                       env=bx.env, capture_output=True, text=True, timeout=60)
    q = bx.gl("query", "a")
    check(r.returncode == 0 and q.returncode == 0 and "FREE" in q.stdout, "an old-style release frees it",
          r.stdout + q.stdout)
    import driver_lock as D
    got = D.acquire(bx.a, "BENCH", "rimflow bridge take's own call", ident_of(s.pid))
    q = bx.gl("query", "a")
    check(got["ok"] and q.returncode == 75 and "rimflow bridge take's own call" in q.stdout,
          "a take through driver_lock.acquire (rimflow bridge take's call) is seen", q.stdout)
    st = subprocess.run([sys.executable, HG, "status"], env=bx.env, capture_output=True, text=True, timeout=60)
    check("HELD" in st.stdout, "and host_guard.py status (the old reader) reads the same record", st.stdout)
    kill(s)


def t_release_frees_only_this_process_trees_hold():
    bx = Box()
    s = sleeper()
    bx.gl("claim", "a", "--for", "someone else", pid=s.pid)
    r = bx.gl("release", "a")
    check(r.returncode == 75 and bx.lock() is not None, "release of another tree's live hold: 75, lock untouched",
          r.stdout)
    r = bx.gl("release", "a", "--force", "test cut")
    check(r.returncode == 0 and bx.lock() is None, "--force cuts it (recorded on the act)", r.stdout + r.stderr)
    kill(s)
    r = bx.gl("claim", "a", "--for", "mine", pid=os.getpid())
    check(r.returncode == 0, "claim for this test process", r.stdout)
    r = bx.gl("release", "a")
    check(r.returncode == 0 and "RELEASED" in r.stdout and bx.lock() is None,
          "a child of the holder releases the tree's hold", r.stdout)
    r = bx.gl("release", "a")
    check(r.returncode == 0 and "already FREE" in r.stdout, "release of a free game: 0, already FREE", r.stdout)


# Run the CLI entry point in a fresh interpreter and count work from its first import.
_QUERY_WORK = r"""
import os
import sys
import time

script, sources, helper = sys.argv[1:]
sys.argv = [script, "query", "a"]
sys.path[0] = os.path.dirname(script)
sys.path.insert(0, os.path.join(sources, "Utils"))
with open(script, "rb") as f:
    code = compile(f.read(), script, "exec")
loaded = set(sys.modules)
calls, reads = [], []
lines = 0

def audit(event, args):
    if event in ("subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.fork", "os.forkpty", "socket.connect"):
        calls.append(event)
        raise RuntimeError("unexpected query operation: " + event)
    if event in ("open", "os.listdir", "os.scandir", "sqlite3.connect"):
        if not sys._getframe(1).f_code.co_filename.startswith("<frozen importlib."):
            reads.append(os.fsdecode(args[0]) if isinstance(args[0], (str, bytes)) else str(args[0]))

def profile(frame, event, func):
    if event == "c_call" and func is time.sleep:
        calls.append("time.sleep")
        raise RuntimeError("unexpected query operation: time.sleep")

def trace(frame, event, arg):
    global lines
    if event == "call":
        return trace if frame.f_code.co_filename.startswith(sources) else None
    if event == "line":
        lines += 1
    return trace

sys.addaudithook(audit)
sys.setprofile(profile)
sys.settrace(trace)
try:
    if helper:
        import rmpaths
        rmpaths.AGENT_STORAGE = helper
    exec(code, {"__name__": "__main__", "__file__": script})
finally:
    sys.settrace(None)
    sys.setprofile(None)
    imports = sorted(set(sys.modules) - loaded)
    import json
    print("QUERY_WORK " + json.dumps(dict(imports=imports, calls=calls, reads=reads, lines=lines)), file=sys.stderr)
"""

# Observed on Archmagi on 2026-11-24 with Python 3.12 and 3.14. Only these imports may run in a fresh query.
_QUERY_IMPORTS = set("""
__future__ _collections _contextvars _datetime _functools _heapq _json _locale _operator _posixsubprocess
_py_warnings _socket _sqlite3 _sre _strptime _types _weakrefset array calendar collections contextlib control
collections.abc copyreg datetime difflib driver_lock enum errno fcntl fnmatch functools game_names glob grp
heapq io ipaddress itertools json json.decoder json.encoder json.scanner keyword locale math ntpath operator
pathlib pathlib._os probe_result pwd re re._casefix re._compiler re._constants re._parser reprlib rmpaths
select selectors signal socket sqlite3 sqlite3.dbapi2 subprocess threading types urllib urllib.parse warnings
""".split())
# The high-water mark was 771 repository line events on 2026-11-24. Allow roughly 10% for small code changes.
_QUERY_LINES = 850


def _check_query_work(env, cases):
    issues = []
    worst = 0
    for name, expected, case_env, helper, allowed in cases:
        case_env = dict(env, **case_env)
        if helper:
            del case_env["RM_DATA_ROOT"]  # exercise a warm cache hit with the normal resolver
        r = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", _QUERY_WORK, GL, os.path.dirname(HERE) + os.sep, helper],
                           env=case_env, capture_output=True, text=True, timeout=60)
        report = next((line.removeprefix("QUERY_WORK ") for line in r.stderr.splitlines()
                       if line.startswith("QUERY_WORK ")), "")
        try:
            work = json.loads(report)
        except ValueError:
            issues.append("%s: missing work report (%s)" % (name, r.stderr[-300:]))
            continue
        worst = max(worst, work["lines"])
        extra_imports = set(work["imports"]) - _QUERY_IMPORTS
        extra_reads = Counter(work["reads"]) - allowed
        if extra_imports:
            issues.append("%s imports %s" % (name, ", ".join(sorted(extra_imports))))
        if extra_reads:
            issues.append("%s extra reads %s" % (name, ", ".join(sorted(extra_reads))))
        if work["calls"]:
            issues.append("%s calls %s" % (name, ", ".join(sorted(set(work["calls"])))))
        if r.returncode != expected:
            issues.append("%s exit %d, expected %d" % (name, r.returncode, expected))
    return check(not issues and worst <= _QUERY_LINES,
                 "query work (worst %d line events, limit %d, %d cases)" % (worst, _QUERY_LINES, len(cases)),
                 ", ".join(issues))


def _measure_query_wall(bx, env):
    # One batch of nine and the half-cores threshold come from the 2026-11-21 boundary and Windows precedent.
    # A bare interpreter's 30 ms wall ceiling is twice the 15 ms CPU upper reading on Archmagi (2026-11-24).
    # It detects contention that the guest load can miss without judging the query by its own CPU or wall ratio.
    cores = len(os.sched_getaffinity(0))
    load = os.getloadavg()[0]
    if load > cores / 2:
        print("     UNMEASURED: query's 100 ms wall bound (load %.1f on %d cores)" % (load, cores))
        return

    startup, query, answers = [], [], []
    for _ in range(9):
        t0 = time.perf_counter()
        subprocess.run([sys.executable, "-c", "pass"], env=env, capture_output=True, timeout=60, check=True)
        startup.append((time.perf_counter() - t0) * 1000)
        t0 = time.perf_counter()
        r = bx.gl("query", "a", **env)
        query.append((time.perf_counter() - t0) * 1000)
        answers.append(r.returncode)
    check(all(code == 75 for code in answers), "the timed queries report the held lock", answers)
    load = max(load, os.getloadavg()[0])
    baseline = statistics.median(startup)
    if load > cores / 2 or baseline > 30:
        print("     UNMEASURED: query's 100 ms wall bound (bare Python median %.1f ms, load %.1f on %d cores)"
              % (baseline, load, cores))
        return
    med = statistics.median(query)
    check(med < 100, "query wall time on a throwaway held lock and control store (median %.1f ms, "
          "worst %.1f ms, limit 100 ms, %d cases, bare Python median %.1f ms)"
          % (med, max(query), len(query), baseline))


def t_a_query_answers_under_100_ms():
    import control
    import socket

    bx = Box()
    lodestar = os.path.join(bx.d, "Lodestar")
    os.makedirs(lodestar)
    machines = os.path.join(lodestar, "machines.md")
    open(machines, "w").close()
    helper = os.path.join(lodestar, "agent_storage.py")
    with open(helper, "w", encoding="utf-8") as f:
        f.write("print(%r)\n" % bx.d)
    cache = os.path.join(bx.d, "root-cache.json")
    env = dict(bx.env, RM_DATA_ROOT=bx.d, LODESTAR_ROOT=lodestar, RM_PATHS_CACHE=cache)
    # Seed the resolver's cache from fixture files so a broken cache would call only the fixture helper.
    st = os.stat(machines)
    key = [socket.gethostname(), env.get("AGENT_STORAGE_ROOT", "").strip(), env.get("LODESTAR_MACHINE", ""),
           lodestar, helper, [st.st_size, st.st_mtime_ns]]
    with open(cache, "w", encoding="utf-8") as f:
        json.dump({"key": key, "root": bx.d}, f)

    control.init(env["RM_CONTROL_DB"])
    holder = sleeper()
    try:
        env["RM_DRIVER_PID"] = str(holder.pid)
        write_lock(bx.a, "BENCH", holder.pid)
        free_lock = os.path.join(bx.d, "free.json")
        pipe_db = os.path.join(bx.d, "pipe.db")
        control.init(pipe_db)
        control.switch("game:a", True, "query work fixture", p=pipe_db)
        # Per-path maxima measured on 2026-11-24. A free lock also reads its generation file. A held lock
        # inspects the holder's start and boot. Both states consult the fixture control store once.
        free = Counter([free_lock, free_lock + ".gen", env["RM_CONTROL_DB"], cache])
        holder_reads = Counter({bx.a: 1, "/proc/%d/stat" % holder.pid: 3, "/proc/sys/kernel/random/boot_id": 6})
        cases = (
            ("cached free", 0, {"RIMFLOW_DRIVER_LOCK": free_lock}, helper, free),
            ("held", 75, {}, "", holder_reads + Counter([env["RM_CONTROL_DB"]])),
            ("pipe hold", 3, {"RM_CONTROL_DB": pipe_db}, "", holder_reads + Counter([pipe_db])),
        )
        if _check_query_work(env, cases):
            _measure_query_wall(bx, env)
    finally:
        kill(holder)


# --- the four disagreements of 2026-11-21, one test each ----------------------------------------------------------
def t_the_225_am_release_that_left_bridge_who_saying_held():
    """2:25 AM: the visit run ended; this clone's ledger still had its take, so `bridge who` read "held by BENCH" and
    the next run waited. Now who and take read the lock: its holder process is gone, so the game is free."""
    bx = Box()
    s = sleeper()
    r = bx.rf("bridge", "take", "--for", "Pyrelands visit", pid=s.pid)
    check(r.returncode == 0, "the fixture take lands", r.stdout + r.stderr)
    kill(s)                                       # the run ends: no release event is ever written
    r = bx.rf("bridge", "who")
    check(r.returncode == 0 and "bridge FREE" in r.stdout and "held by" not in r.stdout,
          "bridge who reads FREE from the lock, not the ledger's stale take", r.stdout + r.stderr)
    s2 = sleeper()                                 # another seat: the ledger's fresh BENCH take would refuse it
    # (an unreadable control store DOES stop a take since 34d860f96a: COULD NOT LOOK, selftest_bridge_take_pipe_hold)
    r = bx.rf("bridge", "take", "--for", "Gimme Some Slack visit", pid=s2.pid, RIMFLOW_SEAT="FOUNDRY")
    check(r.returncode == 0 and bx.lock()["purpose"] == "Gimme Some Slack visit",
          "the next take, by another seat, succeeds without --force or a hand release (the ledger's stale take "
          "does not stop it)", r.stdout + r.stderr)
    s3 = sleeper()
    r = bx.rf("bridge", "idle", "--for", "a third run", pid=s3.pid)
    check(r.returncode == 1 and "Gimme Some Slack visit" in r.stdout,
          "and `bridge idle` reads the new live holder from the lock", r.stdout + r.stderr)
    kill(s2)
    kill(s3)


def t_the_243_am_game_b_record_that_named_the_ended_run():
    """2:43 AM: game b's bridge record named the pit-trap run that had ended an hour before, while the guard named the
    new test pilot. Now `bridge who --host archmagi.b` prints game b's lock and nothing else."""
    bx = Box()
    s = sleeper()
    r = bx.rf("bridge", "take", "--host", "archmagi.b", "--for", "pit-trap run", pid=s.pid)
    check(r.returncode == 0, "the pit-trap run takes game b", r.stdout + r.stderr)
    kill(s)
    s2 = sleeper()
    r = bx.gl("claim", "b", "--for", "test pilot", pid=s2.pid)
    check(r.returncode == 0, "the test pilot claims game b", r.stdout)
    r = bx.rf("bridge", "who", "--host", "archmagi.b")
    out = r.stdout + r.stderr
    check(r.returncode == 0 and "test pilot" in out and "pit-trap" not in out,
          "bridge who for game b names the live test pilot, never the ended run", out)
    kill(s2)


def t_the_335_am_ledger_free_while_the_lock_was_held():
    """3:35 AM: the BRIDGE glance file (now retired) and this clone's ledger read FREE while another clone's visit held the driver lock.
    Now `bridge who` reads the lock, so a hold made from any clone is seen at once."""
    bx = Box()
    s = sleeper()
    write_lock(bx.a, "BENCH", s.pid, "Gimme Some Slack visit (another clone)")
    r = bx.rf("bridge", "who")
    check(r.returncode == 0 and "Gimme Some Slack visit (another clone)" in r.stdout and "bridge held by BENCH"
          in r.stdout and "FREE" not in r.stdout, "bridge who reads HELD from the lock while this ledger is empty",
          r.stdout + r.stderr)
    check(not os.path.exists(os.path.join(bx.d, "BRIDGE")), "no BRIDGE glance file is written (retired; the lock is read)")
    s2 = sleeper()
    r = bx.rf("bridge", "take", "--for", "a third run", pid=s2.pid)
    check(r.returncode == 75 and "Gimme Some Slack" in r.stderr, "a take from this clone is refused by the lock (75)",
          r.stdout + r.stderr)
    r = bx.rf("bridge", "release", pid=s2.pid)
    check(r.returncode == 75 and bx.lock() is not None, "a release from this clone frees nothing and says why (75)",
          r.stdout + r.stderr)
    kill(s)
    kill(s2)


def t_the_tick_line_that_named_a_dead_run_as_live():
    """The tick's status line named a dead run as live on FlowWorks and on Gimme Some Slack. Now its words about a game
    carry the lock, read at the moment they are written, and its free-game reading is the lock's."""
    import maturation_dispatch as MD
    import maturation as M
    bx = Box()
    saved = dict(os.environ)
    try:
        os.environ.update(bx.env)
        os.environ.pop("MATURATION_BRIDGE_IDLE", None)
        _g, whys = MD.pick_game({"game_instances": ["a"]}, lambda p, game="a": (True, "TAKEABLE"), "visit",
                                held={"a": "rm-role-dead-run"})
        check(whys and "the lock now: %s: FREE" % MD._GN.show("a") in whys[0],
              "a game a run record names is shown with the lock's reading of now", whys)
        s = sleeper()
        write_lock(bx.a, "BENCH", s.pid, "a live visit")
        go, why = M.bridge_idle("visit", game="a")
        check(not go and "a live visit" in why, "the tick's free-game reading is the lock's: held", why)
        kill(s)
        go, why = M.bridge_idle("visit", game="a")
        check(go and "FREE" in why, "its holder gone, the tick reads game a free at once", why)
        go, why = M.bridge_idle("fly the hawk", game="a")
        check(not go and "flyer" in why, "a flyer's flight is never a free game for the tick", why)
    finally:
        os.environ.clear()
        os.environ.update(saved)


def t_the_old_shared_file_is_neither_written_nor_read():
    """Every other reader of game a's holder reads the lock (model.game_a_lock_record); a take or a release writes no
    BRIDGE_SHARED.json, and a planted one names no holder anywhere."""
    bx = Box()
    planted = os.path.join(bx.d, "BRIDGE_SHARED.json")
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rec = {"holder": "FOUNDRY", "since": now, "touched": now, "purpose": "a planted old record", "clone": bx.d}
    with open(planted, "w") as f:
        json.dump(rec, f)
    s = sleeper()
    r = bx.rf("bridge", "take", "--for", "readers see it", pid=s.pid, RM_ROLE_UNIT="rm-detached-x-1",
              RIMFLOW_SHARED_BRIDGE=planted)
    check(r.returncode == 0, "a take through rimflow", r.stdout + r.stderr)
    with open(planted) as f:
        check(json.load(f) == rec, "the take wrote nothing over the planted old file")
    probe = ("import sys, json; sys.path[:0] = [%r, %r, %r]\n"
             "from rimflow import model as M, seat_restart as SR, wrapup as W\n"
             "import testq\n"
             "rec = M.game_a_lock_record() or {}\n"
             "print(json.dumps({'rec': [rec.get('holder'), rec.get('role_unit'), rec.get('clone')],\n"
             " 'gate_bench': M.bridge_gate('BENCH'), 'gate_foundry': M.bridge_gate('FOUNDRY'),\n"
             " 'testq': testq.bridge_holder(), 'wrapup': (W.World().game_a_hold() or {}).get('holder'),\n"
             " 'seat_restart': SR.bridge_reading('BENCH').get('bridge')}))"
             % (os.path.dirname(HERE), HERE, os.path.join(os.path.dirname(HERE), "Utils", "testq")))

    def readers():
        p = subprocess.run([sys.executable, "-c", probe], env=dict(bx.env, RIMFLOW_SHARED_BRIDGE=planted),
                           capture_output=True, text=True, timeout=60)
        try:
            return json.loads(p.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return {"error": (p.stdout + p.stderr)[-600:]}
    got = readers()
    import model as M
    check(got.get("rec") == ["BENCH", "rm-detached-x-1", M.ROOT],
          "game_a_lock_record names the lock's holder, its unit and its clone", got)
    check(got.get("gate_bench") is None and "BENCH" in (got.get("gate_foundry") or ""),
          "model.bridge_gate decides from the lock: the holder passes, another seat is refused naming it", got)
    check("BENCH" in (got.get("testq") or "") and got.get("wrapup") == "BENCH" and got.get("seat_restart") == ["BENCH"],
          "testq, wrapup and seat_restart name the lock's holder, never the planted FOUNDRY", got)
    kill(s)
    got = readers()
    check(got.get("rec") == [None, None, None] and got.get("testq") is None and got.get("wrapup") is None
          and got.get("seat_restart") == [] and "nobody" in (got.get("gate_bench") or ""),
          "its holder gone, every reader reads game a free at once (the planted file names FOUNDRY still)", got)
    r = bx.rf("bridge", "release", RIMFLOW_SHARED_BRIDGE=planted)
    with open(planted) as f:
        check(json.load(f) == rec, "a release wrote nothing over the planted old file")


def t_a_windows_python_client_obeys_the_lock():
    """The real python.exe against throwaway locks held by live WSL processes (selftest_game_lock_windows_python.py):
    refused from another clone, passed when it inherited the take or runs the holder's clone, a dead holder free."""
    p = subprocess.run([sys.executable, os.path.join(HERE, "selftest_game_lock_windows_python.py")],
                       capture_output=True, text=True, timeout=300)
    if p.returncode == 2:
        print("UNMEASURED a-windows-python-client-obeys-the-lock: %s" % p.stdout.strip()[-200:])
        return
    check(p.returncode == 0, "a Windows python.exe bridge client obeys the lock (every case)", p.stdout[-900:])


def t_a_windows_python_client_checks_the_lock_in_under_50_ms():
    """The real python.exe, a live WSL holder from this clone, the transport stubbed: a mutating call's client steps
    average under 50 ms (selftest_game_lock_windows_python.py timed). Red at 315 ms before the identity was cached."""
    p = subprocess.run([sys.executable, os.path.join(HERE, "selftest_game_lock_windows_python.py"), "timed"],
                       capture_output=True, text=True, timeout=300)
    if p.returncode == 2:
        print("UNMEASURED a-windows-python-client-checks-the-lock-in-under-50-ms: %s" % p.stdout.strip()[-200:])
        return
    check(p.returncode == 0, "a Windows python.exe client checks the lock in under 50 ms a call", p.stdout[-900:])


_READERS = []


def _readers_run():
    """The equivalence run on its fixture cases (selftest_game_driver_readers.py), run once for the two promises."""
    if not _READERS:
        _READERS.append(subprocess.run([sys.executable, os.path.join(HERE, "selftest_game_driver_readers.py")],
                                       capture_output=True, text=True, timeout=600))
    return _READERS[0]


def _readers_ok(p, words):
    """-> the run's verdict on the cases whose line names `words`: each such line is ok, and at least one exists."""
    lines = [ln for ln in p.stdout.splitlines() if ln.startswith(("ok ", "FAIL ")) and any(w in ln for w in words)]
    return bool(lines) and all(ln.startswith("ok ") for ln in lines) and "\n0 failed" in p.stdout


def t_the_two_last_glance_file_readers_read_every_game_from_the_lock():
    """The equivalence run on its fixture cases: the old readers (frozen) and the new on the same locks, every
    difference classed; the new readers equal `game_lock.py query all` (selftest_game_driver_readers.py)."""
    p = _readers_run()
    check(p.returncode == 0 and _readers_ok(p, ("query_all", "preflight")),
          "preflight_bridge and query_all read every game from its lock, never the glance file",
          p.stdout[-900:] + p.stderr[-300:])


def t_the_handoff_and_flowworks_p_b1_read_the_lock_and_nothing_prints_a_glance_file():
    """The same run: the handoff's Bridge lines are `query all`'s, P-B1 reads its own game's lock, neither opens a
    glance file, and rimflow has no printer of one."""
    p = _readers_run()
    check(p.returncode == 0 and _readers_ok(p, ("handoff", "P-B1", "printer is gone")),
          "the handoff and P-B1 read the lock; no glance file is printed or read", p.stdout[-900:] + p.stderr[-300:])


def main():
    t_a_query_answers_under_100_ms()        # first: the cases below spawn and kill dozens of processes
    t_one_record_per_game()
    t_two_claimers_race_and_exactly_one_wins()
    t_a_dead_holder_reads_free_at_once()
    t_an_unreadable_lock_is_could_not_look()
    t_run_releases_on_exit_crash_and_sigterm()
    t_his_hold_refuses_with_exit_3()
    t_an_old_style_hold_is_seen_and_an_old_style_release_frees_it()
    t_release_frees_only_this_process_trees_hold()
    t_the_225_am_release_that_left_bridge_who_saying_held()
    t_the_243_am_game_b_record_that_named_the_ended_run()
    t_the_335_am_ledger_free_while_the_lock_was_held()
    t_the_tick_line_that_named_a_dead_run_as_live()
    t_the_old_shared_file_is_neither_written_nor_read()
    t_a_windows_python_client_obeys_the_lock()
    t_a_windows_python_client_checks_the_lock_in_under_50_ms()
    t_the_two_last_glance_file_readers_read_every_game_from_the_lock()
    t_the_handoff_and_flowworks_p_b1_read_the_lock_and_nothing_prints_a_glance_file()
    for p in SLEEPERS:
        if p.poll() is None:
            p.kill()
    print("\n%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
