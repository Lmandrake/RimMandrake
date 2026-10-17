SUBJECT: ExplosiveGrowth (RimWorld 1.6 mod, C# + XML defs) — ExplosiveGrowth_B

Reviewed only the supplied slice. Locations below use method names rather than inferred line numbers. Reproductions are proposed tests; I did not run the mod.

1. **The “never downs or kills” burst has no such protection**

   **Severity:** wrong behaviour — potentially lethal.

   **Location:** `src/RimMandrake/ExplosiveGrowth/Source/RM_TopResolver.cs`, `HurtPawnsNear`.

   ```csharp
   if (p.health.summaryHealth.SummaryHealthPercent > 0.5f)
   {
       p.TakeDamage(new DamageInfo(DamageDefOf.Blunt, amount));
   ```

   Overall health percentage does not establish whether another injury will cross a pain, consciousness, or vital-part threshold. Checking `Dead`/`Downed` afterwards merely prevents stunning an already incapacitated victim.

   **Repro:** Place a pawn with overall health above 50% but pain just below its downing threshold beside a Burst plant. Save, fire the top, and repeat until the blunt injury crosses that threshold. Small animals and pawns with damaged vital parts also expose the lethal case.

   **Confidence:** high. The promised predictive check is replaced with an unrelated aggregate threshold.

2. **Re-soaking the component’s own cell enumeration can throw**

   **Severity:** crash — collection-modification exception in the API call.

   **Locations:** `src/RimMandrake/ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs`, `SoakedCells`; `src/RimMandrake/ExplosiveGrowth/Source/Kernel/RM_ExplosiveGrowthKernel.cs`, `TrySoak`.

   ```csharp
   public IEnumerable<IntVec3> SoakedCells => ledger.soakUntil.Keys;
   if (!soakUntil.TryGetValue(c, out prior) || prior < until) soakUntil[c] = until;
   ```

   `ExplosiveGrowthAPI.SoakCells` enumerates its input directly. Passing `comp.SoakedCells` therefore enumerates the same dictionary that extending the deadlines modifies. Mono’s dictionary enumerator can invalidate even when an existing entry’s value is replaced.

   **Repro:** Soak several cells for 1,000 ticks. Immediately call `ExplosiveGrowthAPI.SoakCells(map, comp.SoakedCells, 10000)`. Check for `InvalidOperationException` and a partially extended footprint.

   **Confidence:** medium. The alias is definite; the exception depends on the target runtime’s dictionary implementation.

3. **Reloading manufactures charge time**

   **Severity:** wrong behaviour.

   **Location:** `src/RimMandrake/ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs`, timer fields and `ExposeData`; `src/RimMandrake/ExplosiveGrowth/Source/Kernel/RM_ExplosiveGrowthKernel.cs`, `PassDelta`.

   ```csharp
   private int nextPassTick = -1;
   private int lastPassTick = -1;
   return lastPassTick < 0 ? PassInterval : Math.Min(Math.Max(now - lastPassTick, 1), PassInterval * 8);
   ```

   Neither timer is saved. Every load schedules an immediate pass whose elapsed time is reported as 250 ticks, regardless of when the previous pass occurred.

   **Repro:** Keep a mature charging plant soaked and growing. Immediately after a pass, pause and save. Reload and advance one tick: charge advances by roughly another 250 ticks. Save and repeat. The plant can reach its top after very little simulated time. A dry charge can likewise be drained by repeated reloads.

   **Confidence:** high. Both the reset and the fabricated initial delta are explicit.

4. **Rupture mutations pass through walls and survive removal of the gas**

   **Severity:** wrong behaviour.

   **Location:** `src/RimMandrake/ExplosiveGrowth/Source/RM_TopResolver.cs`, `RuptureExposurePulse`.

   ```csharp
   foreach (IntVec3 cell in GenRadial.RadialCellsAround(z.center, z.radius, true))
   if (p.GetStatValue(StatDefOf.VacuumResistance) >= 0.999f) continue;
   Mutate(p, pool.RandomElement());
   ```

   Exposure tests radial distance and vacuum resistance. It never tests gas occupancy, walls, line of sight, or whether the gas has dispersed. The dangerous “cloud” is an independent invisible disc.

   **Repro:** Use a loaded mutation pool and set mutation chance to 1 through a script. Put an unprotected flesh pawn inside a sealed room within 3.9 cells of a rupture outside. Fire it. The pawn mutates through the wall. Alternatively, clear the tox gas after a rupture and advance another component pass; mutations continue until the zone expires.

   **Confidence:** high. None of the environmental barriers appears in the exposure predicate.

5. **A naturally fired rupture applies two exposure rolls immediately**

   **Severity:** wrong behaviour.

   **Locations:** `src/RimMandrake/ExplosiveGrowth/Source/RM_TopResolver.cs`, `Rupture`; `src/RimMandrake/ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs`, `Pass`.

   ```csharp
   comp.AddRupture(c, RuptureRadius, RuptureCloudTicks);
   RuptureExposurePulse(map, new RM_RuptureZone { center = c, radius = RuptureRadius });
   if (ruptures.Count > 0) TickRuptures(now);
   ```

   `ledger.Pass` fires the plant and registers the zone. The enclosing component pass then ticks that new zone again at the same game tick. At the default chance, an eligible pawn gets a 15.36% chance of at least one successful roll during that tick, rather than 8%, assuming eligible parts remain.

   **Repro:** Instrument `RuptureExposurePulse` with a counter recording `TicksGame`. Let a charged Rupture plant top through normal ticking. Observe two calls for its zone at the same tick. Compare with manually firing it between passes.

   **Confidence:** high. The call sequence is entirely visible.

6. **Bloomcrop’s advertised Burst top resolves to Churn**

   **Severity:** wrong behaviour.

   **Locations:** `src/RimMandrake/ExplosiveGrowth/Defs/ThingDefs_Plants/RM_BloomCrop.xml`; `src/RimMandrake/ExplosiveGrowth/Source/RM_ExplosiveGrowthRegistry.cs`, `Rebuild`.

   ```xml
   <defName>RM_BloomCrop</defName>
   ```
   ```csharp
   var p = new RM_PlantProfile { top = RM_GrowthTop.Churn };
   ```

   The XML calls this the flagship Burst plant, but supplies no ExplosiveGrowth extension. The supplied roster also contains no `RM_BloomCrop` row. Its visible classification is therefore Churn.

   **Repro:** Spawn `RM_BloomCrop`. Read `RM_ExplosiveGrowthRegistry.For(plant.def).top`, or fire its top beside flooring. It reports/executes Churn: no Burst hay, pawn injury, or floor-invading ring.

   **Confidence:** high within this slice. An unseen XML patch or campaign roster could override it.

7. **Large positive API durations overflow into already-expired deadlines**

   **Severity:** wrong behaviour.

   **Location:** `src/RimMandrake/ExplosiveGrowth/Source/Kernel/RM_ExplosiveGrowthKernel.cs`, `TrySoak` and `Suppress`.

   ```csharp
   int until = now + Math.Max(1, ticks);
   return soakUntil.Count != 0 && soakUntil.TryGetValue(c, out until) && now < until;
   ```

   Deadline addition is unchecked. A valid positive `int` duration can wrap negative, while `TrySoak` still returns success. Suppression uses the same calculation.

   **Repro:** After game tick zero, call `ExplosiveGrowthAPI.Soak(map, freshCell, int.MaxValue)`. It returns true, but `IsSoaked` returns false immediately. Repeat with suppression: it can remove existing soak without establishing an active suppression deadline.

   **Confidence:** high. This follows directly from integer addition and deadline comparison.

8. **The master switch leaves ambient growth acceleration running**

   **Severity:** wrong behaviour.

   **Location:** `src/RimMandrake/ExplosiveGrowth/Source/ExplosiveGrowthMod.cs`, `ExplosiveGrowthSettings.BandsOn`.

   ```csharp
   public static bool BandsOn => bandsEnabled && RimMandrake.Biomes.RM_BiomesSettings.Enabled(RosterKey);
   ```

   `BandsOn` omits `enabled`. This contradicts the master-switch comment that every runtime read goes through `On`, and its tooltip saying plants revert to the ambient rate supplied by the rest of the mod list.

   **Repro:** On an in-scope map, inspect an unsoaked bush’s growth rate. Disable “Explosive plant growth enabled,” leaving everyday growth enabled. The bush retains its ×4 or wet-biome band. Disable everyday growth separately and observe the rate fall.

   **Confidence:** high. The ambient postfix explicitly uses this property.

9. **Turning suppression off leaves existing suppression fully effective**

   **Severity:** wrong behaviour.

   **Location:** `src/RimMandrake/ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs`, `Suppress` and `IsSuppressed`; `src/RimMandrake/ExplosiveGrowth/Source/Kernel/RM_ExplosiveGrowthKernel.cs`, `TrySoak`.

   ```csharp
   if (!ExplosiveGrowthSettings.suppressionEnabled) return;
   return ledger.IsSuppressed(c, now);
   if (IsSuppressed(c, now)) return false;
   ```

   The switch prevents new suppression writes. Existing entries continue refusing soak and sprouts for their entire saved duration, despite the setting being presented as taking effect now.

   **Repro:** Suppress a cell for three days. Turn suppression off. Try to soak it and sow a ring across it. Both remain blocked. Save and reload with suppression still disabled; the persisted block remains.

   **Confidence:** high. All consumers ignore the switch.

10. **Changing a map into a no-soak biome does not stop existing soak or charge**

    **Severity:** wrong behaviour.

    **Location:** `src/RimMandrake/ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs`, `Pass`; `src/RimMandrake/ExplosiveGrowth/Source/RM_ExplosiveGrowthPatches.cs`, soak postfix.

    ```csharp
    if (!RM_ExplosiveGrowthRegistry.BiomeInScope(map.Biome))
    if (comp == null || comp.SoakedCount == 0 || !RM_ExplosiveGrowthRegistry.BiomeInScope(map.Biome)) return;
    ```

    Both paths check scope, but neither checks `BiomeRefusesSoak`. A carve-out blocks new writes through `TrySoak`; it does not stop previously soaked plants growing faster, charging, and firing there.

    **Repro:** Soak and arm a mature plant. Through a script, add the current biome’s name to a loaded roster’s `noSoakBiomes`, then rebuild. Confirm `BiomeRefusesSoak` is true. Existing soak still boosts growth and the plant continues toward its top, although a fresh soak request is refused.

    **Confidence:** high. The carve-out is absent from both existing-state consumers.

11. **Drying never lowers the saved tell stage**

    **Severity:** wrong behaviour.

    **Location:** `src/RimMandrake/ExplosiveGrowth/Source/Kernel/RM_ExplosiveGrowthKernel.cs`, `RM_EgLedger.Pass`.

    ```csharp
    if (want > rec.stage)
    rec.stage = want;
    if (rec.stage == RM_TellStage.Tremble || rec.stage == RM_TellStage.Creak) sink.OnTellPuff(c);
    ```

    Charge decays, but stage only moves upward. A plant that dries from Creak to Ground keeps producing late-stage dust. If re-soaked before its charge reaches zero, it cannot play its creak again when it crosses that threshold.

    **Repro:** Charge a plant to about 0.9. Suppress it until charge falls below 0.15 without reaching zero. Inspect its charge record: stage remains Creak. Remove suppression/re-soak it and let charge rise again; the creak threshold produces no new creak.

    **Confidence:** high. Stage is explicitly monotonic and is saved across reloads.

12. **The test-only all-biomes override leaks into subsequent games**

    **Severity:** wrong behaviour.

    **Locations:** `src/RimMandrake/ExplosiveGrowth/Source/RM_ExplosiveGrowthRegistry.cs`, `TestScopeAll`; `src/RimMandrake/ExplosiveGrowth/Source/RM_ExplosiveGrowthProof.cs`, `SetTestScopeAll`.

    ```csharp
    public static bool TestScopeAll;
    RM_ExplosiveGrowthRegistry.TestScopeAll = on;
    ```

    “Never Scribed” does not mean “off at every game start.” This is process-wide static state. Neither the supplied load path nor registry rebuild resets it.

    **Repro:** Call `ProofTestScopeAllOn` on a foreign-biome map. Interrupt the suite before cleanup. Load another save or start another game without restarting RimWorld. `ProofScope` still reports `testScopeAll=True`, and foreign biomes remain affected despite the player option being false.

    **Confidence:** high within this slice. Only an unseen lifecycle hook could prevent the leak.

13. **Disabling the engine can leave its swollen, tinted mesh baked indefinitely**

    **Severity:** cosmetic.

    **Location:** `src/RimMandrake/ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs`, `MapComponentTick`.

    ```csharp
    if (!ExplosiveGrowthSettings.On || !RM_ExplosiveGrowthRegistry.Ready)
    {
        lastPassTick = now;
    ```

    This branch returns before charge processing and mesh dirtying. Changing settings rebuilds the registry but does not invalidate affected map sections. The Print/Graphic guards only help when another event causes those sections to regenerate.

    **Repro:** Let a plant visibly swell and tint. Disable the engine while its section is displayed. Leave the camera and section undisturbed. The old appearance can persist despite the feature being disabled. Force a section rebuild to make it disappear.

    **Confidence:** high. The supplied disable path never requests the necessary redraw.

14. **“Maximum scale = 1” still makes trembling plants change size**

    **Severity:** cosmetic.

    **Location:** `src/RimMandrake/ExplosiveGrowth/Source/Kernel/RM_ExplosiveGrowthKernel.cs`, `VisualScale`.

    ```csharp
    float s = 1f + (maxOvergrowthScale - 1f) * InverseLerp(SwellAt, 1f, charge);
    if (charge >= TrembleAt && charge < SilenceAt) s *= wobbleParity ? 1.035f : 0.965f;
    ```

    The wobble is applied after calculating the configured maximum. At maximum scale 1, trembling plants still alternate between 0.965 and 1.035. The validation only checks charge 0.97, after wobble has stopped, so it misses this.

    **Repro:** Set `maxOvergrowthScale=1`. Set a plant’s charge to 0.75. Read `VisualScaleFor` across successive reprint passes or call the kernel with both parity values. Results are 1.035 and 0.965.

    **Confidence:** high. The arithmetic is explicit.

## Outside this slice

- **Dictionary save/load scratch-list aliasing needs verification.** `ExposeData` reuses `tmpKeys` across three dictionary calls and `tmpInts` across two. Whether that corrupts reconstruction depends on the omitted `Scribe_Collections.Look` implementation and its load-phase handling; I am not calling it a proven save-corruption bug.
- **Harvest payout and gamble ordering needs vanilla callers.** The prefix removes charge before `PlantCollected`, but this slice does not establish when harvesting/cutting jobs calculate and place yield.
- **Removal safety is unproven.** The supplied code saves custom component and deep-record types, but safe loading after removing the assembly depends on missing loader behaviour, dependency metadata, and migration support.
- **DLC requirements and donor validity are unproven.** The code uses tox gas and `VacuumResistance`; prerequisite metadata and the referenced pawn, mutation, terrain, and donor plant defs are absent.
- **Patch gating and ordering require the shared patcher.** `PatchApplier` is not supplied, so I cannot establish its toggle/unpatch behaviour or compatibility with other Harmony owners.