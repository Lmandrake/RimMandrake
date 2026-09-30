# LOAD_ERRORS_FAUNA_FLORA_1 — fix report

Cold load 2026-09-30, source: `Transient/load_errors_2026-09-30.txt`. Scope: our mods
only (src/RimMandrake, src/RimStarWars, src/RimUtinni), three Config-error classes:
tool linkedBodyPartsGroup mismatches, Nutrition==0/preferability mismatches, animal
trainability=null. NOT touching: Def Error XML field errors, unresolved cross-refs,
duplicate keys, missing textures (owned by a parallel agent).

## Class 1: tool linkedBodyPartsGroup mismatches (28 defs fixed)

Read the real BodyDef groups from vanilla `Data/Core/Defs/Bodies/*.xml` (Bird,
BeetleLike, BeetleLikeWithClaw, TurtleLike, QuadrupedAnimalWithPawsAndTail,
QuadrupedAnimalWithClawsTailAndJowl, QuadrupedAnimalWithHoovesAndHump, Monkey) and
our own `RSW_Orray` BodyDef, then repointed each broken tool at a group that body
actually has, keeping the tool's bite/claw/kick intent:

- Bird bodies only have `HeadAttackTool`/`Beak`/`Feet` (no Teeth, no per-side
  paw groups — left+right claws both land on `Feet`, matching vanilla Bird's own
  single-group-per-limb-type shape): RM_Grimewing, RM_Sparkleech, RM_Vrisk,
  RM_Nizzek (in RM_Drazzik.xml), RSW_Nizzek — Teeth→Beak; RM_Blisterfloat,
  RM_Gorekite, RM_Skinflap, RM_Nizzek, RSW_Nizzek — FrontLeft/RightPaw→Feet.
- BeetleLike/BeetleLikeWithClaw only have `HeadAttackTool`/`Mouth`(+`HeadClaw` on
  the WithClaw variant): RM_Ollathrix, RM_Quarrok, RM_Vennick, RM_Gristleswarm,
  RM_SootGristleswarm, RM_Krannock, RM_Kurreth, RM_KurrethQueen — Teeth→Mouth;
  RM_Gripper — FrontLeftPaw→HeadClaw (only claw-bearing group on that body).
- TurtleLike only has `HeadAttackTool`/`TurtleBeakAttackTool` (matches vanilla
  Tortoise exactly): RM_Cravvet, RM_Gravelgut, RM_Smolderback, RM_Scaldhide —
  Teeth→TurtleBeakAttackTool; RM_Scorchpod — FrontLeftPaw→HeadAttackTool (no
  claw/paw group exists on a turtle body at all, same fallback vanilla Tortoise
  uses for its non-beak attack).
- QuadrupedAnimalWithClawsTailAndJowl uses `FrontLeftClaws`/`FrontRightClaws`,
  not `FrontLeftPaw`/`FrontRightPaw`: RM_Slagmole, RM_Bloodlurk, RM_Eyestinger.
- QuadrupedAnimalWithPawsAndTail uses `FrontLeftPaw`/`FrontRightPaw`, not
  `FrontLeftLeg`/`FrontRightLeg`: RUT_Radiothermal.
- QuadrupedAnimalWithHoovesAndHump uses `FrontLeftLeg`/`FrontRightLeg`, not
  paws (no claw group at all): RM_Shambles — FrontLeftPaw→FrontLeftLeg.
- Monkey has `LeftHand`/`RightHand` (its `Teeth` group is real — RM_Tarruq's
  bite tool was already correct and untouched): RM_Tarruq —
  FrontLeftPaw→LeftHand, FrontRightPaw→RightHand.
- RSW_Orray's own custom BodyDef has `HeadAttackTool`/`FrontLeftPaw`/
  `FrontRightPaw` and no Teeth group at all: bite tool Teeth→HeadAttackTool
  (its claw tools were already correctly on FrontLeft/RightPaw).

