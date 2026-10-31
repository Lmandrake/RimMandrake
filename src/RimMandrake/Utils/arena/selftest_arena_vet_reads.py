"""Selftest for arena_vet_reads.py (ARENA_TREE_FIX_OMITS_CHECK_READ_PATHS) and the vet/judge/census wiring around it.

    python3 src/RimMandrake/Utils/arena/selftest_arena_vet_reads.py

A fixture repo whose hidden check reads a file and scans a directory OUTSIDE the judge's tree (TREE_PATHS + area): the
plain judge tree fails it at base AND fix (the instrument control), the traced vet makes it pass at the fix and fail
at base, and records the read set the judge then materialises. Runs the real sandbox (bwrap), no game, no bridge.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_tasks as A  # noqa: E402
import arena_judge as J  # noqa: E402
import arena_vet_reads as VR  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def git(repo, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="Fixture", GIT_AUTHOR_EMAIL="f@x", GIT_COMMITTER_NAME="Fixture",
               GIT_COMMITTER_EMAIL="f@x")
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env, timeout=60)
    assert r.returncode == 0, (args, r.stderr)
    return r.stdout.strip()


def commit(repo, files, msg):
    for rel, body in files.items():
        p = Path(repo) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    git(repo, "add", "-A", ".")          # fixture repo only, in a temp dir
    git(repo, "commit", "-q", "-m", msg)
    return git(repo, "rev-parse", "HEAD")


LIB = "src/RimMandrake/Utils/vr_lib.py"
CHECK = "src/RimMandrake/Utils/selftest_vr_lib.py"
TABLE = "src/Other/data/table.txt"
SCAN = "src/Other/scan"
# reads TABLE through os.path.join pieces (no literal a static scan could find), then probes and lists SCAN; it dies
# at the first missing read, so the trace discovers the two reads in successive rounds
BODY = '''import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import vr_lib
want = int(open(os.path.join(REPO, "src", "Other", "data", "table.txt")).read().split("=")[1])
scan = os.path.join(REPO, "src", "Other", "scan")
if not os.path.isdir(scan):
    print("SKIP scan: no tool sources")
    sys.exit(1)
names = sorted(os.listdir(scan))
assert names == ["a.txt", "b.txt"], names
assert vr_lib.f() == want, (vr_lib.f(), want)
print("PASS")
'''
PASSING = 'import sys\nsys.path.insert(0, __import__("os").path.dirname(__file__))\nimport vr_lib\nassert vr_lib.f() == 2\n'
# a VCS dir no read can supply (was .git: since ARENA_VET_FIX_ENV_CULLED_CLASSES a check naming git gets a synthetic
# repo tree from the judge, so .git is no longer an unsuppliable path)
NEEDS_VCS = 'import os\nassert os.path.isdir(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".hg"))\n'


def t_units(tmp):
    check(VR.judge_tree_paths(None, J.TREE_PATHS) == tuple(J.TREE_PATHS), "judge_tree_paths: no hidden -> tree paths")
    got = VR.judge_tree_paths({"reads": [TABLE, J.TREE_PATHS[0]]}, J.TREE_PATHS)
    check(got == tuple(J.TREE_PATHS) + (TABLE,), "judge_tree_paths: reads appended once (%s)" % (got,))
    for bad in (["../x"], ["/abs"], ["a/.git/x"], ["a//b"], ["./a"], [""], ["-x"], "src/x", [3]):
        try:
            VR.judge_tree_paths({"reads": bad}, J.TREE_PATHS)
            check(False, "judge_tree_paths refuses %r" % (bad,))
        except ValueError:
            check(True, "judge_tree_paths refuses %r" % (bad,))
    tree = tmp / "unit_tree"
    (tree / "src/Here").mkdir(parents=True)
    (tree / "src/Here/x.txt").write_text("x")
    files = {"src/Here/x.txt", "src/Far/y.txt", "src/Wide/" + "f.txt"}
    dirs = {"src": 3, "src/Here": 1, "src/Far": 1, "src/Wide": VR.READ_DIR_CAP + 1}
    add, wide = VR.new_reads({"src/Here/x.txt", "src/Far/y.txt", "src/Far", "src/Wide", "src/Gone.txt", "..", ""},
                             tree, files, dirs, set())
    check(add == {"src/Far/y.txt", "src/Far"} and wide == {"src/Wide"},
          "new_reads: absent-but-committed file and dir added, present/uncommitted ignored, wide dir refused "
          "(%s, %s)" % (sorted(add), sorted(wide)))
    # ARENA_VET_READS_REFUSE_FIX_CHANGED_PATHS: a read the fix changed outside the area is refused, a dir holding one too
    files2 = files | {"infra/items/X.md", "src/Here/y.txt"}
    dirs2 = dict(dirs, **{"infra": 1, "infra/items": 1})
    ref: set = set()
    add, _ = VR.new_reads({"infra/items/X.md", "src/Far/y.txt"}, tree, files2, dirs2, set(),
                          {"infra/items/X.md", "src/Here/y.txt"}, ["src/Here/*"], ref)
    check(add == {"src/Far/y.txt"} and ref == {"infra/items/X.md"},
          "new_reads: a fix-changed path outside the area is refused, an unchanged one added (%s, %s)"
          % (sorted(add), sorted(ref)))
    ref = set()
    add, _ = VR.new_reads({"infra"}, tree, files2, dirs2, set(), {"infra/items/X.md"}, [], ref)
    check(not add and ref == {"infra"}, "new_reads: a dir read holding a fix-changed path is refused (%s)" % ref)
    check(not VR.fix_changed("src/Here", {"src/Here/y.txt"}, ["src/Here/*"]) and
          VR.fix_changed("src/Here", {"src/Here/y.txt"}, []),
          "fix_changed: a change inside the area is the arm's to make, so it does not refuse")
    # ARENA_TRACE_HARDEN_LOG_SHAPE_KILLS_VET: a log of the wrong shape is no reads, never an exception
    for raw in ("null", "[1]", '[["open", ["x"]]]', '{"a": 1}', "[[\"open\"]]", "not json", "", '[["open", "a"], 3]'):
        check(VR.parse_log(raw) == set(), "parse_log: malformed log %r -> no reads" % raw)
    check(VR.parse_log('[["open", "a/b"], ["list", "c"]]') == {"a/b", "c"},
          "parse_log: a well-formed log -> its paths (positive control)")
    for bad in (["x"], "x", 3):
        try:
            VR.judge_tree_paths(bad, J.TREE_PATHS)
            check(False, "judge_tree_paths refuses a non-dict hidden %r" % (bad,))
        except ValueError:
            check(True, "judge_tree_paths refuses a non-dict hidden %r (ValueError, not AttributeError)" % (bad,))


def t_fixture(tmp):
    repo = tmp / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    base = commit(repo, {LIB: "def f():\n    return 1\n", TABLE: "want=2\n", SCAN + "/a.txt": "a",
                         SCAN + "/b.txt": "b", "src/Other/unrelated.txt": "u"}, "base")
    fix = commit(repo, {LIB: "def f():\n    return 2\n", CHECK: BODY}, "fix")
    area = A.area_for([LIB, CHECK])
    checks = [{"kind": "fix_test", "path": CHECK, "body": BODY}]

    # instrument control: the plain judge tree (no reads) fails the check at BOTH sides, as the vet used to see it
    plain = {}
    for side, sha in (("fix", fix), ("base", base)):
        d = tmp / ("plain_" + side)
        tree = J.materialise(repo, sha, area, d / "tree")
        plain[side] = J.run_hidden(checks, tree, d)[0]["result"]
        shutil.rmtree(d, ignore_errors=True)
    check(plain == {"fix": "fail", "base": "fail"}, "control: without the reads the check is fail/fail (%s)" % plain)

    tr = VR.trace_reads(repo, fix, area, checks, tmp / "trace", 30)
    check(tr["reads"] == [TABLE, SCAN] and tr["converged"] and tr["rounds"] == 3 and not tr["too_wide"],
          "trace: the file read and the scanned dir are found in successive rounds, then it converges (%s)" % tr)
    check("src/Other/unrelated.txt" not in tr["reads"], "trace: an unread sibling is not pulled in")

    job = {"task": "RP_VR", "base": base, "fix": fix, "area": area,
           "checks": [{"path": CHECK, "body": BODY, "key": "vr-1"}]}
    rec = A._vet_task(job, repo, tmp / "vt", 30)[0]
    check(rec["fix_result"] == "pass" and rec["base_result"] == "fail" and A.vet_verdict(rec) == (True, "discriminating"),
          "vet: with the traced reads the check passes at the fix and fails at base (%s/%s)"
          % (rec["fix_result"], rec["base_result"]))
    check(rec["reads"] == [TABLE, SCAN] and rec["reads_trace"]["converged"],
          "vet record carries the read set the judge must materialise (%s)" % rec.get("reads"))

    jp = {"task": "RP_VR_PASS", "base": base, "fix": fix, "area": area,
          "checks": [{"path": CHECK.replace("vr_lib", "vr_ok"), "body": PASSING, "key": "vr-2"}]}
    rp = A._vet_task(jp, repo, tmp / "vt2", 30)[0]
    check(rp["fix_result"] == "pass" and rp["reads"] == [] and "reads_trace" not in rp,
          "vet: a check passing at the fix is not traced and carries no reads (%s)" % rp.get("reads"))
    jg = {"task": "RP_VR_GIT", "base": base, "fix": fix, "area": area,
          "checks": [{"path": CHECK.replace("vr_lib", "vr_vcs"), "body": NEEDS_VCS, "key": "vr-3"}]}
    rg = A._vet_task(jg, repo, tmp / "vt3", 30)[0]
    check(rg["fix_result"] == "fail" and A.vet_verdict(rg)[1] == "fails_at_fix" and rg["reads"] == [],
          "vet: a check needing .hg still fails at the fix (no read can supply it; the drop stands) (%s)"
          % rg.get("reads_trace"))

    # the judge's tree for the same task, built the judge's way from the hidden reads, passes the check at the fix
    d = tmp / "judge_side"
    tree = J.materialise(repo, fix, area, d / "tree", VR.judge_tree_paths({"reads": rec["reads"]}, J.TREE_PATHS))
    check(J.run_hidden(checks, tree, d)[0]["result"] == "pass",
          "judge tree from hidden reads reproduces the vet's fix-side pass")
    shutil.rmtree(d, ignore_errors=True)


ITEM_MD = "infrastructure/state/items/VR_ITEM.md"
# reads a bookkeeping file the fix itself changes (outside the area): only the fix's copy passes it
READS_ITEM = '''import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import vr_lib
assert vr_lib.f() == 2
assert "state: new" in open(os.path.join(REPO, "infrastructure", "state", "items", "VR_ITEM.md")).read()
'''


def forged(log_json):
    """A check that overwrites the trace log with `log_json` and dies before the tracer's own dump."""
    return ("import os\nfd = os.open(%r, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)\nos.write(fd, %r)\n"
            "os._exit(1)\n" % (VR.TRACE_LOG, log_json.encode()))


