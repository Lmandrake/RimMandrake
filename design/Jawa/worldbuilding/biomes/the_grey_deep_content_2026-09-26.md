# The Grey Deep — content drop, 2026-09-26

_The owner's Grey Sea content drop, delivered at the bench 2026-09-26, captured by a
BENCH design-capture pass the same day. This document is a CAPTURE, not a design: it
structures what he said and adds build notes. It amends the frozen sheet
`design/Jawa/worldbuilding/biomes/the_grey_deep.md` under that sheet's own rule —
**amendments add detail; they never change a ruling** — and §8 below flags the two places
where the drop and the sheet may disagree, for him to settle at a sitting._

## 0. Provenance

| | |
|---|---|
| **author** | the owner, at the bench, 2026-09-26 |
| **captured by** | BENCH (design capture pass, same day) |
| **status** | additive amendment to the FROZEN Grey Deep sheet; nothing here re-rules the sheet |
| **what is his** | every block quote, every *italic quoted phrase*, and the five full flora specs in §4 and the Brine Elders paragraph in §7.1 — reproduced **verbatim, unedited** |
| **what is ours** | anything marked **BENCH NOTE**, the section headings, the "structured" reading in §7.2, §8–§10 entirely |

**Reading rule:** if a sentence is not in a block quote, not in quotation marks and not
inside a **BENCH NOTE**, it is connective prose written by BENCH from his words and
carries no more authority than a BENCH NOTE does. When in doubt, the quote wins.

**Where the Grey Sea stands in the build, MEASURED by BENCH 2026-09-26** (do not
re-derive):

- The sea floor is a generated **pocket map** —
  `src/RimMandrake/DivingInteraction/Defs/MapGeneration/RM_SeaDiveGenerators.xml`,
  `RM_SeaDiveGenerator_GreySea` (`pocketMapProperties/biome` = `RM_GreySea`,
  temperature 12, mutator `RM_SeaFloorHabitat`; gensteps `ElevationFertility`,
  `RM_SeaFloorTerrain`, `RM_PlaceSeaDiveExit`, `RM_SeaFloorFauna`, `Animals`,
  `RockChunks`, `Fog`). It is **not** a BiomeDef of its own: the floor's cast is read off
  `RM_GreySea`'s `<wildAnimals>`.
- The floor's one terrain is the shared `RM_SeaFloorGround` ("sea floor sediment",
  placeholder Sand art, `src/RimMandrake/DivingInteraction/Defs/TerrainDefs/RM_SeaFloorGround.xml`),
  whose own header says *"per-sea floor dressing … is follow-on content."* This drop IS
  the Grey's floor dressing.
- Floor cast BUILT (`src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Races/RM_GreySeaFauna.xml`,
  `RM_SeaBeasts_Invented.xml`): `RM_Reefback` (the crusted giant, bodySize 32),
  `RM_Fessk` (**this IS the sheet's ossuary shrimp**), `RM_Otheska`, `RM_Sorruth`,
  `RM_Essarn`.
- Catch BUILT: 9 `fishTypes` entries on `RM_GreySea`, `maxFishPopulation` 120, rare table
  `RUT_RareGreyCatches` (`RUT_SaltCameo`, a hessal bed, a silver ring).
- **NOT built:** zero plants, zero own weather (the def carries vanilla `Clear`/`Fog`/`Rain`
  only), zero own terrain, zero buildings, zero incidents, zero minerals — **and the
  pillars exist in no def of any kind**, though four creature descriptions reference them.
- The Grey Sea's liquid is `RM_Liquid_Brine` (`RM_Body_GreySea`,
  `src/RimMandrake/FlowWorks/Defs/LiquidTypes/`), terrain suite `RM_WaterBrineShallow` /
  `RM_WaterBrineDeep`. The saturated-plus **pool** grade the sheet asks for
  (`LIQUID_TYPES_MOD_1` cross-flow) does not exist yet.

## 1. Reference images

He supplied four. They are in the repo under
`design/Jawa/worldbuilding/reference/grey_sea/`. Each is cited below by path, with his
words on what it is for, and a BENCH reading of what an artist or def-author should take
from it.

### 1.1 `design/Jawa/worldbuilding/reference/grey_sea/01_pillar_forest_underwater.png`

> *"A wonderland of odd pillars and formations."*

A diver hanging in hazy blue-green water among a forest of tall, encrusted, near-vertical
columns rising out of frame; the floor is rubble and litter, lit from far above. **For:**
the pillar forest — the sheet's unbuilt PILLAR-MASON and its pillar-to-pillar navigation
law (`the_grey_deep.md` §4). This is what the floor of the pocket map should read as:
verticals in murk, and a diver very small between them.

**BENCH NOTE:** the reference is bluer and clearer than the sheet's palette allows
(*"grey-green dimness fading to blind"*, §9). Take the *forms* — column spacing, the
encrusted-not-smooth surfaces, the rubble floor — and not the colour.

### 1.2 `design/Jawa/worldbuilding/reference/grey_sea/02_crusted_white_shoreline.png`

> *"the crusty whiteness that should be on every Grey Sea shoreline"*

Lumpy, cauliflower-textured white salt crusts grown over red-brown stones at a flat
waterline, under a pale overcast sky, the sea a dull steel colour. **For:** every Grey Sea
shore, above water. The crust is a *growth* on the stones — knobbly, popcorn-like — not a
flat pan.

**BENCH NOTE:** this is the SURFACE shore, so it lands on `terminator_sea.md`'s ground
(the sheet already has *"the ground is salt crust, white, and it takes a footprint"*) and
on `RM_SeaShoreExtension` (`mandrake.rm.seashores`, already wired on `RM_GreySea`). The
existing `RUT_Jawa_SaltCrust` terrain (`src/RimUtinni/UtinniPatches/Defs/TerrainDefs/JawaSaltCrust.xml`)
is a *flat evaporite pan* by its own description — the right family, the wrong texture for
this image. See §2.6 and open question Q4.

### 1.3 `design/Jawa/worldbuilding/reference/grey_sea/03_salt_domes_mushroom_forms.png`

> *"there should be salt-domes a little like mushrooms growing, strange shapes everywhere"*

Bulbous, cream-white salt mounds — some conical, some capped and overhanging like
mushrooms, some flat-topped terraces behind — rising out of milky turquoise water, with a
dry salt-flat and bare hills behind. Surfaces are granular, almost beaded. **For:** the
salt-dome formations, both as sea-floor features and where they break the surface at the
shore. The overhang on the cap is the "mushroom" he means.

### 1.4 `design/Jawa/worldbuilding/reference/grey_sea/04_salt_chimneys_brine_vents.png`

> *"real 'salt chimneys' shooting up from the sea floor, shooting out murky white
> super-brine"*

A five-panel plate of underwater salt chimneys: (a, b) single pale columns with flared,
plate-like tops in green water; (c) a chimney built of visible cubic crystal blocks;
(d) a cluster of stubby rust-brown-and-white chimneys in blue haze; (e) a dense thicket of
fluffy white columns. Some are actively venting a cloudy plume. **For:** the salt-chimney
building/feature and the "murky white super-brine" plume it emits — and the *cubic*
crystal habit in panel (c) is the same habit his crystalline flora is built from (§4).

