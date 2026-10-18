#!/usr/bin/env python3
"""scratch_reap.py — delete stale scratch clones and agent session scratchpads, but ONLY when nothing in
them exists nowhere else. Dry run by default; --apply deletes.

Owner, 2026-10-18, by card (BUILDUP_BUILD_CLONES_STOP_BREEDING, Q2): "Reaper may delete stale scratch
clones? -> Yes, after 24h, if fully pushed". Design: design/RimMandrake/buildup_prevention_design_2026-10-18.md
Source 1. Lesson behind the ledger check: a session scratchpad held the ONLY copy of CRACKEDLANDS_FULL_RENAME_1's
three commits and a hand cleanup deleted it (2026-10-18, lessons/20261018T192736Z-…).

    scratch_reap.py                 report: DELETE / REFUSE (with reasons) / YOUNG for every candidate
    scratch_reap.py --apply         delete the DELETE rows (each re-checked immediately before rmtree)
    scratch_reap.py --json          machine-readable rows

Candidates (never anything else — loose files and other dirs are counted and left alone):
  * a git clone anywhere under /home/mandrake/rm/scratch/** or ~/.seat-tmp/** (a dir holding `.git`);
  * an agent session dir  ~/.seat-tmp/<SEAT>/claude-*/<project>/<session-uuid>/  (its scratchpad/ and tasks/).

A candidate is deleted only if EVERY rule passes; any failure REFUSES it and writes an alarm line:
  1. older than the TTL (24 h): the NEWEST mtime anywhere inside it, not the dir's own;
  2. for every clone (the candidate, or each clone inside a session dir):
       no commit reachable from any local ref (branches, tags, HEAD, stash, backup/rescue refs) that is
       missing from every remote-tracking ref; at least one remote; no remote that is a vanished local path;
       `git status --porcelain` empty (no tracked change and no untracked file; ignored files do not count);
       no stash; no rebase/merge/cherry-pick in progress; not a linked worktree (`.git` file);
  3. no other repo borrows its objects (objects/info/alternates pointing inside it);
  4. no ledger event, live or closed item, or handoff in either seat clone names its path, its session
     uuid, or (for a distinctive name) its directory name — "committed LOCALLY, not pushed" notes name these;
  5. no running process has it as cwd or names it on its command line.

Env (the selftest uses them): SCRATCH_REAP_ROOTS (os.pathsep list), SCRATCH_REAP_CORPUS (os.pathsep list of
clone roots whose infrastructure/state is grepped), SCRATCH_REAP_TTL_HOURS, SCRATCH_REAP_STATE.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HOME = Path.home()
DEFAULT_ROOTS = [Path("/home/mandrake/rm/scratch"), HOME / ".seat-tmp"]
DEFAULT_CORPUS = [Path("/home/mandrake/rm/bench"), Path("/home/mandrake/rm/foundry")]
NEVER = {Path("/home/mandrake/rm/bench"), Path("/home/mandrake/rm/foundry"), Path("/home/mandrake/rm/store.git"),
         Path("/home/mandrake/rm/mirror.git"), Path("/mnt/d/Luke/dev/RimMandrake"), HOME}
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
GENERIC = {"scratch", "scratchpad", "clone", "repo", "tmp", "temp", "work", "test", "tasks", "foundry", "bench",
           "rimmandrake", "backup", "src", "build", "out", "old", "new"}
WALK_CAP = 400_000          # entries; a tree bigger than this is not aged (REFUSE: too big to age)


def roots() -> list[Path]:
    v = os.environ.get("SCRATCH_REAP_ROOTS")
    return [Path(x) for x in v.split(os.pathsep) if x] if v else DEFAULT_ROOTS


def corpus_roots() -> list[Path]:
    v = os.environ.get("SCRATCH_REAP_CORPUS")
    return [Path(x) for x in v.split(os.pathsep) if x] if v else DEFAULT_CORPUS


def ttl_s() -> float:
    return float(os.environ.get("SCRATCH_REAP_TTL_HOURS", "24")) * 3600


def state_dir() -> Path:
    return Path(os.environ.get("SCRATCH_REAP_STATE",
                               Path(os.environ.get("XDG_STATE_HOME", HOME / ".local" / "state")) / "rm-scratch-reap"))


def git(repo: Path, *a, check=False) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True,
                          env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"))


# ---------------------------------------------------------------- discovery
def is_clone(d: Path) -> bool:
    return os.path.lexists(d / ".git")


def find_clones(top: Path, depth: int = 6) -> list[Path]:
    """Every git work tree under `top` (top itself included), not descending into a found clone."""
    out: list[Path] = []

    def walk(d: Path, k: int):
        if is_clone(d):
            out.append(d)
            return
        if k <= 0:
            return
        try:
            with os.scandir(d) as it:
                subs = [Path(e.path) for e in it if e.is_dir(follow_symlinks=False)]
        except OSError:
            return
        for s in subs:
            walk(s, k - 1)
    walk(top, depth)
    return out


def candidates() -> tuple[list[tuple[str, Path]], int]:
    """-> ([(kind, path)], count of other entries left alone)."""
    cands: list[tuple[str, Path]] = []
    seen: set[Path] = set()
    others = 0
    for r in roots():
        if not r.is_dir():
            continue
        # session dirs first: ~/.seat-tmp/<SEAT>/claude-*/<project>/<uuid>
        for s in glob.glob(str(r / "*" / "claude-*" / "*" / "*")):
            p = Path(s)
            if UUID.match(p.name) and p.is_dir() and not p.is_symlink():
                cands.append(("session", p))
                seen.add(p)
        for c in find_clones(r):
            if any(c == s or s in c.parents for s in seen):
                continue                     # judged as part of its session
            cands.append(("clone", c))
    return cands, others


# ---------------------------------------------------------------- measurements
def newest_mtime_and_size(d: Path) -> tuple[float, int, bool]:
    """(newest mtime of anything inside, total bytes, capped?) — never follows symlinks."""
    newest, size, n = 0.0, 0, 0
    stack = [str(d)]
    while stack:
        cur = stack.pop()
        try:
            st = os.lstat(cur)
            newest = max(newest, st.st_mtime)
            it = os.scandir(cur)
        except OSError:
            continue
        with it:
            for e in it:
                n += 1
                if n > WALK_CAP:
                    return newest, size, True
                try:
                    st = e.stat(follow_symlinks=False)
                except OSError:
                    continue
                newest = max(newest, st.st_mtime)
                if e.is_dir(follow_symlinks=False):
                    stack.append(e.path)
                else:
                    size += st.st_size
    return newest, size, False


def origin_mirrors() -> list[Path]:
    v = os.environ.get("SCRATCH_REAP_MIRRORS")
    if v is not None:
        return [Path(x) for x in v.split(os.pathsep) if x]
    return [Path("/home/mandrake/rm/mirror.git"), Path("/home/mandrake/rm/store.git")]


def still_unpushed(c: Path, unpushed: list[str]) -> list[str]:
    """A clone's remote-tracking refs go stale (its commits were pushed from elsewhere, or landed later):
    a local ref tip that is an ANCESTOR of origin/main in the locally kept mirror/store is on origin, and so is
    everything it reaches. Only exact commits count — a patch-equivalent replay is still refused."""
    tips = set(git(c, "for-each-ref", "--format=%(objectname)", "refs/heads", "refs/tags", "refs/stash",
                   "refs/backup", "refs/rescue").stdout.split())
    h = git(c, "rev-parse", "-q", "--verify", "HEAD").stdout.strip()
    if h:
        tips.add(h)
    uset = set(unpushed)
    left = [t for t in tips if t in uset]
    for m in origin_mirrors():
        if not left:
            break
        ref = next((r for r in ("refs/remotes/origin/main", "refs/heads/main")
                    if git(m, "rev-parse", "-q", "--verify", r).returncode == 0), None)
        if ref:
            left = [t for t in left if git(m, "merge-base", "--is-ancestor", t, ref).returncode]
    if left:
        return unpushed
    return []


def clone_problems(c: Path) -> list[str]:
    """Every reason this clone may NOT be deleted; empty means it holds nothing that is not on a remote."""
    why: list[str] = []
    dotgit = c / ".git"
    if dotgit.is_file() or dotgit.is_symlink():
        return [f"{c}: .git is a file/link (linked worktree or submodule) — its real repo is elsewhere"]
    if git(c, "rev-parse", "--git-dir").returncode:
        return [f"{c}: git cannot read it (corrupt or not a repo) — inspect by hand"]
    gd = dotgit
    for m in ("rebase-merge", "rebase-apply", "MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "BISECT_LOG"):
        if (gd / m).exists():
            why.append(f"{c}: a {m} is in progress")
    remotes = [x for x in git(c, "remote").stdout.split() if x]
    if not remotes:
        why.append(f"{c}: no remote at all — every commit here exists only here")
    for rm in remotes:
        url = git(c, "remote", "get-url", rm).stdout.strip()
        local = url[7:] if url.startswith("file://") else url
        if local.startswith("/") and not os.path.exists(local):
            why.append(f"{c}: remote '{rm}' is a local path that no longer exists ({local})")
    if git(c, "rev-parse", "-q", "--verify", "refs/stash").returncode == 0:
        n = len(git(c, "stash", "list").stdout.splitlines())
        why.append(f"{c}: {n} stash entr{'y' if n == 1 else 'ies'}")
    r = git(c, "rev-list", "--all", "HEAD", "--not", "--remotes")
    if r.returncode:
        r = git(c, "rev-list", "--all", "--not", "--remotes")      # unborn HEAD
    unpushed = [x for x in r.stdout.split() if x]
    if unpushed and not r.returncode:
        unpushed = still_unpushed(c, unpushed)
    if r.returncode:
        why.append(f"{c}: cannot list commits ({r.stderr.strip()[:120]})")
    elif unpushed:
        why.append(f"{c}: {len(unpushed)} commit(s) on no remote (e.g. {unpushed[0][:10]})")
    st = git(c, "status", "--porcelain=v1", "-z", "--untracked-files=normal")
    if st.returncode:
        why.append(f"{c}: git status failed ({st.stderr.strip()[:120]})")
    else:
        recs = [x for x in st.stdout.split("\0") if x]
        untracked = sum(1 for x in recs if x.startswith("??"))
        tracked = len(recs) - untracked
        if tracked:
            why.append(f"{c}: {tracked} tracked file(s) changed")
        if untracked:
            why.append(f"{c}: {untracked} untracked file(s)")
    return why


def all_repos_for_alternates() -> list[Path]:
    repos = list(DEFAULT_CORPUS) + [Path("/home/mandrake/rm/store.git"), Path("/home/mandrake/rm/mirror.git")]
    for r in roots():
        if r.is_dir():
            repos += find_clones(r)
    return repos


def borrowers_of(target: Path, repos: list[Path]) -> list[str]:
    out = []
    t = str(target.resolve()) + os.sep
    for r in repos:
        if r == target or target in r.parents:
            continue
        for alt in (r / ".git" / "objects" / "info" / "alternates", r / "objects" / "info" / "alternates"):
            try:
                lines = alt.read_text().splitlines()
            except OSError:
                continue
            for ln in lines:
                p = ln.strip()
                if p and not os.path.isabs(p):
                    p = os.path.normpath(os.path.join(alt.parent.parent, p))
                if p and (os.path.realpath(p) + os.sep).startswith(t):
                    out.append(f"{r} borrows objects from it ({alt})")
    return out


_CORPUS: list[tuple[str, str]] | None = None


def corpus() -> list[tuple[str, str]]:
    """[(file, text)] of every ledger file, item (live + closed) and handoff in each seat clone."""
    global _CORPUS
    if _CORPUS is None:
        _CORPUS = []
        for cr in corpus_roots():
            st = cr / "infrastructure" / "state"
            pats = [st / "ledger" / "events.jsonl", st / "ledger" / "events" / "*.jsonl", st / "items" / "*.md",
                    st / "items" / "closed" / "*.md", st / "handoffs" / "*.md"]
            for pat in pats:
                for f in glob.glob(str(pat)):
                    try:
                        _CORPUS.append((f, open(f, encoding="utf-8", errors="replace").read()))
                    except OSError:
                        pass
    return _CORPUS


def needles(p: Path, kind: str) -> list[str]:
    n = {str(p), str(p).replace(str(HOME), "~", 1)}
    if kind == "session":
        n.add(p.name)                                   # the session uuid
    elif len(p.name) >= 6 and p.name.lower() not in GENERIC:
        n.add(p.name)
    return sorted(n)


def ledger_mentions(p: Path, kind: str) -> list[str]:
    hits = []
    for nd in needles(p, kind):
        rx = re.compile(r"(?<![A-Za-z0-9_.-])" + re.escape(nd) + r"(?![A-Za-z0-9_-])")
        for f, text in corpus():
            m = rx.search(text)
            if m:
                line = text[text.rfind("\n", 0, m.start()) + 1: text.find("\n", m.end())][:160]
                hits.append(f"{os.path.basename(f)} names '{nd}': …{line.strip()}…")
                break
    return hits


def live_users(p: Path) -> list[str]:
    out = []
    t = str(p)
    for pid in os.listdir("/proc"):
        if not pid.isdigit() or int(pid) == os.getpid():
            continue
        try:
            cwd = os.readlink(f"/proc/{pid}/cwd")
            if cwd == t or cwd.startswith(t + os.sep):
                out.append(f"pid {pid} has cwd inside it")
                continue
            cmd = open(f"/proc/{pid}/cmdline", "rb").read().replace(b"\0", b" ").decode("utf-8", "replace")
            if t in cmd or (UUID.match(p.name) and p.name in cmd):
                out.append(f"pid {pid} names it: {cmd[:100]}")
        except OSError:
            continue
    return out


# ---------------------------------------------------------------- verdicts
def judge(kind: str, p: Path, repos: list[Path], now: float) -> dict:
    row = {"kind": kind, "path": str(p), "verdict": "DELETE", "why": [], "age_h": None, "bytes": None}
    rp = p.resolve()
    if p.is_symlink() or rp in NEVER or not any(rp == r.resolve() or r.resolve() in rp.parents for r in roots()) \
            or any(rp == r.resolve() for r in roots()):
        row.update(verdict="REFUSE", why=["outside the reap roots, a root itself, a symlink, or a protected repo"])
        return row
    newest, size, capped = newest_mtime_and_size(p)
    row["age_h"], row["bytes"] = round((now - newest) / 3600, 1), size
    if capped:
        row.update(verdict="REFUSE", why=[f"more than {WALK_CAP} entries — too big to age safely; inspect by hand"])
        return row
    if now - newest < ttl_s():
        row["verdict"] = "YOUNG"
        return row
    why = []
    clones = [p] if kind == "clone" else find_clones(p, depth=8)
    for c in clones:
        why += clone_problems(c)
        why += borrowers_of(c, repos)
    why += ledger_mentions(p, kind)
    for c in clones:
        if c != p:
            why += ledger_mentions(c, "clone")
    why += live_users(p)
    if why:
        row.update(verdict="REFUSE", why=why)
    row["clones"] = [str(c) for c in clones]
    return row


def human(n: int | None) -> str:
    if n is None:
        return "?"
    for u in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or u == "TB":
            return f"{n:.1f} {u}" if u != "B" else f"{n} B"
        n /= 1024
    return "?"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true", help="delete the DELETE rows (default: report only)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    now = time.time()
    cands, _ = candidates()
    repos = all_repos_for_alternates()
    rows = [judge(k, p, repos, now) for k, p in cands]
    sd = state_dir()
    sd.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
    deleted = 0
    for r in rows:
        if r["verdict"] != "DELETE" or not a.apply:
            continue
        again = judge(r["kind"], Path(r["path"]), all_repos_for_alternates(), time.time())   # TOCTOU re-check
        if again["verdict"] != "DELETE":
            r.update(verdict="REFUSE", why=["changed since the scan: "] + again["why"])
            continue
        shutil.rmtree(r["path"])
        r["verdict"] = "DELETED"
        deleted += 1
    with open(sd / "runs.jsonl", "a") as f:
        f.write(json.dumps({"ts": stamp, "apply": a.apply, "rows": rows}) + "\n")
    refused = [r for r in rows if r["verdict"] == "REFUSE"]
    if refused:
        with open(sd / "alarms.log", "a") as f:
            for r in refused:
                f.write(f"{stamp} REFUSE {r['path']} ({human(r['bytes'])}, {r['age_h']} h): {r['why'][0]}"
                        + (f" (+{len(r['why']) - 1} more)" if len(r["why"]) > 1 else "") + "\n")
    if a.json:
        print(json.dumps(rows, indent=1))
        return 0
    order = {"DELETED": 0, "DELETE": 1, "REFUSE": 2, "YOUNG": 3}
    for r in sorted(rows, key=lambda r: (order[r["verdict"]], r["path"])):
        print(f"{r['verdict']:7} {r['kind']:7} {human(r['bytes']):>9} {str(r['age_h']):>7}h  {r['path']}")
        for w in r["why"][:4]:
            print(f"          - {w}")
        if len(r["why"]) > 4:
            print(f"          - … {len(r['why']) - 4} more")
    tot = {v: sum(1 for r in rows if r["verdict"] == v) for v in order}
    take = sum(r["bytes"] or 0 for r in rows if r["verdict"] in ("DELETE", "DELETED"))
    print(f"\n{len(rows)} candidate(s): " + ", ".join(f"{v} {n}" for v, n in tot.items() if n)
          + f"; {'freed' if a.apply else 'would free'} {human(take)}"
          + ("" if a.apply else "  (dry run — --apply deletes the DELETE rows)"))
    print(f"alarms: {sd / 'alarms.log'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
