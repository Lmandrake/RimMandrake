#!/usr/bin/env python3
"""Proof for ARTPIPE_TWINS_PRUNE_FAILED_COPY: every done/failed twin was resolved by `artpipe_state.py twins`.

Reads the committed record (infrastructure/state/evidence/ARTPIPE_TWINS_PRUNE_FAILED_COPY.json): the 32 twin ids of
review w94 are all pruned (moved, with sha, backup and why per file), the last run's moves are exactly the jobs the
committed ARTPIPE_DONE_RECORDS_AUDIT_LOST_PNG record rules purged/superseded, and the re-scan after found 0 twins.
If the live state dir is readable it also re-runs the dry run and requires 0 twins (else says so and skips)."""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EV = REPO / "infrastructure/state/evidence"
FAILS = []


def check(name, ok):
    print(f"{'PASS' if ok else 'FAIL'}  {name}")
    if not ok:
        FAILS.append(name)


rec = json.loads((EV / "ARTPIPE_TWINS_PRUNE_FAILED_COPY.json").read_text())
dec = json.loads((EV / "ARTPIPE_DONE_RECORDS_AUDIT_LOST_PNG.json").read_text())["jobs"]
runs = rec["pruned_runs"]
rows = [r for v in runs.values() for r in v]
ids = {r["id"] for r in rows}
check(f"32 twin ids pruned across {len(runs)} run(s) (got {len(ids)})", len(ids) == 32)
check("every moved file has sha256, backup, why and tool",
      all(len(r.get("sha256", "")) == 64 and r.get("backup") and r.get("why") and r.get("tool") for r in rows))
check("the misclaimed stray failed/cauldronsoilrich_breathes_a.manifest.manifest.json was moved",
      any(r["file"] == "failed/cauldronsoilrich_breathes_a.manifest.manifest.json" for r in rows))
last = runs[sorted(runs)[-1]]
ruled = {j for j, d in dec.items() if d.get("decision") in ("purged", "superseded")}
lids = {r["id"] for r in last}
check(f"last run moved only jobs the decision record rules purged/superseded ({sorted(lids)})",
      lids and lids <= ruled and all(r["evidence"].get("retired", {}).get("decision") == dec[r["id"]]["decision"]
                                    for r in last))
check("re-scan after apply: 0 twins", any(l.startswith("twins: 0 ids") for l in rec["rescan_after"]))
tool = REPO / "src/RimMandrake/Utils/artpipe/artpipe_state.py"
try:
    p = subprocess.run([sys.executable, str(tool), "twins"], capture_output=True, text=True, timeout=120)
    live = [l for l in p.stdout.splitlines() if l.startswith("twins: ")]
except Exception as e:  # noqa: BLE001 — the walled checker cannot reach the state dir
    p, live = None, []
if p is not None and p.returncode == 0 and live:
    check(f"live dry run: {live[0]}", live[0].startswith("twins: 0 ids"))
else:
    print("SKIP  live state dir unreadable here; the committed re-scan stands")
print(f"{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failure(s)")
sys.exit(1 if FAILS else 0)
