I found **11 issues**. This is a source-only audit; the checks below are proposed, not executed. Paths are relative to `src/RimMandrake/FlowWorks/Source/`. I cite exact code lines instead of unverified line numbers.

**F1 — HIGH — Ferry routing can remain uninitialized after loading**

- **Where:** `Rivers/RM_MapComponent_RiverCurrent.cs`, `MapComponentTick`: `worksDirty = true;` followed by `Scan();`. `Rivers/RM_FerryAndLevee.cs`, `ApplyRope`: `HashSet<int> rope = map?.GetComponent<RM_MapComponent_RiverCurrent>()?.RopeIndicesNoRebuild;`.
- **What happens:** Loading restores partners but leaves the derived rope set empty. Marking it dirty does not rebuild it. With every pawn and loose item on dry ground, `Scan()` never reaches the river-lane `InPool()` call that invokes `EnsureWorks()`. Path-grid computation deliberately reads without rebuilding, so undrafted routing can continue ignoring a valid ferry. Removal can similarly leave stale rope costs. Disabling surface current prevents even the periodic scan.
- **Repro:** Save a paired ferry with nobody or anything loose in the river. Reload and assign an undrafted crossing job.
- **Suggested check — cheap live read:** Read `RopeIndicesNoRebuild.Count` and perceived cost before requesting `RopeCellCount`; then request that getter and recompute paths. The getter repairs the state, so existing ferry proofs that call it can mask this bug.
- **Confidence:** High.

**F2 — MEDIUM — A silt-table upgrade can overwrite a player’s replacement floor**

- **Where:** `Rivers/RM_SiltTrapAndDrift.cs`, `Clog()`:
  `if (rich == null || c.GetTerrain(Map) == rich)`
  followed by `Map.terrainGrid.SetTerrain(c, orig);`.
- **What happens:** Saved provenance contains the original terrain, but not the terrain actually applied. If an update removes the original terrain’s swap entry, `RichFor(orig)` becomes null. That makes the condition unconditional: a breach overwrites whatever now occupies the square, including a player-built floor. Changing the destination instead produces the opposite failure: old rich terrain no longer matches and becomes permanently unrevertible when the records are cleared.
- **Repro:** Richen a square, build flooring over it, save, remove that swap entry in a version-update fixture, load, and breach the nearby weir.
- **Suggested check — offline SelfTest:** Test original terrain `O`, saved applied terrain `R`, current floor `F`, and a missing/changed lookup. Assert that `F` survives and old `R` remains identifiable.
- **Confidence:** High.

**F3 — HIGH — Turning rivers off leaves session-wide river avoidance active**

- **Where:** `Rivers/RM_RiverWorks.cs`, `static RM_RiverPathCost()`:
  `t.extraNonDraftedPerceivedPathCost += RM_RiverMath.AvoidanceCost(RM_RiversSettings.riverWorksEnabled,`
- **What happens:** Avoidance is baked into shared `TerrainDef`s once at startup. Turning off the rivers master or surface current stops carrying, but never restores those costs or invalidates existing perceptual grids. Existing and subsequently loaded maps therefore retain strong avoidance of now-inert water. The reverse also occurs when startup settings disable currents and the player enables them later. The avoidance checkbox discloses a restart requirement; the master/current switches promise runtime vanilla behavior.
- **Repro:** Start with rivers enabled, disable the rivers master during play, then inspect routing across a short river versus a distant bridge.
- **Suggested check — cheap live read:** Compare the river terrain’s `extraNonDraftedPerceivedPathCost` and `UndraftedCostAt()` before and after disabling the master, including on another loaded map.
- **Confidence:** High.

**F4 — HIGH — Repairing a stake cannot stop its scheduled cascade**

- **Where:** `Rivers/RM_Weir.cs`, `TickBreach()`:
  `stake.TakeDamage(new DamageInfo(DamageDefOf.Deterioration, stake.MaxHitPoints));`.
