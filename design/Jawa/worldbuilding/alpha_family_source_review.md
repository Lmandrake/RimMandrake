# Alpha-family source review — mechanics catalog and generalization proposals

Filed against `ALPHA_FAMILY_SOURCE_REVIEW_1`. Read `README_BIOME_GRAMMAR.md` first
for how this doc's sheet references work. Nothing here has been ruled by the owner —
every generalization proposal below is a CARD, not a decision.

## 1. Inventory — which Alpha mods are in our stack (MEASURED)

Read directly from the live `ModsConfig.xml`
(`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`),
2026-09-08:

- **`sarg.alphabiomes` (Alpha Biomes) — ACTIVE.**
- **Alpha Animals (`sarg.alphaanimals`, source repo `AlphaAnimals`) — NOT in the active
  list.** No packageId for it, under any casing, appears in `<activeMods>`.
- No other Alpha-family mod (Alpha Genes, Alpha Memes, Alpha Mechs, Alpha Incidents,
  etc.) is active either.

⚠️ **Caveat on this measurement**: the live `ModsConfig.xml` at read time held only
**25** active mods (`brrainz.harmony`, the four DLCs, `oskarpotocki.vanillafactionsexpanded.core`,
`brrainz.rimbridgeserver`, `7f.alienworlds(.tidallylocked)`, `sarg.alphabiomes`,
`oblitus.mylittleplanet`, `mandrake.rm.inhabited`, `neronix17.toolbox`,
`Neronix17.OuterRim.Core`, `erdelf.HumanoidAlienRaces`, `mandrake.rsw.ionweapons`,
`mandrake.rsw.droidworks`, `mandrake.rm.fluidcanals`, `mandrake.rut.shipmemory`,
`mandrake.rut.vaultdungeons`, `rw.mod.simplestairs`, `Kutte.Stairs`,
`mlie.decorativecliffs`) — a reduced/test list, not the ~599-mod full stack the
2026-09-08 commit log references. Per `CLAUDE.md`, `ModsConfig.xml` describes only the
**next load**, and per the memory note it can be stale relative to the owner's actual
full list. **This is what the file said when read; it is not proof Alpha Animals is
absent from the full/played list** — only that it is absent from whatever list is
queued next. If the full-stack membership of Alpha Animals matters for a ruling, it
needs re-measuring against the 599-mod capture, not this file.

Regardless of live/inactive status, this review treats **both** `AlphaBiomes` and
`AlphaAnimals` (the repo behind the in-game "Alpha Animals" mod; its C# assembly and
namespace are actually `AlphaBehavioursAndEvents`) as in scope, per the work item's
explicit instruction to study both repos.

## 2. License findings