def t_refuse_changed(tmp):
    """ARENA_VET_READS_REFUSE_FIX_CHANGED_PATHS: a check reading a path the fix changed outside the area."""
    repo = tmp / "repo_ch"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    base = commit(repo, {LIB: "def f():\n    return 1\n", ITEM_MD: "state: old\n"}, "base")
    fix = commit(repo, {LIB: "def f():\n    return 2\n", CHECK: READS_ITEM, ITEM_MD: "state: new\n"}, "fix")
    area = A.area_for([LIB, CHECK])
    check(not any(J.in_area(ITEM_MD, [a]) for a in area), "instrument: the item file is outside the area")
    checks = [{"kind": "fix_test", "path": CHECK, "body": READS_ITEM}]
    old = VR.trace_reads(repo, fix, area, checks, tmp / "tr_old", 30)
    check(old["reads"] == [ITEM_MD], "control: without base= the trace admits the fix-changed read (%s)" % old)
    tr = VR.trace_reads(repo, fix, area, checks, tmp / "tr_new", 30, base=base)
    check(tr["reads"] == [] and tr["refused"] == [ITEM_MD],
          "trace with base: the fix-changed read is refused and reported (%s)" % tr)
    rec = A._vet_task({"task": "RP_CH", "base": base, "fix": fix, "area": area,
                       "checks": [{"path": CHECK, "body": READS_ITEM, "key": "ch-1"}]}, repo, tmp / "vt_ch", 30)[0]
    check(A.vet_verdict(rec) == (False, "fails_at_fix") and rec["reads"] == []
          and rec["reads_trace"]["refused"] == [ITEM_MD],
          "vet: the check no arm can win is fails_at_fix (unscored), not a false discriminator (%s/%s %s)"
          % (rec["fix_result"], rec["base_result"], rec.get("reads_trace")))