## 2. Terrain and formations

Six things, all his, in the order he gave them.

### 2.1 Salt chimneys

> **Salt chimneys** on the sea floor, venting murky white super-brine.

Reference: image 04 (§1.4). A vertical feature on the pocket-map floor that emits a
plume. The plume is the same "super-brine" the pools are made of (§6), so a chimney is a
pool's vertical cousin.

**BENCH NOTE (build shape, not a ruling):** a `ThingDef` building, natural-spawned by a
scatterer genstep on the Grey floor only, with an emitter effect (the Scald already ships
`RUT_ScaldVent` — `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Buildings/RUT_ScaldVent.xml` —
as a venting floor feature; read it before writing a new one). Whether a chimney's plume
carries the §6 crystallisation defence is open question Q2.

### 2.2 Huge harvestable salt crystals

> **Huge salt crystals on the sea floor, harvestable and rather valuable.**

A mineable/harvestable resource node. "Rather valuable" is his phrase — this is not
bulk salt; it is a treasury item, consistent with the sheet's §7 *"soluble minerals …
the planet's evaporite treasury"*.

**BENCH NOTE:** no salt *mineral* exists anywhere in `src/` yet (MEASURED: the only salt
defs are `RM_DeltaSalt`, `RM_SeepSalt` (Miasma/Weeping Stones goods), `RUT_SaltCameo`
(a Grey rare catch), and the `RUT_Jawa_SaltCrust` terrain). The cleanest engine shape is
the Odyssey `SolidIce` pattern — a `RockBase`-parented mineable with its own atlas,
`mineableYieldWasteable false`, `biomeSpecific true` — yielding a salt-crystal item.

### 2.3 Coloured salts as cooking ingredients

> **Different colours of salt make great RimCuisine ingredients.**

**BENCH NOTE — RimCuisine is NOT in the mod list.** MEASURED 2026-09-26 against the newest
full-list snapshot (`infrastructure/state/modlists/ModsConfig_full_plus_gelatinousslime_2026-09-21.xml`,
620 active): the only packageId matching `cuisine` is **ours** — `mandrake.rsw.cuisine`
(`src/RimStarWars/Cuisine/`, "RimStarWars: Cuisine", the mod `high_cuisine_deep_design.md`
names as the home of all later cooking waves). The live `ModsConfig.xml` at the time of
measurement held an 11-mod test list and so proves nothing either way about the full
list. ⇒ Read his sentence as *"great ingredients for our cuisine mod"*: the coloured
salts are `RM_`-tier items in the Grey Sea's own mod, and `mandrake.rsw.cuisine` consumes
them via `MayRequire`-guarded recipes. No hard dependency in either direction. Nothing
here should reference a workshop RimCuisine packageId.

The colours he named for the crystal *flora* are **pink, violet and amber** (§4.1) — the
salt palette should be the same three, plus white, so that ingredient and plant read as one
mineralogy. (BENCH inference from his words; not a ruling.)

### 2.4 Salt domes

> **Salt domes like mushrooms growing, strange shapes everywhere.**

Reference: image 03 (§1.3). Rounded, capped, sometimes overhanging mounds — a *second*
formation family beside the pillars, squat where the pillars are tall. "Strange shapes
everywhere" is a density instruction: the Grey floor is not empty sediment with a few
columns on it; it is crowded with mineral forms.

### 2.5 The pillar wonderland

> **A wonderland of odd pillars and formations.**

