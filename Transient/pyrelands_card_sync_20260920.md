# Pyrelands card-vs-shipped sync — 2026-09-20

## TOPOLOGY

There are **two independent Pyrelands biome implementations**, and the one
actually painted on the frozen Ash'karr world is not the one carrying most of
the card's content.

1. **`RM_FE_Pyrelands`** — a real, self-contained `BiomeDef` at
   `src/RimMandrake/Pyrelands/Defs/BiomeDefs/Pyrelands.xml` (mod
   `mandrake.rm.pyrelands`, `src/RimMandrake/Pyrelands/`). Placed
   algorithmically by its own `workerClass`
   (`RimMandrake.StarWars.FireEcology.BiomeWorker_Pyrelands`, scoring tile
   temp/rainfall) — i.e. it is a **worldgen-time** biome. Ships its own full
   fire-ecology kit: EmberGrass+Quickgrass, AshFall/Cinderfall/BlackRain
   weather, the ash-terrain ladder, Firebreak/ScorchableGround, scorched-ruins
   genstep. Per its own About.xml: "places itself on an ordinary generated
   world with no other mod required."
2. **`ZBiome_Grasslands`** — the More Vanilla Biomes donor def. This is what
   is **actually painted onto all 63 of the authored Ash'karr "Pyrelands"
   tiles** (confirmed live: `world/ASHKARR_WORLDMAP_tiles.csv`, region=
   "Pyrelands" rows all carry `biome=ZBiome_Grasslands`; zero rows anywhere
   in the 21,872-row file carry `RM_FE_Pyrelands`). `AshStorms_Pyrelands.xml`
   says explicitly: "the authored map stamps ... Pyrelands tiles itself, so
   nothing depends on the generator being allowed to roll the biome" — i.e.
   this is deliberate: Ash'karr is a frozen, hand-painted world (no
   worldgen), so `RM_FE_Pyrelands`'s algorithmic worker structurally can
   never fire on it.

A third mod, **`src/RimUtinni/PyrelandsMechanics`** (`mandrake.rut.
pyrelandsmechanics`, closed item `PYRELANDS_MECHANICS_1`), ships the
behavioral C# layer (burn-line, igniters, flame harvest, fire raid, fire
rite) and is correctly biome-aware of the split: `PyrelandsTuning.
PyrelandsBiomeDefNames = { "ZBiome_Grasslands", "RM_FE_Pyrelands" }`
(CONFIRMED, `src/RimUtinni/PyrelandsMechanics/Source/PyrelandsTuning.cs`).

A fourth mod, **`src/RimUtinni/UtinniPatches`**, wires roster/weather/flora
content onto the two biomes — but **inconsistently**: fauna
(`WildAnimals_Pyrelands.xml`) targets `RM_FE_Pyrelands` only; flora
(`BiomeFlora_Ashkarr.xml`) and weather (`AshStorms_Pyrelands.xml`) target
`ZBiome_Grasslands` only. See DRIFT below.

All four mods (`mandrake.rm.pyrelands`, `mandrake.rut.pyrelandsmechanics`,
`mandrake.rut.patches`) are active in the current full campaign list
(`infrastructure/state/modlists/ModsConfig_full_plus_longhunger_2026-09-19.xml`,
621 active mods) — CONFIRMED. (The live `ModsConfig.xml` on disk right now is
a minimal 11-mod test list — not representative, not used for this check.)

Fauna itself: `RUT_FireHawk`/`RUT_FurnaceBeast` (the two commissioned
igniters) and `RUT_Emberscythe` live in
`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/`
(`RUT_PyrelandsFauna.xml`, `RUT_Emberscythe.xml`); the four donor-ported
predators (Sytheclaw/Barbslinger/FireWasp/Flamefang) live in
`RUT_PyrelandsPortedFauna.xml` — all four mod folders confirmed to have real
`About/About.xml` + real Defs, not stub folders.

## VERDICT