Left untouched (not config errors, already valid): RM_Eyestinger's tail-stinger
tool (`Tail` group — not flagged by the game, so out of scope even though vanilla
core defines no such BodyPartGroupDef; likely supplied by another active mod),
RM_Tarruq's/RSW_Orray's bite tools on `Teeth` (Monkey body genuinely has Teeth).
RUT_Ashwallow's `FrontLeftFoot`/`FrontRightFoot` tool groups were NOT touched —
those are the separate "unresolved cross-reference" class (the group doesn't
exist anywhere, vanilla or ours, vs. "body doesn't have this group"), owned by
the parallel agent.

## Class 2: Nutrition==0 / preferability mismatches (51 defs fixed + 5 food items given real Nutrition)

All 51 flagged plants are `ParentName="PlantBase"` with no `<ingestible>`
override of their own — PlantBase = PlantBaseNonEdible + `<ingestible>
<foodType>Plant</foodType><preferability>RawBad</preferability></ingestible>`
(confirmed against `Data/Core/Defs/ThingDefs_Plants/Plants_Bases.xml`), and none
of them set a nutrition value, so they inherit RawBad with Nutrition 0. Rather
than adding a `<ingestible><preferability>NeverForNutrition</preferability>
</ingestible>` override, I followed this project's own already-proven idiom
(`src/RimMandrake/EnvironmentalHazards/Defs/ThingDefs_Plants/RM_Venomvine.xml`,
MEASURED live 2026-09-21, same error, same fix): reparent from `PlantBase` to
`PlantBaseNonEdible` directly. This drops the whole ingestible block (matching
vanilla's own idiom for "nothing eats this") and is a strict subset of what
PlantBase adds, so nothing else about the plant changes.

Fixed (51): RM_Kollavane, RM_Vessark, RM_Tavrosk, RM_Dulloth, RM_Brimlock,
RM_Threllick, RM_Sellith, RM_Varrisk, RM_Kessaroth, RM_Norrveth, RM_Sorrivel,
RM_Pellareth, RM_Ruddreth, RM_Fellome, RM_Grennick, RM_Brennoth, RM_Scumgrass,
RM_TallScumgrass, RM_Cinderfelt, RM_FloatstoneGarden, RM_VauliskLure,
RM_Thulvane, RM_Skethral, RM_Varnoth, RM_Plennith, RM_Ossagrel, RM_Cistrel,
RM_Maulith, RM_Verrow, RM_Nubrith, RM_Halquin, RM_Ammeth, RM_Claithe,
RM_Corvath, RM_Sodderel, RM_Seepril, RM_Skimmel, RM_Wanlith, RM_Tullick,
RM_Meatvine, RM_Toothmoss, RM_Wombpod, RM_Eyebark, RM_Lashgrass, RM_Bleedleaf,
RM_Gorestalk, RM_Rattlegrope, RM_Sapblister, RM_BloodyFist, RM_HalfmadeTree,
RM_HalfmadeTreeBlighted.

**Finding for the parallel agent (XML field error class): a real bug, not
touched here.** 5 of the Config-error defs — RM_TavroskLiquor,
RM_ThornbugNectar, RM_DrommathSap, RM_DrommathBurstSap, RM_OssagrelSap — are
genuinely meant to be food (sap/nectar/liquor resource items with an authored
`<ingestible><preferability>DesperateOnly</preferability><nutrition>0.05</
nutrition></ingestible>` block) but their Nutrition reads 0 at runtime because
`<nutrition>` (and `<nutritionInterval>`, seen on RM_PitchpearlBeads/
RM_StonewaterIce, which have their own separate `Def Error` but are NOT in the
Nutrition==0 Config-error list) **is not a real field on `IngestibleProperties`
in 1.6** — confirmed against vanilla (`PlantFoodRawBase` in
`Data/Core/Defs/ThingDefs_Items/Items_Resource_RawPlant.xml` sets nutrition via
`<statBases><Nutrition>0.05</Nutrition></statBases>`, a STAT, not an ingestible
field). Per this item's brief ("if it is meant to be food, give it real
Nutrition instead"), I added the correct `<Nutrition>` stat entry (0.05 for
RM_TavroskLiquor/RM_ThornbugNectar/RM_OssagrelSap, 0.04 for
RM_DrommathSap/RM_DrommathBurstSap) to each def's `<statBases>`, WITHOUT
touching the invalid `<ingestible><nutrition>` line itself — that line, and the
matching one on RM_PitchpearlBeads/RM_StonewaterIce, is the parallel agent's
XML-field-error class to remove.

