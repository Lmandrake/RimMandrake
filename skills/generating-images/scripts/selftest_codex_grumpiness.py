#!/usr/bin/env python3
"""Selftest for codex_grumpiness.py — zero quota, fixture rollout JSONL only."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import codex_grumpiness as G  # noqa: E402

TOTAL = 0
FAILURES = []


def check(name, cond):
    global TOTAL
    TOTAL += 1
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILURES.append(name)


def rollout_line(primary_pct, secondary_pct):
    # rate_limits is a SIBLING of info under payload, not nested inside it -
    # this fixture mirrors a real rollout line byte-for-byte on that point,
    # because the first version of this fixture (and the code) got it wrong.
    return json.dumps({
        "timestamp": "2026-09-07T18:18:24.849Z", "ordinal": 1, "type": "event_msg",
        "payload": {
            "type": "token_count",
            "info": {"total_token_usage": {"total_tokens": 1}, "model_context_window": 1},
            "rate_limits": {
                "limit_id": "codex", "limit_name": None,
                "primary": {"used_percent": primary_pct, "window_minutes": 300,
                            "resets_at": 1788822151},
                "secondary": {"used_percent": secondary_pct, "window_minutes": 10080,
                              "resets_at": 1789357637},
            }}}) + "\n"


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        sessions = home / "sessions" / "2026" / "09" / "07"
        sessions.mkdir(parents=True)

        # 1. No rollout at all -> ok:False, a stated reason, never a raise.
        r = G.read_meters(home)
        check("empty home -> ok:False with a reason", r["ok"] is False and "reason" in r)

        # 2. One rollout, calm reading.
        f1 = sessions / "rollout-2026-09-07T11-00-00-a.jsonl"
        f1.write_text(rollout_line(8.0, 2.0), encoding="utf-8")
        r = G.read_meters(home)
        check("calm reading parses ok", r["ok"] is True)
        check("calm reading not grumpy", r["grumpy"] is False)
        check("primary_used_percent read correctly", r["primary_used_percent"] == 8.0)
        check("secondary_resets_at read correctly", r["secondary_resets_at"] == 1789357637)

        # 3. LAST line in a file wins, not the first.
        f1.write_text(rollout_line(8.0, 2.0) + rollout_line(50.0, 3.0), encoding="utf-8")
        r = G.read_meters(home)
        check("last line in file wins over first", r["primary_used_percent"] == 50.0)

        # 4. A second, NEWER rollout is the one picked up (mtime, not filename order).
        time.sleep(0.05)
        f2 = sessions / "rollout-2026-09-07T09-00-00-b.jsonl"  # earlier timestamp in NAME
        f2.write_text(rollout_line(99.0, 99.0), encoding="utf-8")
        os.utime(f2, None)  # mtime = now, i.e. newer than f1 despite the name
        r = G.read_meters(home)
        check("newest-by-mtime file picked, not newest-by-name", r["primary_used_percent"] == 99.0)

        # 5. `after` filters out a stale rollout from a prior job on a reused home.
        cutoff = time.time() + 5  # nothing on disk is newer than 5s in the future
        r = G.read_meters(home, after_mtime=cutoff)
        check("`after` cutoff excludes every existing rollout", r["ok"] is False)

        # 6. grumpy fires on EITHER meter crossing its own threshold.
        f3 = sessions / "rollout-2026-09-07T12-00-00-c.jsonl"
        f3.write_text(rollout_line(G.GRUMPY_PRIMARY_PCT, 0.0), encoding="utf-8")
        os.utime(f3, None)
        r = G.read_meters(home)
        check("primary at its own threshold is grumpy", r["grumpy"] is True)

        f4 = sessions / "rollout-2026-09-07T13-00-00-d.jsonl"
        f4.write_text(rollout_line(0.0, G.GRUMPY_SECONDARY_PCT), encoding="utf-8")
        os.utime(f4, None)
        r = G.read_meters(home)
        check("secondary at its own threshold is grumpy", r["grumpy"] is True)

        # 7. A rollout with no token_count event at all -> ok:False, distinct reason.
        f5 = sessions / "rollout-2026-09-07T14-00-00-e.jsonl"
        f5.write_text(json.dumps({"type": "session_meta"}) + "\n", encoding="utf-8")
        os.utime(f5, None)
        r = G.read_meters(home)
        check("rollout with no rate_limits event -> ok:False", r["ok"] is False)

        # 8. A torn/partial trailing line must not raise.
        f6 = sessions / "rollout-2026-09-07T15-00-00-f.jsonl"
        f6.write_text(rollout_line(5.0, 1.0) + '{"payload":{"rate_limi', encoding="utf-8")
        os.utime(f6, None)
        r = G.read_meters(home)
        check("torn trailing line does not raise, calm reading still parses",
              r["ok"] is True and r["primary_used_percent"] == 5.0)

    if FAILURES:
        print("%d/%d FAILED: %s" % (len(FAILURES), TOTAL, ", ".join(FAILURES)))
        return 1
    print("%d/%d passed" % (TOTAL, TOTAL))
    return 0


if __name__ == "__main__":
    sys.exit(main())
