"""The paths a hidden check reads outside the judge's tree, measured by a trace at the fix (ARENA_TREE_FIX_OMITS_CHECK_READ_PATHS).

arena_judge.materialise writes only TREE_PATHS + the task's area dirs. A hidden check that reads a file outside that
set (an XML def, a C# source, a directory it scans) fails, or skips, identically at base and at the fix, so the vet
rejects a good task as non-discriminating. The task's `area` cannot simply be widened: it is the ARM's scope (the gate's
s_scope step and the neutralised diff both use it), so widening it would let an arm edit, and would hint, what the
hidden check reads. The read set is judge-only instead: hidden["reads"], written by the census from the vet record.

TRACE. Only a check that fails at the fix under the plain tree is traced (one that passes needs nothing more, and the
judge then reproduces it with no reads). The trace runs the check inside the judge's own sandbox (run_sandboxed, kind
"check", its own tree copy as the only writable path) under TRACER: an audit hook records every `open`, `os.listdir`,
`os.scandir` and `glob.glob` path, and os.stat/os.lstat are wrapped so an exists()/isdir() probe is seen too. A
recorded path under the tree that is ABSENT from the tree but present at the fix commit is added: a file exactly, a
directory whole (refused, and reported in `too_wide`, above READ_DIR_CAP blobs). The tree is re-materialised and the
trace re-run until no new read appears (at most ROUNDS rounds; `converged` says whether it did), since newly present files lead to further reads.

REFUSED (ARENA_VET_READS_REFUSE_FIX_CHANGED_PATHS). A read the fix itself changed (base..fix, outside the area:
a bookkeeping path such as infrastructure/state/items/*, which area_for leaves out) is never added: the judge
materialises the reads from the ARM's head, and an arm may not touch a path outside its area, so the base copy is all
it can supply. Adding it would let the vet measure a pass no arm can win (a false discriminator). A directory read
holding such a path is refused too. Refused reads are reported (`refused`); the check is then measured without them,
so it fails at the fix and is unscored, and a task left with no scored check stays out of the pool.

MALFORMED LOG (ARENA_TRACE_HARDEN_LOG_SHAPE_KILLS_VET). The check runs in the same process as the tracer and can
overwrite the log. Anything but a JSON list of [kind, path] string pairs counts as NO reads (never an exception that
stops the vet). A well-formed forged log can name a committed path: bounded (only committed, non-.git paths inside the
tree are added, and the check could open that path anyway).

RESIDUAL (stated). A read made only by a subprocess the check spawns, or after an os._exit, is not seen; a check that
reads a path only on the base side's code path is not traced (the fix side decides the set, as a perfect arm's tree).

    judge_tree_paths(hidden, tree_paths)  the judge's materialise tree paths: tree_paths + the validated hidden reads
    trace_reads(repo, fix, area, checks, work, timeout, base=)  -> {"reads", "too_wide", "refused", "rounds",
                                                                  "converged"}
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

ROUNDS = 12          # a check that dies at its first missing file reveals one read per round
READ_DIR_CAP = 2000          # blobs: a directory read wider than this is not materialised (src/ is ~2 GB)
TRACE_LOG = ".arena_trace_reads.json"

TRACER = r'''
import os, sys, runpy, json
target, log = sys.argv[1], sys.argv[2]
root = os.path.realpath(os.getcwd())
seen = set()
def rec(p, kind):
    try:
        if p is None:
            p = "."
        if isinstance(p, int):
            return
        p = os.fsdecode(p)
        a = os.path.normpath(os.path.join(os.getcwd(), p))
        if a == root or a.startswith(root + os.sep):
            r = os.path.relpath(a, root)
            if r != log:
                seen.add((kind, r))
    except BaseException:
        pass
_WILD = "*?["
def hook(ev, args):
    if ev == "open" and args:
        rec(args[0], "open")
    elif ev in ("os.listdir", "os.scandir") and args:
        rec(args[0], "list")
    elif ev == "glob.glob" and args and isinstance(args[0], (str, bytes)):
        g = os.fsdecode(args[0])
        cut = min([g.find(c) for c in _WILD if c in g] or [len(g)])
        rec(os.path.dirname(g[:cut]) if cut < len(g) else g, "list")
sys.addaudithook(hook)
_st, _lst = os.stat, os.lstat
def _stat(p, *a, **k):
    rec(p, "stat")
    return _st(p, *a, **k)
def _lstat(p, *a, **k):
    rec(p, "stat")
    return _lst(p, *a, **k)
os.stat, os.lstat = _stat, _lstat
def dump():
    fd = os.open(os.path.join(root, log), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    os.write(fd, json.dumps(sorted(seen)).encode())
    os.close(fd)
sys.argv = [target]
sys.path.insert(0, os.path.dirname(os.path.abspath(target)))
try:
    runpy.run_path(target, run_name="__main__")
except BaseException:
    pass
finally:
    dump()
'''


def judge_tree_paths(hidden: dict | None, tree_paths) -> tuple:
    """tree_paths + hidden["reads"], each a plain repo-relative path (no absolute path, no empty, `.`, `..` or .git
    component); anything else refuses (ValueError) rather than being skipped, so a bad judge file cannot silently
    shrink the tree the vet measured."""
    if hidden is not None and not isinstance(hidden, dict):
        raise ValueError("hidden must be a dict")
    reads = (hidden or {}).get("reads") or []
    if not isinstance(reads, list):
        raise ValueError("hidden reads must be a list")
    for r in reads:
        parts = r.split("/") if isinstance(r, str) else None
        if (not parts or r.startswith("/") or r.startswith("-")
                or any(x in ("", ".", "..") or x.lower() == ".git" for x in parts)):
            raise ValueError("hidden read %r is not a plain repo-relative path" % (r,))
    return tuple(tree_paths) + tuple(r for r in reads if r not in tree_paths)


def _changed(repo: Path, base: str, fix: str) -> set:
    """Every path base..fix touches (renames split into delete + add, so both names count)."""
    import arena_judge as J
    with J.SafeRepo(Path(repo)) as g:
        raw = g.git("diff", "--no-renames", "--name-only", "-z", base, fix)
    return {x.decode("utf-8", "surrogateescape") for x in raw.split(b"\0") if x}


def fix_changed(rel: str, changed: set, area) -> bool:
    """rel is, or is a directory holding, a path the fix changed outside the area (an arm cannot reproduce it)."""
    import arena_judge as J
    return any((c == rel or c.startswith(rel + "/")) and not J.in_area(c, list(area or [])) for c in changed)


def parse_log(raw: str) -> set:
    """The recorded paths of one trace log; anything not a list of [kind, path] string pairs -> empty (no reads)."""
    try:
        data = json.loads(raw)
    except ValueError:
        return set()
    if not isinstance(data, list):
        return set()
    out = set()
    for e in data:
        if not (isinstance(e, (list, tuple)) and len(e) == 2 and all(isinstance(x, str) for x in e)):
            return set()
        out.add(e[1])
    return out


def _listing(repo: Path, sha: str):
    """(files, {dir: blob count}) at sha."""
    import arena_judge as J            # lazy: arena_judge imports this module
    with J.SafeRepo(Path(repo)) as g:
        raw = g.git("ls-tree", "-r", "-z", "--name-only", "--full-tree", sha)
    files = {x.decode("utf-8", "surrogateescape") for x in raw.split(b"\0") if x}
    dirs: dict = {}
    for f in files:
        d = os.path.dirname(f)
        while d:
            dirs[d] = dirs.get(d, 0) + 1
            d = os.path.dirname(d)
    return files, dirs


def trace_once(checks: list[dict], tree: Path, work: Path, timeout: int) -> set:
    """Run each check under TRACER in its own copy of `tree` (the judge sandbox); the union of recorded paths."""
    import arena_judge as J
    seen = set()
    for i, c in enumerate(checks):
        scratch = work / ("trace_%02d" % i)
        if scratch.exists():
            shutil.rmtree(scratch)
        shutil.copytree(tree, scratch, symlinks=True)
        try:
            target = J._write_check(scratch, c["path"], c["body"])
            J.run_sandboxed([sys.executable, "-P", "-c", TRACER, str(target), TRACE_LOG], work=work,
                            stdin=b"", timeout=timeout, cwd=scratch, rw=[scratch],
                            env={"PYTHONDONTWRITEBYTECODE": "1"}, kind="check")
            logf = scratch / TRACE_LOG
            if logf.is_file() and not logf.is_symlink():
                seen |= parse_log(logf.read_text(encoding="utf-8", errors="replace"))
        except (J.JudgeError, ValueError, OSError):
            pass
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
    return seen


def new_reads(seen, tree: Path, files: set, dirs: dict, have, changed: set = frozenset(), area=(),
              refused: set | None = None) -> tuple[set, set]:
    """(paths to add, too-wide dirs) from one trace: recorded, absent from the tree, present at the fix, and not a
    path the fix changed outside the area (those go to `refused`)."""
    add, wide = set(), set()
    for rel in seen:
        if not isinstance(rel, str) or rel in ("", ".") or rel.startswith("..") or rel in have:
            continue
        if os.path.lexists(tree / rel):
            continue
        if (rel in files or rel in dirs) and fix_changed(rel, changed, area):
            if refused is not None:
                refused.add(rel)
            continue
        if rel in files:
            add.add(rel)
        elif rel in dirs:
            (wide if dirs[rel] > READ_DIR_CAP else add).add(rel)
    return add, wide


def trace_reads(repo: Path, fix: str, area: list[str], checks: list[dict], work: Path, timeout: int,
                rounds: int = ROUNDS, base: str | None = None) -> dict:
    """`base`: the task's base sha; reads the fix changed (base..fix, outside the area) are refused, not added."""
    import arena_judge as J
    files, dirs = _listing(repo, fix)
    changed = _changed(repo, base, fix) if base else set()
    reads: set = set()
    wide: set = set()
    refused: set = set()
    n, converged = 0, False
    for n in range(1, rounds + 1):
        d = work / ("round_%d" % n)
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
        try:
            tree = J.materialise(repo, fix, area, d / "tree", J.TREE_PATHS + tuple(sorted(reads)))
            seen = trace_once(checks, tree, d, timeout)
            add, w = new_reads(seen, tree, files, dirs, reads, changed, area, refused)
        finally:
            shutil.rmtree(d, ignore_errors=True)
        wide |= w
        if not add:
            converged = True
            break
        reads |= add
    # a file under a directory read already in the set is redundant
    out = sorted(r for r in reads if not any(r.startswith(o + "/") for o in reads if o != r))
    return {"reads": out, "too_wide": sorted(wide), "refused": sorted(refused), "rounds": n, "converged": converged}
