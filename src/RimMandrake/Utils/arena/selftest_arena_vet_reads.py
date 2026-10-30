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
NEEDS_GIT = 'import os\nassert os.path.isdir(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".git"))\n'


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
          "checks": [{"path": CHECK.replace("vr_lib", "vr_git"), "body": NEEDS_GIT, "key": "vr-3"}]}
    rg = A._vet_task(jg, repo, tmp / "vt3", 30)[0]
    check(rg["fix_result"] == "fail" and A.vet_verdict(rg)[1] == "fails_at_fix" and rg["reads"] == [],
          "vet: a check needing .git still fails at the fix (no read can supply it; the drop stands) (%s)"
          % rg.get("reads_trace"))

    # the judge's tree for the same task, built the judge's way from the hidden reads, passes the check at the fix
    d = tmp / "judge_side"
    tree = J.materialise(repo, fix, area, d / "tree", VR.judge_tree_paths({"reads": rec["reads"]}, J.TREE_PATHS))
    check(J.run_hidden(checks, tree, d)[0]["result"] == "pass",
          "judge tree from hidden reads reproduces the vet's fix-side pass")
    shutil.rmtree(d, ignore_errors=True)


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
        t_wiring(tmp)
        t_sanity()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
