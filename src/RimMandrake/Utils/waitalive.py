#!/usr/bin/env python3
"""waitalive — one long wait for a job, that checks that the job lives. For `claude -p` runs, whose turn ends the run.

  waitalive.py run [--name N] [--max DUR] [--silence DUR] [--progress FILE] -- CMD...   start CMD and wait for its end
  waitalive.py attach NAME [--max DUR] [--silence DUR] [--progress FILE]                wait again for a job of this run

  Call it in ONE foreground Bash call with the tool's `timeout` at 3420000. --max: default and highest 55m. --silence:
  default 10m. The sign of life is growth of CMD's output, of the progress file, or of the CPU time of its process tree.
  It prints the tail of the output and one verdict line last, and kills nothing:
    0 FINISHED rc=0 | 1 FINISHED rc=N | 2 usage | 3 HUNG (pid) | 4 STILL RUNNING at --max (pid; attach takes it)
    5 COULD NOT LOOK | 6 DIED with no exit code
  state: $WAITALIVE_STATE, else <data root>/waitalive (rmpaths.py); verdicts.jsonl there holds each verdict.
Page: design/specs/2026-11-23-long-waits/boundary.md
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
# budget: danger=the wait outlives the one-hour prompt cache; ends no work: it reads STILL RUNNING; attach waits again
MAX_WAIT_S = 3300       # under the one-hour prompt cache (page, LIMITS)
# budget: danger=a hung job holds its caller; ends no work: the silence bound of a progress guard: it reads HUNG and kills
# budget: nothing
SILENCE_S = 600
CPU_SHARE = 0.01        # CPU growth under 1% of the silence bound is a poll loop, not work
CPU_MIN_S = 0.05
# budget: danger=a supervisor that never starts holds its caller; never reached in the 14 days to 2026-11-24; no record of its
# budget: run
START_S = 30
KEEP_DAYS = 14
TAIL_LINES = 20
TICK = os.sysconf("SC_CLK_TCK") if hasattr(os, "sysconf") else 100
FINISHED, FAILED, USAGE, HUNG, RUNNING, BLIND, DIED = range(7)


class CouldNotLook(Exception):
    pass


def dur(s):
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*([smh]?)\s*", str(s))
    if not m or float(m.group(1)) <= 0:
        raise argparse.ArgumentTypeError("bad duration %r (use 90, 90s, 5m, 2h)" % s)
    return float(m.group(1)) * {"": 1, "s": 1, "m": 60, "h": 3600}[m.group(2)]


def human(s):
    s = int(round(s))
    return "%ds" % s if s < 60 else "%dm%02ds" % (s // 60, s % 60) if s < 3600 else "%dh%02dm" % (s // 3600, s % 3600 // 60)


def state_root():
    env = os.environ.get("WAITALIVE_STATE")
    if env:
        return env
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    try:
        import rmpaths
        return os.path.join(str(rmpaths.rm_data_root()), "waitalive")
    except Exception as e:  # noqa: BLE001  no root: no state can be kept or read
        raise CouldNotLook("no state folder: %s: %s" % (type(e).__name__, e))


def scope_dir(root):
    """The jobs of one detached run (or of one window's shells) have their own folder: two runs may use one name."""
    who = os.environ.get("RM_DETACHED_UNIT") or os.environ.get("RM_ROLE_UNIT") or "window"
    return os.path.join(root, re.sub(r"[^A-Za-z0-9_.-]", "_", who))


def job_name(name):
    return re.sub(r"[^A-Za-z0-9_.~-]", "_", name).lstrip(".") or "job"


def write_json(path, obj):
    tmp = "%s.%d.tmp" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f)
    os.replace(tmp, path)


def read_json(path):
    """-> the object, or None when there is no such file. Anything else that is wrong is COULD NOT LOOK."""
    if not os.path.lexists(path):       # a record is only ever added (write_json), never taken away
        return None
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError) as e:
        raise CouldNotLook("%s cannot be read (%s: %s)" % (path, type(e).__name__, e))
    if not isinstance(d, dict):
        raise CouldNotLook("%s holds no record" % path)
    return d


# ------------------------------------------------------------------------------------------------ the process tree

