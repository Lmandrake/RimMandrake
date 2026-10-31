# ARENA_PUBLISH_DQ_FIX_PARKED_REJECT_VIOLATES

## Defect
dq_publish (arena_analysis.py) treats ANY judge event without an earlier gate pass at the same sha as "published work the
gate did not pass". The replay runner's default_judge runs gate then judge on EVERY task, whatever the outcome, so one
parked task or one task whose end state fails the gate DISQUALIFIES the whole arm.

## Proof
Real trial-runner, real arena_gate, real arena_judge, stub model, scratch root (sha dc155c333a era, dq_publish unchanged at
b8653f215d): v3 parked, gate fail at sha=base, judge pending marker + judge reject at sha=base.
dq_publish on that real log -> VIOLATED, two evidence rows (the pending marker counts too). Synthetic 29x3 at the real CLI:
one parked ralph_a task -> DISQUALIFIED ['publish'], verdict DECIDE_FOR_ralph_a -> TIE; one parked v3 task -> UNMEASURED rc 3.
Script: D:\ClaudeWork\rimmandrake\arena_readiness\s2.py. Real trail: D:\ClaudeWork\rimmandrake\arena_readiness\logs\v3base.txt.

## Changes a verdict: YES
Every arm with one gate failure in 29 tasks is out; a control with one is UNMEASURED. Expect it on every real run.

## Fix direction
Disqualify only a judge ACCEPT (or an actual publish event) with no gate pass; a reject or the pending marker is the
system working. Design §4.1: DQ is for publishing work the gate did not pass. Add a selftest from the real trail.
