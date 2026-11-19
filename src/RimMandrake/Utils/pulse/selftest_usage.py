#!/usr/bin/env python3
"""Selftest for usage.py's panel and config, the part streams.py's budget measure reads: a reading is measured,
stale or unknown by its age, never shown as measured without one. Fixture state only; no network, no credentials.
(Its fetcher checks went with the fetchers, RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES.)"""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(tempfile.mkdtemp(prefix="st_usage_"))
os.environ["RM_ACCOUNTS_DIR"] = str(ROOT / "acc")
os.environ.pop("RM_BUDGET_CONF", None)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import usage  # noqa: E402

FAILS = []
NOW = 1_792_900_000.0
DAY = 86400


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        FAILS.append(name)


CFG = {"owned": ["own_a", "own_b"], "spare": {"spare_c": 0.5}, "evening_share": 0.4}
ST = {"accounts": {"own_a": {"week": {"pct": 12.0, "resets_at": NOW + DAY}, "five": {"pct": 5.0}, "measured_at": NOW - 60},
                   "own_b": {"week": {"pct": 93.0, "resets_at": NOW + DAY}, "measured_at": NOW - 2 * usage.FRESH,
                             "why": "token expired"},
                   "spare_c": {"why": "no stored credentials"}},
      "codex": {"pct": 40.0}}
p = usage.panel(ST, CFG, NOW)
rows = {r["name"]: r for r in p["accounts"]}
check("owned accounts first, then the spare, each once", [r["name"] for r in p["accounts"]] == ["own_a", "own_b", "spare_c"], p)
check("a fresh reading is measured, with its numbers", rows["own_a"]["state"] == "measured" and rows["own_a"]["pct"] == 12.0
      and rows["own_a"]["five_pct"] == 5.0, rows["own_a"])
check("a reading older than FRESH is stale, never measured", rows["own_b"]["state"] == "stale"
      and rows["own_b"]["why"] == "token expired", rows["own_b"])
check("no reading at all is unknown with no number", rows["spare_c"]["state"] == "unknown" and rows["spare_c"]["pct"] is None,
      rows["spare_c"])
check("the spare carries its role and cap", rows["spare_c"]["role"] == "spare" and rows["spare_c"]["cap"] == 0.5
      and rows["own_a"]["role"] == "owned", rows)
check("codex and the evening rule pass through", p["codex"] == {"pct": 40.0} and p["evening_share"] == 0.4
      and p["evening_from"] == 18, p)
check("an empty state is every account unknown", {r["state"] for r in usage.panel({}, CFG, NOW)["accounts"]} == {"unknown"})
check("no budget.json is an empty config, not a crash", usage.config() == {})
(ROOT / "acc").mkdir(parents=True)
(ROOT / "acc" / "budget.json").write_text(json.dumps(CFG))
check("budget.json is read from the accounts dir", usage.config() == CFG, usage.config())
(ROOT / "acc" / "budget.json").write_text("{torn")
check("an unreadable budget.json is an empty config", usage.config() == {})

print(f"\n{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failing")
sys.exit(1 if FAILS else 0)
