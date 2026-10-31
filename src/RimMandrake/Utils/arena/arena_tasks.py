#!/usr/bin/env python3
r"""arena_tasks.py — Harness step 1: the replay task census and its freeze.

Design: design/RimMandrake/architecture_switch_harness_2026-10-29.md §1.1 (task specs, frozen before assignment) and
§3.2 (picking the tasks); build ticket ARENA_TASKS_BUILD_FROZEN_BEFORE_ASSIGNED (testpilot_merged_2026-10-29.md §6.5).

    python3 src/RimMandrake/Utils/arena/arena_tasks.py census [--sanity ID] [--dry-run]
    python3 src/RimMandrake/Utils/arena/arena_tasks.py freeze
    python3 src/RimMandrake/Utils/arena/arena_tasks.py check [--task T ...]

WHERE THINGS LIVE (all outside git, so no arm can edit them; §1):
  <arena>/tasks/<TASK>.json         arm-readable task spec: no hidden check, no label, no fix sha
  <arena>/judge/hidden/<TASK>.json  judge-only: label, fix sha, hidden checks (stored test bodies, rework text)
  <arena>/events/harness.jsonl      the freeze events (§1.7 schema); harness code writes it, never an agent
  <arena>/census/census_<ts>.json   the census report: pool, rejects by reason, sanity probe
`<arena>` = `$ARENA_ROOT`, else `<rmpaths data root>/arena` (rmpaths reads Lodestar's agent_storage.py,
`python3 ~/dev/Lodestar/bin/lib/agent_storage.py rimmandrake`; never hard-wired).

CENSUS (§3.2). Reads the ledger only through rimflow's `model.read()` / `model.replay()` (key `id`, never `item`:
instrument_traps.md). An item is kept when ALL hold:
  - its final state is `done` and its LAST close event falls in WINDOW (UTC dates, inclusive);
  - the close sha resolves to a commit with exactly one parent (base_sha = that parent), and the diff
    (bookkeeping stripped: ledger, queue projections, item prose) touches 1-8 files;
  - its `needs` is `offline` and its files hold code the gate judges offline (Python, XML defs/patches, C#);
  - an objective proof exists: the diff adds or changes a selftest, a Defs/Patches XML, or C#;
  - CONDUCTOR DECISION 2026-10-30 (owner authority): the proof goes beyond "the build succeeds": the fix adds or
    changes at least one selftest. A C#-only (winbuild) or XML-only (validate_patch) fix is build-only: excluded.
BENCH POOL RULING (note 2026-10-30T01:59:10Z): no start event is required, and the label is OPTIONAL metadata. An
item is ESCAPED when a caused_by DESCENDANT (children, and their children: a review's findings are grandchildren),
filed no later than 7 days after the close, is a closed code fix whose commit descends from the parent's fix and
changes at least one of the parent's files (a "remaining half" split that fixes other files is not an escape); CLEAN
with a `verify` pass in the final close cycle and no such rework; otherwise unlabelled (label null), still in
the pool. Escaped-defect analysis uses the labelled subset only. A child filed seconds BEFORE the close counts
like one filed after it.
The census reports its pool with a SANITY PROBE: a hand-picked item that must be found. A missing sanity item is a
blind instrument, not a small pool: the census exits 2 and writes nothing.

PINNING. The census resolves pre-rewrite commits through an ordered LIST of old-history git dirs (old_history_repos:
`$ARENA_OLD_HISTORY`, os.pathsep-separated globs, else the mirror then retired-trees/*-git-*). They are unreachable
there, so a gc would blind the next census. `census` (not --dry-run) and `pin` point refs/arena/old/<sha> at each
of them in the repo that resolved it (update-ref only: never pushed, never forced; mirror.py's `fetch --prune`
touches refs/remotes/origin only).

FREEZE (§1.1). Writes one `freeze` event per task (sha256 of the task file and of its judge file) plus one batch
event whose `pool_sha256` seeds the stratified draw, BEFORE any `assign` event exists; with an assign-like record
anywhere under events/ (any file name, any nesting, event/type/kind/action containing "assign" in any case) it
refuses, and an events/ entry it cannot read as a top-level *.jsonl is itself a refusal. A symlinked task or judge
file is refused. The task bytes are read once, scanned, and re-read after the leak scan: a file swapped meanwhile
is refused, not frozen. Re-freezing an unchanged task is a no-op; a changed one is refused. The one way to replace
a frozen task (before any assign) is `refreeze TASK --reason TEXT`, which APPENDS a `refreeze` record naming the
hash it replaces and the reason; restore the task file first with `census --replace TASK`. `check` (and
`load_frozen()`, which the judge and gate call) refuses any task whose file hash differs from its freeze, any task
not frozen, any `live` outside {none, minimal, minimal+deps} (the trial has no `full` tier, owner 2026-10-29),
and any hidden check that reached an arm-readable path.

ARM CLONES: A WHITELIST, NOT A BLACKLIST. build_arm_clone makes a fresh depth-1 clone at base_sha (`git init
--template=`: no hooks; no remote, tags, FETCH_HEAD, alternates or extra refs) holding exactly the files of
`git ls-tree -r base_sha` plus any harness-written files it is handed, verifies that its object store is exactly
`rev-list --objects -n1 base_sha` of the source, and records a manifest of EVERY path in the clone (.git included:
sha256, mode, symlink target) in the judge dir (judge/clones.jsonl + judge/clones/<nonce>.json). Nothing about the
clone is trusted from inside it. `check` re-proves each clone against its manifest:
  - before its task is assigned: the path set and every hash must be EQUAL. Any extra, missing or changed file,
    directory, ref, tag, object or commit message is a leak, whatever its encoding (gzip, rot13, a filename...);
  - after assignment (the arm works there): .git may not borrow (alternates, a gitfile), may not hold a commit of the
    source repo other than base_sha, and no nested repository or object store may exist anywhere in the clone;
    every changed or new file, and every commit, tag and blob object outside the manifest, is token-scanned for the
    OTHER tasks' hidden checks (the arm's own work naming its own test is not a leak).
Every finding has a SCOPE: the task whose hidden check it exposes (a deviation of a not-yet-assigned clone is
scoped to that clone's task), or `*` (an unregistered path under the clone root, a nested or borrowed repository,
source history, a judge link). load_frozen(T) refuses only on scope T or `*`; freeze withholds a task with a
scoped leak and freezes the rest. The token scan (sha prefixes, ids, test paths, test-text anchors) stays as the
secondary check on the task specs and the event log.

PROMPT PROVENANCE. Every task carries `prompt_source: "base_parent"`: the prose in the prompt and criteria is the
item file at base_sha (the parent of the closing sha), per the Conductor's 2026-10-30 01:59Z pool ruling. The
claim-time prose (the item file at the commit nearest before the item's start event, `git log -1 --before=<ts>`,
when a start event exists) is derivable but intentionally NOT used. When the prose at base_sha holds a non-blank
line the claim-time prose lacks (text added after the claim, a possible hint), the task is flagged
`prompt_may_hold_hints: true`; that is metadata only and changes no behaviour.

RESIDUAL (same OS user). Everything above is tamper-EVIDENT, not tamper-PROOF against an arm that runs as the same
OS user as the judge: such an arm can open the judge directory and rewrite the hashes and the log together. Only a
different OS user, or a sandbox that does not mount the judge directory, closes it. This module does not claim to.

Replay tasks are `live: none`: the build half runs in throwaway clones with no game (§3.1).
Every task carries `live_plan` (the TestPilot plan, L3), hashed with the rest of the file: null for `live: none`
(the census writes null for every replay task); a live task must carry a plan testpilot.check_live_plan accepts, or
validate_task/freeze/load_frozen refuse it. A file frozen before the field existed loads only if it is `live: none`.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import bz2
import io
import lzma
import zipfile
import zlib
import contextlib
import datetime as dt
import difflib
import fcntl
import fnmatch
import glob
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
UTILS = HERE.parent
sys.path.insert(0, str(UTILS.parent))       # src/RimMandrake -> `rimflow`
sys.path.insert(0, str(UTILS))              # rmpaths
from rimflow import model  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
import arena_safe_git as SG  # noqa: E402  (git on an arm-written .git)
import arena_vet_reads as VR  # noqa: E402  (the paths a hidden check reads outside the tree)

REPO = UTILS.parent.parent.parent

WINDOW = ("2026-10-12", "2026-10-27")
ESCAPE_DAYS = 7
# ARENA_CENSUS_FIXSHA_WRONG_COMMIT: words of an item id/title that say nothing about which change this is
RELATED_STOP = frozenset("this that with from into when then have does each only must fix fixes fixed item rework "
                         "build wire harden prove".split())
# the subject of a later commit that repaired code, whether or not anyone filed the repair as rework
LATER_FIX_RE = re.compile(r"\b(?:fix|fixes|fixed|restores?|restored|repairs?|repaired|regress\w*|wrong|bugs?|back)\b",
                          re.I)
# Hand-read 2026-10-30, not repairs of the fix they follow: the two later worker.py commits of the sanity item
# (STEVEDESKTOP_WORKER_BUILD_DURABLE_ATTEMPTS): a canary-stops-the-game feature, a runner-clone heal. "restore" there
# is a feature word.
LATER_FIX_CLEARED = frozenset({"59ba780056", "589859a8d6"})
MAX_FILES = 8
LIVE_OK = ("none", "minimal", "minimal+deps")
KINDS = ("python-util", "xml-def-patch", "csharp", "live-verify", "tooling")
# Hand-picked: an item the census must keep (instrument_traps: a count is a query bug until a sanity probe proves the
# instrument can see). Since the vet gates the pool it must also DISCRIMINATE under the judge route (pass at the fix,
# fail at base). FOUNDRY 2026-10-30 (ARENA_SANITY_ITEM_FIX_NOT_DISCRIMINATING): the old pick
# STEVEDESKTOP_WORKER_BUILD_DURABLE_ATTEMPTS fails at the fix too (its check reads source_sha from git; the judge tree
# has no .git). TANKS_ROW_FIX_LEVELS_WHAT_RULING_FORBADE discriminates but is now label_suspect (unlabelled), so the
# probe is ROAST_STICK's item: Clean, and pass/fail only with its traced reads (src/RimStarWars/Cuisine/Defs), so a
# broken read trace also trips the probe.
SANITY_ITEM = "ROAST_STICK_FIX_DISABLED_COOK_STAT_ERRORS"
# FOUNDRY 2026-10-30 (ARENA_SANITY_HARDEN_GREEN_ON_DEAD_BASE): "kept" is one-sided. ROAST_STICK's base failure is a
# FileNotFoundError on a fix-added file, so a dead (empty) base tree fails it the same way and the probe stays green;
# and a census that dropped the reads would still keep it while the judge rejects every arm. So, with a vet, the
# sanity item also needs (1) its hidden reads to hold `reads` (what the judge materialises), and (2) a NEGATIVE
# CONTROL: `control` = (item, check path) whose vet record must stay passes_at_base. That check imports the tree's
# own code at base, so a base side materialised empty or wrong fails it and the census raises SanityFail.
SANITY_PROBES = {SANITY_ITEM: {"reads": ("src/RimStarWars/Cuisine/Defs",),
                               "control": ("READER_BASELINE_REPAIR_OLD_ORDER_TRIPS",
                                           "src/RimMandrake/rimflow/selftest_reader_invariant.py")}}
BOOKKEEPING = ("infrastructure/state/ledger/*", "infrastructure/state/queue/*", "infrastructure/state/items/*",
               "AGENTS.md")
# size points from the original diff (counted files, added+deleted lines); fixed at freeze
SIZE_RULES = ((1, 2, 80), (2, 4, 300))      # (points, max files, max lines); larger is 4
TOOLING_ROOTS = ("src/RimMandrake/rimflow/", ".claude/", "infrastructure/", "skills/", "bin/")
HIDDEN_KEYS = ("label", "fix_sha", "checks", "reworks")
# A caused_by child is a rework that makes its parent Escaped only when it is itself a closed FIX: state done, not a
# design/review/decision-type kind, not a "Review/Vet ..." task, and closed at a resolvable one-parent commit that
# changes code. A proposed follow-up, a design idea or a vet task is not evidence the original fix escaped.
NONFIX_KINDS = {"design", "decision", "review", "research", "question", "ruling", "card", "investigate",
                "investigation", "check", "verify", "trial", "finding", "spike", "epic", "followup", "process",
                "decide", "innovation"}
REVIEW_TITLE = re.compile(r"(?i)^\W*(review|re-review|vet|verify|audit|assess|check|consider|decide|design)\b")
DEAD_STATES = {"dropped", "superseded"}
SCAN_CHUNK = 4 << 20                    # files larger than this are scanned in overlapping chunks, never skipped
SCAN_OVERLAP = 64 << 10
ANCHOR = 60                             # every 120-char window of a hidden body contains one aligned 60-char anchor
SHORT_BODY = 12                         # a novel block shorter than 2*ANCHOR (but >= this) is matched exactly
REWORK_DEPTH = 3                        # caused_by generations followed (child, grandchild, great-grandchild)
# the pre-rewrite history, searched in order (old_history_repos; $ARENA_OLD_HISTORY overrides, os.pathsep-separated)
OLD_HISTORY_DEFAULT = ("/home/mandrake/rm/mirror.git", "/home/mandrake/rm/retired-trees/*-git-*")
PIN_PREFIX = "refs/arena/old/"          # gc pins for pre-rewrite commits in $ARENA_OLD_HISTORY (never pushed)
ALL = "*"                               # leak scope: every task


class ArenaError(Exception):
    """A refusal. The message says what was refused and why."""


class SanityFail(ArenaError):
    pass


class TaskRefused(ArenaError):
    pass


# ---------------------------------------------------------------- paths

def arena_root() -> Path:
    env = os.environ.get("ARENA_ROOT", "").strip()
    if env:
        return Path(env)
    import rmpaths
    return rmpaths.rm_path("arena")             # agent_storage root (D:\\ClaudeWork\\rimmandrake), never hard-wired


def paths(root: Path | None = None) -> dict:
    r = Path(root) if root else arena_root()
    return {"root": r, "tasks": r / "tasks", "judge": r / "judge" / "hidden", "events": r / "events",
            "census": r / "census", "log": r / "events" / "harness.jsonl",
            # the AUTHORITATIVE freeze record: judge-only (never arm-readable), hash-chained, written only by freeze()
            "freeze": r / "judge" / "freeze.jsonl", "lock": r / "arena.lock"}


def arm_readable_roots(p: dict) -> list[Path]:
    """Paths an arm may read: the task specs, the event log, and the arm clones (everything under the arena clone
    root except its judge directory). `$ARENA_CLONES` overrides the clone root (selftests)."""
    clones = Path(os.environ.get("ARENA_CLONES", "/home/mandrake/rm/arena"))
    return [p["tasks"], p["events"], clones]


def _inside(child: Path, parent: Path) -> bool:
    c, q = os.path.realpath(child), os.path.realpath(parent)
    return c == q or c.startswith(q.rstrip("/") + "/")


# ---------------------------------------------------------------- git

def _git(repo: Path, *args, check=True) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=60)
    if check and r.returncode != 0:
        raise ArenaError("git %s: %s" % (" ".join(args), r.stderr.strip()[:200]))
    return r.stdout if r.returncode == 0 else ""


def _resolve(repo: Path, sha: str):
    out = _git(repo, "rev-parse", "--verify", "--quiet", "%s^{commit}" % sha, check=False).strip() if sha else ""
    return out or None


def _is_ancestor(repo: Path, a: str, b: str) -> bool:
    return subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", a, b],
                          capture_output=True, timeout=60).returncode == 0


def old_history_repos(old=None) -> list[Path]:
    """The pre-rewrite history, as an ordered list of existing git dirs. `old` (else $ARENA_OLD_HISTORY, else
    OLD_HISTORY_DEFAULT) is a list, or one string of os.pathsep-separated entries; each entry may be a glob.
    POOL DIAG 2026-10-30: of the 123 in-window close shas the mirror alone could not find, 107 live in the retired
    pre-rewrite clones (retired-trees/<seat>-git-<ts>): with one repo a real commit read as 'resolves nowhere'."""
    if old is None:
        old = os.environ.get("ARENA_OLD_HISTORY") or list(OLD_HISTORY_DEFAULT)
    entries = [str(e) for e in old] if isinstance(old, (list, tuple)) else str(old).split(os.pathsep)
    out = []
    for e in (e.strip() for e in entries):
        if not e:
            continue
        for p in (sorted(glob.glob(e)) if glob.has_magic(e) else [e]):
            if Path(p).is_dir() and Path(p) not in out:
                out.append(Path(p))
    return out


class Resolver:
    """A ledger sha -> (a commit in `repo`'s current history, how), or (None, why not).

    🔴 origin/main was REWRITTEN on 2026-10-28/29 (RIMMANDRAKE_EXCISE_WORK_HISTORY; lesson
    20261029T140946Z-BENCH-history-rewrite-origin-main-rimmandrake-excise.md): measured 2026-10-30, 0 of the
    in-window close shas resolve in bench or foundry. The old objects survive, unreachable, in the old-history
    repos (old_history_repos: the mirror, then the retired pre-rewrite clones). A rewritten commit keeps its author date, author and subject,
    so an old sha maps to the one current commit with the same triple; a commit the rewrite excised maps to none.
    """

    def __init__(self, repo: Path, old=None):
        self.repo = Path(repo)
        self.old = old_history_repos(old)
        self._index = None
        self.old_used = {}          # full pre-rewrite sha -> the old-history repo it was read from (pin it there)

    def _key_index(self):
        if self._index is None:
            self._index = {}
            for line in _git(self.repo, "log", "--format=%aI%x09%an%x09%s%x09%H", "HEAD").splitlines():
                a, n, s, h = line.split("\t", 3)
                self._index.setdefault((a, n, s), []).append(h)
        return self._index

    def __call__(self, sha: str):
        sha = (sha or "").strip()
        if not re.fullmatch(r"[0-9a-fA-F]{4,40}", sha):
            return None, "close sha missing or not hex"
        cur = _resolve(self.repo, sha)
        # REVIEW 2026-10-30: an object in the store that HEAD cannot reach (dangling, a stale ref's) is not current
        # history; it falls through to the old-history lookup like any other pre-rewrite sha
        if cur and _is_ancestor(self.repo, cur, "HEAD"):
            return cur, "current"
        if not self.old:
            return None, "close sha does not resolve (no old-history repo)"
        for old in self.old:                # first repo that holds the commit wins
            r = subprocess.run(["git", "-C", str(old), "log", "-1", "--format=%H%x09%aI%x09%an%x09%s",
                                sha + "^{commit}"], capture_output=True, text=True, timeout=60)
            if r.returncode == 0 and r.stdout.strip():
                break
        else:
            return None, "close sha resolves nowhere"
        full, key = r.stdout.rstrip("\n").split("\t", 1)
        self.old_used.setdefault(full, str(old))
        hits = self._key_index().get(tuple(key.split("\t", 2)), [])
        if len(hits) == 1:
            # FOUNDRY 2026-10-30 (ARENA_RESOLVER_VERIFY_REMAP_BY_PATCH_ID): the triple is metadata; two commits can
            # share it and differ in content. Measured on the real pool, 2 of 241 remaps did (old 465f61350b
            # changed FlowWorks/validation.py, its triple twin afd094c3ba does not).
            why = remap_content_differs(Path(old), full, self.repo, hits[0])
            if why:
                return None, "remap content differs (%s)" % why
            return hits[0], "remapped"
        return None, ("close sha excised by the history rewrite" if not hits else "close sha remaps ambiguously")


EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
PATHSPEC_CHUNK = 400


def _run(repo: Path, args, inp=None, timeout=120) -> bytes:
    r = subprocess.run(["git", "--literal-pathspecs", "-C", str(repo), *args], input=inp, capture_output=True,
                       timeout=timeout)
    if r.returncode != 0:
        raise ArenaError("git %s: %s" % (" ".join(args[:3]), r.stderr.decode("utf-8", "replace").strip()[:200]))
    return r.stdout


def _commit_diff(repo: Path, sha: str):
    """(first parent or the empty tree, {path: binary?}) of `sha`'s own change, renames off."""
    par = (_parents(repo, sha) or [EMPTY_TREE])[0]
    out = {}
    for rec in _run(repo, ["diff-tree", "-r", "-z", "--numstat", "--no-renames", par, sha]).split(b"\0"):
        if rec:
            a, _d, path = rec.split(b"\t", 2)
            out[path.decode("utf-8", "surrogateescape")] = a == b"-"
    return par, out


def _patch_id(repo: Path, par: str, sha: str, paths) -> str:
    """git patch-id --stable of `par..sha` restricted to `paths` (chunked pathspecs, one id: --stable sums per-file
    hashes, so the concatenated chunks give the id of the whole restricted diff)."""
    paths, diff = sorted(paths), b""
    for i in range(0, len(paths), PATHSPEC_CHUNK):
        diff += _run(repo, ["diff-tree", "-p", "--no-renames", "--full-index", par, sha, "--",
                            *paths[i:i + PATHSPEC_CHUNK]])
    if not diff:
        return ""
    out = _run(repo, ["patch-id", "--stable"], inp=diff).split()
    return out[0].decode() if out else ""


def _paths_in(repo: Path, tree: str, paths) -> set:
    """The subset of `paths` that exist (as a file) in `tree`."""
    if tree == EMPTY_TREE:
        return set()
    paths, got = sorted(paths), set()
    for i in range(0, len(paths), PATHSPEC_CHUNK):
        for p in _run(repo, ["ls-tree", "-r", "-z", "--name-only", tree, "--",
                             *paths[i:i + PATHSPEC_CHUNK]]).split(b"\0"):
            if p:
                got.add(p.decode("utf-8", "surrogateescape"))
    return got


def _tree_entries(repo: Path, tree: str, paths) -> dict:
    """{path: (mode, blob)} for the subset of `paths` present in `tree`."""
    if tree == EMPTY_TREE:
        return {}
    paths, got = sorted(paths), {}
    for i in range(0, len(paths), PATHSPEC_CHUNK):
        for rec in _run(repo, ["ls-tree", "-r", "-z", tree, "--", *paths[i:i + PATHSPEC_CHUNK]]).split(b"\0"):
            if rec:
                meta, _, path = rec.partition(b"\t")
                mode, _, blob = meta.decode().split(" ")
                got[path.decode("utf-8", "surrogateescape")] = (mode, blob)
    return got


def remap_content_differs(old: Path, old_sha: str, repo: Path, new_sha: str) -> str:
    """'' when the pre-rewrite commit and its triple twin made the same change, else why not.
    A path the old commit changed that exists in NEITHER the new commit's tree nor its parent's was excised by the
    rewrite and is dropped; the rest must be the very same path set with the same `git patch-id --stable`, and a
    binary path (numstat '-', which patch-id does not see) the same resulting blob."""
    try:
        opar, od = _commit_diff(old, old_sha)
        npar, nd = _commit_diff(repo, new_sha)
        alive = _paths_in(repo, new_sha, od) | _paths_in(repo, npar, od)
        kept = {p: b for p, b in od.items() if p in alive}
        if set(kept) != set(nd):
            extra, miss = sorted(set(kept) - set(nd)), sorted(set(nd) - set(kept))
            return "paths: old only %s, new only %s" % (extra[:3], miss[:3])
        text = [p for p in kept if not kept[p] and not nd[p]]
        if _patch_id(old, opar, old_sha, text) != _patch_id(repo, npar, new_sha, text):
            return "patch-id of %d text path(s) differs" % len(text)
        # patch-id sees neither binary content nor mode lines: compare (mode, blob) before and after for a binary
        # path (so A->C and B->C, or two different deletions, differ) and the mode pair for every path
        e = [_tree_entries(old, opar, kept), _tree_entries(old, old_sha, kept), _tree_entries(repo, npar, kept),
             _tree_entries(repo, new_sha, kept)]
        none = ("", "")
        for p in sorted(kept):
            o, n = (e[0].get(p, none), e[1].get(p, none)), (e[2].get(p, none), e[3].get(p, none))
            if kept[p] or nd[p]:
                if o != n:
                    return "binary %s differs" % p
            elif (o[0][0], o[1][0]) != (n[0][0], n[1][0]):
                return "mode of %s differs" % p
    except (ArenaError, subprocess.TimeoutExpired, ValueError) as e:
        return "cannot compare: %s" % str(e)[:120]
    return ""


def pin_old(shas, old=None) -> dict:
    """Point refs/arena/old/<sha> at each pre-rewrite commit so gc cannot drop it. `shas` is {repo: [sha]} (the
    census report's old_history_pins: each pinned in the repo that resolved it) or a list (each pinned in the first
    old_history_repos(old) entry holding it). update-ref only (no push, no force); an existing pin is left alone, and
    one that points at a DIFFERENT commit is reported in `conflict` (never counted as pinned, never moved).
    -> {pinned, already, conflict, missing, repo}."""
    repos = old_history_repos(old)
    groups = ({Path(r): list(v) for r, v in shas.items()} if isinstance(shas, dict) else {None: list(shas)})
    out = {"repo": os.pathsep.join(str(r) for r in (repos if None in groups else groups)), "pinned": 0,
           "already": 0, "conflict": [], "missing": []}
    have = {}
    for where, group in groups.items():
        for s in sorted(set(group)):
            for r in ([where] if where is not None else repos):
                if not r.is_dir() or _resolve(r, s) != s:
                    continue
                if r not in have:
                    have[r] = dict(ln.split(" ", 1)[::-1] for ln in _git(
                        r, "for-each-ref", "--format=%(objectname) %(refname)", PIN_PREFIX, check=False).splitlines())
                ref = PIN_PREFIX + s
                if ref in have[r]:
                    if have[r][ref] == s:
                        out["already"] += 1
                    else:
                        out["conflict"].append(s)
                else:
                    _git(r, "update-ref", ref, s)
                    have[r][ref] = s
                    out["pinned"] += 1
                break
            else:
                out["missing"].append(s)
    return out


def _parents(repo: Path, sha: str) -> list[str]:
    return _git(repo, "rev-list", "--parents", "-n", "1", sha).split()[1:]


def _numstat(repo: Path, base: str, head: str) -> list[tuple[str, int, str]]:
    """[(path, lines, status)] with renames off, so a moved file is a delete plus an add."""
    status = {}
    for line in _git(repo, "diff-tree", "-r", "--no-renames", "--name-status", base, head).splitlines():
        st, _, path = line.partition("\t")
        status[path] = st[:1]
    out = []
    for line in _git(repo, "diff-tree", "-r", "--no-renames", "--numstat", base, head).splitlines():
        a, d, path = line.split("\t", 2)
        lines = (int(a) if a.isdigit() else 0) + (int(d) if d.isdigit() else 0)
        out.append((path, lines, status.get(path, "M")))
    return out


def _show(repo: Path, sha: str, path: str):
    r = subprocess.run(["git", "-C", str(repo), "show", "%s:%s" % (sha, path)], capture_output=True, timeout=60)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


# ---------------------------------------------------------------- classification

def is_bookkeeping(path: str) -> bool:
    return any(fnmatch.fnmatch(path, g) for g in BOOKKEEPING)


def is_selftest(path: str) -> bool:
    return path.endswith(".py") and os.path.basename(path).startswith("selftest")


def is_defxml(path: str) -> bool:
    return path.endswith(".xml") and bool(re.search(r"/(Defs|Patches)/", path))


def classify(files: list[str]):
    """-> kind or None (nothing the gate can judge offline). C# outranks XML outranks Python."""
    if any(f.endswith(".cs") for f in files):
        return "csharp"
    if any(is_defxml(f) for f in files):
        return "xml-def-patch"
    py = [f for f in files if f.endswith(".py")]
    if not py:
        return None
    if all(f.startswith(TOOLING_ROOTS) for f in py):
        return "tooling"
    return "python-util"


def _mod_of(path: str):
    parts = path.split("/")
    return parts[2] if len(parts) > 3 and parts[0] == "src" else None


HELD_BACK = "the judge runs %d held-back selftest(s) the original fix added"


def proof_for(files: list[str], added=frozenset(), deleted=frozenset()):
    """The proof an arm is told about, or None when the fix added no objective proof. A selftest the fix ADDED is a
    hidden check: it did not exist at base_sha, so naming it would leak it; the proof only says how many the judge
    holds. A selftest the fix CHANGED existed at base and is named. A file the fix DELETED proves nothing."""
    files = [f for f in files if f not in deleted]
    cmds = []
    tests = sorted(f for f in files if is_selftest(f) and f not in added)
    if tests:
        cmds.append("python3 src/RimMandrake/Utils/run_selftests.py --only " + " ".join(tests))
    held = sum(1 for f in files if is_selftest(f) and f in added)
    if held:
        cmds.append(HELD_BACK % held)
    xml = sorted(f for f in files if is_defxml(f))
    if xml:
        cmds.append("python3 skills/rimworld-modding/scripts/validate_patch.py " + " ".join(xml))
    for mod in sorted({_mod_of(f) for f in files if f.endswith(".cs")} - {None}):
        cmds.append("python3 src/RimMandrake/Utils/winbuild.py " + mod)
    return " && ".join(cmds) or None


def size_points(nfiles: int, lines: int) -> int:
    for pts, mf, ml in SIZE_RULES:
        if nfiles <= mf and lines <= ml:
            return pts
    return 4


def area_for(files: list[str]) -> list[str]:
    return sorted({(os.path.dirname(f) or ".") + "/*" for f in files})


def _section(prose: str, name: str):
    m = re.search(r"(?ims)^##\s*%s\s*$(.*?)(?=^##\s|\Z)" % re.escape(name), prose or "")
    return m.group(1).strip() if m else None


def _day(ts: str) -> str:
    return (ts or "")[:10]


def _epoch(ts: str) -> float:
    return dt.datetime.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc).timestamp()


