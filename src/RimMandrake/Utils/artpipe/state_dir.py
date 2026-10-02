#!/usr/bin/env python3
"""state_dir.py — the ONE answer to "where does the artpipe queue live?"

The queue is runtime state, not source: it moved out of git on 2026-10-02
(git migration Phase 5, `design/RimMandrake/git_migration_phase5_artpipe_2026-10-02.md`).
Every reader and writer — the daemon, fill_queue, artreg, sheet builders, the
dashboard hub — resolves it here, never by joining a path onto the repo root.

Resolution order:
  1. `$ARTPIPE_STATE_DIR` if set (tests, a second machine, the launcher).
  2. `/mnt/d/Luke/dev/_artpipe` when `/mnt/d/Luke/dev` exists (Archmagi, WSL):
     on the Windows drive on purpose — codex.exe runs with its cwd in the
     per-job `_artsrc/<id>/` dir and fails from ext4 (plan §2.3).
  3. `<parent of this clone>/_artpipe` otherwise (a Mac: `~/dev/_artpipe`).
     The daemon does not run there, so it is usually absent — and an absent
     state dir must be reported as absent, never read as an empty queue.

Tracked config (`legibility_*.json`, `art_lists/`, README) stays in the repo at
`CONFIG_ROOT`. Deliberately stdlib-only and import-cheap: `common.py` imports
codex_image at import time, which a dashboard script must not pay for.
"""
from __future__ import annotations

import os
from pathlib import Path

ENV_VAR = "ARTPIPE_STATE_DIR"
WINDOWS_DEFAULT = Path("/mnt/d/Luke/dev/_artpipe")

# this file -> artpipe -> Utils -> RimMandrake -> src -> repo root.
REPO_ROOT = Path(__file__).resolve().parents[4]
CONFIG_ROOT = REPO_ROOT / "infrastructure" / "artpipe"

QUEUE_DIRS = ("pending", "active", "done", "failed")


def resolve(environ=None, windows_default: Path = WINDOWS_DEFAULT,
            repo_root: Path = REPO_ROOT) -> Path:
    env = os.environ if environ is None else environ
    v = env.get(ENV_VAR, "").strip()
    if v:
        return Path(v).expanduser()
    if windows_default.parent.is_dir():
        return windows_default
    return repo_root.parent / "_artpipe"


STATE_ROOT = resolve()


def require(root: Path | None = None) -> Path:
    """For READERS that would otherwise report 'found nothing': a missing
    state dir is an error, not an empty answer."""
    root = STATE_ROOT if root is None else root
    if not (root / "done").is_dir():
        raise SystemExit(f"artpipe state dir {root} has no done/ — wrong machine, or "
                         f"${ENV_VAR} unset/wrong. Not answering 'nothing found'.")
    return root


if __name__ == "__main__":
    print(STATE_ROOT)