def t_log_shape(tmp):
    """ARENA_TRACE_HARDEN_LOG_SHAPE_KILLS_VET: a check that forges the trace log never stops the trace or the vet."""
    repo = tmp / "repo_log"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    base = commit(repo, {LIB: "def f():\n    return 1\n"}, "base")
    fix = commit(repo, {LIB: "def f():\n    return 2\n", CHECK: "x = 1\n"}, "fix")
    area = A.area_for([LIB, CHECK])
    tree = J.materialise(repo, fix, area, tmp / "log_tree")
    for raw in ("null", "[1]", '[["open", ["x"]]]'):
        try:
            seen = VR.trace_once([{"path": CHECK, "body": forged(raw)}], tree, tmp / "log_w", 30)
            check(seen == set(), "trace_once: forged log %s counts as no reads (%s)" % (raw, seen))
        except Exception as e:      # noqa: BLE001
            check(False, "trace_once: forged log %s raised %s: %s" % (raw, type(e).__name__, e))
    jobs = [{"task": "RP_LOG%d" % i, "base": base, "fix": fix, "area": area,
             "checks": [{"path": CHECK, "body": forged(raw), "key": "log-%d" % i}]}
            for i, raw in enumerate(("null", "[1]", '[["open", ["x"]]]'))]
    cache = tmp / "log_cache.jsonl"
    out = A.run_vet(jobs, repo, tmp / "log_vw", cache, workers=2, timeout=30)
    recs = A.read_vet_cache(cache)
    check(out["ran"] == 3 and not out["errors"] and len(recs) == 3
          and all(A.vet_verdict(r)[1] == "fails_at_fix" and r["reads"] == [] for r in recs.values()),
          "run_vet: three forged-log checks are vetted (fails_at_fix, no reads), none stops the vet (%s)" % out)
    # an unexpected exception in one task is reported for that task, not raised out of the vet
    saved = A._vet_task
    try:
        A._vet_task = lambda *a, **k: (_ for _ in ()).throw(TypeError("boom"))
        out = A.run_vet([dict(jobs[0], checks=[dict(jobs[0]["checks"][0], key="log-x")])], repo, tmp / "log_vw2",
                        tmp / "log_cache2.jsonl", timeout=30)
        check(out["left"] == 1 and out["errors"] and "TypeError" in out["errors"][0]["error"],
              "run_vet: a TypeError in one task is reported, the check stays unvetted (%s)" % out)
    except TypeError as e:
        check(False, "run_vet: a TypeError escaped the vet (%s)" % e)
    finally:
        A._vet_task = saved


