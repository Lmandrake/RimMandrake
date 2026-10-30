#!/usr/bin/env python3
"""arena_safe_git_traps.py - test helper (not a selftest): plants every trap a build helper can leave in a .git so a
selftest can show plain git is fooled and arena_safe_git is not. Used by selftest_arena_gate.py and
selftest_arena_ralph_c.py. Writes only under the directory it is given."""
import os
import stat
import subprocess
from pathlib import Path

ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
ENV.pop("GIT_CONFIG_GLOBAL", None)
TRAPS = ("replace", "graft", "attributes", "fsmonitor", "hooksPath", "filter", "textconv", "external", "sshCommand",
         "uploadpack")


def git(repo, *a, check=True, env=None):
    r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, env=env or ENV)
    if check and r.returncode:
        raise RuntimeError("git %s: %s" % (a, r.stderr))
    return r.stdout.strip()


def plain(repo, *a):
    """What an unhardened caller sees: bare `git -C repo ...`."""
    r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, env=ENV)
    return r.stdout


def make_repo(root, name="builder"):
    """-> (repo, A, B): two commits; f.txt alpha -> beta, g.txt kept, .gitattributes routes f.txt to the `evil` drivers."""
    repo = Path(root) / name
    repo.mkdir(parents=True)
    git(repo, "init", "-q")
    (repo / "f.txt").write_text("alpha\n")
    (repo / "g.txt").write_text("keep\n")
    (repo / ".gitattributes").write_text("f.txt diff=evil filter=evil\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "A")
    a = git(repo, "rev-parse", "HEAD")
    (repo / "f.txt").write_text("beta\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "B")
    return repo, a, git(repo, "rev-parse", "HEAD")


def _script(path, body):
    path.write_text("#!/bin/sh\n" + body)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return str(path)


def plant(repo, a, b, traps=TRAPS):
    """Plant `traps` into repo/.git. -> markers dir: a file in it per trap whose code ran as the harness."""
    repo = Path(repo)
    mk = repo.parent / (repo.name + "_markers")
    sc = repo.parent / (repo.name + "_scripts")
    mk.mkdir(exist_ok=True)
    sc.mkdir(exist_ok=True)
    gd = repo / ".git"

    def mark(n, tail="cat"):
        return _script(sc / n, "touch '%s/%s'\n%s\n" % (mk, n, tail))
    if "replace" in traps:      # B is read as a commit whose f.txt is EVIL
        t = git(repo, "rev-parse", b + "^{tree}")
        (repo / "f.txt").write_text("EVIL\n")
        env = dict(ENV, GIT_INDEX_FILE=str(repo.parent / "idx_replace"))
        git(repo, "read-tree", t, env=env)
        git(repo, "update-index", "--add", "--cacheinfo", "100644,%s,f.txt" % git(repo, "hash-object", "-w", "f.txt"), env=env)
        t2 = git(repo, "write-tree", env=env)
        c = git(repo, "commit-tree", t2, "-p", a, "-m", "evil")
        git(repo, "replace", "-f", b, c)
        (repo / "f.txt").write_text("beta\n")
    if "graft" in traps:       # B is read as parentless
        with open(gd / "info" / "grafts", "a") as f:
            f.write(b + "\n")
    attrs = []
    if "attributes" in traps:
        attrs.append("g.txt export-ignore")
    if attrs:
        (gd / "info").mkdir(exist_ok=True)
        (gd / "info" / "attributes").write_text("\n".join(attrs) + "\n")
    if "fsmonitor" in traps:
        git(repo, "config", "core.fsmonitor", mark("fsmonitor", "exit 1"))
    if "hooksPath" in traps:
        hk = repo.parent / (repo.name + "_hooks")
        hk.mkdir(exist_ok=True)
        _script(hk / "post-checkout", "touch '%s/hooksPath'\n" % mk)
        git(repo, "config", "core.hooksPath", str(hk))
    if "filter" in traps:
        git(repo, "config", "filter.evil.clean", mark("filter"))
        git(repo, "config", "filter.evil.smudge", mark("filter_smudge"))
    if "textconv" in traps:
        git(repo, "config", "diff.evil.textconv", mark("textconv", "echo TEXTCONV"))
    if "external" in traps:
        git(repo, "config", "diff.external", mark("external", "echo EXTERNAL"))
    if "sshCommand" in traps:
        git(repo, "config", "core.sshCommand", mark("sshCommand", "exit 1"))
    if "uploadpack" in traps:
        git(repo, "config", "remote.origin.uploadpack", mark("uploadpack", "exit 1"))
    return mk


def fired(mk):
    return sorted(p.name for p in Path(mk).iterdir())
