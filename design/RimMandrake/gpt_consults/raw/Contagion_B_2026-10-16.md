SUBJECT: Contagion (RimWorld 1.6 mod, C# + XML defs) — Contagion_B

Five findings below. Repros are proposed; I did not execute the game.

1. **Three Unfinished attacks instantiate an abstract verb**
   
   **Severity:** crash — verb initialization exception.

   **Location:** `src/RimMandrake/Contagion/Defs/HediffDefs/RM_UnfinishedHediffs.xml:47`; repeated at lines 68 and 89.

   ```xml
   <verbClass>Verb_MeleeAttack</verbClass>
   <defaultCooldownTime>2.0</defaultCooldownTime>
   <meleeDamageBaseAmount>9</meleeDamageBaseAmount>
   ```

   `Verb_MeleeAttack` is the abstract melee base. It cannot be instantiated by the verb tracker. Claw, Spike and Fang all have this defect. The damage implementation is `Verb_MeleeAttackDamage`; alternatively, use the `tools` shape already used by the grown limbs.

   **Repro:**
   1. Spawn an Unfinished.
   2. Using development tools, add `RM_UnfinishedClaw` to an intact external part.
   3. Order melee combat, forcing its hediff verb tracker to initialize.
   4. Inspect the initialization exception. Repeat with Spike and Fang.

   **Confidence:** high. The configured class is abstract; the failure does not depend on the missing randomizer implementation.

2. **Wombpod sacs never receive their hatching ticks**
   
   **Severity:** wrong behaviour.

   **Location:** `src/RimMandrake/Contagion/Defs/ThingDefs/RM_WombpodSac.xml:32`.

   ```xml
   <li Class="CompProperties_Hatcher">
     <hatcherDaystoHatch>3</hatcherDaystoHatch>
     <hatcherPawn>RM_BloodyMess</hatcherPawn>
   ```

   The ThingDef inherits vanilla `ResourceBase` and never sets `tickerType`. That leaves it with `Never`. `ThingWithComps` alone does not schedule ticks, and `CompHatcher` needs normal ticks to advance.

   **Repro:**
   1. Spawn one sac on an ordinary map, outside any container.
   2. Run four simulated days, approximately 240,000 ticks.
   3. Observe that it remains a sac.
   4. Inspect its resolved `tickerType`; repeat after adding `<tickerType>Normal</tickerType>`.

   **Confidence:** high under the named vanilla parent. The required ticking declaration is absent from the complete ThingDef.

3. **A healer mech serum can remove the supposedly mandatory lifespan**
   
   **Severity:** wrong behaviour.

   **Location:** `src/RimMandrake/Contagion/Defs/HediffDefs/RM_UnfinishedHediffs.xml:174`, within `RM_UnfinishedUnraveling`.

   ```xml
   <tendable>false</tendable>
   <scenarioCanAdd>false</scenarioCanAdd>
   <maxSeverity>1.0</maxSeverity>
   ```

   This standalone def never sets `everCurableByItem` to false. `tendable=false` prevents tending; it does not prevent healer-item removal. Removing this hediff removes the XML mechanism enforcing dissolution. The whole-body mutation base elsewhere in this slice explicitly disables item cures, but the lifespan def does not.

   **Repro:**
   1. Spawn a player-owned Unfinished and keep it fed and protected.
   2. Set its unraveling severity to approximately 0.9, with no competing serious conditions.
   3. Administer healer mech serum.
   4. Confirm that “coming apart” disappears.
   5. Keep it continuously spawned for more than four days and check that the original dissolution deadline passes.

   **Confidence:** high for item curability. Whether unseen code later reinstates the lifespan requires inspecting that code.

4. **The organ patch deliberately overwrites another mod’s surgery worker**
   
   **Severity:** wrong behaviour.

   **Location:** `src/RimMandrake/Contagion/Patches/OrganInstallGenomeMatch.xml:33`; the same replacement exists for all four organs.

   ```xml
   <xpath>/Defs/RecipeDef[defName="InstallNaturalHeart"]/workerClass</xpath>
   <value>
     <workerClass>RimMandrake.Contagion.Recipe_InstallGrownBodyPart</workerClass>
   ```

   The match branch accepts *any* existing worker and replaces it. Another mod’s compatibility, rejection, surgical-outcome or transplant logic disappears when this patch runs afterwards. Inheriting from vanilla’s worker cannot preserve an unrelated worker subclass. This affects ordinary organ transplants globally.

   **Repro:**
   1. Create a small compatibility fixture that assigns `InstallNaturalHeart` a `Recipe_InstallNaturalBodyPart` subclass which logs when invoked.
   2. Load that fixture before Contagion.
   3. Inspect the resolved recipe worker: it has become `Recipe_InstallGrownBodyPart`.
   4. Perform the surgery and verify that the fixture worker never executes.

   **Confidence:** high. The unconditional replacement is visible; no particular third-party mod is needed to demonstrate it.

5. **The Monstrous health bonus does not increase pawn body-part health**
   
   **Severity:** wrong behaviour.

   **Location:** `src/RimMandrake/Contagion/Defs/HediffDefs/RM_UnfinishedHediffs.xml:150`.

   ```xml
   <MeleeDamageFactor>0.6</MeleeDamageFactor>
   <MaxHitPoints>40</MaxHitPoints>
   <ArmorRating_Sharp>0.15</ArmorRating_Sharp>
   ```

   Pawn body-part maximum health derives from body-part HP and the pawn’s health scale. The Thing `MaxHitPoints` stat does not supply that health. Consequently, the middle entry grants no additional anatomical durability; the damage and armor entries still work.

   **Repro:**
   1. Spawn one healthy Unfinished and pause.
   2. Record its torso’s maximum health using development inspection or a script.
   3. Add `RM_UnfinishedMonstrous` without changing anything else.
   4. Read the same part’s maximum health again: it is unchanged.
   5. Remove the hediff and repeat to eliminate differences between generated pawns.

   **Confidence:** high. This uses the wrong health mechanism for a pawn.

## Outside this slice

- **Save/load and lifetime safety cannot be assessed:** no implementations of the gestation, genome identity, draftprint, quest part, sky component, Coalescence, death workers or haze are provided. Their comments do not establish correct serialization, post-load initialization or despawn handling.
- **Inherited comp duplication needs the parent XML:** inspect merged `AddedMutationBase` and `BurnBase` before accepting the custom emergence and scar comps. The shown children append comps; the unprovided parents determine whether duplicate vanilla/custom effects result.
- **Bulloo consciousness needs verification:** both shown bodies omit a brain, and the custom hood’s tags contain only `MovingLimbCore`. Establish the resulting capacity behaviour before calling these bodies functional; the necessary vanilla capacity implementation is not included.
- **Dependency resolution remains unproven:** the biome directly names `GU_*` terrains and `Biomes/AB_OcularForest`. Also, the live RustPuff gate names `mandrake.rm.biomes`, while the validation document says `mandrake.rm.therot`. Provider defs, assets and composition manifests are absent.
- **Harmony ordering, setting-toggle cleanup, multi-map behaviour and tick catch-up remain unaudited:** the corresponding runtime code is absent.