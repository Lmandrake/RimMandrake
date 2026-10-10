#!/usr/bin/env python3
"""rimflow/gitindex.py — which commits on the PUBLISHED branch name which item.

WHY THIS EXISTS (rimflow redesign step 1, 2026-10-07)
=====================================================
`rimflow next` used to be a pure function of the ledger, and the evidence that an item
is already built lives in git. Measured 2026-10-07: 186 of the 272 ready+doing items
were named in a commit subject, and SALVAGE_WRECKAGE_EVERYWHERE_1 was claimed twice by
FOUNDRY with four build commits in between while `next` kept offering it as fresh work.
(`design/RimMandrake/rimflow_system_and_stuck_state_2026-10-07.md` §2.4, §3.8.)

This module is the git half of the fix: ONE batched `git log` pass over the published
ref, cached by that ref's head sha, mapping every item id named in a commit SUBJECT or a
`Closes:` / `Implemented:` line to the commits that name it. `reconcile.py` joins it with
the ledger; `next` and the rendered queue use that join.

🔑 RULES THIS MODULE KEEPS
- **Published ref only** (`origin/main`). A commit that exists only in a local clone is
  not evidence that work shipped (review §2). Nothing here fetches: the ref is as fresh
  as the clone's last fetch, and every output names the ref and its head so a reader
  can tell.
- **A subject match is a TRIGGER, never a verdict.** Nothing here closes, starts or
  changes anything. It only says "these commits name this item".
- **Bookkeeping commits are not evidence.** A commit whose every changed path is under
  `infrastructure/state/` or `Transient/` (a ledger sync, a handoff, a review sheet)
  names items without building them; it is indexed but flagged, and `matches()` skips it.
- **Searched from item creation, not from the last event** (review §1): a build followed
  by a note or a re-claim must still be found. The caller passes the item's `created_at`.
- **Never raises into a caller.** No git, no ref, a corrupt cache: the answer is None and
  `next` behaves exactly as it did before this module existed.

SEAMS FOR TESTS
===============
`RIMFLOW_GITINDEX=off` disables it. `RIMFLOW_GITINDEX=<path.json>` loads a FIXTURE of raw
commits (`{"ref", "head", "commits": [{"sha","ts","subject","body","files"}]}`), parsed by
the same code as real `git log` output. With neither, a REDIRECTED ledger
(`RIMFLOW_LEDGER`, i.e. every selftest) gets None — synthetic item ids must never be
matched against this repo's real history.
"""
import calendar
import json
import os
import re
import subprocess
import time

try:
    from . import model
except ImportError:                                         # script invocation
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from rimflow import model                               # noqa: E402

REF = "origin/main"
CACHE_NAME = "rimflow-gitindex.json"          # under the git dir: per clone, never tracked
BOOKKEEPING_PREFIXES = ("infrastructure/state/", "Transient/")
TRAILER_RE = re.compile(r"^\s*(Closes|Implemented)\s*:\s*(.+?)\s*$", re.I | re.M)
TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")
# Strength of a mention, strongest last: a trailer is a stated claim, a subject an association.
HOW_RANK = {"subject": 0, "closes": 1, "implemented": 2}
SUBJECT_KEEP = 100
VERSION = 3          # 3: ids_in also reads SUBJECT_INTENT_TWIST ids (2026-10-10)


# ---------------------------------------------------------------------------
# PARSING — shared by real `git log` output and test fixtures
# ---------------------------------------------------------------------------
def ids_in(text):
    """-> [id] of every named item id (legacy `_N` or SUBJECT_INTENT_TWIST) in `text`,
    in order, deduped. A new-form token needs an intent-word hinge, so a constant like
    MAX_FLIGHT_TIME is not mistaken for an item."""
    out = []
    for tok in TOKEN_RE.findall(text or ""):
        if model.is_named_id(tok) and tok not in out:
            out.append(tok)
    return out


def _bookkeeping(files):
    files = [f for f in (files or []) if f]
    return bool(files) and all(f.startswith(BOOKKEEPING_PREFIXES) for f in files)


