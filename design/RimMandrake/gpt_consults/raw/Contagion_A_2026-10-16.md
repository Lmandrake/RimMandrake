SUBJECT: Contagion (RimWorld 1.6 mod, C# + XML defs). Slice: Contagion_A.

Static review of the supplied code only. Locations use method names where line numbers were not supplied.

1. **Interrupting injection still performs the injection**

   **Severity:** data loss / wrong behaviour  
   **Location:** `src/RimMandrake/Contagion/Source/JobDriver_RM_InjectGenomeSample.cs`, `MakeNewToils`
   ```csharp
   inject.AddFinishAction(delegate
   ```
   ```csharp
   pawn.inventory.innerContainer.Remove(sample);
   sample.Destroy();
   ```
   A toil finish action also executes during cleanup when the toil is interrupted. It is not a success-only continuation. Once the injection toil starts, cancellation can start gestation and consume the sample without completing the 180 ticks.

   **Repro:**
   1. Order injection and wait until its progress bar appears.
   2. Immediately order the colonist to move elsewhere.
   3. Inspect the host’s health and the colonist’s inventory: gestation has begun and the sample is gone.

   **Confidence:** high. The mutation is inside a cleanup callback. The sampling and Sunbeam jobs already demonstrate the correct pattern: a separate subsequent toil.

2. **Caravan completion leaves a living, permanently spent host**

   **Severity:** data loss / wrong behaviour  
   **Locations:** `src/RimMandrake/Contagion/Source/Hediff_AmoebaGestation.cs`, `PostTick`; `src/RimMandrake/Contagion/Source/AmoebaHostUtility.cs`, `CompleteGestation`
   ```csharp
   completed = true;
   AmoebaHostUtility.CompleteGestation(pawn, sourcePawnID, sourcePawnName, monstrous);
   ```
   ```csharp
   if (map == null)
   ```
   The null-map branch returns before producing anything or killing the host. Nevertheless, `completed` is already true and saved. The gestation hediff remains, so `IsEligibleHost` also rejects another injection.

   **Repro:**
   1. Begin gestation on a caravan-capable host and take it off-map.
   2. Allow severity to reach completion while travelling; alternatively, invoke `PostTick` on an unspawned host at maximum severity.
   3. Return it to a map, then save and reload.
   4. Observe a living host with completed gestation, no batch, and no reinjection option.

   **Confidence:** high. The permanent latch, serialization, early return, and eligibility rejection are all visible.

3. **A zero stack limit makes mulch dropping an infinite allocation loop**

   **Severity:** perf — main-thread hang  
   **Location:** `src/RimMandrake/Contagion/Source/RM_ContagionMulch.cs`, `RM_ContagionMulchUtility.Drop`
   ```csharp
   t.stackCount = count > def.stackLimit ? def.stackLimit : count;
   count -= t.stackCount;
   GenPlace.TryPlaceThing(t, cell, map, ThingPlaceMode.Near);
   ```
   With `stackLimit == 0`, `count` never decreases. A negative limit increases it. The loop continues constructing Things and attempting placement.

   **Repro:**
   1. In a disposable test session, patch the supplied mulch def’s `stackLimit` to zero.
   2. Kill an Unfinished, or call `Drop(def, 2, validCell, map)`.
   3. Observe that the call never returns. Use an external watchdog for this test.

   **Confidence:** high for the failure; conditional on malformed or externally patched def data. This does not establish that the omitted shipped XML has that value.

4. **Failed replacement surgery can award the successful-install bonus**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/Contagion/Source/Recipe_InstallGrownBodyPart.cs`, `ApplyOnPawn`
   ```csharp
   base.ApplyOnPawn(pawn, part, billDoer, ingredients, bill);
   ```
   ```csharp
   if (pawn.health.hediffSet.PartIsMissing(part))
   ```
   “Part is present afterward” does not establish surgery success when replacing an existing damaged organ. A failed operation can leave the original organ present, pass this check, and grant the donor-match memory and success message.

   **Repro:**
   1. Give a colonist a present but damaged organ eligible for natural replacement.
   2. Supply an organ stamped with that colonist’s ID.
   3. Force a nonfatal surgery failure that leaves the original organ present.
   4. Check for `RM_GenomeMatchedInstall` despite the failed transplant.

   **Confidence:** high. The check cannot distinguish the original present organ from a successfully installed replacement.

5. **Injection continues after the host moves out of reach**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/Contagion/Source/JobDriver_RM_InjectGenomeSample.cs`, `MakeNewToils`
   ```csharp
   inject.defaultCompleteMode = ToilCompleteMode.Delay;
   inject.defaultDuration = InjectDurationTicks;
   inject.WithProgressBarToilDelay(TargetIndex.A);
   ```
   The delay has no touch/range failure condition. The global conditions only require an eligible, spawned host and a carried sample. Neither completion nor `TryBeginGestation` checks distance.

   **Repro:**
   1. Start injection and wait for the delay toil.
   2. Using a test script, relocate the host to a distant cell on the same map without despawning it.
   3. Let the delay complete.
   4. Gestation begins remotely and the sample is consumed.

   **Confidence:** high. There is no proximity check after approach; the draftprint job explicitly includes one.

6. **A “weather only” Burn still advances Contagion-touched**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/Contagion/Source/RM_ContagionTouched.cs`, `RM_MapComponent_ContagionTouch.MapComponentTick`
   ```csharp
   burnSky = sky != null && sky.BurnActive && map.weatherManager.curWeather == RM_ContagionSkyDefOf.RM_ContagionBurn;
   ```
   ```csharp
   props.burnDosePerPoll, props.contactDosePerPoll, RM_ContagionSettings.touchedExposureFactor);
   ```
   Unlike the Burn’s pressure loop, this path ignores both `burnEnabled` and `burnDamageFactor`. Consequently, the advertised “0 = weather only, no harm” setting still permits Burn-driven exposure and subsequent mutations.

   **Repro:**
   1. Set Burn damage to zero, leaving touched exposure enabled.
   2. Force a Burn with a powered Repulsor.
   3. Put a human colonist outside, away from contact sources.
   4. Observe increasing `RM_ContagionTouched` severity.
   5. Repeat with `burnEnabled` off: the Repulsor-held Burn still supplies this dose.

   **Confidence:** high. The inconsistent gates are visible in both exposure implementations and the settings text.

7. **Disabling genome growing does not stop an existing injection job**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/Contagion/Source/JobDriver_RM_InjectGenomeSample.cs`, `MakeNewToils`
   ```csharp
   this.FailOn(() => !AmoebaHostUtility.IsEligibleHost(Host));
   this.FailOn(() => !pawn.inventory.innerContainer.Any(t => t.def == RM_ContagionDefOf.RM_GenomeSample));
   ```
   The setting is checked when constructing the float-menu option, but neither the running job nor `TryBeginGestation` checks it. Fixing the finish-action defect alone would not fix this.

   **Repro:**
   1. Order injection while the feature is enabled.
   2. Disable genome growing while the colonist is approaching or injecting.
   3. Resume play.
   4. The job still consumes a sample and begins gestation.

   **Confidence:** high. The execution path contains no setting check.

