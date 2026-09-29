# The Forge — bedazzle review (movements 1–2), 2026-09-28

Program: `BAROQUE_BEDAZZLE_PROGRAM_1`, row 6. Reviewer: DESIGN subagent (Fable).
Both spellings swept: "TheForge"/"The Forge", prefixes `RM_Forge`/`RUT_Forge`.

## What's there

**Item:** FORGE_BEDAZZLE_SITTING_1 · **Program:** BAROQUE_BEDAZZLE_PROGRAM_1 (row 6)
**Author:** DESIGN subagent (Fable), movement 1–2 pass. Sources read this pass:
`src/RimMandrake/TheForge/` (all defs + C#), the frozen twin
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheForge.xml`, all seven Forge Utinni
patches + the FoundryFloor/Tower/Vent/Tibanna def files,
`src/RimMandrake/EnvironmentalHazards/Source/` (the whole Forge kit lives there),
`rosters/the_forge.json`, the frozen sheet `the_forge.md`
(🧊 *"FROZEN — BIOME_FREEZE_FABLE_REVIEW_1, 2026-09-07. The rulings in this sheet are
frozen: amendments add detail; they never change a ruling."*),
`FORGE_MECHANICS_1` (all four build passes), `forge_kit_spec.md`, the accent doc Batch 5c,
artpipe `registry.jsonl`/`done/`/`_artsrc/`/`pending/` + `Transient/*.decisions.json`.
No rename is ruled for this biome.

### BiomeDef(s)

Two, deliberately (twin architecture, `biome_mod_architecture.md` §5) — the sheet's
"three defs as one place" (Volcano · LavaField · AB_PyroclasticConflagration, one
massif zoned by elevation) is long since merged into the single owned def pair:

- **`RM_TheForge`** — `src/RimMandrake/TheForge/Defs/BiomeDefs/RM_TheForge_Biome.xml`,
  ships in `mandrake.rm.theforge` ("RimMandrake: The Forge"), built 2026-09-25
  (`THEFORGE_RM_MOD_BUILD_1`). animalDensity 1.2, plantDensity 0.4, own worker
  `RM_BiomeWorker_TheForge` (temp 38–65 °C, elev 1100–2400 m bands, replaces the donor
  AlphaBiomes worker), own `RM_RedFog` weather (owner ruling 2026-09-24 de-SW-ing
  RSW_SW_RedFog), `RM_ForgePulse` biomeMapCondition wired natively. Hard modDependency:
  `mandrake.rm.environmentalhazards` (the shared kit assembly).
- **`RUT_TheForge`** — the frozen campaign twin, still carrying the donor's bare
  `Beldon`/`LavaFlea` rows and `RSW_SW_RedFog`; served the live world to date.

Donor exposure in the RM def, disclosed in its own headers: 3 AB_ terrainsByFertility
bands inline unguarded, `AB_VolcanicAsh`/`AshRain` weathers (MayRequire-guarded),
donor flora rows (below), vanilla `ExtremeDesert` worldmap texture stand-in.

### Flora roster (def + patch-added, merged)

No Utinni flora patch for this biome — flora is inline on the RM def (shorthand
`<DefName>commonality</DefName>` form, parsed as such). 10 rows:

| def | comm | provenance |
|---|---|---|
| `Plant_Fireweed` | 0.9 | vanilla/Odyssey — THE signature per the frozen sheet (heat-gear fiber economy) |
| `Plant_MagmaCactus` | 0.7 | vanilla/Odyssey |
| `RM_FireLavender` | 0.6 | OURS — renamed from RUT_, glower, 50–352 °C band; art done+deployed (`FireLavender_a.png`) |
| `RM_CinderCrust` | 0.4 | OURS — Q13 divergence of shared RUT_Sagecrust (TheRot took RM_Sagecrust); **no art yet** (texPath points at nothing) |
| `IronScruff_PrimordialGrass` | 0.35 | donor |
| `AB_TinkleGrass` | 0.3 | Alpha Biomes donor |
| `IronScruff_PrimordialTallGrass` | 0.3 | donor |
| `IronScruff_Bindweed` | 0.25 | donor |
| `AB_FirevineTree` | 0.2 | Alpha Biomes donor tree |
| `RM_HeatsinkFungus` | 0.2 | OURS — renamed from RUT_, heat-drinking tree; art done+deployed |

### Fauna roster (def + patch-added, merged)

RM def inline (5 rows): `AA_Aerofleet` 0.4 (sky jelly-fleet — sheet renames it
"fumerider", still donor label) · `LavaSnail` 0.35 (Odyssey) · `AA_Metallovore` 0.15 ·
`AA_CrescendoAnole` 0.5 (pyramid-law small) · **`RM_FleetFlier` 0.45** (OURS,
from-scratch small sky darter; real core-1.6 flight stats `MaxFlightTime 15` +
`CompProperties_VaporDrifter`; **no textures in the mod yet** but art EXISTS in artpipe).

Patch-added (`UtinniPatches/Patches/WildAnimals_TheForge.xml`, one
PatchOperationConditional targeting `Defs/BiomeDef[defName="RM_TheForge"]/wildAnimals`,
species read from the op's own value): `RSW_LavaFlea` 0.25 · **`RSW_Beldon` 0.08** (the
tibanna herd — fixing the frozen twin's latent mismatch where the tap targeted RSW_Beldon
but only bare donor `Beldon` ever spawned) · `RSW_Maguana` 0.5 (magma-camouflage lizard,
ours ex-BMT).

**Campaign cast: 8 wired species. RM-standalone cast with no donors installed: 1
creature (the fleet flier) + 3 owned plants + 2 vanilla plants.** See roster gaps.

Roster-vs-wiring gap (adjudicate at the sitting, no action taken):
`rosters/the_forge.json` fauna carries `AA_ColossalAerofleet` (0.5) and `Tibidee` (0.5)
wired NOWHERE (twin comment says both were left out on purpose as LARGE during the
pyramid-law small-share fix; the roster still lists them). `Beldon` roster confidence
block: "placid" ruling vs register predator special — resolved in RSW_Beldon's port per
the roster's stat_adjustments row, worth re-confirming at the sitting.

### Terrain / weather / conditions

- Terrain: the 3 donor AB_ bands (`AB_BlackPebbles`/`AB_HardenedGrass`/`+Fertile`)
  inline — **no owned TerrainDef anywhere in the biome**; the sheet's §7 obsidian/
  volcanic-glass material family has no def expression.
- Weather: `RM_RedFog` (owned), `RM_ForgeStill` + `RM_BoilingRain` (owned, only ever
  forced by the pulse), AB_VolcanicAsh/AshRain donors, Clear 40. Rain/snow all 0 (ban 6).
- **`RM_ForgePulse`** GameConditionDef (canBePermanent, on the biome's
  biomeMapConditions): `RM_GameCondition_WeatherPulse` forces ForgeStill, rolls MTB-10h
  bursts of BoilingRain 20–40 min, deals `RUT_Scald` damage (4/60 ticks, unroofed only),
  starts a 2 h flash-growth window per burst. This is a REAL, shipped, biome-scale
  unique mechanic.

### Mechanics / C# (the Forge kit — FORGE_MECHANICS_1, all six built, item still `doing`)

The kit lives in `src/RimMandrake/EnvironmentalHazards/` (shared assembly, hard dep),
Forge-specific content in `UtinniPatches/`. Build passes 2026-09-13/14, offline-proven,
live quicktest still owed:

| F# | mechanic | state |
|---|---|---|
| F1 | Boiling-rain pulse + scald + flash flora | SHIPPED: `RM_GameCondition_WeatherPulse`, `RM_MapComponent_FlashCycle`, `RUT_Plant_FlashFlora` (×8 growth in window / ×0.05 outside), `RUT_Scald` DamageDef + `RM_ScaldArmor`/`RM_ArmorRating_Scald` |
| F2 | Beldon tibanna tap | SHIPPED: `RM_CompGatherableGas` (CompMilkable-shape), `RUT_TibannaTap_BeldonWiring.xml` (FindMod-gated onto RSW_Beldon, 12 gas / 2 days), `RUT_TibannaGas` item (placeholder price; **DEPLOY_HOLD, no art**). Ban-5 linter: only consumer is the tap — monopoly holds by construction |
| F3 | Vapor-column flight layer | SHIPPED (classes): `RM_MapComponent_VaporColumns` (columns from steam geysers / CompActiveGasEmitter / dangerous+avoidWander terrain), `RM_CompVaporDrifter`, `RUT_VaporDrifter_AerofleetWiring.xml`; ThinkTree wander-root wiring proven but thin |
| F4 | Foundry tower dungeon | SHIPPED (shell): `RUT_FoundryTowerEntrance` (MapPortal → `RUT_FoundryFloor` 80×80 pocket map, temp 70 °C, LavaDeep melt channels via `RM_GenStep_TerrainChannels`, salvage cache + tender spawn gensteps, `RUT_FoundryTowerScatter` on player maps). One floor per owner card 1 (RULED 2026-09-12); interiors are vanilla ScatterRuinsSimple stand-ins; tender pawnkind NOT cast; **both buildings DEPLOY_HOLD, no art** |
| F5 | Contagion die-off ring | SHIPPED: `RM_CompScriptedDieOff`, `RUT_DyingCreep`→`RUT_DeadCreep` (spread 6–10 over 4 h, dead by 8 h); in no wildPlants by design |
| F6 | Geothermal vent industry | SHIPPED (XML): `RUT_VentSmelter`/`RUT_VentForge`/`RUT_VentKiln` + recipe wirings |

Mod Settings: `RM_TheForgeMod.cs` — master toggle + 6 per-mechanic knobs (weather pulse,
tibanna rate, vapor immunity, tower scatter, die-off density, vent work-speed) —
**declared but NOT wired** except F1's shared `weatherPulseEnabled`; consolidation owed
to FORGE_MECHANICS_1 per the file's own header.

⚠️ **`RM_HediffComp_ForgeOnSurvival.cs` is NOT a Forge-biome mechanic.** It is the
MIASMA's fever-"forged" survival-boon comp (`onlyInBiomes: RUT_Miasma`, wired by
`Miasma/Patches/RUT_Miasma_ForgeOnSurvival.xml`). Named "forge" for the verb. Recorded
here so no census counts it either way.

Campaign plot on top (not this sitting's to build): `TIBANNA_EMBARGO_PLOT_1` (Empire gas
monopoly clock, both cards RULED 2026-09-12, source cut executed, build surfaces owed);
`TibannaEmbargo_CutMineableRoute.xml` live.

### Art status per cast member

From artpipe `registry.jsonl` + `done/` + `_artsrc/` + `Transient/*.decisions.json`
(checked before anything is called "owed", per the standing rule). Blanket owner ruling
2026-09-20: **replace** on every ported donor row's art.

| subject | status |
|---|---|
| `RM_FleetFlier` | **art DONE in artpipe** (`rutfleetflier_v1` east/north/south in `done/` + `_artsrc/`) — but the mod ships 0 PNGs and the def's texPath expects `Things/Pawn/Animal/RM_FleetFlier/`. **Wiring ticket, not an art ask** |
| `RSW_Beldon` | canon art DONE (`canon_beldon_v1` 3 facings) — replace ruling satisfied |
| `RM_FireLavender` | done + deployed (`FireLavender_a.png` in mod) |
| `RM_HeatsinkFungus` | done + deployed (`HeatsinkFungus_a.png`) |
| `RM_CinderCrust` | **no art anywhere** (searched cinder/cindercrust — only Cinderfelt/Cinderwing/Cindermite, different subjects). Q13 "regenerate the second copy's identity" still owed |
| fireweed / firevine | `firevine_fireweed_v1` done |
| sagecrust lineage | `sagecrust_v1` + `rot_sagecrust_v2` done (Rot's copy — not this biome's) |
| `AA_Aerofleet`/`AA_Metallovore`/`AA_CrescendoAnole`/`LavaSnail`/`RSW_LavaFlea`/`RSW_Maguana` | donor/port art live; all under the 2026-09-20 blanket "replace" ruling, none replaced yet, none queued |
| `RUT_TibannaGas`, `RUT_FoundryTowerEntrance`, `RUT_FoundrySalvageCache` | **DEPLOY_HOLD "no art yet"** (held 2026-09-13/14) — three real art debts on shipped mechanics |

⛔ Nothing in this table may be re-queued at movement 4; the fleet flier especially —
its art exists and sits unwired.

## Nine-mark scorecard

| # | Mark | Verdict | Evidence |
|---|---|---|---|
| 1 | Unique mechanic | **HAVE (one half unwired)** | The closed boiling-rain pulse is real, shipped and biome-scale: `RM_ForgePulse` on the BiomeDef's own `biomeMapConditions` → `RM_GameCondition_WeatherPulse` (ForgeStill → MTB-10h BoilingRain bursts → `RUT_Scald` on the unroofed → 2 h flash window). No other biome does anything like it. ⚠️ But the flash-GROWTH half is engine-only: `RUT_Plant_FlashFlora` (×8 in-window / ×0.05 outside) is used as thingClass by **zero plant defs anywhere** (git grep this pass — only the C# and one comment reference it). The sheet's "mosses drink in the seconds between fall and flash" is compiled and completely unexpressed in content. |
| 2 | Discoverable technology | **PARTIAL** | F6's vent industry is built (`RUT_VentSmelter`/`VentForge`/`VentKiln`, +20% work speed, no fuel) — but all three keep their vanilla research prereqs (Smithing/Stonecutting/Electric smelting): nothing is DISCOVERED, nothing learned here is kept elsewhere. The foundry-tower salvage caches (`RUT_FoundrySalvageCache`) are marker-only loot with no teach. Slate A. |
| 3 | Unique resources | **HAVE (thin)** | ⭐ Tibanna gas is real: `RUT_TibannaGas` + the beldon tap (`RM_CompGatherableGas`, 12/2 days), ban-5 monopoly linter-clean (only consumer is the tap). Caveats: placeholder MarketValue (TIBANNA_EMBARGO_PLOT_1 owns pricing), DEPLOY_HOLD no-art. The sheet's OTHER two headline resources are unbuilt: fireweed FIBER (the planet's heat-gear economy — no fiber item, no gear; `RM_ArmorRating_Scald` shipped with nothing granting it) and obsidian/volcanic glass (no owned TerrainDef or material def at all). |
| 4 | Surprising creatures | **PARTIAL** | The "what" moments are all carried by canon/donor rows: RSW_Beldon (colossal gas-grazer you can milk for blaster gas — genuinely surprising, Utinni layer), AA_Metallovore (metal-eater), RSW_Maguana (magma camouflage). The RM tier's one owned creature, the fleet flier, is charming but modest. Every donor row sits under the 2026-09-20 blanket art-replace ruling, none replaced. |
| 5 | GIANT beast | **PARTIAL** | The colossus exists but is canon and patch-layer only (RSW_Beldon 0.08, sky). The roster's two other giants — `Tibidee` (bodySize 12!) and `AA_ColossalAerofleet` (both 0.5 in `the_forge.json`) — are wired NOWHERE (left out during the pyramid-law small-share fix, still in the roster). The RM tier has no giant of any kind. Fill: the dhokkur. |
| 6 | Gravship touch | **MISS** | Nothing. The kit assembly even carries the proven detection point (`RM_Patch_GravshipArrivalLetter`, GenStep_GravshipMarker postfix — BIOME_ARRIVAL_NARRATION_1) and only TheSump has wired a letter to it; the Forge has neither a letter nor any mechanical voice against the ship. Slate B. |
| 7 | Soundscape | **MISS** | Sheet §9 writes the strongest sound brief on the planet — vent-roar, geyser-cough, the rain's hiss-and-flash, tower harmonics, "beneath it, felt more than heard, the working of machines under the melt" — and the shipped weathers borrow vanilla `Ambient_Wind_Storm`/`Ambient_Rain`/`Ambient_Wind_Fog`. No SoundDef of ours exists. Slate C. |
| 8 | Interesting weather | **HAVE** | Three owned WeatherDefs (`RM_ForgeStill`, `RM_BoilingRain`, `RM_RedFog` — the last de-Star-Wars'd by owner ruling 2026-09-24), plus the pulse condition that owns the sky. The only biome whose weather is a closed loop the map itself drives. Donor AB_VolcanicAsh/AshRain still ride alongside, MayRequire-guarded — acceptable, not a defect. |
| 9 | Relationship to the gods | **PARTIAL (ruled richly, zero built)** | The frozen sheet §8 is the ruled content: two faiths, one mountain, no correction — Sh'kaar's forge (war-sun's anvil) vs the Tribes' unstolen fire, with the ratified precept *"Pyrelands fire is collected; Forge fire is only witnessed"* and hard ban 4 backing it. Ruled 2026-09-07 at the freeze; the sheet's own Owed line still lists the canon sitting (precept → `faction_religions.md` §4). No def, text or precept expresses any of it in game. Slate F. |

**Score: 3 HAVE, 4 PARTIAL, 2 MISS (6, 7).** The Forge is the inverse of the Cauldron:
its mechanics kit is the most complete of any biome (all six F-mechanics have shipped
build passes) while its CONTENT skin is thin — flash flora unwired, fiber economy
absent, giants unwired, sound and gravship untouched, one owned creature. The volley
should aim at 6/7, at converting 2/3/4/5/9's ruled-but-unbuilt halves into tickets, and
at the free wins already sitting in the tree (fleet-flier art unwired, flash-flora
class unused, Tibidee/ColossalAerofleet unwired).

## Roster gaps + Proposed fills

**Q11a standalone-tier depth**: the free `RM_` mod with no donors installed fields
**1 creature** (fleet flier — whose art exists in artpipe but is not in the mod) and
**5 plants** (3 owned + 2 vanilla/Odyssey), on a biome whose animalDensity is the
highest of the bedazzle list so far (1.2). 4 of 5 inline fauna rows are MayRequire'd
donors. Q11a says the free mod must look the same as the campaign one — today it is a
near-empty sky.

Structural role holes (independent of donor presence):

- **No owned GIANT** (mark 5) — and both roster giants unwired.
- **No owned ground herbivore** — the one ground herd (RSW_LavaFlea) is campaign-layer;
  the RM tier's ground fauna is all donors.
- **No predator anywhere in the sky** — aerofleet, beldon, fleet flier are all prey;
  the pyramid has no apex in the biome's own signature stratum (the columns).
- **No flash-interval creature** — the biome's admission test ("lives in the
  flash-interval, or in the sky") has zero fauna expression on the flash side.
- **No voice** (mark 7) and no fiber/obsidian expression (mark 3) — flora/terrain gaps
  rather than fauna.

### Proposed fills (movement 2 pitches — owner admits or strikes at the sitting)

All NEW inventions, one home (the Forge), named in the biome's own ruled accent
(Batch 5c: *heat — a `j` or breathed `dh` at the front, a back vowel, a coda that
closes like a vent: -ur/-osh/-ox*; existing register: jibbur, dhommur, jorrosh).
Collision-swept this pass with `git grep -il` across `src/`, `design/`,
`infrastructure/state/` — sweep sanity-probed on `korrum` (**66 files** — instrument
proven able to see); every name below returned **0 files**. All four also passed
`check_pseudo_sw_name.py` (4/4 PASS, shape + no collision with the 137 canon entries).

| name | defName | kind | role |
|---|---|---|---|
| **dhokkur** | `RM_Dhokkur` | creature (GIANT) | The colossus (mark 5), built on the biome's own clock: an obsidian-backed rain-drinker the size of a hill that sits dormant through the still heat — reads as terrain — and unfurls to walk and drink ONLY during a boiling-rain burst. The burst that scalds every colonist is its feeding hour: the biome's hazard inverts into its giant's pulse. Neutral, immensely tough, slow; butchers into heat-shielding hide (couples to the fiber/scald-gear lane, slate D/E). |
| **julmox** | `RM_Julmox` | creature | The owned ground herd (RM-tier legal herbivore). A low, wide, plate-footed grazer that squats sealed between bursts and fans out across the skirts in the flash window to crop the steaming moss film — the fauna half of the flash-interval admission test. Herd animal, tamable, the standalone tier's pastoral spine. |
| **jossur** | `RM_Jossur` | creature | The sky apex (pyramid law). A long-winged column-rider that stoops on fleet fliers and young fumeriders where the updrafts are strongest — the first predator in the biome's signature stratum. Real 1.6 flight stats (MaxFlightTime, the flier law); rides the F3 vapor-column layer that already ships (`RM_CompVaporDrifter`). |
| **dhuvvox** | `RM_Dhuvvox` | creature | The flash-swarm (mark 4's owned "what" moment). Knuckle-sized skitterers that exist as sealed nodules in the ash until the rain hits, then erupt by the hundred for the two-hour window to strip the wet rock — a living clock the player learns to read. Harmless singly, a floor of motion during a burst; despawn/reseal on window end. |

Reserve (swept clean, offered only if he wants more): *dhorrox, jukkur, jovvosh*
(0 collisions each) — but four pitches is the proven sitting shape.

**Not proposed:** re-homing anything; wiring Tibidee/ColossalAerofleet (the owner's
rows to wire or strike — both are LARGE and were deliberately left out during the
pyramid-law pass); any lava-native anything (ban 1); anything furred/lush (ban 3).

## Candidate mechanics slate

Ranked pitches for the four-turn volley, aimed at the MISSes (6, 7) and at converting
the ruled-unbuilt halves of 1/2/3/5/9. All DLCs assumed present. None reuses another
biome's spine (Blue Desert detonation, Cracked Lands FlowWorks water, Cauldron
gas/filter/loud-ground, Pyrelands fire-collection, Miasma vermin) — the Forge already
owns its spine (the closed rain); most of this slate deepens it rather than adding a
rival.

**A. Wire the Flash — the interval made playable** *(marks 1 + 3; rank 1)*
The cheapest big win in any biome reviewed so far: `RUT_Plant_FlashFlora` compiles,
`RM_MapComponent_FlashCycle` runs, and no plant uses either. Wire the owned flora (and
the julmox/dhuvvox fills) to the window, then make the window the player's harvest
economy: flash-blooming moss harvestable ONLY in the 2 h after a burst at multiplied
yield, wild fireweed ripening on the same clock. Colony life reorganizes around the
mountain's breath — everyone shelters through the burst, then everyone runs out to reap.
*Engine:* thingClass swap + a harvest-window comp; the hard parts already shipped.
*Trade-off:* needs the burst telegraph (slate C) or the reap window feels arbitrary;
tune so sheltering isn't just pause-and-wait.

**B. The Ship Drinks the Mountain — free heat as launch economy** *(mark 6; rank 2)*
The Forge's voice against the gravship, in the biome's own thesis ("the one place fire
costs nothing"): while landed here, a deployable heat-exchanger rig taps a vent and
feeds the grav-engine — launch charge builds measurably faster than anywhere on the
planet — but every burst scours the parked ship (minor exterior damage/ash filth on
unroofed ship tiles during boiling rain). The Forge is the best refuel stop on Ash'karr
and the most uncomfortable one; landing here is a bargain the player prices. Arrival
letter rides the already-proven `RM_Patch_GravshipArrivalLetter` seam (TheSump
precedent). *Engine:* GravEngine charge-rate hook + the F1 condition's burst state, one
building def; Odyssey assumed. *Trade-off:* charge-rate balance against the campaign's
travel pacing; the scour must stay annoyance-grade, not hull-loss-grade.

**C. The Mountain's Breath, Heard — soundscape + telegraph** *(marks 7 + 1; rank 3)*
Author the §9 brief as real SoundDefs: vent-roar floor under ForgeStill, geyser-cough
one-shots, tower harmonics near foundry towers, the sub-felt machine throb near melt —
and make the burst AUDIBLE BEFORE IT ARRIVES: a building hiss that swells in the last
in-game half-hour before boiling rain (the pulse condition already knows). The ear
becomes the weather alert; slate A's reap-run starts on a sound cue. *Engine:*
SoundDefs + sustainers keyed to weather/condition state (RustCathedral hum precedent in
this repo); the telegraph is a few lines in the condition. *Trade-off:* audio assets
are a pipeline ask; needs a visual fallback (letter/alert) for muted players.

**D. Fireweed Fiber — the heat-gear economy made real** *(marks 3 + 2; rank 4)*
The sheet's headline resource ("the source material of the planet's heat-survival gear
economy") built at last: fireweed harvest yields fiber, fiber + tailoring makes
scald-gear (apparel granting `RM_ArmorRating_Scald` — the stat shipped 2026-09-13 and
NOTHING in the repo grants it), and scald-gear is what lets a colonist work through a
burst instead of sheltering. The biome that hurts you grows the thing that lets you
endure it — and the gear is the export every other hot biome wants. *Engine:* pure XML
(item, recipes, apparel statOffsets); the armor category and damage type already exist
and are consumed by the shipped F1 damage path. *Trade-off:* balance against vanilla
heat gear; decide the RM/RUT tier split (fiber is generic, campaign gear lists are not).

**E. Tender-Craft — the discoverable technology** *(mark 2; rank 5)*
What the towers teach: studying a foundry salvage cache (they ship marker-only today)
yields forge-tech fragments → a techprint-style unlock, **vent-craft** — the player
keeps the ancients' trick of building the F6 vent benches (and slate B's heat-exchanger)
on ANY map with a steam geyser, not just the Forge. The biome's lesson travels; ban 2
holds — you learn to use the heat, never what the machines below are for. *Engine:*
Royalty techprint or Anomaly study-interactable on `RUT_FoundrySalvageCache` (both DLCs
assumed); research gates the benches already have. *Trade-off:* makes geothermal
industry planet-portable — deliberate power creep the owner should price.

**F. Two Faiths, One Mountain — the gods layer, in content** *(mark 9; rank 6)*
Per the Blue Desert precedent (mark 9 = biome-local lore, no campaign ideoligion defs):
the witness-trail up the ash as a mapgen ruin line (cairns, a summit witness-ring), a
"witnessed fire" thought/ritual hook for pilgrim visitors, Sh'kaar's LavaLake/LavaCrater
sites flavored as his anvil — and the precept's teeth stay textual: Forge fire is seen,
never carried (ban 4 already forbids the def that would break it). *Engine:* scatter
defs + thoughts/strings, zero C#. *Trade-off:* his call how much reaches defs vs the
canon sitting the sheet already owes; zero mechanics if he keeps it prose.

**G. The Dhokkur Hour — the giant on the clock** *(marks 5 + 4; rank 7)*
The fill made mechanical: dormant dhokkur read as rock (no threat, minable-looking,
tooltip lies); when the rain hits they stand up and walk, drinking, indifferent,
flattening what stands in the path they've walked for a thousand bursts. Colony siting
becomes a read of the herd's paths; a killed dhokkur is a mountain of heat-shielding
hide and a permanently vacant path. *(Deliberately NOT a harvest-the-living-giant
economy — that is the Cauldron vexxiss's spine.)* *Engine:* dormancy comp
(CanBeDormant/WakeUpDormant precedent) keyed to the pulse condition's burst state; big
animal + pather. *Trade-off:* "giant walks through your wall" needs care to read as
majestic, not griefing; path memory is a light MapComponent.

**H. The Columns Made Visible** *(marks 1 + 7 support; rank 8)*
`RM_MapComponent_VaporColumns` already computes the column field and nothing shows it:
render the columns (shimmer/steam overlay on column cells), have fumerider and beldon
herds visibly congregate in them, and let slate B's heat-exchanger and F6 benches read
adjacency from the same component. One system, three consumers, and the sky pasture —
the biome's signature image — becomes something the player can SEE. *Engine:* the
component ships; an overlay drawer + wander-root wiring (the proven
`JobGiver_Wander.GetWanderRoot` seam, classes still unwritten). *Trade-off:* overlay
rendering cost on big maps; visual noise budget against the ash palette.

---

*Movement 1–2 complete on paper: the census is measured (parsed from the element-form
rosters and the patch's own xpath+value, never `<li>` counts; no tile counts cited),
the scorecard names its evidence, the four fills are collision-proven and
checker-passed, and the slate is the movement-3 opening hand. Nothing here edits the
frozen sheet, re-opens a frozen ruling, files an item, or queues art. Found-and-recorded
for the sitting rather than acted on: the unwired `RUT_Plant_FlashFlora` class, the
fleet flier's finished-but-unwired art, the granted-by-nothing `RM_ArmorRating_Scald`,
the unwired Tibidee/ColossalAerofleet roster rows, and the three DEPLOY_HOLD art debts.*
