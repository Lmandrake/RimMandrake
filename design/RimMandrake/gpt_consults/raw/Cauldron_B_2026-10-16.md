Cauldron (RimWorld 1.6 mod, C# + XML defs) — slice Cauldron_B.

Source review only; these repros have not been executed. Eight findings are supportable without inventing missing implementations.

1. **The “nonlethal” metal load can kill a pawn with compromised breathing**

   **Severity:** wrong behaviour — pawn death.

   **Location:** `src/RimMandrake/Cauldron/Defs/HediffDefs/RM_VentMetalLoad.xml:83`

   ```xml
   <capacity>Breathing</capacity>
   <offset>-0.15</offset>
   ```

   Capping hediff severity at 1 does not protect vital capacities. This additive penalty can push an already impaired pawn’s breathing to zero. The additional Consciousness penalty at lines 91–92 presents the same class of risk. This contradicts the file’s explicit “it cripples, it does not kill” contract.

   **Repro:** In a test mod, give a healthy human a temporary hediff with a Breathing offset of `-0.90`. Confirm the pawn survives with approximately 10% breathing. Add `RM_VentMetalLoad`, set its severity to `0.7`, and advance health ticks. The additional `-0.15` can eliminate the remaining breathing capacity.

   **Confidence:** high. The def directly subtracts from a vital capacity; there is no protective capacity floor in these modifiers.

2. **Drinking and scaffold damage continue after the drinker is moved away**

   **Severity:** wrong behaviour.

   **Location:** `src/RimMandrake/Cauldron/Source/RM_CauldronVents.cs` — `RM_JobDriver_VexxissDrinkVent.MakeNewToils()`, drinking `tickAction`.

   ```csharp
   if (tap != null)
       tap.parent.TakeDamage(new DamageInfo(DamageDefOf.Blunt, RM_VentGasKernel.PryDamage, 0f, -1f, pawn));
   ```

   Adjacency is established once by `GotoThing`. The subsequent 900-tick drinking toil never checks whether the pawn still touches the vent. Both suppression and damage operate directly on the target reference.

   **Repro:** Spawn a vent, a scaffold over it, and a wild vexxiss. Start its drinking job and wait until the drinking toil begins. Through a debug script, assign the pawn a distant, valid `Position` **without ending its job**. Advance ticks. Observe the distant vent’s suppression increasing and, with prying enabled, the scaffold losing HP.

   **Confidence:** high. Neither the tick action nor the drinking toil has a continuing proximity condition. The repro deliberately preserves the job; a teleport implementation that cancels jobs would mask this.

3. **Disabling vent drinking does not cancel an animal’s approach**

   **Severity:** wrong behaviour.

   **Location:** `src/RimMandrake/Cauldron/Source/RM_CauldronVents.cs` — `RM_JobDriver_VexxissDrinkVent.MakeNewToils()`.

   ```csharp
   yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
   ```
   ```csharp
   drink.AddFailCondition(() => !RM_CauldronSettings.vexxissDrinksVentsEnabled);
   ```

   The setting condition belongs only to the drinking toil. The preceding travel toil has no equivalent condition. A slow vexxiss can continue a lengthy forced trip after a setting advertised as applying “now” is disabled.

   **Repro:** Place a wild vexxiss far from a reachable vent. Start `RM_VexxissDrinkVent`. While it is walking, disable “Vexxiss drink from vents.” Advance ticks and inspect its current job. This driver continues the approach and only encounters the setting failure when it reaches the drinking toil.

   **Confidence:** high. The condition’s attachment and the order of the two toils are explicit.

4. **The supposedly four-weather biome still admits vanilla dry thunderstorms**

   **Severity:** wrong behaviour.

   **Location:** `src/RimMandrake/Cauldron/Defs/BiomeDefs/RM_Cauldron.xml:134`

   ```xml
   <DryThunderstorm>1</DryThunderstorm>
   ```

   Clear and Fog are explicitly zeroed, but DryThunderstorm retains positive commonality. The biome therefore admits a fifth weather outside its authored twilight weather set, including stock lightning and weather presentation.

   **Repro:** Generate a temperate Cauldron map. Repeatedly advance natural weather transitions using a debug harness and log the selected weather defs. Check for `DryThunderstorm`; its occurrence remains subject to normal weather eligibility rules. A static regression check can also assert that every positive commonality belongs to the four `RM_` weathers—this row fails immediately.

   **Confidence:** high for the erroneous positive weight. The precise frequency depends on vanilla weather selection, so `1/101` should not be treated as its actual probability.

5. **Roasting tsevrix explicitly preserves the raw-food mood penalty**

   **Severity:** wrong behaviour.

   **Location:** `src/RimMandrake/Cauldron/Defs/ThingDefs_Items/RM_CauldronFloraItems.xml:51`

   ```xml
   <foodType>VegetableOrFruit</foodType>
   <preferability>MealSimple</preferability>
   <tasteThought>AteRawFood</tasteThought>
   ```

   The cooked product is preferred like a simple meal while explicitly requesting the thought for eating raw food. Cooking removes the toxin but leaves an unexpected mood punishment.

   **Repro:** Use a colonist whose ideology does not exempt raw-food penalties. Roast five pulp at a stove, then order the colonist to consume the resulting `RM_TsevrixRoasted`. Inspect the food-related memory.

   **Confidence:** high. `AteRawFood` is explicitly assigned to the roasted product.

6. **The advertised campfire preparation route is absent**

   **Severity:** wrong behaviour.

   **Location:** `src/RimMandrake/Cauldron/Defs/RecipeDefs/RM_TsevrixRoast.xml:23`

   ```xml
   <li>FueledStove</li>
   <li>ElectricStove</li>
   ```

   These are the complete `recipeUsers` entries. The raw pulp’s description tells the player to roast it “at a stove or campfire,” but this recipe supplies no campfire route. This matters particularly for a tribal start relying on the advertised way to detoxify its harvest.

   **Repro:** Build a campfire and a fueled stove. Stock at least five `RM_TsevrixPulp`. Compare their bill menus: “roast tsevrix pulp” is available at the stove and absent at the campfire.

   **Confidence:** high within this slice. The recipe has no parent and explicitly lists only the two stoves. An additional campfire registration elsewhere would need separate evidence.

7. **Fauna remain forcibly hushed after the falter ends or the feature is disabled**

   **Severity:** wrong behaviour.

   **Location:** `src/RimMandrake/Cauldron/Source/RM_CauldronVents.cs` — `RM_MapComponent_CauldronVents.HushFauna()`.

   ```csharp
   Job hush = JobMaker.MakeJob(JobDefOf.Wait_MaintainPosture);
   hush.expiryInterval = ext.hushJobTicks;
   p.jobs.StartJob(hush, JobCondition.InterruptForced);
   ```

   The map component renews these jobs during faltering, but never releases them. Ending the falter only resets counters; disabling `faunaHushEnabled` only stops further renewals. Existing waits can continue for almost the full 300 ticks after their reason disappears.

   **Repro:** Start a bloom transition with an awake wild eskith beside a vent. Wait for a 240-tick hush pulse. Immediately disable fauna hush—or finish the weather transition. Inspect the pawn’s job while advancing individual ticks: `Wait_MaintainPosture` can remain until its original expiry.

   **Confidence:** high. No termination condition ties the issued job to either the setting or the falter.

8. **The displayed hush count is lost across save/load**

   **Severity:** cosmetic.

   **Location:** `src/RimMandrake/Cauldron/Source/RM_CauldronVents.cs` — `RM_MapComponent_CauldronVents.ExposeData()` and `hushedThisFalter`.

   ```csharp
   Scribe_Values.Look(ref generated, "rmVentsGenerated", false);
   Scribe_Values.Look(ref falterNotified, "rmVentFalterNotified", false);
   ```
   ```csharp
   public int hushedThisFalter;
   ```

   The count shown in every vent’s inspect string is neither saved nor reconstructed. Existing hush jobs can survive loading while the displayed count resets to zero. Subsequent renewals do not count those animals because their current job is already `Wait_MaintainPosture`.

   **Repro:** During a falter, wait until a vent reports a positive number of natives hushed. Save and reload before that transition finishes. Inspect the same vent while the same animals are still waiting: the count starts at zero and is not restored by their normal renewal.

   **Confidence:** high. Serialization omits the field, and the increment explicitly excludes pawns already doing the wait job.

## Outside this slice

These are unresolved checks, not additional established findings:

- **Suush death explosions:** `RM_CauldronFauna.xml` relies on `<explodeOnKilled>true</explodeOnKilled>` and its commentary assumes pawn death invokes `CompExplosive.PostDestroy`. That lifecycle assumption needs verification against the engine implementation. Test lethal Cut damage separately from the existing nonlethal Cut control and Bullet test.
- **DLC and donor dependencies:** Vexxiss and nettle defs name Odyssey toxic-water terrains without local gates; CrystalMit’s weird-food list retains `GU_` and `AB_` names. Their field types, resolution behavior, and the actual dependency manifest are absent. Missing references or safe string fallbacks cannot be established here.
- **Permanent dusk:** the supplied weather defs specify different day/night sky colors—for example, `RM_CauldronWeathers.xml:49` uses `(0.66,0.62,0.70)`, while line 67 uses `(0.30,0.28,0.36)`. Whether another lighting implementation overrides that cycle is not shown.
- **Turning visual features off:** `RemeshAllMaps()` returns when both `RM_AssayFlecks.Active` and `RM_DewfallSaturation.Active` are false. If those properties track the current toggles, switching the last effect off could skip the cleanup remesh. Their implementations are needed to establish this.
- **Persistence, removal safety, and Harmony conflicts:** the gas grid, gas tap, ruin kit, exposure component, kernels, startup gates, and Harmony patches are absent. Their serialization, cache lifetime, numerical guards, patch ordering, and behavior after mod removal cannot be audited from these files.