## Class 3: animal trainability = null (4 defs fixed)

Valid 1.6 `TrainabilityDef`s are `None`/`Intermediate`/`Advanced` (`Data/Core/
Defs/Misc/TrainabilityDefs/TrainabilityDefs.xml`) — `Simple` and `Minimal` do
not exist, which is also the log's separate "No Verse.TrainabilityDef named
Simple" cross-reference. Set to `None` on all four (matches this project's own
established convention — see the comment already in RM_CauldronFauna.xml citing
a MEASURED confirmation that `Pawn_TrainingTracker.CanAssignToTrain` doesn't
even read trainability, "which is how vanilla's own trainability:None animals
(turkeys) are tameable" — and matches vanilla's own pattern for placid grazers/
livestock: Cow/Pig/Goat/Sheep/Yak/Boomalope/Horse/Muffalo are all `None` despite
being herd/pack animals):

- RM_Zisska (`RM_CauldronFauna.xml`): `Simple`→`None`
- RM_Eskith (`RM_CauldronFauna.xml`): `Simple`→`None`
- RM_Julmox (`RM_TheForgeNatives.xml`): `Simple`→`None`
- RUT_Ashwallow (`RUT_Ashwallow.xml`): `Minimal`→`None`

Swept the whole tree for any other `<trainability>Simple</trainability>` or
`<trainability>Minimal</trainability>` afterward — none remain. RUT_Ashwallow's
own `FrontLeftFoot`/`FrontRightFoot` tool-group cross-reference errors were left
alone (parallel agent's class).

## Verification

- All 27 touched XML files parse clean (`xml.etree.ElementTree`).
- Wrote an offline checker (`verify_bodygroups.py`) that builds each BodyDef's
  real group set (recursively, from `<groups><li>` — vanilla `Data/*/Defs/
  Bodies/*.xml` plus every `<BodyDef>` under our own `src/`) and checks every
  `<tools><li><linkedBodyPartsGroup>` in every `RM_`/`RSW_`/`RUT_` creature
  ThingDef with a `<race><body>` against it. 459 of our creature defs checked;
  **0 remaining mismatches** among resolvable bodies. The only body name it
  couldn't resolve is `Rat` — that body genuinely doesn't exist anywhere
  (vanilla or ours), matching the log's separate "Could not resolve
  cross-reference: No Verse.BodyDef named Rat" entry (parallel agent's class,
  not a group mismatch on an existing body).
- `run_selftests.py`: **78/79 passed, 0 failed**, 1 UNMEASURED
  (`selftest_tool_metadata.py` — no local C# build artifact present, expected
  per CLAUDE.md's toolchain note, not a failure), 2 SKIPPED (human-driven /
  needs a separate venv, both by design). `selftest_deployed_biome_refs`
  (flagged in the task brief as a known pre-existing failure) PASSED clean in
  this run (476.2s).

## Not touched (parallel agent's classes, confirmed out of scope)

- Def Error XML field errors (e.g. `<drawStyleCategory>`, `<wildness>`,
  `<soundCall>`, `<coverEffectiveness>`, `<lethal>`, `<nutrition>`/
  `<nutritionInterval>` inside `<ingestible>`, `<letterLabel>`/
  `<displayOrder>` on GameConditionDef, `<checkIntervalTicks>` on a
  `CompProperties`, `<butcherProducts>` on RaceProperties, `<ingredients>`/
  `<fixedIngredientFilter>`/`<products>` on RecipeMakerProperties,
  `<specialTrainables>` on PawnKindDef).
- Unresolved cross-references (missing SoundDefs, BodyPartGroupDefs that don't
  exist anywhere, missing ThingDef/PawnKindDef references, the `Rat` BodyDef,
  the `Simple`/`Minimal` TrainabilityDef references themselves — I fixed our
  side, the source of the dangling reference, not the cross-ref mechanism).
- Duplicate keys, missing textures.