8. **Looking at a map changes the simulation’s random stream**

   **Severity:** wrong behaviour — determinism  
   **Location:** `src/RimMandrake/Contagion/Source/CompZhoolHaze.cs`, `EmitHaze`
   ```csharp
   if (map != Find.CurrentMap) return;
   int n = RM_ZhoolHazeKernel.Puffs(Props.hazePuffs, RM_ContagionSettings.zhoolHazeDensity, Rand.Value);
   ```
   Visible haze consumes `Rand` values, including further draws in `Puff`; off-screen haze does not. There is no isolated RNG state. Merely switching maps, hiding haze, or changing its density changes the random stream subsequently used by conversion and other simulation rolls.

   **Repro:**
   1. Create a breathing zhool on map A.
   2. Under a fixed `Rand.PushState(seed)`, invoke `EmitHaze` through reflection with A selected, then record the next `Rand.Value`.
   3. Repeat from the same seed with another map selected.
   4. Compare the subsequent random values.

   **Confidence:** high. The camera-dependent branch precedes unbalanced global RNG consumption.

9. **Changing away from the biome can make shaking plants disappear**

   **Severity:** cosmetic  
   **Location:** `src/RimMandrake/Contagion/Source/RM_MapComponent_ContagionSky.cs`, `UpdateVisibleTells`
   ```csharp
   if (shaking == lastShaking) return;
   lastShaking = shaking;
   if (ext == null || ext.tellRattlers.NullOrEmpty()) return;
   ```
   While shaking, rattlegropes deliberately print nothing into the static mesh. Losing the biome extension changes `lastShaking` to false but returns before dirtying their sections. Their dynamic drawing then also stops.

   **Repro:**
   1. Enter the tell window with rattlegropes present.
   2. Let their sections rebuild while shaking.
   3. Change the tile to a biome without the extension, without forcing a complete mesh rebuild.
   4. Advance past the next sky poll.
   5. Plants disappear until an unrelated section rebuild restores them.

   **Confidence:** high for the missing invalidation; the visible repro requires a biome-change mechanism that does not independently rebuild every section.

10. **Four unreachable shelters permanently prevent choosing a reachable fifth**

    **Severity:** wrong behaviour  
    **Locations:** `src/RimMandrake/Contagion/Source/RM_GameCondition_ContagionBurn.cs`, `TryDive`; `src/RimMandrake/Contagion/Source/Kernel/RM_SkyKernel.cs`, `PickDive`
    ```csharp
    if (++tried > 4) return -1;
    if (reachable(i)) return i;
    ```
    Every pressure pulse retries the same nearest four candidates. There is no rotation or remembered failure. Four nearby roofed cells behind a sealed wall can therefore prevent escape to reachable shelter slightly farther away for the entire Burn.

    **Repro:**
    1. Put a UV-shy native outside a sealed roofed room containing the nearest four sheltered cells.
    2. Provide reachable roofed shelter farther away, within 14 cells.
    3. Start a Burn.
    4. Observe repeated damage without a shelter job.

    **Confidence:** high. The budget is explicit, but its repeated fixed ordering creates permanent starvation rather than a temporary search delay.