Reference: image 01 (§1.1). 🔑 This is the content behind the frozen sheet's **pillar-mason**
(§4: *"a crystal-binding film that builds — mineral columns rising from the floor toward
light they never reach"*) and its navigation law (*"all travel below is pillar-to-pillar"*).
The sheet named the organism; this drop supplies what the organism's work looks like.

**BENCH NOTE:** `GREYSEA_ANCHOR_CREATURES_1` already scopes the pillar-mason as *"a
navigation system, not a creature encounter … terrain/structure generation and a
navigation affordance."* The pillar is therefore a **building/feature def** placed by the
floor generator, and the mason is its fiction, not a `PawnKindDef`. `RM_Sorruth`'s
description already says it *"grazes the film off the Grey Sea's pillar-mason columns"* and
`RUT_SaltCameo` is *"jacketed in pillar-mineral"* — the pillar has been referenced by four
defs and defined by none. Building it closes that gap.

### 2.6 The crusted shoreline

> **Every Grey Sea shoreline carries the crusty whiteness** of image 02.

Reference: image 02 (§1.2). This is a surface-and-shore statement and so belongs to
`terminator_sea.md`'s domain (which the Grey Deep inherits). "Every" is a coverage rule:
no Grey Sea shore tile without the crust.

**BENCH NOTE:** the natural carrier is `RM_SeaShoreExtension` (`mandrake.rm.seashores`),
already declared on `RM_GreySea` — a Grey-specific shore terrain with the image-02 texture,
distinct from the flat `RUT_Jawa_SaltCrust` pan. Whether it also dresses the shore with
dome/crust *things* (image 03's mounds breaking the surface) is open question Q4.

## 3. Fauna

One sentence, his:

> **Abundant shrimp, clam and mussel equivalents lurk among the formations, picking
> through what organic matter rains down from the surface.**

Three things it says: (1) *equivalents* — invented, never Earth shrimp/clam/mussel by
name or read (sheet ban 6 and the standing recognisability ban both hold); (2) *abundant* —
this is the small, common, sessile-or-slow layer of the floor, the base of the food chain;
(3) *what rains down from the surface* — a marine-snow economy, which is also what the
§5 salt-snow weather and the §4 detritus-harvesting flora feed on.

**BENCH NOTE — read before building any of these as new:**
- `RM_Fessk` **is** the man-sized ossuary shrimp — it is not one of these; these are the
  small abundant layer beneath it.
- `RM_Sorruth` (a fist-sized mineral-caked snail on the pillars) and `RM_Otheska` (a flat
  shelled detritivore on the statuary) already occupy the "shelled thing lurking among the
  formations" niche. The clam/mussel equivalents may be **one or two more sessile defs**, or
  may be a case where the answer to *"do we already have one?"* is *sorruth and otheska*.
  Open question Q5.
- ⚠️ *"Abundant"* meets the inherited **no-schools/no-swarms** ban (`the_grey_deep.md` §6
  ban 2; `terminator_sea.md` §6). Abundance by *many single spawns at moderate commonality*
  (like `RM_Sorruth`'s `wildGroupSize 1~3`) is inside the law; a swarm def is not. Flagged
  in §8.
- A donor `RSW_Yobshrimp` exists but the roster already ruled it the wrong scale
  (`rosters/the_grey_sea.json`, `new_defs` row 2) — and it is a Star Wars canon creature, so
  it could only ever live in the Utinni layer anyway.
- Each new floor species owes two defs if it is catchable (floor resident + `*Catch`), per
  the standing sea rule and the `RM_Essarn` ↔ `RM_EssarnCatch` precedent.

## 4. Flora — the crystalline idea

This is the centre of the drop. The Grey floor's plants are **crystalline**: living tissue
that force-aligns the salt around itself into geometric armour. Seven forms — two short,
five specified in full. All are his; the five full specs are reproduced verbatim as their
own subsections and must not be paraphrased in any derived def without going back to the
quote.

**BENCH NOTE — the two things every def author must hold:**
1. 🔴 His one aesthetic rule, verbatim: *"marred slightly, don't make them too perfect or
   they look manufactured."* Every crystal form is chipped, clouded, asymmetric somewhere.
   This goes into every art brief for this biome.
2. ⚠️ The frozen sheet's ban 4 — *"No light-source flora, no bioluminescent dressing …
   the murk stays blind"* — and `terminator_sea.md`'s bans on heliotropism and
   open/close behaviour. Nothing below emits light; the kelp and the fan palms *use*
   filtered light and the Brine Crown *retracts* — see §8 for whether retraction counts
   as "opens and closes".

MEASURED: **no crystal plant exists in any Grey def**, and `RM_GreySea` ships no
`<wildPlants>`. The Lantern Deeps' `RM_DeepFlora.xml` (ten `RM_` plants for another
pocket-floor biome) is the closest shipped pattern for authoring a floor flora set.

### 4.1 The two short ones

**Crystalline cubic sculptures** — his words:

> **Beautiful crystalline cubic sculptures**: green plants growing INSIDE the crystal,
> using proteins to force-align the salt outside them as armour. **Pink, violet and amber
> geometric solids** sitting on the sea floor with striking natural beauty — *"marred
> slightly, don't make them too perfect or they look manufactured."*

**Sphere plants** — his words:

> **Sphere plants** propped up by radial thin spines surrounding them, both armour and
> weaponry — *"like a huge version of a microscopic creature."*

**BENCH NOTE:** the cubic sculptures are the *general* form (and the Crucible Pod, §4.6,
is its fully-specified case: a lobed sphere in a cubical cage); the sphere-with-radial-
spines is a radiolarian/diatom read at macro scale, and its "weaponry" makes it the
second of two plants here that hurt (the Brine Crown, §4.3, is the other). Whether
"weaponry" means a contact-damage plant is open question Q6.

### 4.2 Glass Veil Kelp

> **Glass Veil Kelp** — A plant-equivalent that grows in tall curtain-like stands over
> trenches and brine rivers. It anchors deep and grows long flexible sheets of transparent
> tissue. Along every strand it precipitates cubic crystal beads and razor-thin plates,
> making each frond into a hanging chain of salt prisms. The living photosynthetic cells
> lie in thin shadowed channels behind the crystals, using filtered light. When currents
> move through them, the crystal-laced veils clatter softly. Entire forests shimmer like
> hanging bead curtains in a palace ruin. Star Wars vibe: elegant, eerie, slightly
> ceremonial.

**BENCH NOTE:** *"over trenches and brine rivers"* — the spec places it where the floor
has relief and where brine *flows*, which implies a brine-river terrain/feature the pocket
map does not yet generate (open question Q3). "Tall … stands" on a 2-D map reads as a tall
`drawSize`, multi-cell-looking plant; the sheet's silhouette language is *"verticals in
fog"*, so this is on-theme. The "clatter" is a sound cue (`soundAmbient` is not a plant
field in vanilla — UNMEASURED whether any shipped plant carries ambient sound; treat as
art-direction text unless someone measures it).

### 4.3 Brine Crown Anemoflora

> **Brine Crown Anemoflora** — A plant-animal ambiguous organism that resembles an anemone
> made of crystal thorns. A squat base anchors it into the bottom. Around the living core
> rises a crown of long cubic spines grown from salt and other evaporites. Between these
> spines hang fleshy, dark membranes that capture both light and dissolved nutrients. When
> the salinity shifts, the membranes retract deep into the "crown," leaving only a deadly
> mineral porcupine behind. Small bottom-dwelling grazers get impaled or trapped in salt
> pockets around it, and decay then feeds the plant. So it is not purely photosynthetic;
> it's partly a detritus-harvester.

**BENCH NOTE:** two states (membranes out / membranes retracted) keyed to *salinity
shifts* — the natural in-game trigger is the §5 salt-snow weather or a nearby chimney
venting. "Deadly mineral porcupine" that impales small grazers is a contact-damage plant,
the same shape `RM_Venomvine` already ships in `mandrake.rm.environmentalhazards`
(`src/RimMandrake/EnvironmentalHazards/Defs/ThingDefs_Plants/RM_Venomvine.xml`) — read that
before writing a new harm mechanism. It should hurt the §3 shrimp/clam/mussel equivalents,
which are exactly the "small bottom-dwelling grazers" it names. See §8 on the
open/close ban.

### 4.4 Mosaic Fan Palms

> **Mosaic Fan Palms** — Broad fan-shaped bottom flora that open toward weak filtered
> light from above. Their "leaves" are not continuous tissue. Instead they are arrays of
> small square crystal panes, each grown at slightly different angles. Beneath each pane
> is a thin layer of pigmented living tissue. The fan looks like a tiled mosaic or
> ceremonial shield. Some species can rotate portions of the fan by swelling internal
> canals, changing how light is directed inward. These would look very artistic and
> strongly fit that psychedelic / ritual / alien-arid aesthetic.

**BENCH NOTE:** "open toward weak filtered light from above" — on a pocket map the light
is directionless, so this is pose, not heliotropism (the palm does not *track*; it is
built facing up). The pane-rotation is an art/description detail, not a mechanic, unless
he wants it as a growth-rate modifier. "Some species" invites two or three colour/pattern
variants of one def (pink/violet/amber, matching §4.1) rather than three defs.

### 4.5 Salt Chimney Vines

> **Salt Chimney Vines** — These grow only around warm mineral seeps or chemical vents in
> the saline depths. They begin as creeping mats. Once they find a seep, they climb it by
> growing spiraled cubic bracing around the chimney. Their main energy source is a
> combination of dim-light harvesting and chemosynthetic symbionts. Delicate inner tissues
> remain hidden in moist protected channels inside the mineral spiral. From outside they
> resemble white angular vines twining around black vent rock. This gives a more
> industrial, harsh, "mustafar-meets-salt-sea" feel.

**BENCH NOTE:** this plant is *bound* to §2.1's salt chimney — it spawns only adjacent
to one, so the chimney must exist first (build order, §10). The engine's adjacency
mechanism for "grows only next to X" is UNMEASURED here; `mandrake.rm.livingregrowth`-
style map components already gate growth on terrain (see the greatbole's
`RM_MapComponent_LivingRegrowth` precedent noted in `CLAUDE.md`), so a
"spawn only within N cells of a chimney" rule is a small C# genstep or a
`plant.wildBiomes`-free scatter tied to the chimney's own placement. ⚠️ *"chemosynthetic
symbionts"* brushes `terminator_sea.md` ban *"no cold gas vents … those belong to the
poison forest"* — but these are **warm mineral seeps**, and the ban is on cold gas
chemistry, not on chemosynthesis as such. Flagged in §8 for the record, position: no
contradiction.

### 4.6 Crucible Pods

> **Crucible Pods** — Round bottom-dwelling plants that use salt architecture as
> incubators. The main body is a lobed sphere embedded in sediment. It grows a thick
> cubical crystal cage around a central chamber. Inside the chamber are its photosynthetic
> and reproductive organs. When mature, it dissolves one face of the cube and releases
> drifting seed-cysts or buoyant larvae. Juveniles settle in cracks between salt blocks
> and begin growing their own tiny geometric shells. This gives a lifecycle that feels
> alien and visually memorable.

**BENCH NOTE:** three visible growth stages map straight onto vanilla plant growth
graphics (sealed cube → cube with one face dissolved → empty cage), which is exactly what
`<graphicData>` + `plant.leaflessGraphic`/growth-stage art can carry with no C#. The
"juveniles settle in cracks between salt blocks" line is the reproduction rule — its
`wildClusterRadius`/`wildClusterWeight` should favour spawning beside §2.2 crystals and
§2.4 domes. It is the fully-specified case of §4.1's "cubic sculptures".

## 5. Weather

One weather, his:

> On the sea floor, a special weather event: **precipitating salt crystals, like snow.**

It is *on the sea floor* — a pocket-map weather, not a surface one. Salt crystallising out
of the water column and drifting down: the biome's one visible motion besides the pools
breathing, and (BENCH inference) the natural trigger for the Brine Crown's retraction
(§4.3) and the feed for the shrimp/clam layer (§3).

**BENCH NOTE — the pattern is already shipped, read it first.**
`src/RimMandrake/Pyrelands/Defs/WeatherDefs/AshFall.xml` (`RM_FE_Weather_AshFall`, "ash
that blows like snow") documents in its own header, with RimSage line cites, exactly how
to make a falling-particle weather out of vanilla's `WeatherOverlay_SnowGentle` by
setting the weather's own `<overlay>` colour — and why `snowRate` must stay 0 (it would
write white snow into `map.snowGrid` and melt it). For salt the overlay colour is
off-white, so this is the one case where the borrowed snow sheet is almost the right
colour already. Accumulation, if wanted, would be a filth or a terrain tint via a map
component as the Pyrelands does (`RM_FE_Filth_LooseAsh`), never `snowRate`.

⚠️ `terminator_sea.md` §6 bans *"no rain, no thunderstorms, no snow, no ice"* — for the
SURFACE. This weather is on the floor, is salt not water, and the sheet's own §9 already
has *"the crackle of growing crystal"* and *"scrape-dust falling"*. Flagged in §8;
position: additive, not a contradiction. Note also that `RM_GreySea` currently carries
vanilla `Rain 4` in `baseWeatherCommonalities`, which IS against the surface ban and
predates this drop — a defect to fix in the same pass, not part of the drop.

MEASURED: zero own WeatherDefs in the Grey Sea today; the only terminal-sea weather is the
Scald's `RUT_ScaldSteam`.

## 6. Brine pools and the crystallisation defence

He called the brine pools *"the center of the weird mechanisms."* Three sentences, his:

> **Brine pools and the creatures near them have a unique defence: they squirt out a
> protein shower causing ultra-rapid crystallisation around the player, freezing them in
> place and possibly smothering them** — *"just like being frozen in ice already exists in
> the game."*

> **Touching a brine pool directly does the same thing.**

> ⇒ **Loot within the pools is ultra-protected until the player figures out how to get
> at it.**

So: one mechanism, three triggers (a pool-creature's squirt · direct contact with a pool ·
by implication, the Elders' pool in §7), one consequence (the pawn is jacketed in salt
where they stand, cannot move, and may suffocate), and one economic result (the pools'
contents are a locked treasury with a key the player has to *discover*).

This is the frozen sheet's §3 *"everything that enters dies; everything that dies there
keeps"* and §6 ban 1 *"no survivable brine-pool entry … harvest happens at their
shores"* turned into a mechanism — and it is the same mechanism that made the statuary
(§8 of the sheet). The drop does not contradict the sheet; it explains it.

**BENCH NOTE — what "frozen in ice already exists in the game" resolves to. MEASURED
2026-09-26 against the installed 1.6 `Data/` tree and the decompiled engine via
RimSage.**

- **For THINGS (loot, structures, bodies): yes, it exists, and it is the right shape.**
  Odyssey's `SolidIce` (`Data/Odyssey/Defs/ThingDefs_Misc/Stone_Various.xml`,
  `ParentName="RockBase"`, 240 HP, *"can be mined through with relative ease"*,
  `leaveTerrain Ice`) plus the encasing routine
  `GenStep_FrozenRuins.EncaseStructuresInIce` (`Source/RimWorld/GenStep_FrozenRuins.cs`,
  a `GenMorphology.GenerateNaturalPatch` of `SolidIce` over `Ice` terrain around the
  structure rects), the `SolidIce_Loot` prefab (`Data/Odyssey/Defs/PrefabDefs/AncientPrefabs.xml`)
  and `TileMutatorWorker_AncientRuins_Frozen`. That is exactly "loot ultra-protected
  until you dig it out". ⇒ A **salt** twin of `SolidIce` (call it the jacket mineral —
  defName UNMEASURED/unassigned) with a `GenMorphology` patch around pools and around the
  statuary gives the sheet's *"jacketed salvage … chiseled free"* and this drop's
  *"loot within the pools is ultra-protected"* with no new engine mechanism at all.
