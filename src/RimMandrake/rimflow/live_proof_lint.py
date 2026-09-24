#!/usr/bin/env python3
"""CLOSE_OWED_LIVE_PROOF_1 — detect a close whose debt lives only in prose.

THE DEFECT
==========
A close can be entirely legitimate on offline evidence (`dotnet build`,
`validate_patch`, selftests) and still owe live proof, a deploy, or follow-on
work. That debt gets named in the CLOSING COMMIT'S MESSAGE and nowhere else —
no queue, dashboard or `rimflow next` ever reads a commit body, so the moment
the session ends nobody is looking for it. MEASURED 2026-09-20 against two
real closes (`ALPHA_MECHANICS_KIT_1` at 636192203, `BRAINWORM_MOD_BUILD_1` at
2e7aa9cff) — both told the truth in prose that nothing durable then read.

THE FIX
=======
`rimflow spawn --from <run> --for <seat> --name <ID>` already exists and was
simply never reached for at close time. This module is the shared detector
used by both:

  - the sweep (`python3 live_proof_lint.py sweep`) — the whole-ledger baseline
    the item's `verify` block asks for.
  - the hook (`.claude/hooks/warn_close_live_proof_owed.py`) — catches a NEW
    close matching the same shape, before it lands.

WARN, NOT REFUSE — the item's own spec, verbatim: "the honest wording is the
signal, and a hook that punishes it would teach seats to stop writing it,
which is strictly worse than the defect." Nothing here ever blocks a close;
it only tells a future reader (or the closing seat, right then) that the debt
named in the commit has nowhere else to live.

WHAT COUNTS AS A SPAWNED SUCCESSOR
===================================
`rimflow spawn --from X --for SEAT --name Y` records `from: X` — see
`cmd_spawn` in cli.py, "`from` IS the causal link". A closed item ID counts as
having a successor if ANY spawn event anywhere in the ledger names it (or a
run under it, `ID/run-N@env`) as `from` — at any time, by any seat. This is
deliberately NOT scoped to "spawned before this exact close event": the rule
going forward is "in the same sitting, before the close", but detection over
old history only needs to know a successor exists somewhere, not exactly when.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
LEDGER = os.path.join(ROOT, "infrastructure", "state", "ledger", "events.jsonl")

# The four phrases named in the item's `spec`. Matched case-insensitively —
# "Deploy owed." at a sentence start is exactly as real as "deploy owed".
PHRASES = (
    "live proof owed",
    "live proof still owed",
    "deploy owed",
    "follow-on work",
)
PHRASE_RE = re.compile("|".join(re.escape(p) for p in PHRASES), re.I)


def commit_body(root, sha):
    """-> the full commit message body for `sha`, or None if it can't be read.

    `sha` may be the short form `rimflow close` defaults to (`head_sha()` in
    cli.py uses `--short`) — `git show` resolves an abbreviated sha fine.
    """
    if not sha:
        return None
    try:
        p = subprocess.run(["git", "-C", root, "show", "-s", "--format=%B", sha],
                           capture_output=True, text=True, timeout=8)
    except (OSError, subprocess.SubprocessError):
        return None
    return p.stdout if p.returncode == 0 else None


def _ledger_paths(path):
    """-> the ledger head plus every per-seat shard beside it.

    🔴 THE LEDGER IS SEVERAL FILES since 2026-09-23. `events.jsonl` is frozen history
    and every new event lands in `events/<SEAT>.jsonl` (the authority is
    `rimflow.model.SHARD_DIR`; this file stays stdlib-only and import-free because the
    `.claude/hooks/` guard imports it, so the pattern is duplicated on purpose). Reading
    the head alone would make this lint blind to every close and every spawn written
    since the cutover — and its whole job is to notice a MISSING spawn, so going blind
    reads as "all clear".
    """
    paths = [path]
    d = os.path.join(os.path.dirname(path) or ".", "events")
    try:
        paths += [os.path.join(d, n) for n in sorted(os.listdir(d))
                  if n.endswith(".jsonl")]
    except OSError:
        pass
    return paths


def _read_events(path):
    """-> every event across the ledger head and its shards, ordered by `ts`."""
    out = []
    for p in _ledger_paths(path):
        out.extend(_read_one(p))
    # `str(...)`: a non-string stamp must not raise TypeError inside a lint. Stable
    # sort, so each file's own order survives a tie — same rule as `model.read()`.
    out.sort(key=lambda e: str(e.get("ts") or ""))
    return out


def _read_one(path):
    out = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except ValueError:
                    continue           # a torn line: skip it, never crash the lint
    except OSError:
        pass
    return out


def close_events(path=None):
    """-> every `close` event, in ledger order."""
    return [ev for ev in _read_events(path or LEDGER)
            if ev.get("event") == "close" and ev.get("id")]


def spawn_froms(path=None):
    """-> the raw list of every `from` value across every `spawn` event ever."""
    return [str(ev["from"]) for ev in _read_events(path or LEDGER)
            if ev.get("event") == "spawn" and ev.get("from")]


def has_spawned_successor(iid, froms):
    """-> True if some spawn's `from` names `iid` itself or a run under it."""
    prefix = iid + "/"
    return any(f == iid or f.startswith(prefix) for f in froms)


def matched_phrase(body):
    """-> the first matched phrase in `body`, or None."""
    m = PHRASE_RE.search(body or "")
    return m.group(0).lower() if m else None


def offline_only_unspawned_closes(root=None, ledger=None):
    """-> [(id, sha, seat, phrase), ...] for every close whose commit body names
    live-proof debt and has no spawned successor anywhere in the ledger.

    This is the whole-ledger sweep the item's `verify` block asks for: "every
    close event whose commit body matches those phrases, joined against
    spawned successors."
    """
    root = root or ROOT
    ledger = ledger or LEDGER
    froms = spawn_froms(ledger)
    out = []
    for ev in close_events(ledger):
        iid, sha = ev["id"], ev.get("sha")
        phrase = matched_phrase(commit_body(root, sha))
        if not phrase:
            continue
        if has_spawned_successor(iid, froms):
            continue
        out.append((iid, sha, ev.get("seat"), phrase))
    return out


def _sweep_main():
    hits = offline_only_unspawned_closes()
    print("CLOSE_OWED_LIVE_PROOF_1 baseline sweep — whole ledger, %d close event(s) "
          "checked." % len(close_events(LEDGER)))
    print("%d close(s) name live-proof debt in the commit body with no spawned "
          "successor:\n" % len(hits))
    for iid, sha, seat, phrase in hits:
        print("  %-42s %-9s %-8s %r" % (iid, sha or "(no sha)", seat or "?", phrase))
    return 0


if __name__ == "__main__":
    sys.exit(_sweep_main())
