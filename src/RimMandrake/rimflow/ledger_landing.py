"""The one home for "which repo paths did this rimflow write make, and land exactly those".

    rimflow note <ID> --text "..." --seat BENCH --why "..." --publish

`model.append` records the shard it appended to (`wrote`), and `cli.py` records the item prose a write made (a card
stamp's prose, `close`'s move to items/closed/, `reopen`'s move back). With `--publish`, `cli.main` calls `land` after
the verb: one `./publish -m "ledger: <ID> <verb>" <paths>` in the ledger's clone, naming exactly the recorded paths.

Why: a helper used to be told in prose which shard to publish ("the seat's, and OWNER.jsonl after an owner flag"). That
rule missed `./game --why` stamps, which land in OWNER.jsonl with no owner flag (1,252 events on 2026-11-22), and every
prose path. The process that wrote knows what it wrote. Boundary: design/specs/2026-11-22-ledger-write-lands-its-shard/
boundary.md.
"""
import os
import shlex
import subprocess
import sys

LANDING_FAILED = 4      # the write stands, the landing did not happen; distinct from a refused verb (1) and argparse (2)
PUBLISH_PY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Utils", "publish.py")
GIT_TIMEOUT_S = 60      # hang guard on one `git rev-parse`/`ls-files` (a local read takes well under 1 s)
PUBLISH_TIMEOUT_S = 21600  # hang guard on one ./publish: its own git calls are bounded at 300 s each, its checks run on top # budget: class=publish

# One list per process, whichever name imported this module (`rimflow.ledger_landing` from cli.py, bare `ledger_landing`
# from a tool that put rimflow/ on sys.path): two lists would make `--publish` miss the writes the other copy saw.
_written = next((m._written for m in (sys.modules.get("rimflow.ledger_landing"), sys.modules.get("ledger_landing"))
                 if m is not None and hasattr(m, "_written")), [])


def wrote(path):
    """Record one file this process wrote or moved (absolute or cwd-relative). Each path once, in write order."""
    p = os.path.abspath(path)
    if p not in _written:
        _written.append(p)


def written():
    return list(_written)


def reset():
    del _written[:]


def subject(verb, item=None):
    return "ledger: %s %s" % (item, verb) if item else "ledger: %s" % verb


def _git(top, *args, runner=subprocess.run):
    return runner(["git", "-C", top] + list(args), capture_output=True, text=True, timeout=GIT_TIMEOUT_S,
                  stdin=subprocess.DEVNULL)


def repo_paths(paths, runner=subprocess.run):
    """-> (top, [repo-relative paths]) for the recorded `paths`: sorted, each once, a missing path kept only when git
    tracks it (a move's old side; an untracked file that moved away has nothing to land). Raises ValueError naming the
    cause when the paths are not in one git clone."""
    if not paths:
        return None, []
    tops = set()
    for p in paths:
        d = os.path.dirname(p)
        while d and not os.path.isdir(d):
            d = os.path.dirname(d)
        r = _git(d or ".", "rev-parse", "--show-toplevel", runner=runner)
        if r.returncode != 0:
            raise ValueError("%s is not in a git clone (%s)" % (p, (r.stderr or "").strip()))
        tops.add(r.stdout.strip())
    if len(tops) != 1:
        raise ValueError("the written paths span %d clones (%s)" % (len(tops), ", ".join(sorted(tops))))
    top = tops.pop()
    rels = sorted({os.path.relpath(os.path.realpath(p), os.path.realpath(top)) for p in paths})
    keep = []
    for rel in rels:
        if os.path.exists(os.path.join(top, rel)):
            keep.append(rel)
            continue
        r = _git(top, "ls-files", "--error-unmatch", "--", rel, runner=runner)
        if r.returncode == 0:
            keep.append(rel)
    return top, keep


def command(rels, subj):
    """The one hand command that lands `rels` (the line a failed landing prints)."""
    return " ".join(["./publish", "-m", shlex.quote(subj)] + [shlex.quote(r) for r in rels])


def land(verb, item=None, rc=0, paths=None, runner=subprocess.run, out=None):
    """After a verb that exited `rc`: land what it wrote. -> the exit code to return (rc, or LANDING_FAILED)."""
    out = out or sys.stdout
    paths = written() if paths is None else paths
    subj = subject(verb, item)
    if not paths:
        print("nothing to publish: this command wrote no ledger or prose path", file=out)
        return rc
    try:
        top, rels = repo_paths(paths, runner=runner)
    except (ValueError, OSError, subprocess.SubprocessError) as e:
        print("WRITTEN, NOT PUBLISHED: %s; the paths: %s" % (e, " ".join(paths)), file=out)
        return rc or LANDING_FAILED
    if not rels:
        print("nothing to publish: the paths this command wrote are gone and untracked (%s)" % " ".join(paths), file=out)
        return rc
    if rc != 0:
        print("NOT PUBLISHED (the command exited %s): in %s run %s" % (rc, top, command(rels, subj)), file=out)
        return rc
    try:
        # --ledger: shards alone land past the clone's publish lock and take no peer's commit (publish.land_ledger); with
        # any other path among them, or where that cannot be done, publish.py takes its ordinary route
        r = runner([sys.executable, PUBLISH_PY, "--ledger", "-m", subj] + rels, cwd=top, capture_output=True, text=True,
                   timeout=PUBLISH_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as e:
        print("WRITTEN, NOT PUBLISHED: ./publish could not run (%s); to pass, run in %s: %s"
              % (e, top, command(rels, subj)), file=out)
        return LANDING_FAILED
    said = (r.stdout or "") + (r.stderr or "")
    line = next((ln for ln in said.splitlines() if ln.startswith("PUBLISHED ")), None)
    if r.returncode == 0 and line:
        print("%s  (%s)" % (line, " ".join(rels)), file=out)
        return 0
    tail = " | ".join(ln.strip() for ln in said.strip().splitlines()[-3:]) or "no output"
    print("WRITTEN, NOT PUBLISHED: ./publish exited %d: %s; to pass, run in %s: %s"
          % (r.returncode, tail, top, command(rels, subj)), file=out)
    return LANDING_FAILED
