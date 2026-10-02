# Week summary: gameplay mechanics & mod capabilities, 2026-09-18 to 2026-09-25

## New C# files by mod folder

- **src/RimMandrake/CreatureBehaviors** (58 new files)
- **src/RimMandrake/EnvironmentalHazards** (28 new files)
- **src/RimMandrake/WeepingStones** (18 new files)
- **src/RimUtinni/PropaneLakeMechanics** (15 new files)
- **src/RimMandrake/FeverWood** (13 new files)
- **src/RimStarWars/SWBestiary** (11 new files)
- **src/RimMandrake/SeaShores** (8 new files)
- **src/RimMandrake/Graffiti** (7 new files)
- **src/RimMandrake/DivingInteraction** (5 new files)
- **src/RimMandrake/OasisMaker** (5 new files)
- **src/RimMandrake/bridgetools** (4 new files)
- **src/RimStarWars/Bacta** (4 new files)
- **src/RimUtinni/UtinniPatches** (4 new files)
- **src/RimMandrake/FlowWorks** (3 new files)
- **src/RimMandrake/GelatinousSlime** (3 new files)
- **src/RimMandrake/Pyrelands** (3 new files)
- **src/RimMandrake/RustCathedral** (3 new files)
- **src/RimMandrake/BlueDesert** (2 new files)
- **src/RimMandrake/Contagion** (2 new files)
- **src/RimMandrake/ForsakenCrags** (2 new files)
- **src/RimMandrake/Miasma** (2 new files)
- **src/RimMandrake/PoisonForest** (2 new files)
- **src/RimMandrake/TerminalBiomes** (2 new files)
- **src/RimMandrake/TheForge** (2 new files)
- **src/RimMandrake/TheRot** (2 new files)
- **src/RimMandrake/TheSump** (2 new files)
- **src/RimMandrake/Wasteland** (2 new files)
- **src/RimMandrake/Webwork** (2 new files)
- **src/RimUtinni/ShipShields** (2 new files)
- **src/RimMandrake/LeaningScrub** (1 new files)
- **src/RimMandrake/LongShade** (1 new files)
- **src/RimMandrake/NightsideIce** (1 new files)
- **src/RimMandrake/Ninefold** (1 new files)
- **src/RimMandrake/Scarlands** (1 new files)
- **src/RimMandrake/Stillsand** (1 new files)
- **src/RimStarWars/JawaRules** (1 new files)

## New mods created this week (About.xml)

- `mandrake.rm.webwork` — RimMandrake: Webwork
- `mandrake.rm.warscar` — RimMandrake: Warscar (Scarlands folder)
- `mandrake.rm.thesump` — RimMandrake: the Sump
- `mandrake.rm.rustcathedral` — RimMandrake: the Rust Cathedral
- `mandrake.rm.miasma` — RimMandrake: the Miasma
- `mandrake.rm.contagion` — RimMandrake: The Contagion
- `mandrake.rm.theforge` — RimMandrake: The Forge
- `mandrake.rm.poisonforest` — RimMandrake: Poison Forest
- `mandrake.rm.bluedesert` — RimMandrake: Blue Desert
- `mandrake.rm.leaningscrub` — RimMandrake: Leaning Scrub
- `mandrake.rm.forsakencrags` — RimMandrake: Forsaken Crags
- `mandrake.rm.hostileflora` — RimMandrake: Hostile Flora
- `mandrake.rut.greentideraidant` — RimUtinni: Greentide Raid Ant
- `mandrake.rut.propanelakemechanics` — RimUtinni: Propane Lake Mechanics
- `mandrake.rm.wasteland` — RimMandrake: Wasteland
- `mandrake.rm.stillsand` — RimMandrake: Stillsand
- `mandrake.rm.longshade` — RimMandrake: Long Shade
- `mandrake.rm.nightsideice` — RimMandrake: Nightside Ice
- `mandrake.rm.terminalbiomes` — RimMandrake: Terminal Biomes
- `mandrake.rm.feverwood` — RimMandrake: Fever Wood
- `mandrake.rm.therot` — RimMandrake: The Rot
- `mandrake.rsw.graffitiimperial` — RimStarWars: Imperial Graffiti (Aurebesh/Imperial-cog stencil addon)
- `mandrake.rm.weepingstones` — RimMandrake: Weeping Stones (stocked-pool bestiary + cuisine)
- `mandrake.rm.oasismaker` — RimMandrake: Oasis Maker
- `mandrake.rsw.gualaarartoverride` — Gualaar Art Override (RSW art-only addon)
- `mandrake.rm.seashores` — RimMandrake: Sea Shores (coastal mutator + fishing)

