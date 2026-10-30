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
  - it has a `start` event before that close;
  - the close sha resolves to a commit with exactly one parent, and the diff (bookkeeping stripped: ledger,
    queue projections, item prose) touches 1-8 files;
  - its `needs` is `offline` and its files hold code the gate judges offline (Python, XML defs/patches, C#);
  - an objective proof exists: the diff adds or changes a selftest, a Defs/Patches XML, or C#;
  - it carries a label: ESCAPED (an item filed with `caused_by` = it within 7 days of the close) or CLEAN
    (a `verify` pass and no such rework). An item with neither is rejected as `unlabelled`.
The census reports its pool with a SANITY PROBE: a hand-picked item that must be found. A missing sanity item is a
blind instrument, not a small pool: the census exits 2 and writes nothing.

FREEZE (§1.1). Writes one `freeze` event per task (sha256 of the task file and of its judge file) plus one batch
event whose `pool_sha256` seeds the stratified draw, BEFORE any `assign` event exists; with an `assign` already in
the log it refuses. Re-freezing an unchanged task is a no-op; a changed one is refused. `check` (and
`load_frozen()`, which the judge and gate call) refuses any task whose file hash differs from its freeze, any task
not frozen, any `live` outside {none, minimal, minimal+deps} (the trial has no `full` tier, owner 2026-10-29),
and any hidden check that reached an arm-readable path.

Replay tasks are `live: none`: the build half runs in throwaway clones with no game (§3.1).
"""
from __future__ import annotations

import argparse
import base64
import binascii
import contextlib
import datetime as dt
import difflib
import fcntl
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
UTILS = HERE.parent
sys.path.insert(0, str(UTILS.parent))       # src/RimMandrake -> `rimflow`
sys.path.insert(0, str(UTILS))              # rmpaths
from rimflow import model  # noqa: E402

REPO = UTILS.parent.parent.parent

WINDOW = ("2026-10-12", "2026-10-27")
ESCAPE_DAYS = 7
MAX_FILES = 8
LIVE_OK = ("none", "minimal", "minimal+deps")
KINDS = ("python-util", "xml-def-patch", "csharp", "live-verify", "tooling")
# Hand-picked and checked by hand (2026-10-30, git + ledger, not this tool): claimed and started 2026-10-26T00:00:18Z,
# verify pass and close 00:21:32Z at ledger sha 6a925e0b57, which the rewrite turned into 310ad7f953 (the ledger
# commit 05c8baefa6 says "close ... at 310ad7f953"): 2 files, worker.py + selftest_steve_worker.py, needs offline,
# no rework. If the census cannot see it, the census is blind (instrument_traps: a count is a query bug until a
# sanity probe proves the instrument can see).
SANITY_ITEM = "STEVEDESKTOP_WORKER_BUILD_DURABLE_ATTEMPTS"
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
MARKER = "arena_clone.json"             # <clone>/.git/arena_clone.json, written by build_arm_clone


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


class Resolver:
    """A ledger sha -> (a commit in `repo`'s current history, how), or (None, why not).

    🔴 origin/main was REWRITTEN on 2026-10-28/29 (RIMMANDRAKE_EXCISE_WORK_HISTORY; lesson
    20261029T140946Z-BENCH-history-rewrite-origin-main-rimmandrake-excise.md): measured 2026-10-30, 0 of the
    in-window close shas resolve in bench or foundry. The old objects survive, unreachable, in the old-history
    repo (`$ARENA_OLD_HISTORY`, default the mirror). A rewritten commit keeps its author date, author and subject,
    so an old sha maps to the one current commit with the same triple; a commit the rewrite excised maps to none.
    """

    def __init__(self, repo: Path, old=None):
        self.repo = Path(repo)
        old = old if old is not None else os.environ.get("ARENA_OLD_HISTORY", "/home/mandrake/rm/mirror.git")
        self.old = Path(old) if old and Path(old).exists() else None
        self._index = None

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
        if cur:
            return cur, "current"
        if not self.old:
            return None, "close sha does not resolve (no old-history repo)"
        r = subprocess.run(["git", "-C", str(self.old), "log", "-1", "--format=%aI%x09%an%x09%s", sha + "^{commit}"],
                           capture_output=True, text=True, timeout=60)
        if r.returncode != 0 or not r.stdout.strip():
            return None, "close sha resolves nowhere"
        hits = self._key_index().get(tuple(r.stdout.rstrip("\n").split("\t", 2)), [])
        if len(hits) == 1:
            return hits[0], "remapped"
        return None, ("close sha excised by the history rewrite" if not hits else "close sha remaps ambiguously")


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


def _rework_verdict(r, by_id, resolve, repo):
    """-> (verdict, fix commit). verdict 'counts' (a closed code fix: the parent escaped), 'pending' (an open
    fix-type child: the parent's Clean is provisional), or why it does not count."""
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

def census(events=None, repo: Path = REPO, window=WINDOW, sanity=SANITY_ITEM, old_history=None):
    """-> (pool, report). Pool entries are (task, hidden). Raises SanityFail when the sanity item is not kept."""
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
        if not any(e.get("event") == "start" and e.get("ts", "") <= close.get("ts", "") for e in evs):
            reject(iid, "no start before close"); continue
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
        t_close = _epoch(close["ts"])
        rw, pending, considered = [], [], []
        for r in reworks.get(iid, []):
            if not (r.created_at and 0 <= _epoch(r.created_at) - t_close <= ESCAPE_DAYS * 86400):
                continue
            verdict, rfix = _rework_verdict(r, by_id, resolve, repo)
            considered.append({"item": r.id, "kind": r.kind, "state": r.state, "verdict": verdict})
            if verdict == "counts":
                rw.append((r, rfix))
            elif verdict == "pending":
                pending.append(r.id)
        verified = any(e.get("event") == "verify" and e.get("result") == "pass" for e in evs)
        label = "Escaped" if rw else ("Clean" if verified else None)
        if not label:
            reject(iid, "unlabelled (no verify pass, no rework)"); continue

        lines = sum(d[1] for d in diff)
        prose = _prose_at(repo, base, iid)
        filed = next((e for e in evs if e.get("event") == "file"), {})
        title = filed.get("title") or it.title or iid
        prompt = title + ("\n\n" + prose.strip() if prose else "")
        crit = _section(prose, "criteria") if prose else None
        crit_src = "prose ## criteria at base_sha"
        if not crit and it.criteria:
            crit, crit_src = "\n".join("%s: %s" % (c["id"], c["text"]) for c in it.criteria), "ledger manifest"
        if not crit:
            crit, crit_src = title, "title (no criteria written)"
        tid = "RP_" + iid
        checks = []
        for path, _, st in diff:
            if is_selftest(path) and st != "D":
                checks.append(_test_entry(repo, fix, base, path, st, type="fix_test",
                                          command="python3 src/RimMandrake/Utils/run_selftests.py --only " + path))
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
                  "sha_resolution": how, "checks": checks,
                  "reworks": rw_out, "rework_candidates": considered,
                  # an open fix-type rework filed in the window: Clean is provisional until it closes or dies
                  "label_pending": sorted(pending),
                  # a fixed instant, not a now-dependent boolean, so a re-census reproduces the frozen bytes; a label
                  # read before this instant can still flip to Escaped
                  "label_window_ends": dt.datetime.fromtimestamp(t_close + ESCAPE_DAYS * 86400, dt.timezone.utc)
                  .strftime("%Y-%m-%dT%H:%M:%SZ")}
        task = {"id": tid, "source_item": iid, "kind": kind, "size": size_points(len(diff), lines),
                "size_basis": {"files": len(diff), "lines": lines}, "area": area_for(files), "prompt": prompt,
                "criteria": crit, "criteria_source": crit_src, "proof": proof, "live": "none",
                "hidden_checks": None, "base_sha": base}
        own = Matcher([hidden]).hits(_public_bytes(task))
        if own:                           # this one task is rejected; the census goes on
            reject(iid, "task would carry its own hidden check (%s)" % own[0][1]); continue
        pool.append((close["ts"], task, hidden))

    # Chains: a later pool task's public file can name an earlier one's hidden check (it IS the earlier item's rework,
    # or it edits a test that rework added). An arm reading it would learn the earlier task's label or check, so in
    # close order the earlier task is kept and the later one rejected.
    kept_pool, seen = [], Matcher([])
    for _, task, hidden in sorted(pool, key=lambda x: x[0]):
        hit = seen.hits(_public_bytes(task))   # base_sha stripped: starting where an earlier fix landed is history
        if hit:
            reject(task["source_item"], "would expose a hidden check of earlier pool task " + hit[0][0])
            continue
        seen.add(hidden)
        kept_pool.append((task, hidden))
    pool = sorted(kept_pool, key=lambda th: th[0]["id"])

    labels = {"Clean": 0, "Escaped": 0}
    for _, h in pool:
        labels[h["label"]] += 1
    kept = {t["source_item"] for t, _ in pool}
    report = {"window": list(window), "scanned_closed_in_window": scanned, "pool": len(pool), "labels": labels,
              "rejects": dict(sorted(rejects.items(), key=lambda kv: -kv[1])),
              "sanity": {"item": sanity, "found": sanity in kept, "reason_if_not": reasons.get(sanity)},
              "kinds": _count(t["kind"] for t, _ in pool), "sizes": _count(str(t["size"]) for t, _ in pool)}
    if sanity and sanity not in kept:
        raise SanityFail("sanity item %s was not kept (%s): the census is blind, not the pool small"
                         % (sanity, reasons.get(sanity) or "not scanned: not a done item closed in window"))
    return pool, report


def _count(xs):
    out: dict = {}
    for x in xs:
        out[x] = out.get(x, 0) + 1
    return out


def _dump(obj) -> bytes:
    return (json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_pool(pool, p: dict) -> dict:
    """Write task + judge files. A frozen task is never rewritten: identical content is skipped, a change refused.
    A frozen task the new census no longer picks is reported (`frozen_not_in_pool`): the CLI refuses that census,
    because the stored pool and the census would disagree."""
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
        if task["id"] in frozen:
            if hashlib.sha256(tb).hexdigest() == frozen[task["id"]]["sha256"]:
                skipped += 1
            else:
                refused.append(task["id"])
            continue
        hp.write_bytes(hb)
        tp.write_bytes(tb)
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
    task is an error, not a later or earlier winner; each batch record's manifest must equal the tasks frozen so far."""
    out = {}
    for rec in _chain(p)[0]:
        d = rec.get("detail") or {}
        if rec.get("task"):
            if rec["task"] in out:
                raise ArenaError("duplicate freeze record for %s in %s: refusing" % (rec["task"], p["freeze"]))
            out[rec["task"]] = d
        elif d.get("manifest") != {t: v.get("sha256") for t, v in out.items()}:
            raise ArenaError("freeze batch %s manifest disagrees with the task records: refusing" % rec.get("run_id"))
    return out


def _mirror_problems(p: dict, frozen: dict) -> list[str]:
    """The §1.7 event log carries a copy of every freeze. A freeze record in any other events file is forged; one in
    harness.jsonl that disagrees with the authority, or an authority freeze the log lost, is tampering."""
    probs, seen = [], set()
    for ev in read_log(p):
        if ev.get("event") != "freeze" or not ev.get("task"):
            continue
        t, d = ev["task"], ev.get("detail") or {}
        if ev["_file"] != p["log"].name:
            probs.append("%s: freeze record in events/%s, outside the harness log: forged" % (t, ev["_file"]))
        elif t not in frozen or (d.get("sha256"), d.get("hidden_sha256")) != (
                frozen[t].get("sha256"), frozen[t].get("hidden_sha256")):
            probs.append("%s: freeze record in the event log conflicts with the authority" % t)
        elif t in seen:
            probs.append("%s: duplicate freeze record in the event log" % t)
        seen.add(t)
    probs += ["%s: frozen, but the event log lost its freeze record" % t for t in sorted(set(frozen) - seen)]
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

def validate_task(task: dict, hidden_path: Path, p: dict, hidden_bytes: bytes | None = None):
    """Refuse a task spec the trial may not run. Raises TaskRefused."""
    tid = task.get("id")
    for k in ("id", "source_item", "kind", "size", "area", "prompt", "criteria", "proof", "live", "base_sha"):
        if task.get(k) in (None, "", []):
            raise TaskRefused("%s: field %s missing" % (tid, k))
    if not isinstance(task["live"], str) or task["live"] not in LIVE_OK:
        raise TaskRefused("%s: live %r refused: the trial runs on the minimal list only (owner 2026-10-29); "
                          "allowed %s" % (tid, task["live"], ", ".join(LIVE_OK)))
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


def _decodings(raw: bytes) -> list[str]:
    """Every text an arm could recover from these bytes without a key: UTF-8, UTF-16 (either byte order, either
    alignment), JSON/string escapes (two levels) and base64 runs (standard and urlsafe, wrapped or not)."""
    out = [raw.decode("utf-8", "replace")]
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


def leak_tokens(hidden: dict) -> list[str]:
    """Literal tokens (lowercase) whose presence on an arm-readable path means a hidden check leaked: the fix and
    rework shas (any 7-40 char prefix counts), rework and pending-rework ids, the path of every test the fix or a
    rework ADDED (one it changed was visible at base), and each normalised novel body anchor."""
    a, b, c = _typed_tokens(hidden)
    return a + b + c


class Matcher:
    """Hidden-check matcher over raw bytes: case-insensitive, sha prefixes of 7-40 hex, either slash direction,
    normalised whitespace, every decoding _decodings finds."""

    def __init__(self, hiddens):
        self.sha7, self.lits, self.anchors = {}, [], []
        for h in hiddens:
            self.add(h)

    def add(self, h: dict):
        owner = h.get("task") or "?"
        shas, lits, anchors = _typed_tokens(h)
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


def _scan_file(fp: Path, matcher: Matcher, skip_shas=()) -> list[tuple[str, str]]:
    """Whole file, in overlapping SCAN_CHUNK pieces when large: no size is skipped."""
    out = {}
    with open(fp, "rb") as fh:
        pos = 0
        while True:
            fh.seek(max(pos - SCAN_OVERLAP, 0))
            raw = fh.read(SCAN_CHUNK + (SCAN_OVERLAP if pos else 0))
            if not raw:
                break
            if fp.suffix == ".json" and fp.parent.name == "tasks" and pos == 0:
                raw = _BASE_FIELD.sub(b'"base_sha": null', raw)     # a task's own base_sha field is history
            for owner, what in matcher.hits(raw, skip_shas):
                out.setdefault(owner, what)
            pos += SCAN_CHUNK
            if len(raw) < SCAN_CHUNK:
                break
    return sorted(out.items())


def _clone_check(top: Path, objs: dict, p: dict) -> tuple[list[str], set, list]:
    """A git repository under the arm clone root. -> (problems, paths exempt from the text scan).

    The clone must be what build_arm_clone makes: a marker naming its base_sha; no hidden object (fix or rework
    commit, hidden test blob) in its object store, alternates included; no commit of the source repo that is not
    base_sha or an ancestor of it; HEAD at or after base_sha. Only a tracked file byte-identical to base_sha's
    version is exempt from the text scan (its content is the base the object scan just verified); a tracked file
    whose content differs from base (edited, staged, or committed in the clone) is scanned like any other."""
    probs = []
    gitdir = _git(top, "rev-parse", "--absolute-git-dir", check=False).strip()
    if not gitdir:
        return ["%s: .git present but git cannot open it" % top], set(), []
    if not _inside(Path(gitdir), top):
        probs.append("%s: its git dir %s is outside the clone" % (top, gitdir))
    if (Path(gitdir) / "objects" / "info" / "alternates").is_file():
        probs.append("%s: borrows objects via alternates (the full history is readable)" % top)
    if objs:
        ids = sorted(objs)
        r = subprocess.run(["git", "-C", str(top), "cat-file", "--batch-check"], input="\n".join(ids) + "\n",
                           capture_output=True, text=True, timeout=120)
        for sha, line in zip(ids, r.stdout.splitlines()):
            if not line.endswith(" missing"):
                probs.append("%s: hidden check of %s readable at %s (git object %s present)"
                             % (objs[sha], objs[sha], top, sha[:12]))
    mk = Path(gitdir) / MARKER
    if not mk.is_file():
        probs.append("%s: git clone without an %s marker: its history is unverified (build it with "
                     "build_arm_clone)" % (top, MARKER))
        return probs, set(), []
    try:
        m = _loads(mk.read_bytes(), str(mk))
        base, src = m["base_sha"], Path(m.get("source") or REPO)
    except (ArenaError, KeyError, TypeError) as e:
        return probs + ["%s: marker unreadable: %s" % (top, e)], set(), []
    tf = p["tasks"] / ("%s.json" % m.get("task"))
    if m.get("task") and tf.is_file():
        try:
            if _loads(tf.read_bytes()).get("base_sha") != base:
                probs.append("%s: marker base %s is not task %s's base_sha" % (top, base[:12], m["task"]))
        except ArenaError:
            pass
    if not _resolve(top, base):
        return probs + ["%s: marker base %s is not in the clone" % (top, base[:12])], set(), []
    if subprocess.run(["git", "-C", str(top), "merge-base", "--is-ancestor", base, "HEAD"],
                      capture_output=True, timeout=60).returncode != 0:
        probs.append("%s: HEAD is not base_sha %s or a descendant" % (top, base[:12]))
    allobj = [ln.split() for ln in _git(top, "cat-file", "--batch-all-objects", "--unordered",
                                        "--batch-check=%(objectname) %(objecttype)").splitlines()]
    commits = [o for o, t in allobj if t == "commit"]
    others = [c for c in commits if c != base]
    if others and src.exists():
        r = subprocess.run(["git", "-C", str(src), "cat-file", "--batch-check"], input="\n".join(others) + "\n",
                           capture_output=True, text=True, timeout=120)
        in_src = [c for c, ln in zip(others, r.stdout.splitlines()) if not ln.endswith(" missing")]
        if in_src:
            anc = set(_git(src, "rev-list", base).split())
            late = [c for c in in_src if c not in anc]
            if late:
                probs.append("%s: holds %d source commit(s) after base_sha %s (e.g. %s): later history readable"
                             % (top, len(late), base[:12], late[0][:12]))
    in_base = set(_git(top, "ls-tree", "-r", "-z", "--name-only", base).split("\0")) - {""}
    changed = set(_git(top, "diff", "--no-renames", "--name-only", "-z", base).split("\0"))
    base_objs = {ln.split()[2] for ln in _git(top, "ls-tree", "-r", "-t", base).splitlines() if ln.strip()}
    # every blob that is not part of base_sha's tree (written by the arm, or fetched) is text-scanned by the caller
    extra = [o for o, t in allobj if t == "blob" and o not in base_objs]
    return probs, {str(top / f) for f in in_base - changed}, extra


def _blob_hits(top: Path, blobs: list[str], matcher) -> list[tuple[str, str, str]]:
    """[(blob, owner, what)] for clone blobs outside base_sha's tree."""
    out = []
    for b in blobs:
        r = subprocess.run(["git", "-C", str(top), "cat-file", "blob", b], capture_output=True, timeout=120)
        for owner, what in matcher.hits(r.stdout) if r.returncode == 0 else ():
            out.append((b, owner, what))
    return out


def find_leaks(p: dict) -> list[str]:
    """Scan every arm-readable root for any hidden check. Nothing is skipped silently: every file of any size, every
    git object store under the clone root (_clone_check), and every symlink, which is flagged when it resolves into
    the judge dir or outside the arm-readable roots (it is never followed; a link inside a root points at a file
    the walk scans anyway). A hard link to a judge file is flagged by inode."""
    leaks = []
    roots = arm_readable_roots(p)
    judge_root = p["freeze"].parent
    for r in roots:
        for j in (p["judge"], judge_root):
            if _inside(j, r):
                leaks.append("judge directory %s is inside arm-readable %s" % (j, r))
    hiddens, objs, inodes = [], {}, set()
    for d in {p["judge"], judge_root}:
        for f in d.glob("*") if d.is_dir() else []:
            if f.is_file():
                st = os.stat(f)
                inodes.add((st.st_dev, st.st_ino))
    for hf in sorted(p["judge"].glob("*.json")) if p["judge"].is_dir() else []:
        try:
            h = _loads(hf.read_bytes(), str(hf))
        except (OSError, ArenaError) as e:
            leaks.append("judge file %s unreadable: %s" % (hf, e))
            continue
        h.setdefault("task", hf.stem)
        hiddens.append(h)
        for o in hidden_objects(h):
            objs.setdefault(o, hf.stem)
    matcher = Matcher(hiddens)
    real_roots = [os.path.realpath(r) for r in roots]

    def outside(target):
        return not any(target == q or target.startswith(q.rstrip("/") + "/") for q in real_roots)

    exempt = set()
    for r in roots:
        if not r.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(r):
            dp = Path(dirpath)
            if (dp / ".git").exists():
                probs, ex, extra = _clone_check(dp, objs, p)
                leaks += probs
                exempt |= ex
                if matcher:
                    leaks += ["%s: hidden check of %s readable at %s (git blob %s, %s)" % (o, o, dp, b[:12], w)
                              for b, o, w in _blob_hits(dp, extra, matcher)]
            keep = []
            for name in dirnames + filenames:
                fp = dp / name
                if os.path.islink(fp):
                    tgt = os.path.realpath(fp)
                    if _inside(Path(tgt), judge_root) or _inside(Path(tgt), p["judge"]):
                        leaks.append("symlink %s -> %s points into the judge directory" % (fp, os.readlink(fp)))
                    elif outside(tgt) and str(fp) not in exempt:
                        # a link base_sha itself tracks, unchanged, is task content (the real repo has one, into
                        # MandrakeWorkflows); only one the arm made or retargeted is flagged. Into the judge: always.
                        leaks.append("symlink %s -> %s resolves outside the arm-readable roots"
                                     % (fp, os.readlink(fp)))
                elif name in dirnames:
                    keep.append(name)
            dirnames[:] = [d for d in dirnames if d in keep]
            for fn in filenames:
                fp = dp / fn
                if os.path.islink(fp):
                    continue
                gp = dp.parts[dp.parts.index(".git"):] if ".git" in dp.parts else ()
                if (gp == (".git",) and fn == "index") or (len(gp) == 3 and gp[1] == "objects" and (
                        re.fullmatch(r"[0-9a-f]{2}", gp[2]) and re.fullmatch(r"[0-9a-f]{38}", fn)
                        or gp[2] == "pack" and re.fullmatch(r"pack-[0-9a-f]{40,64}\.[a-z]+", fn))):
                    continue                    # git's compressed stores: every object in them is checked above
                try:
                    st = os.lstat(fp)
                    if (st.st_dev, st.st_ino) in inodes:
                        leaks.append("%s is a hard link to a judge file" % fp)
                        continue
                    if str(fp) in exempt or not matcher:
                        continue
                    for owner, what in _scan_file(fp, matcher):
                        leaks.append("%s: hidden check of %s readable at %s (%s)" % (owner, owner, fp, what))
                except OSError as e:
                    leaks.append("%s: unreadable by the scan (%s): not verified" % (fp, e))
    return leaks


# ---------------------------------------------------------------- arm clones

def build_arm_clone(base_sha: str, dest: Path, src: Path = REPO, task: str | None = None) -> Path:
    """The only sanctioned arm clone: a depth-1 fetch of base_sha into an empty repo, checked out detached, with no
    remote, no tags, no FETCH_HEAD and no alternates, so no commit after base_sha (the fix included) exists in it.
    Writes the marker _clone_check reads."""
    dest = Path(dest)
    if dest.exists() and any(dest.iterdir()):
        raise ArenaError("%s is not empty" % dest)
    full = _resolve(Path(src), base_sha)
    if not full:
        raise ArenaError("base_sha %s does not resolve in %s" % (base_sha, src))
    dest.mkdir(parents=True, exist_ok=True)
    _git(dest, "init", "-q")
    r = subprocess.run(["git", "-C", str(dest), "fetch", "-q", "--depth", "1", "--no-tags",
                        "file://" + str(Path(src).resolve()), full], capture_output=True, text=True, timeout=540)
    if r.returncode != 0:
        raise ArenaError("fetch %s: %s" % (full[:12], r.stderr.strip()[:200]))
    # a full-tree checkout of the real repo outlasts _git's 60 s (probe CONTROL2 on drvfs), so it gets fetch's bound
    r = subprocess.run(["git", "-C", str(dest), "checkout", "-q", "--detach", full],
                       capture_output=True, text=True, timeout=540)
    if r.returncode != 0:
        raise ArenaError("checkout %s: %s" % (full[:12], r.stderr.strip()[:200]))
    gd = Path(_git(dest, "rev-parse", "--absolute-git-dir").strip())
    (gd / "FETCH_HEAD").unlink(missing_ok=True)
    (gd / MARKER).write_text(json.dumps({"task": task, "base_sha": full, "source": str(Path(src).resolve())},
                                        sort_keys=True) + "\n")
    return dest


# ---------------------------------------------------------------- freeze / check

def freeze(p: dict, now=None) -> dict:
    """Freeze every task file, under the arena lock from the assign check to the last append. Refuses: any assign
    already logged; any leak; any tampering with the authority or the event log's freeze copies; a frozen task
    whose file is gone or changed; a Clean label still inside its rework window or with an open fix-type rework."""
    ts = now or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with arena_lock(p):
        if any(ev.get("event") == "assign" for ev in read_log(p)):
            raise TaskRefused("an assign event is already in the log: freezing after assignment is refused (§1.1)")
        leaks = find_leaks(p)
        if leaks:
            raise TaskRefused("hidden checks reachable by an arm, nothing frozen:\n  " + "\n  ".join(leaks[:20]))
        frozen = frozen_hashes(p)
        bad = _mirror_problems(p, frozen)
        if bad:
            raise TaskRefused("freeze records tampered with, nothing frozen:\n  " + "\n  ".join(bad[:20]))
        run_id = "freeze-" + ts
        recs, all_hashes, refused, early = [], [], [], []
        files = sorted(p["tasks"].glob("*.json")) if p["tasks"].is_dir() else []
        if not files:
            raise TaskRefused("no task files under %s" % p["tasks"])
        gone = sorted(set(frozen) - {f.stem for f in files})
        if gone:
            raise TaskRefused("frozen task file(s) missing, refused: " + ", ".join(gone))
        for tf in files:
            tb = tf.read_bytes()                # one read: these bytes are hashed, parsed and validated
            task = _loads(tb, str(tf))
            if task.get("id") != tf.stem:
                raise TaskRefused("%s: id %r does not match its file name" % (tf, task.get("id")))
            hp = p["judge"] / tf.name
            hb = hp.read_bytes() if hp.is_file() else None
            if hb is None:
                raise TaskRefused("%s: judge file missing" % tf.stem)
            validate_task(task, hp, p, hidden_bytes=hb)
            h = hashlib.sha256(tb).hexdigest()
            all_hashes.append((tf.stem, h))
            if tf.stem in frozen:
                if frozen[tf.stem].get("sha256") != h:
                    refused.append(tf.stem)
                continue
            hidden = _loads(hb, str(hp))
            if hidden.get("label") == "Clean" and (str(hidden.get("label_window_ends") or "9") > ts
                                                   or hidden.get("label_pending")):
                early.append("%s (window ends %s, open reworks %s)" % (tf.stem, hidden.get("label_window_ends"),
                                                                      hidden.get("label_pending") or "none"))
            recs.append({"ts": ts, "arm": "harness", "lane": None, "run_id": run_id, "task": tf.stem,
                         "event": "freeze", "detail": {"sha256": h, "hidden_sha256": hashlib.sha256(hb).hexdigest(),
                                                       "path": str(tf)}})
        if refused:
            raise TaskRefused("frozen task file(s) changed since freeze, refused: " + ", ".join(refused))
        if early:
            raise TaskRefused("Clean label(s) still provisional, nothing frozen: " + "; ".join(early))
        pool_hash = hashlib.sha256("\n".join("%s %s" % x for x in all_hashes).encode()).hexdigest()
        if recs:
            manifest = {t: d.get("sha256") for t, d in frozen.items()}
            manifest.update({r["task"]: r["detail"]["sha256"] for r in recs})
            recs.append({"ts": ts, "arm": "harness", "lane": None, "run_id": run_id, "task": None,
                         "event": "freeze", "detail": {"pool_sha256": pool_hash, "n": len(all_hashes),
                                                       "new": len(recs), "manifest": manifest}})
            _append_authority(p, recs)
            _append(p, recs)
    return {"frozen_new": max(len(recs) - 1, 0), "pool": len(all_hashes), "pool_sha256": pool_hash}


def load_frozen(task_id: str, p: dict | None = None, leaks: bool = True) -> dict:
    """The task as frozen, or TaskRefused. The judge and the gate call this; nothing reads a task file directly.
    The file is read ONCE: the returned task is parsed from the very bytes whose hash was checked. With `leaks`
    (the default) any hidden check readable by an arm refuses it too."""
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
        found = find_leaks(p)
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
    problems += find_leaks(p)
    return problems


# ---------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("census", help="scan the ledger, write task + judge files and a report")
    c.add_argument("--sanity", default=SANITY_ITEM, help="item the census must find (default %(default)s)")
    c.add_argument("--dry-run", action="store_true", help="report only; write no task files")
    sub.add_parser("freeze", help="hash every task file into the event log (before any assignment)")
    k = sub.add_parser("check", help="refuse changed, unfrozen, live:full or leaked tasks")
    k.add_argument("--task", nargs="+")
    b = sub.add_parser("clone", help="build an arm clone of a frozen task's base_sha (depth 1, no later history)")
    b.add_argument("task")
    b.add_argument("dest")
    a = ap.parse_args(argv)
    p = paths()
    try:
        if a.cmd == "census":
            pool, rep = census(sanity=a.sanity)
            rep["arena"] = str(p["root"])
            if not a.dry_run:
                rep["write"] = write_pool(pool, p)
                p["census"].mkdir(parents=True, exist_ok=True)
                rp = p["census"] / ("census_%s.json" % dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
                rp.write_bytes(_dump(rep))
                print("report:", rp)
            print(json.dumps({k: rep[k] for k in ("pool", "labels", "sanity", "scanned_closed_in_window")}))
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
            print(build_arm_clone(t["base_sha"], Path(a.dest), task=a.task))
            return 0
        if a.cmd == "freeze":
            print(json.dumps(freeze(p)))
            return 0
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
