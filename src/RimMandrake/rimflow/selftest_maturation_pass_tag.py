#!/usr/bin/env python3
"""Selftest for the pass tag of maturation.py (page design/specs/2026-11-20-maturation-pass-tag/boundary.md; item
RIMMANDRAKE_TAG_EACH_PASSED_MOD_VERSION_PIPELINE_DOES_IT). Each test builds a fixture clone with a bare origin and a
small `publish` of its own, moves a fixture mod his_walk -> passed through `advance` (its evaluation and refusal
store stubbed: what is under test is what happens after the move is allowed) or calls `tag_pass`, and MEASURES the
tag on origin with `git ls-remote`. Every test prints what it read. Red on the base 0fe80361702d (no tag code)."""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maturation as M  # noqa: E402

MOD, VER = "TagMod", "0.1.0"
TAG = "mod/%s/v%s" % (MOD, VER)
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}
PUBLISH = """#!/bin/sh
# fixture publish: commit the named paths, push them to origin main, print PUBLISHED <sha>
set -e
[ -f FAIL_PUBLISH ] && { echo "fixture publish: refused on purpose" >&2; exit 1; }
msg=""
if [ "$1" = "-m" ]; then msg="$2"; shift 2; fi
git add -- "$@"
git commit -q -m "$msg" -- "$@"
git push -q origin HEAD:main
echo "PUBLISHED $(git rev-parse HEAD)"
"""
REJECT_TAGS = """#!/bin/sh
while read old new ref; do case "$ref" in refs/tags/*) echo "fixture origin: tags refused" >&2; exit 1;; esac; done
exit 0
"""
FAILS = []


def check(ok, what, got=None):
    print("%s %s%s" % ("PASS" if ok else "FAIL", what, "" if got is None else "  [read: %s]" % (got,)))
    if not ok:
        FAILS.append(what)


def git(cwd, *a, check_=True):
    r = subprocess.run(["git", "-C", cwd] + list(a), capture_output=True, text=True, timeout=60)
    if check_ and r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr.strip()))
    return r.stdout.strip()


def remote_tag(work):
    """-> the commit the tag peels to on origin, or None. Measured with ls-remote, never the clone's own refs."""
    out = git(work, "ls-remote", "origin", "refs/tags/%s^{}" % TAG)
    return out.split()[0] if out else None


def fixture(tmp, name):
    bare, work = os.path.join(tmp, name + ".git"), os.path.join(tmp, name)
    git(tmp, "init", "-q", "--bare", "-b", "main", bare)
    git(tmp, "init", "-q", "-b", "main", work)
    git(work, "remote", "add", "origin", bare)
    with open(os.path.join(work, "publish"), "w") as f:
        f.write(PUBLISH)
    os.chmod(os.path.join(work, "publish"), 0o755)
    vd = os.path.join(work, "design", "concepts", MOD, "version")
    os.makedirs(vd)
    with open(os.path.join(vd, "stage_record.json"), "w") as f:
        json.dump({"mod": MOD, "version": VER, "stage": "his_walk", "moves": [], "cycles": {"visit": 0, "total": 0}},
                  f, indent=1)
    with open(os.path.join(work, "design", "concepts", MOD, "journal.md"), "w") as f:
        f.write("# TagMod journal\n\n- **Stage now:** his walk.\n- **Waiting on:** his walk.\n")
    with open(os.path.join(work, ".gitignore"), "w") as f:   # as the repo's .gitignore does (its line 357)
        f.write("design/concepts/*/.stage_move.lock\n")
    git(work, "add", "publish", ".gitignore", "design")
    git(work, "commit", "-q", "-m", "fixture base")
    git(work, "push", "-q", "origin", "main")
    return work, bare


