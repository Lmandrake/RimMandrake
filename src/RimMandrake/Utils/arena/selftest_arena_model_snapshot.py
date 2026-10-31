#!/usr/bin/env python3
"""selftest_arena_model_snapshot: the judge's resolved model is recorded outside arena_judge.py
(ARENA_JUDGE_RECORD_RESOLVED_MODEL_NOT_ALIAS) and the vet key does not move. Offline: a fake `claude` prints a CLI
envelope whose modelUsage key is taken from its environment. Rows: an alias that resolves into its family is ok; one
that resolves elsewhere exits 3 with the evidence written; no model variable exits 2 naming both; a non-JSON answer
exits 3; arena_critic_tester records the modelUsage keys; the vet key is the same before and after import."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "sim"))
import arena_model_snapshot as MS  # noqa: E402

FAILS = []
FAKE = r'''import json, os, sys
sys.stdin.read()
m = os.environ.get("FAKE_RESOLVED")
if m is None:
    print("plain text"); sys.exit(0)
print(json.dumps({"type": "result", "is_error": False, "total_cost_usd": 0.001,
                  "modelUsage": {m: {"inputTokens": 3, "outputTokens": 1}}}))
'''


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def main():
    import arena_tasks as T
    key0 = T.vet_runner_id()
    tmp = Path(tempfile.mkdtemp(prefix="selftest_model_snapshot_"))
    fake = tmp / "fake_claude.py"
    fake.write_text(FAKE)
    exe = [sys.executable, str(fake)]
    base = {"PATH": os.environ.get("PATH", "")}
    rc, doc = MS.snapshot(tmp / "a", exe=exe, env=dict(base, ANTHROPIC_DEFAULT_OPUS_MODEL="fam",
                                                       FAKE_RESOLVED="model-fam-9"))
    on_disk = json.loads((tmp / "a" / MS.OUT_NAME).read_text())
    check(rc == 0 and on_disk["judge"]["resolved"] == ["model-fam-9"] and on_disk["judge"]["ok"]
          and on_disk["env"]["ANTHROPIC_DEFAULT_OPUS_MODEL"] == "fam",
          "an alias resolving into its family: rc 0, resolved id and env written (%s)" % on_disk["judge"])
    rc, doc = MS.snapshot(tmp / "b", exe=exe, env=dict(base, ARENA_JUDGE_OPUS_MODEL="fam",
                                                       ANTHROPIC_DEFAULT_OPUS_MODEL="x", FAKE_RESOLVED="model-other-1"))
    check(rc == 3 and (tmp / "b" / MS.OUT_NAME).exists() and doc["judge"]["requested"] == "fam"
          and not doc["judge"]["ok"], "resolved elsewhere: rc 3, evidence still written, ARENA_ var wins (%s)"
          % doc["judge"])
    rc, doc = MS.snapshot(tmp / "c", exe=exe, env=dict(base))
    err = doc["judge"].get("error") or ""
    check(rc == 2 and "ARENA_JUDGE_OPUS_MODEL" in err and "ANTHROPIC_DEFAULT_OPUS_MODEL" in err,
          "no model variable: rc 2 naming both variables (%s)" % err)
    rc, doc = MS.snapshot(tmp / "d", exe=exe, env=dict(base, ANTHROPIC_DEFAULT_OPUS_MODEL="fam"))
    check(rc == 3 and "no JSON" in (doc["judge"].get("error") or ""), "a text answer: rc 3, no JSON (%s)"
          % doc["judge"].get("error"))
    check(MS.resolves_to("model-fam-9", ["model-fam-9"]) and not MS.resolves_to("fam", ["model-fam-9", "model-b"]),
          "an exact id resolves to itself; two resolved models are not one judge model")
    import inspect
    import arena_critic_tester as CT
    check('"models_used": sorted(d["modelUsage"])' in inspect.getsource(CT),
          "arena_critic_tester records the CLI's modelUsage keys as models_used")
    check(T.vet_runner_id() == key0, "the vet key is unchanged by this module (%s)" % key0)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