CTRL_LIB = "src/RimMandrake/Utils/vr_ctrl.py"
CTRL = "src/RimMandrake/Utils/selftest_vr_ctrl.py"
# the negative control: imports the tree's own code, so it passes at a REAL base and fails at an empty one
CTRL_BODY = ("import os, sys\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\nimport vr_ctrl\n"
             "assert vr_ctrl.g() in (1, 2)\n")
SANE, CONTROL = "VR_SANE_FIX_ONE", "VR_CONTROL_FIX_TWO"
PROBES = {"reads": [TABLE, SCAN], "control": (CONTROL, CTRL)}


def _ledger(sane_sha, ctrl_sha):
    E = []
    for i, (iid, sha, day) in enumerate(((SANE, sane_sha, "2026-10-14"), (CONTROL, ctrl_sha, "2026-10-15"))):
        for k in ({"event": "file", "id": iid, "title": "title of " + iid, "kind": "task", "needs": "offline",
                   "for": "FOUNDRY", "ts": day + "T10:00:00Z"},
                  {"event": "verify", "id": iid, "result": "pass", "config": "c", "evidence": "e", "sha": sha[:10],
                   "ts": day + "T10:03:30Z"},
                  {"event": "close", "id": iid, "sha": sha[:10], "reason": "r", "ts": day + "T10:04:00Z"}):
            E.append(dict(k, seat="FOUNDRY", tsn="vr%d%s" % (i, k["event"])))
    return E