def _prose_at(repo: Path, sha: str, iid: str):
    for rel in ("infrastructure/state/items/%s.md" % iid, "infrastructure/state/items/closed/%s.md" % iid):
        txt = _show(repo, sha, rel)
        if txt is not None:
            return txt
    return None


def _prompt_hints(repo: Path, fix: str, iid: str, start_ts, base_prose) -> bool:
    """Metadata only: does the prose at base_sha hold a non-blank line the claim-time prose lacks? The claim-time
    prose is the item file at the commit nearest before the start event (git log -1 --before=<ts>); no start event
    -> False (nothing to compare against)."""
    if not start_ts or not base_prose:
        return False
    try:
        claim = _git(repo, "log", "-1", "--format=%H", "--before=" + str(start_ts), fix, check=False).strip()
    except ArenaError:
        return False
    if not claim:
        return True                       # the item had no history before the claim: all of it came later
    cp = _prose_at(repo, claim, iid)
    if cp is None:
        return True
    have = {ln.strip() for ln in cp.splitlines() if ln.strip()}
    return any(ln.strip() and ln.strip() not in have for ln in base_prose.splitlines())


def _rework_verdict(r, by_id, resolve, repo, parent_fix=None, parent_files=frozenset()):
    """-> (verdict, fix commit). verdict 'counts' (a closed code fix that descends from the parent's fix and changes
    one of the parent's files: the parent escaped), 'pending' (an open fix-type descendant: the parent's Clean is
    provisional), or why it does not count."""
    kind = (r.kind or "").lower()
    if kind in NONFIX_KINDS:
        return "not a fix (kind %s)" % kind, None
    if REVIEW_TITLE.match(r.title or ""):
        return "a review/design task, not a fix (title)", None
    if r.state in DEAD_STATES:
        return "rework %s" % r.state, None
    if r.state != "done":
        return "pending", None
    rclose = [e for e in by_id.get(r.id, []) if e.get("event") == "close"]
    rfix = resolve(str(rclose[-1].get("sha") or ""))[0] if rclose else None
    if not rfix or len(_parents(repo, rfix)) != 1:
        return "closed without a resolvable one-parent fix commit", None
    files = [d[0] for d in _numstat(repo, _parents(repo, rfix)[0], rfix) if not is_bookkeeping(d[0])]
    if not classify(files):
        return "its close commit changes no code", None
    if parent_fix and (rfix == parent_fix or _is_ancestor(repo, rfix, parent_fix)):
        return "its fix landed at or before the parent's fix", None
    # REVIEW 2026-10-30: "lands after" means DESCENDS from the parent's fix; a commit on a divergent branch never
    # had the parent's fix under it, so changing the same file there is not an escape of that fix
    if parent_fix and not _is_ancestor(repo, parent_fix, rfix):
        return "its fix does not descend from the parent's fix (divergent branch)", None
    if parent_files and not set(files) & set(parent_files):
        return "its fix changes none of the parent's files (%s)" % ", ".join(sorted(files)[:3]), None
    return "counts", rfix


def _blob(repo: Path, sha: str, path: str):
    return _git(repo, "rev-parse", "%s:%s" % (sha, path), check=False).strip() or None


def _test_entry(repo: Path, sha: str, base: str, path: str, st: str, **extra) -> dict:
    """A hidden test as the judge stores it: body at `sha`, its git blob id (the object scan looks for it), and the
    NOVEL blocks (lines the task's base does not have), which are what the text scan matches."""
    body = _show(repo, sha, path)
    old = _show(repo, base, path)
    return dict(extra, path=path, added=st == "A", body=body, blob=_blob(repo, sha, path),
                novel=_novel_blocks(old, body))


def _novel_blocks(old, new) -> list[str]:
    if not new:
        return []
    if not old:
        return [new]
    a, b = old.splitlines(), new.splitlines()
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return ["\n".join(b[j1:j2]) for tag, _, _, j1, j2 in sm.get_opcodes() if tag in ("insert", "replace")]


_BASE_FIELD = re.compile(rb'"base_sha":\s*"[0-9a-fA-F]{7,40}"')


def _public_bytes(task: dict) -> bytes:
    """The task file's bytes with its base_sha FIELD removed: that one field may name an earlier fix (history)."""
    return _BASE_FIELD.sub(b'"base_sha": null', _dump(task))


# ---------------------------------------------------------------- census

def _related_tokens(text: str) -> set:
    return set(re.findall(r"[a-z]{4,}", (text or "").replace("_", " ").lower())) - RELATED_STOP