- **What happens:** The design explicitly promises that reaching a post and repairing it can stop the cascade. Execution checks only whether the referenced stake exists and is not destroyed. Repair never cancels its timer or exempts a healthy stake; it receives the same full-MaxHP damage.
- **Repro:** Breach a weir, repair a downstream scheduled stake to full HP before its deadline, and let that deadline pass.
- **Suggested check — cheap live test:** Read `CascadeTickFor(stake)`, restore its HP before that tick, advance just beyond it, and inspect survival. No seasonal wait is needed.
- **Confidence:** High.

**F5 — MEDIUM — Switching breach off does not stop an active catastrophe**

- **Where:** `Rivers/RM_Weir.cs`, `Tick()`:
  `if (breaching)` → `TickBreach();` → `return;`.
  The `breachEnabled` check occurs later.
- **What happens:** Disabling breach prevents new breaches but leaves scheduled stake destruction running. Disabling bank works pauses execution while absolute deadlines continue passing; reenabling can fire several overdue snaps together. That conflicts with the design’s breach-off behavior of no catastrophic failure and makes runtime switches surprising.
- **Repro:** Begin a slow cascade, disable breach before the next snap, and advance. Separately, disable bank works until multiple deadlines pass, then reenable it.
- **Suggested check — offline SelfTest:** Exercise the breach state machine with scheduled deadlines and both switches changing midway; assert the intended cancellation or remaining-delay policy.
- **Confidence:** High.

**F6 — HIGH — Fast water has a long acquisition grace period that permits ordinary crossings**

- **Where:** `Rivers/RM_MapComponent_RiverCurrent.cs`:
  `private const int ScanIntervalTicks = 250;`
  and `nextMoveTick[t] = Find.TickManager.TicksGame + CadenceFor(t, t.Position);`.
- **What happens:** New river entrants are discovered only every 250 ticks. Their first shove is then delayed by another full cadence. A pawn entering immediately after a scan can walk normally for almost 250 ticks before even being registered, contradicting the advertised inescapable fast lane. Short crossings can finish without a shove or warning.
- **Repro:** Immediately after a scan, order a drafted pawn across a short chest-deep strip.
- **Suggested check — cheap live test:** Align entry just after a scan and read position/current registration over the crossing. An offline scheduling case should also assert the present worst-case delay of nearly `250 + cadence` ticks.
- **Confidence:** High.

**F7 — MEDIUM — Current speeds silently cap and round upward to 15-tick steps**

- **Where:** `Rivers/RM_MapComponent_RiverCurrent.cs`:
  `private const int ProcessIntervalTicks = 15;`
  and `nextMoveTick[t] = Find.TickManager.TicksGame + CadenceFor(t, next);`.
- **What happens:** Processing makes at most one move per thing every 15 ticks, then schedules from the actual processing time. Consequently, cadence 18 becomes 30 ticks per cell; cadence 1–15 becomes 15. There is no accumulated timing remainder or catch-up. Strength, size and flood multipliers therefore flatten together at the fast end and often deliver materially slower speeds than the math/settings describe.
- **Repro:** Use a huge river, high strength and a low fast-lane interval; compare requested cadence with actual movement timestamps.
- **Suggested check — offline SelfTest:** Run the scheduler for cadences 1, 9, 18 and 45. Verify actual intervals against the intended arithmetic.
- **Confidence:** High.

**F8 — MEDIUM — Production ferry pairing can connect two posts on the same bank**

- **Where:** `Rivers/RM_FerryAndLevee.cs`, `TryPair()`:
  `float bestDist = float.MaxValue;`
  and `LineCrossesWater()`:
  `if (RM_RiverWorks.IsWaterCell(Map, c))` → `return true;`.
