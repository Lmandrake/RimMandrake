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
import datetime as dt
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
            "census": r / "census", "log": r / "events" / "harness.jsonl"}


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


def proof_for(files: list[str], added=frozenset()):
    """The proof an arm is told about, or None when the fix added no objective proof. A selftest the fix ADDED is a
    hidden check: it did not exist at base_sha, so naming it would leak it; the proof only says how many the judge
    holds. A selftest the fix CHANGED existed at base and is named."""
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
        if it.state != "done" or not closes:
            continue
        close = closes[-1]
        if not (window[0] <= _day(close.get("ts")) <= window[1]):
            continue
        scanned += 1
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
        proof = proof_for(files, {d[0] for d in diff if d[2] == "A"})
        if not proof:
            reject(iid, "no objective proof"); continue
        t_close = _epoch(close["ts"])
        rw = [r for r in reworks.get(iid, [])
              if r.created_at and 0 <= _epoch(r.created_at) - t_close <= ESCAPE_DAYS * 86400]
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
            if is_selftest(path):
                checks.append({"type": "fix_test", "path": path, "added": st == "A",
                               "command": "python3 src/RimMandrake/Utils/run_selftests.py --only " + path,
                               "body": _show(repo, fix, path)})
        rw_out = []
        for r in rw:
            rclose = [e for e in by_id.get(r.id, []) if e.get("event") == "close"]
            rfix = resolve(str(rclose[-1].get("sha") or ""))[0] if rclose else None
            prel = os.path.relpath(model.item_path(r.id), str(model.ROOT))
            entry = {"item": r.id, "title": r.title, "filed": r.created_at, "state": r.state, "fix_sha": rfix,
                     # pinned to the rework's own fix where there is one, so the judge bytes do not drift with HEAD
                     "prose": (_show(repo, rfix, prel) if rfix else None) or _show(repo, "HEAD", prel), "tests": []}
            if rfix and len(_parents(repo, rfix)) == 1:
                for path, _, st in _numstat(repo, _parents(repo, rfix)[0], rfix):
                    if is_selftest(path):
                        entry["tests"].append({"path": path, "added": st == "A", "body": _show(repo, rfix, path)})
            entry["needs_authoring"] = not entry["tests"]
            rw_out.append(entry)
            checks.append({"type": "escape_rework", "rework_item": r.id, "needs_authoring": not entry["tests"]})
        hidden = {"task": tid, "source_item": iid, "label": label, "fix_sha": fix, "ledger_sha": close.get("sha"),
                  "sha_resolution": how, "checks": checks,
                  "reworks": rw_out,
                  # a fixed instant, not a now-dependent boolean, so a re-census reproduces the frozen bytes; a label
                  # read before this instant can still flip to Escaped
                  "label_window_ends": dt.datetime.fromtimestamp(t_close + ESCAPE_DAYS * 86400, dt.timezone.utc)
                  .strftime("%Y-%m-%dT%H:%M:%SZ")}
        task = {"id": tid, "source_item": iid, "kind": kind, "size": size_points(len(diff), lines),
                "size_basis": {"files": len(diff), "lines": lines}, "area": area_for(files), "prompt": prompt,
                "criteria": crit, "criteria_source": crit_src, "proof": proof, "live": "none",
                "hidden_checks": None, "base_sha": base}
        own = [tok for tok in leak_tokens(hidden) if tok in json.dumps(task)]
        if own:
            raise ArenaError("census bug: task %s would carry its own hidden check %r" % (tid, own[0][:60]))
        pool.append((close["ts"], task, hidden))

    # Chains: a later pool task's public file can name an earlier one's hidden check (it IS the earlier item's rework,
    # or it edits a test that rework added). An arm reading it would learn the earlier task's label or check, so in
    # close order the earlier task is kept and the later one rejected.
    kept_pool, seen = [], []
    for _, task, hidden in sorted(pool, key=lambda x: x[0]):
        pub = json.dumps(dict(task, base_sha=None))   # starting where an earlier fix landed is history, not a leak
        hit = next((h["task"] for h in seen if any(tok in pub for tok in leak_tokens(h))), None)
        if hit:
            reject(task["source_item"], "would expose a hidden check of earlier pool task " + hit)
            continue
        seen.append(hidden)
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
    """Write task + judge files. A frozen task is never rewritten: identical content is skipped, a change refused."""
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
            "withdrawn_unfrozen": sorted(set(stale))}


# ---------------------------------------------------------------- event log