**Total new mods this week: 26** (most are biome-mod-split scaffolds — About.xml + settings — per the biome-mod-split ruling; a handful ship real new mechanics, noted below).

## Closed items in the window (capability delivered)

New biome-mod-split scaffolds (About.xml + settings, per BIOME_MOD_SPLIT ruling — routine, not new mechanics):
FEVERWOOD, THEFORGE, TERMINALBIOMES (4 biomes in one mod: Scald/PropaneLake/TwilightSea/GreySea),
WASTELAND, LEANINGSCRUB, WEEPINGSTONES, STILLSAND, BLUEDESERT, POISONFOREST, WEBWORK, THESUMP,
NIGHTSIDEICE, RUSTCATHEDRAL, MIASMA, LANTERNDEEPS, SCARLANDS, THEROT, FORSAKENCRAGS, PYRELANDS,
CONTAGION, GELATINOUSSLIME, FLOODEDCANYON.

New player-facing MECHANICS / capabilities closed this window:
- INHABITED_STOCK_ONTO_MAP_AND_FATE_1 — a real feature (not a bugfix) for placing inhabited stock onto the map with a fate system.
- SLIME_STREAM_ROWS_1 — mucosal slime (red/green/white/yellow) now flows as viscous streams and pools, not static goo.
- LIQUID_SINK_DRAINAGE_1 — map-edge sinks now drain a canal automatically (live-proven).
- SCALD_DIVING_MOD_1 — Deep Diving: a whole new interaction letting colonists dive into deep water bodies.
- COLONY_VISIBILITY_BUILD_1 — a new visibility mechanic/build.
- DEEPS_FAUNA_MECHANICS (via DEEPS_FAUNA_VERDICTS_1 + commit log) — Grabber hold-and-crush grapple, Drinker fluid-sac bite+poison, Soulchime psychic stun/tame-soothe/shard-armor: three reusable creature-attack mechanics.
- DRUM_LURE_PREDATOR_BUILD_1 — a subsurface predator that lures prey with drumming, plus an egg-trap clutch mechanic.
- VENOMVINE_CONTACT_VENOM_BUILD_1 + VENOMVINE_PATHCOST_AND_FLYER_1 — a stationary plant that injects contact venom on touch, with its own pathing/flight interaction.
- SHRUBLAND_GIANT_ENRAGE_1 — a giant creature with a large-young life stage and parental "enrage on approach" behavior (protect the kids).
- DESERT_SHADE_WHALE_FILTERFEED_1 — a giant "shade whale" that filter-feeds through sand and seeds dung behind it (an ecology loop).
- DESERT_SHADE_GRID_KEYSTONE_1 — a ShadeAt MapComponent: the map now tracks and reacts to shade coverage as a real mechanic.
- EXTREME_DESERT_CAVERN_BEAST_1 — a cave-beast with eggs, a new predator archetype for caverns.
- DESERT_LEACHMOSS_BUILD_1 — leachmoss, a nutrient-racing plant mechanic for the desert.
- DESERT_STAGGERSEED_BUILD_1 — the staggerseed cycle plant (a plant with its own life-cycle mechanic).
- FEVERWOOD_TENTACLE_BESTIARY_1 — six distinct limb/tentacle attack types plus a "drive-off" ladder for Fever Wood creatures.
- FEVERWOOD_DIANOGA_PRISON_1 — a prison mechanic built as a tank (submerged holding), not a normal pen.
- FEVER_WOOD_MECHANICS_1 — Fever Wood's own C# kit; first "spike" attack pass landed.
- GREATBOLE_HARVEST_LADDER_1 — a tiered harvest ladder + fruit economy for the giant greatbole tree, contested by grubs that fight back.
- WASTELAND_BRINE_BATTERY_CREATURE_1 / _DISCHARGE_1 — a creature that acts as a living "brine battery," including an ion-gradient electrical discharge attack.
- WASTELAND_EXCRETOR_BEZOAR_1 — an excretor herd creature that produces a harvestable metal-salt bezoar.
- WASTELAND_RADIOTHERMAL_SOLITARY_1 — a radiothermal creature (heat + spacing behavior; C# partly owed).
- PROPANE_LAKE_PIPE_MECHANICS_1 — gas vents, a pipe-rupture network, a saturation tracker, V-wake agitation, and a "heist" raid built around a propane lake.
- WATER_TRUCE_RETRIBUTION_1 — breaking an in-game truce at a water source makes the biome itself fight back.
- OASIS_MAKER_MACHINES_1 / OASIS_MAKER_BUILD_1 — ancient machines that slowly grow new oases over time.
- STOCKED_POOL_BUILD_1 / WEEPING_STONES_FISH_HUSBANDRY_1 — fishing reframed as gardening: an 8-row stocked-pool bestiary, a doubt-meat mood economy, and cuisine recipes.
- GREENTIDE_YEARNING_FRUIT_FILTH_1 — a fruit whose filth mechanically disperses its own seeds.
- SLIME_GENE_ARCHIVE_BUILD_1 — a gene-archive machine now serves real xenogenes instead of placeholders.
- TITANOSLIME_PERMANENT_GROWTH_LIVE_1 — a titan slime that grows permanently larger over time (live-verified).
- NINEFOLD_ENGINE / loudness+front (commit log) — factions' "loudness" now derives a shifting front line that can flip mid-game on a big enough event.
- JAWA_MESS_IMMUNITY_1 — Jawa colonists are now immune to being bothered by mess/filth.
- FLOWWORKS_LIQUID_FACES_1 — every liquid in the flow system now renders with correct directional faces.
- BRIDGE_SELECT_NONCOLONIST_PAWN_1 — (tooling) a direct way to select and cast abilities on non-colonist pawns.
- BACTA_SIDE_ITEMS_1 — a bacta-tank kit gets satellite content: a medical droid, field consumables, and trader wiring.
- GOO_BOOM_COMMISSION_1 / VQE_ANCIENTS_CURATION_1 — a big reskinned "boom" creature kept for an assailant dungeon; ancient VQE creatures curated in.


## Notable mechanics (detail)

1. **The Greatbole harvest ladder** — the giant greatbole tree has a threshold system: mine under 40% and it just heals; push past 40% and "The Great Shaking" drops fruit and grubs but staggers your pawns; push to 60% and it seals/crushes itself back to full; cross 70% and "the catastrophe" collapses a 50-cell radius forever, altering the map permanently for a huge one-time yield. Grubs actively contest the harvest.

2. **Water Truce Retribution** — fight anyone at a water source (even defend yourself against raiders) and the local wildlife turns on the aggressor. Built on a real engine capability (RimWorld already tracks per-hit "who started it" via `DamageInfo.Instigator`/`InstigatorGuilty`), so self-defense doesn't trigger it — only the instigator does.

3. **Deep Diving** — a genuine dive-site mechanic for the Scald's boiling sea: colonists can now dive to the depths of a body of water that used to be pure hazard, without needing a full swimming-pawn simulation (the depths are a site, not a creature).

4. **Propane Lake pipe network** — self-igniting gas vents that build up pressure until pumped, a rupturing pipe network with on-map manual shutoffs, a saturation tracker that lingers in caverns, and a raid built specifically around exploiting a saturated lake (enemies bring non-flammable gear and try to trigger a heist).

5. **Deeps creature mechanics (Grabber / Drinker / Soulchime)** — three new bite/attack archetypes: a pincer "grapple" that gets harder to escape the longer it holds; a fluid-sac drinker that either feeds off you or poisons warm-blooded victims; and a psychic "soulchime" that stuns wild creatures within range, soothes its own tamed handlers, and grows a shard-armor shell.

6. **Oasis-maker ancient machines** — placeable ancient treasure buildings that slowly grow a real oasis (terrain conversion) around themselves over a long time when sited correctly near shade and rock, guided by a green/red placement overlay like a terraforming pump — meant to be quest-obtainable or sabotage-able.

7. **Stocked Pool fish husbandry** — reframes fishing as gardening: an 8-row stocked-pool bestiary with its own "doubt-meat" mood economy and dedicated cuisine recipes, so tending a fish pool becomes a food-production loop in its own right.

8. **Ninefold loudness/front system** — factions now have a derived "loudness" from their in-game actions, the loudest holds priority over a shared ship system, and violent-enough events can flip who's "in front" mid-game, not just at landing.


