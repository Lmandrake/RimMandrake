#!/usr/bin/env python3
"""Selftest of waitalive.py and of the Bash limit of a detached run. Each promise of
design/specs/2026-11-23-long-waits/boundary.md has a test of its name. WAITALIVE_TOOL and WAITALIVE_DH name a mutated copy
of waitalive.py and of detached_helper.py (design/specs/2026-11-23-long-waits/mutants.py).

    python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_waitalive.py
"""
import importlib.util
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RIMFLOW = os.path.join(REPO, "src", "RimMandrake", "rimflow")
SPEC = os.path.join(REPO, "design", "specs", "2026-11-23-long-waits")
TOOL = os.environ.get("WAITALIVE_TOOL") or os.path.join(HERE, "waitalive.py")
TMP = tempfile.mkdtemp(prefix="selftest_waitalive_")
os.environ["RM_UNDER_SELFTEST"] = "1"
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "dispatcher")
PIDS = set()
PY = sys.executable


def module(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


sys.path.insert(0, RIMFLOW)
sys.path.insert(0, HERE)
W = module("waitalive_under_test", TOOL)


def env(state=None, unit="rm-detached-selftest"):
    e = dict(os.environ, WAITALIVE_STATE=state or os.path.join(TMP, "state"), RM_DETACHED_UNIT=unit)
    e.pop("RM_ROLE_UNIT", None)
    return e


def wa(*a, **kw):
    r = subprocess.run([PY, TOOL] + list(a), env=kw.get("env") or env(), capture_output=True, text=True, timeout=60,
                       stdin=subprocess.DEVNULL, cwd=kw.get("cwd"))
    out = (r.stdout + r.stderr).strip()
    PIDS.update(int(x) for x in re.findall(r"pid (\d+)", out))
    return r.returncode, out, out.splitlines()[-1] if out else ""


def need(ok, what):
    if not ok:
        raise AssertionError(what)


def is_alive(pid):
    st = W.stat_of(pid)
    return bool(st and st[0] not in ("Z", "X"))


def t_a_hung_job_is_named():
    for cmd in (["sleep", "30"], ["sh", "-c", "while :; do sleep 1; done"]):     # idle, and a poll loop that does no work
        t = time.time()
        rc, out, last = wa("run", "--max", "20s", "--silence", "2s", "--", *cmd)
        need(rc == 3 and "HUNG" in last and re.search(r"pid \d+", last), "%s: rc %s, %s" % (cmd, rc, last))
        need(time.time() - t < 10, "named late: %.1f s" % (time.time() - t))
    # a line, then silence: HUNG, and the silence counts from the line
    rc, out, last = wa("run", "--max", "20s", "--silence", "2s", "--", "sh", "-c", "echo one; sleep 30")
    need(rc == 3 and "| one" in out, "a line then silence: rc %s, %s" % (rc, last))


    rc, out, last = wa("run", "--max", "20s", "--silence", "1s", "--progress", os.path.join(TMP, "absent"), "--", "sleep", "20")
    need(rc == 3 and "absent is not there" in last, "a progress file that is not there is not named: rc %s, %s" % (rc, last))


def t_a_live_job_is_never_called_hung():
    p = os.path.join(TMP, "progress")
    ok = {
        "prints": ["sh", "-c", "for i in 1 2 3 4 5 6 7 8; do echo $i; sleep 0.5; done"],
        "burns CPU": [PY, "-c", "import time\nt=time.time()\nwhile time.time()-t<4: pass"],
        "burns CPU in a child": ["sh", "-c", PY + " -c 'import time\nt=time.time()\nwhile time.time()-t<4: pass'; true"],
    }
    for what, cmd in ok.items():
        rc, out, last = wa("run", "--max", "20s", "--silence", "2s", "--", *cmd)
        need(rc == 0, "%s: rc %s, %s" % (what, rc, last))
    rc, out, last = wa("run", "--max", "20s", "--silence", "2s", "--progress", p, "--", "sh", "-c",
                       "for i in 1 2 3 4 5 6 7 8; do echo x >> %s; sleep 0.5; done" % p)
    need(rc == 0, "progress file: rc %s, %s" % (rc, last))


def t_a_failure_is_never_finished_well():
    for n in (1, 7, 137):
        rc, out, last = wa("run", "--", "sh", "-c", "exit %d" % n)
        need(rc == 1 and "FINISHED rc=%d" % n in last, "exit %d: rc %s, %s" % (n, rc, last))
    rc, out, last = wa("run", "--", "no_such_command_here")
    need(rc == 1 and "rc=127" in last and "did not start" in last, "no command: rc %s, %s" % (rc, last))
    f = os.path.join(TMP, "not_executable")
    open(f, "w").close()
    rc, out, last = wa("run", "--", f)
    need(rc == 1 and "rc=126" in last, "not executable: rc %s, %s" % (rc, last))
    rc, out, last = wa("run", "--", "true")
    need(rc == 0 and "FINISHED rc=0" in last, "true: rc %s, %s" % (rc, last))


def t_a_dead_job_is_died():
    rc, out, last = wa("run", "--", "sh", "-c", "kill -9 $$")
    need(rc == 6 and "DIED" in last and "FINISHED" not in last, "own signal: rc %s, %s" % (rc, last))
    rc, out, last = wa("run", "--name", "both", "--max", "1s", "--", "sleep", "40")     # the supervisor dies too
    need(rc == 4, "start: rc %s, %s" % (rc, last))
    with open(os.path.join(TMP, "state", "rm-detached-selftest", "both", "job.json")) as fh:
        job = json.load(fh)
    os.kill(job["sup"], signal.SIGKILL)
    os.killpg(job["pid"], signal.SIGKILL)
    time.sleep(0.3)
    rc, out, last = wa("attach", "both", "--max", "5s")
    need(rc == 6 and "DIED" in last, "no exit code recorded: rc %s, %s" % (rc, last))


def t_could_not_look_is_its_own_answer():
    rc, out, last = wa("attach", "never_started")
    need(rc == 5 and "COULD NOT LOOK" in last, "unknown: rc %s, %s" % (rc, last))
    st = os.path.join(TMP, "broken")
    for f, text in (("exit.json", "{"), ("exit.json", "{}"), ("exit.json", "[]"), ("job.json", "not json"), ("job.json", "{}")):
        d = os.path.join(st, "rm-detached-selftest", "j")
        subprocess.run(["rm", "-rf", d])
        os.makedirs(d)
        open(os.path.join(d, "out"), "w").close()
        with open(os.path.join(d, f), "w") as fh:
            fh.write(text)
        rc, out, last = wa("attach", "j", "--max", "2s", env=env(st))
        need(rc == 5 and "COULD NOT LOOK" in last, "%s = %s: rc %s, %s" % (f, text, rc, last))
    # the job is gone and its end is recorded, but unreadable: it may have ended well, so it is not DIED
    gone = subprocess.Popen(["true"])
    gone.wait()
    with open(os.path.join(d, "job.json"), "w") as fh:
        json.dump({"pid": gone.pid, "start": 1, "boot": W.boot_id(), "cmd": ["x"]}, fh)
    with open(os.path.join(d, "exit.json"), "w") as fh:
        fh.write('{"rc":')
    rc, out, last = wa("attach", "j", "--max", "2s", env=env(st))
    need(rc == 5 and "COULD NOT LOOK" in last, "an unreadable end: rc %s, %s" % (rc, last))
    # the process table cannot be read: that is not "the process is gone"
    W.open = lambda *a, **k: (_ for _ in ()).throw(OSError(24, "Too many open files"))
    try:
        for fn in (lambda: W.stat_of(1), W.boot_id):
            try:
                fn()
                need(False, "an unreadable /proc is an answer")
            except W.CouldNotLook:
                pass
    finally:
        del W.open
    f = os.path.join(TMP, "a_file")
    open(f, "w").close()
    rc, out, last = wa("run", "--", "touch", os.path.join(TMP, "started"), env=env(os.path.join(f, "x")))
    need(rc == 5 and "COULD NOT LOOK" in last, "no state folder: rc %s, %s" % (rc, last))
    need(not os.path.exists(os.path.join(TMP, "started")), "the command ran with no record of it")


def t_no_wait_outlives_the_cache():
    need(W.MAX_WAIT_S <= 3300, "MAX_WAIT_S %s" % W.MAX_WAIT_S)
    got = []
    keep = W.wait
    W.wait = lambda d, max_s, *a, **k: (got.append(max_s), (W.FINISHED, "FINISHED rc=0", {}))[1]
    old = dict(os.environ)
    os.environ.update(env(os.path.join(TMP, "clamp")))
    try:
        with open(os.devnull, "w") as null:
            so, sys.stdout = sys.stdout, null
            try:
                for extra in (["--max", "2h"], ["--max", "3301s"], [], ["--max", "10m"]):
                    W.main(["run"] + extra + ["--", "true"])
            finally:
                sys.stdout = so
    finally:
        W.wait = keep
        os.environ.clear()
        os.environ.update(old)
    need(got == [3300, 3300, 3300, 600], "the bounds: %s" % got)
    # the bound holds inside the wait too: a fake clock, a job that always prints
    clock = [0.0]
    d = os.path.join(TMP, "fake")
    os.makedirs(d)
    me = W.stat_of(os.getpid())
    W.write_json(os.path.join(d, "job.json"), {"pid": os.getpid(), "start": me[4], "boot": W.boot_id(), "cmd": ["x"]})

    def sleep(s):
        clock[0] += s
        with open(os.path.join(d, "out"), "a") as fh:
            fh.write("x")
    code, text, facts = W.wait(d, 600, 100, now=lambda: clock[0], sleep=sleep)
    need(code == W.RUNNING and 600 <= clock[0] < 603, "code %s at %.1f s" % (code, clock[0]))
    import detached_helper
    DH = module("dh_under_test", os.environ["WAITALIVE_DH"]) if os.environ.get("WAITALIVE_DH") else detached_helper
    need(W.MAX_WAIT_S * 1000 < DH.BASH_MAX_MS <= 59 * 60 * 1000, "BASH_MAX_MS %s" % DH.BASH_MAX_MS)


def t_the_job_outlives_the_wait():
    rc, out, last = wa("run", "--name", "long", "--max", "1s", "--", "sh", "-c", "sleep 3; echo end; exit 5")
    need(rc == 4 and "STILL RUNNING" in last and "attach long" in last, "at --max: rc %s, %s" % (rc, last))
    need(is_alive(int(re.search(r"pid (\d+)", last).group(1))), "the job was killed at --max")
    rc, out, last = wa("attach", "long", "--max", "20s")
    need(rc == 1 and "rc=5" in last and "| end" in out, "attach: rc %s, %s" % (rc, last))
    rc, out, last = wa("run", "--name", "hung", "--max", "20s", "--silence", "1s", "--", "sh", "-c", "sleep 4; exit 6")
    need(rc == 3 and is_alive(int(re.search(r"pid (\d+)", last).group(1))), "HUNG killed it: rc %s, %s" % (rc, last))
    rc, out, last = wa("attach", "hung", "--max", "20s", "--silence", "10s")
    need(rc == 1 and "rc=6" in last, "attach after HUNG: rc %s, %s" % (rc, last))
    # the harness cuts the call: the whole process group of the wait, and each of its children, is killed
    p = subprocess.Popen([PY, TOOL, "run", "--name", "cut", "--", "sh", "-c", "sleep 3; echo after; exit 4"], env=env(),
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True)
    line = p.stdout.readline()
    PIDS.update(int(x) for x in re.findall(r"pid (\d+)", line))
    subprocess.run(["pkill", "-KILL", "-P", str(p.pid)])
    os.killpg(p.pid, signal.SIGKILL)
    p.wait(timeout=10)
    rc, out, last = wa("attach", "cut", "--max", "20s")
    need(rc == 1 and "rc=4" in last and "| after" in out, "attach after a cut: rc %s, %s" % (rc, last))


def t_the_call_returns():
    t = time.time()
    rc, out, last = wa("run", "--max", "1s", "--", "sh", "-c", "sleep 15")      # wa reads both pipes to their end
    need(rc == 4 and time.time() - t < 8, "rc %s after %.1f s: the job holds a pipe" % (rc, time.time() - t))


def t_one_verdict_line_last():
    rc, out, last = wa("run", "--", "sh", "-c", "echo FINISHED rc=0; echo STILL RUNNING; exit 3")
    need(rc == 1 and last.startswith("waitalive: FINISHED rc=3"), "the job's own words: rc %s, %s" % (rc, last))
    need(wa("run", "--")[0] == 2 and wa("run")[0] == 2 and wa()[0] == 2, "no command is not usage")
    need(wa("run", "--max", "soon", "--", "true")[0] == 2 and wa("run", "--max", "0", "--", "true")[0] == 2, "a bad duration")
    need(wa("attach")[0] == 2, "attach with no name")
    codes = [W.FINISHED, W.FAILED, W.USAGE, W.HUNG, W.RUNNING, W.BLIND, W.DIED]
    need(codes == list(range(7)), "the exits: %s" % codes)


def t_a_taken_name_is_repaired():
    st = env(os.path.join(TMP, "names"))
    cmd = ["sh", "-c", "sleep 3; exit 8"]
    rc, out, last = wa("run", "--name", "n", "--max", "1s", "--", *cmd, env=st)
    need(rc == 4, last)
    rc, out, last = wa("run", "--name", "n", "--max", "1s", "--", "sh", "-c", "sleep 2; exit 9", env=st)
    need(rc == 4 and "attach n-2" in last, "another command: rc %s, %s" % (rc, last))
    rc, out, last = wa("run", "--name", "n", "--max", "20s", "--", *cmd, env=st)
    need(rc == 1 and "rc=8" in last and "attaches" in out, "the same command: rc %s, %s" % (rc, last))
    # an ended job keeps its name, its output and its end; the next use of the name has a number
    rc, out, last = wa("run", "--name", "n", "--", "echo", "again", env=st)
    need(rc == 0 and "| again" in out and "this job is n-3" in out, "the name of an ended job: rc %s, %s" % (rc, out))
    rc, out, last = wa("run", "--name", "n", "--", "echo", "again", env=st)
    need(rc == 0 and "this job is n-4" in out, "an ended job of the same command was not run again: %s" % out)
    rc, out, last = wa("attach", "n", env=st)
    need(rc == 1 and "rc=8" in last and "n-3" in out, "attach reads the end of another job: rc %s, %s" % (rc, out))
    # the same command in another folder is another job
    for i, code in (("a", 0), ("b", 7)):
        os.makedirs(os.path.join(TMP, "cwd", i))
        with open(os.path.join(TMP, "cwd", i, "code"), "w") as fh:
            fh.write(str(code))
    cmd = ["sh", "-c", "sleep 2; exit $(cat code)"]
    rc, out, last = wa("run", "--name", "c", "--max", "1s", "--", *cmd, env=st, cwd=os.path.join(TMP, "cwd", "a"))
    need(rc == 4, last)
    rc, out, last = wa("run", "--name", "c", "--max", "20s", "--", *cmd, env=st, cwd=os.path.join(TMP, "cwd", "b"))
    need(rc == 1 and "rc=7" in last, "another folder's job was taken for this one: rc %s, %s" % (rc, last))
    # an ended job whose child still holds its output (on D: such a folder cannot be renamed)
    wa("run", "--name", "h", "--", "sh", "-c", "sleep 20 & echo pid $!; exit 0", env=st)
    rc, out, last = wa("run", "--name", "h", "--", "true", env=st)
    need(rc == 0, "a held output: rc %s, %s" % (rc, last))
    rc, out, last = wa("attach", "n", env=env(os.path.join(TMP, "names"), unit="another-run"))
    need(rc == 5, "another run sees this run's job: rc %s, %s" % (rc, last))


def t_each_verdict_is_logged():
    st = os.path.join(TMP, "logged")
    wa("run", "--", "true", env=env(st))
    wa("run", "--max", "20s", "--silence", "1s", "--", "sleep", "20", env=env(st))
    wa("attach", "nobody", env=env(st))
    with open(os.path.join(st, "verdicts.jsonl")) as fh:
        rows = [json.loads(x) for x in fh]
    need([r["verdict"] for r in rows] == ["FINISHED", "HUNG", "COULD NOT LOOK"], "the rows: %s" % rows)
    need(rows[1]["silent_s"] >= 1 and rows[1]["pid"] and rows[1]["unit"] == "rm-detached-selftest", "the HUNG row: %s" % rows[1])
    os.remove(os.path.join(st, "verdicts.jsonl"))
    os.mkdir(os.path.join(st, "verdicts.jsonl"))
    rc, out, last = wa("run", "--", "sh", "-c", "exit 7", env=env(st))
    need(rc == 1 and "rc=7" in last and "was not logged" in out, "no log: rc %s, %s" % (rc, last))


def setting_faults(exp, argv):
    """-> why the setting of `argv` does not stand on the experiment, "" when it does (or when argv sets none)."""
    m = re.search(r"BASH_MAX_TIMEOUT_MS=(\d+)", " ".join(argv))
    if not m:
        return ""
    for r in [exp] + exp.get("runs", []):
        if r.get("cut_by_harness") is not False:
            return "a run was cut by the harness"
        if r.get("cache_rebuilt_after") is not False:
            return "a run rebuilt the cache"
    if not any(r.get("setting_ms") == int(m.group(1)) and r.get("call_lasted_s", 0) > 660 for r in [exp] + exp.get("runs", [])):
        return "no run tried %s" % m.group(1)
    return ""


def launch_argv():
    import detached_helper
    DH = module("dh_under_test", os.environ["WAITALIVE_DH"]) if os.environ.get("WAITALIVE_DH") else detached_helper
    rec = {"unit": "rm-detached-t", "seat": "BENCH", "item": "X", "clone": "/tmp/c", "model": "opus", "budget_usd": 0.0,
           "max_s": None, "out": "/tmp/o", "err": "/tmp/e", "state": "/tmp/s", "brief_file": "/tmp/b", "at": 0}
    return DH, DH.launch_argv(rec, "m", "/usr/bin/claude")


def t_the_setting_stands_on_the_experiment():
    with open(os.path.join(SPEC, "experiment.json")) as fh:
        exp = json.load(fh)
    DH, argv = launch_argv()
    i = argv.index("BASH_MAX_TIMEOUT_MS=%d" % DH.BASH_MAX_MS) if DH.BASH_MAX_MS else -1
    need(i < argv.index("--") and argv[i - 1] == "--setenv", "the variable is not a --setenv of the unit")
    need(setting_faults(exp, argv) == "", setting_faults(exp, argv))
    # the checker sees each fault
    need(setting_faults(dict(exp, cut_by_harness=True), argv), "a cut call is not seen")
    need(setting_faults(dict(exp, cache_rebuilt_after=True), argv), "a rebuilt cache is not seen")
    need(setting_faults(dict(exp, cut_by_harness=None), argv), "an unknown reading is not seen")
    need(setting_faults(exp, ["BASH_MAX_TIMEOUT_MS=9999999"]), "a value that nobody tried is not seen")


def t_the_brief_names_the_command():
    DH, _ = launch_argv()
    text = DH.FOOTER.format(clone="/c", item="X", seat="BENCH", bound_text="b")
    need("waitalive.py run --name" in text and "waitalive.py attach" in text and str(DH.BASH_MAX_MS) in text, "the line")
    line = next(x for x in text.split("\n- ") if "waitalive.py run" in x)
    need(not re.search(r"\$\s?\d|\bweighted\b|\bbudget|\bspend|\btokens?\b|\bcost", line, re.I), "the line tells spend: " + line)


def run_one(t):
    try:
        t()
        return ""
    except Exception as e:  # noqa: BLE001
        return "%s: %s" % (type(e).__name__, e)


def main():
    tests = [t_a_hung_job_is_named, t_a_live_job_is_never_called_hung, t_a_failure_is_never_finished_well,
             t_a_dead_job_is_died, t_could_not_look_is_its_own_answer, t_no_wait_outlives_the_cache,
             t_the_job_outlives_the_wait, t_the_call_returns, t_one_verdict_line_last,
             t_a_taken_name_is_repaired, t_each_verdict_is_logged, t_the_setting_stands_on_the_experiment,
             t_the_brief_names_the_command]
    serial = [t_no_wait_outlives_the_cache, t_the_setting_stands_on_the_experiment,
              t_the_brief_names_the_command]
    with ThreadPoolExecutor(6) as ex:       # each test waits far more than it works
        got = dict(zip([t for t in tests if t not in serial], ex.map(run_one, [t for t in tests if t not in serial])))
    for t in serial:
        got[t] = run_one(t)
    for p in PIDS:
        try:
            os.killpg(p, signal.SIGKILL)
        except OSError:
            pass
    for t, why in got.items():
        print("%s  %s%s" % ("FAIL" if why else "PASS", t.__name__[2:].replace("_", "-"), "  -- " + why if why else ""))
    bad = sum(1 for w in got.values() if w)
    subprocess.run(["rm", "-rf", TMP])
    print("%s %d/%d" % ("FAIL" if bad else "PASS", len(got) - bad, len(got)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