@contextlib.contextmanager
def stubbed():
    """The move is allowed: evaluate passes, the refusal store takes it, the pass record is a small fixed one."""
    saved = (M.evaluate, M.tag_new_since, M.RC.submit, M.pass_record, M.ledger_stage_move)

    def evaluate(root, mod, to, **kw):
        rec = M.load(root, mod)
        return {"ok": True, "from": rec["stage"], "to": to,
                "revision": (rec["stage"], rec.get("version"), len(rec.get("moves") or [])),
                "walk_identity": {"visit_record": "version/in_game/visit_1/exit.json", "mod_hash": "h"},
                "verdict": {"ok": True, "sha": "fixture", "passed": [{"clause": "owner_said"}], "refusals": [],
                            "item": "%s@%s" % (mod, VER), "family": "fixture"}}
    M.evaluate = evaluate
    M.tag_new_since = lambda v: 0
    M.RC.submit = lambda v, now=None: {"ok": True, "counted": False, "errors": []}
    M.pass_record = lambda root, mod, rec, owner, sha, t, wid: ("%s/%s.json" % (M.PASS_RECORD_DIR, rec["version"]),
                                                                {"mod": mod, "version": rec["version"]})
    M.ledger_stage_move = lambda *a, **k: None
    try:
        yield
    finally:
        M.evaluate, M.tag_new_since, M.RC.submit, M.pass_record, M.ledger_stage_move = saved


def do_pass(work):
    with stubbed():
        return M.advance(work, MOD, "passed", by="CONDUCTOR", why="his walk passed it", owner="OWNER:1")


def pass_file(work):
    return os.path.join(work, "design", "concepts", MOD, M.PASS_RECORD_DIR, VER + ".json")


def t_pass_lands_and_tags(tmp):
    work, _ = fixture(tmp, "lands")
    r = do_pass(work)
    head = git(work, "rev-parse", "origin/main")
    added = git(work, "log", "--diff-filter=A", "--format=%H", "origin/main", "--",
                os.path.relpath(pass_file(work), work))
    on_origin = remote_tag(work)
    tag = r.get("tag") or {}
    check(r.get("ok") and M.load(work, MOD)["stage"] == "passed", "the move to passed is made", r.get("ok"))
    check(added == head, "the PUBLISHED commit is the one that adds the pass record", (added[:10], head[:10]))
    check(on_origin == head and tag.get("name") == TAG and tag.get("commit") == head and tag.get("pushed") is True,
          "origin's tag %s peels to the pass commit and res['tag'] says so" % TAG,
          (on_origin and on_origin[:10], tag))
    kind = git(work, "cat-file", "-t", "refs/tags/" + TAG)
    check(kind == "tag", "the tag is annotated (a tag object, not a bare ref)", kind)
    check(not r.get("untagged"), "no untagged outcome on a clean pass", r.get("untagged"))
    clean = git(work, "status", "--porcelain", "--", "design")
    check(clean == "", "the pass's own files are all committed", clean or "clean")


def t_untagged_pass_is_loud(tmp):
    # planted fault 1: origin refuses every tag push
    work, bare = fixture(tmp, "loud_push")
    hook = os.path.join(bare, "hooks", "pre-receive")
    with open(hook, "w") as f:
        f.write(REJECT_TAGS)
    os.chmod(hook, 0o755)
    r = do_pass(work)
    u = r.get("untagged") or {}
    check(r.get("ok") and M.load(work, MOD)["stage"] == "passed" and os.path.isfile(pass_file(work)),
          "a push that fails leaves the move made and the pass record written once", M.load(work, MOD)["stage"])
    check(u.get("name") == TAG and u.get("step") == "push" and "tag-pass %s" % MOD in (u.get("retry") or "")
          and not r.get("tag") and remote_tag(work) is None,
          "the failed push is res['untagged'] with name, step push and the retry command; no res['tag']", u)
    # planted fault 2: the landing itself fails
    work2, _ = fixture(tmp, "loud_land")
    open(os.path.join(work2, "FAIL_PUBLISH"), "w").close()
    r2 = do_pass(work2)
    u2 = r2.get("untagged") or {}
    check(u2.get("step") == "land" and "refused on purpose" in (u2.get("why") or "") and not r2.get("tag"),
          "a landing that fails is res['untagged'] step land, its cause quoted", u2)
    # the CLI: PASSED BUT NOT TAGGED, exit 5
    out = io.StringIO()
    with stubbed(), contextlib.redirect_stdout(out):
        work3, _ = fixture(tmp, "loud_cli")
        open(os.path.join(work3, "FAIL_PUBLISH"), "w").close()
        rc = M.main(["--root", work3, "advance", MOD, "--to", "passed", "--by", "CONDUCTOR", "--why", "x",
                     "--owner-said", "OWNER:1"])
    said = out.getvalue()
    check(rc == 5 and "PASSED BUT NOT TAGGED" in said and TAG in said,
          "the CLI prints PASSED BUT NOT TAGGED with the tag name and exits 5", (rc, said.strip().splitlines()[-1:]))


