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

## done so far (FOUNDRY, 2026-09-12) — 3 of 4 verify bullets MET, one deferred

Built `src/RimMandrake/Utils/rimdrive/`: `session.py` (L1 `Session` —
reconnect-on-poisoned-socket via `Reconnected`, `paused()` verified by two
independent `ticksGame` reads, `track()`/`sweep()` litter registry, runtime
tool census into `self.tools` + `require_tools()` for a verb to fail at
connect, `game_focus.preflight()` on connect / `restore_focus()` on exit,
optional `lock="rimflow"`, one-Session-per-process enforced) and `verify.py`
(L2 `mutate()` + `Unchanged`/`Indeterminate`/`Reconnected`/`UNVERIFIED`).
Added `game_focus.preflight()` (thin wrapper naming what the design doc
already called it — `focus_game()` underneath, unchanged).

- ✅ **FakeSession-pattern offline selftest**: `rimdrive/selftest.py`, 12
  cases (mutate happy/no-op/strict/non-strict, UNVERIFIED tainting, both
  reconnect branches including the declared-idempotent retry, litter sweep
  for things vs. pawns via a bare `Session.__new__` + scripted `.call`, the
  one-Session-per-process guard) — picked up automatically by
  `run_selftests.py`'s `selftest*.py` glob. 12/12 pass.
- ✅ **rimbench/core.py imports from rimdrive, no duplicated Session**:
  `core.Session(rimdrive.Session)`, keeping only rimbench's own pre-L3
  convenience verbs (`spawn`, `set_stuff`, `wear`, `look`, ...) that predate
  the L3 families and haven't migrated yet (design §5: attrition, not a
  rewrite). `core.Unchanged` re-exported for existing `except` callers.
  Full repo `run_selftests.py` sweep: 45/49 pass, same 4 pre-existing
  failures as before this change (sound-path/canon/artpipe-throughput/
  one-path-seam — none touch rimdrive, rimbench or game_focus; verified by
  grep before trusting that).
- ✅ **UNVERIFIED, not silent True**: proven by
  `t_mutate_unverified_is_not_a_noop` — a `verify()` returning the
  `UNVERIFIED` sentinel lands in `session.unverified`, never in `no_ops`,
  and is never mistaken for a truthy pass. (Unit-proven, deterministically
  repeatable; not additionally demonstrated live — see below.)
- ⏳ **NOT done: the live selftest chain on a minimal-list quicktest**
  (spawn → verify → sweep → pause-verify). The owner's live campaign colony
  was up and Playing throughout this work, not a quicktest — and
  `rimworld/start_debug_game_ready` needs `go_to_main_menu` first and
  **discards the current map without further warning**
  (rimworld-debug-testing skill). Running the live chain right now would
  have meant discarding the owner's live game to get a throwaway world,
  which is exactly the kind of call this seat does not make unilaterally on
  someone else's live session. Left `doing`, not closed, for exactly this
  reason. Whoever next has a genuine quicktest window (or the owner is
  between sessions) should run it — `Session(strict=True)` as a context
  manager: `s.call("rimworld/spawn_thing", ...)` + `s.track("thing", tid,
  x=X, z=Z)`, read it back, `with s.paused(): ...`, then let `__exit__`
  sweep it and confirm `{"swept": 1, "left": []}`.