11. **Contact exposure performs a synchronized pawn-by-source cross-product**

    **Severity:** perf  
    **Location:** `src/RimMandrake/Contagion/Source/RM_ContagionTouched.cs`, `MapComponentTick` and `InContact`
    ```csharp
    bool contact = InContact(p);
    ```
    ```csharp
    for (int j = 0; j < tmpSources.Count; j++)
    ```
    Every eligible humanlike can scan every contact source, including distant sources. This runs on all maps on the same global 250-tick boundary. There is no spatial lookup or distance rejection before constructing expanded occupied rectangles.

    **Repro:**
    1. Spawn several hundred humanlikes and several hundred contact-source creatures, keeping them separated so searches cannot exit early.
    2. Profile ticks around multiples of 250.
    3. Double both populations: contact checks approach four times the previous count.
    4. Repeat across multiple loaded maps to expose synchronized spikes.

    **Confidence:** high for the complexity and synchronization. Actual tick cost requires profiling.

12. **Conversion manufactures growth instead of preserving it**

    **Severity:** wrong behaviour  
    **Location:** `src/RimMandrake/Contagion/Source/CompZhoolHaze.cs`, `Convert`
    ```csharp
    float growth = Mathf.Clamp(old.Growth, 0.15f, 1f);
    ```
    The documented preservation rule is false for every plant below 15% growth. Conversion immediately promotes seedlings to at least 15%.

    **Repro:**
    1. Create an eligible plant at `Growth = 0.01f`.
    2. Trigger conversion, or invoke `Convert` through reflection.
    3. Inspect the replacement: its growth is `0.15f`.

    **Confidence:** high. The increase follows directly from the clamp.

13. **Loading during a tell restarts the sinking animation**

    **Severity:** cosmetic  
    **Location:** `src/RimMandrake/Contagion/Source/RM_MapComponent_ContagionSky.cs`, `UpdateVisibleTells`
    ```csharp
    if (tellsBegun && !wasTellsBegun) tellsBeganTick = now;
    ```
    `tellsBegun` is saved, but `wasTellsBegun` and `tellsBeganTick` are not. At the first post-load poll, an already ongoing tell is treated as newly begun. This defeats the render kernel’s intended fallback to the original tell-window start.

    **Repro:**
    1. Save after sinkers have fully settled, while the tell remains active.
    2. Reload and advance to the next sky poll.
    3. Observe sinkers reset toward floating and settle again, despite the Burn being imminent.

    **Confidence:** high. The first poll replaces the unknown start time with the load-time clock.

14. **The haze message cooldown survives the process, not the save**

    **Severity:** cosmetic  
    **Location:** `src/RimMandrake/Contagion/Source/CompZhoolHaze.cs`, `lastMessageTick` and `Convert`
    ```csharp
    private static int lastMessageTick = -1;
    ```
    ```csharp
    lastMessageTick = now;
    ```
    The cooldown is neither serialized nor owned by a game component. Restarting the application resets it; switching games in the same process can carry it into another game. Detecting a backward clock does not identify every game change.

    **Repro:**
    1. Trigger a conversion message and immediately save.
    2. Quit the application and reload.
    3. Trigger another conversion before 60,000 ticks have elapsed: another message appears.
    4. Separately, load an unrelated save whose tick is just above the previous game’s last message tick; its first message can be suppressed.

    **Confidence:** high. Both outcomes follow from process-static, unsaved state.

## Outside this slice

- **Stacking can corrupt sample grade, donor identity, or draftprint features.** These three comps have per-item state but no visible `AllowStackWith`, `PostSplitOff`, or stack-absorption handling. Whether this is reachable depends on the omitted item defs’ stack limits and any stacking patches.
- **Aggregated hediff ticks may undercount mutations.** `HediffComp_RM_ContagionTouched.CompPostTickInterval` discards elapsed remainder and always supplies 250 ticks to `MTBEventOccurs`. A call with `delta = 2500` accounts for only 250 ticks. Establishing which caravan/world-pawn paths actually supply such deltas requires engine code absent here.
- **Removal safety is unestablished.** The slice saves custom hediff subclasses, a custom building, and a custom quest part. No removal/migration mechanism is shown; behavior after disabling the containing mod requires the omitted loader and cleanup paths.
- **XML wiring and Harmony conflicts cannot be assessed here.** No XML defs, patch operations, or Harmony patches were supplied. Their absence from this slice does not establish that their referenced defs or integration hooks are broken.