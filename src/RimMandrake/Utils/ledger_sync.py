#!/usr/bin/env python3
"""ledger_sync.py — rescue ledger events stranded in a seat clone onto origin/main.

Why: `rimflow` appends events to `infrastructure/state/ledger/events/<SEAT>.jsonl` in the
seat clone (`/home/mandrake/rm/<seat>`). When that clone falls far behind origin with
other uncommitted work, it cannot publish them: `git pull --rebase` refuses on the dirty
tree, the pre-push `ledger_lint` refuses NOT_APPEND, and resetting/stashing the seat clone
is forbidden. The events then sit there unpublished, invisible to every other window.

What it does (the seat clone is only READ — never reset, stashed, checked out or written):
  1. reads the seat clone's WORKTREE shard (covers unpushed commits and uncommitted lines);
  2. in a FRESH clone (``--clone PATH``, created from origin if absent, else a temp dir —
     never the seat clone) fetches origin and checks out origin/main;
  3. finds the local lines whose event (canonical JSON, i.e. full-line identity after
     key-sorting) is absent from origin/main's shard. Lines already on origin are skipped,
     so a re-run is a no-op (idempotent). A line sharing ledger_lint's identity
     (seat, event, subject, ts) with an origin line but different content is an edit in
     place, not a stranded event: it is reported as CONFLICT and never appended;
  4. appends only the missing lines, in local file order, to the END of the origin shard
     (append-only, the same shape `merge=union` produces), runs ledger_lint.py against
     origin/main, commits that one path, `pull --rebase`, `push origin HEAD:main`.

Dry run by default (steps 1-3, prints the count and the lines' verbs). `--apply` does 4.

    python3 src/RimMandrake/Utils/ledger_sync.py --seat FOUNDRY --clone <scratch dir>
    python3 src/RimMandrake/Utils/ledger_sync.py --seat FOUNDRY --clone <scratch dir> --apply

Selftest: `selftest_ledger_sync.py` (temp git repos, no network).
"""
import argparse
import collections
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SHARD_DIR = "infrastructure/state/ledger/events"
LINT = os.path.join(HERE, "ledger_lint.py")
SEAT_CLONES = {"FOUNDRY": "/home/mandrake/rm/foundry", "BENCH": "/home/mandrake/rm/bench"}


def git(root, *args, check=True):
    r = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError("git %s failed in %s: %s" % (" ".join(args), root,
                                                        (r.stderr or r.stdout).strip()))
    return r