def read_log(p: dict) -> list[dict]:
    out = []
    if not p["events"].is_dir():
        return out
    for f in sorted(p["events"].glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(json.loads(line))
    return out


def frozen_hashes(p: dict) -> dict:
    """task -> its FIRST freeze detail. The first freeze is the contract; nothing later can move it."""
    out = {}
    for ev in read_log(p):
        if ev.get("event") == "freeze" and ev.get("task") and ev["task"] not in out:
            out[ev["task"]] = ev.get("detail") or {}
    return out


def _append(p: dict, recs: list[dict]):
    p["events"].mkdir(parents=True, exist_ok=True)
    with open(p["log"], "a", encoding="utf-8") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        for r in recs:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


# ---------------------------------------------------------------- validation

def validate_task(task: dict, hidden_path: Path, p: dict):
    """Refuse a task spec the trial may not run. Raises TaskRefused."""
    tid = task.get("id")
    for k in ("id", "source_item", "kind", "size", "area", "prompt", "criteria", "proof", "live", "base_sha"):
        if task.get(k) in (None, "", []):
            raise TaskRefused("%s: field %s missing" % (tid, k))
    if task["live"] not in LIVE_OK:
        raise TaskRefused("%s: live %r refused: the trial runs on the minimal list only (owner 2026-10-29); "
                          "allowed %s" % (tid, task["live"], ", ".join(LIVE_OK)))
    if task["kind"] not in KINDS:
        raise TaskRefused("%s: kind %r unknown" % (tid, task["kind"]))
    if task["size"] not in (1, 2, 4):
        raise TaskRefused("%s: size %r is not 1, 2 or 4" % (tid, task["size"]))
    hc = task.get("hidden_checks")
    if not isinstance(hc, dict) or set(hc) != {"held_by", "sha256"}:
        raise TaskRefused("%s: hidden_checks must be only a {held_by, sha256} stub; the checks live in the "
                          "judge's directory" % tid)
    if any(k in task for k in HIDDEN_KEYS):
        raise TaskRefused("%s: judge-only key in an arm-readable task file" % tid)
    if not hidden_path.is_file():
        raise TaskRefused("%s: judge file missing" % tid)
    if sha256_file(hidden_path) != hc["sha256"]:
        raise TaskRefused("%s: judge file changed since the task was written" % tid)


def leak_tokens(hidden: dict) -> list[str]:
    """Strings whose presence on an arm-readable path means a hidden check leaked: the fix sha, rework ids, the
    path of every test the fix or a rework ADDED (one it changed was visible at base anyway), and stored bodies."""
    toks = []
    if hidden.get("fix_sha"):
        toks.append(hidden["fix_sha"][:12])
    for c in hidden.get("checks", []):
        if c.get("type") == "fix_test" and c.get("added"):
            toks.append(c["path"])
        if c.get("body") and len(c["body"].strip()) >= 40:
            toks.append(c["body"].strip()[:400])
    for r in hidden.get("reworks", []):
        toks.append(r["item"])
        for t in r.get("tests", []):
            if t.get("added"):
                toks.append(t["path"])
            if t.get("body") and len(t["body"].strip()) >= 40:
                toks.append(t["body"].strip()[:400])
    return [t for t in toks if t]


def _tracked(top: Path) -> set:
    """Files git tracks in a clone work tree: their content is fixed by the checked-out commit (a task's base_sha),
    so a hidden token there is the pool's own history (an earlier task's fix), not a harness leak."""
    try:
        r = subprocess.run(["git", "-C", str(top), "ls-files", "-z"], capture_output=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return set()
    return {str(top / f) for f in r.stdout.decode("utf-8", "replace").split("\0") if f} if r.returncode == 0 else set()


def find_leaks(p: dict, max_bytes=4 << 20) -> list[str]:
    """Scan every arm-readable root for any hidden check's tokens; also refuse a judge dir inside one.

    Scope, so that the pool's own history is not called a leak: a task's own file is scanned for all its tokens; in
    every other file a fix sha that is some task's base_sha is not a token (task B legitimately starts where task A's
    fix landed); files git tracks inside a clone are skipped (see _tracked). Untracked and ignored files in a clone,
    the tasks dir and the event log are scanned for every token."""
    leaks = []
    roots = arm_readable_roots(p)
    for r in roots:
        if _inside(p["judge"], r):
            leaks.append("judge directory %s is inside arm-readable %s" % (p["judge"], r))
    toks, shas = {}, {}
    if p["judge"].is_dir():
        for hf in sorted(p["judge"].glob("*.json")):
            try:
                h = json.loads(hf.read_text(encoding="utf-8"))
            except (OSError, ValueError) as e:
                leaks.append("judge file %s unreadable: %s" % (hf, e))
                continue
            for t in leak_tokens(h):
                toks.setdefault(t, hf.stem)
            if h.get("fix_sha"):
                shas[h["fix_sha"][:12]] = hf.stem
    if not toks:
        return leaks
    bases = set()
    for tf in p["tasks"].glob("*.json") if p["tasks"].is_dir() else []:
        try:
            bases.add(str(json.loads(tf.read_text(encoding="utf-8")).get("base_sha") or "")[:12])
        except (OSError, ValueError):
            pass
    shared = {t for t, own in shas.items() if t in bases}
    tracked = set()
    for r in roots:
        if not r.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(r):
            dirnames[:] = [d for d in dirnames if d != ".git" and not _inside(Path(dirpath) / d, p["judge"])]
            if (Path(dirpath) / ".git").exists():
                tracked |= _tracked(Path(dirpath))          # top-down walk: covers the whole clone below
            for fn in filenames:
                fp = Path(dirpath) / fn
                if str(fp) in tracked:
                    continue
                try:
                    if fp.stat().st_size > max_bytes:
                        continue
                    txt = fp.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                for t, owner in toks.items():
                    if t in shared and fp.stem != owner:
                        continue
                    if t in txt:
                        leaks.append("%s: hidden check of %s readable at %s" % (owner, owner, fp))
                        break
    return leaks


# ---------------------------------------------------------------- freeze / check

def freeze(p: dict, now=None) -> dict:
    if any(ev.get("event") == "assign" for ev in read_log(p)):
        raise TaskRefused("an assign event is already in the log: freezing after assignment is refused (§1.1)")
    leaks = find_leaks(p)
    if leaks:
        raise TaskRefused("hidden checks reachable by an arm, nothing frozen:\n  " + "\n  ".join(leaks[:20]))
    frozen = frozen_hashes(p)
    ts = now or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    run_id = "freeze-" + ts
    recs, all_hashes, refused = [], [], []
    files = sorted(p["tasks"].glob("*.json")) if p["tasks"].is_dir() else []
    if not files:
        raise TaskRefused("no task files under %s" % p["tasks"])
    for tf in files:
        task = json.loads(tf.read_text(encoding="utf-8"))
        if task.get("id") != tf.stem:
            raise TaskRefused("%s: id %r does not match its file name" % (tf, task.get("id")))
        hp = p["judge"] / tf.name
        validate_task(task, hp, p)
        h = sha256_file(tf)
        all_hashes.append((tf.stem, h))
        if tf.stem in frozen:
            if frozen[tf.stem].get("sha256") != h:
                refused.append(tf.stem)
            continue
        recs.append({"ts": ts, "arm": "harness", "lane": None, "run_id": run_id, "task": tf.stem, "event": "freeze",
                     "detail": {"sha256": h, "hidden_sha256": sha256_file(hp), "path": str(tf)}})
    if refused:
        raise TaskRefused("frozen task file(s) changed since freeze, refused: " + ", ".join(refused))
    pool_hash = hashlib.sha256("\n".join("%s %s" % x for x in all_hashes).encode()).hexdigest()
    if recs:
        recs.append({"ts": ts, "arm": "harness", "lane": None, "run_id": run_id, "task": None, "event": "freeze",
                     "detail": {"pool_sha256": pool_hash, "n": len(all_hashes), "new": len(recs)}})
        _append(p, recs)
    return {"frozen_new": max(len(recs) - 1, 0), "pool": len(all_hashes), "pool_sha256": pool_hash}


def load_frozen(task_id: str, p: dict | None = None) -> dict:
    """The task as frozen, or TaskRefused. The judge and the gate call this; nothing reads a task file directly."""
    p = p or paths()
    fz = frozen_hashes(p).get(task_id)
    tf = p["tasks"] / (task_id + ".json")
    if not fz:
        raise TaskRefused("%s: not frozen" % task_id)
    if not tf.is_file():
        raise TaskRefused("%s: frozen but its file is gone" % task_id)
    if sha256_file(tf) != fz.get("sha256"):
        raise TaskRefused("%s: task file hash %s != frozen %s: refused" % (task_id, sha256_file(tf)[:12],
                                                                           str(fz.get("sha256"))[:12]))
    hp = p["judge"] / tf.name
    if not hp.is_file() or sha256_file(hp) != fz.get("hidden_sha256"):
        raise TaskRefused("%s: judge file changed since freeze: refused" % task_id)
    task = json.loads(tf.read_text(encoding="utf-8"))
    validate_task(task, hp, p)
    return task


def check(p: dict, only=None) -> list[str]:
    problems = []
    names = set(only or [])
    if not names:
        names = set(frozen_hashes(p)) | ({f.stem for f in p["tasks"].glob("*.json")} if p["tasks"].is_dir() else set())
    for t in sorted(names):
        try:
            load_frozen(t, p)
        except (TaskRefused, ValueError) as e:
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
            if rep.get("write", {}).get("refused_frozen_changed"):
                print("REFUSED: frozen tasks would change:", rep["write"]["refused_frozen_changed"])
                return 1
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
