SUBJECT: ExplosiveGrowth (RimWorld 1.6 mod, C# + XML defs) — ExplosiveGrowth_A

Static review of the supplied files only. Reproductions below are proposed tests; I did not run the game.

1. **A zero-stack-limit harvest product can hang the simulation**

   **Severity:** crash / hang  
   **Location:** `src/RimMandrake/ExplosiveGrowth/Source/RM_TopResolver.cs` — `SpawnNear`
   ```csharp
   t.stackCount = Mathf.Min(count, def.stackLimit);
   count -= t.stackCount;
   GenPlace.TryPlaceThing(t, at, map, ThingPlaceMode.Near);
   ```
   These execute inside `while (count > 0)`. With `stackLimit == 0`, `count` never decreases. A negative limit makes it increase. Placement failure does not terminate the loop either.

   **Repro:** In an isolated test process, set a harvestable plant’s product def’s `stackLimit` to zero through a script. Trigger its Churn top with positive yield. The loop cannot complete normally; placement might throw first.

   **Confidence:** high. The missing progress guarantee is directly visible. This requires an abnormal product def, but the engine automatically opts other mods’ plants into Churn.

2. **The burst’s “never downs or kills” guarantee is false**

   **Severity:** wrong behaviour — potentially lethal  
   **Location:** `src/RimMandrake/ExplosiveGrowth/Source/RM_TopResolver.cs` — `HurtPawnsNear`
   ```csharp
   if (p.health.summaryHealth.SummaryHealthPercent > 0.5f)
   {
       p.TakeDamage(new DamageInfo(DamageDefOf.Blunt, amount));
   ```
   Aggregate health above 50% does not establish that the selected body part can survive the hit, or that pain/consciousness will remain above the downing threshold. There is no prospective damage check or rollback.

   **Repro:** Prepare several otherwise healthy, small flesh pawns with a nearly destroyed vital part, while retaining summary health above 50%. Place them beside a Burst plant and trigger bursts across several restored saves/seeds. A hit to the vulnerable part can kill; pain-sensitive pawns can also be downed.

   **Confidence:** high. The code implements a summary-health threshold, not the promised injury/downing ceiling.

3. **Reloading advances charge without the corresponding elapsed time**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs` — scheduling fields and `MapComponentTick`; `src/RimMandrake/ExplosiveGrowth/Source/Kernel/RM_ExplosiveGrowthKernel.cs` — `PassDelta`
   ```csharp
   private int lastPassTick = -1;
   ```
   ```csharp
   return lastPassTick < 0 ? PassInterval : Math.Min(Math.Max(now - lastPassTick, 1), PassInterval * 8);
   ```
   `ExposeData` saves charges but none of the pass timestamps. Every loaded component therefore receives a fresh 250-tick charge step on its first tick, irrespective of how recently its saved charge was stepped.

   **Repro:** In daylight, soak a mature plant and use `DebugSetCharge(p, 0.94f)`. Save. Repeatedly load, advance approximately one tick, pause and save again. With its debug clock factor of one, roughly four reloads can finish the remaining charge despite only a handful of elapsed ticks.

   **Confidence:** high. Both the unsaved timestamp and unconditional first-step duration are explicit. Dry decay and rupture/source pulse scheduling also change across reloads.

4. **Leaving scope freezes hazardous charges instead of retiring them**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs` — `Pass`; `src/RimMandrake/ExplosiveGrowth/Source/RM_ExplosiveGrowthPatches.cs` — `RM_Patch_Plant_PlantCollected_Gamble.Prefix`
   ```csharp
   if (!RM_ExplosiveGrowthRegistry.BiomeInScope(map.Biome))
   {
       if (ruptures.Count > 0) TickRuptures(now);
   ```
   That branch returns without processing or clearing charges. Meanwhile, the collection patch checks `On` and `Spawned`, but never biome scope, before taking that retained charge and potentially firing its top.

   **Repro:** Enable `applyInOtherBiomes` on a vanilla-biome map. Charge a hazardous plant to 0.9. Turn that option off and leave the map running beyond the soak’s expiry. Its charge remains frozen. Cut it repeatedly across restored saves: the last-swing gamble can still fire outside scope. Re-enabling scope resumes the old charge.

   **Confidence:** high. The scope exit and collection gates are visible and inconsistent.

5. **Mutation exposure penetrates walls and survives removal of the gas**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/ExplosiveGrowth/Source/RM_TopResolver.cs` — `RuptureExposurePulse`
   ```csharp
   foreach (IntVec3 cell in GenRadial.RadialCellsAround(z.center, z.radius, true))
   ```
   ```csharp
   Mutate(p, pool.RandomElement());
   ```
   Exposure uses a geometrical disk. It never checks gas presence, intervening walls, room connectivity or whether the gas has dispersed.

   **Repro:** Put an unsealed flesh pawn inside a closed room, within 3.9 cells of a rupture outside its wall. Use a nonempty mutation pool and elevated mutation chance. Trigger the rupture and observe exposure inside. Separately, clear the gas while leaving the rupture zone active: mutation rolls continue.

   **Confidence:** high for the unconditional radial exposure; medium that this violates the intended cloud geometry, which the supplied descriptions present as gas exposure.

6. **A new rupture exposes pawns twice on its creation tick**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/ExplosiveGrowth/Source/RM_TopResolver.cs` — `Rupture`; `src/RimMandrake/ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs` — `Pass`
   ```csharp
   comp.AddRupture(c, RuptureRadius, RuptureCloudTicks);
   RuptureExposurePulse(map, new RM_RuptureZone { center = c, radius = RuptureRadius });
   ```
   ```csharp
   if (ruptures.Count > 0) TickRuptures(now);
   ```
   A naturally firing plant adds the zone and exposes immediately. The same map pass then exposes through the newly added zone again.

   **Repro:** Place one eligible pawn beside one charging Rupture plant. Instrument `RuptureExposurePulse`, then allow the plant to reach its top through normal ticking. Observe two calls for that zone on the same game tick. At the default chance, two eligible rolls give a 15.36% chance of at least one success rather than 8%.

   **Confidence:** high. The call sequence is entirely in this slice.

7. **The master switch is absent from the ambient-band gate**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/ExplosiveGrowth/Source/ExplosiveGrowthMod.cs` — `ExplosiveGrowthSettings.BandsOn`
   ```csharp
   public static bool BandsOn => bandsEnabled && RimMandrake.Biomes.RM_BiomesSettings.Enabled(RosterKey);
   ```
   Turning `enabled` off leaves `BandsOn` true when the band and roster switches remain enabled. The band postfix uses this property, despite the master-switch tooltip promising the ambient rate supplied by the rest of the mod list.

   **Repro:** On an in-scope map, leave everyday growth enabled and turn only “Explosive plant growth enabled” off. Compare a banded plant’s growth rate. A direct scripted call to the band postfix also demonstrates that `enabled = false` does not inhibit its multiplication.

   **Confidence:** high for the missing runtime gate. Whether the unseen `PatchApplier` separately removes this patch needs verification.

8. **Hydroponics and pots receive the bonus and can enter the destructive cycle**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs` — `GrowthFactorFor`, `Sink.TryGetPlant`
   ```csharp
   return ledger.GrowthFactor(plant.Position, Find.TickManager.TicksGame, prof != null && prof.Soaks, ExplosiveGrowthSettings.soakMultiplier);
   ```
   ```csharp
   soaks = prof != null && prof.Soaks && RM_TopResolver.Effective(prof.top) != RM_GrowthTop.None;
   ```
   Neither eligibility path distinguishes a plant inside a grower. The supplied H1 ruling requires vanilla speed and no cycle there.

   **Repro:** Grow corn in a hydroponics basin on an in-scope map. Soak its cell through the API. Compare growth before/after soaking, then mature it and wait through the charge period. The grower supplies no exemption from acceleration or Churn.

   **Confidence:** high. Both growth and charging eligibility omit the grower condition.

9. **The runtime still applies the explicitly superseded stacked rate model**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/ExplosiveGrowth/Source/ExplosiveGrowthMod.cs` — multiplier defaults; `src/RimMandrake/ExplosiveGrowth/Source/RM_ExplosiveGrowthPatches.cs` — both GrowthRate postfixes
   ```csharp
   public static float defaultMultiplier = 4f;
   public static float wetAmbientMultiplier = 10f;
   public static float soakMultiplier = 10f;
   ```
   The supplied rulings replace these bands with archetype rates. This implementation instead gives an ordinary non-tree banded plant ×4 dry and ×40 soaked, and a wet-biome plant ×10 dry and ×100 soaked. There is no archetype distinction or vanilla-crop water requirement.

   **Repro:** On an in-scope map, measure a qualifying non-tree plant with both tiers disabled, then enabled dry, then soaked. Repeat in a named wet biome. The ratios follow the old stacked model rather than the ruled ×0.1/×10 and ×4 rates.

   **Confidence:** high. This is an implementation/spec mismatch explicitly exposed by the supplied defaults and multiplication paths.

10. **Removing a water source leaves a full day of unexplained irrigation**

    **Severity:** wrong behaviour  
    **Location:** `src/RimMandrake/ExplosiveGrowth/Source/RM_SoakSources.cs` — `IrrigationSoakTicks`, `PulseIrrigation`; `src/RimMandrake/ExplosiveGrowth/Source/Kernel/RM_ExplosiveGrowthKernel.cs` — `TrySoak`
    ```csharp
    private const int IrrigationSoakTicks = GenDate.TicksPerDay;
    ```
    ```csharp
    if (!soakUntil.TryGetValue(c, out prior) || prior < until) soakUntil[c] = until;
    ```
    Source disappearance has no corresponding revocation. Once accepted, irrigation becomes a day-long timestamp independent of the channel’s continued contents. That contradicts the supplied presence-based water ruling.

    **Repro:** Let an accepted channel source soak a plant. Immediately drain/remove the source after its irrigation slice runs. Check `IsSoaked` and plant growth: the cell retains its bonus for almost a day and can continue charging after the visible source is gone.

    **Confidence:** high for timestamp persistence. The external reader determines initial acceptance, but cannot revoke these entries through the shown read path.

11. **Slime irrigation waters every eligible species**

    **Severity:** wrong behaviour  
    **Location:** `src/RimMandrake/ExplosiveGrowth/Defs/ExplosiveGrowth/RM_ExplosiveGrowthRoster.xml` — `irrigationFluids`; `src/RimMandrake/ExplosiveGrowth/Source/RM_SoakSources.cs` — `PulseIrrigation`
    ```xml
    <li>RM_Fluid_SlimeRed</li>
    <li>RM_Fluid_SlimeGreen</li>
    <li>RM_Fluid_SlimeWhite</li>
    ```
    Those fluids join one global accepted set. Once their cells are soaked, plant eligibility only asks whether the profile `Soaks`; no liquid identity reaches the plant. The supplied T2 ruling restricts these liquids to adapted plants.

    **Repro:** Put ordinary corn beside a dug channel containing an accepted slime fluid. Wait for the irrigation sweep. Corn receives the same soak multiplier and charge eligibility as an adapted slime plant.

    **Confidence:** high. The cell ledger loses source chemistry, and profiles contain no adaptation field.

12. **The flagship BloomCrop resolves to Churn, not Burst**

    **Severity:** wrong behaviour  
    **Location:** `src/RimMandrake/ExplosiveGrowth/Source/RM_ExplosiveGrowthRegistry.cs` — `Rebuild`; `src/RimMandrake/ExplosiveGrowth/Defs/ThingDefs_Plants/RM_BloomCrop.xml`
    ```csharp
    var p = new RM_PlantProfile { top = RM_GrowthTop.Churn };
    ```
    The supplied BloomCrop def has no growth extension, and the supplied roster contains no `RM_BloomCrop` row. Consequently, the plant described as the flagship BURST crop receives the default Churn.

    **Repro:** Spawn `RM_BloomCrop`, query `RM_ExplosiveGrowthRegistry.For(p.def).top`, then soak and mature it. The profile reports Churn; its top lacks Burst’s hay, pawn damage and permissive sprout ring.

    **Confidence:** high within this slice. An extension or roster supplied elsewhere could override this; none is shown.

13. **Turning suppression off leaves existing suppression fully operative**

    **Severity:** wrong behaviour  
    **Location:** `src/RimMandrake/ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs` — `Suppress`, `IsSuppressed`; `src/RimMandrake/ExplosiveGrowth/Source/Kernel/RM_ExplosiveGrowthKernel.cs` — `TrySoak`
    ```csharp
    if (!ExplosiveGrowthSettings.suppressionEnabled) return;
    ```
    ```csharp
    if (IsSuppressed(c, now)) return false;
    ```
    The switch prevents new suppression writes. Existing entries still refuse soaking and sprouting, with no setting check on those reads.

    **Repro:** Suppress a cell for several days. Turn suppression off. Attempt to soak it through the API and sow a ring across it. Both remain blocked until the original expiry.

    **Confidence:** high. The writer and readers implement different toggle semantics.

14. **Public duration inputs can overflow into immediate expiry**

    **Severity:** wrong behaviour  
    **Location:** `src/RimMandrake/ExplosiveGrowth/Source/Kernel/RM_ExplosiveGrowthKernel.cs` — `TrySoak`, `Suppress`
    ```csharp
    int until = now + Math.Max(1, ticks);
    ```
    Positive durations are accepted without limiting the addition. A duration near `int.MaxValue` overflows the expiry in ordinary unchecked arithmetic; checked arithmetic throws instead.

    **Repro:** After game tick zero, call `ExplosiveGrowthAPI.Soak(map, validCell, int.MaxValue)`. It can return true while `IsSoaked` immediately returns false. Repeat through `Suppress` with the same duration.

    **Confidence:** high. The public API admits the input and the addition is unprotected.

15. **The tell stage never moves backwards during relaxation**

    **Severity:** cosmetic / wrong behaviour  
    **Location:** `src/RimMandrake/ExplosiveGrowth/Source/Kernel/RM_ExplosiveGrowthKernel.cs` — `RM_EgLedger.Pass`
    ```csharp
    if (want > rec.stage)
    ```
    ```csharp
    if (rec.stage == RM_TellStage.Tremble || rec.stage == RM_TellStage.Creak) sink.OnTellPuff(c);
    ```
    Scale and hue follow the current charge, but stage only increases. A relaxing Tremble plant keeps emitting tremble puffs below the tremble threshold. A plant that reached Silence remains silent if dried partway and re-wetted, suppressing subsequent warning transitions.

    **Repro:** Charge a plant to 0.97, dry it until charge falls below 0.7 without reaching zero, then re-soak it. Query its record during decay and recharge: `stage` remains Silence, and the renewed approach to the top emits no creak.

    **Confidence:** high. The one-way stage assignment is explicit.

16. **BloomBurst can resurrect expired soak footprints**

    **Severity:** wrong behaviour  
    **Location:** `src/RimMandrake/ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs` — `SoakedCells`; `src/RimMandrake/ExplosiveGrowth/Source/RM_IncidentWorker_BloomBurst.cs` — `TryExecuteWorker`
    ```csharp
    public IEnumerable<IntVec3> SoakedCells => ledger.soakUntil.Keys;
    ```
    ```csharp
    List<IntVec3> floor = comp.SoakedCells.ToList();
    if (floor.Count == 0) floor = FallbackFloor(map);
    ```
    Dictionary membership is not current wetness. Expired entries remain until the next pass. The incident treats them as an active flood footprint, suppresses fallback generation, and refreshes them.

    **Repro:** Immediately after a component pass, soak one roofed or paved cell for one tick. Advance two ticks, staying before the next pass. Confirm `IsSoaked` is false, then execute a test BloomBurst incident. It re-soaks that stale cell instead of selecting the fertile fallback footprint.

    **Confidence:** high. The snapshot omits the expiry predicate that `IsSoaked` uses.

17. **The static component cache retains an abandoned map**

    **Severity:** perf — memory retention  
    **Location:** `src/RimMandrake/ExplosiveGrowth/Source/RM_MapComponent_ExplosiveGrowth.cs` — static cache and `For`
    ```csharp
    private static Map cachedMap;
    private static RM_MapComponent_ExplosiveGrowth cachedComp;
    ```
    Both are strong static references. The only explicit reset shown is during `PostLoadInit`; there is no removal/new-game cleanup. The cache retains the last queried map until another non-null map replaces it.

    **Repro:** Query the component on the only settlement map, abandon that settlement and remain on the world map. Inspect these fields or a memory snapshot. They still reference the removed map and its component.

    **Confidence:** high for the retained reference. This pins one map, not an unbounded collection; another `For` call or post-load reset releases it.

18. **The test-only scope override leaks across games in the same process**

    **Severity:** wrong behaviour  
    **Location:** `src/RimMandrake/ExplosiveGrowth/Source/RM_ExplosiveGrowthRegistry.cs` — `TestScopeAll`, `BiomeInScope`; `src/RimMandrake/ExplosiveGrowth/Source/RM_ExplosiveGrowthProof.cs` — `SetTestScopeAll`
    ```csharp
    public static bool TestScopeAll;
    ```
    ```csharp
    ExplosiveGrowthSettings.applyInOtherBiomes || ScopeForcedBy != null || TestScopeAll
    ```
    “Never Scribed” prevents disk persistence; it does not reset a static when loading another save or starting another game. No game-start reset is shown, despite the field’s comment promising one.

    **Repro:** Call `ProofTestScopeAllOn`. Without calling its Off counterpart or restarting RimWorld, load another save on a vanilla biome with `applyInOtherBiomes = false`. `ProofScope` still reports the override and permits the mechanic there.

    **Confidence:** high within the supplied lifecycle code. Only an unseen reset could prevent it.

### Outside this slice

- **Scribe dictionary working-list reuse:** `ExposeData` shares `tmpKeys` across all three dictionaries and `tmpInts` across two. Whether this corrupts a round trip depends on the exact Verse `Scribe_Collections.Look` phase behaviour, which is not supplied. I would test populated, distinct dictionaries before declaring this safe or broken.
- **Collection/gamble/jackpot ordering:** Whether a successful destructive gamble duplicates already-created harvest products, or skips another mod’s required collection prefix, requires vanilla’s collection caller and the other patches.
- **Shared `visualSizeRange` mutation:** The Print prefix temporarily edits the shared ThingDef. Nested same-def printing could compound scales, but establishing an actual trigger requires another print patch or caller absent here.
- **Removal safety and DLC prerequisites:** The assembly/def composition, dependency manifest, alias XML, pawn kinds and mutation hediff implementations are absent. This slice cannot establish safe mod removal, old-def migration, or whether all required DLC content is guaranteed.
- **Patch installation and ordering:** `PatchApplier` is absent. Its master gating, live patch removal, namespace filtering and ordering against other mods cannot be verified here.