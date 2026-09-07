#!/usr/bin/env python3
"""codex_grumpiness.py — read the account rate-limit meters off a Codex rollout.

Every codex exec turn's rollout JSONL carries a `token_count` event whose
`payload.rate_limits` object (a SIBLING of `payload.info`, not nested inside
it - a truncated pretty-print looked nested on first read and cost one wrong
implementation before this file's own sanity check against a real rollout
caught it) is the SAME data `account/rateLimits/read` would return, already
measured and logged for free
(`$CODEX_HOME/sessions/YYYY/MM/DD/rollout-*.jsonl`, MEASURED 2026-09-07):

    {"payload": {"type": "token_count", "info": {...}, "rate_limits": {
        "primary":   {"used_percent": 8.0, "window_minutes": 300,   "resets_at": 1788822151},
        "secondary": {"used_percent": 2.0, "window_minutes": 10080, "resets_at": 1789357637},
        ...}}}

🔴 TOP RULE (CODEX_PARALLEL_WORKERS_1's addendum): a timeout is never evidence
of throttling. A ChatGPT-login throttle arrives as a fast, explicit
TooManyRequests error with no retry-after, and it can fire while these meters
still show headroom - read used_percent as a BUDGET GAUGE, not a predictor of
the next call's success.

No thresholds here are canon: CODEX_PARALLEL_WORKERS_1's own spec cites "the
addendum's six-row table" for these, but no such addendum was found on disk
when this was built (broken/missing reference, same as
`OPUS_REVIEW_codex_graphics_second_pipeline.md`). GRUMPY_PRIMARY_PCT/
GRUMPY_SECONDARY_PCT below are this file's own stated assumption, so a future
reader with the real table can override them without re-deriving the read
path, which is the part that was actually missing.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from pathlib import Path

# Assumption, not measured from the missing six-row table: past this primary
# (5-hour window) usage, treat the account as "grumpy" - degrade gracefully
# (smaller batches, lower reasoning effort) rather than push more load into it.
GRUMPY_PRIMARY_PCT = 80.0
# The secondary window is 7 days (10080 minutes) and is the harder ceiling to
# recover from, so it gets a lower bar.
GRUMPY_SECONDARY_PCT = 70.0


def sessions_dir(codex_home: Path) -> Path:
    return codex_home / "sessions"


def newest_rollout(codex_home: Path, after_mtime: float | None = None) -> Path | None:
    """The most recently modified rollout-*.jsonl under this CODEX_HOME.

    `after_mtime` filters to files touched at/after that time, so a queue
    worker with a long-lived CODEX_HOME reads THIS job's session, not a
    leftover from an earlier one on the same home.
    """
    pattern = str(sessions_dir(codex_home) / "**" / "rollout-*.jsonl")
    candidates = glob.glob(pattern, recursive=True)
    if not candidates:
        return None
    if after_mtime is not None:
        candidates = [c for c in candidates if os.path.getmtime(c) >= after_mtime - 1]
        if not candidates:
            return None
    return Path(max(candidates, key=os.path.getmtime))


def read_last_rate_limits(rollout_path: Path) -> dict | None:
    """The LAST rate_limits reading in the file - the freshest one for that turn.

    Returns None if the file has no token_count event yet (e.g. a turn that
    failed before its first assistant token), never raises on a torn/partial
    line - a rollout being actively written is a normal race, not a defect.
    """
    last = None
    try:
        with open(rollout_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or '"rate_limits"' not in line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                rl = (rec.get("payload") or {}).get("rate_limits")
                if rl:
                    last = rl
    except OSError:
        return None
    return last


def classify(rate_limits: dict) -> dict:
    """Turn a raw rate_limits reading into a decision-ready summary."""
    primary = rate_limits.get("primary") or {}
    secondary = rate_limits.get("secondary") or {}
    p_pct = primary.get("used_percent")
    s_pct = secondary.get("used_percent")
    grumpy = (p_pct is not None and p_pct >= GRUMPY_PRIMARY_PCT) or \
             (s_pct is not None and s_pct >= GRUMPY_SECONDARY_PCT)
    return {
        "primary_used_percent": p_pct,
        "primary_window_minutes": primary.get("window_minutes"),
        "primary_resets_at": primary.get("resets_at"),
        "secondary_used_percent": s_pct,
        "secondary_window_minutes": secondary.get("window_minutes"),
        "secondary_resets_at": secondary.get("resets_at"),
        "grumpy": grumpy,
    }


def read_meters(codex_home: Path, after_mtime: float | None = None) -> dict:
    """One call: find the newest rollout, read its last rate_limits, classify.

    Always returns a dict - `ok: False` with a `reason` string when nothing
    could be read, so a caller logs the ATTEMPT rather than skipping silently.
    """
    rollout = newest_rollout(codex_home, after_mtime)
    if rollout is None:
        return {"ok": False, "reason": "no rollout file found under this CODEX_HOME"}
    rl = read_last_rate_limits(rollout)
    if rl is None:
        return {"ok": False, "reason": "rollout has no token_count/rate_limits event yet",
                "rollout": str(rollout)}
    out = {"ok": True, "rollout": str(rollout)}
    out.update(classify(rl))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--codex-home", required=True, help="the worker's CODEX_HOME")
    ap.add_argument("--after", type=float, default=None,
                    help="only consider rollouts modified at/after this unix time")
    a = ap.parse_args()
    result = read_meters(Path(a.codex_home), a.after)
    print(json.dumps(result, indent=1))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
