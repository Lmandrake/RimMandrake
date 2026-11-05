#!/usr/bin/env python3
"""A passed git reach repair gives the Marker's box git history (CHECKER_REACH_BUILD_GIT_AND_GH_ADAPTERS, gen 3).

The instance: gen 1 gave the git/gh/proc gaps offbox adapters (git log at the candidate, gh api reads, a /proc census) and the
repair "passed its probe, yet the Judge is still blind" on JAM_CLASS_BUILD_OPS_DETECTOR_PER_CLASS, OPS_TMP_DRAIN_RESTORE_DEVU
and the four items waiting on them: their IN-BOX proofs run git themselves (git rev-parse HEAD, git show <rev>:path, the
objects of a fixed.sha), and an adapter's reading outside the box cannot make a selftest inside it green. Rows:
  (1) make_box with the git_history grant: tree/.git whose HEAD is the candidate, every ancestor's objects readable (the
      clone's own objects and its alternates, as a check clone has), `git show sha:path` works, no branch or remote ref;
  (2) props() binds the shared object store read only at a box path and leaves the deny list as it was (the clone's own
      objects are copied in, so no folder on the way to them opens);
  (3) the box without the grant is unchanged (no .git), and its prompt still says no git history; with it, the prompt
      says the history is there and that commit messages are workers' words;
  (4) the reach repair carries the grant: the JAM text classes as git (not gh), the git and gh rows grant git_history
      (a /proc text that names git gains it from every matching row),
      an applied repair's grants() returns it, a Judge may propose it by name, and a stored proposal from before the
      grant (the six blocked items) gains it from its blind text when the sweep re-probes;
  (5) the sweep hands the grant to the probe, and the probe of a grant is a real one when its source repo is given.
Rows 1-4 fail on the code before the grant (make_box had no grants and the gh row took the JAM text)."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless_reachfix as RF    # noqa: E402
import relentless_wall as W         # noqa: E402

FAILS = []
GRANT = getattr(W, "GIT_GRANT", "git_history")
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
JAM_TEXT = ("git objects for fixed.sha 7684d1bcbe/b010c5b289/6ab91a442b/a558ca513f/bbaccde0b0: no .git in the export (ls), "
            "/home/mandrake/rm/bench/.git permission denied (ls), git ls-remote git@github.com:Lmandrake/RimMandrake failed")
DEVU_TEXT = ("process visibility the reaper's hold check needs: 'ls -l /proc/1/cwd' -> Permission denied; the in-box proof "
             "is red only for that reason; git history/origin/main for the committed-saves guard: the tree is a git-less "
             "export, so 'git show <rev>:...' cannot run")


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + ("" if cond else "  %s" % str(detail)[:300]))
    if not cond:
        FAILS.append(name)


def git(d, *a):
    return subprocess.run(["git", "-C", str(d), *a], capture_output=True, text=True, env=ENV)


def store_and_clone(root):
    """A shared object store and a check clone that borrows it through alternates, like ~/rm/store.git and a check clone."""
    store = Path(root, "store")
    git(root, "init", "-q", str(store))
    Path(store, "a.py").write_text("one\n", encoding="utf-8")
    Path(store, "conversations").mkdir()
    Path(store, "conversations/x.md").write_text("withheld\n", encoding="utf-8")
    git(store, "add", "-A")
    git(store, "commit", "-qm", "root")
    old = git(store, "rev-parse", "HEAD").stdout.strip()
    clone = Path(root, "clone")
    subprocess.run(["git", "clone", "-q", "--shared", str(store), str(clone)], check=True, env=ENV)
    Path(clone, "a.py").write_text("two\n", encoding="utf-8")
    git(clone, "commit", "-qam", "the candidate")
    sha = git(clone, "rev-parse", "HEAD").stdout.strip()
    git(clone, "branch", "-q", "later")
    return store, clone, old, sha


def prof(root):
    return {"enforce": True, "box_root": str(Path(root, "boxes")), "deny": [], "deny_children": [root],
            "tmpfs": [], "tree_exclude": ["conversations"], "read_through": []}


def test_box(root):
    store, clone, old, sha = store_and_clone(root)
    Path(root, "the-store").mkdir()
    p = prof(root)
    try:
        box = W.make_box(p, str(clone), sha, "g1", grants=[GRANT])
    except TypeError as e:
        check("make_box takes the git_history grant", False, e)
        return None
    tree = Path(box, "tree")
    sobj = os.path.realpath(str(Path(store, ".git/objects")))
    binds = W.git_reads(box)
    check("(2) the shared store is bound at a box path, the clone's own objects copied in", len(binds) == 1
          and binds[0][0] == sobj and binds[0][1].startswith(box + "/gitobj/"), binds)
    pr = W.props(p, box, [str(Path(root, "the-store"))])
    check("(2) the bind is read only and may be gone", ("BindReadOnlyPaths=-%s:%s" % binds[0]) in pr if binds else False, pr)
    check("(2) the deny list is untouched: the store repo and the clone stay denied", ("InaccessiblePaths=" + str(store)) in pr
          and ("InaccessiblePaths=" + str(clone)) in pr and not any(x.startswith("ReadOnlyPaths=") for x in pr), pr)
    check("(2) the supervisor's store stays denied", ("InaccessiblePaths=" + str(Path(root, "the-store"))) in pr)
    for src, dst in binds:      # outside a unit, stand in for the mount with a link
        os.rmdir(dst)
        os.symlink(src, dst)
    check("(1) HEAD is the candidate", git(tree, "rev-parse", "HEAD").stdout.strip() == sha, git(tree, "rev-parse", "HEAD"))
    check("(1) an ancestor in the shared store reads", git(tree, "cat-file", "-t", old).stdout.strip() == "commit")
    check("(1) git show sha:path reads the blob", git(tree, "show", "%s:a.py" % sha).stdout == "two\n")
    refs = git(tree, "for-each-ref").stdout.strip()
    check("(1) no branch, remote or tag ref: only HEAD", refs == "", refs)
    lg = git(tree, "log", "--all", "--format=%H").stdout.split()
    check("(1) --all walks the candidate's ancestry only", lg == [sha, old], lg)
    st = git(tree, "status", "--porcelain")
    check("(1) the index is the candidate's, the excluded folder skipped: git status is clean, no alternate error",
          st.stdout.splitlines() == [] and "alternate" not in st.stderr, (st.stdout, st.stderr))
    txt = W.marker_prompt({"candidate": {"sha": sha, "evidence": "e"}, "contract": {"proof": "x"}}, "ITEM", box)
    check("(3) the granted prompt says the history is there", "read-only git history" in txt and "no git history" not in txt
          and "workers' words" in txt, txt[:400])
    plain = W.make_box(p, str(clone), sha, "g2")
    check("(3) no grant, no .git", not Path(plain, "tree/.git").exists() and W.git_reads(plain) == [])
    txt = W.marker_prompt({"candidate": {"sha": sha, "evidence": "e"}, "contract": {"proof": "x"}}, "ITEM", plain)
    check("(3) no grant, the prompt still says no git history", "no git history" in txt)
    check("(3) no grant, no git bind", not any("gitobj" in x for x in W.props(p, plain, [])))
    cap, W.GIT_COPY_MAX = getattr(W, "GIT_COPY_MAX", 0), 1     # the clone's own objects past the cap: no grant
    try:
        bad = W.make_box(p, str(clone), sha, "g3", grants=[GRANT])
    finally:
        W.GIT_COPY_MAX = cap
    check("(3) a grant that cannot be made leaves the plain box, never a crash", not Path(bad, "tree/.git").exists()
          and Path(bad, "git_grant_failed").exists() and W.git_reads(bad) == [])
    W.remove_box(bad)
    W.remove_box(plain)
    return box, store, clone, sha


def test_reach(root):
    r = json.loads(Path(HERE, "relentless_rules.json").read_text(encoding="utf-8"))
    check("(4) the JAM text classes as git, not gh", RF.classify(r, [JAM_TEXT])["class"] == "git", RF.classify(r, [JAM_TEXT]))
    for c in ("git", "gh"):
        row = [x for x in RF.classes(r) if x["class"] == c][0]
        check("(4) the %s row grants git_history" % c, GRANT in (row.get("grants") or []), row)
    cls = RF.classify(r, [DEVU_TEXT])
    prop = RF.propose(r, cls, [], [], DEVU_TEXT)
    check("(4) the seed proposal for the DEVU text carries the grant", GRANT in prop.get("grants", []), prop)
    prop = RF.propose(r, cls, ["git_history"], [], DEVU_TEXT)
    check("(4) a Judge may propose the grant by name", prop.get("grants") == [GRANT] and not prop["refused"], prop)
    st = {"reach": {"status": "applied", "class": "proc", "proposal": {"adapters": ["proc_cwds"], "paths": [],
                                                                        "grants": [GRANT]}}}
    check("(4) an applied repair's grants", RF.grants(st) == [GRANT], RF.grants(st))
    check("(4) a waiting one grants nothing", RF.grants({"reach": dict(st["reach"], status="probe")}) == [])
    old = {"adapters": ["proc_cwds"], "paths": [], "by": "seed", "refused": {}}
    st = {"reach": {"class": "proc", "proposal": old, "still_blind": DEVU_TEXT}, "blind": None}
    check("(4) a stored proposal from before the grant gains it on the re-probe",
          GRANT in RF.refreshed(r, st).get("grants", []), RF.refreshed(r, st))


def test_sweep_and_probe(made):
    import selftest_relentless_reachfix as SR
    x = SR.rig(probe=(True, "ok"))
    seen = []
    x.w.reach_probe = lambda r, paths, adapters, values, store_root, grants=(): (seen.append(list(grants)) or (True, "ok"))
    SR.B.to_check(x, "I0")
    SR.blind(x, "I0", what=JAM_TEXT)
    x.tick()
    check("(5) the sweep hands the git grant to the probe", seen and GRANT in seen[0], seen)
    st = x.st("I0")
    check("(5) the applied overlay holds the grant", RF.grants(st) == [GRANT], st.get("reach"))
    x.done()
    if not made or not os.path.exists("/usr/bin/systemd-run") or os.environ.get("RELENTLESS_NO_UNIT_PROBE"):
        print("skip (5) live probe: no systemd-run here")
        return
    import relentless as R
    box, store, clone, sha = made
    fx = R.Effects.__new__(R.Effects)
    fx.books = str(clone)
    r = {"walls": {"marker": dict(prof(os.path.dirname(str(clone))), box_root=tempfile.mkdtemp(prefix="gprobe"))}}
    sroot = tempfile.mkdtemp(prefix="gstore")      # a store root that exists: a missing denied path fails the unit
    good, why = fx.reach_probe(r, [], [], {"sha": sha, "repo": str(clone)}, sroot, grants=[GRANT])
    if "probe unit" in why or "Failed to" in why or "bus" in why.lower():
        print("skip (5) live probe: no user systemd here (%s)" % why[:120])
        return
    check("(5) the grant's probe reads HEAD inside the wall", good and sha[:10] in why, why)
    bad, why = fx.reach_probe(r, [], [], {"sha": "0" * 40, "repo": str(clone)}, sroot, grants=[GRANT])
    check("(5) a sha the history lacks fails its probe", not bad, why)


def main():
    root = tempfile.mkdtemp(prefix="gitgrant")
    made = None
    for t in (lambda: test_box(root), lambda: test_reach(root), lambda: test_sweep_and_probe(made)):
        try:
            got = t()
            made = made or got
        except Exception as e:      # a row that crashes is a red row, not a dead selftest
            check("row ran", False, "%s: %s" % (type(e).__name__, e))
    if made:
        W.remove_box(made[0])
    print("RESULT: %s" % ("GREEN" if not FAILS else "RED %d: %s" % (len(FAILS), ", ".join(FAILS))))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
