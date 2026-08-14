# Jawa Ion Weapons (local) — mini-mod

Industrial-tier Jawa ion armament for this run. All *behavior* is our own pure-XML defs (vanilla-EMP based, no C# assembly of our own). **Depends on Outer Rim - Core** (`Neronix17.OuterRim.Core`) for the fired bolt sprite (`BlasterBolt_Blue`) and blaster fire sound (`OuterRim_Shot_DLT19DBlasterBolt`) — Core is already in the local stack, and it transitively pulls Vanilla Expanded Framework + Tabula Rasa. The gun's own sprite is bundled here (ripped from the EOL Tatooine mod).

Design locked 2026-08-08 (see `design/Jawa/mods/required_mods.md` §"JAWA ION WEAPONRY" — the Claude memory note `jawa_ion_weapon.md` it also cited has since been deleted).

## What it is

One signature weapon — the **Jawa Ion Blaster** — plus its own ion damage type and a custom "ion buildup" stun hediff.

Design pillars honored:
- **Capture-not-kill:** ion damage is `harmsHealth=false / makesBlood=false`. It cannot injure or kill a flesh target; it disables.
- **Tiered by target (the "differing levels" the user asked for):** this rides the vanilla EMP stun-resistance gradient. Mechanoids/droids are EMP-stunned hard and fast. Flesh pawns resist per-hit stun, so they must be *worn down* by accumulating `JawaIon_Stun` severity until their Consciousness is pinned below the downed threshold — they collapse **alive and unharmed**, ready to arrest.
- **Weak but cunning, terrain-rewarding:** low damage (8), slow warmup (1.9s), long cooldown (2.6s), modest range (22), steep accuracy falloff (0.80 touch → 0.22 long). You win by ganging up, using cover/chokes, kiting, and *stacking* buildup — not by out-shooting anyone. (Cross-checked against Outer Rim Core's ion suite, which runs warmup 1.2 / range 24–42; ours is deliberately slower and shorter.)
- **Industrial, buildable from start:** `techLevel Industrial`, cheap scrap cost (45 steel + 3 industrial components), built at a vanilla machining table or fabrication bench. Honors the "Jawa start industrial" pillar — NOT the spacer `HypertechFabrication` gate Core uses.

## Files (the 5 build artifacts)

| # | Artifact | File | defName |
|---|----------|------|---------|
| 1 | Weapon ThingDef | `Defs/ThingDefs_JawaIonBlaster.xml` | `JawaIon_Blaster` |
| 2 | Stun hediff (also the CPERS stun→down fix) | `Defs/HediffDefs_JawaIonStun.xml` | `JawaIon_Stun` |
| 3 | Ion damage + projectile | `Defs/DamageDefs_JawaIon.xml` + weapon file | `JawaIon_Damage`, `JawaIon_Bullet` |
| 4 | Industrial research unlock | `Defs/ResearchProjectDefs_JawaIon.xml` | `JawaIon_Weaponry` |
| 5 | Scenario starting kit | *see below — set in scenario, not a Def here* | — |

The build recipe auto-generates from the weapon's `<recipeMaker>` (vanilla); no separate recipe def needed.

## Artifact 5 — starting kit

Two ways to spawn 2–4 blasters in the Jawa starting inventory:

**(a) In-game scenario editor (simplest):** Scenario → *Edit mode* → "Start with" → add `JawaIon_Blaster` ×3.

**(b) In a custom ScenarioDef**, add a ScenPart:
```xml
<li Class="ScenPart_StartingThing_Defined">
  <def>StartingThing_Defined</def>
  <thingDef>JawaIon_Blaster</thingDef>
  <count>3</count>
</li>
```
To make them **buildable from literal turn 1** without researching, also either pre-complete `JawaIon_Weaponry` in the scenario, or delete the `<researchPrerequisite>` line from the weapon's `recipeMaker`.

## ⚠️ Must verify in-game (not yet playtested)

Everything is XML-well-formed, but two behaviors need a live check because they depend on runtime resolution:
1. **Buildup accrual on flesh.** The `additionalHediffs` block on `JawaIon_Damage` should apply `JawaIon_Stun` on every hit regardless of target flesh/mech. Confirm a healthy raider actually accumulates severity and collapses (downed, not dead) after ~4 hits, and that the collapse reads as arrestable. If `additionalHediffs` does not fire for the EMP-family damage on flesh, fall back to a `CompProperties` on the projectile or a small custom `DamageWorker` (would add C#).
2. **`setMax` on Consciousness downs the pawn.** Confirm the top "overloaded" stage (`setMax 0.10`) actually forces a down state and that decay (-1.2/day) then revives them if left alone (so captures require prompt arrest).

Tune knobs if needed: `severityPerDamageDealt` (0.03) and the stage `minSeverity` thresholds control how many hits it takes; `severityPerDay` (-1.2) controls how fast buildup fades.

## Art

`Textures/JawaIon/Weapon_JawaIonBlaster.png` is a **placeholder path** — supply real art from the graphics-review pass (Outer Rim Core's `IonBlaster`/`IonRifle`/`HeavyIonRifle` are the reference silhouettes; their PNGs were stripped from `mod_sources` and are being re-fetched). Projectile currently reuses a tinted vanilla `Bullet_Big`.