**Both repos ship no LICENSE file and GitHub's own license detector returns `license:
null` for both** (checked via `gh api repos/juanosarg/AlphaBiomes` and
`repos/juanosarg/AlphaAnimals`, and by listing each repo's root tree — no
`LICENSE`/`LICENSE.md`/`COPYING` file exists in either). About.xml carries no
license field either (RimWorld's schema has none).

**Verbatim conclusion: there is no license grant of any kind.** Under default
copyright (US and most jurisdictions), publishing source on GitHub does **not**
itself grant permission to copy, modify, or redistribute the code — "all rights
reserved" is the default absent an explicit license. GitHub's own Terms of Service
(§D.5, "License Grant to Other Users") only guarantees other users may **view and
fork** the repository on GitHub itself; it explicitly does **not** grant rights to
"use, copy, modify, merge, publish, distribute... or sell copies" — those require an
express license, which is absent here.

**What this means for us, on top of our existing precedent** (borrowing design and
def-identities — biome names, creature concepts, mechanic ideas — is already our
practice; shipping the donor's actual code or art files is already banned
regardless of license):

- **Shipped C# is banned, full stop — and the absence of a license makes this
  stricter than our usual "don't ship it" norm, not looser.** We may not copy any
  `.cs` file, or a substantially verbatim translation of one, into `src/`. This
  applies even though the mod's own About.xml requires Harmony/VEF and freely
  patches base-game methods — that says nothing about our right to reuse Sarg's code.
- **Independent reimplementation of the underlying mechanic (the pattern: "a Gas
  subclass that ticks and damages nearby pawns," "a GameCondition that offsets
  temperature," "a Harmony postfix that multiplies `GenCelestial.CurCelestialSunGlow`")
  is not copyright-restricted** — these are unprotectable ideas/systems, not
  expression, and RimWorld's own `Verse`/`RimWorld` base classes are what do most of
  the real work in every file below. Writing our own comp from scratch, in our own
  words, that reaches a similar player-facing effect is safe. This review's mechanics
  table and generalization proposals lean on that distinction throughout: every
  proposed comp is a fresh implementation against RimWorld's public API, described
  by function, never a port.
- **This is a CARD, not a ruling** — if the owner wants a second opinion (e.g. on
  whether a near-identical class shape, like "a `ThingComp` that increments a
  counter and spawns gas in a radius," counts as expression rather than idea), that
  needs his call before any of the L-effort ports below are built.

## 3. Mechanics catalog — comp/worker · effect · target sheet · replication effort

Read directly from `github.com/juanosarg/AlphaBiomes` and `github.com/juanosarg/AlphaAnimals`
(default branch `master`, both repos), 38 `.cs` files fetched and read in full via the
GitHub contents API (file-listing sweep of both `1.6/Source/` trees, then a curated
read of the files matching the spec's named examples plus every other comp/worker
touching a base-game-can't mechanic). This is not every `.cs` file in either repo
(AlphaBiomes alone has ~100; AlphaAnimals ~120) — it is a representative cut across
gas/terrain/hediff/ability/death-action/pawn-class/game-condition categories, enough
to catalog every *kind* of mechanic these mods use, not every instance of it.

Sheet mappings below come from a keyword grep across `design/Jawa/worldbuilding/biomes/*.md`
(spore/mushroom/fog/gas/acid/vent/quicksand/tar/radiation/mutation/ocular/eye/swallow/
crush/siege/detonate/nocturnal/dark/gangrene/toxic), not a full read of every sheet —
treat "which sheet wants it" as a first-pass candidate list for the owner's biome
conversation, not a committed assignment.

| Comp/worker (repo, file) | What it actually does | Candidate sheet(s) | Replicate effort |
|---|---|---|---|
| `Gas_Mycotic` (AlphaBiomes, `Gas and Filth/Gas_Mycotic.cs`) | `Gas` subclass; every 120 ticks, damages every non-immune pawn standing in the gas cell (1 cut dmg + 0.05 ToxicBuildup) and deals 50 dmg to any plant not on an immunity list. Pure tick-and-scan, no pathing. | `the_rot.md` (Sporefields region), `the_fever_wood.md` (Sporefall) | **S** |
| `TileMutatorWorker_AgariluxPrime` (AlphaBiomes, `TileMutatorWorkers/Flora/`) | `TileMutatorWorker.GeneratePostFog`: finds a clear, unfogged rect via `MapGenUtility`, flattens terrain to Soil, and one-shot spawns a `PrefabDef` (a pre-built structure/plant cluster) there, tracking used rects so mutators don't overlap. This is worldgen placement, not a runtime comp. | `the_rot.md` | **S** (the placement pattern is generic; the prefab itself is content) |
| `CompGasProducer` (AlphaBiomes, `Comps/CompGasProducer.cs`) | Generic `ThingComp`: every `gasTickMax` (512) ticks, if powered (optionally gated on `CompPowerTrader`), spawns a `Thing` named by `Props.gasType` in a random subset of cells within `Props.radius` at `Props.rate` probability. **This is already the generic "active gas-emitter" comp** — the one Alpha Biomes actually reuses across multiple gas types via `CompProperties_GasProducer` fields. | `the_rot.md`, `the_fever_wood.md`, `the_miasma.md`, `poison_forest.md`, `terminator_sea.md` | **S** — closest thing in either repo to an already-generic comp; a straight reimplementation is nearly free |
| `Building_MagmaVent` + `MagmaSprayer` (AlphaBiomes, `Buildings/`, `Building Effects/`) | Building with a periodic "spray" cycle: on trigger, lays temporary `LavaShallow` terrain in a radius (auto-reverting after 6000 ticks via `tempTerrain.QueueRemoveTerrain`), plays a sustainer sound, and lays snow-melt radially. A geyser that **temporarily reshapes terrain**, not just particles. | `the_forge.md` (vents, tremors, lava), `the_sump.md` (tar-pit adjacency) | **M** |
| `CompAncientBloodRainVent` / `CompAncientGreyPallVent` / `CompAncientFreezingVent` / `CompAncientDeathPallVent` (AlphaBiomes, `Comps/Ancient Vents/`) | All four are near-identical `CompAncientVent` subclasses whose only override toggles a `CompFleckEmitterLongTerm` on/off — i.e. a **named, ambient, on/off visual-effect emitter driven by a base class** (`CompAncientVent`, not shown but clearly a shared toggle/duration framework) tied to a `TileMutatorWorker_AncientVent` on the world layer. The real mechanic lives in the un-fetched `CompAncientVent` base — worth a follow-up read before replicating. | `the_forge.md`, `the_scarlands.md`, `deep_desert.md` (radiation) | **S** (visual toggle) / **M** if the base class's duration-cycle logic is wanted too |
| `GameCondition_AmbientRadiation` (AlphaBiomes, `GameConditions/`) | Every 900,000 ticks (~15 days), picks one random free colonist and **force-adds a random base-creation-eligible `GeneDef`** (excluding animal-summary and modded exclusions), then letters the player. A slow, narrative mutation-by-radiation mechanic — genuinely something the base game can't do (no vanilla system randomly grants a gene). | `deep_desert.md` (merciless radiation), `the_scarlands.md` (all-toxic) | **S** |
| `GameCondition_GelatinousMemoryEcho` (AlphaBiomes, `GameConditions/`) | Every 120,000 ticks, rolls psychically-sensitive colonists through a 3-way branch: free inspiration, a good/bad thought (`AB_GelatinousEchoes_Good/Bad`), or a forced mental break (`DarkVisions` if Anomaly is active, else `Wander_Sad`). A **psychic-ambient-hazard game condition**, structurally identical to vanilla's Psychic Drone but home-rolled. | `the_slime.md` | **S** |
| `BiomeWorker_GelatinousSuperorganism` (AlphaBiomes, `BiomeWorkers/`) | `BiomeWorker.GetScore` — not a runtime mechanic, but worth noting the technique: it lazily attaches a `WorldComponentExtender` to `Find.World` and scores tiles against a cached Perlin "weirdness" noise field rather than climate stats. **Non-climate biome placement is a real, reusable worldgen pattern** (though world layer work is explicitly out of scope per `README_BIOME_GRAMMAR.md`/CLAUDE.md's no-worldgen ruling — noted for completeness, not proposed). | n/a (worldgen, out of scope) | n/a |
| `StatPart_QuiveringSurface` / `StatPart_SymbioticNutrients` (AlphaBiomes, `StatParts/`) | Both: flat multiplier (`0.8`/`0.9`) on a stat, gated by `pawn.Map.TileInfo.Mutators.Contains(<mutator>)` — i.e. **a StatPart that only applies while standing on a specific `TileMutatorDef`**. Generic pattern: any stat, any tile mutator, any multiplier. | `the_slime.md` | **S** |
| `HediffComp_GangreneWounds` (AlphaBiomes, `Hediff Comps/`) | On a `HediffWithComps`, ticks a counter; past a severity threshold, rolls a chance (per two severity "stages," each with its own MTB/chance/threshold) to deal bonus finger/toe damage from a custom `DamageDef`. A **staged, severity-gated self-damage hediff**. | `the_slime.md`, `the_rot.md` | **S** |
| `ThoughtWorker_MoldyEnvironment` (AlphaBiomes, `ThoughtWorkers/`) | Extends `ThoughtWorker_GameCondition`; active only while the pawn is also standing somewhere that "uses outdoor temperature" (i.e. actually exposed, not just under the condition's map). A **condition + exposure gate combined**, avoiding vanilla's "active anywhere on the map" default. | `the_rot.md` | **S** |
| `GameCondition_AcidRain` (AlphaBiomes, `Weathers and Conditions/`) | Full custom weather-condition: forces `weatherManager.curWeather` to a custom `AB_AcidRainWeather` def on both `Init` and every 300-tick recheck (fighting vanilla's own weather rotation), deals scaled `ToxicBuildup` to every unroofed pawn every 10,000 ticks (species-gated: flesh + flammable only, with an Alpha-Animals-specific alt damage def), rots unroofed items faster, kills a fraction of toxic-vulnerable plants per tick, and zeroes animal/plant spawn density for the duration. **This is the fullest "environmental attack weather" example in the catalog** — pawn damage, plant/item decay, spawn suppression and forced weather-lock all in one condition. | `the_sump.md`, `the_scald.md` ("fouled, not toxic" — a near-miss worth flagging to the owner), `poison_forest.md` | **M** |
| `TileMutatorWorker_TarLakes` (AlphaBiomes, `TileMutatorWorkers/Ponds/`) | Subclasses vanilla's `TileMutatorWorker_Lake`; overrides `ProcessCell` to paint `AB_Tar`/`AB_TarMud` instead of water/mud, keyed off the same noise-threshold plumbing vanilla lakes already use. **Cheapest possible "hazard terrain that reuses vanilla lake-gen"** pattern. | `the_sump.md` (tar pits) | **S** |
| `TileMutatorWorker_QuicksandPits` (AlphaBiomes, `TileMutatorWorkers/Ponds/`) | Builds its own Perlin/falloff/displacement noise stack (Odyssey-gated) to flatten elevation and paint a custom `AB_Quicksand` terrain (with a `SoftSand` transition ring) independent of vanilla lake-gen. Heavier than TarLakes but still worldgen-only — no runtime "sinking" mechanic was found in this file (that would live in the terrain def's `TerrainAffordance`/movement fields or a companion comp not fetched). | `the_webwork.md` (movementDifficulty already noted in its donor inventory) | **M** (the noise-authoring part; the actual "quicksand sinks you" runtime behavior needs a further read of the terrain def / a possible unread comp) |
| `GameCondition_ExtremeTemperatureFluctuations` (AlphaBiomes) | Every 6000 ticks, samples day/night via `GenCelestial.IsDaytime`; `TemperatureOffset()` returns ±17°C lerped in/out by the condition's transition window. A **day/night-keyed temperature-swing condition**, generic over the swing amount. | `the_pyrelands.md`, `deep_desert.md` | **S** |
| `GameCondition_VolcanicHeatWave` (AlphaBiomes) | Simpler sibling: flat +30°C offset, disables outdoor joy. | `the_forge.md`, `the_pyrelands.md` | **S** |
| `GameCondition_ExplodingAnimals` (AlphaBiomes) | Every 6000 ticks, force-adds an `AB_Exploder` hediff to every animal on the map that doesn't already have it (the hediff itself — not shown — presumably carries a death-explosion comp). A **condition that arms a population-wide latent hazard** rather than doing the damage itself. | `the_forge.md` | **S** (the condition) / needs the `AB_Exploder` hediff def read to size the hediff side |
| **The "Forsaken fog / darkness" mechanic** — `AlphaBiomes_GenCelestial_CurCelestialSunGlow_Patch` (Harmony postfix, `Harmony/GenCelestial_CurCelestialSunGlow.cs`) + `AlphaBiomes_ConditionalStatAffecter_InSunlight_Applies_Patch` (`Harmony/ConditionalStatAffecter_InSunlight_Applies.cs`) | **Not a GameCondition or weather def at all.** A Harmony postfix multiplies `GenCelestial.CurCelestialSunGlow(map)` by `0.34` whenever `map.Biome == AB_RockyCrags` — this alone darkens the whole biome permanently (cached per-map in a `Dictionary<Map,bool>`), and vanilla's existing darkness→accuracy/mood/plant-growth chain does the rest for free. A second postfix on `ConditionalStatAffecter_InSunlight.Applies` forces sunlight-gated stat bonuses (e.g. vampire weaknesses) to read as "false" on that biome specifically. **The "accuracy in darkness" effect the spec named is not a bespoke comp — it's vanilla's own systems, unlocked by patching one glow-multiplier method.** | `the_lantern_deeps.md` (darkness as a real mechanic v1 — direct hit), `the_miasma.md` ("out of darkness") | **S** — this is the cheapest mechanic in the whole catalog to replicate: one Harmony postfix, biome-gated, no new Def type needed |
| `Ability_OcularEruption` / `Ability_DestroyEyes` (AlphaAnimals, `Abilities/Oculist/`) | Two `VEF.Abilities.Ability` subclasses. Eruption: adds 4–7 `AA_MalevolentEye` hediffs to random body parts on the target. DestroyEyes: finds every `BodyPartDefOf.Eye` part and one-shots it with 1000 armor-piercing burn damage, propagation disabled. A **targeted multi-part hediff-affliction ability pair** — inflict N of something, or destroy every part matching a BodyPartDef. | `the_contagion.md` (Ocular Forest donor content incorporated wholesale — direct hit) | **S** each |
| `Gas_Ocular` (AlphaAnimals, `Gases/Gas_Ocular.cs`) | `Gas` subclass; every 64 ticks, **transmutes** any tree/grass plant standing in the gas cell into an "alien" variant (species-immunity list per plant type, weighted random pick among 3 grass variants), preserving `Growth`. A gas that **rewrites terrain flora identity**, not damage. | `the_contagion.md` | **M** (transmutation-on-tick is a new pattern vs. the damage-only gases above) |
| `Gas_Frost` (AlphaAnimals, `Gases/Gas_Frost.cs`) | Same tick-and-scan shape as `Gas_Mycotic`, damages non-immune pawns with `DamageDefOf.Frostbite` every 128 ticks. Confirms the "damage-gas" shape is the repos' default template — three near-identical implementations (Mycotic, Frost, this) argue strongly for one generic comp. | `poison_forest.md`, `terminator_sea.md` (cold gas vents — direct hit), `nightside_ice.md` | **S** |
| `Hediff_Crushing` (AlphaAnimals, `Hediffs/Hediff_Crushing.cs`) | A `HediffWithComps` that, while active and the pawn is awake/spawned, every 30 ticks deals falloff-by-distance damage (`GenMath.LerpDouble`, 1.0→0.2 across radius 0–4.2) to every Thing in a 3-tile radius via a custom `DamageDef` (category-weighted: pawns most vulnerable when animal/downed-reduced, items ~3%, buildings 80%, plants 170%), respecting thick-roof/natural-rock immunity, plus periodic filth (`Filth_RubbleRock`) generation and a looping sustainer sound. **This is the "environmental-attack terrain/aura" mechanic the spec explicitly asked for** — an active area-damage field carried by the afflicted pawn rather than a building. | Any sheet wanting a "walking hazard" creature (candidates: `the_forge.md`, `fall_line.md` — "debris strike is an ambient hazard") | **M** |
| `Hediff_OverpoweringAcidBuildup` (AlphaAnimals) | Every 64 ticks, deals 1 dmg via a custom acid-burn `DamageDef` unless the pawn carries a specific `CompAcidImmunity` (from VEF's AnimalBehaviours module — a dependency, not ours to reuse). A **periodic self-damage hediff with an immunity-comp escape hatch**. | `the_slime.md`, `the_rust_cathedral.md` (flagged "no true acid terrain" — a near-miss to raise with the owner, not silently apply) | **S** |
| `Hediff_Stalking` (AlphaAnimals) | Records the pawn's hediff count on `PostAdd`; every 20 ticks, if the count has grown (i.e. *any* new hediff was added — a camouflage-break proxy), force-dirties the renderer and removes itself. A **"camouflage breaks on any new condition" hediff**, reusable for a stealth-predator concept. | none matched by grep — a genuinely new idea for the owner's stealth-predator conversations | **S** |
| `MentalState_PhotosensitiveExoskeleton` (AlphaAnimals, `MentalStates/`) | A `MentalState` that only ends once the pawn has gone `def.minTicksBeforeRecovery` ticks **without** seeing sunlight (checked every 30 ticks against a companion `ThoughtWorker`). A **sunlight-avoidance forced mental state**, the mirror image of the Forsaken-fog darkness patch above. | `the_lantern_deeps.md`, nocturnal-creature candidates generally | **S** |
| `JobGiver_Mine` (AlphaAnimals, `Jobs/JobGiver_Mine.cs`) | `ThinkNode_JobGiver` that scans 40 random cells in the pawn's region for an adjacent impassable 1x1 edifice (excluding `CollapsedRocks`) and issues a designation-ignoring `Mine` job. **This is the "burrowing creature" mechanic named in the spec** — it is literally "an animal that mines through rock like a miner pawn," not a movement-through-solid-matter trick. | Any sheet with a burrower concept (none matched cleanly by grep; a fresh idea to raise) | **S** |
| `DeathActionWorker_AcidExplosion` / `_GargantuanExplosion` / `_FrostbiteExplosion` (AlphaAnimals, `DeathActionWorkers/`) | Three near-identical `DeathActionWorker` subclasses: life-stage-scaled explosion radius (juvenile/adult/elder tiers) on death, each with a different `DamageDef` + explosion fleck/sound set (acid spit + goo pop + slime filth; plain flame; frostbite + ice-crash + frost-puff). **Confirms "scaled death explosion" is a single generic pattern with three content skins**, not three mechanics. | `the_forge.md` (`GameCondition_ExplodingAnimals` pairs with this exact worker), `nightside_ice.md` (frostbite variant) | **S** (one comp, def-driven radius/damage/fleck set) |
| `DamageWorker_Siege` (AlphaAnimals, `ExplosionsAndDamage/`) | `DamageWorker_AddInjury` override: against natural rock or `Wall` specifically, deals `dinfo.Amount * 8` raw HP damage (bypassing normal armor/injury math) instead of the usual roll. **The "terrain/wall attack" mechanic the spec named** — a creature or ability that is disproportionately effective at breaching built structures. | `the_forge.md`, `the_rust_cathedral.md` | **S** |
| `DamageWorker_SwallowWhole` + `Pawn_SwallowWhole` (AlphaAnimals, `ExplosionsAndDamage/`, `PawnClasses/`) | A custom `Pawn` subclass carrying a `ThingOwner<Thing>` "stomach" (`IThingHolder`), fed via a `DamageWorker_Cut` override that downs and swallows the victim outright once bite damage lands (species-immunity check), then a `TickRare`-driven digestion timer that kills+rots swallowed pawns and ejects the container on a schedule; ejects/destroys contents safely on the swallower's own death. **The most structurally complex mechanic in the catalog** — genuinely something base-game `Pawn` cannot do (hold another live Thing inside itself as a mechanic, not cosmetic). | No sheet matched by grep (a "big predator" concept, not yet on a sheet) | **L** |
| `Pawn_Detonator` (AlphaAnimals, `PawnClasses/Pawn_Detonator.cs`) | Adds a player-triggerable `Command_Action` gizmo that force-adds/escalates an `AA_Kamikaze` hediff (presumably carrying its own death-explosion comp, not fetched) — i.e. a **player-commandable self-destruct** on a pawn class, distinct from the death-action-on-natural-death workers above. | `the_forge.md` (detonator-creature candidate) | **S** (the gizmo/hediff-trigger shape; the actual explosion payload rides one of the DeathActionWorkers above) |
| `Pawn_GrowOnCombat` (AlphaAnimals, `PawnClasses/Pawn_GrowOnCombat.cs`) | Every 100 ticks, if the pawn is awake and mid-melee-attack and doesn't already carry a "grown"/"exhausted" hediff, adds a growth hediff to its body-core part. A **combat-triggered transformation pawn class** (berserker/enrage-growth archetype). | none matched by grep | **S** |
| `Ability_SpawnOnRadius` / `Ability_Summon` (AlphaAnimals, `Abilities/Generic/`) | Both are `VEF.Abilities.Ability` subclasses driven entirely by DefExtension fields (`thingToSpawn`/`probability`/population-cap; `pawnToSpawn`/`numberCreated`/faction/enrage-on-spawn) — **fully generic "spawn N things/pawns on cast, population-capped" abilities**, no per-creature code at all. This is the cleanest "already generalized, just port the pattern" example in the whole catalog. | `the_contagion.md` (swarm/summon concepts), general hive/nest creature candidates | **S** |

## 4. Generalized comp proposals (tier grammar, CARDS not rulings)

Per `design/NAMING_SCHEME_PLAN.md`, a mechanic with **no Star Wars or Utinni
specificity** — these are engine-level patterns (a gas that ticks and damages, a
GameCondition that offsets temperature, a Harmony postfix on a glow multiplier) —
belongs at the **`RM_` tier** (`RimMandrake.<ModName>`, "any RimWorld game"), not
`RSW_`/`RUT_`. The work item asks for `RSW_`/`RUT_` output specifically; the
resolution proposed here is: **build the mechanism once at `RM_` tier, then expose
it to each biome sheet through `RSW_`/`RUT_` content defs** (a `ThingDef`,
`HediffDef`, or `GameConditionDef` per sheet) that reference the generic
`CompProperties`/base class by field values only. That keeps exactly one C#
implementation per mechanic while every sheet gets its own tuned instance — the same
shape Alpha Biomes itself uses internally (one `CompGasProducer` class, many
`CompProperties_GasProducer` instances).

Proposed new mod: `src/RimMandrake/EnvironmentalHazards/` (packageId
`mandrake.rm.environmentalhazards`), namespace `RimMandrake.EnvironmentalHazards`.

1. **`RM_CompActiveGasEmitter`** (generalizes `CompGasProducer` / the `Gas_Mycotic`,
   `Gas_Frost`, `Gas_Ocular` family) — a `ThingComp` with `CompProperties` fields for
   `gasType` (any `ThingDef` of category Gas), `radius`, `rate`, `tickInterval`,
   optional power-gate. The gas Thing itself is a second small class,
   `RM_Gas_Damaging` (fields: `damageDef`, `damageAmount`, `hediffToApply`,
   `hediffSeverityPerTick`, `plantDamageAmount`, an immunity `defName` list) — one
   class replaces Mycotic/Frost's damage-gas duplication. A **third** variant,
   `RM_Gas_Transmuting` (fields: `treeReplacement`, weighted `otherReplacements`
   list, immunity list), covers `Gas_Ocular`'s flora-rewrite behavior as a sibling
   rather than a fork. Feeds `the_rot.md`, `the_fever_wood.md`, `poison_forest.md`,
   `terminator_sea.md`, `nightside_ice.md`, `the_contagion.md`. **Effort: S**, three
   small classes sharing one tick pattern.
2. **`RM_HediffComp_PeriodicAreaAttack`** (generalizes `Hediff_Crushing`) — a
   `HediffComp` (not a bespoke `Hediff` subclass, so it stacks onto any existing
   hediff via XML) with fields for `radius`, `tickInterval`, `damageDef`,
   `damageFalloffCurve`, per-`ThingCategory` damage multipliers, roof/rock immunity
   toggle, optional filth spawn chance + `ThingDef`, optional sustainer `SoundDef`.
   This is the spec's named "active-defender plant" and "terrain attack" comp in one
   — a plant, a building, or a creature can all carry it. Feeds any sheet wanting a
   stationary or slow-moving area hazard (Rot's guardian mushrooms, a Contagion
   aberration, the Lantern's guardian). **Effort: M** (falloff curve + category
   multiplier table is the only real new work over `Hediff_Crushing`'s hardcoded
   version).
3. **`RM_HarmonyPatch_BiomeGlowMultiplier`** (generalizes the Forsaken-fog Harmony
   pair) — one Harmony postfix on `GenCelestial.CurCelestialSunGlow`, driven by a
   `Dictionary<BiomeDef, float>` built at startup from a `DefModExtension` on each
   `BiomeDef` (`RM_BiomeGlowMultiplierExtension { multiplier }`) rather than a
   hardcoded biome check — so every dark-biome sheet (`the_lantern_deeps.md`,
   `the_miasma.md`) gets its own tuned darkness without a new patch per biome. Ride
   the same technique to also patch `ConditionalStatAffecter_InSunlight.Applies` if
   any Ash'karr xenotype needs a sun-sensitivity exception. **Effort: S** — this is
   the single cheapest, highest-leverage item in the whole catalog: one patch, one
   DefModExtension, reused by every dark sheet forever.
4. **`RM_GameCondition_EnvironmentalWeather`** (generalizes `GameCondition_AcidRain`)
   — a data-driven weather-lock condition: forces a specified `WeatherDef` for the
   duration, deals a specified `DamageDef` to unroofed pawns on an interval (species
   category gate: flesh/mechanical/both), optional item-rot acceleration, optional
   plant-kill chance, optional animal/plant density suppression. One class replaces
   Acid Rain, and by extension covers Ambient Radiation's and Volcanic Heat Wave's
   simpler subsets as config presets rather than new classes where the effect is
   "temperature offset only" (fold `GameCondition_ExtremeTemperatureFluctuations`
   and `GameCondition_VolcanicHeatWave`'s day/night and flat offsets in as two more
   fields: `dayOffset`/`nightOffset` vs. a flat `tempOffset`). Feeds `the_sump.md`,
   `poison_forest.md`, `the_forge.md`, `the_pyrelands.md`, `deep_desert.md`.
   **Effort: M**.
5. **`RM_CompProperties_ScaledDeathExplosion`** (generalizes the three
   `DeathActionWorker_*Explosion` classes) — one `DeathActionWorker` reading
   life-stage-scaled radius (three floats), `damageDef`, optional weapon `ThingDef`
   for the flash, optional filth `ThingDef`, from its `CompProperties`, instead of
   three hardcoded subclasses. Pairs naturally with a generic
   `RM_GameCondition_ArmLatentHazard` (generalizing `GameCondition_ExplodingAnimals`
   — "add hediff X to every animal on the map periodically," data-driven on the
   hediff def) for the Forge's exploding-fauna concept. **Effort: S** for both.
6. **`RM_Ability_TargetedHediffAffliction`** (generalizes `Ability_OcularEruption`
   and the `HediffCompProperties_ExplodeOnDowned`-style single-part variant
   implied by `Ability_DestroyEyes`) — one ability class, DefExtension-driven:
   either "add N of hediff X to random body parts" or "destroy every part matching
   BodyPartDef Y with damage Z." Feeds `the_contagion.md` directly (Ocular Forest is
   explicitly donor content already incorporated — this generalizes the mechanism
   behind it rather than the content). **Effort: S.**

Two items are **not** worth a generic comp on their own merits, but are worth
flagging as already-cheap-to-reimplement content patterns rather than mechanics:
`Ability_SpawnOnRadius`/`Ability_Summon` are already fully data-driven in the donor
(no generalization work needed beyond writing our own class against the same VEF
`Ability` base — **S**), and `JobGiver_Mine` (burrowing) is a ~30-line
`ThinkNode_JobGiver` with no generalization surface worth adding — write it directly
per creature that needs it.

**Deliberately not proposed as generic comps**: `Pawn_SwallowWhole` (L effort, no
sheet currently wants it — worth a card to the owner as a "big predator" concept
before spending the build) and the Ancient Vent family (needs the un-fetched
`CompAncientVent` base class read before its duration-cycle logic can be
generalized — flagged as an open follow-up, not blocking this review).

## 5. Broadening beyond the donor's intent (feeding sheet Owed lists)

- **`RM_HarmonyPatch_BiomeGlowMultiplier`** broadens trivially beyond "one dark
  biome": Ash'karr could use it for *partial* darkness too (a 0.6–0.8 multiplier
  reads as "permanent overcast," not full night) — useful for `the_grey_deep.md`'s
  "grey-green murk" and `the_twilight_deep.md` without needing either to be a true
  darkness biome.
- **`RM_Gas_Transmuting`** (from `Gas_Ocular`) generalizes past "turns plants alien"
  into a slow, gas-driven terrain-corruption tool usable anywhere the owner wants a
  visible, spreading "this ground is being changed" effect — a candidate for
  `the_greentide.md`'s spread mechanic or `the_cracked_lands.md`'s pooling toxins,
  beyond the single donor use.
- **`RM_HediffComp_PeriodicAreaAttack`** on a *plant* rather than a creature is the
  literal "active-defender plant" the spec asked for — broaden past Hediff_Crushing's
  walking-hazard use into a stationary guardian flora for the Rot's mushrooms, with
  the radius/falloff tuned down to a "don't stand next to this" rather than a
  battlefield hazard.
- **`RM_GameCondition_EnvironmentalWeather`**'s spawn-density-suppression field is
  worth broadening into a *positive* density modifier too (some biomes should get
  MORE spawns during their signature weather, not fewer) — a one-field addition, not
  a new class, but flagged because none of the donor's own conditions use it that
  direction.
- **`DamageWorker_Siege`**'s "bonus damage to built structures" idea broadens past a
  creature ability into an environmental hazard property (a terrain tile or weather
  condition that erodes walls over time) for `the_forge.md`'s tremor concept —
  distinct from any creature carrying it.

## 6. What could NOT be completed, and why

- **Spec bullet 5 ("the owner has ruled which mechanics we replicate")**: not
  completed — this document is the review that precedes that ruling, not the ruling
  itself. Every generalization above is a card. `verify` in the item spec says "the
  owner has ruled" as a condition of the item being DONE; this file alone does not
  close it.
- **The `CompAncientVent` base class** (shared by all four Ancient Vent comps) was
  not fetched or read — the four subclasses read only toggle a fleck emitter, but
  the actual on/off-cycle timing, duration, and any pawn-facing effects live in the
  unread base. Flagged in §4 rather than guessed at.
- **The `AB_Exploder` and `AA_Kamikaze` hediff defs** (referenced by
  `GameCondition_ExplodingAnimals` and `Pawn_Detonator` respectively) were not
  fetched — these are XML defs, not `.cs` files, and the spec's scope was the C#
  mechanics; their existence and shape is inferred from the comps that reference
  them, not confirmed by reading them.
- **Alpha Animals' full ~120-file `.cs` tree and Alpha Biomes' full ~100-file tree**
  were not read exhaustively — 38 representative files were fetched and read in
  full (see §3's methodology note). This catalog is a first pass across every
  *category* of mechanic present (gas, hediff-comp, game-condition, death-action,
  pawn-class, ability, damage-worker, Harmony patch), not a complete inventory of
  every individual comp in either repo. A second pass would likely surface more
  instances of the same six patterns rather than new ones, based on how repetitive
  the sampled set already was (three near-identical damage-gases, three
  near-identical scaled-explosion workers).
- **Sheet-to-mechanic mapping (§3, §5) is a keyword-grep pass across
  `design/Jawa/worldbuilding/biomes/*.md`, not a full read of every sheet** — per
  `biomes-sheets-are-a-conversation-loop`, the owner defines sheets with BENCH one
  at a time, so committing these mappings as fact would overreach; they are offered
  as candidates for that conversation, sourced from each sheet's own donor-inventory
  language where it already exists (e.g. `the_lantern_deeps.md`'s own "darkness as a
  real mechanic v1" line, `the_slime.md`'s own "slime-in-eyes" line).
