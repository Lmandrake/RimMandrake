#!/usr/bin/env python3
"""Mutation testing of the v3 acceptance machinery, on idle CPU (SteveDesktop first).

mutmut 2.5.1 (pinned: infrastructure/stevedesktop/mutation_requirements.txt) mutates the source file ON DISK in
a throwaway clone and runs a custom runner command, so a selftest that imports the module from its own checkout,
or launches it in a subprocess from that checkout, sees the active mutant. Every shard still proves that before
it is trusted: a reach probe appends `raise RuntimeError(...)` to the module and the runner MUST fail (exit != 0);
a shard whose probe passes is reported UNREACHED and its numbers are not counted.

Never run this in a seat's working clone or the testq runner clone. `launch` makes its own sparse hardlink clones
under ~/mutation/shards/<run>/ from the base clone ~/mutation/RimMandrake (fetched to origin/main first), and runs
each worker as a `systemd-run --user` unit in mutation.slice (Nice=19, idle I/O, a per-unit CPUQuota and a slice
CPUQuota, so the game/testq lane keeps its cores). WSL python only; no worktrees; no tmpfs.

  run_mutation.py targets                         # the module -> selftest map
  run_mutation.py plan [--since SHA | --all]      # targets whose module or selftest changed since the last run
  run_mutation.py launch [--targets a,b] [--changed] [--workers 6] [--gate-phases load]
  run_mutation.py status --run RUN                # per-shard progress
  run_mutation.py collect --run RUN [--copy-to DIR]   # summary.json + summary.md + survivors per module
  run_mutation.py nightly [--workers 6]           # the timer: collect finished runs, launch changed targets

The pre-mutation hook (`_gate`) blocks before each mutant while the testq attempt on this host is in one of the
--gate-phases (default: none; measured 2026-10-27, see the summary's lane section). It never runs inside the timed
test window, so a gate wait cannot turn into a false timeout.

Timeouts (MEASURED by the testing-sim pilot, 2026-10-27): mutmut 2.5.1 killed by an outer timeout leaves the MUTATED
source on disk and its test processes running. So every child here runs in its own process group and a timeout
kills the whole group (run_group); the runner's selftest child also dies with the runner (PR_SET_PDEATHSIG) and a
runner reaps any group its predecessor left (.mut-pgid); and a worker checks `git diff` on the module before the
probe and after mutmut, restoring it from HEAD (source_guard) -- a shard whose source would not restore is
SOURCE_DIRTY and is not counted.
"""
import argparse
import ast
import json
import os
import shutil
import signal
import sqlite3
import subprocess
import tempfile
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
HOME = os.path.expanduser("~")
BASE = os.environ.get("MUTATION_BASE", os.path.join(HOME, "mutation"))
BASE_CLONE = os.path.join(BASE, "RimMandrake")
VENV_PY = os.path.join(BASE, "venv", "bin", "python")
TESTQ = os.environ.get("MUTATION_TESTQ_DIR", "/mnt/d/RimTest/testq")
SPARSE = ["src/RimMandrake/Utils", "src/RimMandrake/rimflow", "src/RimMandrake/contracts", "infrastructure",
          "skills/rimworld-modding"]
PGID_FILE = ".mut-pgid"
PROBE = "\nraise RuntimeError('mutation-reach-probe')\n"

