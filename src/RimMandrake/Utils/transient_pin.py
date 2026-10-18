#!/usr/bin/env python3
"""transient_pin.py — Transient/ is UNTRACKED; this manages the few paths pinned to stay in git.

Owner, 2026-10-18, by card (BUILDUP_BUILD_CLONES_STOP_BREEDING, Q1): "Stop tracking; pin to keep".
Design: design/RimMandrake/buildup_prevention_design_2026-10-18.md (Source 5, owner answers).

The pin list IS `Transient/.gitignore`: it ignores everything (`*`), re-includes directories (`!*/`, so
a pin deep in a tree can work), keeps every `*.decisions.json` (owner picks are never lost), and holds one
`!/<path>` or `!/<dir>/**` line per pin between the PINS markers. One file, one source of truth, read by
git itself — no second list to drift.

    transient_pin.py list                     the pins
    transient_pin.py add <path>...            pin (path relative to the repo or to Transient/); then
                                              ./publish -m "pin ..." Transient/.gitignore <path>...
    transient_pin.py rm <path>... [--apply]   unpin; --apply also lands the untrack commit (files stay on disk)
    transient_pin.py cited [--add]            Transient paths cited by LIVE items or ledger evidence that
                                              exist here and are not pinned; --add pins them
    transient_pin.py untrack [--apply]        tracked Transient files the rules now ignore; --apply lands one
                                              commit removing them from the index (never from disk)
    transient_pin.py status                   counts: tracked, ignored-but-tracked, pins

Files stay on disk in every clone: seat_sync.reset_keep (./sync, ./publish, land.sh) keeps a file upstream
stopped tracking. No history rewrite — every old Transient file is still in git history
(`git log --all -- <path>`; `git show <sha>:<path>` restores one).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TDIR = "Transient"
BEGIN = "# --- PINS (managed by transient_pin.py; edit with it, one pin per line) ---"
END = "# --- END PINS ---"
HEADER = """\
# Transient/ is UNTRACKED since 2026-10-18 (owner, by card: "Stop tracking; pin to keep";
# BUILDUP_BUILD_CLONES_STOP_BREEDING). Everything here is ignored except this file, every
# *.decisions.json (owner picks are never lost), and the PINS below.
# A file lives only in the clone that wrote it unless pinned. Manage pins with:
#     python3 src/RimMandrake/Utils/transient_pin.py list|add|rm|cited|untrack|status
*
!*/
!/.gitignore
!*.decisions.json
.gatecheck_*/
"""


def root() -> str:
    return os.environ.get("TRANSIENT_PIN_ROOT", ROOT)


def gi_path() -> str:
    return os.path.join(root(), TDIR, ".gitignore")


def git(*a, inp=None, env=None, check=True) -> str:
    r = subprocess.run(["git", "-C", root(), *a], capture_output=True, text=True, input=inp,
                       env=dict(os.environ, **(env or {})))
    if check and r.returncode:
        sys.exit("REFUSED: git %s failed: %s" % (" ".join(a[:3]), (r.stderr or r.stdout).strip()[-400:]))
    return r.stdout


def read_gi() -> tuple[str, list[str], str]:
    """-> (text before the pin block, pin lines, text after)."""
    try:
        text = open(gi_path(), encoding="utf-8").read()
    except OSError:
        text = HEADER
    if BEGIN not in text:
        return text.rstrip("\n") + "\n", [], ""
    pre, rest = text.split(BEGIN, 1)
    body, _, post = rest.partition(END)
    return pre, [ln for ln in body.splitlines() if ln.strip()], post.lstrip("\n")


def write_gi(pre: str, pins: list[str], post: str) -> None:
    os.makedirs(os.path.dirname(gi_path()), exist_ok=True)
    with open(gi_path(), "w", encoding="utf-8") as f:
        f.write(pre.rstrip("\n") + "\n" + BEGIN + "\n")
        for p in sorted(set(pins)):
            f.write(p + "\n")
        f.write(END + "\n" + post)


def rel_t(path: str) -> str:
    """A path given relative to the repo, to Transient/, or absolute -> relative to Transient/."""
    p = path
    if os.path.isabs(p):
        p = os.path.relpath(p, root())
    p = p.replace("\\", "/").strip("/")
    if p.startswith(TDIR + "/"):
        p = p[len(TDIR) + 1:]
    if not p or p.startswith("..") or p == TDIR:
        sys.exit("REFUSED: %r is not a path inside Transient/" % path)
    return p


def esc(p: str) -> str:
    p = re.sub(r"([\\*?\[\]])", r"\\\1", p)
    return re.sub(r" $", r"\\ ", p)


def pin_line(rel: str) -> str:
    full = os.path.join(root(), TDIR, rel)
    return "!/%s/**" % esc(rel) if os.path.isdir(full) else "!/%s" % esc(rel)


def cmd_list(_a) -> int:
    _, pins, _ = read_gi()
    for p in pins:
        print(p)
    print("%d pin(s) in %s" % (len(pins), os.path.relpath(gi_path(), root())))
    return 0


def add_pins(paths: list[str]) -> list[str]:
    pre, pins, post = read_gi()
    if not pins and "!*.decisions.json" not in pre:
        pre = HEADER
    added = []
    for path in paths:
        rel = rel_t(path)
        if not os.path.lexists(os.path.join(root(), TDIR, rel)):
            print("skip (not on disk): %s/%s" % (TDIR, rel))
            continue
        ln = pin_line(rel)
        if ln not in pins:
            pins.append(ln)
            added.append("%s/%s" % (TDIR, rel))
    write_gi(pre, pins, post)
    return added


def cmd_add(a) -> int:
    added = add_pins(a.paths)
    print("pinned %d: %s" % (len(added), " ".join(added) or "(nothing new)"))
    if added:
        print("publish:  ./publish -m \"Transient: pin %d path(s)\" %s/.gitignore %s"
              % (len(added), TDIR, " ".join(added)))
    return 0


def tracked_ignored() -> list[str]:
    out = git("ls-files", "-z", "-c", "-i", "--exclude-standard", "--", TDIR)
    return [p for p in out.split("\0") if p]


def land_untrack(paths: list[str], msg: str) -> int:
    """One commit on top of origin/main: drop `paths` from the tree, carry the worktree's ignore files.
    Built in a TEMP index (the clone's index and peers' staged work are never touched), landed by land.sh."""
    git("fetch", "-q", "origin", "main")
    up = git("rev-parse", "refs/remotes/origin/main").strip()
    with tempfile.TemporaryDirectory() as td:
        env = {"GIT_INDEX_FILE": os.path.join(td, "index")}
        git("read-tree", up, env=env)
        git("rm", "-q", "-r", "--cached", "--ignore-unmatch", "--pathspec-from-file=-", "--pathspec-file-nul",
            inp="\0".join(paths) + "\0", env=env)
        for gi in (".gitignore", "%s/.gitignore" % TDIR):
            blob = git("hash-object", "-w", "--", gi).strip()
            git("update-index", "--add", "--cacheinfo", "100644,%s,%s" % (blob, gi), env=env)
        tree = git("write-tree", env=env).strip()
    if tree == git("rev-parse", up + "^{tree}").strip():
        print("NOTHING TO LAND: origin/main already has this tree")
        return 0
    c = git("commit-tree", tree, "-p", up, "-F", "-", inp=msg + "\n").strip()
    land = os.path.join(root(), "src", "RimMandrake", "Utils", "land.sh")
    r = subprocess.run([land, c, TDIR, ".gitignore"], cwd=root(), capture_output=True, text=True)
    sys.stderr.write(r.stderr[-1500:])
    print(r.stdout.strip() or "land.sh exited %d" % r.returncode)
    return r.returncode


TRAILER = ("\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>\n"
           "Claude-Session: https://claude.ai/code/session_01QobXckUXJ6LnxbpPwWBirk")


def cmd_untrack(a) -> int:
    paths = tracked_ignored()
    tops = {}
    for p in paths:
        k = p.split("/")[1] if p.count("/") > 1 else "(top-level files)"
        tops[k] = tops.get(k, 0) + 1
    for k, n in sorted(tops.items(), key=lambda kv: -kv[1])[:15]:
        print("  %6d  %s/%s" % (n, TDIR, k))
    print("%d tracked Transient file(s) the rules ignore" % len(paths))
    if not paths or not a.apply:
        if paths:
            print("dry run. --apply lands ONE commit removing them from the index; every clone keeps the files")
        return 0
    return land_untrack(paths, a.message or ("Transient: stop tracking %d unpinned files (owner card 2026-10-18)"
                                              % len(paths)) + TRAILER)


def cmd_rm(a) -> int:
    pre, pins, post = read_gi()
    drop = set()
    for path in a.paths:
        rel = rel_t(path)
        drop |= {"!/%s/**" % esc(rel), "!/%s" % esc(rel)}
    left = [p for p in pins if p not in drop]
    print("unpinned %d" % (len(pins) - len(left)))
    write_gi(pre, left, post)
    if a.apply:
        return cmd_untrack(argparse.Namespace(apply=True, message="Transient: unpin %s" % " ".join(a.paths) + TRAILER))
    print("then: transient_pin.py untrack --apply   (files stay on disk)")
    return 0


WHOLE_DIR_SKIP = {"biome_ffar", "biome_ffar/img"}   # the sheet image cache: 10k+ regenerable files
CITE = re.compile(r"Transient/[A-Za-z0-9_.@+/-]*[A-Za-z0-9_@+-]")


def cited() -> list[str]:
    """Transient paths a LIVE item (items/*.md) or any ledger `evidence` field names, present here."""
    st = os.path.join(root(), "infrastructure", "state")
    found = set()
    for p in glob.glob(os.path.join(st, "items", "*.md")):
        found |= set(CITE.findall(open(p, encoding="utf-8", errors="replace").read()))
    for p in [os.path.join(st, "ledger", "events.jsonl")] + glob.glob(os.path.join(st, "ledger", "events", "*.jsonl")):
        try:
            fh = open(p, encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in fh:
            if '"evidence"' not in line:
                continue
            try:
                ev = json.loads(line).get("evidence")
            except ValueError:
                continue
            if isinstance(ev, str):
                found |= set(CITE.findall(ev))
    out = []
    for c in sorted(found):
        rel = c[len(TDIR) + 1:]
        if not rel or rel in WHOLE_DIR_SKIP:
            continue                     # citing a whole cache dir is not a pin request; its files are
        if os.path.lexists(os.path.join(root(), c)):
            out.append(c)
    return out


def is_ignored(path: str) -> bool:
    return subprocess.run(["git", "-C", root(), "check-ignore", "-q", "--no-index", "--", path]).returncode == 0


def cmd_cited(a) -> int:
    pins = read_gi()[1]
    todo = [c for c in cited()
            if ((pin_line(rel_t(c)) not in pins) if os.path.isdir(os.path.join(root(), c)) else is_ignored(c))]
    for c in todo:
        print("  unpinned: %s" % c)
    print("%d cited Transient path(s) not pinned" % len(todo))
    if a.add and todo:
        added = add_pins(todo)
        print("pinned %d; publish Transient/.gitignore plus them" % len(added))
    return 0


def cmd_status(_a) -> int:
    n = len([p for p in git("ls-files", "-z", "--", TDIR).split("\0") if p])
    print("tracked under Transient/: %d; tracked-but-ignored: %d; pins: %d"
          % (n, len(tracked_ignored()), len(read_gi()[1])))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    sub.add_parser("status")
    p = sub.add_parser("add"); p.add_argument("paths", nargs="+")
    p = sub.add_parser("rm"); p.add_argument("paths", nargs="+"); p.add_argument("--apply", action="store_true")
    p = sub.add_parser("cited"); p.add_argument("--add", action="store_true")
    p = sub.add_parser("untrack"); p.add_argument("--apply", action="store_true"); p.add_argument("-m", "--message")
    a = ap.parse_args(argv)
    return {"list": cmd_list, "status": cmd_status, "add": cmd_add, "rm": cmd_rm,
            "cited": cmd_cited, "untrack": cmd_untrack}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
