# LOAD_STALL_PROBE_INSTRUMENT_GAPS_1

Code review of `prove_load_stall_probe.py` / `JawaBenchLoadStallProbe.cs`
(commit 1b7feef4), findings surfaced by a `/code-review high` fork run against
d0e3ec16/3cd027a0/8c4d8daf/1b7feef4 that completed after the 2026-09-02
agent-reboot (the reboot handoff had marked it "lost, no findings captured" —
it wasn't lost, just slow).

## spec

Fix the two "instrument lies" defects; the rest are lower-priority cleanup,
fix opportunistically:

1. **`prove_load_stall_probe.py:46`** — spinner-delta only reports threads
   present in BOTH snapshots (`ta.get(t["id"])` + `if prev:` silently drops
   any thread that entered the top-8 CPU list between readings). A thread
   that starts spinning mid-probe never appears in "top spinners" — the exact
   case the script exists to catch.
2. **`prove_load_stall_probe.py:30`** — docstring claims the probe
   "DELIBERATELY never calls ... anything that marshals to the main thread",
   but `snap()` calls `rimworld/get_ui_state` first, which does marshal to
   the main thread. During a real stall (main thread wedged) this call can
   block up to the 60s client timeout, defeating the stated purpose, and the
   comment will mislead the next person into trusting it's safe.
3. **`JawaBenchLoadStallProbe.cs:98`** — reflection reads for `currentEvent`
   / `eventThread` / `executingToExecuteWhenFinished` return the same value
   for "field is genuinely null" and "field not found on this engine build"
   (no `fieldErrors` entry in the latter case). If a future RimWorld build
   renames these private fields, the probe reports a confident "null (no
   long event running)" instead of flagging an instrument failure — exactly
   the silent-wrong-number class CLAUDE.md warns about.

Lower priority (fix if touching the file anyway, not worth a separate pass):

4. `JawaBenchPawnKitTools.cs:680` — leak-prevention fallback only fires on
   `moved <= 0`; a partial merge that hits `maxStacks` mid-transfer returns
   `moved > 0` and the residual is silently dropped. Needs an unusually
   constrained container (default maxStacks is 999999) — low practical risk.
5. `JawaBenchPawnKitTools.cs:678` — `if (part.Spawned) part.DeSpawn(...)` is
   dead code (`SplitOff` already despawns/never spawns the split piece); the
   comment above it misattributes the despawn. Harmless, just misleading.
6. `JawaBenchLoadStallProbe.cs:190` — sorts anonymous-type threads via
   reflection (`GetType().GetProperty(...).GetValue(...)`) instead of a
   typed tuple list. No functional bug, just avoidable per-call reflection
   cost.

## verify

Re-run `prove_load_stall_probe.py` against a live bridge during an
artificial spin (or re-read the fixed diff) and confirm: a thread that only
appears in the second snapshot's top-8 shows up in the delta table, and the
docstring either drops the no-marshal claim or the `get_ui_state` call moves
after a stall-safe check.

## criteria

Findings 1-3 fixed and re-verified; 4-6 fixed or explicitly deferred with a
one-line reason.

## closed (FOUNDRY, 2026-09-02)

1. Fixed: spinner-delta now treats a thread absent from the first snapshot as
   a 0s baseline instead of dropping it.
2. Fixed: dropped the `get_ui_state` call from `snap()` entirely — it was
   never used in the script's actual output, only in the first debug dump,
   so the docstring's no-marshal claim is now true rather than aspirational.
3. Fixed: `currentEvent`/`executingToExecuteWhenFinished`/`eventThread` each
   now distinguish "field not found" (added to `fieldErrors`, reported as
   `UNMEASURED (field not found)`) from "field value is null" (reported as
   `"null (...)"`).
4-6: deferred — real but low-value: 4 needs an unusually small
`maxStacks` to trigger (default is 999999), 5 is a misleading comment on
dead code with no runtime effect, 6 is a reflection-cost nit with no
functional bug. Not worth a separate pass; fix opportunistically if this
file is touched again.

Verified: `python.exe src/RimMandrake/bridgetools/build.py` compiles clean
(plan-only, not deployed — the live companion has tools this build tree
doesn't build with default flags, unrelated to this change). Python fix
verified with `py_compile`.
