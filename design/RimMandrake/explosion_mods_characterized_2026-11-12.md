# Explosion mods on our lists, characterized (2026-11-12)

For Explosive Knockback (EK, `mandrake.rm.explosiveknockback`), coverage gap 2.

**Owner's words (2026-11-12, ~4:10 PM PST, on the EK certification card "Show me the 4 gaps, then I certify"):**
> "2: Search our modlist for explosion. There is at least one that makes them bigger and more impressive, we should have characterized them first I now see."

**Owner's words (relayed by the Conductor, same sitting):**
> "We should decide if we need those other explosion mods we have or they should be absorbed into this one."

This document decides nothing and changes no mod list. The choices that are his are at the end.

## How this was measured

- **Mod roots.** Both were swept, including inactive mods: `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods` and the workshop folder `...\workshop\content\294100`.
  - 1373 About.xml files were read; 68 mention explosions or blasts.
  - Scratch: `D:\ClaudeWork\rimmandrake\ek_certify_20261112\about_hits.json`.
- **Tiers.** Each ModsConfig was parsed, not grepped:
  - live: 16 mods, the owner's current sitting;
  - MINIMAL: 27 mods (`infrastructure\state\modlists\ModsConfig.MINIMAL.xml`);
  - FULL.LATEST: 316 mods (`infrastructure\state\modlists\ModsConfig.FULL.LATEST.xml`).
- **Defs.** These come from the FULL def dump through `measure`: MEASURED 59262 defs, capture 2026-11-12T08:10:06Z.
  - The capture predates commit `bb195048ac` (10:25 PST), which set Flame's knockback force to 0.5. That is why the dump still shows Flame at force 0. It is a stale dump, not a defect.
- **Harmony targets.** Every DLL of the 310 FULL.LATEST mods found on disk (635 DLLs) was searched for the names of our patch targets and their neighbours. This is a literal-string search, so a hit is a lead, not proof of a patch.
  - Scratch: `D:\ClaudeWork\rimmandrake\ek_certify_20261112\dll_hits2.json`.
- **EK's Harmony targets:**
  - `DamageWorker.ExplosionDamageThing`
  - `CompShield.PostPreApplyDamage`
  - `Thing.TakeDamage`
  - `PawnFlyer.CheckDestination` and `PawnFlyer.RespawnPawn`
- **Decompiled.** Forge's DLL was decompiled with ILSpy (see "Code reading, 2026-11-12" below). Anything only a live blast can show is marked UNMEASURED.

## The explosion-effect mods

None of these four is active on live (16) or on MINIMAL (27). All four are active on FULL.LATEST (316).

### 1. Extra Explosion Effects: the one that makes blasts bigger and more impressive

