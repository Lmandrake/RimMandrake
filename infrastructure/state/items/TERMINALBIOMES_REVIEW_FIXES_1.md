# TERMINALBIOMES_REVIEW_FIXES_1 — fix wave from the 29-file TerminalBiomes full-file review, 2026-09-27

## spec

Three sonnet reviewers swept all 29 C# files changed in the Twilight build wave
(7c3e79e35..HEAD, `src/RimMandrake/TerminalBiomes/Source/`). Findings below are
**EVIDENCE from a sonnet pass, not verified facts** — verify each against the source
(and RimSage where it cites the engine) before fixing. csproj `<Compile Include>`
coverage was checked clean by all three reviewers: no orphaned source files.

⛔ **No file gets `mark-clean` from this pass.** Fix, commit, then a full-file
re-review of the touched files closes the loop.

### BUG — dead mechanisms (the tickerType family, fix first)

1. `RM_Comp_VaeuliskLure.cs:64` — the whole reveal-on-approach ambush is dead code.
   `RM_VauliskLure` inherits `tickerType Long` from `PlantBaseNonEdible`, and the
   engine calls ONLY `TickLong()` for Long tickers — the comp overrides `CompTick()`,
   which never runs. The lure never springs, in every game. (Reviewer MEASURED this
   against the decompiled engine via RimSage.) Fix: move logic to `CompTickLong()`
   (interval math in 2000-tick units) or set `tickerType Normal` on the def.
2. `RM_CompGlowerMobile.cs:58` — `CompTickRare()` only runs when the parent def's
   `tickerType == Rare`; every mover the file's own header names is a Pawn
   (`TickerType.Normal`), so the walking-glower stranded-light fix never executes.
   Sibling `RM_Comp_WarblingGlow.cs` shows the correct shape: `CompTick()` +
   `IsHashIntervalTick`.
3. `RM_Thing_CargoFloat.cs:44` — UNKNOWN/same family: `RM_CargoFloat.xml`
   (`ParentName="ResourceBase"`) sets no `tickerType`; if the effective value is
   `Never`, `Tick()` (the weir/sink catch-and-unload logic) never fires. Check the
   effective tickerType first (def dump / RimSage), then fix or clear.

### BUG — behaviour

4. `RM_CompCageCropSnapshot.cs:69` — `CaptureSnapshot` runs on EVERY `PostDeSpawn`
   (mode never inspected): an ordinary deconstruct/destroy kills the live plants and
   the snapshot dies with the parent. Should only capture on minify/reinstall paths.
5. `RM_Comp_WellChart.cs:35,44` — `PostPostMake` fires before the Thing is on any map,
   so `parent.MapHeld` is null and every chart snapshots `RM_TwilightChart_NoData`.
   Verify the real spawn call-site, then capture at first spawn/first read instead.
6. `RM_Building_SiltTrap.cs:87-98` — `Clog()` rewrites previously-richened cells to
   `RM_BankSilt` without checking current terrain: a breach silently deletes floors
   the player built over richened cells. Guard on current terrain == `RM_BankSilt_Rich`.
7. `RM_MapComponent_WellLedger.cs:192` + `RM_TerminalBiomesMod.cs:159,317-321` —
   `twilightDriftCadence` ("Frozen — wells never age") is persisted but never read;
   `OpenNewWell` always rolls 5–9 days. Wire the setting or the label lies.
8. `RM_TerminalBiomesMod.cs:163,335-337` — `twilightLivingDecorNeedsLight` is inert:
   no consumer anywhere in Source/ (reviewer grepped). Wire it or remove the toggle.
   (7 and 8 both violate the "every mod ships superb Mod Settings" ruling: a toggle
   must do what it says.)

### RISK

9. `RM_Patch_GravEngineLaunchGate.cs:71` — no null guard on
   `RM_VeilFallDefOf.RM_VeilPane` before dictionary use; a failed def load makes EVERY
   launch attempt throw from the postfix. Owner approved the Harmony gate by card
   2026-09-26; add the guard. Null-DefOf → skip the gate (fail open, downgrade-only
   stays honest).
10. `RM_Building_SunSphere.cs:65` — culture/glow tick ignores
    `masterEnabled`/`twilightSeaEnabled`; all-off does not degrade this feature.
11. `RM_Building_SunSphere.cs:48` — seed/food comps told apart purely by
    `CompRefuelable` list order with no `ConfigErrors` enforcement; a def reorder
    silently swaps semantics. Add the check.
12. `RM_HediffComp_Sunk.cs:55,66-70` — a sunk pawn carried off-map (caravan, unspawned)
    reads as "not rescued" and keeps ramping toward death. Decide the rescue predicate
    and fix.
13. `RM_Comp_ClaimBuoy.cs:43` + `RM_MapComponent_WellLedger.cs:461` — "nearest well"
    is actually "first in storage order"; `OpenWells()`'s doc comment claims an
    ordering it does not provide. Sort by distance or fix both comments.
14. `RM_JobGiver_SeekGlow.cs:53` — brightest-glower search linear-scans
    `AllThings` per pass; fine now, flag for a glower-only list if late-game maps chug.

### NIT (fix opportunistically in the same files)

15. `RM_Building_BankWeir.cs:98-121` — `TickBreach()` cascade scan un-gated per tick
    for the 2500-tick breach window.
16. `RM_MapComponent_ChannelCurrent.cs:229-243` — `HasCurrent()` relies on the
    all-three-arrays invariant instead of null-checking `lane` like its siblings.
17. `RM_Comp_DropLureOrganOnDeath.cs:45` — `TryPlaceThing` result discarded; organ can
    vanish silently on impassable kill sites.
18. `RM_IncidentWorker_SuulkArrival.cs:74` — two-suulk letter jump-target only points
    at the second pawn.

## criteria

- [ ] Items 1–2 fixed and the mechanisms proven live (lure springs; mobile glower moves its glow) — quicktest or state read, not code inspection alone.
- [ ] Item 3 resolved MEASURED (effective tickerType named), then fixed or cleared.
- [ ] Items 4–13 verified, fixed or explicitly cleared with a one-line reason each.
- [ ] DLL rebuilt, selftests pass, `.srchash` pushed with the DLL.
- [ ] Touched files re-reviewed full-file before any `mark-clean`.