- **What happens:** Pairing selects the nearest unpaired post whose line touches any moving-water square. It never establishes opposite banks or a usable crossing. Two nearby posts on one indented bank can pair across a small water notch, consuming the posts intended for separate cross-river ferries.
- **Repro:** Build two posts along an indented bank before building their intended counterparts across the main channel.
- **Suggested check — offline geometry case:** Supply two same-bank candidates whose connecting segment clips water, plus intended opposite-bank candidates; assert the intended pairing policy.
- **Confidence:** High. This is production `TryPair()`, distinct from the already-fixed longest-crossing search in the proof-site helper.

**F9 — HIGH — Partial catch placement can create fish without debiting fish stock**

- **Where:** `Rivers/RM_Weir.cs`, `Deposit()`:
  `return GenPlace.TryPlaceThing(t, BankCell, Map, ThingPlaceMode.Near) ? n : 0;`.
  `TryCatchFish()` returns before `tracker.Notify_Fished(WaterCell, placed);` when `placed <= 0`.
- **What happens:** The wash code explicitly documents the relevant `GenPlace.TryPlaceThing` failure behavior: some units can merge into existing stacks before placement of the remainder fails. `Deposit()` treats that as zero deposited, loses its reference to the remainder, and debits no fish stock despite the merged fish now existing. This is the same placement-failure class handled by `WashHeld`, at another caller.
- **Repro:** Fill the nearby placement area, leaving only a compatible fish stack with room for part of the catch, then force catch attempts.
- **Suggested check — offline SelfTest:** Inject a placer that merges one unit and returns false. Assert stock debit equals actual deposited units and every remainder has an explicit disposition. Confirm the engine path with one cramped live placement.
- **Confidence:** High, using the placement semantics documented in the supplied wash implementation.

**F10 — LOW — River steam continues rising from cells that stopped being river**

- **Where:** `ManyWaters/RiverSteamHook.cs`, `MapComponentTick()`:
  `if (!cell.Fogged(map))` → `ThrowRibbon(cell);`.
- **What happens:** Vents are selected during `FinalizeInit()` and never revalidated against terrain during normal play. A vent square converted to a bridge, ford or dry terrain keeps emitting river steam until reload or the developer-only rescan.
- **Repro:** Locate a visible vent, replace its river terrain, and continue ticking.
- **Suggested check — cheap live test:** Replace one known vent square and advance beyond its puff deadline. Check that emissions stop without invoking `Rescan()`.
- **Confidence:** High.

**F11 — HIGH — Two supplied files have unmatched terminal braces**

- **Where:** `Rivers/RM_RiverMath.cs`, immediately after `WashHeld()`, ends with:
  ```csharp
              return moved;
          }
      }
  }
  }
  ```
  `Rivers/RM_WorldComponent_SweptAway.cs` has the same extra closing brace after `SurfaceHomeMap()`.
- **What happens:** Each file contains one namespace and one outer class; the final fourth brace above is unmatched. Compiling these literal texts produces a syntax error such as CS1022. A runnable existing DLL therefore cannot establish that this exact supplied source builds.
- **Repro:** Compile the supplied texts unchanged.
- **Suggested check — offline:** Run the normal release build against these exact inputs; a lexical brace-balance check can catch this before invoking the compiler.
- **Confidence:** High for the inlined text.

## Outside this slice

- **`TakenByLand/RM_TakenByLand.cs` and its world component are missing.** New swept-away pawns use that service. Pawn ownership, save/load, return scheduling, map removal and session statics for the active implementation cannot be audited here.
- River XML, terrain XML, project compile inclusions and compatibility converters are absent. Placement restrictions, drift contents, stake implementation and old TerminalBiomes migrations remain unverified.
- Registrations into the static flood/arrest/current-rule lists are outside the input. Whether those delegates capture obsolete maps or game instances cannot be established.
- Excavation, liquid stock, tanks, pocket-grid invalidation and shared patch/settings helpers are missing. Their conservation and cache behavior cannot be certified from their settings declarations.
- No source file appeared truncated. The ledger explicitly contains truncated item heads. The unmatched braces are present in the supplied file endings, rather than apparent truncation.