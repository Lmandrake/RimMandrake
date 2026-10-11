"""Change events for telemetry: `emit_change("deploy", subject=..., sha=..., detail={...})`.

Appends one JSON line to <telemetry root>/inbox/changes/changes_<utc-day>.jsonl (E:\\telemetry on
Windows, /mnt/e/telemetry on WSL); telemetryd ingests it into the events table, and Grafana
shows it as an annotation. Design §6.1: deploys, builds and mod-list changes were the biggest gap.

NEVER raises and never blocks the calling tool: telemetry being absent must not break a deploy.
Kinds: deploy, build, modlist, proof_start, proof_end, marker, canary.
"""
from __future__ import annotations

import json
import os
import time


def _root() -> str:
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from tcommon import cfg
        return cfg()["inbox"]
    except Exception:  # noqa: BLE001
        return "E:\\telemetry\\inbox" if os.name == "nt" else "/mnt/e/telemetry/inbox"


def emit_change(kind: str, subject: str | None = None, sha: str | None = None, seat: str | None = None,
                detail: dict | None = None, ts: float | None = None, ts_end: float | None = None) -> bool:
    try:
        inbox = _root()
        if not os.path.isdir(os.path.dirname(inbox)):
            return False
        d = os.path.join(inbox, "changes")
        os.makedirs(d, exist_ok=True)
        t = ts or time.time()
        row = {"ts": t, "kind": kind, "subject": subject, "sha": sha,
               "seat": seat or os.environ.get("RIMFLOW_SEAT"), "detail": detail or {}}
        if ts_end:
            row["ts_end"] = ts_end
        day = time.strftime("%Y-%m-%d", time.gmtime(t))
        with open(os.path.join(d, f"changes_{day}.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row, separators=(",", ":"), default=str) + "\n")
        return True
    except Exception:  # noqa: BLE001 — telemetry must never break the tool that calls it
        return False


def git_head(repo: str | None = None) -> str | None:
    try:
        import subprocess
        return subprocess.run(["git", "-C", repo or os.getcwd(), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, timeout=5).stdout.strip() or None
    except Exception:  # noqa: BLE001
        return None


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("kind")
    ap.add_argument("subject", nargs="?")
    ap.add_argument("--sha")
    a = ap.parse_args()
    print("emitted" if emit_change(a.kind, a.subject, a.sha) else "not emitted (telemetry root absent)")