- packageId `Keshash.ExtraExplosionEffects`, workshop 3066208882, author Keshash. Depends on `brrainz.harmony`.
- **What it changes.** It adds a Harmony **Postfix on `GenExplosion.DoExplosion`** (C# source ships with the mod, 753 lines). The postfix adds visual effects to the blast.
  - **Bomb blasts** get extra blast flecks, lingering smoke, dirt or stone debris, soot, a crater and orange sparks.
  - **Big blasts** (damage over 300 or radius 2 or more) also get a shockwave and screen quake, with Royalty.
  - **Stun** gets sparks and ripples.
  - It changes no damage, radius or trigger. It also ships a Combat Extended variant.
- **What our knockback does with it today.**
  - The target differs from ours: it runs after the explosion starts, while ours runs per damaged thing. No shared target.
  - The throw itself should be unchanged, because no damage or radius changes.
  - UNMEASURED: how its smoke, crater and quake read next to our thrown pawns and items and the carrier shadow.
  - UNMEASURED: whether its debris flecks hide the flight.
- **Code versus art.** About 60% code, 40% art: 10 PNG flecks, which are **donor art**.
- **Licence.** No licence file and no licence text in About.xml, so UNMEASURED. Treat it as all rights reserved: absorbing means re-implementing the idea in our own code with our own flecks, not copying.
- **Absorb job.** About 2 to 3 agent-days [guess ~50%]. A "blast dressing" layer in EK on its own hook, our own flecks through the art-eval pipeline, and a settings toggle.
- **Collision risk if kept.** Low. No shared Harmony target with EK.
- **Recommendation.** Absorb the idea (re-implement, own art), then drop it from the list.

### 2. Better Explosions

- packageId `nephlite.advexplosions`, workshop 2572683272, author Nephlite.
- **What it changes.** It is XML only, with no C#.
  - It **redefines the vanilla DamageDefs** Bomb, Flame, BombSuper, Extinguish, Smoke and Stun with new flecks and colours (`Mote_AdvExplosion1`, `Mote_AdvExplosion2`, `Mote_AdvFlame`, `SubMote_AdvParticle*`), keeping the same damage values.
  - It also patches the Smoke fleck texture.
  - The FULL dump confirms it: Bomb uses `Mote_AdvExplosion1` with damage 50, and Flame uses `Mote_AdvFlame`.
- **What our knockback does with it today.**
  - MEASURED in the FULL dump: under its redefinition, Bomb and BombSuper still carry our knockback extension (force 1), so our tuning survives it.
  - MEASURED from its files (see Code reading below): purely visual. UNMEASURED live.
- **Code versus art.** 0% code, 100% art: 11 PNG plus an Assets.zip, all **donor art**.
- **Licence.** MEASURED: none. No licence file and no licence or credit text in About.xml. Treat as all rights reserved. Absorbing means drawing our own recolour.
- **Absorb job.** About 1 to 1.5 agent-days [guess ~60%], almost all of it art.
- **Collision risk if kept.** Low. No Harmony. It rewrites the same DamageDef nodes our patch adds to, and the dump shows they coexist.
- **Recommendation.** Drop it from the list. It recolours what #1 already dresses up, and it is all donor art.

### 3. Dynamic Effects Forge

- packageId `blues.forge`, workshop 3735443951, author Blues.
- **What it changes.** "Overrides vanilla explosions with multi-stage volumetric particle sequences."
  - Its DLL (BluesForge.dll, 92 KB, no source shipped) patches `Explosion.StartExplosion` with a **Postfix only**, never a Prefix, and never a transpiler (decompiled; see Code reading below).
  - Its BlastMatchDefs map Bomb, BombSuper, Flame, Smoke, Extinguish, Stun and EMP to its own effects.
  - It also adds a humidifier building and patches `Proj_Foam`, `Filth_FireFoam`, `ElectricalSpark` and the chemshine barrel.
- **What our knockback does with it today.**
  - MEASURED from the decompiled code: it does not change what reaches our `ExplosionDamageThing` hook (no prefix, no skip, no radius, damage, damage type or cell change, no list change). See Code reading below.
  - UNMEASURED: how it looks beside #1, which dresses the same blasts.
- **Code versus art.** About 25% code, 75% art: 51 PNG plus an Assets.zip, all **donor art**.
- **Licence.** MEASURED: none. No licence file, no licence or copyright text in About.xml, and none in the decompiled code. Treat as all rights reserved.
- **Absorb job.** About 3 to 5 agent-days [guess ~35%]: volumetric multi-stage effects and their art.
- **Collision risk if kept.** Low for our knockback (visual postfix only). Medium for looks: it overlaps #1 and hides the vanilla blast visuals by default.
- **Recommendation.** Drop it from the list on overlap and donor-art grounds. Its code is no longer a reason: it cannot change our throws.

### 4. Custom Gas Types

- packageId `Greg.CustomGasTypes`, workshop 3756399441, author Legator.
- **What it changes.**
  - Gas shells with their own `CGT_*GasRelease` DamageDefs (harmsHealth false), which release gas from explosions through a DamageDef extension.
  - Its DLL overrides `DamageWorker.ExplosionAffectCell` in a subclass, `DamageWorker_SpawnsCustomGas`. It is an override, not a Harmony patch, and it calls `base` first (read from its shipped source).
- **What our knockback does with it today.** Its damage types do not harm health and carry no EK extension, so they throw nothing, the same as vanilla ToxGas. MEASURED from source: its worker calls `base.ExplosionAffectCell` first, so the vanilla damage path, and our hook, run unchanged. UNMEASURED live.
- **Code versus art.** About 70% code (1445 lines of source ship with it), 30% art: 36 PNG, donor art.
- **Licence.** MEASURED: none. No licence file, no licence text in About.xml or the csproj; the source ships but with no terms. Treat as all rights reserved.
- **Absorb job.** Not EK's job. It is a gas system, not a blast effect.
- **Collision risk if kept.** Low. Its target is not one of EK's.
- **Recommendation.** Keep it separate. It is out of EK's scope.

## Other mods whose explosions our knockback meets (content, not effects)

These mods do not change how blasts look. They use explosions, and what matters is the damage type:

- **Bomb or Flame (plain vanilla types).** Our patch tunes these: Bomb 1.0, Flame 0.5.
- **Untuned harmful types.** They throw at `unpatchedHarmfulPercent` (default 100).
- **Ours, with their own forces.** These are tuned already.

| mod (packageId) | tier | explosion damage types (FULL dump) | what EK does today |
|---|---|---|---|
| Outer Rim Core (`neronix17.outerrim.core`) | MINIMAL, FULL | Bomb (21 users), Flame (plasma grenade, plasma mine), **OuterRim_Sonic (untuned, harmful)**, ProtonBomb/Turbolaser/Ion/CryoBan (force 1) | Bomb and Flame tuned; Sonic at the other-mods percent |
| Jawa Armoury (`mandrake.rsw.armoury`) | FULL | `guy762_GrenadeDamage_frag/sonic/ion/thermaldet`, `guy762_ExplosiveDamage_*`, `RSW_Blaster_Damage` (untuned, harmful) | other-mods percent |
| Rimefeller (`dubwise.rimefeller`) | FULL | Flame (`Bullet_Shell_Napalm` r2.9, `CrudeCracker`) | Flame at half |
| Vanilla Gravship Expanded (`vanillaexpanded.gravship`) | FULL | `VGE_AstrofireDamage` (untuned), Thump (force 2.5) | mixed |
| Vanilla Genetics Expanded (`vanillaexpanded.vgeneticse`) | FULL | `GR_DistortionDamage` (untuned), `GR_MiniGrain` (force 1) | mixed |
| VFE Security (`vanillaexpanded.vfesecurity`) | FULL | Blunt and RangedStab explosions (catapult, ballista); Flame and Bomb shells | Blunt and RangedStab at the other-mods percent |
| Kinetic Arms (`mandrake.rm.kineticarms`, ours) | FULL | `RM_Concussive_*`, `RM_Repulse_*` (forces 2 to 4) | tuned by design |

Two more facts from the DLL search:

- **HugeThings shares our hook.** HugeThings (`mandrake.rm.hugethings`, ours) also prefixes `DamageWorker.ExplosionDamageThing` to reroute trunk cells. This is a known co-tenant on our hook, both ours.
- **JecsTools has its own knockback.** JecsTools (`jecrell.jecstools`, FULL) has its own `HediffComp_Knockback`, a melee or ability knockback, not a blast one. There is no shared target.

## The three unnamed lanes of `sc_blast_kinds`

All three can use real defs from `neronix17.outerrim.core`, which is already on the MINIMAL list. None needs a labelled test damage type.

1. **A modded damaging explosion.** `OuterRim_SonicGrenadeProj`, damage type `OuterRim_Sonic`.
   - The type is harmful and carries no EK extension, so it throws at the other-mods percent: expected 100 at the default, and nothing at 0 (the scene's control).
2. **Stacking lane, a modded Flame explosion.** `OuterRim_PlasmaGrenadeProj`, damage type Flame.
   - Expected 50 at the other-mods percent 50: the Flame tuning alone, not 25.
3. **Stacking lane, a modded explosion of an untuned type.** `OuterRim_SonicGrenadeProj` again, at the other-mods percent 50.
   - Expected 50: the other-mods percent alone.

Stage reads each def's damage type back from the loaded defs; the dump readings above are from FULL.

## Choices that are his

1. **Bigger, showier blasts (Extra Explosion Effects).**
   - (a) **Recommended:** absorb the idea into EK with our own flecks, then drop the mod. About 2 to 3 agent-days. No donor art stays, and one mod owns blasts.
   - (b) Keep the mod as it is. Free now, but donor art stays and the look is not ours to tune.
   - (c) Drop it with no replacement. Blasts go back to vanilla looks.
2. **Better Explosions (a recolour of vanilla blasts).**
   - (a) **Recommended:** drop it from the list. Choice 1 already covers the show, and it is all donor art.
   - (b) Absorb it by drawing our own recolour, about 1 agent-day of art.
   - (c) Keep it.
3. **Dynamic Effects Forge.**
   - (a) **Recommended:** drop it from the list. It overlaps choice 1, its closed code patches the start of every explosion, and its effect on our throws is unmeasured.
   - (b) Keep it, and owe one live look of a blast with EK and Forge together first.
   - (c) Absorb it, about 3 to 5 agent-days.
4. **Custom Gas Types.**
   - (a) **Recommended:** keep it separate. It is a gas system, not a blast effect, and EK already ignores its gas.
   - (b) Drop it.

## Code reading, 2026-11-12

Scratch (never committed, it is someone else's code): `D:\ClaudeWork\rimmandrake\conductor\explosion_mods_20261112\forge_src\`.

### Decompiler that worked

- WSL has no dotnet. Windows has only the .NET 8.0.21 runtime, no SDK, so `dotnet tool install` fails ("No .NET SDKs were found").
- What worked: the ilspycmd 9.1.0.7988 package downloaded from nuget as a zip, unpacked to `D:\ClaudeWork\rimmandrake\tools\ilspy\pkg`, and run on the Windows runtime: `dotnet.exe pkg\tools\net8.0\any\ilspycmd.dll -p -o <out> BluesForge.dll`. It produced 6458 lines of C# in project form. Nothing was installed in the repo or ~/dev.

### A. Dynamic Effects Forge (blues.forge), from the decompiled code

**Every Harmony patch.** Set up in `Blues/ForgeInit.cs`, lines 34 to 80 (one Harmony id, `blues.forge`), plus `val.PatchAll()` for the attribute patches:
- `Explosion.StartExplosion`: Postfix only, `Patch_Explosion_AddCustomVFX.Postfix` (ForgeInit.cs line 52 to 56). No prefix, no transpiler.
- `CombatExtended.ExplosionCE:StartExplosionCE`: the same Postfix, only if Combat Extended is loaded (lines 58 to 62).
- `Projectile.Launch` (the overload taking a Vector3): `PatchProjectileLaunch.Postfix`, a visual trail (lines 64 to 68).
- `CombatExtended.Verb_ShootCE:TryCastShot`: `PatchCastShot.Postfix`, only with CE (lines 74 to 78).
- `Graphic_Flicker.DrawWorker`: `Patch_Graphic_Flicker_DrawWorker.Prefix`. It returns false (skips drawing) only for a `Fire` thing when the "wildfire" setting is on and the map's fire danger is below a threshold. Drawing only.
- `Fire.SpawnSmokeParticles`: `Patch_Fire_SpawnSmokeParticles.Prefix`. It returns false to skip smoke particles under the same fire-danger condition. Drawing only.
- The earlier note that it "carries both Prefix and Postfix" on the explosion start was wrong. The two Prefixes belong to the fire drawing patches above.

**What the explosion Postfix does** (`Patch_Explosion_AddCustomVFX.cs`, lines 21 to 70):
- It runs after vanilla's `StartExplosion` has returned, so it cannot skip vanilla, and it never touches `radius`, `damType`, `damAmount`, the cells or the thing lists. It only reads `radius` and `damType`.
- It returns early (does nothing) when the explosion is off the current map or off screen (view rect plus 4 plus radius), when `doPatch` is off, or when it is throttled.
- Its one write is `__instance.doVisualEffects = false` (line 54), only when the "hide vanilla" setting `overwrite` is on, which is the default. That field only stops vanilla's own flecks and motes.
- It then calls `EffectRunner.Create` with a particle sequence picked by damage type (`BlastCache.explosions`).
- It does not spawn an Explosion. The only damage-adjacent call in the whole assembly is `GenSpawn.Spawn` of a Projectile in `EffectRunner.FireShots` (EffectRunner.cs line 927), reached only when a Forge effect def names a `<projectile>`. The shipped defs leave that empty (`Defs/BluesForge/Explosions/Bomb.xml` line 39, `ExplosionMatcher.xml` line 6, `<projectileDefs />`). A search of the decompiled source for `DamageInfo`, `TakeDamage`, `GenExplosion` and `DoExplosion` found nothing else.

**Does our knockback still see the same things with the same damage? Yes.** Our hook is `[HarmonyPatch(typeof(DamageWorker), "ExplosionDamageThing")]` in `src/RimMandrake/ExplosiveKnockback/Source/RM_Patch_DamageWorker_ExplosionKnockback.cs`, line 15. Forge never patches `DamageWorker`, never changes the explosion's inputs, and its postfix runs after `StartExplosion`. It does not change the list of things damaged or the damage. One caution, from the code as read and not tested live: if vanilla applies the cell damage in the later `Explosion.Tick`, `doVisualEffects` false still only removes flecks. Nothing in the chain changes damage either way.

**Cost.** Throttled by design, not profiled live:
- an effect starts at most once every `oneAtEvery` ticks (BlastSet.cs line 40: default 5, presets 10, 5 and 2);
- explosions outside the camera view are skipped;
- a decaying "visual heat" budget (`MaxInEveryTenSecs`, `maxInEvery` times 5) randomly drops effects in a burst, so a barrage cannot pile up;
- GPU instancing is used if the device supports it, otherwise the vanilla fleck renderer with a log warning.
- UNMEASURED live: the per-tick cost of `EffectRunner` itself.

**Settings that turn its override off** (BlastSet.cs lines 8 to 40, shown in `Forge.cs` lines 268 to 271):
- `doPatch` ("BluesPatchExplosions"): off means the explosion postfix does nothing.
- `overwrite` ("BluesHideVanilla"): off means vanilla's own explosion visuals stay on beside Forge's.
- `vanillaEffects`, `doWild` and `doTame` govern the fire smoke and flicker patches and the fire overlay swap.
- `humidifier` hides the humidifier building from the build menu.

**Licence.** No licence file in the mod folder (About, Assemblies, Assets.zip, Defs, Languages, Patches, Textures) and no licence or copyright text in About.xml or the decompiled code. Treat as all rights reserved.

### A2. Better Explosions (nephlite.advexplosions): purely visual, confirmed from its files

- XML only: `About`, `Defs/DamageDef/Damages.xml` per game folder (1.3 to 1.7), `Patches/DamageDefPatches.xml` per game folder, textures and an Assets.zip. No Assemblies.
- Despite the file name, `Damages.xml` defines only new **FleckDefs** (every top-level def is `ParentName="FleckBase"` or `FleckBase_Thrown`, with only `defName`, `graphicData`, `altitudeLayer`, `fadeInTime`, `solidTime`, `fadeOutTime`, `growthRate` and, for one, `fleckSystemClass`). It defines no DamageDef.
- `DamageDefPatches.xml` (1.6: 12 PatchOperationAdd and 15 PatchOperationReplace; 1.7: 26 xpaths) touches the DamageDefs Bomb, BombSuper, Flame, Extinguish, Smoke, Stun and EMP, and every value it writes is one of `explosionColorCenter`, `explosionColorEdge`, `explosionCellFleck`, `explosionInteriorFleck`. It also replaces the Smoke FleckDef's `texPath`.
- **Fields changed on a DamageDef other than flecks, motes, colours and sounds: none.** No damage, armour, radius, knockback or worker field. It only retargets fleck and colour fields on the DamageDef. (No sound fields appear either.)
- Licence: none; no licence text in About.xml.

### B. Custom Gas Types (Greg.CustomGasTypes, by Legator, v1.1.0, supports 1.6 and 1.7)

**What a player gets.** A Gas Warfare research tab, five chemical gases, and the ways to deliver them:
- **Tear gas.** Riot control. The victim is blinded and chokes. Rarely lethal. Research: after Drug production.
- **Nitrous oxide.** The victim becomes lightheaded, then intoxicated, then anaesthetised. Good for capturing raiders alive. A "gas-happy" mood thought (`CGT_N2OGiggles`) goes with it. Research: after Drug production.
- **Mustard gas.** A persistent blister agent. Chemical burns that can kill without treatment, through four stages up to internal haemorrhaging. Research: after Drug production and Biofuel refining.
- **Halothane.** A knockout gas that is deadly in overdose. Research: after Medicine production and the Multi-analyzer.
- **VX nerve agent.** Rapidly lethal area denial. Research: after Advanced fabrication, Medicine production and the Multi-analyzer.
- **How they work on pawns.** Each gas gives an exposure hediff (`CGT_*Exposure`) with staged capacity penalties. Gases spread, thin out and vent like vanilla gas, are blocked by walls and doors, and are countered by gas masks (mustard and VX only partly, since they act through skin). Tear gas also reduces shooting accuracy like blind smoke.
- **How they are released.** From explosions, through a DamageDef extension (`CGT_*GasRelease`, worker `DamageWorker_SpawnsCustomGas`, which calls the vanilla `ExplosionAffectCell` and then adds gas to cells inside the radius). Also from IED traps.
- **What it adds.** Five gas canisters made at the drug lab (`CGT_Make*GasCanister`); five IED traps (`CGT_TrapIED_*`, research "weaponized gas IEDs"); five 81 mm mortar shells and their recipes (research "weaponized gas shells"). The shells come in a vanilla form, or a Combat Extended ammo form with its own ammo categories when CE is active (`LoadFolders.xml`). It adds one extra DamageDef, `CGT_ArtificialPartCorrosion`.
- **Settings.** One: "Realistic gas colours" (off by default), which recolours the clouds, for example mustard to dark yellow. It takes effect at once.
- **Harmony.** Three patches (`HarmonyPatches.cs`): postfixes on `GasGrid.Notify_ThingSpawned` and `GasGrid.EqualizeGasThroughBuilding`, and one on `ShotReport.HitReportFor`, applied only if a blinding gas exists. None touches explosion damage.
- **Source.** 1445 lines are in the mod's `Source` folder, no licence terms.

**Do any of OUR mods reference it?** Soft references only, nothing that needs it:
- `src/RimUtinni/ResearchRetag/Patches/RUT_ResearchTabAssign.xml` and `RUT_ResearchRetag.xml` move its eight research projects (`CGT_TearGasProduction`, `CGT_N2OGasProduction`, `CGT_MustardGasProduction`, `CGT_HalothaneGasProduction`, `CGT_VXGasProduction` to the Refinery tab; `CGT_WeaponizedGasIEDs` and the shells project to Powder and Slug) and set techLevels. They are conditional-xpath patches, so with the mod absent they match nothing. No `PatchOperationFindMod` names it.
- `src/RimUtinni/PawnFlavor/Patches/PawnFlavorPhase2_ThoughtDef.xml` rewrites the `CGT_N2OGiggles` thought's label and text ("gas-happy"), again conditional, and `src/RimUtinni/PawnFlavor/About/About.xml` lists `Greg.CustomGasTypes` in `loadAfter` (line 30), not in a dependency.
- `src/RimUtinni/ResearchRetag/validation.py` mentions `CGT_*` in a comment only.
- Nothing in EK, FlowWorks or the other tiers references it. Nothing on our lists depends on it. If it is removed, those RimUtinni patches go quiet and the PawnFlavor load-after is ignored.