U, R = "src/RimMandrake/Utils/", "src/RimMandrake/rimflow/"
TARGETS = {
    # the property test is ~1.3 s and drives _top_level/lookup/summarize hard (run 20261027a ran without it)
    "close_evidence": (U + "close_evidence.py", [U + "selftest_close_evidence.py",
                                                U + "selftest_close_evidence_props.py",
                                                U + "selftest_close_evidence_mut.py"]),
    "arbiter_tiers": (R + "arbiter_tiers.py", [R + "selftest_arbiter_tiers.py"]),
    "isolated_evidence": (R + "isolated_evidence.py", [R + "selftest_isolated_evidence.py", R + "selftest_isolated_evidence_mut.py"]),
    "dispatcher": (R + "dispatcher.py", [R + "selftest_dispatcher.py", R + "selftest_dispatcher_r2.py", R + "selftest_dispatcher_mut.py", R + "selftest_dispatcher_mut2.py"]),
    "v3_vs_v2": (U + "v3_vs_v2.py", [U + "selftest_v3_vs_v2.py", U + "selftest_v3_vs_v2_props.py", U + "selftest_v3_vs_v2_mut.py"]),
    "delegated_digest": (R + "delegated_digest.py", [R + "selftest_delegated_digest.py", R + "selftest_delegated_digest_mut.py"]),
    # role_launch has no selftest of its own: the dispatcher's, account_pick's and the DST property tests drive it
    "role_launch": (R + "role_launch.py", [R + "selftest_dispatcher.py", R + "selftest_dispatcher_r2.py",
                                           R + "selftest_account_pick.py", R + "selftest_role_launch_props.py", R + "selftest_role_launch.py",
                                           R + "selftest_role_launch_decide_mut.py"]),
}
# Checks that flake for reasons outside the mutated module; a run failing ONLY these counts as a pass for that
# target (otherwise every flake reads as a killed mutant). Each entry names the item that tracks the flake.
FLAKY = {
    # role_launch.scan_marked goes blind on any young same-uid non-dumpable process (a fresh tailscale-ssh session,
    # a transient sh); the check exercises role_launch, not dispatcher.py. Item SCAN_MARKED_HARDEN_YOUNG_SIBLING_BLINDS.
    "dispatcher": ("B1 procs_of on the real /proc sees a live marked process", "B1 procs_of: none once it is gone"),
    # the same flake, tolerated for role_launch too: a mutant that breaks ONLY those two B1 checks reads as survived
    "role_launch": ("B1 procs_of on the real /proc sees a live marked process", "B1 procs_of: none once it is gone"),
}
#: measured selftest seconds per target on SteveDesktop, 2026-10-27 (sizes the shards; 3.0 for a target not here)
BASELINE_S = {"close_evidence": 17.5, "arbiter_tiers": 3.0, "isolated_evidence": 2.0, "dispatcher": 3.4,
              "v3_vs_v2": 3.5, "delegated_digest": 2.2, "role_launch": 5.0}
STATUS = {"ok_killed": "killed", "bad_survived": "survived", "bad_timeout": "timeout",
          "ok_suspicious": "suspicious", "skipped": "skipped", "untested": "untested"}


def sh(argv, cwd=None, check=True, timeout=600):
    p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if check and p.returncode != 0:
        raise SystemExit("FAILED %s: %s" % (" ".join(argv), (p.stderr or p.stdout)[-600:]))
    return p.stdout


def _pdeathsig():
    """preexec_fn: the child gets SIGKILL if its parent (the runner) dies first -- mutmut SIGKILLs a runner that
    exceeds mutmut's own timeout, which would otherwise orphan the selftest."""
    try:
        import ctypes
        ctypes.CDLL("libc.so.6", use_errno=True).prctl(1, signal.SIGKILL)   # 1 = PR_SET_PDEATHSIG
    except Exception:  # noqa: BLE001 - not Linux/glibc: the pgid reaper still covers it
        pass


def kill_group(pgid):
    """SIGKILL a whole process group; True if it existed."""
    try:
        os.killpg(pgid, signal.SIGKILL)
        return True
    except (ProcessLookupError, PermissionError):
        return False


def run_group(argv, timeout, pgid_file=None, **kw):
    """subprocess.run in a NEW process group; on timeout kill the whole group (not just the leader) and return
    (None, output). The group id is written to pgid_file while it runs so a later caller can reap it."""
    p = subprocess.Popen(argv, start_new_session=True, preexec_fn=_pdeathsig, **kw)
    if pgid_file:
        with open(pgid_file, "w") as f:
            f.write(str(p.pid))
    try:
        out, _ = p.communicate(timeout=timeout)
        return p.returncode, out
    except subprocess.TimeoutExpired:
        kill_group(p.pid)
        out, _ = p.communicate()
        return None, out
    finally:
        kill_group(p.pid)          # stragglers the leader left behind even on a normal exit
        if pgid_file and os.path.exists(pgid_file):
            os.remove(pgid_file)