def stat_of(pid):
    """-> (state, ppid, session, cpu ticks with its reaped children, start ticks) or None when it is gone."""
    try:
        with open("/proc/%s/stat" % pid, "rb") as f:
            x = f.read().rsplit(b")", 1)[1].split()
        return x[0].decode(), int(x[1]), int(x[3]), sum(int(v) for v in x[11:15]), int(x[19])
    except (FileNotFoundError, ProcessLookupError):     # the process is gone; any other error is not an answer
        return None
    except (OSError, IndexError, ValueError) as e:
        raise CouldNotLook("/proc/%s/stat cannot be read (%s: %s)" % (pid, type(e).__name__, e))


def boot_id():
    try:
        with open("/proc/sys/kernel/random/boot_id") as f:
            return f.read().strip()
    except OSError as e:
        raise CouldNotLook("the boot id cannot be read (%s: %s)" % (type(e).__name__, e))


def alive(pid, start):
    st = stat_of(pid)
    return bool(st and st[0] not in ("Z", "X") and st[4] == start)


def tree_cpu(job):
    """-> CPU seconds of the job's process tree: its session, and every descendant."""
    procs = {}
    for p in os.listdir("/proc"):
        if p.isdigit():
            st = stat_of(p)
            if st:
                procs[int(p)] = st
    mine = {p for p, st in procs.items() if st[2] == job or p == job}
    grew = True
    while grew:
        more = {p for p, st in procs.items() if st[1] in mine} - mine
        grew = bool(more)
        mine |= more
    return sum(procs[p][3] for p in mine) / float(TICK)


# ------------------------------------------------------------------------------------------------ the supervisor

def supervise(d):
    """The job's parent: in its own session, with no pipe of the caller. It writes job.json and, at the end, exit.json."""
    with open(os.path.join(d, "spec.json"), encoding="utf-8") as f:
        spec = json.load(f)
    if os.fork():
        os._exit(0)
    os.setsid()
    boot = boot_id()
    with open(os.path.join(d, "out"), "ab") as out:
        try:
            p = subprocess.Popen(spec["cmd"], stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT,
                                 start_new_session=True)
        except OSError as e:
            write_json(os.path.join(d, "exit.json"), {"rc": 127 if isinstance(e, FileNotFoundError) else 126, "at": time.time(),
                                                      "start_error": "%s: %s" % (type(e).__name__, e)})
            os._exit(0)
    st = stat_of(p.pid)
    me = stat_of(os.getpid())
    write_json(os.path.join(d, "job.json"), {"pid": p.pid, "start": st and st[4], "boot": boot, "cmd": spec["cmd"],
                                             "sup": os.getpid(), "sup_start": me and me[4], "at": time.time()})
    rc = p.wait()
    write_json(os.path.join(d, "exit.json"), {"signal": -rc, "at": time.time()} if rc < 0 else {"rc": rc, "at": time.time()})
    os._exit(0)


def running(d):
    """True while the job of folder `d` (or the supervisor that will record its end) runs."""
    if read_json(os.path.join(d, "exit.json")) is not None:
        return False
    job = read_json(os.path.join(d, "job.json"))
    if not job or job.get("boot") != boot_id():
        return False
    return alive(job.get("pid"), job.get("start")) or alive(job.get("sup"), job.get("sup_start"))


def prune(root, now):
    """Delete the folders of jobs that ended over KEEP_DAYS ago. It never decides a verdict."""
    try:
        for s in os.listdir(root):
            for n in os.listdir(os.path.join(root, s)) if os.path.isdir(os.path.join(root, s)) else []:
                d = os.path.join(root, s, n)
                if (os.path.isfile(os.path.join(d, "spec.json")) and now - os.path.getmtime(d) > KEEP_DAYS * 86400
                        and not running(d)):
                    shutil.rmtree(d, ignore_errors=True)
    except (OSError, CouldNotLook):
        pass


def take_folder(scope, name, cmd, cwd, note):
    """-> (folder, attach?). A live job of the same command in the same folder is attached to. Any other taken name gets
    a number: a job's folder is never reused, so no wait and no attach can read the end of another job."""
    n, d = 1, os.path.join(scope, name)
    while True:
        try:
            os.mkdir(d)
            break
        except FileExistsError:
            pass
        spec = read_json(os.path.join(d, "spec.json"))      # None: another run writes it at this moment
        if spec and spec.get("cmd") == cmd and spec.get("cwd") == cwd and running(d):
            note("NOTE: job %s already runs this command; this wait attaches to it" % os.path.basename(d))
            return d, True
        n += 1
        d = os.path.join(scope, "%s-%d" % (name, n))
    if n > 1:
        note("NOTE: the name %s is taken; this job is %s" % (name, os.path.basename(d)))
    return d, False