**Not in sync — badly, in the direction the card would call alarming.** The
biome the player actually visits (`ZBiome_Grasslands`, painted on Ash'karr)
is missing almost everything the card treats as load-bearing: no EmberGrass
fuel bed, no BlackRain/AshFall/Cinderfall, no ash-terrain ladder from
mapgen, no ruled igniter/predator fauna, and it still carries the donor's
ordinary rain and snow — a direct Hard-Ban-2 violation. Everything the card
describes DOES exist and IS correctly built, but almost entirely on
`RM_FE_Pyrelands`, a biome def that structurally cannot appear on the frozen,
no-worldgen Ash'karr world. The one part that got the split right is the
**behavioral C# layer** (`PyrelandsMechanics`), which is biome-aware of both
defNames and should still fire its scripted/incident systems (fire clock,
Tribes fire rite, flame harvest, fire raid) on the real map — but several of
those mechanics depend on wild igniter animals that never spawn there.

## DRIFT (worst first)

1. **Fauna roster** — card: fire-hawks and furnace-beasts as the biome's two
   "irreplaceable igniters," plus fire-followers/burrowers/ash-grazers
   (Sytheclaw, Barbslinger, Emberscythe, FireWasp, Flamefang, SW-canon herd).
   Ships: the full 14-species ruled roster is real and correctly weighted,
   but `WildAnimals_Pyrelands.xml` patches it **only onto
   `RM_FE_Pyrelands`'s `wildAnimals`** node. `ZBiome_Grasslands`'s
   `wildAnimals` (the biome on the real map) still carries the **donor's**
   bare `Iriaz`/`Gizka`/`Nuna`/`Orray`/`Zeer` (only de-duplicated, never
   replaced with `RUT_`/`RSW_` casts — see `AnimalBiomeDuplicates_Fix.xml`,
   `ZZZ_BiomeWildAnimalDuplicates_Generated.xml`). **None of
   RUT_FireHawk/RUT_FurnaceBeast/RUT_Sytheclaw/RUT_Barbslinger/RUT_FireWasp/
   RUT_Flamefang/RUT_Emberscythe wild-spawn on the shipped Pyrelands.**
   CONFIRMED (direct read of the two patch files + the live CSV).
2. **Weather table, Hard Ban 2** — card: "No ordinary rain in the weather
   table — Clear, dry thunderstorms, and BlackRain" (a 🔴 hard ban). Ships:
   `RM_FE_Pyrelands` complies (Clear/DryThunderstorm/AshFall/Cinderfall/
   BlackRain, no Rain/Snow) but is unreachable. `ZBiome_Grasslands` (the real
   biome) keeps its **donor table intact** — `AshStorms_Pyrelands.xml`'s own
   comment cites the loaded 1.6 table as "Clear 18 · SnowGentle 4 · SnowHard
   4 · DryThunderstorm 2 · RainyThunderstorm 2 · Rain 1.5 · Fog 1 · GrayPall 1
   · FoggyRain 0.5 · Windy 0.5 · Overcast 0.5 · TorrentialRain 0.5" — and only
   adds a cosmetic `AB_VolcanicAsh` reskinned "ash storm" at commonality 3 on
   top. **The shipped Pyrelands has ordinary rain and snow.** None of
   BlackRain/AshFall/Cinderfall are wired onto it at all. CONFIRMED
   (`AshStorms_Pyrelands.xml` read directly, PatchOperationAdd only).
3. **Flora / the fuel bed** — card: the grass is the whole mechanism (§3,
   §5: "the burn exists somewhere ... always"; §6 ban 3: "no fire-immune
   flora blanket, the grass burns by design"). `RM_FE_Pyrelands`'s own doc
   comment: "RM_FE_Plant_EmberGrass dominates on purpose: it IS the fuel
   bed... a fire ecology with a thin fuel bed is just a desert." Ships:
   `BiomeFlora_Ashkarr.xml` replaces `ZBiome_Grasslands`'s `wildPlants` with
   **`RM_FE_Plant_Quickgrass` alone (4.0)** — no `RM_FE_Plant_EmberGrass` at
   all. **The actual fuel-bed plant the fire loop is built around does not
   grow on the shipped Pyrelands.** CONFIRMED (direct read,
   `BiomeFlora_Ashkarr.xml:104-114`).
4. **Terrain / ash ladder at mapgen** — card §6 ban 3 / §1 ("what is left
   behind is ash... banking up through four deepening layers"). `RM_FE_
   Pyrelands` ships `terrainsByFertility`/`terrainPatchMakers` seeding old
   burn scars (Trace/Light/Heavy ash) and custom sand/gravel terrain at
   mapgen. No patch onto `ZBiome_Grasslands`'s terrain fields was found in
   any UtinniPatches file. **The shipped Pyrelands mapgen has no
   pre-existing ash scars and uses vanilla-donor ground terrain, not the ash
   ladder.** CONFIRMED for mapgen-time seeding; UNCERTAIN whether the
   in-play burn→ash terrain conversion (triggered by fire, presumably a
   Harmony hook in `FireEcologyHook.cs` watching burning cells generally)
   still functions on a `ZBiome_Grasslands` map regardless of biome — not
   read closely enough to rule either way.
5. **Mechanics (behavioral layer)** — card's "Owed" list (burn-line,
   fire-hawk twig-carry, furnace-beast thermal circuit, flame harvest/fire
   raid, weather table). Ships: all seven numbered mechanisms in
   `PyrelandsMechanics`'s own About.xml map onto real C# (`MapComponent_
   BurnLine.cs`, `CompFireHawkSpread.cs` + `JobDriver/JobGiver_RUT_
   FireHawkCarryEmber.cs`, `CompFurnaceThermalCharge/WarmthAura/
   BedIgnition.cs`, `IncidentWorker_FlameHarvest.cs`, `IncidentWorker_
   FireRaid.cs`, `LordJob_RUT_FireRite.cs`/`PyrelandsFireRite.cs`,
   `PyrelandsFireFront.cs`). This layer correctly checks **both**
   `ZBiome_Grasslands` and `RM_FE_Pyrelands` (`PyrelandsTuning.
   PyrelandsBiomeDefNames`), so the scripted/incident systems (fire clock,
   Tribes fire rite, flame harvest, fire raid, burn re-seeding) should still
   run on the real map. **But** two of the card's "four igniters" (fire-hawks,
   furnace-beasts) are wild-animal-driven, and per row 1 those animals never
   spawn on the real biome — so the igniter mechanic's natural triggers are
   effectively cut to two of four (lightning + deliberate Tribes hands) on
   the shipped map, even though the code itself is sound. CONFIRMED the code
   exists and is biome-aware; UNCERTAIN how much of the igniter behavior is
   actually observable in play given row 1.
6. **Roster/mechanics item status** — card's own "(to file)" note on
   `PYRELANDS_MECHANICS_1` is stale — it is CLOSED, and the mechanics really
   were built (see row 5). This is a card line that is stale because the
   work is DONE (see below), not a drift against shipped content.

## Card lines that are stale because the work is DONE

- §"Owed", bullet 1 (`PYRELANDS_MECHANICS_1` "(to file)") — filed and
  CLOSED; the burn-line, igniter, flame-harvest/fire-raid systems described
  are built in `src/RimUtinni/PyrelandsMechanics`.
- §"Owed", bullet 2 ("Roster — rides the full assignment pass") — the roster
  assignment pass happened (`the_pyrelands.json`, `WildAnimals_Pyrelands.xml`
  ROSTER AND VERIFICATION block) — done as *authoring*, though not reaching
  the real biome (see DRIFT row 1).
- §"Owed", bullet 3 ("FireEcology deploy collision... verify before this
  biome's kit ships") — the kit shipped under distinct mod names
  (`mandrake.rm.pyrelands`, `mandrake.rut.pyrelandsmechanics`); no evidence
  of a live folder-name collision found in this pass.

## UNKNOWN

- Whether the "genetic-tech theme line into the Rakata spec" and "Sun-Debt
  reconciliation into faction_religions.md §4" owed items (§"Owed", bullet 4,
  "Canon sitting") ever landed — out of scope for this pass (prior ground
  truth already says the Sun-Debt/genetic-tech canon never landed in
  `faction_religions.md` or the Rakata spec; not re-verified here).
- Whether the in-play ash-terrain conversion (fire burns ground → ash rungs)
  fires independent of `BiomeDef.terrainsByFertility`, i.e. whether row 4's
  drift is mapgen-only or also blocks the live burn-to-ash gameplay loop on
  `ZBiome_Grasslands` maps. Would need a read of `FireEcologyHook.cs`'s
  Harmony patches, not done here (token budget).
- Whether `RUT_Emberscythe`'s cross-reference to "ZBiome_Grasslands GR_
  Mantistanis row" (its own file header) means it was ALSO once cast
  directly on `ZBiome_Grasslands` before being rehomed — not traced further.
- Card's "Never true" bans 1 (no permanent settlement in the burn's path) and
  4 (scorch-fruit spoilage) not checked against shipped content this pass —
  outside the four bounded axes as settlement/faction placement, and ban 4
  (spoilage) is a `ThingDef` `CompRottable` property on `ScorchFruit.xml`,
  not compared here.