def canon(line):
    """-> canonical JSON of one event line, or None if it is not a JSON object."""
    try:
        ev = json.loads(line)
    except ValueError:
        return None
    if not isinstance(ev, dict):
        return None
    return json.dumps(ev, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def identity(ev):
    subj = ev.get("id") or ev.get("name") or ev.get("system") or ev.get("path") or ""
    return (ev.get("seat"), ev.get("event"), subj, ev.get("ts"))


def split_lines(text):
    return [l for l in text.split("\n") if l.strip()]


def missing_lines(local_text, origin_text):
    """-> (missing, conflicts, malformed): local lines absent from origin, in local order.

    Pure; the selftest drives it. Duplicates within the local shard collapse to one."""
    origin_canon = set()
    origin_idents = collections.defaultdict(set)
    for l in split_lines(origin_text):
        c = canon(l)
        if c is None:
            continue
        origin_canon.add(c)
        origin_idents[identity(json.loads(c))].add(c)
    missing, conflicts, malformed, seen = [], [], [], set()
    for l in split_lines(local_text):
        c = canon(l)
        if c is None:
            malformed.append(l)
            continue
        if c in origin_canon or c in seen:
            continue
        seen.add(c)
        if origin_idents.get(identity(json.loads(c))):
            conflicts.append(l)
            continue
        missing.append(l)
    return missing, conflicts, malformed


def prepare_clone(path, origin_url, reference=None):
    """Fresh clone at `path` (created if absent), fetched and on origin/main."""
    if not os.path.isdir(os.path.join(path, ".git")):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        cmd = ["git", "clone", "-q"]
        if reference:
            cmd += ["--reference", reference, "--dissociate"]
        r = subprocess.run(cmd + [origin_url, path], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError("clone failed: %s" % r.stderr.strip())
    if git(path, "status", "--porcelain", "--untracked-files=no").stdout.strip():
        raise RuntimeError("fresh clone %s has local changes; refusing to touch it" % path)
    git(path, "fetch", "-q", "origin")
    git(path, "checkout", "-q", "-B", "main", "origin/main")
    git(path, "config", "core.hooksPath", "infrastructure/githooks")
    return path


def run(seat, seat_clone, clone, apply=False, lint=LINT, out=print):
    rel = "%s/%s.jsonl" % (SHARD_DIR, seat)
    if os.path.realpath(clone) == os.path.realpath(seat_clone):
        raise RuntimeError("--clone must not be the seat clone")
    with open(os.path.join(seat_clone, rel), encoding="utf-8") as fh:
        local_text = fh.read()
    origin_url = git(seat_clone, "remote", "get-url", "origin").stdout.strip()
    prepare_clone(clone, origin_url, reference=seat_clone)
    shard = os.path.join(clone, rel)
    origin_text = open(shard, encoding="utf-8").read() if os.path.exists(shard) else ""
    missing, conflicts, malformed = missing_lines(local_text, origin_text)
    verbs = collections.Counter(json.loads(l).get("event") for l in missing)
    out("ledger_sync %s: %d line(s) missing from origin/main%s"
        % (seat, len(missing), (" (" + ", ".join("%s %d" % kv for kv in sorted(verbs.items()))
                                + ")") if missing else ""))
    for l in conflicts:
        out("CONFLICT (same identity, different content; not appended): %s" % l[:160])
    for l in malformed:
        out("MALFORMED (not appended): %s" % l[:160])
    if not missing or not apply:
        if missing:
            out("dry run — pass --apply to append, commit and push")
        return {"missing": len(missing), "conflicts": len(conflicts), "pushed": None}
    with open(shard, "a", encoding="utf-8") as fh:
        if origin_text and not origin_text.endswith("\n"):
            fh.write("\n")
        fh.write("\n".join(missing) + "\n")
    r = subprocess.run([sys.executable, lint, "--root", clone, "--base", "origin/main"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("ledger_lint refused:\n%s" % (r.stdout + r.stderr).strip())
    msg = ("Ledger: rescue %d stranded %s event(s) from the seat clone\n\n"
           "Appended by ledger_sync.py; lines were absent from origin/main's shard."
           % (len(missing), seat))
    git(clone, "commit", "-q", "-m", msg, "--", rel)
    git(clone, "pull", "-q", "--rebase", "origin", "main")
    git(clone, "push", "-q", "origin", "HEAD:main")
    sha = git(clone, "rev-parse", "HEAD").stdout.strip()
    out("PUSHED %s (%d event(s))" % (sha, len(missing)))
    return {"missing": len(missing), "conflicts": len(conflicts), "pushed": sha}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seat", default="FOUNDRY")
    ap.add_argument("--seat-clone", default=None, help="default: /home/mandrake/rm/<seat>")
    ap.add_argument("--clone", default=None, help="fresh clone path (default: a temp dir)")
    ap.add_argument("--apply", action="store_true", help="append, commit and push")
    a = ap.parse_args(argv)
    seat_clone = a.seat_clone or SEAT_CLONES.get(a.seat.upper())
    if not seat_clone:
        ap.error("no default seat clone for %s; pass --seat-clone" % a.seat)
    clone = a.clone or os.path.join(tempfile.mkdtemp(prefix="ledger_sync_"), "repo")
    try:
        run(a.seat.upper(), seat_clone, clone, apply=a.apply)
    except RuntimeError as e:
        print("ledger_sync: %s" % e)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
