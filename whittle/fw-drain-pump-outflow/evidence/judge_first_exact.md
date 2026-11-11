I judge all four bullets **true**. Limits are noted under each, and there is no material gap.

## Bullet 1: short first source and full second source share one outflow, conserving liquid — **TRUE**

- **Source:** in `Building_LiquidPump.cs:321-323`, a source can only claim an outflow if `OutflowGive(ex, sources[i]) > 0`. With exact-level off, `RM_PumpMath.SourceTakeUnits` returns 0 for less than a whole notch. So a 900 dL channel is no longer offered to the outflow, and `PumpNext` (`RM_LiquidNetKernel.cs:914-936`) goes on to tanks and then to the next source. In the original, the outflow test was only "outlet not blocked". The short source won the outflow, failed `amt < units` and retired it (`usedOutflows.Add`), which starved the full source.
- **Offline result:** candidates `0:900,1:20000`, after `0:900,1:10000`, moved 10000, total 20900 both before and after.
- **Live result:** independent cell reads went from `[900, 20000, 0]` to `[900, 10000, 10000]` with `tankRoom=0`. Exact-level was confirmed `False` just before the step.

## Bullet 2: retirement, exact-level, hose fill, tank fallback and rollback — **TRUE**

- **Source shortfall** now makes a source ineligible for outflows. That source can still fall back to tanks, and a failed tank attempt retires it by cell (`deadSources`, keyed by cell index).
- **Outlet-room shortfall** still retires that outlet (`:349-352`). The negative control removed only that line: 1257/1260 passed. The three failures were the later-outlet cases, while `PumpOutflow_short_first_real_TryDraw` stayed green. The mutant was restored to the same hash as the fix (`3099a336…`).
- **Duplicate source contacts:** candidates `0:900,1:20000,0:900` moved 10000 from source 1. This case failed on the original.
- **Exact-level:** 900 moved from the short source; 900 and 500 moved into room-limited outlets.
- **Hose fill:** bypasses outlet room but not source supply (10000 into the hose, 0 to the outlet).
- **Tank fallback:** an exact partial fill of 500, and room-short outlet to tank (10000).
- **Rollback:** a refused natural-body pour is put back (the transfer's put-back counter goes up by 1). A refused destination rolls back and the next outlet is used. Retirement resets on the next cycle, and each outlet gets one turn per multi-level cycle.
- **Limits:**
  - A refused *source take* retires the outlet rather than the source. This is the original behaviour and is pinned as `moved=0`. It is rare because eligibility already checks supply.
  - The short-channel tank fallback with exact-level off always fails, because the production `TryTakeDl` rounds down to whole notches. This also predates the fix, and the test models it the same way.

## Bullet 3: production-linked regression checks, focused suite and shipping build — **TRUE**

- **Production code under test:** `PumpOutflowHarness.targets` copies the complete production `Tick`, `TryDraw`, `Sources`, `Drawable`, `SourceTake`, `TankTake`, `OutflowGive` and `ProofDrawCycle` into the test build at build time. The real `PumpNext`, `RM_PumpMath` and `RM_LiquidTransfer` are compiled in. Only the engine is replaced with stand-ins: cells, stock, outlet room, a single tank, and hose storage.
- **Entry point:** the cases are registered in `Program.cs:2170` and run through the normal `run_selftests.py --only selftest_flowworks_stock.py`.
- **Red run:** the original pump source (`767932…`) failed 4 cases, including the starvation case (`outflows=0` retired, moved 0).
  - Limit: that red run used an earlier harness version (`420f1e…`, not the final `bda2a6…`). The final harness cannot compile against the original, which is the compile fault left in `red-original/`.
- **Final run:** 1260/1260 passed, hose 188/188 and 457/457, return code 0. The staged test tree had no missing or mismatched files, and the cache refusals show it was a fresh run, not a cached result.
- **Shipping build:** 0 warnings, 0 errors.

## Bullet 4: disposable live-game check on the deployed DLL — **TRUE**

- **DLL identity:**
  - The repo and deployed DLL are byte-identical (`a4b1acd8…`).
  - The `.srchash` maps that DLL to `Building_LiquidPump.cs 3099a336…`, the tested fix.
  - `ProofDrawCycle` does not exist in the original source, yet the static call succeeded with one copy of the assembly loaded. This shows the new code was the code running.
- **Runs:** live preflight PASS. All four arms record actual ordered candidates and independent dL reads before and after:
  - **repro:** the short source keeps its liquid while the full source sends 10000 out.
  - **full:** the first full source is used.
  - **exact:** 900 moves.
  - **off:** `running=False`, nothing moves.
- **Restoration:**
  - The begin save was reloaded and all settings restored.
  - `changed_existing_saves` is empty and the protected save hashes are identical before and after.
  - The post-scene log has no hits. The only error in the raw stream is an unrelated pawn message.
  - The game finished NOT RUNNING and the driver lock and bridge are FREE.
- **Failed first attempt:** the hose lay `41,41→52,40` was refused with "no route" before any arm ran. Its restoration still passed with no changed saves. The driver was then republished to use `51,40`.

**What the live check does not prove:**
- It calls `TryDraw` directly while the game is paused. That skips the hash-interval scheduling and Tick's multi-level loop, and it restores cycle and retirement state afterwards.
- It covers one channel-to-channel scene only: tank room 0 and hose need 0. Natural bodies, tank fallback and hose fill were not exercised live.
- The 900 dL short source was created with exact-level on and the setting then switched off. That is reachable through Mod Settings, but it is a constructed state.
- The original DLL was never run live, so the "before" behaviour is shown offline only.
- I found no explicit limits field in the raw scene JSON. The limits above are my own reading.

would show: yes