- **For PAWNS: no vanilla hediff freezes a living pawn in place.** MEASURED: no
  `HediffDef` in Core/Royalty/Ideology/Biotech/Anomaly/Odyssey has a defName or label
  containing frozen/encased/immobilised/petrified (RimSage `search_defs frozen` returns
  only Odyssey layout/landmark/genstep defs and a `HairDef`). The nearest vanilla shapes
  are the **Consciousness-pinning** hediffs (`Anesthetic` setMax 0.01, `PsychicShock`/
  `PsychicComa`/`CatatonicBreakdown` setMax 0.1 — all `Core/Defs/HediffDefs/Hediffs_Global_Misc.xml`)
  and Anomaly's `Digested` (a pawn held inside another thing). ⇒ The pawn-side of the
  defence is **a new hediff of ours** (Moving → 0, a smother/asphyxiation severity ramp,
  cured by chiselling — the "figures out how to get at it" key applied to a colonist), or
  the pawn is *replaced* by a `SolidIce`-style jacket thing containing them (the
  `Digested`/`SolidIce_Loot` shape). Which of the two is open question Q1.
- **Not this:** `RM_BrineShock` (`src/RimMandrake/Wasteland/Defs/HediffDefs/RM_BrineShock.xml`)
  is a Wasteland drazz's electrical jolt and passes in hours — the Elders' *discharge* (§7)
  is its cousin, but the crystallisation is not.

