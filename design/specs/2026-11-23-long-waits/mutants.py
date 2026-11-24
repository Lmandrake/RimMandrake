#!/usr/bin/env python3
"""Planted faults of waitalive.py and of the Bash limit in detached_helper.py: each one must turn
src/RimMandrake/Utils/selftest_waitalive.py red. `as built` must stay green. Exit 0 when all are caught."""
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
WA = "src/RimMandrake/Utils/waitalive.py"
DH = "src/RimMandrake/rimflow/detached_helper.py"
TEST = os.path.join(REPO, "src/RimMandrake/Utils/selftest_waitalive.py")
M = [
    ("as built", WA, "", ""),
    ("a silent idle job is called alive", WA, "if silent >= silence_s:", "if False:"),
    ("a poll loop is called alive", WA, "need = max(CPU_MIN_S, CPU_SHARE * silence_s)", "need = 0.0"),
    ("a busy silent job is called hung", WA, "if sig != seen or c - cpu >= need:", "if sig != seen:"),
    ("the CPU of a child is not read", WA, "procs[p][3] for p in mine)", "procs[p][3] for p in mine if p == job)"),
    ("the output is no sign of life", WA, "sig = (size_of(out), ", "sig = (seen[0], "),
    ("the progress file is no sign of life", WA, "sig = (size_of(out), size_of(progress) if progress else None)",
     "sig = (size_of(out), seen[1])"),
    ("exit 7 reads as 0", WA, 'return (FINISHED if end["rc"] == 0 else FAILED)', "return FINISHED"),
    ("exit 7 reads rc=0 in the line", WA, '"FINISHED rc=%d%s" % (end["rc"], why)', '"FINISHED rc=%d%s" % (0, why)'),
    ("a command that did not start reads as 0", WA, '{"rc": 127 if isinstance(e, FileNotFoundError) else 126', '{"rc": 0'),
    ("a killed job reads as finished", WA, '{"signal": -rc, "at": time.time()} if rc < 0 else {"rc": rc',
     '{"rc": max(rc, 0)'),
    ("a killed job reads as a failure", WA, '{"signal": -rc, "at": time.time()} if rc < 0 else {"rc": rc', '{"rc": abs(rc)'),
    ("a job gone without a record reads as finished", WA, 'return DIED, "DIED: the job is gone', 'return FINISHED, "DIED: the job is gone'),
    ("an unknown job reads as finished", WA, "code, text = BLIND,", "code, text = FINISHED,"),
    ("an unreadable record is an empty one", WA, "    except (OSError, ValueError) as e:\n        raise CouldNotLook(\"%s cannot be read",
     "    except (OSError, ValueError) as e:\n        return None\n        raise CouldNotLook(\"%s cannot be read"),
    ("an unreadable process table reads as gone", WA, "    except (FileNotFoundError, ProcessLookupError):", "    except (OSError):"),
    ("an exit record with no code is finished", WA, 'if not isinstance(end.get("rc"), int):', "end.setdefault('rc', 0)\n            if False:"),
    ("the bound is over 59 minutes", WA, "MAX_WAIT_S = 3300 ", "MAX_WAIT_S = 7200 "),
    ("a longer --max is taken", WA, "        max_s = MAX_WAIT_S\n", "        pass\n"),
    ("the wait has no bound", WA, "if t - t0 >= max_s:", "if t - t0 >= 3 * max_s:"),
    ("the job is killed at the bound", WA, "        if t - t0 >= max_s:\n", "        if t - t0 >= max_s:\n            os.killpg(job['pid'], 9)\n"),
    ("a hung job is killed", WA, "        if silent >= silence_s:\n", "        if silence_s <= silent:\n            os.killpg(job['pid'], 9)\n"),
    ("the supervisor dies with the call", WA, "    if os.fork():\n        os._exit(0)\n    os.setsid()\n", "    os.setpgid(0, int(os.environ['WA_PG']))\n"),
    ("the job holds the caller's pipe", WA, "stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True",
     "start_new_session=True"),
    ("the job's own words are the last line", WA, '    if d:\n        for line in tail(os.path.join(d, "out")):\n            print("| " + line)\n',
     '    if d:\n        import atexit\n        atexit.register(lambda: print("\\n".join(tail(os.path.join(d, "out")))))\n'),
    ("a name is taken over", WA, "        except FileExistsError:\n            pass\n",
     "        except FileExistsError:\n            shutil.rmtree(d)\n            os.mkdir(d)\n            break\n"),
    ("the same command in another folder is the same job", WA, ' and spec.get("cwd") == cwd and', " and"),
    ("a live job of the same command is started again", WA, 'if spec.get("cmd") == cmd and', "if False and"),
    ("an ended job is attached to", WA, "== cwd and running(d):", "== cwd:"),
    ("two runs share a job", WA, 'who = os.environ.get("RM_DETACHED_UNIT") or os.environ.get("RM_ROLE_UNIT") or "window"', 'who = "all"'),
    ("the silent time is not logged", WA, 'facts["silent_s"] = round(silent, 1)', "facts.pop('silent_s', None)"),
    ("a log that cannot be written ends the verdict", WA, "    except OSError as e:\n        return \"%s: %s\" % (type(e).__name__, e)\n\n\nWORDS",
     "    except ZeroDivisionError as e:\n        return \"%s: %s\" % (type(e).__name__, e)\n\n\nWORDS"),
    ("the unit has no setting", DH, "BASH_MAX_MS = 3420000", "BASH_MAX_MS = 0"),
    ("the setting is past the cache", DH, "BASH_MAX_MS = 3420000", "BASH_MAX_MS = 3600000"),
    ("the setting is a value nobody tried", DH, "BASH_MAX_MS = 3420000", "BASH_MAX_MS = 3500000"),
    ("the setting is under the wait's bound", DH, "BASH_MAX_MS = 3420000", "BASH_MAX_MS = 3300000"),
    ("the variable is never set", DH, '["--setenv", "BASH_MAX_TIMEOUT_MS=%d" % BASH_MAX_MS] if BASH_MAX_MS else []', "[]"),
    ("the brief does not name the command", DH, "waitalive.py run --name", "waitfor.py run --name"),
]


