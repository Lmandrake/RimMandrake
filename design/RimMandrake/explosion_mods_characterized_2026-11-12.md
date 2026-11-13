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
- **Not measured.** No decompiler was run. Anything only a live blast can show is marked UNMEASURED.

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
  - Expected visual only; UNMEASURED live.
- **Code versus art.** 0% code, 100% art: 11 PNG plus an Assets.zip, all **donor art**.
- **Licence.** UNMEASURED (none found). Absorbing means drawing our own recolour.
- **Absorb job.** About 1 to 1.5 agent-days [guess ~60%], almost all of it art.
- **Collision risk if kept.** Low. No Harmony. It rewrites the same DamageDef nodes our patch adds to, and the dump shows they coexist.
- **Recommendation.** Drop it from the list. It recolours what #1 already dresses up, and it is all donor art.

### 3. Dynamic Effects Forge

- packageId `blues.forge`, workshop 3735443951, author Blues.
- **What it changes.** "Overrides vanilla explosions with multi-stage volumetric particle sequences."
  - Its DLL (BluesForge.dll, 92 KB, no source) names `Explosion.StartExplosion` as a string and carries both Prefix and Postfix. That fits a Harmony patch on the explosion start, set up by reflection.
  - Its BlastMatchDefs map Bomb, BombSuper, Flame, Smoke, Extinguish, Stun and EMP to its own effects.
  - It also adds a humidifier building and patches `Proj_Foam`, `Filth_FireFoam`, `ElectricalSpark` and the chemshine barrel.
- **What our knockback does with it today.**
  - UNMEASURED whether its Prefix skips or alters the vanilla explosion start (radius, damage, cells). If it does, it changes what reaches our `ExplosionDamageThing` hook, and so what we throw.
  - UNMEASURED: how it looks beside #1, which dresses the same blasts.
- **Code versus art.** About 25% code, 75% art: 51 PNG plus an Assets.zip, all **donor art**.
- **Licence.** UNMEASURED (none found).
- **Absorb job.** About 3 to 5 agent-days [guess ~35%]: volumetric multi-stage effects and their art.
- **Collision risk if kept.** Medium. Its prefix sits upstream of our hook in the same explosion, and its code is closed.
- **Recommendation.** Drop it from the list. It overlaps #1, its closed prefix could change our throws, and its art is donor art.

### 4. Custom Gas Types

- packageId `Greg.CustomGasTypes`, workshop 3756399441, author Legator.
- **What it changes.**
  - Gas shells with their own `CGT_*GasRelease` DamageDefs (harmsHealth false), which release gas from explosions through a DamageDef extension.
  - Its DLL names `ExplosionAffectCell`: a DamageWorker override, or a patch of it.
- **What our knockback does with it today.** Its damage types do not harm health and carry no EK extension, so they throw nothing, the same as vanilla ToxGas. UNMEASURED live.
- **Code versus art.** About 70% code (1445 lines of source ship with it), 30% art: 36 PNG, donor art.
- **Licence.** UNMEASURED.
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
