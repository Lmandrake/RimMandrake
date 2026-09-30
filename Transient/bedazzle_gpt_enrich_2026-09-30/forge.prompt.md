You are a senior game designer consulting on a RimWorld mod campaign. The owner wants recommendations to ENRICH one biome that has already been through a design sitting. Be concrete, vivid and buildable in RimWorld 1.6 (XML defs, C# comps, Harmony, incidents, map components, weather, sounds).

BIOME: The Forge

Standing rules of this project (binding on every recommendation):
- RimWorld 1.6 with ALL five DLCs assumed present; a Star Wars (old Tatooine / Jawa scavenger clan) campaign on one hand-made fixed planet. No worldgen, no alternative planets.
- Each animal lives in ONE biome unless there is an in-game reason (migration, life stage).
- Invented exotic names are fine; genuine Star Wars canon goes in a separate Star Wars layer.
- Heat is ONE planet-wide kind riding vanilla heatstroke; biomes differ by heat kind (overhead sun, low sun, ambient steam/volcanic).
- Animals or pawns must never vanish without a readable sign of what happened.
- If it flies in the fiction, it flies in the game.
- Every mod ships real Mod Settings.
- A biome's ideas must NOT echo another biome's signature; each biome has its own voice.
- The "bedazzle" bar is nine marks: unique mechanic, discoverable technology, unique resources, surprising creatures, a GIANT beast, a gravship touch, an interesting soundscape, interesting weather, a relationship to the gods.

WHAT THE OWNER HAS ALREADY RULED for this biome (ledger, verbatim; do NOT contradict or re-propose anything cut here):
- 2026-09-29: VOLLEY TURN 2, owner typed this session (guard cannot see the turn; recording under BENCH). Ruling 1: "Wire in all waiting." - everything found finished-but-unwired wires in: Tibidee, ColossalAerofleet, fleet flier art, FlashFlora plant hookup, the unwired review-doc list.
- 2026-09-29: Ruling 2, the biome spine enriched to a full fire-and-water cycle, owner verbatim: "This is a biome of fire and water. The open lava is horrible, hot, deadly. The occasional washes of superheated gas burst ignite much of the map. Then the torrential rains pour down, causing flooding. There should be huge plumes of steam and transformation of the lava vents to temporary basalt shingle and pumice chunk."
- 2026-09-29: Ruling 2 cont., owner verbatim: "Then the eerie event: strange forms begin to grow quickly from these frozen rock forms fueled by the gases and extreme heat raging below (generate five different ideas on what these could be, dont just say valuable crystals, something really unusual and special). Eventually glowing cracks form on the rock covering, and the whole thing melts back into lava again, destroying them." Five-forms ideation owed in turn 3.
- 2026-09-29: TURN 4, owner typed this session: "1) admit. 2) only E, lets see what we can imagine with the vent-craft. 3) none." - all four fills ADMITTED (dhokkur/julmox/jossur/dhuvvox); slate B, D, F STRUCK, E (vent-craft) kept open for further ideation; ALL FIVE strange-form pitches CUT. Owner commissioned a GPT consult: five ideas per question on (A) non-power uses of a machine on a volcanic geyser vent, (B) transient forms growing from a fire-water interface on frozen basalt in a volcanic crater.
- 2026-09-29: GPT consult BLOCKED: codex.exe exec returns 401 invalid_refresh_token on every call (v0.153.4, auth.json expired) - needs the owner to sign back in to Codex/ChatGPT. Both consult prompts (A vent-machine uses, B transient fire-water forms) are ready to fire the moment auth is back.
- 2026-09-29: GPT consult DONE after owner re-login (codex exec, gpt-5.6-sol xhigh): A1-A5 vent-machine uses + B1-B5 transient forms delivered, full text Transient/forge_gpt_consult_2026-09-28/. Presented to owner with engine reads; awaiting his picks. Review-sheet agent for prior bedazzle art also launched (owner mid-turn request).
- 2026-09-29: TURN 6, owner typed: vent machines ALL CUT - "lets just keep vent-based power as an option (already present in game) and move on" - slate E closes as vanilla geothermal suffices, no new vent tech. GPT B1-B5 ALL CUT as horror: "These are ABSOLUTELY HIDEOUS! Enough with the horror." Owner wants five more: "minerological, otherworldly ecological, or geological possibilities. Xenobiology. Not horror, reproducing dead people, etc." BENCH delivering five in-window.
- 2026-09-29: TURN 7, owner typed: "Floatstone is fantastic! Ultra-light pumice made of what looks like spun glass whirled into tangles. Super strong and light building material, not flammable, quite valuable, and the walls it makes look like swirled stone spun sugar made into blocks. Very beautiful." - FLOATSTONE ADMITTED with that enrichment as the growth-phase form. Other four forms (Prism Groves, Tide of Colours, Ring Chimneys, Iron Blossoms) not ruled either way - asked once at ticket-out, default is they do not ship. Volley closed; ticket-out proceeding.
- 2026-09-29: TURN 8, owner typed: "No to the other four forms." - Prism Groves, Tide of Colours, Ring Chimneys, Iron Blossoms are CUT, ruled not defaulted. Floatstone is the sole growth-phase form. Forge sitting now open for art/build tracking only.

THE BIOME'S DESIGN DOCS:
===== design/Jawa/worldbuilding/biomes/forge_bedazzle_review_2026-09-28.md =====
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


===== design/Jawa/worldbuilding/biomes/forge_bedazzle_cast_2026-09-29.md =====
<!-- status: cast bible — commissioned under FORGE_BEDAZZLE_SITTING_1 movement 4 -->
# The Forge — bedazzle cast bible (movement 4: commission)

**Item:** `FORGE_BEDAZZLE_SITTING_1` · **Program:** BAROQUE_BEDAZZLE_PROGRAM_1 (row 6)
**Date:** 2026-09-29 · **Author:** movement-4 commission agent (Fable)
**Feeds:** `FORGE_RULED_CONTENT_1` (defs) + `FORGE_CYCLE_MECHANICS_1` (the grand cycle)
**Authorities:** `forge_bedazzle_review_2026-09-28.md` (the review; volley CLOSED),
both tickets above (every ruling below is fixed), the frozen sheet `the_forge.md`
(voice only — never edited). Mod: `src/RimMandrake/TheForge/`.

## 0. Shared law — every card obeys this without restating it

- **Voice:** the Forge is the only unstolen fire — native heat that owes nothing to
  the sun. Dark towers against the glare, herds grazing the smoke, the closed rain
  that boils, falls, and flashes. The quotas below are still being run for no one.
  Descriptions talk foundry: anvil, seam, slag, quench, quota.
- **Name accent** (Batch 5c, ruled): heat — a `j` or breathed `dh` at the front, a
  back vowel, a coda that closes like a vent: -ur/-osh/-ox. Register: jibbur,
  dhommur, jorrosh — now dhokkur, julmox, jossur, dhuvvox.
- **Art register (the Forge house style for every job below):** a volcanic massif
  under doubled furnace light — hard white sun above, seam-red from below; basalt
  black, ash grey, obsidian gloss, steam-white plumes, seam-red ONLY where the melt
  actually shows. Realistic painted natural-history illustration, grounded
  believable anatomy, matte mineral surface texture, never cartoonish, never cute,
  no outlines, alien but biologically plausible. Faced jobs: north is a **true rear
  view from directly behind — no eyes, no face, no frontal features.**
- 🔴 **Palette diversity is LAW on this cast** — owner, verbatim, carried in every
  style_notes: *"Your color palette is too uniform per biome. Needs more variety."*
  Each subject below is assigned its OWN palette anchor, deliberately distinct from
  its castmates; the register above is the room they stand in, not the paint they
  wear.
- **Hard bans from the frozen sheet ride every prompt:** nothing lives in the lava
  (no lava-native read); no furred, chilled or lush-register anatomy; no ordinary
  rain anywhere in a prompt.
- **One home.** All four natives are Forge-only (owner law 2026-09-21).
- **Numbers are design proposals** — FOUNDRY calibrates in the build tickets; the
  relationships (who is biggest, what is dormant when, what the freeze is worth)
  are the ruled part.

## 1. Name sweep (MEASURED this pass, 2026-09-29)

Instrument: `git grep -il <name> -- src/ design/ infrastructure/state/`.
**Sanity probe: `korrum` → 67 files** (instrument proven able to see).

| name | files | verdict |
|---|---|---|
| `dhokkur` | 5 | CLEAR — all 5 are this sitting's own commissioning prose (review doc, both tickets, BENCH ledger, queue render). No def, no other subject. |
| `julmox` | 4 | CLEAR — same set, review-pass sweep already paid |
| `jossur` | 4 | CLEAR — same set |
| `dhuvvox` | 4 | CLEAR — same set |
| `floatstone` | 4 | CLEAR — the owner's own turn-7 word; hits are the two tickets, BENCH ledger, queue render |
| `FloatstoneGarden` | 0 | CLEAR — coined this pass |
| `BasaltShingle` | 0 | CLEAR — coined this pass (terrain, FOUNDRY-owed) |
| `PumiceChunk` | 0 | CLEAR — coined this pass (terrain, FOUNDRY-owed) |
| `GlowingCrack` | 0 | CLEAR — coined this pass (terrain, FOUNDRY-owed) |

(All four creature names also passed the review pass's collision sweep +
`check_pseudo_sw_name.py`, per the review doc — not re-litigated here.)

## 2. Art dedup (standing owner law — searched before queuing anything)

Instrument: filename search over `infrastructure/artpipe/` `done/` + `pending/` +
`active/` + `failed/` + `_artsrc/`, content search of `registry.jsonl` and all
`Transient/*.decisions.json`. **Sanity probes: `suush` → 6 files in done/, 24
registry hits; `korrum` → 6 in done/, 2 decision hits** (the instrument sees).

- **Empty everywhere — genuinely owed, queued below:** dhokkur (both states),
  julmox, jossur, dhuvvox (both states), floatstone garden, floatstone item.
  Also swept empty: basalt / basaltshingle / pumice / glowingcrack (no terrain
  art exists to reuse — see §6).
- **Found and NOT queued:** `RM_FleetFlier` — **6 files in done/ + 3 in
  `_artsrc/`** (`rutfleetflier_v1` east/north/south). This is a WIRE for FOUNDRY
  (`FORGE_RULED_CONTENT_1` §1 "wire in all waiting"), never a queue. ⛔ Nothing in
  the review's art table may be re-queued; the three DEPLOY_HOLD debts
  (`RUT_TibannaGas`, `RUT_FoundryTowerEntrance`, `RUT_FoundrySalvageCache`) belong
  to that same wire-in ticket, not to this commission.

## 3. Cast entries — the four admitted natives

### RM_Dhokkur — the giant on the clock (two visual states)

**Ruled frame (fixed, `FORGE_RULED_CONTENT_1` §2):** GIANT. Obsidian-backed
rain-drinker; dormant through the still heat — reads as terrain — and unfurls to
walk and drink only during boiling rain. Neutral, immensely tough, slow; butchers
to heat-shielding hide. Dormancy behavior lives in `FORGE_CYCLE_MECHANICS_1`
(CanBeDormant precedent, keyed to the rain phase; path-memory kept light).

**Description (in the biome's voice):**

> Half the outcrops on the skirts are stone. The other half are waiting for rain.
> A dormant dhokkur sits out the still heat as a hill of banked obsidian plates,
> ash drifted into its seams, and the survey crews learn the difference the day
> the sky opens: the hill stands up. It walks its own path — the same path, worn
> a thousand bursts deep — drinking the scald straight off its back while
> everything else on the mountain runs for a roof. It is not angry. It has never
> needed to be. Its hide turns the boiling rain, and the boiling rain is the
> worst thing this mountain knows how to say.

**Two visual states, both commissioned:**

- **Walking form (3 facings):** a hill that walks — vast low body slung between
  four column limbs, back a shingled massif of obsidian plates channeled with
  rain-gutters running to a low drinking maw at the prow; head barely
  differentiated, more cistern than face. Unfurled plate-fans lifted along the
  spine to catch the fall. Mid-stride, ponderous, streaming.
- **Dormant form (single):** the same animal furled — limbs drawn under, plate-fans
  banked flat, silhouette settled into a weathered outcrop dome with ash in the
  seams. 🔑 The tell must be findable and quiet: the gutter-lines converge too
  regularly for stone. The tooltip lies; the sprite may only whisper.

**Silhouette/palette brief:** obsidian gloss over basalt dark — but this subject's
**palette anchor is RAIN-SLICK**: wet blue-grey sheen and mirror glints on black
glass, silver runnels of standing water in the gutters, cool steam-white breath —
the one cast member painted by the water, not the fire. No seam-red anywhere on
the body (nothing lives in the lava; it drinks rain, not melt). No eyes visible
at sprite scale; no fur, ever.

**Facings:** walking form south, east, north (north = true rear: the plated back
massif, banked fans from behind, rear column limbs). Dormant form single.
**Canvas 512 both states** — colossus precedent (Vhaulk/Muttavaq/Vexxiss): scale
must carry in the pixels. **drawSize intent: ~7.5 walking, ~6.5 dormant**;
bodySize ~6.0 class, slow, rare (0.02-class), neutral.

### RM_Julmox — the plate-footed pastoral spine

**Ruled frame (fixed):** the owned ground herd — sealed between bursts, grazes the
flash-window moss film; tamable, the standalone tier's pastoral spine.

**Description:**

> Low and wide as a cooling slab, on feet spread into plates that never sink into
> hot ash. Between rains the julmox squats sealed, lids down over every seam,
> a row of dull kettles on the skirts. Then the burst passes, the rock steams,
> the moss film blooms — and the herd fans open and goes to work, cropping the
> two hours the mountain allows. The Farmers keep them for the same reason the
> mountain does: they are patient, they are sealed against the worst of it, and
> they turn stone-film into meat. Pasture is wherever it last rained.

**Silhouette/palette brief:** broad flat-backed grazer, wide plate-feet the
signature (oversized, splayed, heat-proof soles), a fringed grazing muzzle held
low; sealing lids visible as seam-lines along flank and face, caught HALF-FANNED —
plates lifted, fringe out — so the sprite reads as the grazing hour, not the wait.
**Palette anchor: ASH-AND-BLOOM** — pale kiln-grey and bone body wearing the flash
window's paint: fresh moss-green staining on muzzle, feet and belly, a faint
steam-damp darkening low. The one cast member allowed real green — it is wearing
its food. No fur; the covering reads as fine mineral plating.

**Facings:** south, east, north (north = true rear: sealed back seams, rear
plate-feet, no face). Canvas 256. **drawSize intent: ~1.8**, bodySize ~1.2 class;
herd animal, tamable, 0.4-class commonality — the standalone tier's texture.
*(The fully-sealed squat is a def/state question: if FOUNDRY wires a dormant
graphic to the cycle phase, file the sealed-form single as a follow-on job —
dressing on the mechanic, not part of this commission.)*

### RM_Jossur — the sky apex, grounded sprite

**Ruled frame (fixed):** sky apex column-rider; REAL 1.6 flight (`MaxFlightTime`
stat, Locust shape). 🔴 **Flight flip-book frames are NOT commissioned now** — the
flyer law says never block flight on frames; a frameless flyer flies with no
wing-beat, correct behaviour, plainer look. Frames are a named follow-on (§7).

**Description:**

> The columns are pasture, and every pasture gets its wolf. The jossur rides the
> vent updrafts on wings longer than the rest of it put together, hanging in the
> shimmer where the fleet fliers race and the young fumeriders drift — and then
> it stops hanging. Grounded, it is an awkward folded thing, all wing-knuckle
> and stilt, mantling over its kill in the ash. Airborne, it is the reason the
> herds keep their young in the middle of the smoke.

**Silhouette/palette brief (grounded):** a long-winged stooper at rest — wings
folded high and crossed over the back like furled banners, wing-knuckles standing
above the shoulder line, body lean and keeled, stilt legs, a hooked heat-shielded
head held low and level. The grounded read is "folded weapon", not "walking bird".
**Palette anchor: SCOUR-RUST** — wind-burnished rust-red and hot umber over dark
primaries, pale scald-scarring on the leading edges, beldon-amber eyeshine as the
one hot accent. No lush plumage register; the covering reads as scoured vane and
plate, heat-adapted and few.

**Facings:** south, east, north (north = true rear: folded wing-backs and tail
vanes, no face). Canvas 256. **drawSize intent: ~2.6 grounded** (the folded wings
carry the size), bodySize ~1.6 class; rare apex (0.06-class), predator band.

### RM_Dhuvvox — the flash-swarm (two visual states)

**Ruled frame (fixed):** knuckle-sized skitterers existing as sealed ash nodules
until the rain hits, erupting by the hundred for the two-hour window; despawn /
reseal on window end. The living clock the player learns to read.

**Description:**

> Kick through the ash between rains and you will turn up little glazed nodules,
> heavy for their size, and think them slag. Then the rain comes down boiling,
> and the slag hatches. For two hours the skirts run with dhuvvox — a floor of
> quick glitter stripping the wet rock of everything the flash woke — and when
> the stone dries they seal where they stand and are slag again. The old hands
> tell time by them. When the dhuvvox run, you reap; when they still, you are
> already late for shelter.

**Two visual states, both commissioned:**

- **Skitterer (3 facings):** a knuckle-sized many-legged glassback — domed
  wet-gloss carapace, legs a fringe of motion, short siphon head down against the
  rock. Posture mid-scuttle. At drawSize it must read as a bright fleck; the
  carapace highlight does that work.
- **Sealed nodule (single):** the same animal shut — a glazed teardrop nodule,
  leg-fringe seams just visible as a spiral, half-dusted with ash. Reads as slag
  until you know.

**Silhouette/palette brief:** **palette anchor: EMBER-FLECK** — charcoal-black body
with a hot ember-orange shine along the carapace dome (reflected seam-light, not
inner glow — nothing lives in the lava and nothing here reads volatile), legs pale
glass. The nodule state inverts it: matte ash-grey glaze, the ember tint only in
the seam-spiral. The swarm's brightness is what makes the clock legible from map
zoom.

**Facings:** skitterer south, east, north (north = rear dome and leg-fringe, no
head). Nodule single. Canvas 256 both. **drawSize intent: ~0.5 skitterer, ~0.4
nodule**; bodySize ~0.1, swarm-common inside the window (the mechanics own
spawn/despawn; `FORGE_CYCLE_MECHANICS_1` phase 5 clock).

## 4. Cast entries — the floatstone family

**Ruled frame (fixed, owner verbatim, turn 7 — this enrichment is LAW for the
art):** *"Ultra-light pumice made of what looks like spun glass whirled into
tangles. Super strong and light building material, not flammable, quite valuable,
and the walls it makes look like swirled stone spun sugar made into blocks. Very
beautiful."* Harvested from floatstone-garden growths during the freeze phase;
unharvested globes tear free and drift off-map ahead of the melt
(`FORGE_CYCLE_MECHANICS_1` phase 5).

### RM_FloatstoneGarden — the growth (lace-walled globe)

**Description:**

> When the melt freezes over and the plumes stand tall, the crust blooms. A
> floatstone garden starts as a knot of glass threads and whirls itself outward
> into a lace-walled globe, chamber over chamber, light enough that a grown one
> strains at its own root. Caught ripe, it is the most beautiful quarry on the
> planet. Left standing, it tears free ahead of the melt and drifts away over
> the seams — the one form the lava never gets back.

**Silhouette/palette brief:** a globe of whirled glass lace on a short mineral
root-boss — visible spun-thread structure, wound in swirls like sugar-work,
chambered and translucent-edged, a few threads trailing loose at the crown (the
tear-free foreshadowed). **Palette anchor: OPAL-LACE** — pale spun-glass whites
and warm pearl, faint opal iridescence in the whirls, root-boss basalt-dark for
contrast; steam-white ambience, zero seam-red on the growth itself. The read is
"very beautiful" first — the cast's one pure grace note, standing on the
deadliest ground.

**Facings:** single (growth; Graphic_Random variants derive from the master).
Canvas 256. **drawSize/visualSize intent: ~1.4 cells.** *(Ripening states: ship
as derives/retints of this master — smaller tighter knot → full globe; dressing
on the cycle, not separate commissions.)*

### RM_Floatstone — the material (item + stuff color master)

**Description:**

> A block of floatstone weighs what a lie weighs. Spun glass whirled into
> tangles, frozen mid-swirl, strong the way a woven thing is strong — it will
> not burn, it barely presses on the hand that carries it, and a wall of it
> looks like swirled stone spun sugar cut into blocks. The Farmers sell it by
> the promise instead of the weight. Nobody has ever asked for the weight back.

**Silhouette/palette brief (item icon; the STUFF colour derives from it):** three
cut blocks stacked, each face showing the whirled spun-glass grain in swirls —
the "spun sugar made into blocks" read is the whole job; the cut faces must carry
visible whirl-lamination, never a flat pumice stipple. **Palette anchor:
OPAL-LACE** (shared with the garden — one family, one paint): pearl-white body,
warm cream swirl-bands, faint opal sheen at the corners. Reads light even as a
picture.

**Facings:** single. Canvas 256. Item + StuffProps ride `FORGE_RULED_CONTENT_1`
§3 (strong, very light, flammability 0, high market value).

### Floatstone walls — the stuff route (checked, no art commissioned)

**MEASURED against the repo's own custom stuffs:** owned stuff-capable materials
here (`RM_Lanternstone`, `src/RimMandrake/LanternDeeps/Defs/ThingDefs_Items/
RM_LanternstoneItems.xml`) ship `<stuffProps>` with a `<color>` + `<appearance>`
and **ride the vanilla wall/blocks atlases tinted by that color** — no owned wall
atlas art exists anywhere in `src/`. ⇒ **Floatstone walls take the same route:**
stuffProps color drawn from the item master (pearl-white, warm cream),
`appearance Smooth` for the glass read. The "swirled spun sugar" wall grain
cannot ride a vanilla tint alone — if the owner wants the swirl visible in the
built wall, that is a custom wall atlas, a real follow-on ask (§7), not assumed
here.

## 5. Cycle set pieces — terrain (FOUNDRY-owed, out of artpipe's lane)

**Route checked (MEASURED):** every owned TerrainDef in `src/` reuses a vanilla
`texturePath` (`RM_SeaFloorGround.xml` → `Terrain/Surfaces/Sand`,
`RUT_BoughSoil.xml` → `Terrain/Surfaces/SoilRich`, the DivingInteraction and
FeverWood families throughout) — terrain textures are hand-picked vanilla
surfaces with def-level `color` tints, and `registry.jsonl` holds **zero** real
terrain-texture jobs. ⇒ **Terrain art is not artpipe's lane here. Nothing queued;
the three set pieces below are FOUNDRY-owed on `FORGE_CYCLE_MECHANICS_1`:**

- **`RM_BasaltShingle`** (phase-4 temporary crust) — vanilla rough-stone family
  texturePath tinted basalt-dark with a cooled blue-grey cast; walkable, the
  treasure floor.
- **`RM_PumiceChunk`** (phase-4 companion crust) — vanilla gravel family
  texturePath tinted pale ash-buff; the lighter, rubblier read beside the
  shingle.
- **`RM_GlowingCrack`** (phase-6 warning terrain) — the one that may exceed a
  tint: vanilla texture with an emissive seam-red color pass if the engine's
  terrain `color`/glow fields carry it; if a custom texture proves genuinely
  needed, FOUNDRY files it then — not pre-queued on a guess.

## 6. Wired-by-FOUNDRY — exists already; NOT queued (⛔ standing law)

| subject | evidence | disposition |
|---|---|---|
| `RM_FleetFlier` | `rutfleetflier_v1` — 6 files in `done/`, 3 in `_artsrc/` | **WIRE** into the RM mod's Textures (`FORGE_RULED_CONTENT_1` §1); an art queue here would throw finished work away |
| `RSW_Beldon` | `canon_beldon_v1`, 3 facings, done | nothing owed |
| `RM_FireLavender` / `RM_HeatsinkFungus` | done + deployed in-mod | nothing owed |
| `RUT_TibannaGas` / `RUT_FoundryTowerEntrance` / `RUT_FoundrySalvageCache` | DEPLOY_HOLD "no art yet" | the review's found-unwired list; rides `FORGE_RULED_CONTENT_1` §1's wire-in, **not** this commission (their register is Utinni industry, a different sitting's judgement) |
| `RM_CinderCrust` | no art anywhere (review-confirmed) | Q13 identity regen owed — but that is `FORGE_RULED_CONTENT_1` roster work with an open identity question; queuing art before the identity is written would paint the wrong plant. Handoff note §8. |

## 7. Queued art — 6 subjects (8 sprite sets), 16 job files

**CSV:** `infrastructure/artpipe/art_lists/forge_bedazzle_cast.csv` —
`rimflow_item_id FORGE_BEDAZZLE_SITTING_1`, channel codex, transparent,
priority 70. Queued via `fill_queue.py` (derive-facings default: east is the
master, north/south derive — ARTPIPE_FACING_COHERENCE_1). Jobs in
`infrastructure/artpipe/pending/`; the daemon claiming one is success.

| id | canvas | facings | kind | palette anchor |
|---|---|---|---|---|
| `RM_Dhokkur` | **512** | south,east,north | creature GIANT, walking state | rain-slick obsidian |
| `RM_DhokkurDormant` | **512** | single | the same giant furled as an outcrop | rain-slick obsidian, ash-dusted |
| `RM_Julmox` | 256 | south,east,north | creature, herd | ash-and-bloom |
| `RM_Jossur` | 256 | south,east,north | creature, sky apex GROUNDED | scour-rust |
| `RM_Dhuvvox` | 256 | south,east,north | creature, flash-swarm | ember-fleck |
| `RM_DhuvvoxNodule` | 256 | single | sealed ash-nodule state | ash-glaze inverse |
| `RM_FloatstoneGarden` | 256 | single | growth (lace-walled globe) | opal-lace |
| `RM_Floatstone` | 256 | single | item + stuff color master | opal-lace |

**Named follow-ons (not commissioned now, deliberately):**
- `RM_Jossur` flight flip-book frames (whole-body directional flip-book,
  `flyingAnimationFramePathPrefix` shape, Sparrow template) — the flyer law says
  never block flight on frames; file after the grounded sprite is accepted.
- `RM_Julmox` sealed-squat single — only if FOUNDRY wires a dormant state graphic
  to the cycle phase.
- Floatstone custom wall atlas — only if the owner asks for the swirl grain in
  the built wall (§4's tint route ships first).
- Floatstone garden ripening variants — derives/retints of the master, dressing.

## 8. Handoff notes (defects/finds observed — nothing filed, per this brief)

- **`RM_CinderCrust` still has no art AND no ruled identity** — its texPath
  points at nothing (review-confirmed). The Q13 divergence ("regenerate the
  second copy's identity") must be written before its art is queued, or the art
  paints a plant nobody has designed. That identity is `FORGE_RULED_CONTENT_1`
  roster work; the art job should be filed the same sitting the identity lands.
- **Dhokkur dormant-state wiring has an exact in-repo precedent to read first:**
  the Cauldron commission's §7 note pattern applies — search `src/` before new
  C#; `CanBeDormant`/`WakeUpDormant` comps exist in the engine, and
  `RM_CompScriptedDieOff` (EnvironmentalHazards) shows the kit's comp shape.
- **The dormant dhokkur and the sealed dhuvvox nodule are STATE GRAPHICS** — two
  sprites per def, swapped by comp/mechanics state. If FOUNDRY defs them as
  separate ThingDefs instead (spawner-style), the job ids here still map 1:1;
  nothing about the art changes.
- **Terrain lane finding (§5) is worth keeping:** artpipe has never generated a
  terrain texture; every owned TerrainDef tints a vanilla surface. Anyone about
  to queue "terrain art" should read §5 before spending jobs.
- **Palette-diversity law is now carried verbatim in every style_notes** of this
  cast's CSV — five distinct anchors across six subjects (the floatstone pair
  deliberately shares one; they are one material family). If a rendered batch
  comes back tonally uniform anyway, that is a prompt-adherence defect to raise
  on the daemon channel, not a reason to re-rule the cast.


TASK: Give 8 to 12 recommendations that would make The Forge richer, more memorable and more distinct, filling the weakest of the nine marks first. Improve and extend what is ruled rather than restarting it. For each recommendation:
- **Name** and a one-line pitch
- What the player sees, hears and feels
- Which of the nine marks it lifts
- How it could be built in RimWorld 1.6 and a rough size (XML only / small C# / large C#)
- Why it belongs to THIS biome and no other

Then list your TOP 3 in rank order with one line of why each. Reply in Markdown, at most about 1500 words. Do not ask questions; do not modify any files.