# Jawa Ion Weapons (local) — mini-mod

Industrial-tier Jawa ion armament for this run. Mostly pure-XML defs (vanilla-EMP based), plus **one small assembly of our own** — `Assemblies/JawaIonWeapons.dll`, built from `Source/DamageWorker_IonBuildup.cs`, which is what makes the flesh half of the weapon work (see "The mechanic" below). **Depends on Outer Rim - Core** (`Neronix17.OuterRim.Core`) for the fired bolt sprite (`BlasterBolt_Blue`) and blaster fire sound (`OuterRim_Shot_DLT19DBlasterBolt`) — Core is already in the local stack, and it transitively pulls Vanilla Expanded Framework + Tabula Rasa. The gun's own sprite is bundled here (ripped from the EOL Tatooine mod).

Design locked 2026-08-08 (see `design/Jawa/mods/required_mods.md` §"JAWA ION WEAPONRY" — the Claude memory note `jawa_ion_weapon.md` it also cited has since been deleted).

## What it is

One signature weapon — the **Jawa Ion Blaster** — plus its own ion damage type and a custom "ion buildup" stun hediff.

Design pillars honored:
- **Capture-not-kill:** ion damage is `harmsHealth=false / makesBlood=false`. It cannot injure or kill a flesh target; it disables.
- **Tiered by target (the "differing levels" the user asked for):** this rides the vanilla EMP stun-resistance gradient. Mechanoids/droids are EMP-stunned hard and fast. Flesh pawns resist per-hit stun, so they must be *worn down* by accumulating `RSW_JawaIon_Stun` severity until their Consciousness is pinned below the downed threshold — they collapse **alive and unharmed**, ready to arrest.
- **Weak but cunning, terrain-rewarding:** low damage (8), slow warmup (1.9s), long cooldown (2.6s), modest range (22), steep accuracy falloff (0.80 touch → 0.22 long). You win by ganging up, using cover/chokes, kiting, and *stacking* buildup — not by out-shooting anyone. (Cross-checked against Outer Rim Core's ion suite, which runs warmup 1.2 / range 24–42; ours is deliberately slower and shorter.)
- **Industrial, buildable from start:** `techLevel Industrial`, cheap scrap cost (45 steel + 3 industrial components), built at a vanilla machining table or fabrication bench. Honors the "Jawa start industrial" pillar — NOT the spacer `HypertechFabrication` gate Core uses.

## Files (the 5 build artifacts)

| # | Artifact | File | defName |
|---|----------|------|---------|
| 1 | Weapon ThingDef | `Defs/ThingDefs_JawaIonBlaster.xml` | `RSW_JawaIon_Blaster` |
| 2 | Stun hediff (also the CPERS stun→down fix) | `Defs/HediffDefs_JawaIonStun.xml` | `RSW_JawaIon_Stun` |
| 3 | Ion damage + projectile | `Defs/DamageDefs_JawaIon.xml` + weapon file | `RSW_JawaIon_Damage`, `RSW_JawaIon_Bullet` |
| 4 | Industrial research unlock | `Defs/ResearchProjectDefs_JawaIon.xml` | `RSW_JawaIon_Weaponry` |
| 5 | Scenario starting kit | *see below — set in scenario, not a Def here* | — |

The build recipe auto-generates from the weapon's `<recipeMaker>` (vanilla); no separate recipe def needed.

## Artifact 5 — starting kit

Two ways to spawn 2–4 blasters in the Jawa starting inventory:

**(a) In-game scenario editor (simplest):** Scenario → *Edit mode* → "Start with" → add `RSW_JawaIon_Blaster` ×3.

**(b) In a custom ScenarioDef**, add a ScenPart:
```xml
<li Class="ScenPart_StartingThing_Defined">
  <def>StartingThing_Defined</def>
  <thingDef>RSW_JawaIon_Blaster</thingDef>
  <count>3</count>
</li>
```
To make them **buildable from literal turn 1** without researching, also either pre-complete `RSW_JawaIon_Weaponry` in the scenario, or delete the `<researchPrerequisite>` line from the weapon's `recipeMaker`.

## The mechanic — why this mod owns a DLL

Two XML facts, both established the hard way, force the C#:

1. **`additionalHediffs` is inert on a stun-family damage.** It is read only by
   `DamageWorker_AddInjury.ApplyDamageToPart`, and an EMP/`StunBase`-derived def never
   reaches that worker — every def in Core that uses `additionalHediffs` is an injury
   damage in `Damages_MeleeWeapon.xml`. So the buildup block never executed and the flesh
   half of the weapon had never once run in game.
2. **The obvious XML workaround breaks the design pillar.** `DamageWorker_AddInjury` with
   tiny damage does apply the buildup — and any injury can kill, which "capture-not-kill"
   forbids. There is no stock worker that applies a hediff without dealing an injury. That
   is the whole gap the assembly closes.

`JawaIonWeapons.DamageWorker_IonBuildup` is wired via `<workerClass>` on `RSW_JawaIon_Damage`.
On a hit it increments `RSW_JawaIon_Stun` by `severityPerDamageDealt × damage` (**read from the
`<additionalHediffs>` block**, so the XML stays the tuning surface), deals no injury and no
blood to flesh, and returns a real `DamageResult` so the hit reads as a hit in the combat
log. Mechanoids are left to the existing `causeStun` path — it does not reimplement EMP.

⚠️ **`StunBase` alone does nothing — do not revert the EMP fields.** Core's `StunBase`
declares only `harmsHealth=false` and `makesBlood=false`: no `workerClass` and **no
`causeStun`**. Vanilla EMP stuns because EMP itself sets `causeStun`, not by inheritance.
Inheriting the "harms nothing" half without the "does something" half made every bolt a
total no-op — no injury, no stun, no combat-log line — which was reported in play as
*"it never seems to hit, even at 20 shooting"*. `RSW_JawaIon_Damage` therefore carries
`causeStun`, `externalViolenceForMechanoids`, `stunAdaptationTicks`, `impactSoundType` and
`combatLogRules` explicitly.

**Rebuilding.** SDK is user-local at `C:\Users\Mandrake\.dotnet\dotnet.exe` (not on PATH;
`C:\Program Files\dotnet` is runtime-only and cannot build). Copy the working `net472`
setup from `src/RimMandrake/RimDefDump/Source/RimDefDump.csproj` rather than reconstructing
one — game DLLs referenced from `RimWorldWin64_Data\Managed` with `<Private>false</Private>`.
Output lands in `Assemblies/`; the game loads the deployed copy under
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\JawaIonWeapons`, never this repo.

## ⚠️ Must verify in-game

The acceptance test, in one load:
1. **Droid** — hard-stunned, drops fast (this half already worked; confirm no regression).
2. **Flesh pawn, repeated hits** — an ion buildup hediff appears in the Health tab and its
   severity climbs per hit; sustained fire reaches the top stage and the target **collapses
   downed with zero injuries listed**, and reads as arrestable.
3. **Stop firing** — severity visibly decays (`-1.2`/day) and clears, so captures require
   prompt arrest.
4. A flesh target **cannot** be killed no matter how long you fire.
5. Log clean: no `workerClass` resolution error, no NRE out of the damage worker.

Offline before spending the load: the assembly builds against net472, and `RSW_JawaIon_Damage`'s
`workerClass` string matches the **compiled** type name, not just the source.

Tune knobs if needed: `severityPerDamageDealt` (0.03) and the stage `minSeverity` thresholds control how many hits it takes; `severityPerDay` (-1.2) controls how fast buildup fades.

## Art

`Textures/JawaIon/Weapon_JawaIonBlaster.png` is a **placeholder path** — supply real art from the graphics-review pass (Outer Rim Core's `IonBlaster`/`IonRifle`/`HeavyIonRifle` are the reference silhouettes; their PNGs were stripped from `mod_sources` and are being re-fetched). Projectile currently reuses a tinted vanilla `Bullet_Big`.

**Open cosmetic todo:** the player reports the shot **sounds and looks underwhelming**.
`soundCast` is Outer Rim's `OuterRim_Shot_DLT19DBlasterBolt` at `muzzleFlashScale 7`.
XML-only, and strictly after the mechanic is confirmed working — never before.