def start(scope, name, cmd, note):
    """-> the job's folder, started (or the live one it attaches to)."""
    try:
        os.makedirs(scope, exist_ok=True)
        cwd = os.getcwd()
        d, attach = take_folder(scope, name, cmd, cwd, note)
        if attach:
            return d
        write_json(os.path.join(d, "spec.json"), {"cmd": cmd, "cwd": cwd})
    except OSError as e:
        raise CouldNotLook("the state folder cannot be written (%s: %s); the command was not started"
                           % (type(e).__name__, e))
    try:
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "_supervise", d], stdin=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True, timeout=START_S)
    except (OSError, subprocess.SubprocessError) as e:
        raise CouldNotLook("the supervisor of %s gave no answer (%s)" % (d, type(e).__name__))
    t = time.time()
    while time.time() - t < START_S:
        if os.path.exists(os.path.join(d, "job.json")) or os.path.exists(os.path.join(d, "exit.json")):
            return d
        time.sleep(0.02)
    raise CouldNotLook("no sign of the start of %s in %d s (supervisor exit %s)" % (d, START_S, r.returncode))


# ------------------------------------------------------------------------------------------------ the wait

def size_of(path):
    try:
        s = os.stat(path)
        return s.st_size, s.st_mtime_ns
    except FileNotFoundError:       # not written yet; any other error is not an answer
        return None
    except OSError as e:
        raise CouldNotLook("%s cannot be read (%s: %s)" % (path, type(e).__name__, e))


def wait(d, max_s, silence_s, progress=None, now=time.monotonic, sleep=time.sleep):
    """-> (verdict, text, facts). Reads the job of folder `d` until its end, its silence bound or max_s."""
    out = os.path.join(d, "out")
    t0 = last = now()
    seen = (size_of(out), size_of(progress) if progress else None)
    job = read_json(os.path.join(d, "job.json"))
    if job is not None and not (isinstance(job.get("pid"), int) and isinstance(job.get("start"), int)):
        raise CouldNotLook("%s names no process" % os.path.join(d, "job.json"))
    cpu = tree_cpu(job["pid"]) if job else 0.0
    need = max(CPU_MIN_S, CPU_SHARE * silence_s)
    facts = {"pid": job and job.get("pid"), "waited_s": 0, "silent_s": 0}
    while True:
        end = read_json(os.path.join(d, "exit.json"))
        if end is None and not running(d):      # ended between the two reads, or gone without a record
            sleep(0.3)
            end = read_json(os.path.join(d, "exit.json"))
            if end is None:
                if not job:
                    raise CouldNotLook("%s holds no job record" % d)
                return DIED, "DIED: the job is gone and recorded no exit code", facts
        t = now()
        facts.update(waited_s=round(t - t0, 1), silent_s=round(t - last, 1))
        if end is not None:
            facts["rc"] = end.get("rc")
            if end.get("signal"):
                return DIED, "DIED: signal %s ended the job; it has no exit code" % end["signal"], facts
            if not isinstance(end.get("rc"), int):
                raise CouldNotLook("%s names no exit code" % os.path.join(d, "exit.json"))
            why = " (the command did not start: %s)" % end["start_error"] if end.get("start_error") else ""
            return (FINISHED if end["rc"] == 0 else FAILED), "FINISHED rc=%d%s" % (end["rc"], why), facts
        sig = (size_of(out), size_of(progress) if progress else None)
        c = tree_cpu(job["pid"])
        if sig != seen or c - cpu >= need:
            last, seen, cpu = t, sig, c
        cpu = min(cpu, c)       # a child that nobody reaped took its CPU time with it
        silent = t - last
        facts["silent_s"] = round(silent, 1)
        if silent >= silence_s:
            return HUNG, ("HUNG: no output, no progress and %.2f s of CPU in %s; pid %d still runs, nothing was killed%s"
                          % (c - cpu, human(silent), job["pid"],
                             "; the progress file %s is not there" % progress if progress and not sig[1] else "")), facts
        if t - t0 >= max_s:
            return RUNNING, "STILL RUNNING after %s; last sign of life %s ago; pid %d" % (
                human(t - t0), human(silent), job["pid"]), facts
        sleep(max(0.02, min(0.2 if t - t0 < 10 else 2.0, silence_s - silent, t0 + max_s - t)))


