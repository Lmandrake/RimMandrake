#!/usr/bin/env python3
"""Selftest: a detached run's stop steps (finish, wrapup, return) do not depend on the LAUNCHER's clone surviving
(RIMMANDRAKE_RUN_FINISH_WITHOUT_LAUNCHER_CLONE_HOLDER_LOST_RESULT). Explosive Knockback's first holder run
(rm-detached-bench-rimmandrake-fix-dry-pit-hauler-descent-s-1794813498, 2026-11-15) ended with "can't open file
.../RIMMANDRAKE_START_PILOT_STAGE_RUNS_FROM_LEDGER_PACKET.det/src/RimMandrake/rimflow/detached_helper.py": its
ExecStopPost named the clone pilot-launch ran in, deleted by then, so finish never ran and its result read "unknown".

Each step now resolves its script at stop time from candidates: finish and wrapup try the run's own clone first (it
lives until the return, the last step), then the launcher's, then the seat clones; the return, which deletes the run's
clone, tries the launcher's and the seat clones before it. The live half runs a real transient systemd unit whose
ExecStopPost is the resolver with the first candidate missing (skipped where systemd-run --user is absent).

    python3 src/RimMandrake/rimflow/selftest_stop_steps_outlive_launcher.py
"""
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import detached_helper as DH    # noqa: E402

res = []


def check(name, ok, detail=""):
    res.append(bool(ok))
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)[:400]))


tmp = tempfile.mkdtemp(prefix="stopsteps_")
run_clone = os.path.join(tmp, "runclone")
rel = os.path.join("src", "RimMandrake", "rimflow")
os.makedirs(os.path.join(run_clone, rel))
for f in ("detached_helper.py", "wrapup.py"):
    open(os.path.join(run_clone, rel, f), "w").close()
rec = {"clone": run_clone, "unit": "rm-detached-bench-x-1", "seat": "BENCH", "max_s": None, "state": tmp,
       "model": "opus", "item": "I", "budget_usd": 1.0, "out": os.path.join(tmp, "o"), "err": os.path.join(tmp, "e"),
       "env": {}}
argv = DH.launch_argv(rec, "brief", "/usr/bin/claude")
posts = [argv[i + 1][len("ExecStopPost="):] for i, a in enumerate(argv[:-1])
         if a == "-p" and argv[i + 1].startswith("ExecStopPost=")]
check("three stop steps", len(posts) == 3, posts)
me = os.path.abspath(DH.__file__)
finish, wrapup, back = posts if len(posts) == 3 else ("", "", "")
check("finish does not name only the launcher's detached_helper.py (it resolves among candidates)",
      DH.STOP_RESOLVER_MARK in finish, finish)
check("finish tries the run's own clone first, then the launcher's", finish.find(
    os.path.join(run_clone, rel, "detached_helper.py")) != -1 and finish.find(os.path.join(run_clone, rel)) <
    finish.find(me), finish)
check("wrapup resolves too, the run's clone first", DH.STOP_RESOLVER_MARK in wrapup and
      os.path.join(run_clone, rel, "wrapup.py") in wrapup, wrapup)
check("the return resolves, the run's clone (which it deletes) last", DH.STOP_RESOLVER_MARK in back and
      back.rfind(os.path.join(run_clone, rel)) > back.find(me), back)
check("the stop lines carry no '$' or '%' (systemd would expand them)", not any(c in p for p in posts for c in "$%"),
      posts)

# the resolver itself, offline: first candidate missing -> the second runs with the arguments
out = os.path.join(tmp, "ran.txt")
good = os.path.join(tmp, "good.py")
with open(good, "w") as fh:
    fh.write("import sys\nopen(%r, 'w').write(' '.join(sys.argv[1:]))\n" % out)
cmd = DH.stop_resolver([os.path.join(tmp, "gone", "detached_helper.py"), good], ["finish", "--unit", "U"])
r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
check("the resolver skips a gone candidate and runs the next with the step's arguments",
      r.returncode == 0 and os.path.exists(out) and open(out).read() == "finish --unit U", (r.returncode, r.stderr))
r = subprocess.run(DH.stop_resolver([os.path.join(tmp, "gone", "a.py")], ["finish"]), capture_output=True, text=True,
                   timeout=60)
check("no candidate left: it fails loudly, naming what it tried", r.returncode != 0 and "gone" in r.stderr, r.stderr)

# live: a real transient unit whose ExecStopPost is the resolver line, first candidate gone
if shutil.which("systemd-run") and subprocess.run(["systemctl", "--user", "is-system-running"], capture_output=True,
                                                    text=True).stdout.strip() in ("running", "degraded"):
    os.remove(out)
    unit = "rm-selftest-stopsteps-%d" % os.getpid()
    line = shlex.join(DH.stop_resolver([os.path.join(tmp, "gone", "detached_helper.py"), good], ["finish", "--unit",
                                                                                                   "U"]))
    r = subprocess.run(["systemd-run", "--user", "--quiet", "--collect", "--unit", unit, "-p", "ExecStopPost=" + line,
                        "/bin/true"], capture_output=True, text=True, timeout=60)
    for _ in range(100):
        if os.path.exists(out):
            break
        time.sleep(0.1)
    check("live: a systemd unit's ExecStopPost runs the resolver past a gone launcher clone",
          r.returncode == 0 and os.path.exists(out) and open(out).read() == "finish --unit U", (r.returncode, r.stderr))
else:
    print("UNRUN live half: no systemd-run --user here")
shutil.rmtree(tmp, ignore_errors=True)
print("PASS %d/%d" % (sum(res), len(res)) if all(res) else "FAIL %d of %d" % (res.count(False), len(res)))
sys.exit(0 if all(res) else 1)