**BENCH NOTE — what the pools need that does not exist:** a pool **terrain** of the
saturated-plus grade (the sheet's `LIQUID_TYPES_MOD_1` cross-flow; today the Grey has only
`RM_Liquid_Brine`'s shallow/deep suite), with its own "shore" cells where the harvest
happens; a contact trigger on that terrain (touching = the defence); and the loot-in-
jacket placement around and under it. The pool creatures that squirt are new defs — he
did not name them; the Elders (§7) are the extreme case, but *"the creatures near them"*
is plural and general. Open question Q2 covers the chimneys.

## 7. The Brine Elders

### 7.1 Verbatim

His paragraph, entire and unedited:

> The Brine Elders are an impossibly ancient native species of colossal branching
> salt-crystal organisms, each rising from the deepest ultra-dense brine pools as a trunk
> five to ten cells wide before dividing into massive cubic and faceted limbs that climb
> upward into the lighter saline ocean. Their bodies are living ionic lattices: they
> accumulate charge directly from the chemically extreme brine that sustains them and can
> release it in blinding area-wide discharges powerful enough to stun living creatures,
> disable droids, collapse shields, and cripple nearby ships. They cannot leave these
> abyssal pools—the ultra-brine is both their habitat and their metabolic substrate—which
> has confined them to scattered deep basins for geological ages and preserved them
> through catastrophes that erased younger civilizations. Their awareness is equally
> ancient but profoundly nonhuman: they remember the arrival of the Reshapers, the changes
> wrought on the world, and events predating nearly every extant culture, yet they
> interpret history through chemistry, pressure, charge, mineral deposition, biological
> composition, and disturbance rather than names, politics, or technology. They can
> deliberately alter the mineralization of their pools, dissolving entire blocks of
> crystallized seafloor to uncover ancient mummified bodies, wreckage, or artifacts, or
> violently ejecting long-entombed objects upward from the brine as part of an exchange.
> What they value above all is novelty: a newly encountered life form, corpse, xenotype,
> tissue, mineral, or unfamiliar material may be extraordinarily valuable once, then
> nearly worthless thereafter because the Elder has already incorporated its chemistry
> into memory. Technology fascinates them but is conceptually opaque; they recognize
> unusual materials, energy states, and structures more readily than intended function.
> In return, they can sometimes modify matter in ways no conventional craftsman can—for
> example growing a resonant storage crystal that passively increases the effective
> capacity or charge retention of all nearby batteries—and they may release singular
> treasures accumulated over millennia, typically only one example of each because
> duplication held no value to them: a functional lightsaber sealed since the Rakatan
> era, an intact pre-Republic navigation core, an unknown droid brain preserved in salt,
> a one-of-a-kind alien weapon whose operating principle is no longer understood, a sealed
> biological relic from an extinct species, or some beautifully useless artifact whose
> significance only becomes apparent much later. Their trade therefore feels less like
> commerce than negotiating with a geological intelligence that has spent tens of
> thousands of years quietly collecting one specimen of anything genuinely new.

### 7.2 Structured

Every line below is his sentence re-filed under a heading; quoted fragments are exact.
BENCH adds nothing except the marked notes.

**What it IS.** *"an impossibly ancient native species of colossal branching salt-crystal
organisms"*, one per pool: *"rising from the deepest ultra-dense brine pools as a trunk
five to ten cells wide before dividing into massive cubic and faceted limbs that climb
upward into the lighter saline ocean."* A body that is *"living ionic lattices."*
— BENCH NOTE: *"five to ten cells wide"* is a map-scale instruction: the trunk is a
multi-cell building-sized thing, the limbs reach up out of the pocket map's "floor" toward
the surface sea. In engine terms this is a large multi-cell `ThingDef` (a building or a
`RockBase`-family thing) with a comp, not a `PawnKindDef` — it *"cannot leave"*, has no
locomotion and trades from where it stands. The largest shipped precedent for a
building-sized living thing with its own map component is the greatbole
(`RM_Greatbole`/`RUT_GreatboleHeartwood`/`RUT_GreatboleCore` — three defs, say which).

**The discharge.** *"they accumulate charge directly from the chemically extreme brine
that sustains them and can release it in blinding area-wide discharges powerful enough to
stun living creatures, disable droids, collapse shields, and cripple nearby ships."*
— BENCH NOTE: four targets, each a real engine surface: stun (a hediff; `RM_BrineShock`
in the Wasteland is the small cousin — Consciousness −0.3, passes in hours), droids
(mechanoid/droid `Pawn` kinds — an EMP-class effect), shields (shield belts — vanilla
`EMP` damage already breaks them), ships (Odyssey gravships — UNMEASURED what "cripple" can
mean to a gravship in engine terms; see Q8). Is it a *defence* (fires when threatened) or
an *event* (fires on its own timer)? He did not say. Q7.

**Why it cannot leave.** *"the ultra-brine is both their habitat and their metabolic
substrate — which has confined them to scattered deep basins for geological ages and
preserved them through catastrophes that erased younger civilizations."* So: one Elder per
deep pool, not every pool has one (*"scattered"*), and an Elder is older than every
faction on the planet.

**Its memory and how it reads history.** *"Their awareness is equally ancient but
profoundly nonhuman: they remember the arrival of the Reshapers, the changes wrought on
the world, and events predating nearly every extant culture, yet they interpret history
through chemistry, pressure, charge, mineral deposition, biological composition, and
disturbance rather than names, politics, or technology."* — this is the voice register
for any Elder dialogue/menu text: it reports *what changed in the water*, never who did it
or why.

🔑 **"The Reshapers" — cross-checked against the campaign lore, 2026-09-26.** The word
**appears nowhere** in `design/`, `infrastructure/state/items/` or `src/` (MEASURED: a
case-insensitive search returns only `enrichment_agents.md`'s "live NPC reshaper", an
unrelated agent name). It is a NEW name in his paragraph. The lore it points at is
already ruled, under other names:
- The world was partly terraformed and then built into a *"tremendous factory — a
  mega-project among mega-projects. Not terraforming: terramanufacture"*
  (`ASHKARR_WORLD_DEFINITION.md` §3b, owner 2026-09-06, `TERRAMANUFACTURE_CANON_1`, closed).
- The builders are the **Rakata** — endonym `Rakata`, exonym *"the Forsaken / the
  Forgotten"* (`ANCIENTS_AS_RAKATA_SPEC.md`, owner 2026-08-20, RULED v1); *"The Forsakens
  tried to fix a tidally locked planet and failed"* (`tidally_locked_world.md` §2).
- `rakatan_legacy_index.md` enforces that *"a new 'the ancients made it' claim anywhere
  else must land a row here, or it is drift."*

⇒ **BENCH position:** "the Reshapers" is most naturally the Elders' *own* exonym for the
Rakata — a name from a geological intelligence that knows them only as *the ones who
changed the world's chemistry* — and this fits his register line exactly (they do not use
names or politics; "Reshapers" is a description, not a name). That reading keeps the lore
single-sourced. But it is an inference: **Q9 asks him**, and if he confirms, the Elders'
memory of the Reshapers' arrival becomes a row in `rakatan_legacy_index.md` (an
*eyewitness* to the terramanufacture, which nothing else on the planet is).

