# RIMDRIVE_LIBRARY_BUILD_1 — extract and harden the shared bridge library (L1+L2)

The spec is the authority: `design/RimMandrake/bridge_library_design.md`
(owner-ruled 2026-09-12: name rimdrive, new package `src/RimMandrake/Utils/rimdrive/`;
UNVERIFIED-taint policy for channel-less writes; this item precedes and is
consumed by MOD_VALIDATION_RUNNER_1).

## spec
L1 `rimdrive.session.Session`: extraction of rimbench Session lifecycle plus
the new hardening — reconnect with post-condition polling (never blind-retry),
verified `paused()` context (ticksGame read twice), litter registry with
`sweep()` on exit AND abort, runtime tool census at connect (each verb declares
required tools; missing tool fails AT CONNECT with the deploy hint), game-focus
preflight, optional `lock="rimflow"` bridge take/release. L2 `rimdrive.verify`:
`mutate()` extracted; fix the two known gaps — hostile/other-faction spawns
verify via `jawa/list_pawns` (list_colonists cannot see them), and a write with
no independent read-back channel is marked UNVERIFIED in the evidence stream,
never a silent True. L3+ verb families are NOT this item — they land verb-by-
verb as consumers need them.

## verify
- FakeSession offline selftest (pattern in load_session.py) asserting call
  shapes and call-count budgets, wired into run_selftests.py.
- Live selftest chain on the minimal-list quicktest: spawn → verify → sweep →
  pause-verify, about a minute end to end.
- rimbench core.py imports from rimdrive after extraction (no duplicated
  Session), and rimbench selftest.py's batching budgets still pass.
- A deliberate channel-less write shows UNVERIFIED in evidence, not True.

## traps
- The poisoned-socket rule: drop, reconnect, poll the POST-CONDITION — never
  re-issue a call whose idempotence is undeclared.
- No pinned tool counts anywhere; the jawa/ census rots by design.
- One Session per process; refuse a second — the 2026-08-15 two-driver stall.
