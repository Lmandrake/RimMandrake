#!/usr/bin/env python3
"""selftest_known_results.py - the known-result ledger: a false "unchanged" is worse than a rerun.

Three layers, all real:
  1. `decide(K)`: known_results.py's decisions on hand-built traces and real files. Taint table, invalidation table,
     red and no-verdict handling, record cap, audit sample.
  2. Mutants: the same `decide` run over known_results.py with one decision broken at a time. Every mutant must be
     caught; a mutant that survives is a check that checks nothing, and fails this test.
  3. The real runner, with the real shim and tracer, on a fixture repo (RM_SELFTEST_KNOWN_RESULTS=1): dependencies are
     MEASURED (transitive import, data file, listing, env, tool binary, a file that appears, a shadowing module), every
     never-cache class stays uncached, a red is never returned, and a planted hidden dependency the key cannot see is
     caught by the nightly's audit, alarmed, deleted and quarantined.

    python3 src/RimMandrake/Utils/selftest_known_results.py
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNER = HERE / "run_selftests.py"
SOURCE = HERE / "known_results.py"
SCRATCH = Path("/home/mandrake/rm/scratch/BENCH") if Path("/home/mandrake/rm").is_dir() else HERE.parents[2] / ".scratch"
FAILS = []


def eq(got, want, what):
    print(("ok   " if got == want else "FAIL ") + what + ("" if got == want else f"  - got {got!r}, want {want!r}"))
    if got != want:
        FAILS.append(what)


def load(source_text=None):
    """known_results as a module, from its file or from a mutated copy of its text."""
    spec = importlib.util.spec_from_file_location(f"kr_{os.getpid()}_{id(source_text)}", SOURCE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod            # dataclass-free, but annotations resolve through it
    if source_text is None:
        spec.loader.exec_module(mod)
    else:
        mod.__dict__["__file__"] = str(SOURCE)
        exec(compile(source_text, str(SOURCE), "exec"), mod.__dict__)
    return mod


# --- layer 1: the decisions, on traces written by hand ---------------------------------------------------------------------
def trace(d: Path, lines, py=None, start=True):
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    if lines is not None:
        (d / "100.native").write_text("\n".join(lines) + "\n")
    if py is not None:
        if start:
            (d / "100.start").write_text("")
        (d / "100.json").write_text(py if isinstance(py, str) else json.dumps(py))
    elif not start:
        (d / "100.start").write_text("")
    return d


def decide(K, root: Path) -> list:
    """Every decision the ledger makes. Returns the names of those that came out wrong; `check` also prints in layer 1."""
    wrong = []

    def check(ok, what):
        if not ok:
            wrong.append(what)

    shutil.rmtree(root, ignore_errors=True)
    repo = (root / "repo").resolve()
    (repo / "sub").mkdir(parents=True)
    (repo / ".git").mkdir()
    (repo / ".git/HEAD").write_text("ref")
    (repo / "a.txt").write_text("one")
    (repo / "sub/x").write_text("x")
    (repo / "probe.txt").write_text("12345")
    tr, own = root / "trace", str(root / "tmp" / "own")
    Path(own).mkdir(parents=True)
    later = time.time() + 60                       # `started` after every file above: nothing "changed during the run"
    SH = "@ /bin/sh"

    def refused(lines, py=None, start=True, started=later):
        return K.analyse(trace(tr, lines, py, start), repo, own, started)["refused"]

    def has(reasons, word):
        return any(word in r for r in reasons)

    # what must not be cached
    for label, lines, word in [
        ("clock shim line", [SH, "C clock"], "clock"),
        ("date binary", [SH, "X /usr/bin/date", "@ /usr/bin/date"], "clock"),
        ("network", [SH, "N 1.2.3.4:80"], "network"),
        ("unix socket", [SH, "U /run/x"], "network"),
        ("meminfo", [SH, "R /proc/meminfo"], "machine state"),
        ("sysfs", [SH, "R /sys/class/x"], "machine state"),
        ("a device", [SH, "R /dev/sda"], "machine state"),
        ("live game path", [SH, "R /mnt/c/Program Files/x"], "external"),
        ("a stat of the live game", [SH, "S /mnt/c/Program Files/x"], "external"),
        ("other mount", [SH, "L /media/x"], "external"),
        ("git state", [SH, f"R {repo}/.git/HEAD"], "git state"),
        ("read and written", [SH, f"R {repo}/a.txt", f"W {repo}/a.txt"], "reads and writes"),
        ("a shared temp file", [SH, "R /tmp/zz-known-results"], "shared temp"),
    ]:
        check(has(refused(lines), word), f"refuses {label}")
    check(has(refused([SH], {"taint": ["socket.connect"]}), "taint"), "refuses a python taint")
    check(has(refused([SH], "{broken"), "unreadable"), "refuses an unreadable tracer file")

    # no observation, no record
    check(has(refused(None), "wrote nothing"), "refuses when the shim wrote nothing")
    check(has(refused([SH, "X /bin/true"]), "unobserved"), "refuses an exec that landed unseen")
    check(not refused([SH, "X /bin/nope", "F /bin/nope"]), "a failed exec needs no landing")
    check(not refused([SH, "X /bin/true", "@ /bin/true"]), "a landed exec is fine")
    check(has(refused(["@ /usr/bin/python3.14"]), "without the tracer"), "refuses python with no tracer")
    check(has(refused(["@ /usr/bin/python3.14"], None, start=False), "died"), "refuses python that left no trace")
    check(not refused(["@ /usr/bin/python3.14"], {}), "python with a tracer is seen")

    # what is no input
    for label, line in [("/proc/self", "R /proc/self/status"), ("/dev/null", "R /dev/null"), ("own tmp", f"R {own}/f"),
                        ("own tmp write", f"W {own}/f")]:
        check(not refused([SH, line]), f"does not refuse {label}")
    check(not refused([SH], {"taint": ["os.fork", "os.exec"]}), "exec taints are covered by the landing count")

    m = K.analyse(trace(tr, [SH, f"R {repo}/a.txt", f"R {repo}/gone", f"L {repo}/sub", f"S {repo}/probe.txt", "E FIX_K",
                             "E TMPDIR"]), repo, own, later)
    check(str(repo / "a.txt") in m["files"], "a read file is an input")
    check(str(repo / "gone") in m["absent"], "a read of nothing is an input")
    check(str(repo / "sub") in m["lists"], "a listing is an input")
    check(str(repo / "probe.txt") in m["probes"], "a stat is an input")
    check("FIX_K" in m["env"] and "PATH" in m["env"], "env read and env always are inputs")
    check("TMPDIR" not in m["env"], "a per-run env name is not")
    check("/bin/sh" in m["files"], "the tool binary is an input")
    m = K.analyse(trace(tr, [SH], {"modules": ["/x/ext.so"], "imports": ["a.b"], "import_dirs": [str(repo / "sub")]}), repo, own, later)
    check("a" in m["imports"] and "b" in m["imports"], "import names split on dots")
    check(str(repo / "sub") in m["import_dirs"], "an import dir is an input")

    d = trace(tr, [SH, f"L {repo}/sub"], {"import_dirs": [str(repo / "sub")], "imports": ["q"]})
    m = K.analyse(d, repo, own, later)
    check(str(repo / "sub") in m["import_dirs"] and str(repo / "sub") not in m["lists"], "python's import listing filters by name")
    (d / "101.native").write_text(f"{SH}\nL {repo}/sub\n")
    m = K.analyse(d, repo, own, later)
    check(str(repo / "sub") in m["lists"], "another process listing the same dir is a full listing")

    # changed during the run: a real file touched after `started`
    now = time.time()
    check(has(refused([SH, f"R {repo}/a.txt"], started=now), "changed during"), "refuses an input touched mid-run")
    check(has(refused([SH, f"L {repo}/sub"], started=now), "changed during"), "refuses a listing touched mid-run")
    check(K.moved([str(repo / "gone")], now) == "", "a vanished path is left to the hash")

    # the ledger: record, hit, every way to miss
    state = root / "state"
    env0 = dict(os.environ)
    os.environ.pop("FIX_K", None)
    try:
        led = K.Ledger(repo, state)
        test = repo / "a.txt"
        lines = [SH, f"R {repo}/a.txt", f"R {repo}/gone", f"L {repo}/sub", f"S {repo}/probe.txt", "E FIX_K"]

        def put(rel="t", st="PASS", ln=None, started=later):
            return led.record(rel, st, 1.0, trace(tr, ln or lines), own, started, test)

        check(put() == (True, ""), "a clean PASS records")
        rec, why = led.lookup("t")
        check(rec is not None and rec["state"] == "PASS", "same world: answered")

        def misses(what, change, undo):
            change()
            r, w = led.lookup("t")
            check(r is None and w, f"{what} misses")
            undo()
            r, _ = led.lookup("t")
            check(r is not None, f"{what}: undone, answers again")

        p = repo / "a.txt"
        misses("same-size edit", lambda: p.write_text("two"), lambda: p.write_text("one"))
        misses("a file appears", lambda: (repo / "gone").write_text("y"), lambda: (repo / "gone").unlink())
        misses("a listed file appears", lambda: (repo / "sub/y").write_text("y"), lambda: (repo / "sub/y").unlink())
        misses("a stat's size", lambda: (repo / "probe.txt").write_text("123456"), lambda: (repo / "probe.txt").write_text("12345"))
        misses("an env value", lambda: os.environ.__setitem__("FIX_K", "1"), lambda: os.environ.pop("FIX_K"))
        misses("an always-env value", lambda: os.environ.__setitem__("LC_COLLATE", "zz"),
               lambda: os.environ.pop("LC_COLLATE") if "LC_COLLATE" not in env0 else os.environ.__setitem__("LC_COLLATE", env0["LC_COLLATE"]))
        led.version, keep = "other", led.version
        check(led.lookup("t")[0] is None, "another runner, tracer or package set misses")
        led.version = keep

        # import dirs: only a name the test tried to import counts
        rel = "imp"
        check(led.record(rel, "PASS", 1, trace(tr, [SH], {"imports": ["shadow"], "import_dirs": [str(repo / "sub")]}), own,
                         later, test)[0], "an import-dir record saves")
        (repo / "sub/other.py").write_text("")
        check(led.lookup(rel)[0] is not None, "an unrelated new module does not miss")
        (repo / "sub/shadow.py").write_text("")
        check(led.lookup(rel)[0] is None, "a module that would shadow the import misses")
        (repo / "sub/shadow.py").unlink()
        (repo / "sub/other.py").unlink()

        # a red is on file and says so; no verdict leaves nothing
        check(put("red", "FAIL")[0], "a FAIL records")
        rec, _ = led.lookup("red")
        check(rec is not None and rec["state"] == "FAIL", "a red stays a red")
        for st in ("CRASH", "UNMEASURED"):
            check(put("nov", st)[0] is False and led.lookup("nov")[0] is None, f"{st} leaves no record")
        check(put("t", "PASS", [SH, "C clock"])[0] is False and led.lookup("t")[0] is None,
              "a tainted rerun deletes the old answer")

        # a record cap, and the newest first
        for i in range(K.RECORDS_PER_TEST + 3):
            p.write_text(f"v{i}")
            put("cap")
        check(len(led._load("cap")) == K.RECORDS_PER_TEST, "records per test are capped")
        p.write_text("v0")
        check(led.lookup("cap")[0] is None or K.RECORDS_PER_TEST < 9, "an old state beyond the cap is gone")
        p.write_text(f"v{K.RECORDS_PER_TEST + 2}")
        check(led.lookup("cap")[0] is not None, "the newest state answers")
        p.write_text(f"v{K.RECORDS_PER_TEST + 1}")
        check(led.lookup("cap")[0] is not None, "a revert to a kept state answers")
        p.write_text("one")

        # quarantine, memo, keys
        led.quarantine("q", "why")
        check(led.quarantined().get("q") == "why", "quarantine holds")
        led.clear_quarantine("q")
        check("q" not in led.quarantined(), "quarantine clears")
        h = K.Hasher(state)
        p.write_text("sameX")
        a = h.file(str(p))
        os.utime(p, ns=(5, 5))
        p.write_text("sameY")
        check(a != h.file(str(p)), "a same-size rewrite rehashes")
        check(h.probe(str(repo / "nope")) is None and h.probe(str(repo)).startswith("d"), "probe names type")
        check(K.Hasher.listing(str(repo / "nope")) is None, "a missing dir lists as nothing")
        led2 = K.Ledger(repo, root / "state2")
        check(led2._key(str(repo / "a.txt")) == "a.txt" and led2._abs("a.txt") == str(repo / "a.txt"),
              "repo paths are relative: two clones share an answer")
    finally:
        os.environ.clear()
        os.environ.update(env0)

    # the audit
    check(K.false_hit("PASS", "FAIL") and K.false_hit("PASS", "CRASH") and K.false_hit("PASS", "UNMEASURED"),
          "a PASS that came back as anything else is a false hit")
    check(not K.false_hit("PASS", "PASS") and not K.false_hit("FAIL", "PASS"), "agreement is not")
    n = sum(K.audit_sample(f"t{i}", "2026-11-01") for i in range(20000))
    check(0.09 * 20000 < n < 0.11 * 20000, f"the audit samples its rate ({n}/20000)")
    day1 = {i for i in range(5000) if K.audit_sample(f"t{i}", "2026-11-01")}
    day2 = {i for i in range(5000) if K.audit_sample(f"t{i}", "2026-11-02")}
    check(day1 != day2 and day1 == {i for i in range(5000) if K.audit_sample(f"t{i}", "2026-11-01")},
          "the sample is fixed per day and rotates")
    check(K.audit_sample("x", "d", 1.0) and not K.audit_sample("x", "d", 0.0), "the rate is obeyed at both ends")

    # second-reader counterexamples (each has a real end-to-end twin in `counterexamples`)
    (repo / "pkg").mkdir()
    (repo / "pkg/m.py").write_text("V = 1\n")
    pyc = f"{repo}/pkg/__pycache__/m.cpython-314.pyc"
    m = K.analyse(trace(tr, [SH, f"R {pyc}"], None, True), repo, own, later)
    check(f"{repo}/pkg/m.py" in m["files"], "a read of a .pyc is a read of its source")
    m = K.analyse(trace(tr, [SH], {"pid": 100, "modules": [f"{repo}/pkg/m.py"]}), repo, own, later)
    check(f"{repo}/pkg/m.py" in m["files"], "a loaded module's source is an input")
    (repo / "target.txt").write_text("t")
    link = str(Path(own) / "l")
    m = K.analyse(trace(tr, [SH, f"K {repo}/target.txt", f"W {link}", f"R {link}"]), repo, own, later)
    check(f"{repo}/target.txt" in m["files"], "what a link in the own TMPDIR points at is an input")
    check(has(refused([SH, f"K {repo}/sub"]), "unobserved"), "a link to a directory refuses")
    shared = root / "tmp" / "someone_elses"
    m = K.analyse(trace(tr, [SH, f"S {shared}"]), repo, own, later)
    check(str(shared) in m["probes"] and not m["refused"], "a probe of an absent shared temp file is an input")
    shared.write_text("x")
    check(has(refused([SH, f"S {shared}"]), "shared temp"), "a probe of a present shared temp file refuses")
    shared.unlink()
    check(not K.analyse(trace(tr, [SH, f"S {root / 'tmp'}", "S /tmp"]), repo, own, later)["refused"], "the temp root itself is no input")
    x = repo / "mode.txt"
    x.write_text("m")
    x.chmod(0o755)
    h = K.Hasher(root)
    before, fbefore = h.probe(str(x)), h.file(str(x))
    x.chmod(0o644)
    check(h.probe(str(x)) != before, "a probe sees permissions")
    check(h.file(str(x)) != fbefore, "a file hash sees permissions: running a tool depends on them too")
    (repo / "same_a").write_text("s")
    (repo / "same_b").write_text("s")
    os.symlink("same_a", repo / "ln")
    one, sees = h.file(str(repo / "ln")), h.probe(str(repo / "ln"))
    os.unlink(repo / "ln")
    os.symlink("same_b", repo / "ln")
    check(h.file(str(repo / "ln")) != one, "a file hash sees the link's own text")
    check(h.probe(str(repo / "ln")) != sees, "a probe sees the link's own text")
    os.unlink(repo / "ln")

    gone = f"{repo}/made.tmp"
    check(not K.analyse(trace(tr, [SH, f"W {gone}", f"K {gone}"]), repo, own, later)["refused"], "a temp name renamed into place is no input")
    check(K.Ledger.__dict__["_key"](types.SimpleNamespace(repo=str(repo)), str(repo)) == ".", "the repo root is relative too")

    m = K.analyse(trace(tr, [SH, "X /x/bin1/tool", "F /x/bin1/tool", "X /usr/bin/true", "@ /usr/bin/true"]), repo, own, later)
    check("/x/bin1/tool" in m["probes"], "a failed exec candidate must stay absent")
    m = K.analyse(trace(tr, [SH, "X fix-tool", "F fix-tool"]), repo, own, later)
    check(any(p.endswith("/fix-tool") for p in m["probes"]), "a bare name walks PATH")
    walk = K._path_walk("sh")
    check(walk[-1:] and os.path.isfile(walk[-1]) and sum(os.path.isfile(p) for p in walk) == 1, "the PATH walk stops at the answer")
    old = os.environ["PATH"]
    os.environ["PATH"] = "/mnt/c/Windows:/nowhere"
    check(K._path_walk("zzz") == ["/nowhere/zzz"], "the PATH walk stays off the Windows drives")
    os.environ["PATH"] = old
    check(K.ENV_WHOLE in m["env"], "a shell makes the whole environment an input")
    check(K.ENV_WHOLE not in K.analyse(trace(tr, ["@ /usr/bin/true"]), repo, own, later)["env"], "and only a shell")
    (repo / "kind").mkdir()
    (repo / "kind/a").write_text("x")
    before = K.Hasher.listing(str(repo / "kind"))
    (repo / "kind/a").unlink()
    (repo / "kind/a").mkdir()
    check(before != K.Hasher.listing(str(repo / "kind")), "a listing knows a file from a folder")
    (repo / "kind/in").mkdir()
    (repo / "ali").symlink_to("kind/in")
    m = K.analyse(trace(tr, [SH, f"R {repo}/ali/../a.txt"]), repo, own, later)
    check(any("symlink" in w for w in m["refused"]), ".. through a symlink is refused")
    check(not K.analyse(trace(tr, [SH, f"R {repo}/sub/../a.txt"]), repo, own, later)["refused"], "plain .. is not")
    m = K.analyse(trace(tr, [SH, f"L {os.path.dirname(own)}"]), repo, own, later)
    check(any("shared temp" in w for w in m["refused"]), "a listing of the shared temp is refused")
    m = K.analyse(trace(tr, [SH, "@ /x/pycheck", "P "]), repo, own, later)
    check(any("without the tracer" in w for w in m["refused"]), "a python under another name owes a trace")

    # arming
    a = K.armed({"RM_SELFTEST_ARM": json.dumps({"trace": "/t", "preload": "/s.so", "pythonpath": "/p"}), "PYTHONPATH": "/q"})
    check(a and a["RM_SELFTEST_TRACE"] == "/t" and a["LD_PRELOAD"] == "/s.so" and a["PYTHONPATH"].split(":") == ["/p", "/q"]
          and "RM_SELFTEST_ARM" not in a, "the arm becomes the test's environment")
    check(K.armed({"X": "1"}) is None, "no arm, nothing measured")
    return wrong


# --- layer 2: mutants ---------------------------------------------------------------------------------------------------
MUTANTS = [
    ("network ignored", 'refused.append(f"network: {val}")', 'pass'),
    ("unix socket ignored", 'refused.append(f"network: unix socket {val}")', 'pass'),
    ("clock ignored", 'refused.append("clock: a python process read the wall clock")', 'pass'),
    ("date ignored", 'refused.append(f"clock: ran {os.path.basename(val)}")', 'pass'),
    ("landing count off", 'if lands < execs + 1:', 'if lands < execs:'),
    ("failed exec not subtracted", 'execs -= 1', 'execs -= 0'),
    ("python without tracer ok", 'missing = pythons - tr["starts"]', 'missing = set()'),
    ("died python ok", 'if len(tr["py"]) < len(tr["starts"]):', 'if False:'),
    ("no shim output ok", 'if not tr["native"]:', 'if False:'),
    ("broken tracer file ok", 'if tr.get("broken"):', 'if False:'),
    ("taint ignored", 'refused.append("taint: " + t)', 'pass'),
    ("exec taints refuse", 'if t not in ("os.fork", "os.forkpty", "os.exec", "os.system", "os.spawn"):', 'if True:'),
    ("machine state /proc ok", 'if not any(p.startswith(o) for o in PROC_OK):', 'if False:'),
    ("/sys ok", 'refused.append(f"machine state: {p}")\n            return False\n        if p in ("/mnt"', 'return False\n        if p in ("/mnt"'),
    ("device ok", 'if not any(p == d or p.startswith(d) for d in DEV_OK if d):', 'if False:'),
    ("external ok", 'if _under(p, EXTERNAL) and not _under(p, (repo,)):', 'if False:'),
    ("git ok", 'if "/.git/" in p + "/" and _under(p, (repo,)) and p not in wrote:', 'if False:'),
    ("read and write ok", 'if p in wrote:      #', 'if False:      #'),
    ("shared temp ok", 'if _under(p, ("/tmp", "/var/tmp", tmp_root)) and p != tmp_root:', 'if False:'),
    ("own tmp not exempt", 'mine = (own_tmp, str(trace_dir))', 'mine = (str(trace_dir),)'),
    ("mid-run change ok", 'if changed:', 'if False:'),
    ("moved: only files", 'changed = moved(files + lists + candidates, started)', 'changed = moved(files + candidates, started)'),
    ("moved: ctime and mtime lost", 'if max(st.st_mtime, st.st_ctime) >= started - TIME_SLOP_S:', 'if False:'),
    ("import listing is a full listing", 'if os.path.normpath(val) not in finder.get(pid, ()):', 'if True:'),
    ("import listing hides every lister", 'if os.path.normpath(val) not in finder.get(pid, ()):', 'if os.path.normpath(val) not in {x for v in finder.values() for x in v}:'),
    ("tool not an input", 'read |= {e for e in exes if e}', 'pass'),
    ("env always dropped", 'env = {n for n in envs | set(ENV_ALWAYS) if n not in ENV_PER_RUN}', 'env = {n for n in envs if n not in ENV_PER_RUN}'),
    ("env read dropped", 'env = {n for n in envs | set(ENV_ALWAYS) if n not in ENV_PER_RUN}', 'env = {n for n in set(ENV_ALWAYS) if n not in ENV_PER_RUN}'),
    ("per-run env kept", 'env = {n for n in envs | set(ENV_ALWAYS) if n not in ENV_PER_RUN}', 'env = envs | set(ENV_ALWAYS)'),
    ("memo ignores size+mtime", 'k = f"{p}|{st.st_size}|{st.st_mtime_ns}|{st.st_ctime_ns}"', 'k = p'),
    ("probe drops size", 'f"f{st.st_size}:{mode}"', 'f"f:{mode}"'),
    ("file ignores permissions", 'h = f"{h}:{_stat.S_IMODE(st.st_mode):o}"', 'pass'),
    ("listing ignores the filter", 'entries = [e for e in entries if e.name.split(".")[0] in keep]', 'pass'),
    ("listing is empty", 'entries = sorted(it, key=lambda e: e.name)', 'entries = []'),
    ("runner not compared", 'if rec.get("runner") != self.version:', 'if False:'),
    ("env not compared", 'if _env_value(n) != v:', 'if False:'),
    ("files not compared", 'if h.file(self._abs(k)) != v:', 'if False:'),
    ("absent not compared", 'if os.path.lexists(self._abs(k)):', 'if False:'),
    ("lists not compared", 'if h.listing(self._abs(k)) != v:', 'if False:'),
    ("import dirs not compared", 'if h.listing(self._abs(k), keep) != v:', 'if False:'),
    ("probes not compared", 'if h.probe(self._abs(k)) != v:', 'if False:'),
    ("a refusal keeps the old answer", 'if m["refused"]:\n            self.forget(rel)', 'if m["refused"]:\n            pass'),
    ("a refusal records anyway", 'if m["refused"]:', 'if False:'),
    ("no-verdict records", 'if state not in ("PASS", "FAIL"):', 'if False:'),
    ("no record cap", '([rec] + recs)[:RECORDS_PER_TEST]', '([rec] + recs)'),
    ("old records dropped", '([rec] + recs)[:RECORDS_PER_TEST]', '[rec]'),
    ("oldest answers", 'for rec in recs:\n            d = self.first_difference(rec)', 'for rec in recs[:1]:\n            d = self.first_difference(rec)'),
    ("quarantine forgets", 'q[rel] = why', 'pass'),
    ("quarantine sticks", 'if q.pop(rel, None) is not None:', 'if False:'),
    ("absolute keys", 'return p[len(self.repo) + 1:] if p.startswith(self.repo + "/") else p', 'return p'),
    ("false hit only on FAIL", 'return stored_state == "PASS" and state != "PASS"', 'return stored_state == "PASS" and state == "FAIL"'),
    ("false hit on a red", 'return stored_state == "PASS" and state != "PASS"', 'return state != stored_state'),
    ("sample ignores the day", 'f"{rel}|{day}"', 'f"{rel}"'),
    ("sample ignores the rate", '< rate * 2 ** 32', '< 0.1 * 2 ** 32'),
    ("pyc source lost", 'read.add(_source_of(os.path.normpath(val)))', 'read.add(os.path.normpath(val))'),
    ("loaded source lost", 'm.endswith((".so", ".pyd", ".py"))', 'm.endswith((".so", ".pyd"))'),
    ("link target lost", 'linked.add(os.path.normpath(val))', 'pass'),
    ("link to a dir passes", 'if keep(p) and os.path.isdir(p):', 'if False:'),
    ("shared probe dropped", 'probes.append(p)', 'probes.append(p) if not _under(p, ("/tmp", "/var/tmp", tmp_root)) else None'),
    ("shared probe present passes", 'if os.path.lexists(p):\n                refused.append(f"shared temp: {p}")', 'if False:\n                pass'),
    ("temp root is an input", 'if p in ("/tmp", "/var/tmp") or _under(tmp_root, (p,)):', 'if False:'),
    ("probe ignores permissions", 'mode = oct(_stat.S_IMODE(st.st_mode))', 'mode = ""'),
    ("file ignores link text", 'return link + h if link and h else h', 'return h'),
    ("probe ignores link text", 'return link + (f"d{mode}"', 'return (f"d{mode}"'),
    ("shared listing allowed", 'refused.append(f"shares: listed shared temp {p}")', 'pass'),
    ("exec names unprobed", 'if not _under(os.path.normpath(val), EXTERNAL):\n                        probed.add(os.path.normpath(val))', 'pass'),
    ("no bare PATH walk", 'probed.update(_path_walk(val))', 'pass'),
    ("PATH walk runs on", 'if os.path.isfile(p) and os.access(p, os.X_OK):\n                break', 'pass'),
    ("PATH walk reaches windows", 'if not _under(p, EXTERNAL):\n            out.append(p)', 'if True:\n            out.append(p)'),
    ("listing without kinds", 'e.name + ("@" if e.is_symlink() else "/" if e.is_dir() else "")', 'e.name'),
    ("shell env not whole", '& ENV_IMPORTERS:', '& set():'),
    ("dotdot allowed", '"/../" in val and os.path', 'False and os.path'),
    ("copied python ok", 'if op == "P":\n                pythons.add(pid)', 'if op == "P":\n                pass'),
    ("rename temp refuses", 'if p in wrote and not os.path.lexists(p):\n            continue', 'if False:\n            continue'),
    ("repo root key absolute", 'if p == self.repo:\n            return "."', 'if False:\n            return "."'),
    ("arm leaves the arm", 'if k != ARM_ENV}', 'if k}'),
    ("arm drops the tracer path", 'os.pathsep.join([arm["pythonpath"]] + [', 'os.pathsep.join(['),
]


def mutants(root: Path):
    src = SOURCE.read_text()
    lived = []
    for name, old, new in MUTANTS:
        if old not in src:
            lived.append(f"{name}: text not in the source (stale mutant)")
            continue
        try:
            wrong = decide(load(src.replace(old, new, 1)), root / "m")
        except Exception as exc:  # noqa: BLE001 - a mutant that crashes the checks was caught by them
            wrong = [f"raised {type(exc).__name__}"]
        if not wrong:
            lived.append(name)
    eq(lived, [], f"{len(MUTANTS)} mutants of known_results.py are all caught")


# --- layer 3: the real runner, shim and tracer ---------------------------------------------------------------------------
FIXTURES = {
    # measured dependencies: each must be found, not declared
    "src/selftest_import.py": "import helper_a\nassert helper_a.value() == 1\n",
    "src/helper_a.py": "import helper_b\ndef value():\n    return helper_b.VALUE\n",
    "src/helper_b.py": "VALUE = 1  # v1\n",
    "src/selftest_data.py": "assert open('src/data.txt').read().startswith('v')\n",
    "src/selftest_listing.py": "import os\nassert 'a' in os.listdir('src/listed')\n",
    "src/selftest_env.py": "import os\nassert os.environ.get('FIX_KNOB', 'x') != 'bad'\n",
    "src/selftest_tool.py": "import subprocess\nsubprocess.run(['src/bin/mytool', '-c', 'exit 0'], check=True)\n",
    "src/selftest_absent.py": "import os\nassert not os.path.exists('src/maybe.txt') or True\n",
    "src/selftest_shadow.py": "import colorsys\nassert colorsys.rgb_to_hsv\n",
    "src/selftest_threads.py": ("import threading\nnames = [f'src/t{i}.txt' for i in range(16)]\n"
                                "ts = [threading.Thread(target=lambda n=n: open(n).read()) for n in names]\n"
                                "[t.start() for t in ts]\n[t.join() for t in ts]\n"),
    "src/selftest_unrelated.py": "print('nothing changes me')\n",
    # a real red
    "src/selftest_red.py": "import sys\nprint(open('src/red.txt').read())\nsys.exit(1)\n",
    # the planted hidden dependency: a verdict hanging on an mtime, which the probe keeps out of the record on purpose
    "src/selftest_hidden.py": "import os, sys\nsys.exit(0 if os.stat('src/hidden.txt').st_mtime == 1000000000 else 1)\n",
    # never cached
    "src/selftest_clock.py": "import time\nprint(time.time())\n",
    "src/selftest_network.py": ("import socket\ntry:\n    socket.create_connection(('127.0.0.1', 9), 1)\n"
                                "except OSError:\n    pass\n"),
    "src/selftest_game.py": "import os\nprint(os.path.exists('/mnt/c/Program Files (x86)/Steam'))\n",
    "src/selftest_git.py": "import subprocess\nsubprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True)\n",
    "src/selftest_machine.py": "print(len(open('/proc/meminfo').read()))\n",
    "src/selftest_python_i.py": "import subprocess, sys\nsubprocess.run([sys.executable, '-I', '-c', 'print(1)'], check=True)\n",
    "src/selftest_env_cleared.py": "import subprocess\nsubprocess.run(['/bin/sh', '-c', 'exit 0'], env={}, check=True)\n",
    "src/selftest_rewrites.py": "p = 'src/rw.txt'\nt = open(p).read()\nopen(p, 'w').write(t)\n",
    "src/selftest_touches.py": "import os\nopen('src/touched.txt').read()\nos.utime('src/touched.txt')\n",
}
CACHEABLE = ["import", "data", "listing", "env", "tool", "absent", "shadow", "threads", "unrelated", "hidden"]
NEVER = {"clock": "clock", "network": "network", "game": "external", "git": "git state", "machine": "machine state",
         "python_i": "unobserved", "env_cleared": "unobserved", "rewrites": "reads and writes", "touches": "changed during"}


def build(root: Path):
    shutil.rmtree(root, ignore_errors=True)
    for rel, body in FIXTURES.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    (root / "src/data.txt").write_text("v1\n")
    (root / "src/red.txt").write_text("red\n")
    (root / "src/hidden.txt").write_text("h\n")
    os.utime(root / "src/hidden.txt", (1000000000, 1000000000))
    (root / "src/rw.txt").write_text("rw\n")
    (root / "src/touched.txt").write_text("t\n")
    (root / "src/listed").mkdir()
    (root / "src/listed/a").write_text("a")
    (root / "src/bin").mkdir()
    shutil.copy2("/bin/sh", root / "src/bin/mytool")
    for i in range(16):
        (root / f"src/t{i}.txt").write_text(str(i))
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=x", "-c", "user.email=x@example.invalid", "commit", "-q",
                    "--allow-empty", "-m", "x"], check=True)


def settle():
    """A file touched within TIME_SLOP_S of a run's start refuses as changed-during-the-run; that is the instrument
    working, so a fixture edit waits it out."""
    time.sleep(2.2)


def run(root: Path, *args, extra=None, state=None, timeout=240):
    env = {k: v for k, v in os.environ.items() if not k.startswith("RM_SELFTEST_")
           and k not in ("PYTHONPATH", "LD_PRELOAD", "PYTHONHASHSEED") and not k.startswith("FIX_")}
    env.update(RM_SELFTEST_REPO_ROOT=str(root), RM_SELFTEST_STATE_DIR=str(state or root.parent / f"{root.name}.state"),
               RM_SELFTEST_LOCK=str(root.parent / f"{root.name}.lock"), RM_SELFTEST_NO_HARNESS="1",
               RM_SELFTEST_KNOWN_RESULTS="1", RM_SELFTEST_CACHE_STORE=str(root.parent / f"{root.name}.cache"),
               SELFTEST_TIMINGS_FILE=str(root.parent / f"{root.name}.timings.json"))
    env.update(extra or {})
    p = subprocess.run([sys.executable, str(RUNNER), *args], cwd=root, env=env, capture_output=True, text=True,
                       timeout=timeout)
    states = {}
    for ln in p.stdout.splitlines():
        parts = ln.split()
        if len(parts) < 3:
            continue
        if parts[0] == "KNOWN" and parts[1] in ("PASS", "RED"):
            states.setdefault(parts[2].rstrip(":"), "KNOWN " + parts[1])
        elif parts[0] in ("PASS", "FAIL", "UNMEASURED", "CRASH"):
            path = next((x for x in parts[1:] if x.startswith("src/")), None)
            have = states.get(path)
            if path and have == "KNOWN RED":
                states[path] = "KNOWN RED then " + parts[0]
            elif path and have is None:     # the table at the end repeats a stored PASS as PASS: the first line decides
                states[path] = parts[0]
    return p, states


def st(states, name):
    return states.get(f"src/selftest_{name}.py")


def fixture(root: Path):
    build(root)
    state = root.parent / f"{root.name}.state"
    settle()
    p, s = run(root)
    eq(p.returncode, 1, "run 1: the one real red reddens the run")
    for n in CACHEABLE + list(NEVER):
        eq(st(s, n), "PASS", f"run 1: {n} ran and passed under tracing")
    eq(st(s, "red"), "FAIL", "run 1: the red is red")
    recs = {r.name: json.loads(r.read_text()) for r in (state / "known_results/records").iterdir()}

    def rec(name):
        return recs.get(f"src__selftest_{name}.py.json", [{}])[0]

    eq("src/helper_b.py" in rec("import").get("files", {}), True, "measured: the transitive import is an input")
    eq("src/data.txt" in rec("data").get("files", {}), True, "measured: the data file is an input")
    eq("src/listed" in rec("listing").get("lists", {}), True, "measured: the listing is an input")
    eq("FIX_KNOB" in rec("env").get("env", {}), True, "measured: the env name is an input")
    eq("src/bin/mytool" in rec("tool").get("files", {}), True, "measured: the tool binary is an input")
    eq("src/maybe.txt" in rec("absent").get("probes", {}) or "src/maybe.txt" in rec("absent").get("absent", []), True,
       "measured: a file that is not there is an input")
    eq(sorted(k for k in rec("threads").get("files", {}) if "/t" in k and k.endswith(".txt")),
       sorted(f"src/t{i}.txt" for i in range(16)), "measured: sixteen threads, sixteen reads, none dropped by the tracer")
    eq(any(k.startswith("/usr/lib/python") or k.startswith("/usr/bin/python") for k in rec("data").get("files", {})), True,
       "measured: the interpreter and its stdlib are inputs")
    for n, word in NEVER.items():
        eq(f"src__selftest_{n}.py.json" in recs, False, f"never cached: {n}")
    refusals = [json.loads(ln) for ln in (state / "known_results/refusals.jsonl").read_text().splitlines()]
    for n, word in NEVER.items():
        why = " ".join(w for r in refusals if r["test"] == f"src/selftest_{n}.py" for w in r["why"])
        eq(word in why, True, f"refused for the right reason: {n} ({word})")

    t0 = time.time()
    p, s = run(root)
    for n in CACHEABLE:
        eq(st(s, n), "KNOWN PASS", f"run 2: {n} answered, not run")
    for n in NEVER:
        eq(st(s, n), "PASS", f"run 2: {n} runs again")
    eq(st(s, "red"), "KNOWN RED then FAIL", "run 2: the red is named and run again, never returned")
    eq(f"{len(CACHEABLE)}/{len(CACHEABLE) + len(NEVER) + 1} answered" in p.stdout, True, "run 2: the hit share is reported")
    eq("selftests.cache_hit_share" in p.stdout, True, "run 2: under the name TE2 reads")
    print(f"     run 2 took {time.time() - t0:.1f}s")

    # one change each, all at once, and one that must NOT invalidate anything
    (root / "src/helper_b.py").write_text("VALUE = 1  # v2\n")
    (root / "src/data.txt").write_text("v2\n")
    (root / "src/listed/b").write_text("b")
    (root / "src/maybe.txt").write_text("now it is")
    (root / "src/colorsys.py").write_text("from math import pi\nrgb_to_hsv = pi\n")
    with open(root / "src/bin/mytool", "ab") as f:
        f.write(b"\0")
    (root / "src/an_unrelated_new_file.txt").write_text("x")
    settle()
    p, s = run(root, extra={"FIX_KNOB": "good"})
    for n, what in [("import", "a transitive dependency"), ("data", "a data file"), ("listing", "a listing"),
                    ("env", "an env value"), ("tool", "a tool binary"), ("absent", "a file appearing"),
                    ("shadow", "a module shadowing an import")]:
        eq(st(s, n), "PASS", f"run 3: {what} changed, so the test really ran")
    eq(st(s, "unrelated"), "KNOWN PASS", "run 3: an unrelated new file invalidates nothing")
    eq(st(s, "threads"), "KNOWN PASS", "run 3: nor another test's inputs")

    # the revert answers from the older record
    (root / "src/data.txt").write_text("v1\n")
    settle()
    p, s = run(root, extra={"FIX_KNOB": "good"})
    eq(st(s, "data"), "KNOWN PASS", "run 4: a revert to a known state answers")

    # a forced rerun must say why
    p, s = run(root, "--no-cache", extra={"FIX_KNOB": "good"})
    eq((p.returncode, "REFUSED" in p.stdout), (2, True), "--no-cache without --because is refused")
    p, s = run(root, "--full", extra={"FIX_KNOB": "good"})
    eq(p.returncode, 2, "--full without --because is refused")
    p, s = run(root, "--no-cache", "--because", "selftest of the reason", extra={"FIX_KNOB": "good"})
    eq(st(s, "unrelated"), "PASS", "--no-cache --because really runs")
    forced = (state / "known_results/forced.jsonl").read_text()
    eq("selftest of the reason" in forced, True, "the reason is on file")

    # the planted hidden dependency: same bytes, same size, another mtime; the key cannot see it
    os.utime(root / "src/hidden.txt", (2000000000, 2000000000))
    settle()
    p, s = run(root, extra={"FIX_KNOB": "good"})
    eq(st(s, "hidden"), "KNOWN PASS", "planted: the key cannot see it (this is the false hit the audit exists for)")
    p, s = run(root, "--nightly", extra={"FIX_KNOB": "good", "RM_SELFTEST_AUDIT_RATE": "0"})
    eq(st(s, "hidden"), "KNOWN PASS", "planted: outside the sample, still unseen")
    p, s = run(root, "--nightly", extra={"FIX_KNOB": "good", "RM_SELFTEST_AUDIT_RATE": "1"})
    eq(st(s, "hidden"), "FAIL", "planted: the audit ran it for real")
    eq("!!! FALSE HIT src/selftest_hidden.py" in p.stdout, True, "planted: the alarm names it")
    eq(p.returncode, 1, "planted: the run is red")
    eq((state / "known_results/records/src__selftest_hidden.py.json").exists(), False, "planted: the record is deleted")
    q = json.loads((state / "known_results/quarantine.json").read_text())
    eq("src/selftest_hidden.py" in q, True, "planted: the test is quarantined")
    runs = [json.loads(x) for x in (state / "known_results/runs.jsonl").read_text().splitlines()]
    eq(runs[-1]["false_hits"], ["src/selftest_hidden.py"], "planted: the run log carries it")

    # quarantine: it passes, records nothing, and only a stated rerun lets it back
    os.utime(root / "src/hidden.txt", (1000000000, 1000000000))
    settle()
    p, s = run(root, extra={"FIX_KNOB": "good"})
    eq(st(s, "hidden"), "PASS", "quarantined: it runs, nothing is answered for it")
    eq("QUARANTINED src/selftest_hidden.py" in p.stdout, True, "quarantined: and it says so")
    p, s = run(root, "--no-cache", "--because", "hidden mtime restored", extra={"FIX_KNOB": "good"})
    eq("src/selftest_hidden.py" in json.loads((state / "known_results/quarantine.json").read_text()), False,
       "a passing --because run clears the quarantine")

    # a nightly that agrees is silent
    p, s = run(root, "--nightly", extra={"FIX_KNOB": "good", "RM_SELFTEST_AUDIT_RATE": "1"})
    eq("FALSE HIT" in p.stdout, False, "an audit that agrees raises nothing")

    # no shim, no ledger: no compiler and no built .so, and everything still runs
    bare = root.parent / f"{root.name}.bare"
    p, s = run(root, extra={"PATH": "/nonexistent", "FIX_KNOB": "good"}, state=bare)
    eq(st(s, "unrelated"), "PASS", "no shim: the test runs")
    eq("KNOWN PASS" in p.stdout or (bare / "known_results/records").exists() and any((bare / "known_results/records").iterdir()),
       False, "no shim: nothing is recorded or answered")

    # the ledger can be switched off, and is off on a fixture that does not ask
    p, s = run(root, extra={"RM_SELFTEST_KNOWN_RESULTS": "0", "FIX_KNOB": "good"})
    eq(st(s, "unrelated"), "PASS", "RM_SELFTEST_KNOWN_RESULTS=0 runs everything")


SECOND_READER = {
    # a .pyc stays valid until the source's stat changes, so the record must carry the source, not the .pyc
    "src/selftest_pyc.py": "import cached_dep\nassert cached_dep.VALUE == 1\n",
    "src/cached_dep.py": "VALUE = 1\n",
    "src/selftest_envcopy.py": "import os\nassert os.environ.copy().get('FIX_GATE', 'ok') == 'ok'\n",
    "src/selftest_envwalk.py": "import os\nassert dict(os.environ.copy())['FIX_WALK'] == 'a'\n",
    "src/selftest_handoff.py": "import os, subprocess\nsubprocess.run(['/bin/true'], env=os.environ.copy(), check=True)\n",
    "src/selftest_mode.py": "import os\nassert os.access('src/tool.sh', os.X_OK)\n",
    "src/selftest_switch.py": "import os\nassert not os.path.exists(%(switch)r)\n",
    "src/selftest_ownlink.py": "import os, tempfile\nd = tempfile.mkdtemp()\nos.symlink(os.path.abspath('src/linked.txt'), d + '/l')\n"
                               "assert open(d + '/l').read() == 'ok'\n",
    "src/selftest_readlink.py": "import os\nassert os.readlink('src/ln') == 'same_a'\n",
    "src/selftest_findspec.py": "import importlib.util, sys\nsys.path.insert(0, 'src/plugins')\n"
                                "assert importlib.util.find_spec('ledger_optional_x') is None\n",
    "src/plugins/keep.txt": "x",
    "src/selftest_forkenv.py": "import os\npid = os.fork()\nif pid == 0:\n    os._exit(0 if os.environ.get('FIX_FORK', 'good') == 'good' else 1)\n"
                               "assert os.waitpid(pid, 0)[1] == 0\n",
    "src/selftest_renamed.py": "import os, tempfile\nd = tempfile.mkdtemp()\nos.rename('src/fixture.txt', d + '/f')\n"
                               "try:\n    good = open(d + '/f').read() == 'good'\nfinally:\n    os.rename(d + '/f', 'src/fixture.txt')\nassert good\n",
    "src/selftest_environb.py": "import os\nassert os.environb.get(b'FIX_BYTES', b'good') == b'good'\n",
    "src/selftest_system.py": "import os\nassert os.system('exec /usr/bin/env -i /usr/bin/python3 -S src/check.py') == 0\n",
    "src/check.py": "assert open('src/linked.txt').read() == 'ok'\n",
    "src/selftest_pathshadow.py": "import os, subprocess\np = os.path.abspath('src/bin1') + ':' + os.path.abspath('src/bin2')\n"
                                  "assert subprocess.run(['fix-tool'], env={**os.environ, 'PATH': p}).returncode == 0\n",
    "src/bin1/keep": "x",
    "src/bin2/fix-tool": "#!/bin/sh\nexit 0\n",
    "src/selftest_scantype.py": "import os\nassert [e.name for e in os.scandir('src/tree') if e.is_file()] == ['a']\n",
    "src/tree/a": "x",
    "src/selftest_shellenv.py": "import subprocess\nassert subprocess.run(['/bin/sh', '-c', 'test \"${FIX_SHELL:-ok}\" = ok']).returncode == 0\n",
    "src/selftest_dotdot.py": "assert open('src/alias/../flag').read() == 'ok'\n",
    "src/flag": "ok",
    "src/sub/flag": "ok",
    "src/sub/inner/keep": "x",
    "src/selftest_pycopy.py": "import os, shutil, subprocess, sys, tempfile\nd = tempfile.mkdtemp()\n"
                              "c = shutil.copy2(os.path.realpath(sys.executable), d + '/pycheck')\n"
                              "subprocess.run([c, '-I', '-c', 'import os; assert os.environ.get(\"FIX_COPY\", \"ok\") == \"ok\"'], check=True)\n",
    "src/selftest_tmpglob.py": "import glob, os, tempfile\nassert not glob.glob(os.path.dirname(tempfile.gettempdir()) + '/rm_known_glob_*.lock')\n",
    "src/selftest_retarget.py": "import subprocess\nassert subprocess.run(['src/tool-link']).returncode == 0\n",
    "src/tool-good": "#!/bin/sh\nexit 0\n",
    "src/tool-bad": "#!/bin/sh\nexit 1\n",
    "src/selftest_pushd.py": "import os\ntry:\n    os.chdir('src/empty-dir')\nexcept OSError:\n    assert False\n",
    "src/selftest_closerange.py": "import os, subprocess\nb = subprocess.check_output(['/bin/cat', 'src/linked.txt'], env={},\n"
                                  "    preexec_fn=lambda: os.closerange(3, 1 << 20))\nassert b == b'ok'\n",
}


def counterexamples(root: Path):
    """The second reader's stale PASSes, end to end: same bytes on the surface, a different answer underneath."""
    shutil.rmtree(root, ignore_errors=True)
    switch = f"/tmp/rm_known_results_switch_{os.getpid()}"
    for rel, body in SECOND_READER.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(body.replace("%(switch)r", repr(switch)))
    src = root / "src"
    (src / "tool.sh").write_text("#!/bin/sh\n")
    (src / "tool.sh").chmod(0o755)
    (src / "linked.txt").write_text("ok")
    (src / "empty-dir").mkdir()
    for n in ("tool-good", "tool-bad"):
        (src / n).chmod(0o755)
    (src / "tool-link").symlink_to("tool-good")
    (src / "bin2/fix-tool").chmod(0o755)
    (src / "alias").symlink_to("sub/inner")
    (src / "fixture.txt").write_text("good")
    (src / "same_a").write_text("same")
    (src / "same_b").write_text("same")
    os.symlink("same_a", src / "ln")
    subprocess.run([sys.executable, "-m", "compileall", "-q", str(src / "cached_dep.py")], check=True)
    state = root.parent / f"{root.name}.state"
    settle()
    try:
        run(root, extra={"FIX_HANDED": "x", "FIX_WALK": "a"})
        p, s = run(root, extra={"FIX_HANDED": "x", "FIX_WALK": "a"})
        stale = ["pyc", "envcopy", "envwalk", "mode", "switch", "ownlink", "readlink", "findspec", "forkenv", "environb", "pathshadow", "scantype", "shellenv", "retarget", "pushd"]
        for n in stale + ["handoff"]:
            eq(st(s, n), "KNOWN PASS", f"second reader: {n} is cacheable before the change")
        rec = json.loads((state / "known_results/records/src__selftest_handoff.py.json").read_text())[0]
        eq("FIX_HANDED" in rec["env"], False, "handing a copy of the environment to a child reads none of it")
        eq(st(s, "closerange"), "PASS", "second reader: a child that closed the shim's fd is run every time")
        why = " ".join(w for r in map(json.loads, (state / "known_results/refusals.jsonl").read_text().splitlines())
                       if r["test"] == "src/selftest_closerange.py" for w in r["why"])
        eq("unobserved" in why, True, "and refused as unobserved")
        for n, word in (("renamed", "reads and writes"), ("system", "unobserved"), ("dotdot", "symlink"), ("tmpglob", "shared temp"), ("pycopy", "without the tracer")):
            why = " ".join(w for r in map(json.loads, (state / "known_results/refusals.jsonl").read_text().splitlines())
                           if r["test"] == f"src/selftest_{n}.py" for w in r["why"])
            eq(st(s, n), "PASS", f"second reader: {n} is run every time")
            eq(word in why, True, f"second reader: {n} refused as {word}")
        (src / "cached_dep.py").write_text("VALUE = 2\n")
        (src / "plugins/ledger_optional_x.py").write_text("x = 1\n")
        (src / "tool-link").unlink()
        (src / "tool-link").symlink_to("tool-bad")
        (src / "empty-dir").rmdir()
        (src / "bin1/fix-tool").write_text("#!/bin/sh\nexit 1\n")
        (src / "bin1/fix-tool").chmod(0o755)
        (src / "tree/a").unlink()
        (src / "tree/a").mkdir()
        (src / "tool.sh").chmod(0o644)
        Path(switch).write_text("x")
        (src / "linked.txt").write_text("no")
        os.unlink(src / "ln")
        os.symlink("same_b", src / "ln")
        settle()
        p, s = run(root, extra={"FIX_HANDED": "x", "FIX_GATE": "bad", "FIX_WALK": "b", "FIX_FORK": "bad", "FIX_BYTES": "bad", "FIX_SHELL": "bad"})
        for n in stale:
            eq(st(s, n), "FAIL", f"second reader: {n} really ran and went red (no stale PASS)")
    finally:
        Path(switch).unlink(missing_ok=True)


def main():
    K = load()
    work = SCRATCH / f"known_results_fixture_{os.getpid()}"
    work.mkdir(parents=True, exist_ok=True)
    try:
        wrong = decide(K, work / "unit")
        eq(wrong, [], "every ledger decision on hand-built traces and real files")
        mutants(work)
        fixture(work / "repo")
        counterexamples(work / "second")
        sys.path.insert(0, str(HERE.parent / "rimflow"))
        import incident as IN
        eq(IN.route_of(IN.load_table(), "selftest_false_hit").get("reader") is not None, True, "a false hit reaches a reader")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(f"{'FAIL' if FAILS else 'ok'}: selftest_known_results - {len(FAILS)} failed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