def close_sha_unrelated(repo: Path, fix: str, iid: str, title: str) -> bool:
    """The close named a commit that is about something else: its message neither names the item nor shares one
    meaningful word with the item's id or title. Measured 2026-10-30 on the 239-task pool: score 0 is FINDMOD and two
    art items; a shared word already holds for terse real fixes, so nothing stricter is safe."""
    msg = _git(repo, "log", "-1", "--format=%B", fix)
    return iid not in msg and not (_related_tokens(iid + " " + title) & _related_tokens(msg))


def later_fixes(repo: Path, fix: str, files: list, t_close: float) -> list:
    """Commits up to ESCAPE_DAYS after the close that touch the fix's code with a repair-shaped subject: rework
    nobody filed (TANK_SETTLE's 1d77c17651), which makes a Clean label unsafe. The fix's own selftests do not count
    unless they are all it changed. Author time, in Python: a rewrite moves committer dates, and --since uses those."""
    code = [f for f in files if not is_selftest(f)] or files
    out = _git(repo, "log", "--abbrev=10", "--format=%h%x00%at%x00%s", "%s..HEAD" % fix, "--", *code)
    hits = []
    for line in out.splitlines():
        sha, at, subject = line.split("\0", 2)
        if (t_close < int(at) <= t_close + ESCAPE_DAYS * 86400 and LATER_FIX_RE.search(subject)
                and sha[:10] not in LATER_FIX_CLEARED):
            hits.append({"sha": sha, "subject": subject[:120]})
    return hits


def census(events=None, repo: Path = REPO, window=WINDOW, sanity=SANITY_ITEM, old_history=None, vet=None,
           vet_missing: list | None = None, probes: dict | None = None, exclude: dict | None = None):
    """-> (pool, report). Pool entries are (task, hidden). Raises SanityFail when the sanity item is not kept.
    `vet(base, fix, path, body)` -> a vet record ({base_rc, fix_rc, ...}) or None when the check was never run
    (vet_lookup over the vet cache). With vet=None nothing is vetted: the pool is candidates, and freeze refuses
    it. With a vet, a never-run check rejects its task (fail closed), and `vet_missing` (a list) collects a vet job
    (vet_jobs shape) for each such task: every candidate, before the chain dedup, so one `vet` pass covers them.
    `probes` ({"reads": [...], "control": (item, path)}, default SANITY_PROBES[sanity]) applies with a vet only:
    the sanity item's hidden reads must hold `reads` and the control check must stay passes_at_base.
    `exclude` ({source item: reason}, default load_pool_exclusions()) leaves those items out of the returned pool
    after the probe; report["excluded"] = {task id: reason}."""
    if probes is None:
        probes = SANITY_PROBES.get(sanity) if sanity else None
    control = tuple((probes or {}).get("control") or ()) or None
    control_rec: list = []
    vstat = {"run": vet is not None, "checks": 0, "discriminating": 0, "passes_at_base": 0, "fails_at_fix": 0,
             "timeout": 0, "base_invalid": 0, "not_vetted": 0, "tasks_rejected": 0}
    if events is None:
        events = model.read()
    world = model.replay(events)
    resolve = Resolver(repo, old_history)
    by_id: dict[str, list] = {}
    for ev in events:
        if ev.get("id"):
            by_id.setdefault(ev["id"], []).append(ev)
    reworks: dict[str, list] = {}
    for it in world.items.values():
        if it.caused_by:
            reworks.setdefault(str(it.caused_by), []).append(it)

    rejects: dict[str, int] = {}
    reasons: dict[str, str] = {}
    pool = []

    def reject(iid, why):
        rejects[why] = rejects.get(why, 0) + 1
        reasons[iid] = why

    scanned = 0
    for iid, it in sorted(world.items.items()):
        evs = by_id.get(iid, [])
        closes = [e for e in evs if e.get("event") == "close"]
        in_win = [e for e in closes if window[0] <= _day(e.get("ts")) <= window[1]]
        if not in_win:
            continue
        scanned += 1                    # every item with a close in the window is counted and gets a reason
        close = closes[-1]
        if it.state != "done":
            reject(iid, "reopened after its in-window close (state now %s)" % it.state); continue
        if close is not in_win[-1]:
            reject(iid, "last close falls outside the window"); continue
        # BENCH POOL RULING 2026-10-30T01:59:10Z: no start event required (base = the closing commit's parent)
        fix, how = resolve(str(close.get("sha") or ""))
        if not fix:
            reject(iid, how); continue
        par = _parents(repo, fix)
        if len(par) != 1:
            reject(iid, "close sha is a merge or root"); continue
        base = par[0]
        diff = [d for d in _numstat(repo, base, fix) if not is_bookkeeping(d[0])]
        if not diff:
            reject(iid, "bookkeeping-only diff"); continue
        if len(diff) > MAX_FILES:
            reject(iid, "diff over %d files" % MAX_FILES); continue
        if it.needs != "offline":
            reject(iid, "needs %s (not offline)" % it.needs); continue
        files = [d[0] for d in diff]
        kind = classify(files)
        if not kind:
            reject(iid, "no offline-judgeable code"); continue
        proof = proof_for(files, {d[0] for d in diff if d[2] == "A"}, {d[0] for d in diff if d[2] == "D"})
        if not proof:
            reject(iid, "no objective proof"); continue
        # CONDUCTOR DECISION 2026-10-30 (owner authority, CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM): a task must carry
        # at least one objective check beyond "the build succeeds". winbuild and validate_patch are build-class; a
        # rework's test is not the fix's own check (the original fix fails it by definition). So >= 1 selftest the
        # fix changed or added (not deleted) is required
        if not any(is_selftest(d[0]) and d[2] != "D" for d in diff):
            reject(iid, "build-only proof (no fix selftest beyond the build/validate)"); continue
        filed = next((e for e in evs if e.get("event") == "file"), {})
        title = filed.get("title") or it.title or iid
        if close_sha_unrelated(repo, fix, iid, title):
            reject(iid, "close sha unrelated to the item"); continue
        t_close = _epoch(close["ts"])
        rw, pending, considered = [], [], []
        for r, depth in _descendants(iid, reworks):
            # any descendant filed up to ESCAPE_DAYS after the close: one filed seconds BEFORE the close (a review
            # child of the closing session) counts too; the fix-order and file checks keep a pre-close split out
            if not (r.created_at and _epoch(r.created_at) - t_close <= ESCAPE_DAYS * 86400):
                continue
            verdict, rfix = _rework_verdict(r, by_id, resolve, repo, fix, files)
            considered.append({"item": r.id, "kind": r.kind, "state": r.state, "depth": depth, "verdict": verdict})
            if verdict == "counts":
                rw.append((r, rfix))
            elif verdict == "pending":
                pending.append(r.id)
        # REVIEW 2026-10-30: only a verify pass in the FINAL close cycle (after the previous close, if any) labels it:
        # a pass recorded before an earlier close verified other code
        prev = _epoch(closes[-2]["ts"]) if len(closes) > 1 else float("-inf")
        verified = any(e.get("event") == "verify" and e.get("result") == "pass" and e.get("ts")
                       and _epoch(e["ts"]) > prev for e in evs)
        # the label is optional metadata (ruling): an unlabelled item stays in the pool with label null
        label = "Escaped" if rw else ("Clean" if verified else None)
        suspect = later_fixes(repo, fix, files, t_close) if label == "Clean" else []
        if suspect:                     # unfiled rework: not Escaped (nothing proves it), but no longer Clean either
            label = None

        lines = sum(d[1] for d in diff)
        prose = _prose_at(repo, base, iid)
        prompt = title + ("\n\n" + prose.strip() if prose else "")
        crit = _section(prose, "criteria") if prose else None
        crit_src = "prose ## criteria at base_sha"
        # FOUNDRY 2026-10-30 (ARENA_TASKS_FIX_CRITERIA_FROM_LATER_LEDGER): no fallback to the ledger manifest
        # (it.criteria): it is written by the `implemented` event, WITH the fix, from the final ledger state, so it
        # can describe the answer. Prose at base, else the title.
        if not crit:
            crit, crit_src = title, "title (no criteria written)"
        tid = "RP_" + iid
        checks = []
        for path, _, st in diff:
            if is_selftest(path) and st != "D":
                checks.append(_test_entry(repo, fix, base, path, st, type="fix_test",
                                          command="python3 src/RimMandrake/Utils/run_selftests.py --only " + path))
        reads: set = set()             # judge-only: what the checks read outside the tree (arena_vet_reads)
        if vet is not None:
            # FOUNDRY 2026-10-30 (ARENA_TASKS_VET_CHECK_FAILS_AT_BASE): a hidden check that also passes at base
            # proves nothing. Each fix_test carries its measured base/fix exit codes; one that does not FAIL at base
            # and PASS at the fix is kept as fix_test_unscored (still leak-scanned, never scored by the judge)
            unvetted = 0
            for c in checks:
                rec = vet(base, fix, c["path"], c["body"])
                if rec is None:
                    unvetted += 1
                    vstat["not_vetted"] += 1
                    c["vet"] = None
                    continue
                ok, why = vet_verdict(rec)
                if control and (iid, c["path"]) == control:
                    control_rec.append(rec)
                reads.update(rec.get("reads") or [])
                vstat[why] += 1
                vstat["checks"] += 1
                c["vet"] = {"key": vet_key(base, fix, c["path"], c["body"]), "runner": _runner_id(),
                            "base_rc": rec.get("base_rc"), "fix_rc": rec.get("fix_rc"), "discriminates": ok,
                            "fix_result": rec.get("fix_result"), "base_result": rec.get("base_result"), "why": why}
                if not ok:
                    c["type"] = "fix_test_unscored"
            if unvetted:               # fail closed: a check that was never run is not evidence either way
                vstat["tasks_rejected"] += 1
                if vet_missing is not None:
                    vet_missing.append({"task": tid, "base": base, "fix": fix, "area": area_for(files), "checks": [
                        {"path": c["path"], "body": c["body"], "key": vet_key(base, fix, c["path"], c["body"])}
                        for c in checks if c.get("vet", 0) is None]})
                reject(iid, "hidden check not vetted (run `arena_tasks.py vet`)"); continue
            # fail closed: a check the judge cannot run (timeout, sandbox-denied, no marker) on either side would be
            # an error in every judged round, whatever its siblings prove, so it takes the whole task out
            if any(c["vet"]["fix_result"] not in ("pass", "fail") or c["vet"]["base_result"] not in ("pass", "fail")
                   for c in checks):
                vstat["tasks_rejected"] += 1
                reject(iid, "a hidden check cannot run under the judge (timeout, denied or no marker)")
                continue
            if not any(c["type"] == "fix_test" for c in checks):
                vstat["tasks_rejected"] += 1
                reject(iid, "no fix selftest discriminates (each passes at base, fails at the fix or times out)")
                continue
            # an unscored ADDED test is not one the judge holds back: the proof must not count it
            unscored_new = {c["path"] for c in checks if c["type"] == "fix_test_unscored" and c["added"]}
            proof = proof_for([f for f in files if f not in unscored_new], {d[0] for d in diff if d[2] == "A"},
                              {d[0] for d in diff if d[2] == "D"})
        rw_out = []
        for r, rfix in rw:
            prel = os.path.relpath(model.item_path(r.id), str(model.ROOT))
            entry = {"item": r.id, "title": r.title, "filed": r.created_at, "state": r.state, "fix_sha": rfix,
                     # pinned to the rework's own fix, so the judge bytes do not drift with HEAD
                     "prose": _show(repo, rfix, prel) or _show(repo, "HEAD", prel), "tests": []}
            for path, _, st in _numstat(repo, _parents(repo, rfix)[0], rfix):
                if is_selftest(path) and st != "D":
                    entry["tests"].append(_test_entry(repo, rfix, base, path, st))
            entry["needs_authoring"] = not entry["tests"]
            rw_out.append(entry)
            checks.append({"type": "escape_rework", "rework_item": r.id, "needs_authoring": not entry["tests"]})
        hidden = {"task": tid, "source_item": iid, "label": label, "fix_sha": fix, "ledger_sha": close.get("sha"),
                  "sha_resolution": how, "checks": checks, **({"reads": sorted(reads)} if reads else {}),
                  "reworks": rw_out, "rework_candidates": considered,
                  # an open fix-type rework filed in the window: Clean is provisional until it closes or dies
                  "label_pending": sorted(pending),
                  "label_suspect": suspect,
                  # a fixed instant, not a now-dependent boolean, so a re-census reproduces the frozen bytes; a label
                  # read before this instant can still flip to Escaped
                  "label_window_ends": dt.datetime.fromtimestamp(t_close + ESCAPE_DAYS * 86400, dt.timezone.utc)
                  .strftime("%Y-%m-%dT%H:%M:%SZ")}
        task = {"id": tid, "source_item": iid, "kind": kind, "size": size_points(len(diff), lines),
                "size_basis": {"files": len(diff), "lines": lines}, "area": area_for(files), "prompt": prompt,
                "criteria": crit, "criteria_source": crit_src, "proof": proof, "live": "none",
                # replay is needs=offline by construction (rejected above otherwise): no live TestPilot plan exists
                # for it, and null says so explicitly (live_plan_refusal); never the proof standing in for one
                "live_plan": None, "hidden_checks": None, "base_sha": base, "prompt_source": "base_parent",
                "prompt_may_hold_hints": _prompt_hints(repo, fix, iid, next(
                    (e.get("ts") for e in evs if e.get("event") == "start"), None), prose)}
        own = Matcher([hidden]).hits(_public_bytes(task))
        if own:                           # this one task is rejected; the census goes on
            reject(iid, "task would carry its own hidden check (%s)" % own[0][1]); continue
        pool.append((close["ts"], task, hidden))

    # Chains: one pool task's public file can name another's hidden check (it IS the other item's rework, or it
    # edits a test that rework added). An arm reading it would learn the other task's label or check, so only one of
    # the two is kept. The check runs BOTH ways (a candidate's public file against the kept hidden checks, and the
    # candidate's hidden check against the kept public files), so the order only decides who wins: LABELLED tasks
    # first (they are the scarce escaped-defect subset), then by close time.
    kept_pool, seen, publics = [], Matcher([]), []
    for _, task, hidden in sorted(pool, key=lambda x: (x[2]["label"] is None, x[0])):
        pub = _public_bytes(task)          # base_sha stripped: starting where an earlier fix landed is history
        hit = seen.hits(pub)
        if hit:
            reject(task["source_item"], "would expose a hidden check of pool task " + hit[0][0])
            continue
        back = Matcher([hidden]).hits(b"\n".join(publics)) if publics else []
        if back:
            reject(task["source_item"], "its hidden check is named by a kept pool task's public file")
            continue
        seen.add(hidden)
        publics.append(pub)
        kept_pool.append((task, hidden))
    probe_pool = sorted(kept_pool, key=lambda th: th[0]["id"])
    # POOL EXCLUSIONS (pool_exclusions.json, Conductor ruling 2026-10-30): applied AFTER the chain dedup and the
    # sanity probe, so the instrument check still sees an excluded sanity item and no excluded task frees a chain
    # loser; the excluded tasks get no files (write_pool withdraws an unfrozen one) and freeze never meets them.
    exclude = load_pool_exclusions() if exclude is None else dict(exclude)
    pool = [th for th in probe_pool if th[0]["source_item"] not in exclude]
    excluded = {t["id"]: exclude[t["source_item"]] for t, _ in probe_pool if t["source_item"] in exclude}

    labels = {"Clean": 0, "Escaped": 0, "unlabelled": 0}
    for _, h in pool:
        labels[h["label"] or "unlabelled"] += 1
    kept = {t["source_item"] for t, _ in probe_pool}
    report = {"excluded": excluded, "window": list(window), "scanned_closed_in_window": scanned, "pool": len(pool), "labels": labels,
              "labelled": labels["Clean"] + labels["Escaped"], "old_history_shas": sorted(resolve.old_used),
              "old_history_pins": {r: sorted(h for h, rr in resolve.old_used.items() if rr == r)
                                   for r in sorted(set(resolve.old_used.values()))},
              "rejects": dict(sorted(rejects.items(), key=lambda kv: -kv[1])),
              "sanity": {"item": sanity, "found": sanity in kept, "reason_if_not": reasons.get(sanity)},
              "kinds": _count(t["kind"] for t, _ in pool), "sizes": _count(str(t["size"]) for t, _ in pool),
              "vet": vstat}
    bc = base_contains(pool, repo)
    report["base_contains"] = bc
    report["base_contains_pairs"] = sum(len(v) for v in bc.values())
    if sanity and sanity not in kept:
        raise SanityFail("sanity item %s was not kept (%s): the census is blind, not the pool small"
                         % (sanity, reasons.get(sanity) or "not scanned: not a done item closed in window"))
    if sanity and probes and vet is not None:
        got = next(h for t, h in probe_pool if t["source_item"] == sanity).get("reads") or []
        want = list(probes.get("reads") or ())
        report["sanity"]["reads"] = got
        if not got or any(r not in got for r in want):
            raise SanityFail("sanity item %s: hidden reads %s lack %s: the judge would reject every arm (reads "
                             "dropped between vet and judge file)" % (sanity, got, [r for r in want if r not in got]))
        if control:
            cr = control_rec[-1] if control_rec else None
            cv = vet_verdict(cr)[1] if cr else "not vetted / not scanned"
            report["sanity"]["control"] = {"item": control[0], "path": control[1], "verdict": cv}
            if cv != "passes_at_base":
                raise SanityFail("negative control %s %s is %s, not passes_at_base: the vet's base side is not the "
                                 "real base tree" % (control[0], control[1], cv))
    return pool, report