def parse_commit(sha, ts, subject, body, files):
    """-> a compact record, or None when the commit names no item.

    record = [sha, ts_utc, subject, bookkeeping, {id: how}]
    """
    named = {}
    for iid in ids_in(subject):
        named[iid] = "subject"
    for m in TRAILER_RE.finditer(body or ""):
        how = m.group(1).lower()
        for iid in ids_in(m.group(2)):
            if HOW_RANK[how] > HOW_RANK.get(named.get(iid), -1):
                named[iid] = how
    if not named:
        return None
    return [sha, ts, (subject or "")[:160], _bookkeeping(files), named]


def _utc(epoch):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(int(epoch)))


def _parse_log(out):
    """Parse `git log --format=%x1e%H%x1f%ct%x1f%s%x1f%b%x1f --name-only` output.

    -> (named, every): `named` the compact records of commits that name an item;
    `every` one [sha, ts, subject] row per commit, so a sha a ledger NOTE cites can be
    shown to be on the published ref (WEBWORK_TRACTION_LANCE_BUILD_1's build commit
    598dec613 names no item at all; only the item's own note cites it)."""
    named, every = [], []
    for chunk in out.split("\x1e")[1:]:
        parts = chunk.split("\x1f")
        if len(parts) < 5:
            continue
        sha, ct, subject, body, files = parts[0], parts[1], parts[2], parts[3], parts[4]
        try:
            ts = _utc(ct)
        except ValueError:
            continue
        sha = sha.strip()
        every.append([sha, ts, subject[:SUBJECT_KEEP]])
        rec = parse_commit(sha, ts, subject, body,
                           [f.strip() for f in files.splitlines() if f.strip()])
        if rec:
            named.append(rec)
    return named, every


# ---------------------------------------------------------------------------
# GIT — one batched pass, cached by head sha, extended incrementally
# ---------------------------------------------------------------------------
_LOG_FORMAT = "--format=%x1e%H%x1f%ct%x1f%s%x1f%b%x1f"


def _git(root, *args):
    try:
        return subprocess.check_output(("git",) + args, cwd=root,
                                       stderr=subprocess.DEVNULL).decode("utf-8", "replace")
    except (subprocess.CalledProcessError, OSError):
        return None


def _log(root, rng):
    out = _git(root, "log", rng, _LOG_FORMAT, "--name-only", "--no-renames")
    return None if out is None else _parse_log(out)


def _cache_path(root):
    p = _git(root, "rev-parse", "--git-path", CACHE_NAME)
    if not p or not p.strip():
        return None
    p = p.strip()
    return p if os.path.isabs(p) else os.path.join(root, p)


def _read_cache(path):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if data.get("version") == VERSION and isinstance(data.get("commits"), list) \
                and isinstance(data.get("every"), list):
            return data
    except (OSError, ValueError, AttributeError):
        pass
    return None


def _write_cache(path, data):
    """Atomic: a reader never sees a half-written cache. Failure is silent — the cache
    is a speed-up, and the next call simply rebuilds it."""
    tmp = "%s.%d.tmp" % (path, os.getpid())
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, separators=(",", ":"))
        os.replace(tmp, path)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def build(root=None, ref=REF, write_cache=True):
    """-> Index for `ref` in the repo at `root`, or None if git or the ref is unavailable.

    Cost: `rev-parse` + a json read when the cache is current; `git log old..new` when
    the ref moved forward; one full `git log` (~0.2 s for 12.7k commits on ext4,
    measured 2026-10-07) otherwise.
    """
    root = root or model.ROOT
    head = _git(root, "rev-parse", "--verify", "-q", ref + "^{commit}")
    head = head.strip() if head else ""
    if not head:
        return None
    cpath = _cache_path(root)
    cached = _read_cache(cpath) if cpath else None
    if cached and cached.get("ref") == ref and cached.get("head") == head:
        return Index(ref, head, cached["commits"], cached["every"])
    got = None
    if cached and cached.get("ref") == ref and cached.get("head"):
        old = cached["head"]
        # Only extend when the cached head is an ANCESTOR (the ref moved forward).
        # Anything else — a rewritten ref, a different clone's cache — rebuilds whole.
        if _git(root, "merge-base", "--is-ancestor", old, head) is not None:
            new = _log(root, "%s..%s" % (old, head))
            if new is not None:
                got = (new[0] + cached["commits"], new[1] + cached["every"])
    if got is None:
        got = _log(root, head)
        if got is None:
            return None
    if write_cache and cpath:
        _write_cache(cpath, {"version": VERSION, "ref": ref, "head": head,
                             "commits": got[0], "every": got[1]})
    return Index(ref, head, got[0], got[1])


