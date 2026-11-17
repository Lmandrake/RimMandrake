#!/usr/bin/env python3
"""Acceptance repro for RIMMANDRAKE_UNFENCE_LIVE_HOLDER_WHEN_RIVAL_NEVER_STARTED: Dispatch launches holder A, then B on the
same mod; B ends never_started. Exit 0 when A can still append (the fix), 1 when A is fenced by B (2026-11-17: EK
run-1794896914 fenced by run-1794896974, which ended never_started 7 s after its grant). Run from the repo root:
    env -u RM_MODLEDGER_WRITER python3 src/RimMandrake/rimflow/fixtures/repro_modledger_never_started_fences_live_holder.py"""
import os, sys, tempfile, shutil
sys.path.insert(0, "src/RimMandrake/rimflow")
import modledger as M
os.environ.pop("RM_MODLEDGER_WRITER", None)
root = tempfile.mkdtemp()
for d in ("design/concepts/ExplosiveKnockback",):
    os.makedirs(os.path.join(root, d), exist_ok=True)
try:
    M.grant(root, "ExplosiveKnockback", "run-0", version="0.1.0", views=False)   # a ledger that names its version
    a = M.launch(root, "ExplosiveKnockback", "run-A", "fixer", stage="blind_challenge", views=False)
    b = M.launch(root, "ExplosiveKnockback", "run-B", "fixer", stage="blind_challenge", views=False)
    M.end_run(root, "ExplosiveKnockback", "run-B", "never_started", views=False)
    os.environ["RM_MODLEDGER_WRITER"] = "HOLDER.run-A"
    try:
        M.append(root, "ExplosiveKnockback", "HOLDER.run-A", "lease.renew", "lease", token=a["token"], views=False)
        print("PASS live holder A still writes after B never started"); rc = 0
    except Exception as e:
        print("FAIL live holder A fenced by a never-started run:", str(e)[:160]); rc = 1
finally:
    shutil.rmtree(root)
sys.exit(rc)