def tail(path, n=TAIL_LINES):
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 8000))
            return [x[:400] for x in f.read().decode("utf-8", "replace").splitlines()[-n:]]  # cut-ok: terminal display
    except OSError as e:
        return ["(output cannot be read: %s)" % e]


def log(root, rec):
    """One line of verdicts.jsonl; -> None, or why it could not be written."""
    try:
        with open(os.path.join(root, "verdicts.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        return None
    except OSError as e:
        return "%s: %s" % (type(e).__name__, e)


WORDS = {FINISHED: "FINISHED", FAILED: "FINISHED", HUNG: "HUNG", RUNNING: "STILL RUNNING", BLIND: "COULD NOT LOOK", DIED: "DIED"}


def parser():
    ap = argparse.ArgumentParser(prog="waitalive.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="verb", required=True)
    for v in ("run", "attach"):
        a = sub.add_parser(v)
        if v == "run":
            a.add_argument("--name")
        else:
            a.add_argument("name")
        a.add_argument("--max", type=dur, default=MAX_WAIT_S)
        a.add_argument("--silence", type=dur, default=SILENCE_S)
        a.add_argument("--progress", metavar="FILE")
    return ap


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["_supervise"]:
        return supervise(argv[1])
    cmd = []
    if "--" in argv:
        i = argv.index("--")
        argv, cmd = argv[:i], argv[i + 1:]
    args = parser().parse_args(argv)
    if args.verb == "run" and not cmd:
        print("waitalive: usage: run [--name N] [--max DUR] [--silence DUR] [--progress FILE] -- CMD...")
        return USAGE

    def note(text):
        print(text, flush=True)
    max_s = args.max
    if max_s > MAX_WAIT_S:
        note("NOTE: --max %s is past the prompt cache; this wait ends at %s (attach takes the rest)"
             % (human(max_s), human(MAX_WAIT_S)))
        max_s = MAX_WAIT_S
    name = job_name(args.name or "job-%s-%d" % (time.strftime("%H%M%S"), os.getpid()))
    facts, root, d = {}, None, None
    try:
        if not os.path.exists("/proc/self/stat"):
            raise CouldNotLook("no /proc on this machine: the sign of life cannot be read")
        root = state_root()
        scope = scope_dir(root)
        if args.verb == "run":
            prune(root, time.time())
            d = start(scope, name, cmd, note)
            name = os.path.basename(d)
            job = read_json(os.path.join(d, "job.json"))        # None: the command did not start
            note("waitalive: job %s, pid %s, output %s" % (name, job.get("pid") if job else "none", os.path.join(d, "out")))
        else:
            name = job_name(args.name)
            d = os.path.join(scope, name)
            if not os.path.isdir(d):
                d = None
                try:
                    known = sorted(os.listdir(scope))
                except OSError:
                    known = []
                raise CouldNotLook("no job %s of this run (its jobs: %s)" % (name, ", ".join(known) or "none"))
            if os.path.isdir("%s-2" % d):
                note("NOTE: the name %s was taken again later: %s" % (name, ", ".join(
                    sorted(x for x in os.listdir(scope) if re.fullmatch(re.escape(name) + r"-\d+", x)))))
        code, text, facts = wait(d, max_s, args.silence, args.progress)
    except (CouldNotLook, OSError) as e:
        code, text = BLIND, "COULD NOT LOOK: %s" % (e if isinstance(e, CouldNotLook) else "%s: %s" % (type(e).__name__, e))
    if d:
        for line in tail(os.path.join(d, "out")):
            print("| " + line)
        text += " | job %s, output %s" % (name, os.path.join(d, "out"))
        if code in (HUNG, RUNNING):
            text += " | wait again: waitalive.py attach %s" % name
    if root and os.path.isdir(root):
        bad = log(root, dict(facts, at=time.strftime("%Y-%m-%dT%H:%M:%S%z"), verdict=WORDS[code], name=name,
                             unit=os.environ.get("RM_DETACHED_UNIT") or os.environ.get("RM_ROLE_UNIT"), silence_s=args.silence,
                             max_s=max_s))
        if bad:
            note("NOTE: the verdict was not logged (%s)" % bad)
    print("waitalive: " + text, flush=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