POOL_EXCLUSIONS = HERE / "pool_exclusions.json"
POOL_EXCLUSIONS_SCHEMA = "arena_pool_exclusions/1"


def load_pool_exclusions(path=None) -> dict:
    """{source item: reason} from the committed exclusion file ({"schema": POOL_EXCLUSIONS_SCHEMA, "exclude":
    [{"item", "reason", "ruling"}]}). Absent file: {}. A malformed file raises ArenaError (never a silent empty)."""
    fp = Path(path) if path else POOL_EXCLUSIONS
    if not fp.exists():
        return {}
    doc = _loads(fp.read_bytes(), str(fp))
    rows = doc.get("exclude") if isinstance(doc, dict) else None
    if not (isinstance(doc, dict) and doc.get("schema") == POOL_EXCLUSIONS_SCHEMA and isinstance(rows, list)):
        raise ArenaError("%s: not an %s document" % (fp, POOL_EXCLUSIONS_SCHEMA))
    out = {}
    for r in rows:
        if not (isinstance(r, dict) and isinstance(r.get("item"), str) and r["item"]
                and isinstance(r.get("reason"), str) and r["reason"].strip()):
            raise ArenaError("%s: every exclusion needs an item and a reason (%r)" % (fp, r))
        if r["item"] in out:
            raise ArenaError("%s: %s excluded twice" % (fp, r["item"]))
        out[r["item"]] = r["reason"] + ((" [" + r["ruling"] + "]") if r.get("ruling") else "")
    return out


def _descendants(iid, children, depth=REWORK_DEPTH):
    """[(item, generation)] of every caused_by descendant, breadth first, each once (a cycle cannot loop)."""
    out, seen, front = [], {iid}, [iid]
    for gen in range(1, depth + 1):
        nxt = []
        for pid in front:
            for c in sorted(children.get(pid, []), key=lambda x: x.id):
                if c.id not in seen:
                    seen.add(c.id)
                    out.append((c, gen))
                    nxt.append(c.id)
        front = nxt
    return out


def _count(xs):
    out: dict = {}
    for x in xs:
        out[x] = out.get(x, 0) + 1
    return out


# ---------------------------------------------------------------- vet (ARENA_TASKS_VET_CHECK_FAILS_AT_BASE)
# A hidden fix_test is evidence only if the JUDGE would see it FAIL at base_sha and PASS at the fix. The vet runs it
# the judge's own way: arena_judge.materialise (TREE_PATHS + the task's area, as the judge builds an arm's tree) of
# each side, then arena_judge.run_hidden (its sandbox, env allow-list, audit-hook runner, nonce marker, timeout). The
# fix side stands for a perfect arm. Results are cached in <arena>/judge/vet_cache.jsonl (judge-only, like the hidden
# checks); the census reads the cache and never runs code.

VET_BUDGET = 480                        # seconds: one `vet` call stays inside a foreground command window
VET_RUNNER = "arena_judge.materialise+run_hidden+trace_reads/2"


def vet_runner_id(judge_src: bytes | None = None) -> str:
    """VET_RUNNER + a hash of ALL the judge code a check result depends on: the whole arena_judge.py (its RUNNER,
    tree paths, env allow-list, timeout, and every helper materialise/run_hidden/the sandbox call, e.g. SafeRepo),
    plus the two outside functions they call (arena_tasks.paths, judge_codex_home.posix_within). In the cache key:
    any judge edit stops every record matching and the census fails closed until `vet` reruns."""
    import inspect
    import arena_judge as J            # lazy: arena_judge imports this module
    src = Path(J.__file__).read_bytes() if judge_src is None else judge_src
    h = hashlib.sha256(src)
    for f in (paths, J.JH.posix_within):
        h.update(b"\0" + inspect.getsource(f).encode("utf-8"))
    h.update(b"\0" + Path(VR.__file__).read_bytes() + b"\0" + _vet_task_keyed_source().encode("utf-8"))
    return VET_RUNNER + "@" + h.hexdigest()[:16]


# ARENA_VET_REPAIR_TAIL_EATS_FAIL_LINES: the stored tails are what a human or the reader sees of a check's output;
# they never feed a verdict (vet_verdict reads results and rcs only). So the tail cut is NOT part of the cache key:
# _vet_task's source is hashed with the vet_tail(...) calls written back as the old `[-600:]` cut, and every
# record vetted before the fix still matches. Any OTHER edit to _vet_task still changes the key.
_TAIL_KEY_FORMS = (('vet_tail(fr.get("tail"))', '(fr.get("tail") or "")[-600:]'),
                   ('vet_tail(br.get("tail"))', '(br.get("tail") or "")[-600:]'))


def _vet_task_keyed_source() -> str:
    import inspect
    src = inspect.getsource(_vet_task)
    for new, old in _TAIL_KEY_FORMS:
        if src.count(new) != 1:
            raise ArenaError("vet key: _vet_task no longer has exactly one %s; update _TAIL_KEY_FORMS" % new)
        src = src.replace(new, old)
    return src


VET_TAIL_CHARS = 1500           # = arena_judge.TAIL_CHARS: the judge tail is stored whole when it fits
VET_TAIL_HEAD = 300
_FAIL_LINE = re.compile(r"Traceback \(most recent call last\)|\b[A-Z]\w*(?:Error|Exception|Exit)\b|\bFAIL|\bassert"
                        r"|\berror\b|\bnot ok\b|\bUNMEASURED\b|\bBLIND\b|\bmissing\b|\bexpected\b", re.I)


def vet_tail(t, n: int = VET_TAIL_CHARS) -> str:
    """The stored tail of one check run: whole when it fits in `n`; else its head, every failure-looking line
    (Traceback, *Error, FAIL, assert, ...) up to half the budget, and as much of the end as is left, in order, with
    a `[... N chars cut ...]` marker at each gap. The old `[-600:]` kept only the end, so a check that prints its
    FAIL lines and then passing lines (or a long stderr) stored no reason at all."""
    t = t or ""
    if len(t) <= n:
        return t
    lines = t.splitlines(keepends=True)
    size = [len(x) for x in lines]            # original lengths, for the gap markers
    keep, used = set(), 0
    budget = n - 160                          # room for the gap markers
    for i, ln in enumerate(lines):            # head
        if used + len(ln) > VET_TAIL_HEAD:
            break
        keep.add(i)
        used += len(ln)
    fails = 0
    for i, ln in enumerate(lines):            # failure lines, each clipped
        if i in keep or not _FAIL_LINE.search(ln):
            continue
        ln = ln if len(ln) <= 240 else ln[:240] + "\n"
        if fails + len(ln) > n // 2 or used + len(ln) > budget:
            break
        lines[i] = ln
        keep.add(i)
        fails += len(ln)
        used += len(ln)
    for i in range(len(lines) - 1, -1, -1):   # end
        if i in keep:
            continue
        if used + len(lines[i]) > budget:
            if budget - used > 0:             # a long line: keep its end
                lines[i] = "[...]" + lines[i][-(budget - used):]
                keep.add(i)
            break
        keep.add(i)
        used += len(lines[i])
    out, gap = [], 0
    for i, ln in enumerate(lines):
        if i in keep:
            if gap:
                out.append("[... %d chars cut ...]\n" % gap)
                gap = 0
            out.append(ln)
        else:
            gap += size[i]
    if gap:
        out.append("[... %d chars cut ...]\n" % gap)
    s = "".join(out)
    return s if len(s) <= n else s[-n:]


_RUNNER_ID: list = []


def _runner_id() -> str:
    if not _RUNNER_ID:
        _RUNNER_ID.append(vet_runner_id())
    return _RUNNER_ID[0]


def vet_cache_path(p: dict | None = None) -> Path:
    return (p or paths())["freeze"].parent / "vet_cache.jsonl"


def vet_key(base: str, fix: str, path: str, body: str) -> str:
    return hashlib.sha256(json.dumps([_runner_id(), base, fix, path, body]).encode("utf-8")).hexdigest()


def vet_verdict(rec: dict) -> tuple[bool, str]:
    """(discriminates, why) from the judge results (arena_judge._check_result) of the two runs: why is one of
    discriminating / passes_at_base / fails_at_fix / timeout / base_invalid. Only fix `pass` and base `fail`
    discriminates: a base run that timed out, was denied by the audit hook or lost its marker proves nothing."""
    f, b = rec.get("fix_result"), rec.get("base_result")
    if f == "error":
        return False, "timeout"
    if f != "pass":
        return False, "fails_at_fix"
    if b == "error":
        return False, "timeout"
    if b == "pass":
        return False, "passes_at_base"
    if b != "fail":
        return False, "base_invalid"
    return True, "discriminating"


def read_vet_cache(path: Path) -> dict:
    """{vet_key: record}; the last record for a key wins; a torn last line is ignored."""
    out = {}
    if Path(path).exists():
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if isinstance(r, dict) and r.get("key"):
                out[r["key"]] = r
    return out


def vet_lookup(recs: dict):
    """The census's vet callable over a read cache: a record, or None (never vetted)."""
    return lambda base, fix, path, body: recs.get(vet_key(base, fix, path, body))


def vet_jobs(pool) -> list[dict]:
    """One job per task: its base, fix, area and every fix_test (scored or not) with its cache key."""
    jobs = []
    for t, h in pool:
        cs = [{"path": c["path"], "body": c["body"], "key": vet_key(t["base_sha"], h["fix_sha"], c["path"], c["body"])}
              for c in h["checks"] if str(c.get("type", "")).startswith("fix_test")]
        if cs:
            jobs.append({"task": t["id"], "base": t["base_sha"], "fix": h["fix_sha"], "area": t.get("area") or [],
                         "checks": cs})
    return jobs


def _vet_task(job: dict, repo: Path, work: Path, timeout: int) -> list[dict]:
    """Both sides of one task, each materialised once and every check run in its own copy (run_hidden)."""
    import shutil
    import arena_judge as J            # lazy: arena_judge imports this module
    checks = [{"kind": "fix_test", "path": c["path"], "body": c["body"]} for c in job["checks"]]
    res = {}

    def run(side, reads):
        d = work / side
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
        try:
            tree = J.materialise(repo, job[side], job.get("area") or [], d / "tree", J.TREE_PATHS + tuple(reads))
            res[side] = J.run_hidden(checks, tree, d, timeout=timeout)
        except J.JudgeError as e:
            raise ArenaError("vet: %s side: %s" % (side, e))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    # ARENA_TREE_FIX_OMITS_CHECK_READ_PATHS: a check failing at the fix is traced for what it reads outside the tree;
    # the fix side is rerun and the base side run with that read set, which the judge then materialises too
    run("fix", ())
    trace = {"reads": []}
    failing = [c for c, r in zip(checks, res["fix"]) if r.get("result") != "pass"]
    if failing:
        try:
            # ARENA_VET_READS_REFUSE_FIX_CHANGED_PATHS: a read the fix changed outside the area is refused (base=)
            trace = VR.trace_reads(repo, job["fix"], job.get("area") or [], failing, work / "trace", timeout,
                                   base=job["base"])
        except J.JudgeError as e:
            raise ArenaError("vet: trace: %s" % e)
        finally:
            shutil.rmtree(work / "trace", ignore_errors=True)
        if trace["reads"]:
            run("fix", trace["reads"])
    run("base", trace["reads"])
    recs = []
    for c, fr, br in zip(job["checks"], res["fix"], res["base"]):
        recs.append({"key": c["key"], "task": job["task"], "path": c["path"], "base": job["base"], "fix": job["fix"],
                     "runner": _runner_id(), "fix_result": fr.get("result"), "base_result": br.get("result"),
                     "fix_rc": fr.get("rc"), "base_rc": br.get("rc"), "fix_tail": vet_tail(fr.get("tail")),
                     "base_tail": vet_tail(br.get("tail")), "timeout": timeout, "reads": trace["reads"],
                     **({"reads_trace": {k: trace[k] for k in ("too_wide", "refused", "rounds", "converged")}}
                        if failing else {}),
                     "at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
    return recs


def run_vet(jobs, repo: Path, workdir: Path, cache: Path, workers: int = 4, timeout: int | None = None,
            budget: float | None = None) -> dict:
    """Run every uncached check; append each finished task's records to `cache`. `timeout` is the judge's own
    CHECK_TIMEOUT (part of the runner hash in the key); only a selftest passes another. Resumable: no new task starts after
    `budget` seconds. An infrastructure error (materialise, sandbox) is reported and NOT cached: the check stays
    unvetted and its task stays out of the pool."""
    import shutil
    import tempfile
    import time
    from concurrent.futures import ThreadPoolExecutor, as_completed
    if timeout is None:
        import arena_judge as J
        timeout = J.CHECK_TIMEOUT
    t0, have = time.monotonic(), read_vet_cache(cache)
    todo = []
    for j in jobs:
        cs = [c for c in j["checks"] if c["key"] not in have]
        if cs:
            todo.append(dict(j, checks=cs))
    cached = sum(len(j["checks"]) for j in jobs) - sum(len(j["checks"]) for j in todo)
    out = {"ran": 0, "cached": cached, "left": 0, "errors": [], "seconds": 0.0}
    if not todo:
        return out
    Path(workdir).mkdir(parents=True, exist_ok=True)
    Path(cache).parent.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="vet-", dir=str(workdir)))

    def one(job):
        if budget is not None and time.monotonic() - t0 > budget:
            return job, None, "budget"
        try:
            return job, _vet_task(job, Path(repo), Path(tempfile.mkdtemp(prefix="t", dir=str(root))), timeout), None
        except Exception as e:      # noqa: BLE001  ARENA_TRACE_HARDEN_LOG_SHAPE_KILLS_VET: one candidate never
            # stops the vet; the error is reported, not cached (the check stays unvetted, its task out of the pool)
            return job, None, "%s: %s" % (type(e).__name__, str(e)[:200])

    try:
        with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
            # as each task finishes, not in submission order: one slow task (two CHECK_TIMEOUTs) must not hold every
            # later finished task's records unwritten until an outer kill loses them all
            for fut in as_completed([ex.submit(one, j) for j in todo]):
                job, recs, err = fut.result()
                if recs is None:
                    out["left"] += len(job["checks"])
                    if err != "budget":
                        out["errors"].append({"task": job["task"], "error": err})
                    continue
                with open(cache, "a", encoding="utf-8") as fh:
                    for r in recs:
                        fh.write(json.dumps(r, sort_keys=True) + "\n")
                out["ran"] += len(recs)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    out["seconds"] = round(time.monotonic() - t0, 1)
    return out


def vet_record_ok(c: dict) -> bool:
    """A scored fix_test's stored vet record is a measured discrimination (judge result pass at the fix, fail at base)."""
    v = c.get("vet")
    return (isinstance(v, dict) and v.get("fix_result") == "pass" and v.get("base_result") == "fail"
            and v.get("fix_rc") == 0 and isinstance(v.get("base_rc"), int) and not isinstance(v.get("base_rc"), bool)
            and v["base_rc"] != 0 and v.get("discriminates") is True)


# ---------------------------------------------------------------- siblings (ARENA_POOL_HARDEN_SIBLING_FIX_IN_BASE)

def base_contains(pool, repo: Path = REPO) -> dict:
    """{task id: [pool task ids whose fix commit is in this task's base]} (sorted; [] when none). Such a pair must
    never be judged in an order where the containing task comes first or alongside: its base already holds the other
    task's answer, so an arm working on the other could read it from history (see schedule_conflicts)."""
    fixes = {t["id"]: h["fix_sha"] for t, h in pool}
    bases = {t["id"]: t["base_sha"] for t, _ in pool}
    out = {tid: [] for tid in sorted(fixes)}
    on_head = {tid: _is_ancestor(repo, b, "HEAD") for tid, b in bases.items()}
    for eid, efix in sorted(fixes.items()):
        desc = set(_git(repo, "rev-list", "--ancestry-path", efix + "..HEAD").split()) | {efix}
        for lid, lb in bases.items():
            if lid != eid and (lb in desc if on_head[lid] else _is_ancestor(repo, efix, lb)):
                out[lid].append(eid)
    return {k: sorted(v) for k, v in out.items()}


def schedule_conflicts(order, contains: dict) -> list[tuple[str, str]]:
    """[(task, contained)] for every task scheduled no later than a pool task whose fix its base contains. `order` is
    a list of task ids (one per round) or a list of rounds (lists/sets of ids judged together). The contained task
    must be judged STRICTLY earlier: same round is a conflict too."""
    rnd = {}
    for i, r in enumerate(order):
        for tid in ([r] if isinstance(r, str) else list(r)):
            rnd.setdefault(tid, i)
    out = []
    for tid, i in sorted(rnd.items(), key=lambda kv: (kv[1], kv[0])):
        for other in contains.get(tid, []):
            if other in rnd and rnd[other] >= i:
                out.append((tid, other))
    return out