def from_fixture(path):
    """-> Index from a JSON fixture of RAW commits (the test seam). Parsed by the same
    `parse_commit` as real log output, so a fixture exercises the parser too."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    recs, every = [], []
    for c in data.get("commits", []):
        every.append([c["sha"], c["ts"], c.get("subject", "")[:SUBJECT_KEEP]])
        rec = parse_commit(c["sha"], c["ts"], c.get("subject", ""), c.get("body", ""),
                           c.get("files", []))
        if rec:
            recs.append(rec)
    return Index(data.get("ref", "fixture"), data.get("head", "fixture"), recs, every)


def _ledger_is_real(events_path=None):
    """True when rimflow is reading the production ledger, not a redirected one."""
    real = os.path.abspath(os.path.join(model.LEDGER, "events.jsonl"))
    used = os.path.abspath(events_path or model.EVENTS)
    return used == real


def for_ledger(events_path=None, write_cache=True):
    """-> the Index `next` and the queue render should use, or None. Never raises.

    `RIMFLOW_GITINDEX=off` -> None; `=<file.json>` -> that fixture; otherwise the real
    repo's `origin/main`, but ONLY when the ledger in use is the real one (see header).
    """
    seam = os.environ.get("RIMFLOW_GITINDEX", "").strip()
    try:
        if seam.lower() == "off":
            return None
        if seam:
            return from_fixture(seam)
        if not _ledger_is_real(events_path):
            return None
        return build(model.ROOT, REF, write_cache=write_cache)
    except Exception:                                       # noqa: BLE001
        return None


# ---------------------------------------------------------------------------
# THE INDEX
# ---------------------------------------------------------------------------
class Match(object):
    __slots__ = ("sha", "ts", "subject", "how", "bookkeeping")

    def __init__(self, sha, ts, subject, how, bookkeeping):
        self.sha, self.ts, self.subject = sha, ts, subject
        self.how, self.bookkeeping = how, bookkeeping

    @property
    def short(self):
        return self.sha[:9]

    def __repr__(self):
        return "<Match %s %s>" % (self.short, self.how)


class Index(object):
    """id -> [Match] (commits that NAME the item), plus every commit on the ref so a
    sha cited in a ledger note can be resolved and shown to be published."""

    def __init__(self, ref, head, commits, every=()):
        self.ref, self.head = ref, head
        self.by_id = {}
        for sha, ts, subject, bk, named in commits:
            for iid, how in named.items():
                self.by_id.setdefault(iid, []).append(Match(sha, ts, subject, how, bk))
        self._by7 = {}
        for sha, ts, subject in every:
            self._by7.setdefault(sha[:7], []).append((sha, ts, subject))

    def matches(self, iid, since=None, include_bookkeeping=False):
        """-> [Match] naming `iid`, committed at or after `since` (the item's creation
        ts, UTC ISO), oldest first. Bookkeeping-only commits are skipped by default."""
        out = []
        for m in self.by_id.get(iid, ()):
            if m.bookkeeping and not include_bookkeeping:
                continue
            if since and m.ts < since:
                continue
            out.append(m)
        out.sort(key=lambda m: m.ts)
        return out

    def resolve(self, prefix, how="note"):
        """-> Match for a UNIQUE sha prefix (>= 7 hex) on the published ref, else None.
        An ambiguous or unpublished prefix is None — it proves nothing."""
        prefix = (prefix or "").lower()
        if len(prefix) < 7:
            return None
        hits = [h for h in self._by7.get(prefix[:7], ()) if h[0].startswith(prefix)]
        if len(hits) != 1:
            return None
        sha, ts, subject = hits[0]
        return Match(sha, ts, subject, how, False)


if __name__ == "__main__":                                  # quick manual probe
    import sys
    idx = build()
    if idx is None:
        print("no index (git or %s unavailable)" % REF)
        sys.exit(1)
    print("%s @ %s: %d ids named" % (idx.ref, idx.head[:9], len(idx.by_id)))
    for iid in sys.argv[1:]:
        for m in idx.matches(iid, include_bookkeeping=True):
            print("  %s %s %-11s %s%s" % (m.short, m.ts, m.how, m.subject[:80],
                                         "  [bookkeeping]" if m.bookkeeping else ""))