def _dead_base(base):
    """Mutant 1: the vet's base side gets an empty tree."""
    real = J.materialise

    def m(clone, head, area, dest, tree_paths=J.TREE_PATHS):
        if head == base:
            dest.mkdir(parents=True, exist_ok=True)
            return dest
        return real(clone, head, area, dest, tree_paths)
    return real, m


def t_census_judge(tmp):
    """ARENA_SANITY_HARDEN_GREEN_ON_DEAD_BASE: census output carried through arena_judge.judge(), and the two
    sanity probes (hidden reads present; a passes_at_base negative control), each killed by its mutant."""
    root = tmp / "cj"
    env = {"ARENA_ROOT": root / "arena", "ARENA_CLONES": root / "clones", "ARENA_PRIVATE": root / "private",
           "ARENA_JUDGE_WORK": root / "work"}
    saved_env = {k: os.environ.get(k) for k in env}
    try:
        for k, v in env.items():
            os.environ[k] = str(v)
            if k != "ARENA_PRIVATE":
                v.mkdir(parents=True)
        repo = env["ARENA_CLONES"] / "vr"
        repo.mkdir()
        git(repo, "init", "-q", "-b", "main")
        base = commit(repo, {LIB: "def f():\n    return 1\n", TABLE: "want=2\n", SCAN + "/a.txt": "a",
                             SCAN + "/b.txt": "b", CTRL_LIB: "def g():\n    return 1\n"}, "base")
        ctrl = commit(repo, {CTRL_LIB: "def g():\n    return 2\n", CTRL: CTRL_BODY}, CONTROL + ": g returns 2")
        sane = commit(repo, {LIB: "def f():\n    return 2\n", CHECK: BODY}, SANE + ": f returns 2")
        E = _ledger(sane, ctrl)
        miss: list = []
        A.census(E, repo=repo, sanity=None, old_history=[], vet=lambda *a: None, vet_missing=miss)
        check(sorted(j["task"] for j in miss) == ["RP_" + CONTROL, "RP_" + SANE],
              "census: both fixture tasks are vet candidates (%s)" % [j["task"] for j in miss])
        cache = root / "vet_cache.jsonl"
        out = A.run_vet(miss, repo, root / "vw", cache, timeout=30)
        check(out["ran"] == 2 and not out["errors"], "vet ran both fixture checks (%s)" % out)
        recs = A.read_vet_cache(cache)
        pool, rep = A.census(E, repo=repo, sanity=SANE, old_history=[], vet=A.vet_lookup(recs), probes=PROBES)
        check(rep["sanity"].get("reads") == [TABLE, SCAN] and rep["sanity"]["control"]["verdict"] == "passes_at_base",
              "census: sanity kept with its reads, negative control passes_at_base (%s)" % rep["sanity"])
        task, hidden = next((t, h) for t, h in pool if t["source_item"] == SANE)

        # mutant 1: a dead base side. The sanity item alone stays green (its base fails either way) ...
        cache_m = root / "vet_cache_dead.jsonl"
        for j in miss:                            # each task's own base side is the dead one
            real, J.materialise = _dead_base(j["base"])
            try:
                A.run_vet([j], repo, root / "vw_dead", cache_m, timeout=30)
            finally:
                J.materialise = real
        rm = A.read_vet_cache(cache_m)
        try:
            A.census(E, repo=repo, sanity=SANE, old_history=[], vet=A.vet_lookup(rm), probes={})
            check(True, "mutant 1 instrument: without the control the dead base side stays green (the finding)")
        except A.SanityFail as e:
            check(False, "mutant 1 instrument: expected the bare probe to stay green (%s)" % e)
        try:
            A.census(E, repo=repo, sanity=SANE, old_history=[], vet=A.vet_lookup(rm), probes=PROBES)
            check(False, "mutant 1 (dead base side): the negative control raises SanityFail")
        except A.SanityFail as e:
            check("negative control" in str(e), "mutant 1 (dead base side): SanityFail: %s" % str(e)[:120])

        # mutant 2: the census drops the reads before building hidden
        strip = lambda *a: {k: v for k, v in (A.vet_lookup(recs)(*a) or {}).items() if k != "reads"} or None
        try:
            A.census(E, repo=repo, sanity=SANE, old_history=[], vet=strip, probes=PROBES)
            check(False, "mutant 2 (reads dropped): SanityFail")
        except A.SanityFail as e:
            check("hidden reads" in str(e), "mutant 2 (reads dropped): SanityFail: %s" % str(e)[:120])

        # the census output through the judge: a perfect arm (the fix itself) passes the hidden check ...
        arm = J.arms()[0]
        gate = {"verdict": "pass", "arm": arm, "steps": {"tests": "pass"}, "log": "/x/gate.log"}

        class Accept:
            def __call__(self, prompt, work):
                return '{"verdict": "accept", "reasons": ["r"], "arm_guess": "unknown"}'

        def run(h, tid):
            return J.judge(task=dict(task, id=tid), hidden=h, clone=repo, base=ctrl, head=sane, arm=arm, gate=gate,
                           judges=J.Judges(Accept(), Accept(), Accept()))
        r = run(hidden, "T_CJ_GOOD")
        check(r["verdict"] == "accept" and [h["result"] for h in r["hidden"]] == ["pass"],
              "judge: census hidden file -> perfect arm's hidden check passes (%s %s)"
              % (r["verdict"], r.get("why")))
        # ... and with the reads dropped (mutant 2's judge file) it is rejected: what the probe now guards
        r = run({k: v for k, v in hidden.items() if k != "reads"}, "T_CJ_NOREADS")
        check(r["verdict"] == "reject", "judge: hidden without reads rejects the perfect arm (%s)" % r.get("why"))
        # ARENA_TRACE_HARDEN_LOG_SHAPE_KILLS_VET: a bad reads list is an invalid verdict, not a crash
        for bad in (["../x"], "src/x", [3]):
            try:
                r = run(dict(hidden, reads=bad), "T_CJ_BAD")
                check(r["verdict"] == "invalid", "judge: hidden reads %r -> invalid (%s)" % (bad, r.get("why")))
            except Exception as e:      # noqa: BLE001
                check(False, "judge: hidden reads %r raised %s: %s" % (bad, type(e).__name__, e))
    finally:
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def t_wiring(tmp):
    src = Path(J.__file__).read_text(encoding="utf-8")
    check("A.VR.judge_tree_paths(hidden, tree_paths)" in src,
          "arena_judge.judge materialises the hidden reads (judge_tree_paths in its hidden-check tree)")
    tsrc = Path(A.__file__).read_text(encoding="utf-8")
    check('**({"reads": sorted(reads)} if reads else {})' in tsrc and 'reads.update(rec.get("reads") or [])' in tsrc,
          "census copies the vet records' reads into the judge file (only when non-empty: frozen bytes stay)")
    # the vet cache key moves with this module: a trace change re-vets
    now = A.vet_runner_id()
    alt = tmp / "arena_vet_reads.py"
    alt.write_bytes(Path(VR.__file__).read_bytes() + b"\n# changed\n")
    saved = VR.__file__
    try:
        VR.__file__ = str(alt)
        other = A.vet_runner_id()
    finally:
        VR.__file__ = saved
    check(now != other and now.startswith(A.VET_RUNNER + "@"), "vet runner id hashes arena_vet_reads.py")


