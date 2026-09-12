#!/usr/bin/env python3
"""Terminal twin of the hub's freshness lamps (DASHBOARD_HUB_ARTIFACT_1).

Reads the same per-tab data files the published shell reads and prints one
line per tab: lamp, age, and whether the recorded source fingerprint still
matches the file on disk (STALE means the source moved on and the tab's
publisher owes a re-render). Exit 1 if any lamp is red or any source is
stale, so the check can gate.
"""
import hashlib
import json
import pathlib
import sys
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
TABS = {
    "art": REPO / "infrastructure/artpipe/art_status.json",
    "health": HERE / "data/health.json",
    "maturity": HERE / "data/maturity.json",
    "worldmap": HERE / "data/worldmap.json",
}


def lamp(hours: float) -> str:
    return "GREEN" if hours < 24 else "AMBER" if hours < 72 else "RED"


def main() -> int:
    bad = 0
    for tab, path in TABS.items():
        if not path.exists():
            print(f"{tab:9s} GREY   no data file at {path}")
            bad = 1
            continue
        d = json.loads(path.read_text())
        try:
            ts = datetime.fromisoformat(d["generatedAt"].replace("Z", "+00:00"))
            hours = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
            state = lamp(hours)
            age = f"{hours:6.1f} h"
        except (KeyError, ValueError):
            state, age = "GREY", "UNMEASURED"
        src = d.get("source") or d.get("sourceFingerprint") or {}
        fresh = ""
        if src.get("sha256_12") and src.get("path"):
            sp = REPO / src["path"]
            if sp.exists():
                now = hashlib.sha256(sp.read_bytes()).hexdigest()[:12]
                fresh = "source ok" if now == src["sha256_12"] else \
                        f"STALE — source is {now}, tab holds {src['sha256_12']}"
        print(f"{tab:9s} {state:5s} {age}  {fresh}")
        if state == "RED" or fresh.startswith("STALE"):
            bad = 1
    return bad


if __name__ == "__main__":
    sys.exit(main())
