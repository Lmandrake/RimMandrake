#!/usr/bin/env python3
"""requeue_flakes: a worker that died spends none of a job's requeues; a failure of its own does (failure_class)."""
import contextlib
import io
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
import requeue_flakes as Q  # noqa: E402

with tempfile.TemporaryDirectory() as t:
    S = Path(t)
    for d in ("failed", "pending", "active", "done", "_requeued_manifests"):
        (S / d).mkdir()
    Q.require = lambda: str(S)

    def job(jid, parked):
        (S / "failed" / f"{jid}.json").write_text("{}")
        (S / "failed" / f"{jid}.manifest.json").write_text(json.dumps({"worker_status": "worker_error"}))
        for k, m in enumerate(parked):
            (S / "_requeued_manifests" / f"{jid}.manifest.{k}.json").write_text(m if isinstance(m, str) else json.dumps(m))
    job("died", [{"worker_status": "worker_error"}] * 5)
    job("own", [{"worker_status": "failed_canon"}] * 3)
    job("torn", ["{not json"] * 4)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = Q.main([])
    moved = sorted(p.name for p in (S / "pending").glob("*.json"))
    assert rc == 0 and moved == ["died.json", "torn.json"], (moved, out.getvalue())
    assert "'cap': 1" in out.getvalue(), "the job that failed on its own three times stays: " + out.getvalue()
    assert "torn: 4 parked manifest(s) of no known outcome" in out.getvalue(), out.getvalue()
print("selftest_requeue_flakes OK")