def one(m):
    name, rel, old, new = m
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        src = f.read()
    if old and src.count(old) != 1:
        return name, None, "the text to change is there %d times" % src.count(old)
    if "WA_PG" in new:      # a supervisor that stays in the group of the call
        src = src.replace("stderr=subprocess.DEVNULL, start_new_session=True, timeout=START_S)", "stderr=subprocess.DEVNULL, "
                          "start_new_session=False, timeout=START_S)").replace("    if os.fork():\n        os._exit(0)\n    os.setsid()\n",
                                                                               "    if os.fork():\n        os._exit(0)\n")
        src = src.replace("stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT,\n                                 start_new_session=True)",
                          "stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT)")
    else:
        src = src.replace(old, new) if old else src
    d = os.path.dirname(os.path.join(REPO, rel))
    fd, p = tempfile.mkstemp(suffix=".py", prefix="mutant_%s_" % os.path.basename(rel)[:-3])
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        if rel == WA:       # the copy finds its neighbours where the real file does
            src = src.replace("HERE = os.path.dirname(os.path.abspath(__file__))", "HERE = %r" % d)
        else:
            src = src.replace("HERE = os.path.dirname(os.path.abspath(__file__))", "HERE = %r" % d)
        f.write(src)
    try:
        r = subprocess.run([sys.executable, TEST], capture_output=True, text=True, timeout=400,
                           env=dict(os.environ, **{"WAITALIVE_TOOL" if rel == WA else "WAITALIVE_DH": p}))
    finally:
        os.remove(p)
    red = re.findall(r"^FAIL  (\S+)", r.stdout, re.M)
    return name, r.returncode, ", ".join(red) or r.stdout[-200:] + r.stderr[-300:]


def main():
    bad = 0
    if sys.argv[1:]:        # only the faults whose name holds this text
        M[:] = [m for m in M if sys.argv[1] in m[0]]
    with ThreadPoolExecutor(3) as ex:
        for name, rc, text in ex.map(one, M):
            ok = rc == 0 if name == "as built" else rc == 1
            bad += not ok
            print("%s  %s: %s" % ("OK" if ok else "NOT CAUGHT" if rc == 0 else "BROKEN", name, "green" if rc == 0 else text), flush=True)
    print("%s %d/%d" % ("PASS" if not bad else "FAIL", len(M) - bad, len(M)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