**What it does to its pool.** *"They can deliberately alter the mineralization of their
pools, dissolving entire blocks of crystallized seafloor to uncover ancient mummified
bodies, wreckage, or artifacts, or violently ejecting long-entombed objects upward from
the brine as part of an exchange."* — BENCH NOTE: this is the mechanism by which the §6
"ultra-protected loot" is *released*: the Elder is one of the keys to the pools. The
in-engine action is: remove jacket-mineral cells (§6's salt `SolidIce` twin) around the
pool, or spawn an item on the pool's shore. Both are trivially buildable once the jacket
mineral exists.

**The novelty economy — the trade rule.** *"What they value above all is novelty: a newly
encountered life form, corpse, xenotype, tissue, mineral, or unfamiliar material may be
extraordinarily valuable once, then nearly worthless thereafter because the Elder has
already incorporated its chemistry into memory."* And: *"Technology fascinates them but
is conceptually opaque; they recognize unusual materials, energy states, and structures
more readily than intended function."*
— BENCH NOTE: the rule in one line: **each Elder keeps a set of what it has seen; the
first specimen of a category it has not seen is worth a great deal; every later one is
worth almost nothing.** "Category" is his list — life form (a creature def), corpse,
xenotype (a `XenotypeDef` — so a *colonist* of a new xenotype is an offering, which is
delicious and dangerous), tissue, mineral, unfamiliar material (a stuff/ThingDef). The
"technology is opaque" line means the valuation ignores `MarketValue` and tech level
entirely — a plasteel ingot and a charge rifle are both "an unusual material" once. The
seen-set is per-Elder and must persist in the save (a `WorldComponent` or the Elder's own
`IExposable` comp). This is a **new trade mechanism**, not a `TraderKindDef`: nothing in
vanilla trades on novelty. It is also a natural place for the Bazaar-style whole-deal
haggle already ruled elsewhere (`bazaar-trade-window-ruled` memory) — but that is an
architecture question for the build, not this capture.

**What it gives back.** Two kinds:
1. *"they can sometimes modify matter in ways no conventional craftsman can — for example
   growing a **resonant storage crystal that passively increases the effective capacity
   or charge retention of all nearby batteries**."* — BENCH NOTE: a building with an area
   comp that raises `CompPowerBattery` capacity/retention for batteries in range.
   MEASURED: no such comp exists in `src/` (the only `StoredEnergyMax` references are in
   bridge tooling and an absorbed Gonk-droid def); `RUT_BrineBattery` is an *animal*
   (`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_BrineBattery.xml`) and unrelated
   beyond the pun. New C#, small.
2. *"they may release singular treasures accumulated over millennia, typically only one
   example of each because duplication held no value to them"* — his list, verbatim:
   - *"a functional lightsaber sealed since the Rakatan era"*
   - *"an intact pre-Republic navigation core"*
   - *"an unknown droid brain preserved in salt"*
   - *"a one-of-a-kind alien weapon whose operating principle is no longer understood"*
   - *"a sealed biological relic from an extinct species"*
   - *"some beautifully useless artifact whose significance only becomes apparent much
     later"*

   BENCH NOTE on tier: the first three are **genuine Star Wars canon IP** (lightsaber,
   Rakata, Republic, droid) and by Q11a (`biome_mod_architecture.md` §7) live in the
   `RSW_`/`RUT_` layer, patched onto the Elder's treasure table with `MayRequire`; the last
   three are invented and can ship `RM_`. "One example of each" is a one-shot-per-world
   flag on each treasure (persisted with the seen-set). The *"beautifully useless artifact
   whose significance only becomes apparent much later"* is a plot hook with no owner yet —
   it needs a home in a plot item before it is built, or it will be built as a trinket.

**The feel of trading with it.** *"Their trade therefore feels less like commerce than
negotiating with a geological intelligence that has spent tens of thousands of years
quietly collecting one specimen of anything genuinely new."* — the design target for the
UI and text: not a trade window with prices, an exchange with a thing that wants to *see*
something. (BENCH NOTE: this sentence, and the register line above, are the brief for any
LLM-voiced Elder text under the standing `claude -p` rule — the Elder is a strong
candidate for the Oracle-style text-only consumer, since it *only* speaks in chemistry.)

## 8. What this means for the frozen sheet

`the_grey_deep.md` is 🧊 FROZEN (`BIOME_FREEZE_FABLE_REVIEW_1`, 2026-09-07): amendments
add detail, never change a ruling; the unfreeze is his call at a sitting. Read against
every section of the sheet and of `terminator_sea.md` (inherited), the drop sorts as
follows. **BENCH does not resolve any FLAG below — that is the sitting's job.**

### 8.1 Additive — lands under the sheet as written

| drop item | sheet hook | why it is additive |
|---|---|---|
| pillars, domes, chimneys, crystals (§2) | §1 *"salt pillars rise from the bottom like a blind forest"*, §4 the pillar-mason, §7 *"soluble minerals"*, *"pillar stone"* | the sheet named them; the drop draws them |
| crusted shoreline (§2.6) | `terminator_sea.md` §5 *"the ground is salt crust, white"* | texture for a ruling already made |
| crystalline flora (§4) | §7 *"crystallization products no dayside chemistry makes"*, §9 palette *"crystal white"* | the sheet had no flora at all; this fills an empty slot without touching a ban — **provided** ban 4 (no glow) holds, and every spec above is non-luminous |
| shrimp/clam/mussel layer (§3) | §4 cap released 2026-09-10, *"solitary added kinds are legal"* | new kinds are allowed; see 8.2 for "abundant" |
| salt-snow weather (§5) | §9 *"the crackle of growing crystal … scrape-dust falling"* | the sheet already has falling crystal as sound and motion |
| crystallisation defence + protected loot (§6) | §3 *"everything that enters dies; everything that dies there keeps"*; §6 ban 1 *"no survivable brine-pool entry"*; §7 *"jacketed salvage"*; §8 the statuary | the drop is the *mechanism* of rulings already frozen |
| the Elders' pool-dissolving and ejecting (§7) | §7 *"the jacketed salvage … chiseled free"* | a second way to free what the sheet says is there |
| the novelty trade, the resonant crystal, the treasures (§7) | nothing in the sheet — new | pure addition; no ruling touched |

### 8.2 FLAGGED — could be read as contradicting a ruling; owner to settle

1. **A second colossal organism.** `terminator_sea.md` §4: *"about three lineages exist"*
   … *"one or two enormous, ancient, solitary brine animals per sea, endemic to it"*; the
   Grey Deep §0: *"one monoculture, one endemic giant lineage."* The Elders are a colossal
   *branching salt-crystal organism* per deep pool. **BENCH position:** not a contradiction
   — the Elder is sessile, mineral, and *"a geological intelligence"*; it is a formation
   that thinks, not a second giant *animal*, and the sheet's "lineage" language is about
   the fauna. But it IS a new apex presence in a biome whose whole law is solitude, so he
   should say so in a sitting.
2. **"Abundant" vs no-schools/no-swarms.** §3's *"abundant shrimp, clam and mussel
   equivalents"* against `the_grey_deep.md` §6 ban 2 and `terminator_sea.md` §6 *"no herds,
   flocks, schools, packs or swarms … fauna are single-spawn and low-density by def."*
   **BENCH position:** abundance by many *individually spawned* sessile things (a mussel
   equivalent at commonality 0.6, `wildGroupSize 1`) satisfies both; a schooling or
   clustered def does not. Build to that and no ruling moves.
3. **Membranes that retract / fans that rotate** vs `terminator_sea.md` §6 *"no
   heliotropism, no sun-tracking, no plants that open and close."* The Brine Crown (§4.3)
   retracts on *salinity shift* and the Fan Palm (§4.4) rotates panes. **BENCH position:**
   the ban's target is sun-driven diurnal behaviour on a world with no day; a
   chemistry-driven defensive retraction is not that. But it is *"plants that open and
   close"* by the plain words, and the sheet inherits it — flagged.
4. **Salt snow vs "no snow, no ice".** `terminator_sea.md` §6. **BENCH position:** that
   ban is about water weather on the surface (its own reason: *"at +14 °C with no lift, the
   only water delivery is thin fog"*); the drop's weather is salt, on the floor. Additive.
   ⚠️ The def's existing vanilla `Rain 4` IS against the ban and is a pre-existing defect.
5. **Chemosynthetic symbionts** (Salt Chimney Vines, §4.5) vs `terminator_sea.md` §6 *"no
   cold gas vents … those belong to the poison forest."* **BENCH position:** warm mineral
   seeps ≠ cold gas vents; the chimneys vent *brine*, not gas. Additive.
6. **Star Wars canon inside a franchise-free sea.** The Elder's treasure list names a
   lightsaber, the Rakatan era, a pre-Republic navcore and a droid brain. Per Q11a these are
   IP and live in the `RSW_`/`RUT_` layer — the `RM_` Elder ships with the three invented
   treasures and the canon three are patched on. Not a sheet contradiction; a tier rule.
7. **The Reshapers** — a new proper noun for a ruled people (§7.2). Not a contradiction;
   a naming question (Q9), and the legacy index's drift rule applies.

### 8.3 Roster consequences

`rosters/the_grey_sea.json` is stale against this drop in two places that BENCH did not
edit (the roster is the owner's via BENCH, edited at a sitting): `"flora": []` is now
false — seven flora forms are commissioned; and `new_defs` should gain rows for the
pillar (as terrain/feature, its existing row says "plant"), the chimneys, the crystal
mineral, the pool grade, the Elders, and the shrimp/clam/mussel layer. The roster's
pillar-mason row already carries `"mechanic_load": "pillar navigation/waymarks deferred
to diving mods"` — the diving mod shipped, so that deferral has expired (as
`GREYSEA_ANCHOR_CREATURES_1` already records).

## 9. Open questions for the owner

Each with a BENCH position, so a sitting can say "yes" or "no" rather than design from
scratch. None is blocking for the smallest build steps in §10.

- **Q1 — The frozen pawn: hediff or jacket-thing?** Vanilla has no pawn-freezing hediff
  (MEASURED, §6). Two honest shapes: (a) a hediff of ours — Moving 0, a smothering
  severity ramp, removed by a chisel job on the pawn's cell; (b) the pawn is *encased*:
  despawned into a salt-jacket thing (the `SolidIce_Loot` / Anomaly `Digested` shape) that
  must be mined, which is how the statuary already works for the dead. **Position:** (b).
  It is one mechanism for the living and the dead, it makes "smothering" a timer on the
  jacket rather than a second hediff, and a colonist standing as a white statue among the
  war's vehicles is the sheet's image exactly. It is also the more dangerous of the two
  (a downed pawn can be rescued; an encased one must be dug), which is what *"ultra-
  protected"* asks for.
- **Q2 — Do the salt chimneys carry the crystallisation defence?** He gave the defence to
  pools and to "creatures near them"; chimneys vent the same super-brine. **Position:**
  yes, at reduced range — a chimney's plume is a small standing hazard cell-cluster that
  jackets anything that walks into it, which makes chimneys the *visible* teacher of a
  mechanism the pools deliver invisibly. Costs one shared comp.
- **Q3 — Brine rivers.** Glass Veil Kelp grows *"over trenches and brine rivers"*; the
  pocket map has no river genstep and the surface sea has `allowRivers false`.
  **Position:** a floor "brine channel" terrain strip from a chimney field down to a pool
  (the super-brine flows downhill into the basin), generated as a terrain line, no
  vanilla river machinery. It gives the kelp its home and gives the floor a legible
  gradient toward the danger.
- **Q4 — How far does "every shoreline carries the crusty whiteness" reach?** Texture only
  (a Grey shore terrain), or also image 03's domes breaking the surface as shore things?
  **Position:** both — the terrain is the rule ("every"), the domes are scatter on it. The
  shore is the one part of the Grey a non-diving player ever sees, so it carries the whole
  biome's identity above water.
- **Q5 — Shrimp/clam/mussel equivalents: new defs, or sorruth + otheska already?** The
  Grey has two shelled floor-crawlers; his sentence names three groups. **Position:** two
  new sessile defs (a "mussel" that clusters on pillars and domes and a "clam" that sits in
  sediment), both catchable (floor + `*Catch`), and *no* new shrimp — `RM_Fessk` is the
  shrimp, and a small shrimp would read as a second of the same kind in a biome whose law
  is "do we already have one?".
- **Q6 — Sphere-plant "weaponry": contact damage?** *"both armour and weaponry."*
  **Position:** yes, low — a `RM_Venomvine`-style touch injury, so the floor has two plants
  that hurt (Brine Crown, sphere) and five that do not, and a diver learns to read the
  crystal by shape.
- **Q7 — The Elder's discharge: defence, event, or both?** **Position:** both, on a clear
  tell. It fires *defensively* when the pool is disturbed (harvest at the shore is fine;
  mining the jacket at the pool's edge is a disturbance), and *rarely* on its own as an
  incident — the biome's one "weather" that is not weather, with a visible charge build-up
  on the limbs so an observant diver leaves before it lands. The sheet's own principle:
  *"the tell that lets the observant survive."*
- **Q8 — "Cripple nearby ships."** What does an Elder discharge do to a gravship
  (Odyssey)? UNMEASURED in engine terms — gravship damage/disable surfaces were not
  investigated in this pass. **Position:** file it as a bar on the Elder item, resolved by
  a Desktop RimSage read, and do not let it gate the Elder's other three effects.
- **Q9 — Are "the Reshapers" the Rakata?** (§7.2.) **Position:** yes — it is the Elders'
  own word for the people who terramanufactured the world, and it should be *recorded as
  their exonym* in `rakatan_legacy_index.md` (a row: "the Elders' memory — the only
  eyewitness to the arrival") rather than introduced as a new faction. If he means a
  *different* people — earlier than the Rakata — that is a new lore thread and needs its
  own sitting before anything is written.
- **Q10 — Is the whole Elder a Grey-Sea-only thing, or do other seas get one?** *"scattered
  deep basins"* is plural. **Position:** Grey only, for now — the Grey is the planet's
  chemical works and the only sea with the super-brine substrate; the Twilight Deep's law
  is mat-and-placid and the Scald boils. Anything else is a later drop.

## 10. Build-order suggestion, smallest first

**BENCH NOTE throughout.** Ordered so each step ships something visible on its own and
nothing waits on an open question it does not need. Everything below lands in
`mandrake.rm.terminalbiomes` unless it is a mechanism shared across seas (then
`mandrake.rm.divinginteraction`) or canon IP (then the Utinni patch layer).

| # | step | new defs (rough) | C# | needs | unlocks |
|---|---|---|---|---|---|
| 1 | **Fix the pre-existing surface defect** — drop vanilla `Rain` from `RM_GreySea`'s `baseWeatherCommonalities` (`terminator_sea.md` ban) | 0 (edit) | none | nothing | honesty |
| 2 | **Salt-snow weather** on the floor (§5) — clone the AshFall pattern with an off-white overlay; wire it into the pocket map's weather | 1 WeatherDef | none | nothing | the Brine Crown's trigger; the floor moves |
| 3 | **The jacket mineral** — a salt twin of `SolidIce` (mineable, yields a salt-crystal item) + the **huge salt crystal** node (§2.2) + the salt-crystal item | 2 ThingDefs + 1 item | none | nothing | the statuary becomes real; §6 loot protection; Q1(b) |
| 4 | **Pillars and domes** (§2.4, §2.5) — two natural building/feature families, scattered by a Grey-only genstep on the floor; the pillar is the mason's work | 2–4 ThingDefs + 1 GenStep/scatterer | tiny (scatter) | 3 (they are the same mineral) | the navigation law has something to navigate; four existing descriptions stop lying |
| 5 | **Crusted shore** (§2.6) — a Grey shore terrain with image-02's texture via `RM_SeaShoreExtension`; domes as shore scatter if Q4 = both | 1 TerrainDef (+ reuse of 4) | none | 4 | the surface reads as the Grey |
| 6 | **The seven flora** (§4) — Crucible Pod, Mosaic Fan Palm, cubic sculpture, sphere plant, Glass Veil Kelp, Brine Crown, Salt Chimney Vine; `<wildPlants>` on `RM_GreySea`; the two that hurt use the `RM_Venomvine` shape | 7 plant ThingDefs (+ colour variants as graphics, not defs) | small (retraction state; chimney adjacency) | 3–4 for cluster rules; 7 for the vine | the floor is a wonderland |
| 7 | **Salt chimneys** (§2.1) + brine channel if Q3 = yes | 1 ThingDef (+1 TerrainDef) | small (plume effecter; hazard if Q2) | 3 | the vines' host; the teacher for §6 |
| 8 | **Coloured salts → cuisine** (§2.3) — 3–4 salt ingredient items `RM_`; `MayRequire`-guarded recipes in `mandrake.rsw.cuisine` | 3–4 items + recipes | none | 3 | the treasury has a use |
| 9 | **Shrimp/clam/mussel layer** (§3) — two sessile defs, each floor + `*Catch` | 4 ThingDefs + 2 PawnKindDefs | none | 4 (they cluster on it) | the food chain under fessk; the Brine Crown has prey |
| 10 | **The brine pool grade** — the saturated-plus liquid/terrain (`LIQUID_TYPES_MOD_1`'s owed grade), pool basins in the floor genstep, jacket mineral around and under them | 1 LiquidDef + 2 TerrainDefs + genstep changes | small | 3, 4 | the sheet's *"lakes at the bottom of a sea"* exist |
| 11 | **The crystallisation defence** (§6) — contact trigger on pool terrain; the encase-a-pawn mechanism (Q1); the chisel-free job | 1–2 HediffDefs or 1 jacket ThingDef + 1 JobDef | **medium** — the one genuinely new mechanism | 10, Q1 | the pools are deadly and the loot is locked |
| 12 | **The Brine Elders** (§7) — the multi-cell sessile organism; the discharge; the seen-set novelty trade; the resonant crystal; the six treasures (three `RM_`, three patched canon) | 1 large ThingDef + 1 building + ~6 treasure ThingDefs + 1 IncidentDef | **large** — trade UI, persisted seen-set, discharge, battery comp | 10, 11, Q7–Q9 | the biome has a mind |

**Rough count of distinct new defs the drop implies:** ~35–45. By category:
terrain/formation ~8 (jacket mineral, crystal node, pillar, dome, chimney, shore terrain,
pool shallow/deep, brine channel) · minerals/items ~6 (salt crystal, 3–4 coloured salts,
recipes) · weather 1 · flora 7 · fauna 4–6 (two sessile species × floor + catch) ·
hediffs/jobs 2–3 · Elder cluster ~10 (organism, resonant crystal, six treasures,
incident, trade). Zero of these exist today (MEASURED, §0).

**Items BENCH thinks should be filed** (names are suggestions in the project's grammar;
BENCH files, not this pass):
- `GREYSEA_FLOOR_FORMATIONS_1` — steps 3, 4, 7 (jacket mineral, crystals, pillars, domes,
  chimneys): the terrain half of the drop, and the thing four defs already describe.
  This absorbs the pillar-mason scope bar of `GREYSEA_ANCHOR_CREATURES_1`.
- `GREYSEA_CRYSTAL_FLORA_1` — step 6, the seven specs, verbatim text carried into each
  def's authoring note; the "marred, never manufactured" art rule on every artpipe job.
- `GREYSEA_SALT_SNOW_WEATHER_1` — step 2 (small enough to be its own quick win) plus the
  step-1 rain fix.
- `GREYSEA_SHORE_CRUST_1` — step 5, surface-side, and Q4.
- `GREYSEA_BRINE_POOL_DEFENCE_1` — steps 10–11: the pool grade, the jacket-encasing of
  pawns and loot, the chisel job; carries Q1–Q2.
- `GREYSEA_BRINE_ELDERS_1` — step 12 whole; carries Q7–Q10 and the Q11a tier split of
  the treasure list; the "beautifully useless artifact" needs a plot home before it is a
  def.
- `GREYSEA_SALT_CUISINE_1` — step 8, cross-mod with `mandrake.rsw.cuisine`.
- `GREYSEA_SESSILE_LAYER_1` — step 9 and Q5.
- And a roster amendment at the next Grey Sea sitting (§8.3) — not an item, a sheet edit
  on his word.