def reap_stale(pgid_file):
    """Kill the group a previous runner recorded and never cleared (it was SIGKILLed mid-test)."""
    try:
        pgid = int(open(pgid_file).read().strip())
    except (OSError, ValueError):
        return False
    os.remove(pgid_file)
    return kill_group(pgid)


def source_guard(relpath, cwd="."):
    """'clean' if relpath matches HEAD; else restore it from HEAD and return 'restored', or 'dirty' if it still
    differs. Never `git checkout --`: the bytes come from `git show HEAD:path`."""
    def same():
        return subprocess.run(["git", "diff", "--quiet", "HEAD", "--", relpath], cwd=cwd).returncode == 0
    if same():
        return "clean"
    head = subprocess.run(["git", "show", "HEAD:" + relpath], cwd=cwd, capture_output=True, check=True).stdout
    with open(os.path.join(cwd, relpath), "wb") as f:
        f.write(head)
    return "restored" if same() else "dirty"


def results_dir():
    return os.environ.get("MUTATION_RESULTS", os.path.join(BASE, "results"))


def test_env():
    env = dict(os.environ)
    env["PATH"] = os.path.join(HOME, ".local", "bin") + os.pathsep + env.get("PATH", "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    # an empty, private cache root: never read a stale .pyc of the un-mutated module
    env["PYTHONPYCACHEPREFIX"] = os.path.join(os.getcwd(), ".mut-pycache-none")
    return env


# --- pure helpers (selftest_run_mutation.py covers these) ----------------------------------------------------------

def func_spans(source):
    """[(first_line, last_line, qualname)] for every def, innermost resolvable by narrowest span."""
    out = []

    def walk(node, prefix):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                q = prefix + ch.name
                start = min([ch.lineno] + [d.lineno for d in getattr(ch, "decorator_list", [])])
                if not isinstance(ch, ast.ClassDef):
                    out.append((start, ch.end_lineno, q))
                walk(ch, q + ".")
            else:
                walk(ch, prefix)
    walk(ast.parse(source), "")
    return out


def func_of(spans, line):
    best = None
    for a, b, q in spans:
        if a <= line <= b and (best is None or b - a < best[1] - best[0]):
            best = (a, b, q)
    return best[2] if best else "<module>"


def split_lines(weights, n):
    """Split {line: mutant_count} into n contiguous groups of near-equal weight. Returns [[lines], ...]."""
    lines = sorted(weights)
    total = sum(weights.values())
    n = max(1, min(n, len(lines) or 1))
    groups, cur, acc, k = [], [], 0, 1
    for ln in lines:
        cur.append(ln)
        acc += weights[ln]
        if acc >= total * k / n and len(groups) < n - 1:
            groups.append(cur)
            cur, k = [], k + 1
    if cur or not groups:
        groups.append(cur)
    return groups


def patch_text(relpath, source_lines, lines):
    """A unified diff that marks exactly `lines` (1-based) as added, for mutmut --use-patch-file."""
    out = ["--- %s" % relpath, "+++ %s" % relpath]
    for ln in sorted(lines):
        out.append("@@ -0,0 +%d,1 @@" % ln)
        out.append("+" + source_lines[ln - 1])
    return "\n".join(out) + "\n"


def plan_costs(costs, workers):
    """Greedy LPT: [(name, cost)] -> list of `workers` bins [[name,...]]."""
    bins = [[0.0, []] for _ in range(max(1, workers))]
    for name, c in sorted(costs, key=lambda x: -x[1]):
        b = min(bins, key=lambda x: x[0])
        b[0] += c
        b[1].append(name)
    return [b[1] for b in bins if b[1]]


def gate_blocked(testq_dir, phases):
    """True when this host's current testq attempt is alive in one of `phases`."""
    if not phases:
        return False
    try:
        aid = open(os.path.join(testq_dir, "current")).read().strip()
        st_path = os.path.join(testq_dir, "attempts", aid, "state.json")
        st = json.load(open(st_path))
        if os.path.exists(os.path.join(testq_dir, "attempts", aid, "result.json")):
            return False
        if time.time() - os.stat(st_path).st_mtime > 900:
            return False
        return st.get("phase") in phases
    except (OSError, ValueError):
        return False


# --- mutant inventory ----------------------------------------------------------------------------------------------

def mutant_lines(path):
    import mutmut
    src = open(path).read()
    ctx = mutmut.Context(source=src, filename=path)
    w = {}
    for mid in mutmut.list_mutations(ctx):
        w[mid.line_number + 1] = w.get(mid.line_number + 1, 0) + 1
    return w


# --- worker side ---------------------------------------------------------------------------------------------------

def cmd_runtests(a):
    _mod, tests = TARGETS[a.target]
    env = test_env()
    reap_stale(PGID_FILE)
    for t in tests:
        if not os.path.exists(t):
            continue
        # private TMPDIR per selftest run, removed after: selftests leak mkdtemp dirs, and thousands of mutants
        # exhausted the /tmp tmpfs inodes on SteveDesktop (2026-10-28), killing the Claude runner (ENOSPC)
        tmpd = tempfile.mkdtemp(prefix="mutrun_")
        try:
            rc, out = run_group([sys.executable, t], a.timeout, pgid_file=PGID_FILE, env=dict(env, TMPDIR=tmpd),
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
        finally:
            shutil.rmtree(tmpd, ignore_errors=True)
        if rc is None:
            return 1               # our own timeout: the group is dead; mutmut normally times out first
        if rc != 0 and not only_flaky(out, FLAKY.get(a.target, ())):
            return 1
    return 0


def only_flaky(output, flaky):
    """True when every FAIL line of a selftest's output is one of the known `flaky` checks (and there is one)."""
    fails = [ln for ln in output.splitlines() if ln.startswith("FAIL")]
    return bool(fails) and bool(flaky) and all(any(f in ln for f in flaky) for ln in fails)


def cmd_gate(a):
    phases = [x for x in (a.phases or "").split(",") if x]
    waited = 0
    while gate_blocked(TESTQ, phases):
        time.sleep(15)
        waited += 15
    if waited:
        with open(".gate_waits", "a") as f:
            f.write("%s %d\n" % (time.strftime("%Y-%m-%dT%H:%M:%S"), waited))
    return 0


def runner_cmd(target, timeout=600):
    return "%s %s _runtests --target %s --timeout %d" % (VENV_PY, os.path.abspath(__file__), target, timeout)


def reach_probe(target):
    """Apply a deliberately-fatal mutant; the runner must fail. Returns (reached, seconds)."""
    mod = TARGETS[target][0]
    orig = open(mod).read()
    t = time.time()
    try:
        with open(mod, "w") as f:
            f.write(orig + PROBE)
        rc, _ = run_group(runner_cmd(target).split(), 900, env=test_env())
        rc = 1 if rc is None else rc
    finally:
        with open(mod, "w") as f:
            f.write(orig)
    return rc != 0, round(time.time() - t, 1)


def export_shard(shard_dir, target):
    mod = TARGETS[target][0]
    src = open(os.path.join(shard_dir, mod)).read()
    spans = func_spans(src)
    db = sqlite3.connect(os.path.join(shard_dir, ".mutmut-cache"))
    rows = db.execute("select m.id, m.status, l.line_number, l.line from Mutant m join Line l on m.line = l.id").fetchall()
    out = []
    for mid, status, ln0, line in rows:
        rec = {"id": mid, "status": STATUS.get(status, status), "line": ln0 + 1, "func": func_of(spans, ln0 + 1),
               "source": (line or "").strip()[:200]}
        if rec["status"] in ("survived", "timeout"):
            rec["diff"] = subprocess.run([VENV_PY, "-m", "mutmut", "show", str(mid)], cwd=shard_dir,
                                         capture_output=True, text=True, timeout=120).stdout[-1500:]
        out.append(rec)
    return out


def cmd_worker(a):
    jobs = json.load(open(a.jobs))
    for job in jobs:
        d = job["dir"]
        os.chdir(d)
        st = {"target": job["target"], "shard": job["shard"], "started": time.time(), "state": "probe"}
        json.dump(st, open("shard_state.json", "w"))
        mod = TARGETS[job["target"]][0]
        st["source_before"] = source_guard(mod)
        if st["source_before"] == "dirty":
            st.update(state="SOURCE_DIRTY", ended=time.time())
            json.dump(st, open("shard_state.json", "w"))
            continue
        reached, probe_s = reach_probe(job["target"])
        st.update(reach_probe_failed_runner=reached, probe_s=probe_s)
        if not reached:
            st.update(state="UNREACHED", ended=time.time())
            json.dump(st, open("shard_state.json", "w"))
            continue
        st["state"] = "mutating"
        json.dump(st, open("shard_state.json", "w"))
        argv = [VENV_PY, "-m", "mutmut", "run", "--paths-to-mutate", TARGETS[job["target"]][0],
                "--tests-dir", ".mut-tests", "--runner", runner_cmd(job["target"]),
                "--use-patch-file", "shard.patch", "--simple-output", "--no-progress",
                "-m", "4.0", "-b", "20"]
        if job.get("gate_phases"):
            argv += ["--pre-mutation", "%s %s _gate --phases %s" % (VENV_PY, os.path.abspath(__file__),
                                                                    job["gate_phases"])]
        os.makedirs(".mut-tests", exist_ok=True)
        with open("mutmut_run.log", "w") as log:
            rc, _ = run_group(argv, job.get("shard_timeout_s"), stdout=log, stderr=subprocess.STDOUT, env=test_env())
        reap_stale(PGID_FILE)
        st.update(mutmut_rc=rc, state="exporting", source_after=source_guard(mod))
        if st["source_after"] == "dirty":     # a mutant would leak into every later run: count nothing
            st.update(state="SOURCE_DIRTY", ended=time.time())
            json.dump(st, open("shard_state.json", "w"))
            continue
        if rc is None:                         # killed at the shard budget: what mutmut recorded still counts
            st["shard_timed_out"] = True
            rc = 0
        if rc & 1 and "Checking mutants" not in open("mutmut_run.log", errors="replace").read():
            st.update(state="baseline_failed", ended=time.time())
            json.dump(st, open("shard_state.json", "w"))
            continue
        json.dump(st, open("shard_state.json", "w"))
        try:
            json.dump(export_shard(d, job["target"]), open("mutants.json", "w"), indent=0)
            st["state"] = "done"
        except Exception as e:  # noqa: BLE001 - recorded, collect reports it
            st.update(state="export_failed", error=repr(e))
        st["ended"] = time.time()
        json.dump(st, open("shard_state.json", "w"))
    return 0


# --- controller side -----------------------------------------------------------------------------------------------

def last_run_path():
    return os.path.join(results_dir(), "last_run.json")


def changed_targets(since, repo=BASE_CLONE):
    files = set(sh(["git", "diff", "--name-only", since, "origin/main"], cwd=repo).split())
    return [n for n, (m, ts) in TARGETS.items() if m in files or files.intersection(ts)]


def last_shas(last):
    """{target: sha it was last COMPLETELY mutated at} from last_run.json. The old one-sha form covers every target."""
    if not last:
        return {}
    if isinstance(last.get("targets"), dict):
        return {n: v.get("sha") for n, v in last["targets"].items() if v.get("sha")}
    return {n: last["sha"] for n in TARGETS} if last.get("sha") else {}


def due_targets(shas, changed):
    """Targets to mutate: never completed, or whose module/selftests changed since their own last sha.
    `changed(since)` -> [target names changed since that sha] (git diff in the base clone)."""
    out = [n for n in TARGETS if n not in shas]
    for since in sorted(set(shas.values())):
        hit = set(changed(since))
        out += [n for n in TARGETS if shas.get(n) == since and n in hit and n not in out]
    return [n for n in TARGETS if n in out]


def read_last():
    return json.load(open(last_run_path())) if os.path.exists(last_run_path()) else None


def cmd_plan(a):
    if a.all:
        print("\n".join(TARGETS))
        return 0
    sh(["git", "fetch", "-q", "origin", "main"], cwd=BASE_CLONE)
    shas = {n: a.since for n in TARGETS} if a.since else last_shas(read_last())
    print("\n".join(due_targets(shas, changed_targets)))
    return 0


SPARSE_EXTRA = {"delegated_digest": ["src"]}   # its selftest scans the repo's XML for >=500 defNames (blind_core.def_names)


def prepare_clone(dst, sha, target=""):
    sh(["git", "clone", "-q", "--local", "--no-checkout", BASE_CLONE, dst])
    sh(["git", "sparse-checkout", "set"] + SPARSE + SPARSE_EXTRA.get(target, []), cwd=dst)
    sh(["git", "checkout", "-q", sha], cwd=dst)


def cmd_launch(a):
    sh(["git", "fetch", "-q", "origin", "main"], cwd=BASE_CLONE)
    sh(["git", "checkout", "-q", "--detach", "origin/main"], cwd=BASE_CLONE)
    sha = sh(["git", "rev-parse", "HEAD"], cwd=BASE_CLONE).strip()
    if a.changed:
        names = due_targets(last_shas(read_last()), changed_targets)
    else:
        names = [x for x in a.targets.split(",") if x] if a.targets else list(TARGETS)
    if not names:
        print("nothing changed since the last run")
        return 0
    base_s = json.loads(a.baseline_s) if a.baseline_s else {}
    run = a.run or time.strftime("%Y%m%dT%H%M%S")
    root = os.path.join(BASE, "shards", run)
    os.makedirs(root)
    # shard each target in proportion to its cost (mutants x baseline seconds)
    weights = {n: mutant_lines(os.path.join(BASE_CLONE, TARGETS[n][0])) for n in names}
    cost = {n: sum(weights[n].values()) * float(base_s.get(n, 3.0)) for n in names}
    unit = sum(cost.values()) / max(1, a.workers)
    shards = []
    for n in names:
        k = max(1, min(a.max_shards, int(round(cost[n] / unit)) or 1))
        src_lines = open(os.path.join(BASE_CLONE, TARGETS[n][0])).read().split("\n")
        for i, lines in enumerate(split_lines(weights[n], k)):
            d = os.path.join(root, "%s-%d" % (n, i))
            prepare_clone(d, sha, n)
            with open(os.path.join(d, "shard.patch"), "w") as f:
                f.write(patch_text(TARGETS[n][0], src_lines, lines))
            shards.append({"dir": d, "target": n, "shard": i, "mutants": sum(weights[n][x] for x in lines),
                           "cost": sum(weights[n][x] for x in lines) * float(base_s.get(n, 3.0)),
                           "gate_phases": a.gate_phases, "shard_timeout_s": a.shard_timeout_h * 3600})
    bins = plan_costs([(s["dir"], s["cost"]) for s in shards], a.workers)
    by_dir = {s["dir"]: s for s in shards}
    sh(["systemctl", "--user", "set-property", "--runtime", "mutation.slice", "CPUQuota=%s" % a.slice_quota],
       check=False)
    meta = {"run": run, "sha": sha, "targets": names, "workers": len(bins), "slice_cpu_quota": a.slice_quota,
            "unit_cpu_quota": a.unit_quota, "gate_phases": a.gate_phases, "started": time.time(), "units": []}
    for i, b in enumerate(bins):
        jf = os.path.join(root, "worker-%d.json" % i)
        json.dump([by_dir[x] for x in b], open(jf, "w"), indent=1)
        unit_name = "mutation-%s-w%d" % (run, i)
        sh(["systemd-run", "--user", "--unit", unit_name, "--slice", "mutation.slice",
            "-p", "Nice=19", "-p", "IOSchedulingClass=idle", "-p", "CPUQuota=%s" % a.unit_quota,
            "-p", "MemoryMax=4G", "--working-directory", root,
            VENV_PY, os.path.abspath(__file__), "_worker", "--jobs", jf])
        meta["units"].append(unit_name)
    json.dump(meta, open(os.path.join(root, "run.json"), "w"), indent=1)
    print(json.dumps({k: meta[k] for k in ("run", "sha", "targets", "workers")}))
    print("shards:", len(shards), "->", root)
    return 0


def shard_states(root):
    out = []
    for d in sorted(os.listdir(root)):
        p = os.path.join(root, d, "shard_state.json")
        if os.path.isdir(os.path.join(root, d)):
            st = json.load(open(p)) if os.path.exists(p) else {"state": "queued"}
            st["dir"] = d
            out.append(st)
    return out


def cmd_status(a):
    root = os.path.join(BASE, "shards", a.run)
    for st in shard_states(root):
        done = ""
        cache = os.path.join(root, st["dir"], ".mutmut-cache")
        if os.path.exists(cache):
            try:
                db = sqlite3.connect("file:%s?mode=ro" % cache, uri=True, timeout=5)
                done = dict(db.execute("select status, count(*) from Mutant group by status").fetchall())
            except sqlite3.Error as e:
                done = repr(e)
        print(st["dir"], st.get("state"), done)
    return 0


def summarize(root):
    meta = json.load(open(os.path.join(root, "run.json")))
    mods = {}
    for st in shard_states(root):
        t = st.get("target") or st["dir"].rsplit("-", 1)[0]
        m = mods.setdefault(t, {"mutants": 0, "killed": 0, "survived": 0, "timeout": 0, "suspicious": 0,
                                "skipped": 0, "untested": 0, "shards": 0, "unreached_shards": 0,
                                "cpu_wall_s": 0.0, "survivors": []})
        m["shards"] += 1
        if st.get("state") == "UNREACHED":
            m["unreached_shards"] += 1
        if st.get("state") in ("baseline_failed", "export_failed", "SOURCE_DIRTY"):
            m.setdefault("failed_shards", []).append(st["dir"])
        if st.get("ended") and st.get("started"):
            m["cpu_wall_s"] += st["ended"] - st["started"]
        mp = os.path.join(root, st["dir"], "mutants.json")
        if os.path.exists(mp):
            for r in json.load(open(mp)):
                m["mutants"] += 1
                m[r["status"]] = m.get(r["status"], 0) + 1
                if r["status"] in ("survived", "timeout"):
                    m["survivors"].append(r)
    for m in mods.values():
        tested = m["killed"] + m["survived"] + m["timeout"] + m["suspicious"]
        m["score"] = round((m["killed"] + m["timeout"] + m["suspicious"]) / tested, 3) if tested else None
        m["cpu_wall_s"] = round(m["cpu_wall_s"])
    return meta, mods


def cmd_collect(a):
    root = os.path.join(BASE, "shards", a.run)
    meta, mods = summarize(root)
    out = os.path.join(results_dir(), a.run)
    os.makedirs(out, exist_ok=True)
    json.dump({"meta": meta, "modules": mods}, open(os.path.join(out, "summary.json"), "w"), indent=1)
    lines = ["# Mutation run %s @ %s" % (meta["run"], meta["sha"][:10]), "",
             "| module | mutants | killed | survived | timeout | suspicious | score | shard wall s | unreached |",
             "|---|---|---|---|---|---|---|---|---|"]
    for n, m in sorted(mods.items()):
        lines.append("| %s | %d | %d | %d | %d | %d | %s | %d | %d |" % (
            n, m["mutants"], m["killed"], m["survived"], m["timeout"], m["suspicious"], m["score"],
            m["cpu_wall_s"], m["unreached_shards"]))
    lines.append("")
    for n, m in sorted(mods.items()):
        byf = {}
        for r in m["survivors"]:
            byf.setdefault(r["func"], []).append(r)
        lines.append("## %s survivors by function" % n)
        for f, rs in sorted(byf.items(), key=lambda x: -len(x[1])):
            lines.append("- %s: %d (lines %s)" % (f, len(rs), ",".join(str(r["line"]) for r in rs[:12])))
        lines.append("")
    open(os.path.join(out, "summary.md"), "w").write("\n".join(lines))
    states = shard_states(root)
    done = all(st.get("state") in ("done", "UNREACHED", "export_failed", "baseline_failed") for st in states)
    if done:
        last = read_last() or {}
        tg = {n: {"sha": s} for n, s in last_shas(last).items()}
        for n, m in mods.items():            # only a target whose every shard finished cleanly is up to date
            if not m.get("failed_shards") and not m["unreached_shards"]:
                tg[n] = {"sha": meta["sha"], "run": meta["run"], "ended": time.time()}
        json.dump({"targets": tg}, open(last_run_path(), "w"), indent=1)
        open(os.path.join(root, "collected"), "w").write(meta["sha"] + "\n")
    if a.copy_to:
        dst = os.path.join(a.copy_to, a.run)
        shutil.copytree(out, dst, dirs_exist_ok=True)
    print(os.path.join(out, "summary.md"), "complete" if done else "PARTIAL")
    return 0


def active_units():
    out = sh(["systemctl", "--user", "list-units", "--plain", "--no-legend", "--state=active", "mutation-*"],
             check=False)
    return [ln.split()[0] for ln in out.splitlines() if ln.strip()]


def cmd_nightly(a):
    """The timer's job: skip while any mutation unit still runs; collect every finished, uncollected run (copied to
    MUTATION_COPY_TO when set); then launch only the targets that changed since their own last complete run."""
    busy = active_units()
    if busy:
        print("busy: %d mutation unit(s) still active (%s); nothing launched" % (len(busy), busy[0]))
        return 0
    root = os.path.join(BASE, "shards")
    for run in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        d = os.path.join(root, run)
        if os.path.exists(os.path.join(d, "run.json")) and not os.path.exists(os.path.join(d, "collected")):
            cmd_collect(argparse.Namespace(run=run, copy_to=os.environ.get("MUTATION_COPY_TO") or None))
    return cmd_launch(argparse.Namespace(
        changed=True, targets=None, workers=a.workers, max_shards=a.max_shards, unit_quota=a.unit_quota,
        slice_quota=a.slice_quota, gate_phases=a.gate_phases, baseline_s=a.baseline_s, run=None))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("targets")
    p = sp.add_parser("plan")
    p.add_argument("--since")
    p.add_argument("--all", action="store_true")
    for name in ("launch", "nightly"):
        p = sp.add_parser(name)
        p.add_argument("--workers", type=int, default=6)
        p.add_argument("--max-shards", type=int, default=6)
        p.add_argument("--unit-quota", default="100%")
        p.add_argument("--slice-quota", default="600%")
        p.add_argument("--gate-phases", default="")
        p.add_argument("--shard-timeout-h", type=float, default=10.0,
                       help="kill a shard's whole mutmut process group after this long; its recorded results count")
        p.add_argument("--baseline-s", default=json.dumps(BASELINE_S), help='JSON {"target": s per selftest run}')
        if name == "launch":
            p.add_argument("--targets")
            p.add_argument("--changed", action="store_true")
            p.add_argument("--run")
    for name in ("status", "collect"):
        p = sp.add_parser(name)
        p.add_argument("--run", required=True)
        p.add_argument("--copy-to")
    p = sp.add_parser("_runtests")
    p.add_argument("--target", required=True)
    p.add_argument("--timeout", type=int, default=600)
    p = sp.add_parser("_gate")
    p.add_argument("--phases", default="")
    p = sp.add_parser("_worker")
    p.add_argument("--jobs", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "targets":
        for n, (m, ts) in TARGETS.items():
            print(n, m, " ".join(ts))
        return 0
    return {"plan": cmd_plan, "launch": cmd_launch, "nightly": cmd_nightly, "status": cmd_status, "collect": cmd_collect,
            "_runtests": cmd_runtests, "_gate": cmd_gate, "_worker": cmd_worker}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