def check_schedule(order, contains: dict) -> None:
    """Raise TaskRefused when `order` judges a task no earlier than one whose fix its base already contains."""
    bad = schedule_conflicts(order, contains)
    if bad:
        raise TaskRefused("schedule judges %d task(s) whose base already contains another scheduled task's fix: %s"
                          % (len(bad), ", ".join("%s<-%s" % b for b in bad[:5])))


def _dump(obj) -> bytes:
    return (json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_pool(pool, p: dict, replace=()) -> dict:
    """Write task + judge files. A frozen task is never rewritten: identical content is skipped, a change refused.
    A frozen task the new census no longer picks is reported (`frozen_not_in_pool`): the CLI refuses that census,
    because the stored pool and the census would disagree. `replace` names frozen tasks whose files are rewritten
    anyway (the recovery path: they then need `refreeze --reason`, and load_frozen refuses them until it runs)."""
    for d in (p["tasks"], p["judge"]):
        d.mkdir(parents=True, exist_ok=True)
    frozen = frozen_hashes(p)
    wrote = skipped = 0
    refused = []
    for task, hidden in pool:
        hb = _dump(hidden)
        task = dict(task, hidden_checks={"held_by": "judge", "sha256": hashlib.sha256(hb).hexdigest()})
        tb = _dump(task)
        tp, hp = p["tasks"] / (task["id"] + ".json"), p["judge"] / (task["id"] + ".json")
        if task["id"] in frozen and task["id"] not in replace:
            if hashlib.sha256(tb).hexdigest() == frozen[task["id"]]["sha256"]:
                skipped += 1
            else:
                refused.append(task["id"])
            continue
        for f, b in ((hp, hb), (tp, tb)):
            if f.is_symlink():              # never write THROUGH a planted link (into an arm-writable clone)
                f.unlink()
            f.write_bytes(b)
        wrote += 1
    keep = {t["id"] for t, _ in pool}
    stale = []
    for d in (p["tasks"], p["judge"]):      # an unfrozen file the new census no longer picks is withdrawn
        for f in d.glob("*.json"):
            if f.stem not in keep and f.stem not in frozen:
                f.unlink()
                stale.append(f.stem)
    return {"wrote": wrote, "unchanged_frozen": skipped, "refused_frozen_changed": refused,
            "withdrawn_unfrozen": sorted(set(stale)), "frozen_not_in_pool": sorted(set(frozen) - keep)}


# ---------------------------------------------------------------- strict JSON

def _no_dups(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError("duplicate key %r" % k)
        out[k] = v
    return out


def _loads(raw, what="json"):
    """Strict parse: a duplicate key (a first-wins reader would see another value) is an error, not last-wins."""
    try:
        return json.loads(raw, object_pairs_hook=_no_dups)
    except (ValueError, UnicodeDecodeError) as e:
        raise TaskRefused("%s unreadable: %s" % (what, e))


def _read_jsonl(path: Path) -> list[tuple[bytes, dict]]:
    """[(line bytes, record)]. Fails closed with a clean error on a corrupt or truncated line (a final line with no
    newline is a torn write, even when its prefix happens to parse)."""
    raw = Path(path).read_bytes()
    out = []
    lines = raw.split(b"\n")
    if lines and lines[-1] == b"":
        lines.pop()
    elif lines and lines[-1]:
        raise ArenaError("%s: last line has no newline (truncated write): refusing" % path)
    for n, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line, object_pairs_hook=_no_dups)
        except (ValueError, UnicodeDecodeError) as e:
            raise ArenaError("%s line %d unreadable (corrupt or truncated): %s: refusing" % (path, n, e))
        if not isinstance(rec, dict):
            raise ArenaError("%s line %d is not a record: refusing" % (path, n))
        out.append((line, rec))
    return out


# ---------------------------------------------------------------- event log and the freeze authority

_LOCK_DEPTH = [0]


@contextlib.contextmanager
def arena_lock(p: dict):
    """One exclusive lock over the arena's logs. freeze() holds it from its assign check to its last append, so no
    assignment can land in between. EVERY writer of an arena event (assign included) must append under it."""
    if _LOCK_DEPTH[0]:
        _LOCK_DEPTH[0] += 1
        try:
            yield
        finally:
            _LOCK_DEPTH[0] -= 1
        return
    p["lock"].parent.mkdir(parents=True, exist_ok=True)
    with open(p["lock"], "a") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        _LOCK_DEPTH[0] = 1
        try:
            yield
        finally:
            _LOCK_DEPTH[0] = 0
            fcntl.flock(fh, fcntl.LOCK_UN)


def read_log(p: dict) -> list[dict]:
    """Every record of every events/*.jsonl (assign events may come from any harness writer). Strict."""
    out = []
    if not p["events"].is_dir():
        return out
    for f in sorted(p["events"].glob("*.jsonl")):
        out += [dict(rec, _file=f.name) for _, rec in _read_jsonl(f)]
    return out


_ASSIGN_KEYS = ("event", "type", "kind", "action", "name")


def _is_assign(rec: dict) -> bool:
    return any(isinstance(rec.get(k), str) and "assign" in rec[k].lower() for k in _ASSIGN_KEYS)


def assignments(p: dict) -> tuple[set, list[str]]:
    """-> (tasks with an assign-like record, problems). Looks EVERYWHERE under events/: any file name, any depth,
    any case of "assign" in event/type/kind/action/name. A record with no task assigns everything (ALL). An entry
    that is not a regular top-level *.jsonl (a subdir, a .json, a symlink) is a problem: an assign could hide in it."""
    tasks, probs = set(), []
    ev = p["events"]
    if not ev.exists():
        return tasks, probs
    for dirpath, dirnames, filenames in os.walk(ev):
        dp = Path(dirpath)
        for name in sorted(dirnames + filenames):
            fp = dp / name
            if dp == ev and name.endswith(".jsonl") and fp.is_file() and not fp.is_symlink():
                try:
                    recs = [r for _, r in _read_jsonl(fp)]
                except ArenaError as e:
                    probs.append(str(e))
                    continue
            elif fp.is_file() and not fp.is_symlink():
                probs.append("events/%s is not a top-level *.jsonl event log: unrecognised" % fp.relative_to(ev))
                raw = fp.read_bytes()
                recs = [{"event": "assign"}] if b"assign" in raw.lower() else []
            else:
                if fp.is_symlink() or not fp.is_dir():
                    probs.append("events/%s is a link or special file: unrecognised" % fp.relative_to(ev))
                elif fp.is_dir():
                    probs.append("events/%s/ is a subdirectory: unrecognised" % fp.relative_to(ev))
                continue
            for r in recs:
                if _is_assign(r):
                    tasks.add(r.get("task") if isinstance(r.get("task"), str) and r.get("task") else ALL)
    return tasks, probs


def _chain(p: dict):
    """-> (records, last line hash). The authority is hash-chained: each line carries the sha256 of the line before
    it and a sequence number, so a dropped, reordered or edited line breaks the chain and everything is refused."""
    f = p["freeze"]
    if not f.is_file():
        return [], "0" * 64
    prev, recs = "0" * 64, []
    for n, (line, rec) in enumerate(_read_jsonl(f)):
        if rec.get("prev") != prev or rec.get("seq") != n:
            raise ArenaError("%s record %d breaks the hash chain (a line was dropped, reordered or edited): "
                             "refusing every freeze" % (f, n))
        prev = hashlib.sha256(line).hexdigest()
        recs.append(rec)
    return recs, prev


def frozen_hashes(p: dict) -> dict:
    """task -> its freeze detail, read ONLY from the authority (judge/freeze.jsonl). A second freeze record for one
    task is an error, not a later or earlier winner; a `refreeze` record replaces the current freeze only when it
    names the hash it replaces and a reason; each batch record's manifest must equal the tasks frozen so far."""
    out = {}
    for rec in _chain(p)[0]:
        d = rec.get("detail") or {}
        if rec.get("task") and rec.get("event") == "refreeze":
            t = rec["task"]
            if t not in out or d.get("replaces") != out[t].get("sha256") or not str(d.get("reason") or "").strip():
                raise ArenaError("refreeze record for %s in %s does not replace its current freeze with a reason: "
                                 "refusing" % (t, p["freeze"]))
            out[t] = d
        elif rec.get("task"):
            if rec["task"] in out or rec.get("event") != "freeze":
                raise ArenaError("duplicate freeze record for %s in %s: refusing" % (rec["task"], p["freeze"]))
            out[rec["task"]] = d
        elif d.get("manifest") != {t: v.get("sha256") for t, v in out.items()}:
            raise ArenaError("freeze batch %s manifest disagrees with the task records: refusing" % rec.get("run_id"))
    return out


def _mirror_problems(p: dict, frozen: dict) -> list[str]:
    """The §1.7 event log carries a copy of every freeze. A freeze record in any other events file is forged; one in
    harness.jsonl that disagrees with the authority, or an authority freeze the log lost, is tampering."""
    probs, logged = [], {}
    auth: dict = {}
    for rec in _chain(p)[0]:
        if rec.get("task"):
            d = rec.get("detail") or {}
            auth.setdefault(rec["task"], []).append((rec.get("event"), d.get("sha256"), d.get("hidden_sha256")))
    for ev in read_log(p):
        if ev.get("event") not in ("freeze", "refreeze") or not ev.get("task"):
            continue
        t, d = ev["task"], ev.get("detail") or {}
        if ev["_file"] != p["log"].name:
            probs.append("%s: freeze record in events/%s, outside the harness log: forged" % (t, ev["_file"]))
            continue
        logged.setdefault(t, []).append((ev.get("event"), d.get("sha256"), d.get("hidden_sha256")))
    for t in sorted(set(auth) | set(logged)):
        a, g = auth.get(t, []), logged.get(t, [])
        if not g and t in frozen:
            probs.append("%s: frozen, but the event log lost its freeze record" % t)
        elif t not in frozen:
            probs.append("%s: freeze record in the event log conflicts with the authority" % t)
        elif len(g) > len(a) and g[:len(a)] == a:
            probs.append("%s: duplicate freeze record in the event log" % t)
        elif g != a:
            probs.append("%s: freeze record in the event log conflicts with the authority" % t)
    return probs


def _write_lines(path: Path, lines: list[bytes]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "ab") as fh:
        for ln in lines:
            fh.write(ln + b"\n")
        fh.flush()
        os.fsync(fh.fileno())


def _append(p: dict, recs: list[dict]):
    """Append event records to events/harness.jsonl under the arena lock."""
    with arena_lock(p):
        _write_lines(p["log"], [json.dumps(r, sort_keys=True).encode() for r in recs])


def _append_authority(p: dict, recs: list[dict]):
    with arena_lock(p):
        old, prev = _chain(p)
        lines = []
        for n, r in enumerate(recs, len(old)):
            ln = json.dumps(dict(r, seq=n, prev=prev), sort_keys=True).encode()
            prev = hashlib.sha256(ln).hexdigest()
            lines.append(ln)
        _write_lines(p["freeze"], lines)


# ---------------------------------------------------------------- validation

def live_plan_refusal(task: dict) -> str | None:
    """Why this task's `live_plan` may not run, or None. The live TestPilot plan is part of the frozen task (L3, the
    test plan is written before the build): a task with `live` other than "none" MUST carry a plan that
    testpilot.check_live_plan accepts; a `live: none` task carries `live_plan: null` (the census writes it) or, if
    frozen before the field existed, no key at all - it is never published to TestPilot, so there is nothing to run.
    An offline task carrying a plan is refused too: the plan would be silently ignored."""
    live = task.get("live", "none")
    if live == "none":
        if task.get("live_plan") is not None:
            return "live_plan given for a live: none task (it would never run): set live or drop the plan"
        return None
    if "live_plan" not in task:
        return ("live %s task has no live_plan field (frozen before the field existed?): it needs a refreeze with "
                "a TestPilot plan, never the offline proof as a stand-in" % live)
    if task["live_plan"] is None:
        return "live %s task has live_plan null: a live task needs a TestPilot plan (L3)" % live
    import testpilot as TP                  # the consumer owns the schema; lazy: testpilot imports the lane stack
    try:
        TP.check_live_plan(task["live_plan"])
    except TP.PilotRefused as e:
        return "live_plan invalid: %s" % e
    except (TypeError, AttributeError, KeyError) as e:   # a shape the validator missed still refuses, never crashes
        return "live_plan malformed (%s: %s)" % (type(e).__name__, e)
    return None


def validate_task(task: dict, hidden_path: Path, p: dict, hidden_bytes: bytes | None = None):
    """Refuse a task spec the trial may not run. Raises TaskRefused."""
    tid = task.get("id")
    for k in ("id", "source_item", "kind", "size", "area", "prompt", "criteria", "proof", "live", "base_sha"):
        if task.get(k) in (None, "", []):
            raise TaskRefused("%s: field %s missing" % (tid, k))
    if not isinstance(task["live"], str) or task["live"] not in LIVE_OK:
        raise TaskRefused("%s: live %r refused: the trial runs on the minimal list only (owner 2026-10-29); "
                          "allowed %s" % (tid, task["live"], ", ".join(LIVE_OK)))
    bad = live_plan_refusal(task)
    if bad:
        raise TaskRefused("%s: %s" % (tid, bad))
    if task["kind"] not in KINDS:
        raise TaskRefused("%s: kind %r unknown" % (tid, task["kind"]))
    if type(task["size"]) is not int or task["size"] not in (1, 2, 4):     # True == 1, so test the type
        raise TaskRefused("%s: size %r is not the integer 1, 2 or 4" % (tid, task["size"]))
    hc = task.get("hidden_checks")
    if not isinstance(hc, dict) or set(hc) != {"held_by", "sha256"}:
        raise TaskRefused("%s: hidden_checks must be only a {held_by, sha256} stub; the checks live in the "
                          "judge's directory" % tid)
    if any(k in task for k in HIDDEN_KEYS):
        raise TaskRefused("%s: judge-only key in an arm-readable task file" % tid)
    if hidden_bytes is None:
        if not hidden_path.is_file():
            raise TaskRefused("%s: judge file missing" % tid)
        hidden_bytes = hidden_path.read_bytes()
    if hashlib.sha256(hidden_bytes).hexdigest() != hc["sha256"]:
        raise TaskRefused("%s: judge file changed since the task was written" % tid)


# ---------------------------------------------------------------- leak scan

_WS = re.compile(r"\s+")
_HEX = re.compile(r"(?<![0-9a-f])[0-9a-f]{7,40}(?![0-9a-f])")
_SLASH = re.compile(r"[\\/]+")
_B64 = re.compile(r"(?:[A-Za-z0-9+/]{4}\s?){4,}(?:[A-Za-z0-9+/]{2,3}={0,2})?|[A-Za-z0-9_-]{16,}")
_JESC = re.compile(r'\\(u[0-9a-fA-F]{4}|["\\/bfnrt])')
_JMAP = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", '"': '"', "\\": "\\", "/": "/"}


def _norm(s: str) -> str:
    return _WS.sub(" ", s.lower()).strip()


def _unescape(s: str) -> str:
    return _JESC.sub(lambda m: chr(int(m.group(1)[1:], 16)) if m.group(1)[0] == "u" else _JMAP[m.group(1)], s)


_UNPACK_CAP = 8 * 1024 * 1024          # decoded bytes per container; a bomb is truncated here, never expanded


def _capped(dec_factory, raw: bytes) -> bytes | None:
    """One bounded decompress call (max_length): never more than _UNPACK_CAP bytes come out, whatever the ratio."""
    try:
        b = dec_factory().decompress(raw, _UNPACK_CAP)
        return b or None
    except (OSError, EOFError, ValueError, zlib.error, lzma.LZMAError):
        return None


def _unpack(raw: bytes) -> list[bytes]:
    """The payloads of gzip / zlib / bz2 / xz-lzma / zip containers in `raw` (each capped at _UNPACK_CAP)."""
    got = []
    if raw[:2] == b"\x1f\x8b":
        got.append(_capped(lambda: zlib.decompressobj(31), raw))
    if raw[:1] == b"\x78":
        got.append(_capped(lambda: zlib.decompressobj(15), raw))
    if raw[:3] == b"BZh":
        got.append(_capped(bz2.BZ2Decompressor, raw))
    if raw[:6] == b"\xfd7zXZ\x00" or raw[:1] == b"\x5d":
        got.append(_capped(lambda: lzma.LZMADecompressor(), raw))
    if raw[:2] == b"PK":
        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                budget = _UNPACK_CAP
                for zi in z.infolist()[:256]:
                    if zi.is_dir() or budget <= 0:
                        continue
                    with z.open(zi) as f:
                        b = f.read(min(budget, _UNPACK_CAP) + 1)[:budget]
                    budget -= len(b)
                    got.append(b)
        except (zipfile.BadZipFile, OSError, EOFError, ValueError, zlib.error, lzma.LZMAError, NotImplementedError,
                RuntimeError):
            pass
    return [g for g in got if g]


def _decodings(raw: bytes, _depth: int = 0) -> list[str]:
    """Every text an arm could recover from these bytes without a key: UTF-8, UTF-16 (either byte order, either
    alignment), JSON/string escapes (two levels), base64 runs (standard and urlsafe, wrapped or not), and the
    payload of a gzip / zlib / bz2 / xz / zip container (8 MiB cap, bomb-safe), recursively (3 levels), so a gzip of
    base64 or a base64 of a gzip is read too."""
    out = [raw.decode("utf-8", "replace")]
    if _depth < 3:
        for b in _unpack(raw):
            out += _decodings(b, _depth + 1)
    if b"\x00" in raw[:65536] or raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        for off in (0, 1):
            for enc in ("utf-16-le", "utf-16-be"):
                out.append(raw[off:].decode(enc, "replace"))
    for t in list(out):
        if "\\" in t:
            u = _unescape(t)
            out.append(u)
            if "\\" in u:
                out.append(_unescape(u))
    for t in list(out):
        for m in _B64.finditer(t):
            run = re.sub(r"\s", "", m.group(0)).replace("-", "+").replace("_", "/")
            for off in range(4):
                s = run[off:]
                s = s[:len(s) - len(s) % 4] if not s.endswith("=") else s
                try:
                    b = base64.b64decode(s, validate=True)
                except (binascii.Error, ValueError):
                    continue
                if b"\x00" in b:
                    out += [b.decode("utf-16-le", "replace"), b.decode("utf-16-be", "replace")]
                out.append(b.decode("utf-8", "replace"))
                if _depth < 3:
                    for u in _unpack(b):
                        out += _decodings(u, _depth + 1)
    return out


def _anchors(block: str) -> list[str]:
    """Aligned ANCHOR-char pieces of a normalised block: any 2*ANCHOR-char window of the block contains one. Pure
    import/shebang boilerplate is dropped (every selftest an arm writes starts with it)."""
    nb = _norm(block)
    if len(nb) < 2 * ANCHOR:
        return [nb] if len(nb) >= SHORT_BODY else []
    out = []
    for i in range(0, len(nb) - ANCHOR + 1, ANCHOR):
        a = nb[i:i + ANCHOR]
        if a.count("import ") >= 2 or a.startswith("#!") or not re.search(r"[a-z]{3}", a):
            continue
        out.append(a)
    return out


def _hidden_shas(h: dict) -> list[str]:
    out = [h.get("fix_sha")] + [r.get("fix_sha") for r in h.get("reworks", [])]
    return [s.lower() for s in out if s]


def _hidden_tests(h: dict):
    for c in h.get("checks", []):
        if c.get("body") is not None or c.get("path"):
            yield c
    for r in h.get("reworks", []):
        yield from r.get("tests", [])


def hidden_objects(h: dict) -> set:
    """git object ids that must not exist in any arm clone: the fix and rework commits, and every hidden test blob."""
    out = set(_hidden_shas(h))
    for t in _hidden_tests(h):
        if t.get("blob"):
            out.add(t["blob"].lower())
        elif t.get("body"):
            b = t["body"].encode("utf-8")
            out.add(hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest())
    return out


def _typed_tokens(hidden: dict):
    """-> (shas, literals, anchors). Literals (ids, added test paths) match the lowercased, slash-normalised text;
    anchors (normalised novel test text) match the whitespace-collapsed text."""
    shas = _hidden_shas(hidden)
    lits = [r["item"].lower() for r in hidden.get("reworks", [])] + [x.lower() for x in hidden.get("label_pending", [])]
    anchors = []
    for t in _hidden_tests(hidden):
        if t.get("added") and t.get("path"):
            lits.append(_SLASH.sub("/", t["path"].lower()))
        for blk in (t.get("novel") if t.get("novel") is not None else [t.get("body") or ""]):
            anchors += _anchors(blk)
    return shas, [x for x in lits if x], [x for x in anchors if x]


def _path_lits(hidden: dict) -> set:
    return {_SLASH.sub("/", t["path"].lower()) for t in _hidden_tests(hidden) if t.get("added") and t.get("path")}


def leak_tokens(hidden: dict) -> list[str]:
    """Literal tokens (lowercase) whose presence on an arm-readable path means a hidden check leaked: the fix and
    rework shas (any 7-40 char prefix counts), rework and pending-rework ids, the path of every test the fix or a
    rework ADDED (one it changed was visible at base), and each normalised novel body anchor."""
    a, b, c = _typed_tokens(hidden)
    return a + b + c


class Matcher:
    """Hidden-check matcher over raw bytes: case-insensitive, sha prefixes of 7-40 hex, either slash direction,
    normalised whitespace, every decoding _decodings finds."""

    def __init__(self, hiddens, no_paths=()):
        """`no_paths`: tasks already handed to an arm, whose ADDED-test path literal is not matched (the arm naming
        the file it writes is its own work, FP1/FP2); their shas, rework ids and test-text anchors still match."""
        self.sha7, self.lits, self.anchors = {}, [], []
        for h in hiddens:
            self.add(h, paths=(h.get("task") or "?") not in no_paths and ALL not in no_paths)

    def add(self, h: dict, paths=True):
        owner = h.get("task") or "?"
        shas, lits, anchors = _typed_tokens(h)
        if not paths:
            drop = _path_lits(h)
            lits = [t for t in lits if t not in drop]
        for s in set(shas):
            self.sha7.setdefault(s[:7], []).append((s, owner))
        self.lits += [(t, owner) for t in lits]
        self.anchors += [(t, owner) for t in anchors]

    def __bool__(self):
        return bool(self.sha7 or self.lits or self.anchors)

    def hits(self, raw: bytes, skip_shas=()) -> list[tuple[str, str]]:
        """[(owner, what)] - at most one hit per owner."""
        found = {}
        for text in _decodings(raw):
            low = text.lower()
            for m in _HEX.finditer(low):
                run = m.group(0)
                for s, owner in self.sha7.get(run[:7], ()):
                    if s.startswith(run) and s not in skip_shas:
                        found.setdefault(owner, "fix/rework sha %s" % run)
            pn = _SLASH.sub("/", low)
            for t, owner in self.lits:
                if owner not in found and t in pn:
                    found.setdefault(owner, "token %r" % t[:60])
            nt = _norm(text)
            for t, owner in self.anchors:
                if owner not in found and t in nt:
                    found.setdefault(owner, "hidden test text %r" % t[:40])
        return sorted(found.items())


def _scan_file(fp: Path, matcher: Matcher, skip_shas=(), strip_base=False) -> list[tuple[str, str]]:
    """Whole file, in overlapping SCAN_CHUNK pieces when large: no size is skipped. `strip_base` (a task spec in
    <arena>/tasks itself, nowhere else) blanks its own base_sha field: starting where an earlier fix landed is
    history."""
    out = {}
    with open(fp, "rb") as fh:
        pos = 0
        while True:
            fh.seek(max(pos - SCAN_OVERLAP, 0))
            raw = fh.read(SCAN_CHUNK + (SCAN_OVERLAP if pos else 0))
            if not raw:
                break
            if strip_base and pos == 0:
                raw = _BASE_FIELD.sub(b'"base_sha": null', raw)
            for owner, what in matcher.hits(raw, skip_shas):
                out.setdefault(owner, what)
            pos += SCAN_CHUNK
            if len(raw) < SCAN_CHUNK:
                break
    return sorted(out.items())


# ---------------------------------------------------------------- clone registry (harness-owned, judge dir)

def _reg_paths(p: dict) -> tuple[Path, Path]:
    j = p["freeze"].parent
    return j / "clones.jsonl", j / "clones"


def clone_registry(p: dict) -> dict:
    """realpath -> its LAST build record. Lives in the judge dir: an arm can neither read nor forge it."""
    reg = _reg_paths(p)[0]
    out = {}
    if reg.is_file():
        for _, rec in _read_jsonl(reg):
            if isinstance(rec.get("path"), str):
                out[rec["path"]] = rec
    return out


def _load_manifest(p: dict, rec: dict) -> dict:
    mp = _reg_paths(p)[1] / ("%s.json" % rec.get("nonce"))
    raw = mp.read_bytes()
    if hashlib.sha256(raw).hexdigest() != rec.get("manifest_sha256"):
        raise ArenaError("manifest %s does not match its registry hash" % mp)
    return _loads(raw, str(mp))


def _sha256_path(fp: Path) -> str:
    h = hashlib.sha256()
    with open(fp, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def _sig(st) -> list:
    # ctime cannot be set from user space: equal (inode, size, mtime, ctime) means the bytes were not rewritten
    return [st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns]


def _entries(top: Path) -> tuple[dict, list[str]]:
    """({relpath: lstat} of every path under top, links never followed, .git included), [unreadable dirs]."""
    out, errs = {}, []
    for dirpath, dirnames, filenames in os.walk(top, onerror=lambda e: errs.append("%s (%s)" % (e.filename, e))):
        dp = Path(dirpath)
        for n in dirnames + filenames:
            fp = dp / n
            try:
                out[str(fp.relative_to(top))] = os.lstat(fp)
            except OSError as e:
                errs.append("%s (%s)" % (fp, e))
    return out, errs


def _kind(st) -> str:
    return "l" if stat.S_ISLNK(st.st_mode) else "d" if stat.S_ISDIR(st.st_mode) else \
        "f" if stat.S_ISREG(st.st_mode) else "?"


def _describe(fp: Path, st) -> dict:
    k = _kind(st)
    if k == "l":
        return {"t": "l", "to": os.readlink(fp)}
    if k == "f":
        return {"t": "f", "x": bool(st.st_mode & 0o111), "sha256": _sha256_path(fp), "stat": _sig(st)}
    return {"t": k}


def _deviations(top: Path, entries: dict) -> tuple[list, list, list, dict, list]:
    """-> (new, changed, missing, current lstat, unreadable) against a build manifest's entries."""
    cur, errs = _entries(top)
    new, changed = [], []
    for rel, st in sorted(cur.items()):
        e = entries.get(rel)
        if e is None:
            new.append(rel)
            continue
        k = _kind(st)
        try:
            if e.get("t") != k or (k == "l" and os.readlink(top / rel) != e.get("to")):
                changed.append(rel)
            elif k == "f" and _sig(st) != e.get("stat") and (
                    bool(st.st_mode & 0o111) != e.get("x") or _sha256_path(top / rel) != e.get("sha256")):
                changed.append(rel)
        except OSError as ex:
            errs.append("%s (%s)" % (top / rel, ex))
    return new, changed, sorted(set(entries) - set(cur)), cur, errs


def _git_in(gitdir: Path, *args, inp: bytes | None = None) -> bytes:
    """git against an ARM-controlled git dir: arena_safe_git's pins (no replace refs/grafts: a replace ref would make
    `cat-file --batch` show other content than the object holds; no hooks, no fsmonitor, no global/system config)."""
    r = subprocess.run(["git"] + SG.GIT_SAFE_CFG + ["--git-dir", str(gitdir), *args], input=inp, capture_output=True,
                       timeout=300, env=dict(SG.safe_env(), GIT_OPTIONAL_LOCKS="0"))
    if r.returncode != 0:
        raise ArenaError("git %s in %s: %s" % (args[0], gitdir, r.stderr.decode("utf-8", "replace").strip()[:200]))
    return r.stdout


def _objects(gitdir: Path) -> dict:
    out = {}
    for ln in _git_in(gitdir, "cat-file", "--batch-all-objects", "--unordered",
                      "--batch-check=%(objectname) %(objecttype)").decode().splitlines():
        o, _, t = ln.partition(" ")
        out[o] = t
    return out


def _present(repo, ids) -> list[str]:
    """The ids that exist in `repo` (a source or old-history repo)."""
    ids = sorted(ids)
    if not ids or not repo or not Path(repo).exists():
        return []
    r = subprocess.run(["git", "-C", str(repo), "cat-file", "--batch-check"], input="\n".join(ids) + "\n",
                       capture_output=True, text=True, timeout=300)
    return [o for o, ln in zip(ids, r.stdout.splitlines()) if not ln.endswith(" missing")]


def _cat_batch(gitdir: Path, ids):
    """Yield (id, type, content) for each object."""
    ids = sorted(ids)
    if not ids:
        return
    raw = _git_in(gitdir, "cat-file", "--batch", inp=("\n".join(ids) + "\n").encode())
    pos = 0
    while pos < len(raw):
        nl = raw.index(b"\n", pos)
        head = raw[pos:nl].decode().split()
        if len(head) < 3:                   # "<id> missing"
            pos = nl + 1
            continue
        size = int(head[2])
        yield head[0], head[1], raw[nl + 1:nl + 1 + size]
        pos = nl + 1 + size + 1


class _Ctx:
    """What one leak scan knows: the judge's hidden checks, matchers, inodes, the assignment state."""

    def __init__(self, p: dict):
        self.p = p
        self.out: list[tuple[str, str]] = []
        self.judge_root = p["freeze"].parent
        self.hiddens, self.objs, self.inodes = [], {}, set()
        for d in {p["judge"], self.judge_root}:
            for f in d.glob("*") if d.is_dir() else []:
                if f.is_file():
                    st = os.stat(f)
                    self.inodes.add((st.st_dev, st.st_ino))
        for hf in sorted(p["judge"].glob("*.json")) if p["judge"].is_dir() else []:
            try:
                h = _loads(hf.read_bytes(), str(hf))
            except (OSError, ArenaError) as e:
                self.add(ALL, "judge file %s unreadable: %s" % (hf, e))
                continue
            h.setdefault("task", hf.stem)
            self.hiddens.append(h)
            for o in hidden_objects(h):
                self.objs.setdefault(o, h["task"])
        try:
            self.assigned, _ = assignments(p)
        except (ArenaError, OSError):
            self.assigned = set()           # unreadable: every clone is held to the strict (pre-assign) check
        self.strict = Matcher(self.hiddens)
        self.loose = Matcher(self.hiddens, no_paths=self.assigned)
        self.roots = arm_readable_roots(p)
        self.real_roots = [os.path.realpath(r) for r in self.roots]

    def add(self, scope, msg):
        self.out.append((scope, msg))

    def outside(self, target: str) -> bool:
        return not any(target == q or target.startswith(q.rstrip("/") + "/") for q in self.real_roots)

    def into_judge(self, target: str) -> bool:
        return _inside(Path(target), self.judge_root) or _inside(Path(target), self.p["judge"])

    def scan(self, fp: Path, matcher: Matcher, strip_base=False, where=None):
        try:
            for owner, what in _scan_file(fp, matcher, strip_base=strip_base):
                self.add(owner, "%s: hidden check of %s readable at %s (%s)" % (owner, owner, where or fp, what))
        except OSError as e:
            self.add(ALL, "%s: unreadable by the scan (%s): not verified" % (fp, e))

    def scan_bytes(self, raw: bytes, matcher: Matcher, where: str):
        for owner, what in matcher.hits(raw):
            self.add(owner, "%s: hidden check of %s readable at %s (%s)" % (owner, owner, where, what))

    def link_or_hardlink(self, fp: Path, st) -> bool:
        """Flag a link into the judge or out of the arm-readable roots, or a hard link to a judge file. True when
        the entry is a link (never followed)."""
        if stat.S_ISLNK(st.st_mode):
            tgt = os.path.realpath(fp)
            if self.into_judge(tgt):
                self.add(ALL, "symlink %s -> %s points into the judge directory" % (fp, os.readlink(fp)))
            elif self.outside(tgt):
                self.add(ALL, "symlink %s -> %s resolves outside the arm-readable roots" % (fp, os.readlink(fp)))
            return True
        if stat.S_ISREG(st.st_mode) and (st.st_dev, st.st_ino) in self.inodes:
            self.add(ALL, "%s is a hard link to a judge file" % fp)
        return False


def _clone_findings(cx: _Ctx, top: Path, rec: dict):
    """Re-prove one registered clone against its build manifest (see the module docstring)."""
    task = rec.get("task") or ALL
    post = task in cx.assigned or ALL in cx.assigned
    try:
        man = _load_manifest(cx.p, rec)
    except (OSError, ArenaError) as e:
        cx.add(ALL, "%s: build manifest unusable (%s): the clone is unverified" % (top, e))
        return
    new, changed, missing, cur, errs = _deviations(top, man.get("entries") or {})
    for e in errs:
        cx.add(ALL, "%s: unreadable by the check (%s): not verified" % (top, e))
    dev = new + changed
    if not post and (dev or missing):
        eg = (dev + missing)[:3]
        cx.add(task, "%s: clone of %s (not yet assigned) is not its build: %d new, %d changed, %d missing path(s) "
                     "(e.g. %s)" % (top, task, len(new), len(changed), len(missing), ", ".join(eg)))
    if task != ALL:
        tf = cx.p["tasks"] / (task + ".json")
        try:
            tb = _loads(tf.read_bytes(), str(tf)).get("base_sha") if tf.is_file() else None
        except (OSError, ArenaError):
            tb = None
        if tb and not str(rec.get("base_sha") or "").startswith(str(tb)):
            cx.add(task, "%s: built at %s, but task %s starts at base_sha %s" % (top, str(rec.get("base_sha"))[:12],
                                                                               task, str(tb)[:12]))
    for o in sorted(set(man.get("objects") or []) & set(cx.objs)):
        # a clone BUILT at a later commit (or at a base holding another pool task's fix) carries hidden objects
        cx.add(cx.objs[o], "%s: hidden check of %s readable at %s (git object %s in its build)"
               % (cx.objs[o], cx.objs[o], top, o[:12]))
    for rel, st in cur.items():
        if stat.S_ISLNK(st.st_mode) and rel not in dev and cx.into_judge(os.path.realpath(top / rel)):
            cx.add(ALL, "symlink %s -> %s points into the judge directory" % (top / rel, os.readlink(top / rel)))
    gd = top / ".git"
    if os.path.islink(gd) or not gd.is_dir():
        cx.add(ALL, "%s: .git is not the directory the harness built (a gitfile or link borrows a repository)" % top)
    for rel in dev:
        fp, st = top / rel, cur[rel]
        parts = Path(rel).parts
        if parts[-1] == ".git" and rel != ".git":
            cx.add(ALL, "%s: nested repository %s (could hold any history)" % (top, rel))
        if parts[0] == ".git" and len(parts) >= 2 and parts[1] in ("worktrees", "modules", "commondir"):
            cx.add(ALL, "%s: %s links another worktree or submodule repository" % (top, "/".join(parts[:2])))
        if rel in (".git/objects/info/alternates", ".git/objects/info/http-alternates"):
            cx.add(ALL, "%s: borrows objects via alternates (the full history is readable)" % top)
        if parts[-1] in ("HEAD", "objects", "refs", "packed-refs") and len(parts) > 1 and parts[:-1] != (".git",):
            par = fp.parent
            if (par / "objects").is_dir() and (par / "HEAD").exists():
                cx.add(ALL, "%s: nested object store %s (a bare repository: any history)" % (top, par))
        if cx.link_or_hardlink(fp, st):
            continue
        if _kind(st) == "?":
            cx.add(task, "%s: special file %s" % (top, rel))
    # names: a body carried in file or directory names
    m = cx.loose if post else cx.strict
    if dev:
        cx.scan_bytes("\n".join(dev).encode(), m, "%s (new or changed path names)" % top)
    for rel in dev:
        if _kind(cur[rel]) == "f":
            cx.scan(top / rel, m)
    if not any(r == ".git" or r.startswith(".git/") for r in dev + missing):
        return                              # the object store is byte-identical to the verified build
    try:
        objs = _objects(gd)
    except ArenaError as e:
        cx.add(ALL, "%s: object store unreadable (%s): not verified" % (top, e))
        return
    expected = set(man.get("objects") or [])
    unexpected = {o: t for o, t in objs.items() if o not in expected}
    for o in sorted(set(objs) & set(cx.objs)):
        cx.add(cx.objs[o], "%s: hidden check of %s readable at %s (git object %s present)"
               % (cx.objs[o], cx.objs[o], top, o[:12]))
    hist = [o for o, t in unexpected.items() if t in ("commit", "tag")]
    for repo in (rec.get("source"), *old_history_repos()):
        got = _present(repo, hist)
        if got:
            cx.add(ALL, "%s: holds %d commit/tag object(s) of %s besides base_sha (e.g. %s): its history is readable"
                   % (top, len(got), repo, got[0][:12]))
    try:
        for o, t, data in _cat_batch(gd, [o for o, t in unexpected.items() if t in ("commit", "tag", "blob")]):
            cx.scan_bytes(data, m, "%s (git %s %s)" % (top, t, o[:12]))
    except (ArenaError, ValueError) as e:
        cx.add(ALL, "%s: object store unreadable (%s): not verified" % (top, e))


# The harness's OWN directories at the top of the clone root (ARENA_FREEZE_FIX_HARNESS_DIRS_REFUSED): each has a
# named writer, and each is exempt from the whitelist ONLY while arm_sandbox's policy hides it from every arm.
HARNESS_DIRS = {
    "judge": "arena_judge work dir ($ARENA_JUDGE_WORK default): masked by arm_sandbox.deny_paths",
    "locks": "arena_replay run locks: masked by arm_sandbox.deny_paths",
    "sandbox": "arm_sandbox.scratch_dir base: /home is a tmpfs in the sandbox and only the arm's own scratch is bound",
}


def _harness_dir_masked(name: str, full: str) -> str | None:
    """Why a top-level directory under the clone root is unreachable by any arm, or None (then it is a finding).
    A HARNESS_DIRS entry counts only when the live sandbox policy agrees: it is in arm_sandbox.deny_paths(), or it
    is the sandbox scratch base. Any error reading the policy, a root the sandbox does not treat as the arena root
    (RM_ARENA_ROOT vs ARENA_CLONES), or a name not listed: None (fail closed)."""
    if name not in HARNESS_DIRS or os.path.islink(full) or not os.path.isdir(full):
        return None
    try:
        import arm_sandbox as SB
        import arena_replay as R
        real = os.path.realpath(full)
        if real in {os.path.realpath(x) for x in SB.deny_paths()}:
            return HARNESS_DIRS[name]
        base = os.environ.get("RM_ARM_SANDBOX_SCRATCH") or str(R.arena_root() / "sandbox")
        if name == "sandbox" and real == os.path.realpath(base) and "sandbox" in SB.ARENA_KEEP \
                and any(_inside(Path(real), Path(c)) for c in SB.CONTAINERS):
            return HARNESS_DIRS[name]
    except Exception:                    # noqa: BLE001 - the policy could not be read: not exempt
        return None
    return None


def _is_empty_dir(full: str) -> bool:
    try:
        return not os.listdir(full)
    except OSError:                      # unreadable: not known empty, so it stays a finding
        return False


def _clone_root_findings(cx: _Ctx, root: Path):
    """Every entry under the clone root must be a registered clone, a directory leading to one, a harness directory
    the arm sandbox masks (HARNESS_DIRS, top level only), or an empty directory whose name is token-scanned."""
    reg = {k: v for k, v in clone_registry(cx.p).items()}
    rr = os.path.realpath(root)
    live = {k: v for k, v in reg.items() if k.startswith(rr.rstrip("/") + "/") and os.path.isdir(k)}
    anc = set()
    for k in live:
        q = os.path.dirname(k)
        while q.startswith(rr.rstrip("/") + "/"):
            anc.add(q)
            q = os.path.dirname(q)
    for dirpath, dirnames, filenames in os.walk(rr, onerror=lambda e: cx.add(
            ALL, "%s: unreadable by the check (%s): not verified" % (e.filename, e))):
        keep = []
        for n in sorted(dirnames):
            full = os.path.join(dirpath, n)
            if os.path.islink(full):
                cx.link_or_hardlink(Path(full), os.lstat(full))
                cx.add(ALL, "%s: unregistered link under the clone root" % full)
            elif full in live:
                _clone_findings(cx, Path(full), live[full])
            elif full in anc:
                keep.append(n)
            elif dirpath == rr and _harness_dir_masked(n, full):
                pass                     # the harness's own dir, hidden from every arm by the sandbox: not walked
            elif _is_empty_dir(full):
                cx.scan_bytes(n.encode("utf-8", "surrogateescape"), cx.strict, "directory name " + full)
            else:
                cx.add(ALL, "%s: unregistered directory under the clone root (not built by build_arm_clone): "
                            "unverified" % full)
        for n in sorted(filenames):
            full = Path(dirpath) / n
            cx.link_or_hardlink(full, os.lstat(full))
            cx.add(ALL, "%s: unregistered file under the clone root: unverified" % full)
        dirnames[:] = keep


def _plain_root_findings(cx: _Ctx, root: Path, tasks_dir: bool):
    """The task specs (a whitelist: regular top-level *.json only) and the event log (token-scanned)."""
    for dirpath, dirnames, filenames in os.walk(root, onerror=lambda e: cx.add(
            ALL, "%s: unreadable by the check (%s): not verified" % (e.filename, e))):
        dp = Path(dirpath)
        for n in sorted(dirnames):
            fp = dp / n
            if os.path.islink(fp):
                cx.link_or_hardlink(fp, os.lstat(fp))
                if tasks_dir:
                    cx.add(ALL, "%s: link in the task specs dir" % fp)
            elif tasks_dir:
                cx.add(ALL, "%s: subdirectory in the task specs dir: unverified" % fp)
        if tasks_dir:
            dirnames[:] = []
        for n in sorted(filenames):
            fp = dp / n
            try:
                st = os.lstat(fp)
            except OSError as e:
                cx.add(ALL, "%s: unreadable by the scan (%s): not verified" % (fp, e))
                continue
            if cx.link_or_hardlink(fp, st):
                if tasks_dir:
                    cx.add(ALL, "%s: link in the task specs dir" % fp)
                continue
            if tasks_dir and not (n.endswith(".json") and stat.S_ISREG(st.st_mode)):
                cx.add(ALL, "%s: not a task spec (the task dir holds regular *.json only)" % fp)
            if stat.S_ISREG(st.st_mode):
                cx.scan(fp, cx.strict if tasks_dir else cx.loose, strip_base=tasks_dir)


def scoped_leaks(p: dict) -> list[tuple[str, str]]:
    """[(scope, message)]: scope is the task whose hidden check is exposed, or ALL. See the module docstring."""
    cx = _Ctx(p)
    roots = cx.roots
    for r in roots:
        for j in (p["judge"], cx.judge_root):
            if _inside(j, r):
                cx.add(ALL, "judge directory %s is inside arm-readable %s" % (j, r))
    tasks, events, clones = roots
    if tasks.is_symlink() or events.is_symlink():
        cx.add(ALL, "an arm-readable arena dir is a link: unverified")
    if tasks.is_dir():
        _plain_root_findings(cx, tasks, True)
    if events.is_dir():
        _plain_root_findings(cx, events, False)
    if clones.is_dir():
        _clone_root_findings(cx, clones)
    seen, out = set(), []
    for s, m in cx.out:
        if (s, m) not in seen:
            seen.add((s, m))
            out.append((s, m))
    return out


def find_leaks(p: dict, task: str | None = None) -> list[str]:
    """Leak messages, each prefixed with its scope. With `task`, only those that refuse that task (its own scope
    or ALL): one arm's note about its own test blocks its own task, never every task."""
    return ["[%s] %s" % (s, m) for s, m in scoped_leaks(p) if task is None or s in (task, ALL)]


# ---------------------------------------------------------------- arm clones

def _git_blob_id(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def build_arm_clone(base_sha: str, dest: Path, src: Path = REPO, task: str | None = None, p: dict | None = None,
                    extra_files: dict | None = None) -> Path:
    """The only sanctioned arm clone: `git init --template=` (no hooks), a depth-1 fetch of base_sha, checked out
    detached, FETCH_HEAD removed, then any harness-written `extra_files` ({relpath: bytes|str}, e.g. AGENTS.md).
    Verified before it is registered: its object store is exactly `rev-list --objects -n1 base_sha` of the source,
    its work tree is exactly `ls-tree -r base_sha` (blob ids recomputed) plus the extra files, there are no refs,
    tags, alternates or other repositories. The manifest of every path goes to the judge dir; nothing is written
    into the clone's .git. A clone that fails verification is left unregistered (every check then refuses it:
    remove it)."""
    p = p or paths()
    dest = Path(dest)
    if dest.is_symlink() or (dest.exists() and any(dest.iterdir())):
        raise ArenaError("%s is not empty" % dest)
    full = _resolve(Path(src), base_sha)
    if not full:
        raise ArenaError("base_sha %s does not resolve in %s" % (base_sha, src))
    srcr = str(Path(src).resolve())
    extra = {k: (v.encode("utf-8") if isinstance(v, str) else bytes(v)) for k, v in (extra_files or {}).items()}
    for k in extra:
        if os.path.isabs(k) or ".." in Path(k).parts or Path(k).parts[:1] == (".git",):
            raise ArenaError("extra file %r escapes the work tree" % k)
    cx = _Ctx(p)
    for k, v in extra.items():
        hits = cx.strict.hits(v)
        if hits:
            raise ArenaError("extra file %s carries a hidden check of %s" % (k, hits[0][0]))
    dest.mkdir(parents=True, exist_ok=True)
    _git(dest, "init", "-q", "--template=")
    r = subprocess.run(["git", "-C", str(dest), "fetch", "-q", "--depth", "1", "--no-tags", "file://" + srcr, full],
                       capture_output=True, text=True, timeout=540)
    if r.returncode != 0:
        raise ArenaError("fetch %s: %s" % (full[:12], r.stderr.strip()[:200]))
    # a full-tree checkout of the real repo outlasts _git's 60 s (probe CONTROL2 on drvfs), so it gets fetch's bound
    r = subprocess.run(["git", "-C", str(dest), "-c", "advice.detachedHead=false", "checkout", "-q", "--detach", full],
                       capture_output=True, text=True, timeout=540)
    if r.returncode != 0:
        raise ArenaError("checkout %s: %s" % (full[:12], r.stderr.strip()[:200]))
    gd = dest / ".git"
    (gd / "FETCH_HEAD").unlink(missing_ok=True)
    for k, v in extra.items():
        (dest / k).parent.mkdir(parents=True, exist_ok=True)
        if (dest / k).is_symlink():
            (dest / k).unlink()
        (dest / k).write_bytes(v)
    # ---- verify: objects
    want = {ln.split()[0] for ln in _git(Path(src), "rev-list", "--objects", "-n1", full).splitlines() if ln.strip()}
    got = _objects(gd)
    if set(got) != want:
        raise ArenaError("clone %s: object store is not exactly base_sha's objects (%d extra, %d missing)"
                         % (dest, len(set(got) - want), len(want - set(got))))
    if (gd / "HEAD").read_text().strip() != full:
        raise ArenaError("clone %s: HEAD is not detached at %s" % (dest, full[:12]))
    for bad in ("packed-refs", "objects/info/alternates", "objects/info/http-alternates", "hooks", "worktrees",
                "modules", "commondir"):
        if (gd / bad).exists():
            raise ArenaError("clone %s: .git/%s exists" % (dest, bad))
    refs = [str(f) for f in (gd / "refs").rglob("*") if f.is_file()] if (gd / "refs").is_dir() else []
    if refs:
        raise ArenaError("clone %s: refs present (%s)" % (dest, refs[0]))
    # ---- verify: work tree == ls-tree -r base_sha (+ extra files)
    tree = {}
    for ln in _git(Path(src), "ls-tree", "-r", "-z", full).split("\0"):
        if ln:
            meta, path = ln.split("\t", 1)
            mode, typ, oid = meta.split()
            tree[path] = (mode, typ, oid)
    ents, errs = _entries(dest)
    if errs:
        raise ArenaError("clone %s: unreadable while verifying: %s" % (dest, errs[0]))
    files = {rel for rel, st in ents.items() if rel != ".git" and not rel.startswith(".git/")
             and _kind(st) != "d"}
    if files != set(tree) | set(extra):
        raise ArenaError("clone %s: work tree is not base_sha's file list (%d extra, %d missing)"
                         % (dest, len(files - set(tree) - set(extra)), len(set(tree) - files)))
    for path, (mode, typ, oid) in tree.items():
        if path in extra:
            continue
        fp = dest / path
        data = os.readlink(fp).encode() if mode == "120000" else fp.read_bytes()
        if typ != "blob" or _git_blob_id(data) != oid:
            raise ArenaError("clone %s: %s is not base_sha's blob" % (dest, path))
    # ---- register (judge dir: never arm-readable)
    nonce = hashlib.sha256(os.urandom(16)).hexdigest()[:24]
    man = {"path": os.path.realpath(dest), "nonce": nonce, "task": task, "base_sha": full, "source": srcr,
           "objects": sorted(want), "harness_files": {k: hashlib.sha256(v).hexdigest() for k, v in extra.items()},
           "entries": {rel: _describe(dest / rel, st) for rel, st in sorted(ents.items())}}
    reg, mdir = _reg_paths(p)
    mb = _dump(man)
    with arena_lock(p):
        mdir.mkdir(parents=True, exist_ok=True)
        (mdir / ("%s.json" % nonce)).write_bytes(mb)
        _write_lines(reg, [json.dumps({
            "ts": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "path": man["path"],
            "nonce": nonce, "task": task, "base_sha": full, "source": srcr, "objects": len(want),
            "files": len(files), "manifest_sha256": hashlib.sha256(mb).hexdigest()}, sort_keys=True).encode()])
    return dest


# ---------------------------------------------------------------- freeze / check

def _no_links(p: dict, files=()):
    for f in (p["tasks"], p["judge"], p["freeze"].parent, *files):
        if os.path.islink(f):
            raise TaskRefused("%s is a symlink: refused (a task or judge file must be the bytes the harness wrote, "
                              "not a link into an arm-writable tree)" % f)


def _no_assign(p: dict, what: str):
    tasks, probs = assignments(p)
    if tasks:
        raise TaskRefused("assign record(s) already in the event log (%s): %s after assignment is refused (§1.1)"
                          % (", ".join(sorted(tasks)), what))
    if probs:
        raise TaskRefused("unrecognised entries under events/ (an assign could hide there), %s refused:\n  %s"
                          % (what, "\n  ".join(probs[:10])))


def _read_pair(p: dict, tf: Path):
    hp = p["judge"] / tf.name
    _no_links(p, (tf, hp))
    tb = tf.read_bytes()
    if not hp.is_file():
        raise TaskRefused("%s: judge file missing" % tf.stem)
    return tb, hp.read_bytes()


def _provisional(hidden: dict, ts: str):
    if hidden.get("label") == "Clean" and (str(hidden.get("label_window_ends") or "9") > ts
                                           or hidden.get("label_pending")):
        return "window ends %s, open reworks %s" % (hidden.get("label_window_ends"),
                                                    hidden.get("label_pending") or "none")
    return None


def _vet_problem(hidden: dict, base) -> str:
    """'' when the hidden file has >= 1 scored fix_test and every scored fix_test carries a measured discrimination
    (ARENA_TASKS_VET_CHECK_FAILS_AT_BASE, fail closed) bound to this very check: its stored key must equal the key
    of (current judge runner, the task's base, fix, path, body) now, so a judge change or an edited body since the
    census refuses; else why not."""
    checks = hidden.get("checks") if isinstance(hidden, dict) else None
    scored = [c for c in checks or [] if isinstance(c, dict) and c.get("type") == "fix_test"]
    if not scored:
        return "no scored fix_test"
    fix = hidden.get("fix_sha")

    def bound(c):
        try:
            return c["vet"].get("key") == vet_key(str(base), str(fix), str(c.get("path")), str(c.get("body")))
        except (AttributeError, TypeError):
            return False
    bad = [str(c.get("path")) for c in scored if not (vet_record_ok(c) and bound(c))]
    return ("fix_test not vetted, not discriminating or vetted under another judge/body: " + ", ".join(bad[:3])) if bad else ""


def freeze(p: dict, now=None) -> dict:
    """Freeze every task file, under the arena lock from the assign check to the last append. Refuses: any
    assign-like record anywhere under events/ (or an entry there it cannot read); a symlinked task, judge or
    judge-dir file; any leak scoped to every task; tampering with the authority or the log's freeze copies; a frozen
    task whose file is gone or changed; a Clean label still inside its rework window; a file changed while the leak
    scan ran (all bytes are read before the scan and re-read after it). A task with a leak scoped to it alone is
    WITHHELD (not frozen, reported) while the others freeze."""
    ts = now or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with arena_lock(p):
        _no_assign(p, "freezing")
        _no_links(p)
        frozen = frozen_hashes(p)
        bad = _mirror_problems(p, frozen)
        if bad:
            raise TaskRefused("freeze records tampered with, nothing frozen:\n  " + "\n  ".join(bad[:20]))
        files = sorted(p["tasks"].glob("*.json")) if p["tasks"].is_dir() else []
        if not files:
            raise TaskRefused("no task files under %s" % p["tasks"])
        gone = sorted(set(frozen) - {f.stem for f in files})
        if gone:
            raise TaskRefused("frozen task file(s) missing, refused: " + ", ".join(gone))
        read = {tf.stem: (tf,) + _read_pair(p, tf) for tf in files}      # every byte read BEFORE the scan
        scoped = scoped_leaks(p)
        every = [m for s, m in scoped if s == ALL]
        if every:
            raise TaskRefused("hidden checks reachable by an arm (every task), nothing frozen:\n  "
                              + "\n  ".join(every[:20]))
        held = {s for s, _ in scoped}
        refused, early, withheld, recs, all_hashes, unvetted = [], [], [], [], [], []
        run_id = "freeze-" + ts
        for t, (tf, tb, hb) in sorted(read.items()):
            task = _loads(tb, str(tf))
            if task.get("id") != t:
                raise TaskRefused("%s: id %r does not match its file name" % (tf, task.get("id")))
            hp = p["judge"] / tf.name
            validate_task(task, hp, p, hidden_bytes=hb)
            h = hashlib.sha256(tb).hexdigest()
            if t in frozen:
                if frozen[t].get("sha256") != h:
                    refused.append(t)
                all_hashes.append((t, h))
                continue
            if t in held:
                withheld.append(t)
                continue
            unvet = _vet_problem(_loads(hb, str(hp)), task.get("base_sha"))
            if unvet:
                unvetted.append("%s (%s)" % (t, unvet))
                continue
            why = _provisional(_loads(hb, str(hp)), ts)
            if why:
                early.append("%s (%s)" % (t, why))
            all_hashes.append((t, h))
            recs.append({"ts": ts, "arm": "harness", "lane": None, "run_id": run_id, "task": t,
                         "event": "freeze", "detail": {"sha256": h, "hidden_sha256": hashlib.sha256(hb).hexdigest(),
                                                       "path": str(tf)}})
        if refused:
            raise TaskRefused("frozen task file(s) changed since freeze, refused: " + ", ".join(refused)
                              + " (recovery: `census --replace TASK` then `refreeze TASK --reason ...`)")
        if unvetted:
            raise TaskRefused("hidden check(s) without a passing vet record (fails at base, passes at the fix), "
                              "nothing frozen: " + "; ".join(unvetted[:20]))
        if early:
            raise TaskRefused("Clean label(s) still provisional, nothing frozen: " + "; ".join(early))
        moved = [t for t, (tf, tb, hb) in read.items() if _read_pair(p, tf) != (tb, hb)]
        if moved or {f.stem for f in p["tasks"].glob("*.json")} != set(read):
            raise TaskRefused("task or judge file(s) changed while the leak scan ran, nothing frozen: %s"
                              % (", ".join(sorted(moved)) or "the task set"))
        all_hashes.sort()
        pool_hash = hashlib.sha256("\n".join("%s %s" % x for x in all_hashes).encode()).hexdigest()
        if recs:
            manifest = {t: d.get("sha256") for t, d in frozen.items()}
            manifest.update({r["task"]: r["detail"]["sha256"] for r in recs})
            recs.append({"ts": ts, "arm": "harness", "lane": None, "run_id": run_id, "task": None,
                         "event": "freeze", "detail": {"pool_sha256": pool_hash, "n": len(all_hashes),
                                                       "new": len(recs), "manifest": manifest}})
            _append_authority(p, recs)
            _append(p, recs)
    return {"frozen_new": max(len(recs) - 1, 0), "pool": len(all_hashes), "pool_sha256": pool_hash,
            "withheld": {t: [m for s, m in scoped if s == t][:3] for t in withheld}}


def refreeze(p: dict, task_id: str, reason: str, now=None) -> dict:
    """The recovery for a frozen task whose file changed (a swap, a re-census with `--replace`): append a `refreeze`
    record naming the hash it replaces and why. Never overwrites: the old freeze stays in the chain. Allowed only
    before any assignment, with a non-empty reason, and when the new bytes pass every freeze check."""
    reason = (reason or "").strip()
    if not reason:
        raise TaskRefused("refreeze needs a --reason")
    ts = now or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with arena_lock(p):
        _no_assign(p, "refreezing")
        frozen = frozen_hashes(p)
        bad = _mirror_problems(p, frozen)
        if bad:
            raise TaskRefused("freeze records tampered with, nothing refrozen:\n  " + "\n  ".join(bad[:20]))
        if task_id not in frozen:
            raise TaskRefused("%s is not frozen: use freeze" % task_id)
        tf = p["tasks"] / (task_id + ".json")
        if not tf.is_file():
            raise TaskRefused("%s: task file missing" % task_id)
        tb, hb = _read_pair(p, tf)
        h = hashlib.sha256(tb).hexdigest()
        hh = hashlib.sha256(hb).hexdigest()
        if h == frozen[task_id].get("sha256") and hh == frozen[task_id].get("hidden_sha256"):
            raise TaskRefused("%s: unchanged since its freeze: nothing to refreeze" % task_id)
        task = _loads(tb, str(tf))
        if task.get("id") != task_id:
            raise TaskRefused("%s: id %r does not match its file name" % (tf, task.get("id")))
        validate_task(task, p["judge"] / tf.name, p, hidden_bytes=hb)
        unvet = _vet_problem(_loads(hb), task.get("base_sha"))
        if unvet:
            raise TaskRefused("%s: hidden check without a passing vet record: %s" % (task_id, unvet))
        why = _provisional(_loads(hb), ts)
        if why:
            raise TaskRefused("%s: Clean label still provisional (%s)" % (task_id, why))
        found = find_leaks(p, task_id)
        if found:
            raise TaskRefused("%s: hidden checks reachable by an arm, refused:\n  %s" % (task_id,
                                                                                         "\n  ".join(found[:10])))
        if _read_pair(p, tf) != (tb, hb):
            raise TaskRefused("%s: file changed while the leak scan ran: refused" % task_id)
        run_id = "refreeze-" + ts
        manifest = {t: d.get("sha256") for t, d in frozen.items()}
        manifest[task_id] = h
        recs = [{"ts": ts, "arm": "harness", "lane": None, "run_id": run_id, "task": task_id, "event": "refreeze",
                 "detail": {"sha256": h, "hidden_sha256": hh, "path": str(tf),
                            "replaces": frozen[task_id].get("sha256"), "reason": reason}},
                {"ts": ts, "arm": "harness", "lane": None, "run_id": run_id, "task": None, "event": "freeze",
                 "detail": {"pool_sha256": hashlib.sha256("\n".join("%s %s" % x for x in sorted(manifest.items()))
                                                          .encode()).hexdigest(),
                            "n": len(manifest), "new": 0, "manifest": manifest}}]
        _append_authority(p, recs)
        _append(p, recs)
    return {"refrozen": task_id, "sha256": h, "replaces": frozen[task_id].get("sha256"), "reason": reason}


def load_frozen(task_id: str, p: dict | None = None, leaks: bool = True) -> dict:
    """The task as frozen, or TaskRefused. The judge and the gate call this; nothing reads a task file directly.
    The file is read ONCE: the returned task is parsed from the very bytes whose hash was checked. With `leaks`
    (the default) a hidden check readable by an arm refuses it too, when the leak is scoped to THIS task or to
    every task (another arm's notes about its own test never refuse it)."""
    p = p or paths()
    fz = frozen_hashes(p).get(task_id)
    tf = p["tasks"] / (task_id + ".json")
    if not fz:
        raise TaskRefused("%s: not frozen" % task_id)
    if not tf.is_file():
        raise TaskRefused("%s: frozen but its file is gone" % task_id)
    tb = tf.read_bytes()
    if hashlib.sha256(tb).hexdigest() != fz.get("sha256"):
        raise TaskRefused("%s: task file hash %s != frozen %s: refused" % (
            task_id, hashlib.sha256(tb).hexdigest()[:12], str(fz.get("sha256"))[:12]))
    hp = p["judge"] / tf.name
    hb = hp.read_bytes() if hp.is_file() else None
    if hb is None or hashlib.sha256(hb).hexdigest() != fz.get("hidden_sha256"):
        raise TaskRefused("%s: judge file changed since freeze: refused" % task_id)
    task = _loads(tb, str(tf))
    validate_task(task, hp, p, hidden_bytes=hb)
    if leaks:
        found = find_leaks(p, task_id)
        if found:
            raise TaskRefused("%s: hidden checks reachable by an arm, refused:\n  %s" % (task_id,
                                                                                         "\n  ".join(found[:10])))
    return task


def check(p: dict, only=None) -> list[str]:
    problems = []
    try:
        frozen = frozen_hashes(p)
        problems += _mirror_problems(p, frozen)
    except ArenaError as e:
        problems.append(str(e))
        frozen = {}
    names = set(only or [])
    if not names:
        names = set(frozen) | ({f.stem for f in p["tasks"].glob("*.json")} if p["tasks"].is_dir() else set())
    for t in sorted(names):
        try:
            load_frozen(t, p, leaks=False)
        except (ArenaError, ValueError, OSError) as e:
            problems.append(str(e))
    if only:
        seen = set()
        for t in only:
            for x in find_leaks(p, t):
                if x not in seen:
                    seen.add(x)
                    problems.append(x)
    else:
        problems += find_leaks(p)
    return problems


# ---------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("census", help="scan the ledger, write task + judge files and a report")
    c.add_argument("--sanity", default=SANITY_ITEM, help="item the census must find (default %(default)s)")
    c.add_argument("--dry-run", action="store_true", help="report only; write no task files")
    c.add_argument("--replace", nargs="+", default=[], metavar="TASK",
                   help="rewrite these FROZEN tasks anyway (they then need `refreeze TASK --reason`)")
    c.add_argument("--no-pin", action="store_true", help="do not pin the old-history shas under " + PIN_PREFIX)
    v = sub.add_parser("vet", help="run each unvetted hidden fix_test at base and at the fix; cache the exit codes")
    v.add_argument("--budget", type=float, default=VET_BUDGET, help="start no task after this many seconds "
                   "(resumable; default %(default)s)")
    v.add_argument("--jobs", type=int, default=4, help="parallel sparse clones (default %(default)s)")
    v.add_argument("--task", nargs="+", help="only these task ids")
    sub.add_parser("freeze", help="hash every task file into the event log (before any assignment)")
    r = sub.add_parser("refreeze", help="re-freeze one changed frozen task, with a recorded reason (appended)")
    r.add_argument("task")
    r.add_argument("--reason", required=True)
    sub.add_parser("pin", help="pin the old-history shas of the last census report under " + PIN_PREFIX)
    k = sub.add_parser("check", help="refuse changed, unfrozen, live:full or leaked tasks")
    k.add_argument("--task", nargs="+")
    b = sub.add_parser("clone", help="build an arm clone of a frozen task's base_sha (depth 1, no later history)")
    b.add_argument("task")
    b.add_argument("dest")
    a = ap.parse_args(argv)
    p = paths()
    try:
        if a.cmd == "vet":
            missing: list = []
            # sanity=None: the sanity item is itself unvetted until this runs; `census` applies the sanity gate
            census(sanity=None, vet=vet_lookup(read_vet_cache(vet_cache_path(p))), vet_missing=missing)
            jobs = [j for j in missing if not a.task or j["task"] in a.task]
            work = Path(os.environ.get("ARENA_VET_DIR") or
                        Path(os.environ.get("ARENA_CLONES", "/home/mandrake/rm/arena")).parent / "arena-vet")
            out = run_vet(jobs, REPO, work, vet_cache_path(p), workers=a.jobs, budget=a.budget)
            out["tasks"] = len(jobs)
            print(json.dumps(out)[:2000])
            return 1 if out["left"] or out["errors"] else 0
        if a.cmd == "census":
            pool, rep = census(sanity=a.sanity, vet=vet_lookup(read_vet_cache(vet_cache_path(p))))
            rep["arena"] = str(p["root"])
            if rep["vet"]["not_vetted"] and not a.dry_run:
                print("REFUSED: %d hidden check(s) never vetted; run `arena_tasks.py vet` until it exits 0"
                      % rep["vet"]["not_vetted"])
                return 1
            if not a.dry_run:
                rep["write"] = write_pool(pool, p, replace=a.replace)
                if not a.no_pin:
                    rep["pins"] = pin_old(rep.get("old_history_pins") or rep.get("old_history_shas") or [])
                p["census"].mkdir(parents=True, exist_ok=True)
                rp = p["census"] / ("census_%s.json" % dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
                rp.write_bytes(_dump(rep))
                print("report:", rp)
                print("next: rerun arena_answer_check.py; freeze refuses until it passes on these files")
            print(json.dumps({k: rep.get(k) for k in ("pool", "excluded", "labels", "labelled", "sanity", "kinds", "vet",
                                                      "base_contains_pairs", "scanned_closed_in_window")}))
            if rep.get("pins"):
                print("pins:", json.dumps({k: (len(v) if isinstance(v, list) else v)
                                           for k, v in rep["pins"].items()}))
            w = rep.get("write", {})
            if w.get("refused_frozen_changed"):
                print("REFUSED: frozen tasks would change:", w["refused_frozen_changed"])
                return 1
            if w.get("frozen_not_in_pool"):
                print("REFUSED: frozen tasks the census no longer picks (stored pool != census):",
                      w["frozen_not_in_pool"])
                return 1
            return 0
        if a.cmd == "clone":
            t = load_frozen(a.task, p)
            print(build_arm_clone(t["base_sha"], Path(a.dest), task=a.task, p=p))
            return 0
        if a.cmd in ("freeze", "refreeze"):   # ARENA_ANSWER_CHECK_FIX_STALE_ROWS_UNGATED: a current, passing check
            import arena_answer_check as AC
            stale = AC.gate(p)
            if stale:
                print("REFUSED: %s refused, the answer check is not current and passing:\n  %s"
                      % (a.cmd, "\n  ".join(stale)))
                return 1
        if a.cmd == "freeze":
            out = freeze(p)
            print(json.dumps(out))
            if out.get("withheld"):
                print("WITHHELD (a hidden check of theirs is arm-readable):", ", ".join(sorted(out["withheld"])))
                return 1
            return 0
        if a.cmd == "refreeze":
            print(json.dumps(refreeze(p, a.task, a.reason)))
            return 0
        if a.cmd == "pin":
            reps = sorted(p["census"].glob("census_*.json")) if p["census"].is_dir() else []
            if not reps:
                raise ArenaError("no census report under %s" % p["census"])
            last = _loads(reps[-1].read_bytes(), str(reps[-1]))
            out = pin_old(last.get("old_history_pins") or last.get("old_history_shas") or [])
            print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in out.items()}))
            return 1 if out.get("missing") else 0
        probs = check(p, a.task)
        for x in probs:
            print("REFUSED", x)
        print("check: %d problem(s)" % len(probs))
        return 1 if probs else 0
    except SanityFail as e:
        print("SANITY FAIL:", e)
        return 2
    except ArenaError as e:
        print("REFUSED:", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
