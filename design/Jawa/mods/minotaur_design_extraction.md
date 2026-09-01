<!-- status: RETIRE — design reference extracted from Roo's Minotaur Xenotype before its removal (owner ruling 2026-08-31). Not Star Wars canon; keep only the mechanism, not the mod. Removal from ModsConfig.xml follows once this doc is committed. -->
# Roo's Minotaur Xenotype — mechanisms extracted before retirement

Owner's ruling, 2026-08-31: RETIRE + extract design — not Star Wars canon,
but its mechanisms are worth capturing for reuse in SW-canon creatures.
Source: `tug.Minotaur` ("Roo's Minotaur Xenotype", by Tug, orig. by Rooboid
and Zelan), workshop id `3548423129`,
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3548423129`.
Hard `modDependencies`: `brrainz.harmony` + `Ludeon.RimWorld.Biotech`. Real C#
assembly `Assemblies/RBM_Minotaur_Mod.dll` — **not** pure XML like `titans.fl`.

## The Herculean gene — verified stat package (`RBM_Herculean`)

| field | value |
|---|---|
| `statFactors.MeleeDamageFactor` | **1.3** (+30% melee damage) |
| `statFactors.ArrestSuccessChance` | **1.5** (+50% arrest chance) |
| `statFactors.MeatAmount` / `LeatherAmount` | 1.5 / 1.5 |
| `statOffsets.MeleeDodgeChance` | **-15** (the "easier to hit" tradeoff — the wielder's own dodge stat, not an attacker buff) |
| `statOffsets.CarryingCapacity` | +25 |
| `biostatCpx` / `biostatMet` | 2 / -2 |
| `geneClass` | `RBM_Minotaur.Gene_RBM_Herculean` (custom, see below) |

All four prompt-cited numbers verified exactly. Also carries a
`VEF.Genes.GeneExtension` (VFE Core) `sizeByAge`: +0.3 body-size offset by
age 18 — carriers are visibly larger, not just statistically stronger.
**Fully XML-portable.**

## Weapon-gene gating — a tag/class convention, not a stat field

No vanilla "requires this gene" field exists on `ThingDef`. The mechanism: a
dedicated `WeaponClassDef` (`RBM_HerculeanClass`, same kind as vanilla
`Melee`/`Ranged`); an abstract parent (`HerculeanBase`) every Herculean-only
weapon inherits (`weaponTags: HerculeanWeapon`, `techLevel: Archotech`,
`tradeTags: HerculeanFabled`, `relicChance: 0.5`, `recipeMaker IsNull` —
found-only); each weapon adds `RBM_HerculeanClass` into its own
`weaponClasses` **alongside** the normal one. Enforcement — refusing
non-Herculean pawns the equip — is **invisible in XML**; it must live in the
custom `geneClass` (`Gene_RBM_Herculean`) via Harmony, almost certainly
checking `weaponClasses.Contains(RBM_HerculeanClass)` against the pawn's
genes. **NOT portable without that C# check** — the tag/class scaffolding
itself is trivial XML.

## See Red — the actual interesting ability (`RBM_SeeRed`, gene `RBM_BovineTemper`)

One button press: `cooldownTicksRange` 60000 (1 day), `warmupTime` 1.5s,
`Ability_EffectRadius` 4.5, gives the caster `HeDiffSeeRed` (`onlyApplyToSelf`)
and — via custom comp `RBM_Minotaur.CompProperties_AbilityTerrify` — scares
everyone else in the radius. `HeDiffSeeRed` starts at `initialSeverity 1`,
decays at `severityPerDay -2.5` (~9.6 real-time hours), and its stages run
**top to bottom as it decays** — the pawn starts buffed and crashes:

| stage (severity) | effect |
|---|---|
| intense (≥0.88, start) | `MeleeHitChance +15`, `PainShockThreshold +2` (near pain-immune), `IncomingDamageFactor -0.5` (**half damage taken**), `StaggerDurationFactor -0.5`, Moving/Manipulation +0.7/+1, forces `Berserk` (`mtbDays 0` — attacks anyone, friend or foe) |
| diminishing (0.82–0.88) | smaller Moving/Manipulation bonus, combat buffs already gone |
| exhausted (0.76–0.82) | Moving/Manipulation **-0.10** each |
| aftermath (<0.76) | `Consciousness` capped at **0.1** — the crash |

Nearby pawns get `HeDiffTerrified` (200-tick `RBM_TerrifiedFlee` forced-flee),
self-clearing once the caster's rage passes peak. **A burst risk/reward
berserker, not a raw damage buff**: guaranteed friendly-fire aggression + an
AOE fear pulse + massive temporary tankiness, paid for by a forced
near-unconscious crash. Portable as `AbilityDef` + 3 `HediffDef`s + 1
`MentalStateDef`, except the fear-pulse comp (custom C#).

## Bovine gene set — occupies vanilla xenotype slots, doesn't invent new ones

| gene | vanilla `ParentName` (slot claimed) | what it adds |
|---|---|---|
| `RBM_BovineEars` | `GeneEarsBase` | ear render nodes only |
| `RBM_BovineHorns` | `GeneHeadboneBase` | horn render nodes |
| `RBM_BovineHead` | `GeneJawBase` | forces 12 vanilla head shapes + bull/cow face markings |
| `RBM_EarthySkin` | `GeneSkinColorOverride` | fixed skin tone |
| `RBM_BovineVoice` | `GeneVoiceBase` | custom call/death/wounded sounds |
| `RBM_UnguligradeLegs` | none (Misc) | `MoveSpeed +0.10`, `FilthRate +3`, `MeleeDodgeChance +10` |
| `RBM_RuminantStomach` | none (Misc) | `dontMindRawFood`, `RawNutritionFactor ×1.5`, `MaxNutrition ×2`, eats hay |
| `RBM_EstrousCycle` | none (Reproduction) | custom `geneClass` — seasonal breeding-drive logic |

**Pattern worth reusing**: cosmetic genes parent off vanilla slot bases (no
collision with other xenotypes); functional genes are plain unparented genes
adding stat packages. `XenotypeDef RBM_Minotaur`: `combatPowerFactor 1.4`,
`inheritable true`, 17 genes total.

## PawnKindDef combatPower spread — verified

| defName | role | `combatPower` |
|---|---|---|
| `RBM_MinotaurGuardianHigh` | ancient elite guard, Herculean-tagged fabled weapons | **120** |
| `RBM_MinotaurGuardianLow` | ancient bodyguard, ordinary weapon tags | **80** |
| `RBM_MinotaurMarauder` | pirate variant | **65** |
| `RBM_MinotaurFighter` ("fleshfighter") | outlander mercenary | **60** |
| `RBM_MinotaurFeral` | tribal savage | **50** |
| `RBM_ProtectedMonarch` | the non-minotaur xeno the guardians protect | **20** |

Matches the prompt's 120/80/65/60/50/20 exactly. The *weapon-tier gate*
(`weaponTags: HerculeanWeapon` only on the 120-power kind) does as much of
the differentiation as the `combatPower` number itself — same body, same
gene, priced by what it's allowed to carry.

## Reusable XML-only trick: body-part hediffs from a melee weapon

`Tunbell`'s `extraMeleeDamages` (custom `Mageia_Sound`) triggers `BruiseSound`
(invisible `InjuryBase`, `disappearsAfterTicks 10`) whose sole job is
`HediffGiver_Random` targeting `Ear` parts, attaching `Ringing` — worsening
via `severityPerDay 200` into permanent `HearingLoss` unless tended. Why:
melee weapons can only target the part they're aimed at, not an unrelated
one — a disposable middleman hediff is the workaround. Fully XML-portable.

## What NOT to copy

The Herculean **enforcement** C# — reuse the gating *pattern*, not the DLL.
Flavor-only gimmicks with no mechanical weight: Midaspear's gold-corpse
(`MidasTouch`), milking/lactation, achievement/backstory/namer content —
lore, not mechanism. `sizeByAge` is a nice-to-have, not load-bearing.

## Status

Extraction complete. Per the owner's ruling, `tug.Minotaur` retires from the
active mod list once this doc is committed — `ModsConfig.xml` removal follows.
