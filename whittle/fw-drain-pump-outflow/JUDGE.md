**Verdict: all four bullets are true.** I found no material gap, though there are limits, listed at the end.

**The fix:** in `Building_LiquidPump.cs:294-299,322`, a new `OutflowGive` check means an outflow is only offered to a source that can give a whole notch when exact-level is off. The original code offered the outflow to any source whose outlet wasn't blocked. A 900 dL first source then hit the `amt < units` check and retired the outlet, which starved the full second source.

### Bullet 1 — short source, full source, one outflow, no tank room: **true**
- **Offline:** `PumpOutflow_short_first_real_TryDraw` runs the real `Tick`/`TryDraw`. Candidates `0:900,1:20000` end as `0:900,1:10000`; 10000 moved, total 20900 → 20900.
- **Live**, on the deployed DLL, with `levelExactEnabled=False` and `tankRoom=0`:
  - Sources `[40,39:900; 40,41:20000]`, outflow `[51,40]`.
  - Measured water `[900, 20000, 0]` → `[900, 10000, 10000]`, units 10000.
  - The short source keeps its liquid and the totals conserve. The driver asserts both (`pump_outflow_live.py:276-277`).

### Bullet 2 — retirement and existing behaviour: **true**
- **Source shortfall:** a short source is never offered an outflow. If its tank attempt fails it is retired for the cycle (`sources=0` in the tank-fallback case).
- **Outlet-room shortfall:** the outlet is still retired (`:351`). With rooms `[900, 20000]` the second outlet receives 10000.
- **Negative control:** removing only that retirement line (`outlet_retirement_narrow.diff`, restored to the same hash afterwards) leaves the original starvation case green. Three later-outlet cases fail with `moved=0` (1257/1260).
- **Exact-level transfers:** 900 moves from the short source, and a 500 dL room moves 500, both offline and live (`[900,20000,0]` → `[0,20000,900]`).
- **Duplicate contacts:** a repeated reach cell and an Intake-end contact still resolve to the full source.
- **Tank fallback:** exact-off short channels still get the old partial tank attempt, which rolls back as before. Exact-on partial tank fill works, and a room-short outlet falls back to tanks.
- **Hose fill:** bypasses outlet room but not source supply.
- **Rollback:** a refused destination puts the take back and the next outlet is used; a natural-body credit is rolled back (PutBacks +1).
- **Per-cycle reset:** retirement resets the next cycle, and a multi-level cycle gives one outflow turn.

### Bullet 3 — regression checks, suite, build: **true**
- **Production code:** the harness pulls the complete shipping methods out of `Building_LiquidPump.cs` at build time and fails the build if any is missing. Production `PumpNext`, `RM_PumpMath` and `RM_LiquidTransfer` are compiled in unchanged. Doubles stand in only for the engine, ledgers, outlets, tanks and hoses.
- **Entry point:** the checks are registered in `Program.cs:2170` and run through the normal `run_selftests.py --only selftest_flowworks_stock.py`.
- **Red:** the run on the original pump source (hash 767932…) exits 1 with `expected move 10000, got 0`.
- **Final:** 1260/1260 pass, the hose suites (188/188 checks, 457/457 assertions) pass, and the run exits 0.
- **Shipping build:** succeeded with 0 warnings and 0 errors. Its `.srchash` lists the fixed pump source (3099a3…), the same hash that was tested.

### Bullet 4 — disposable live check: **true**
- **Loaded DLL:** the game reports sha256 a4b1acd8… with a matching MVID, identical to both the source DLL and the deployed DLL.
- **Arms:** the actual ordered candidates were read back first, then four arms ran with measured before/after water: repro, full control, exact-level, and pump-off control (no change).
- **Restoration:** settings were all restored with no errors, `changed_existing_saves` is empty, and protected save hashes match before and after. The player log shows no exceptions.
- **Final state:** the game is not running and both locks are free.
- **Failed first attempt:** it stopped on a hose-lay "no route" error, and its restoration and save protection also came back clean.

**What the paused live hook does and doesn't prove.** `ProofDrawCycle;step` calls the real `TryDraw` once, with power and `Running` respected, and the liquid changes are real. It skips Tick's hash scheduling and the multi-level loop. It also clears and then restores the cycle's retirement state, so it doesn't show a naturally ticking pump.

**Limits (none change a verdict):**
- **Live scope:**
  - The scene used channel sources only, with one outflow.
  - There was no natural body, Intake end or tank in it, and hose filling and gravity levelling were off.
  - Power came from the dev gizmo with godMode on.
  - The original DLL was not run live.
- **Red harness:** it is an earlier harness version (ce72f7…). The final harness can't compile against the original source because `OutflowGive` doesn't exist there.
- **Runner:** `selftest_flowworks_stock.py` changed between the red and final runs. I didn't see the diff; the final run's timeout rose to 1260 s, which may account for it.
- **Test double:** the harness's `TryTakeDl` refuses when a cell holds less than asked, where production takes what is there. The pump checks before taking, so this doesn't affect these cases.
- **Existing behaviour pinned, not changed:** if a source's take is refused after it was chosen, the outlet is retired rather than the source. In production this is rare because the eligibility check matches the take check.
- **Leftover files:** the two disposable `WHITTLE_PumpOutflow_Begin_*` saves are still in the saves folder.
- **Build label:** it reads `8de445f9c2b2+dirty`, while publication reports d0d7cc2. I judged by byte identity, which matches.

would show: yes