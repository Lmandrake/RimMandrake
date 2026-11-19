#!/usr/bin/env python3
"""The account-budget panel streams.py's budget measure reads: config() from ~/.claude-accounts/budget.json (or
$RM_BUDGET_CONF; this file names no account) and panel() over usage.json. The fetchers that wrote usage.json ran in
the RimPulse daemon and went with the dashboard (RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES);
Utils/account_usage.py measures the accounts now.

The rule (design/RimMandrake/standing_rulings.md §Account and capacity budget, owner 2026-10-25 by card): the owned
accounts may be fully used each WEEK, with a rough daily share; keep a reserve for evening sessions with him; the spare
account only after both owned ones are spent, and never past about half of it; watch GPT capacity too.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ACCOUNTS_DIR = Path(os.environ.get("RM_ACCOUNTS_DIR", Path.home() / ".claude-accounts"))

FRESH = 20 * 60        # a reading older than this is shown as "as of <time>", never as now


def config() -> dict:
    p = Path(os.environ.get("RM_BUDGET_CONF") or ACCOUNTS_DIR / "budget.json")
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return {}


def panel(st: dict, cfg: dict, now: float) -> dict:
    """The snapshot's `charts.usage`: one row per account (state measured | stale | unknown) + codex."""
    rows = []
    spare = cfg.get("spare") or {}
    for n in list(cfg.get("owned") or []) + list(spare):
        a = (st.get("accounts") or {}).get(n) or {}
        w = a.get("week")
        state = "unknown" if not w else "measured" if now - (a.get("measured_at") or 0) <= FRESH else "stale"
        rows.append({"name": n, "role": "spare" if n in spare else "owned", "cap": spare.get(n),
                     "state": state, "pct": (w or {}).get("pct"), "resets_at": (w or {}).get("resets_at"),
                     "five_pct": (a.get("five") or {}).get("pct"), "measured_at": a.get("measured_at"),
                     "why": a.get("why") or ""})
    cx = st.get("codex")
    return {"at": now, "accounts": rows, "codex": cx, "evening_from": cfg.get("evening_from", 18),
            "evening_share": cfg.get("evening_share", 0.4)}