MODHOME = "src/Other/modhome"
IMPORTS = '''import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "src", "Other", "modhome"))
import vrmod
sys.path.insert(0, HERE)
import vr_lib
assert vr_lib.f() == vrmod.V, "FAIL vr_lib.f() != vrmod.V"
print("ok vrmod")
'''


def t_import_miss(tmp):
    """A check importing a module from a sys.path dir outside the tree: the audit hooks see no open/stat of a missing
    dir, so only the meta_path finder (_Miss) can name it (ARENA_VET_REPAIR_SANDBOX_STARVED_CHECKS)."""
    repo = tmp / "repo_imp"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    chk = "src/RimMandrake/Utils/selftest_vr_imp.py"
    base = commit(repo, {LIB: "def f():\n    return 1\n", MODHOME + "/vrmod.py": "V = 2\n"}, "base")
    fix = commit(repo, {LIB: "def f():\n    return 2\n", chk: IMPORTS}, "fix")
    area = A.area_for([LIB, chk])
    check(not any(a == MODHOME or MODHOME.startswith(a.rstrip("/") + "/") for a in area),
          "control: the module home is outside the area (%s)" % area)
    checks = [{"kind": "fix_test", "path": chk, "body": IMPORTS}]
    tr = VR.trace_reads(repo, fix, area, checks, tmp / "trace_imp", 30)
    hit = [r for r in tr["reads"] if r == MODHOME or r.startswith(MODHOME + "/")]
    check(bool(hit) and tr["converged"], "trace: a failed import names its sys.path dir/module (%s)" % tr)
    job = {"task": "RP_VR_IMP", "base": base, "fix": fix, "area": area,
           "checks": [{"path": chk, "body": IMPORTS, "key": "vr-imp"}]}
    rec = A._vet_task(job, repo, tmp / "vt_imp", 30)[0]
    check(rec["fix_result"] == "pass" and rec["base_result"] == "fail",
          "vet: with the traced import dir the check passes at the fix, fails at base (%s/%s, reads %s)"
          % (rec["fix_result"], rec["base_result"], rec.get("reads")))
    check(all("/tmp/arena-check-state/" in v for v in J.CHECK_ENV.values()) and "J.CHECK_ENV" in
          Path(VR.__file__).read_text(encoding="utf-8"), "trace runs with the judge's CHECK_ENV (writable state under /tmp)")