def t_tag_taken_refuses_before_write(tmp):
    work, _ = fixture(tmp, "taken")
    git(work, "tag", "-a", "-m", "someone else", TAG)
    r = do_pass(work)
    check(not r.get("ok") and r.get("tag_taken") and M.load(work, MOD)["stage"] == "his_walk"
          and not os.path.exists(pass_file(work)),
          "a taken tag name refuses the pass before any file is written", (r.get("ok"), r.get("tag_taken")))


def t_retry_tags_the_recorded_commit(tmp):
    work, bare = fixture(tmp, "retry")
    hook = os.path.join(bare, "hooks", "pre-receive")
    with open(hook, "w") as f:
        f.write(REJECT_TAGS)
    os.chmod(hook, 0o755)
    r = do_pass(work)
    pass_commit = git(work, "log", "--diff-filter=A", "--format=%H", "origin/main", "--",
                      os.path.relpath(pass_file(work), work))
    os.remove(hook)
    git(work, "tag", "-d", TAG)          # a clone that never had the tag (another seat's): the retry makes it
    with open(os.path.join(work, "later.txt"), "w") as f:      # main moves on after the pass
        f.write("later\n")
    git(work, "add", "later.txt")
    git(work, "commit", "-q", "-m", "later work")
    git(work, "push", "-q", "origin", "main")
    t1 = M.tag_pass(work, MOD, VER)
    on_origin = remote_tag(work)
    check((r.get("untagged") or {}).get("step") == "push" and (t1.get("tag") or {}).get("commit") == pass_commit
          and on_origin == pass_commit,
          "the retry tags the commit that added the pass record, not HEAD, and origin shows it",
          (on_origin and on_origin[:10], pass_commit[:10], git(work, "rev-parse", "HEAD")[:10]))
    t2 = M.tag_pass(work, MOD, VER)
    check(t2.get("already") and (t2.get("tag") or {}).get("commit") == pass_commit and not t2.get("untagged"),
          "a second run makes nothing new (already)", t2)
    t3 = M.tag_pass(work, MOD, "9.9.9")
    check((t3.get("untagged") or {}).get("step") == "land",
          "a version no commit on origin/main recorded is untagged, step land", t3.get("untagged"))


def t_no_commit_outside_its_own_root(tmp):
    work, _ = fixture(tmp, "outside")
    inner = os.path.join(work, "inner")
    shutil.copytree(os.path.join(work, "design"), os.path.join(inner, "design"))
    shutil.copy2(os.path.join(work, "publish"), os.path.join(inner, "publish"))   # a copied tree, publish and all
    before = (git(work, "rev-parse", "HEAD"), git(work, "tag", "-l"))
    r = do_pass(inner)
    after = (git(work, "rev-parse", "HEAD"), git(work, "tag", "-l"))
    plain = os.path.join(tmp, "plain")
    shutil.copytree(os.path.join(work, "design"), os.path.join(plain, "design"))
    r2 = do_pass(plain)
    check((r.get("untagged") or {}).get("step") == "land" and before == after and remote_tag(work) is None,
          "a root inside another clone commits, tags and pushes nothing there", (r.get("untagged"), after[1]))
    check((r2.get("untagged") or {}).get("step") == "land" and r2.get("ok"),
          "a plain folder (no git) is untagged, step land", r2.get("untagged"))


def main():
    tests = [t_pass_lands_and_tags, t_untagged_pass_is_loud, t_tag_taken_refuses_before_write,
             t_retry_tags_the_recorded_commit, t_no_commit_outside_its_own_root]
    saved_env = {k: os.environ.get(k) for k in GIT_ENV}
    os.environ.update(GIT_ENV)
    tmp = tempfile.mkdtemp(prefix="pass_tag_selftest_")
    try:
        for t in tests:
            try:
                t(tmp)
            except Exception as e:  # a crash is a FAIL of that test, named, never a silent skip
                check(False, "%s crashed: %r" % (t.__name__, e))
                traceback.print_exc(limit=2)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    print("selftest_maturation_pass_tag: %d tests, %d checks failed%s"
          % (len(tests), len(FAILS), "" if not FAILS else ": " + "; ".join(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