def t_sanity():
    check(A.SANITY_ITEM == "ROAST_STICK_FIX_DISABLED_COOK_STAT_ERRORS",
          "sanity default is the item that discriminates under the judge route (ARENA_SANITY_ITEM_FIX_NOT_DISCRIMINATING)")
    cache = A.vet_cache_path()
    recs = [r for r in A.read_vet_cache(cache).values() if r.get("task") == "RP_" + A.SANITY_ITEM
            and r.get("runner") == A._runner_id()] if cache.exists() else []
    if not recs:
        print("SKIP  sanity vet record: none under the current runner yet (run `arena_tasks.py vet`) (UNMEASURED)")
        return
    check(any(A.vet_verdict(r)[0] for r in recs), "the sanity item's vet record discriminates (%s)"
          % [(r["fix_result"], r["base_result"]) for r in recs])
    check(any("src/RimStarWars/Cuisine/Defs" in (r.get("reads") or []) for r in recs),
          "the sanity item discriminates through its traced read (src/RimStarWars/Cuisine/Defs)")


def main():
    tmp = Path(tempfile.mkdtemp(prefix="arena_vet_reads_st_"))
    try:
        t_units(tmp)
        t_fixture(tmp)
        t_refuse_changed(tmp)
        t_log_shape(tmp)
        t_census_judge(tmp)
        t_wiring(tmp)
        t_import_miss(tmp)
        t_sanity()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
