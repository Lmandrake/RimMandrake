# Explosive plant growth — per-plant roster

> 🔴 **SUPERSEDED IN ASSIGNMENT, 2026-09-21 — do not build from this file.**
> The owner reshaped the mechanic (`explosive_plant_growth_design.md` §9). Two of this
> file's keys are now wrong at scale: `GLUT` is **retired** into the new default, and a
> plant bursts **only if its own identity is adaptation to scarce water** — so the 58
> `BURST` rows are an assignment made under a rule that no longer holds. The new default
> is `CHURN` (split, die, fruit, sow sprouts that respect built ground), and `RUPTURE` is
> new for the contaminated.
> ✅ **The plant LIST and the evidence in each row are still good** — it is the variant
> column that must be re-derived. Regenerate, do not hand-edit.

Item: `EXPLOSIVE_PLANT_GROWTH_1`. Design only; no def, mod or C# edited.

## The ruling this roster obeys

Owner, 2026-09-20 (recorded in `design/Jawa/worldbuilding/explosive_plant_growth_design.md` §8), verbatim:

> *"It's less about the biome and more about the plants IN that biome having different
> behaviors. Still comes out to differences between biomes, but it really should be
> driven all by plant genetics / identity / adaptation to the intense sunlight and lack
> of water. So this is about 'plants that are contaminated'."*

So: **the terminal moment is a property of the plant def, never of the BiomeDef.** A
biome's character is the emergent sum of which plants grow there. This file therefore
lists plants, one row each, and assigns each a variant on the strength of that plant's
own identity (its def, its label/description, its sheet role). Where the same plant
grows in several biomes it carries the same variant everywhere. ⛔ There is no
per-biome column and there must never be one.

Standing carve-outs that pre-date the reframing and are unchanged by it, because they
are ALSO plant-identity facts once read that way:
- `PLANT_GROWTH_SPEC.md` R-G5 exempt list (anima, Gauranlen, ambrosia, quest-timed
  plants) — an exempt plant never soaks.
- R-G3 / R-H2b: the terminator (poison forest) stays stunted; `biomes/deep_desert.md`
  §6 HARD BAN 4: no fast growth in the deep desert. In plant terms: the plants whose
  identity IS "adapted to no water" do not charge.
- Fungal biomes: the Sheen is not water; fungal plants do not soak on it.


## The three ruled variants

All ruled by the owner 2026-09-20 (design doc §8), on top of the ruled DEFAULT:

| key | variant | what the plant does at the top | ruled |
|---|---|---|---|
| `BURST` | **the default Burst** | swell → tremble → pop; premium produce scattered; husk; a sown ring of sprouts that IGNORES zones | 2026-09-20 (sow-and-ignore chosen over two softer shapes) |
| `GLUT` | **Fruit-glut** | no pop — a permanently-soaked plant dumps a heavy fruit crop and resets its charge | 2026-09-20 ("Greentide" as asked; now a plant property) |
| `SLIME` | **Slime-ring** | the Burst pays its harvest, but the ring it sows turns the ground to slime instead of sprouts | 2026-09-20 ("Slime" as asked; now a plant property) |
| `TINDER` | **Tinder-burst** | the normal Burst with fuel for debris — husk, chaff, a ring of quickgrass, all flammable | 2026-09-20 ("Pyrelands" as asked; now a plant property) |

One older ruled variant is carried, because it was ruled on the plant, not the tile:

| key | variant | what the plant does at the top | ruled |
|---|---|---|---|
| `FLUSH` | **Nectar Flush** | no surface spectacle; growth runs INSIDE the giant — bark swells, boughways re-route, thornbug nectar glut | 2026-09-10 Q3 ("Fever Wood: Nectar Flush variant IN") |

And the non-variant:

| key | meaning |
|---|---|
| `NONE` | this plant never acquires SOAKED; it grows at the ambient ×4 tier only, or is exempt from that too where the spec says so |

NOT ruled and not assigned here: whether sunlight/water ADAPTATION defuses a charge
(the Contagion question he redirected). Plants where that would matter are marked
`BURST?` with the open question named, never guessed closed.


## Plant set surveyed (sources)

Two sources, read 2026-09-20, joined by defName. Both are small enough to parse whole
(ElementTree / json.load), so the counts below are parsed counts, not scan counts.

1. **The landed biome rosters** — `design/Jawa/worldbuilding/biomes/rosters/*.json`,
   `flora[]` rows (the SOURCE the patch generators read; `_SCHEMA.md`). **125 distinct
   flora defNames** across the biome files, plus **35 `new_defs` rows of kind plant** that
   have no defName yet (sheet-commissioned, unbuilt). `flora_purged` rows are NOT in this
   roster: a purged plant is not on the planet.
2. **Our own plant defs** — every `ThingDefs_Plants/*.xml` and `PlantBases/*.xml` under
   `src/RimUtinni/` and `src/RimStarWars/SWBestiary/Defs/DesertPort/`: **88 def rows**, of
   which the plants (not their harvested products, projectiles or abstract bases) are
   listed below. `src/RimMandrake/Pyrelands` is read for its two plant defs because the
   Pyrelands roster names them.

Donor plants (Alpha Biomes `AB_*`, ReGrowth `RG_*`, Biotech `Plant_*`, Grindterra
`GRim*`, IronScruff, VRE) are rostered by the biome JSONs and are therefore ON the
planet; they get a row here like any plant we wrote. A trait on a donor plant is a patch
target, not a def we own — build's problem, not this roster's.

⚠️ **Name drift observed, not resolved here:** the rosters carry `Plant_Chakroot_Wild`,
`Plant_HubbaGourd_Wild`, `Plant_Nysyllin_Wild`, `Plant_Bloddle` (the donor SW names, per
`_SCHEMA.md`'s "bare names, no RSW_ anticipation"), while the live defs in
`src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortB_Plants.xml` are
`RSW_Plant_Chakroot_Wild` etc. Which name the game actually loads for those four is
UNMEASURED from here (needs the def dump); the roster rows below use the roster's name
and note the RSW_ twin.


## Roster — plants that get explosive growth

One row per plant (or per unbuilt `(new)` sheet commission). `where` is where the rosters place it — evidence only, never the reason. The reason is always the plant.

### GLUT — soak-native genetics (evolved under permanent water: sheds and resets, never pops) — 13 plants

| plant | variant | where rostered | why THIS plant |
|---|---|---|---|
| `Plant_MujaFruit_Wild` | `GLUT` | the_greentide | SW fruit bush rostered only under the Greentide fruit law; its identity IS the fruit that yearns to be eaten — a fruit-bearer that evolved under permanent soak sheds a glut, never pops |
| `Plant_JoganTree_Wild` | `GLUT` | the_fever_wood, the_greentide | SW fruit tree; fruit-crown economy on both sheets. Fruit-crowned jungle native → dumps fruit and resets. Its trunk's fate (the Greentide crack-and-FALL) is the Greentide kit's size-triggered event, not this engine's |
| `AB_SugarFamewort` | `GLUT` | the_greentide | 'sweet free-calorie groundcover' — the fruit law in groundcover form; soak-native |
| `RUT_GiantLeaf` | `GLUT` | the_fever_wood, the_greentide | `RUT_CavernsFlora.xml`: 'grows low in the jungle understory, broad enough to shelter a grown man from the rain' — rain is its habitat, so soak is its baseline: it sheds leaf-produce and resets rather than bursting |
| `Plant_FelucianGlowspore_Wild` | `GLUT` | the_greentide | Felucia jungle canopy tree (SW donor); Felucia is canon's fungal rain-jungle, permanent soak is its genetics |
| `AB_JungleTree` | `GLUT` | the_greentide, the_webwork | Alpha Biomes jungle canopy; soak-native. In the Webwork the same tree sheds, and the thicket's churn comes from the BURST vines below it, not from this tree |
| `Plant_Bubblespore_Wild` | `GLUT` | the_greentide | rostered as Greentide floor cover only; assigned GLUT on roster placement — its def description is UNMEASURED here (SW donor, not in our defs). Confirm from the def dump before wiring |
| `AB_MangroveTree` | `GLUT` | the_miasma | 'the trees run the plumbing' — a mangal stands in water permanently; a permanently-soaked plant that popped would pop forever. Mangroves drop propagules: that IS a glut-and-reset |
| `AB_MangrovePalm` | `GLUT` | the_miasma | mangal family, as AB_MangroveTree |
| `AB_ParasiticMangrove` | `GLUT` | the_miasma | mangal family, as AB_MangroveTree |
| `Plant_Reeds` | `GLUT` | weeping_stones | water-margin blade; a margin native is soak-native. Consequence: even if the truce pools count as a soak (card #5, unruled), the reeds beside them shed quietly and never pop — the sacred water stays quiet by the plant's genetics, not by a biome exception |
| `(new) digestive-accelerant fruit` | `GLUT` | the_greentide new_defs | the fruit that yearns, as a def of its own — the type specimen of GLUT |
| `(new) blade-flora with bladder-fruit` | `GLUT` | weeping_stones new_defs | margin fruit-bearer; as Plant_Reeds |

### FLUSH — the giants (growth runs inside the trunk) — 2 plants

| plant | variant | where rostered | why THIS plant |
|---|---|---|---|
| `Plant_HydenockTree_Wild` | `FLUSH` | the_fever_wood, the_greentide | SW wroshyr-analog giant hardwood; the Fever Wood canton works its crown. A giant's growth runs INSIDE — bark swells, boughways re-route. Carries FLUSH in the Greentide too (the kit's fall is separate and size-triggered) |
| `AB_KeeningCordax` | `FLUSH` | the_fever_wood, poison_forest | 'interim single-tile body for the tower-trunks' — it IS the Fever Wood giant until the authored tree lands, so it carries the giant's variant. In the poison forest it never soaks (trace water), so FLUSH there is inert — the model working as ruled |

### SLIME — slime-fed genetics (the sown ring converts ground) — 9 plants

| plant | variant | where rostered | why THIS plant |
|---|---|---|---|
| `RM_Plant_SlimeGrass` | `SLIME` | (our def, `src/RimMandrake/GelatinousSlime`) | the fertility-1.0 lure the owner ruled farms fail by; its sown ring converting ground to slime is the ruling made watchable |
| `RM_Plant_Bellows` | `SLIME` | (our def, GelatinousSlime) | slime kit pseudo-plant; slime-fed |
| `RM_Plant_Thumbstalk` | `SLIME` | (our def, GelatinousSlime) | slime kit pseudo-plant; slime-fed |
| `RM_Plant_Readerbloom` | `SLIME` | (our def, GelatinousSlime) | slime kit pseudo-plant; slime-fed |
| `AB_TallSlimyGrass` | `SLIME` | the_slime | donor slime-grass f1.0 — 'fields of its own grass'; slime-fed |
| `AB_SlimyFern` | `SLIME` | the_slime | donor slime suite; slime-fed |
| `AB_Slimecasia` | `SLIME` | the_slime | donor slime suite; slime-fed |
| `AB_SlimyTree` | `SLIME` | the_slime | donor slime suite, 'groves of its own trees'; slime-fed |
| `AB_LargeSlimyTree` | `SLIME` | the_slime | donor slime suite; slime-fed |

### TINDER — fire-loop genetics (burst debris is fuel) — 3 plants

| plant | variant | where rostered | why THIS plant |
|---|---|---|---|
| `RM_FE_Plant_Quickgrass` | `TINDER` | the_pyrelands (c=4.0) | the Rakatan feral forage crop whose days-clock green→gold IS R-H3's fire loop; a burst that leaves husk, chaff and a quickgrass ring is the fire's supply line in one event |
| `RM_FE_Plant_EmberGrass` | `TINDER` | (our def, `src/RimMandrake/Pyrelands`) — not in the roster JSON | fire-ecology grass by name and kit; same genetics as quickgrass |
| `RM_FE_Plant_ScorchFruit` | `TINDER` | the_pyrelands new_defs (built) | spoils-in-a-day scorch-fruit wired into FireEcologyHook.cs; a fire-cycle plant, so its burst debris is fuel |

### BURST — the ruled default (plant identity gives no reason to diverge) — 58 plants

| plant | variant | where rostered | why THIS plant |
|---|---|---|---|
| `(new) bloom crop` | `BURST` | the_cracked_lands new_defs | the flagship: born in §10b, contracted to `RUT_BloomBurst`. The default Burst at carpet scale in flood synchrony; the boom-bust die-off and the bloom harvest are the sheet's, not a variant |
| `AB_HardyGrass` | `BURST` | desert, the_cracked_lands | meagre alien grass; nothing in its identity refuses water — an irrigated or flooded grass pops and sows grass |
| `GRimMoss` | `BURST` | the_cracked_lands | generic moss; soaks like anything else. Burst scale on a tiny plant is build's call, not a variant |
| `RUT_TwistingThorngrass` | `BURST` | the_cracked_lands | polluted-arid thorn family (`RUT_PollutedFlora.xml`): hardy, not water-hoarding; a thorn ring sown into a doorway is the encroachment the Burst is for |
| `RUT_TwistingThornweed` | `BURST` | the_cracked_lands | as thorngrass |
| `RUT_TwistingThornwood` | `BURST` | poison_forest, the_cracked_lands | as thorngrass; inert in the poison forest (never soaks) |
| `(new) twisted trees + shade-line grasses/mosses` | `BURST` | the_cracked_lands new_defs | our own Cracked Lands vegetation; default |
| `Plant_Chakroot_Wild` | `BURST` | desert, the_fever_wood, the_greentide | marshland root plant (`RSW_DesertPortB_Plants.xml` description, RSW_ twin); a root vegetable pops and sows — the ruled water-for-food pump. ⚠️ Emergent: in the permanently-soaked Greentide it pops continuously; that is the ruling working, and whether the Greentide roster wants it at c=0.5 is that roster's question |
| `Plant_HubbaGourd_Wild` | `BURST` | desert, the_greentide | Tatooine hardy gourd, Jawa/Tusken dry staple (RSW_ twin's description) — desert genetics, not jungle. Same emergent note as chak-root for its Greentide row |
| `Plant_Bloddle` | `BURST` | dune_sea + deep_desert | hydroponic bulb vegetable (RSW_ twin); a crop plant. Inert on the deep-desert tile (never soaks), Bursts where irrigated |
| `Plant_Nysyllin_Wild` | `BURST` | arid_shrubland | SW medicinal herb; nothing water-hoarding in it |
| `Plant_HealrootWild` | `BURST` | arid_shrubland | RimWorld herb; default |
| `Plant_Brambles` | `BURST` | arid_shrubland | thorny holdout; a bramble ring is encroachment |
| `Plant_Ripthorn` | `BURST` | arid_shrubland | Biotech alien thorn, 'forbids rather than flees'; default with teeth |
| `Plant_Bush` | `BURST` | arid_shrubland | generic shrub; default |
| `Plant_ShrubLow` | `BURST` | arid_shrubland | stand-in for the fuzz; default until the fuzz def lands |
| `RG_Plant_AridGrass` | `BURST` | arid_shrubland | struggling grass; default |
| `RG_Plant_CreepStern` | `BURST` | arid_shrubland | alien low form; default |
| `RG_Plant_Dervish` | `BURST` | arid_shrubland | alien low form; default |
| `(new) the fuzz` | `BURST` | arid_shrubland new_defs | knee-high graze-adapted canopy plant; default |
| `(new) venomvine` | `BURST` | arid_shrubland new_defs | fortress flora; a sown venomvine ring is the fortress growing — default |
| `(new) defending shade plants` | `BURST` | desert new_defs | thorn/venom patch flora; default |
| `AB_Aaklac` | `BURST` | desert, the_webwork | alien arid form; default |
| `AB_Gomphoeria` | `BURST` | the_fever_wood, the_webwork | alien groundcover; default |
| `AB_Iashiphus` | `BURST` | the_fever_wood | alien groundcover; default |
| `RG_Plant_TropicalChokevine` | `BURST` | the_webwork | 'the thicket churns against itself — hostile vine mass'. The sheet's Churn (§4c) IS the default Burst on a vine: pop, sow a ring of chokevine in the gap you were using. No new rule |
| `AB_TangleTea` | `BURST` | the_webwork | churn understory, tangle-form; as chokevine |
| `Plant_TookeTrap_Wild` | `BURST` | the_greentide, the_webwork | predatory SW plant; a burst sowing a ring of traps is encroachment with teeth. Same emergent Greentide note as chak-root |
| `(new) pale flowers (web-tracing bloom)` | `BURST` | the_webwork new_defs | route-signal bloom; default |
| `AB_BloodBouquet` | `BURST` | poison_forest, the_contagion | 'spine-armored seed rolls to the burn line and dies as fertilizer' — seed-discharge is its whole identity, so the default Burst is its native behaviour. NOT put in the contaminated group: it is the Contagion's own uncontaminated seeder. Inert in the poison forest |
| `(new) rainbow flora suite` | `BURST` | the_miasma new_defs | 3–4 genuinely benign blooms (ban 2: never a trap) — a Burst that sows flowers; benign stays benign |
| `AB_GreenRockFern` | `BURST` | weeping_stones | rock-shade fern; default |
| `Plant_Fireweed` | `BURST` | the_forge | heat-proof fibre plant (Odyssey); heat-adapted is not fire-loop-adapted — no reason to leave the default. Reachable only by irrigation (the Forge's rain flashes off the rock) |
| `RUT_FireLavender` | `BURST` | the_forge | 'adapted to survive off the glow of magma' — heat, not drought; default |
| `AB_TinkleGrass` | `BURST` | the_forge | ash-skirt ground cover; default |
| `AB_FirevineTree` | `BURST` | the_forge | pyroclastic donor tree; default |
| `IronScruff_PrimordialGrass` | `BURST` | the_forge | geyser flora; default |
| `IronScruff_PrimordialTallGrass` | `BURST` | the_forge | as PrimordialGrass |
| `IronScruff_Bindweed` | `BURST` | the_forge | as PrimordialGrass |
| `AB_GlowingGrass` | `BURST` | forsaken_crags | glow-carpet grass; nothing refuses water. Reachable by irrigation only (crags trickle is below threshold) |
| `AB_GiantGamma` | `BURST` | forsaken_crags | natural-sunlamp giant; default |
| `AB_ToxicGamma` | `BURST` | forsaken_crags | gamma family; default |
| `AB_GiantSeptimum` | `BURST` | forsaken_crags | fibre giant; default |
| `AB_WildRadagast` | `BURST` | forsaken_crags | glow-berry; default |
| `AG_Gamma` | `BURST` | forsaken_crags | gamma family; default |
| `AG_Septimum` | `BURST` | forsaken_crags | septimum family; default |
| `Plant_GrayGrass` | `BURST` | wasteland | Biotech pollution grass — POLLUTION-adapted, which is not the Contagion's contamination; default. Inert on the brine tile |
| `Plant_Toxipotato` | `BURST` | wasteland | mutant crop gone feral; default |
| `Plant_TreePolux` | `BURST` | wasteland | polux tree; default |
| `VRE_PoluxBush` | `BURST` | wasteland | polux kin; default |
| `AB_ToxiBulb` | `BURST` | wasteland | pollution-marked; default |
| `AB_WeepingToxberry` | `BURST` | wasteland | pollution-marked; default |
| `RG_Plant_ToxiGrass` | `BURST` | wasteland | pollution-marked; default |
| `RG_Plant_TallToxiGrass` | `BURST` | wasteland | pollution-marked; default |
| `AB_ToxiGrass` | `BURST` | the_blue_desert | pollution grass; default. Inert on hydrocarbon ground, Bursts if irrigated |
| `PoisonPlantTallGrass` | `BURST` | the_blue_desert | pollution grass; default |
| `PoisonShrub` | `BURST` | the_propane_lakes | pollution shrub; default |
| `RSW_Dunegrass / RSW_Scrubgrass / RSW_Starvine / RSW_EmberCarpet / RSW_Whirlbloom / RSW_VellaraBloom / RSW_SweetbarkTree` | `BURST` | (our defs, `RSW_DesertPortMisc_Plants.xml`) — in NO roster JSON | seven SW port plants with no roster row, so where they grow is UNMEASURED; by identity (grasses, vines, blooms, a sugar tree) none refuses water — default, pending a roster row |

### BURST? — CONTAMINATED: the owner's worked example, variant NOT yet ruled — 10 plants

| plant | variant | where rostered | why THIS plant |
|---|---|---|---|
| `AB_HalfAlienTree` | `BURST?` | the_contagion | 'the half-transformed trees — the infection front, advancing in Blooms, burned back in Burns'. THE contaminated plant. Whether its burst is a red spore puff and whether a Burn cooks its charge is the trait question he redirected — OPEN |
| `AB_AlienTree_Polluted` | `BURST?` | the_contagion | donor mutated variant, front-line texture; contaminated — OPEN as above |
| `AB_AlienTree` | `BURST?` | the_contagion | ocular trees, the peaks; fully transformed — contaminated — OPEN |
| `AB_AlienGrass` | `BURST?` | the_contagion | ocular grass; contaminated — OPEN |
| `AB_RedLeaves` | `BURST?` | the_contagion | aberration, 'not even 100% carbon based'; contaminated — OPEN |
| `AB_RedPlantsTall` | `BURST?` | the_contagion | aberration; contaminated — OPEN |
| `AB_TentacularPlant` | `BURST?` | the_contagion | 'rattle before a Burn' — the plant already reads the sky, which is exactly why the Burn-defuse question belongs to it; contaminated — OPEN |
| `AB_GlobularPlant` | `BURST?` | the_contagion | drips red sap; contaminated — OPEN |
| `RUT_DyingCreep` | `BURST?` | (our def, `RUT_DyingCreep.xml`) — the creep pushed uphill | 'a tongue of red Contagion-creep… within hours it blackens and dies' — growDays 0.1. R-G5's under-a-day clause says it is exempt from the ×4 tier; whether the creep tongue can charge at all is part of the same OPEN trait question. Likely NONE; recorded here so it is not forgotten |
| `RUT_RustPuff` | `BURST?` | the_contagion (moved from the_rot 2026-09-20) | 'bursts at a touch into a cloud of rust-coloured spores… hatches ocular creature' — a puffball that ALREADY bursts. Fungal by def (would be NONE) but moved into the Contagion as a contaminated thing; which wins is OPEN with the rest of the class |

**Why the contaminated class is `BURST?` and not a fourth ruled variant:** the owner named
"plants that are contaminated" as the reason the axis is the plant, but the only question
put to him about them (does a clear-sky Burn cook a charging plant?) was asked as a
biome question and redirected, not answered. Until it is asked again AS A PLANT TRAIT
— *does a contaminated plant's charge die under UV?* and *is its chaff a spore filth that
applies Contagion-touched?* — these ten run the ruled default. Card owed:
`EXPLOSIVE_PLANT_GROWTH_1` (see `## UNMEASURED`).

**Three emergent consequences worth knowing, none of them a variant:**
1. The permanently-soaked Greentide contains three default-BURST plants (chak-root, hubba
   gourd, tooke trap) that will pop on every charge. That is the ruling — *"a non-jungle
   plant growing in the Greentide does not [glut]"* — and whether the Greentide roster
   wants them at their current commonality is `the_greentide.json`'s question.
2. The Webwork's Churn needs no rule: it is `RG_Plant_TropicalChokevine` and `AB_TangleTea`
   running the default Burst with zone-indifferent sowing.
3. The Weeping Stones truce-pool card (#5) is half-defused by genetics: the margin plants
   are GLUT and shed quietly even if pools soak. Only a sown non-native beside a pool
   could pop there.

## Roster — plants that deliberately do NOT

`NONE`: never acquires SOAKED. Grouped by the identity reason; every plant named is on the planet by a roster row or is a def we ship.

| plant(s) | where rostered | why NOT — the plant's identity |
|---|---|---|
| Plant_Ambrosia | weeping_stones | R-G5 exempt — a deliberately scarce drug source |
| RUT_PaleTree | (our def, RotSporeKit) — the_rot new_defs 'pale tree' | anima reskin; R-G5 exempt (ritual pacing, not botany) |
| RUT_PaleMoss | (our def) | grows only under the pale tree; exempt with it |
| RSW_Ollim | (our def, `RSW_ExtremeDesertSignatureFlora.xml`) | 400-day bone-white deep-desert tree grown 'where the faintest hint of buried moisture fed a single cell' — its identity is the opposite of fast growth; deep_desert.md HARD BAN 4 in plant form |
| RSW_LightPipeNub | (our def) | 'not a leaf and it has never been one' — silica glass; no water metabolism |
| (new) glass-nub light-pipe flora / silverbole | dune_sea new_defs | deep-desert signature flora; HARD BAN 4 |
| AB_GiantStikehr | dune_sea + deep_desert, forsaken_crags | 'dry standing form' — a drought form does not charge, in the crags either |
| RUT_SweetlineTree | (our def, AshkarrFlora) — arid_shrubland new_defs | 'a single ancient giant, centuries old, growing only where the moisture-light trade balances exactly' — as the ollim: its identity is balance, not surge |
| AB_GargantuanLithops | the_cracked_lands | stone-mimic succulent — a water-HOARDER. Hoarders store the soak instead of spending it; they never charge. This is the owner's 'adaptation to… lack of water' axis |
| RG_Plant_CrimsonCushion | arid_shrubland | cushion form = hoarder |
| (new) ultracactus | desert new_defs | cactus = hoarder |
| Plant_MagmaCactus | the_forge | cactus = hoarder (Odyssey) |
| RUT_ScorchedStars | the_scarlands, wasteland | 'rounder cacti covered in sharp spines' — hoarder |
| RUT_TreeMartyr | poison_forest | 'yucca-related plant adapted to poisoned soils' — a yucca is a hoarder, and its weeping form 'sweats' water it is holding in |
| (new) staggerseed cycle plant | desert new_defs | its own corpse-dispersal cycle mechanic; never double-book a plant that already has a life-cycle event |
| (new) transparent fractal flora (ferns, dandelion-heads, fuzzballs) | the_blue_desert new_defs | each is already a butane charge with its own warm-detonation comp — the same rule: a plant that already detonates is not given a second detonation |
| AB_CrystalHorn / AB_CrystalFlower / AB_FrostLeaf / AB_RimeNodules | the_blue_desert, the_propane_lakes, poison_forest | crystal flora 'regrows daily from the fuel snow' — hydrocarbon-fed, not water-fed; water is not their trigger |
| AB_RavenNettle / AB_RedBugloss / AB_GiantToxicFlower / (new) dark crust phototroph films | poison_forest (RedBugloss also the_webwork) | terminator phototrophs — black/red, sealed-world palette. R-G3 restated as genetics: their identity is trace-water adaptation, so they stay stunted, and RedBugloss stays inert in the Webwork too |
| AB_GiantAgariTox | poison_forest | toxic fungal form — fungal |
| every `RUT_*` Rot plant: Skulltop, Dewshrooms, FruitingBodies, Nuitae(+Marsh), Wrinklecap(+Marsh), Arpeau, GreenArpeau, Nogtyl(+Marsh), FlakespireFungus, Pusmelon, Sagecrust, BleedingTooth, CrimsonCap, GreyLady, Shinecap, Brightbell, VioletWimple, MortalMorelPlant(+Growable), MoonlessStripesPlant, DulcisPlant, BlastpodShroom, FurnaceCap, AgelessCap, RegenerantVeil, EuphoricCrown, FalseFruit | the_rot, weeping_stones (Dewshrooms), the_miasma (Nogtyl), the_forge (Sagecrust) | FUNGAL. The soak trigger is water; the Sheen/milk is not water (taxonomy), and a fungus in the Miasma or on the Forge is still a fungus. Nogtyl 'grows fast enough to see' by its own def — that is its identity already, not this engine. BlastpodShroom's volatile pods are its own thing |
| every `AB_*` Rot donor fungus: AgaricusDomeCap, Agarilux, AgariluxPrime, GiantAgarilux, GlowingAgarilux, ArbuscularMycorrhiza, Bryolux, DribblingCap, Glowstool, LilacBeacon, RecurvedStropharia, SlimyPholiota, WitchesOyster | the_rot | fungal, as above |
| (new) tea-source guardian mushrooms | the_rot new_defs | fungal, and a defender-plant comp of their own |
| every Lantern Deeps plant: RUT_DeepMycelium, ZivvitTaper, QuorrFern, OsskBramble, BrellikBulb, TwitchingPuffer, ThrakkCap, PrennaLace, VellokReed, KuvraSpout, NurrikGill, Lanternstone_Sowable | (our defs, `RUT_DeepFlora.xml`, `RUT_LanternstoneSowable.xml`) — injection layer | fungal/crystal — 'what the Deeps have instead of undergrowth'. The aquatic ones (Vellok, Kuvra, Nurrik) live IN water: a permanently-wet fungus that charged would be wallpaper, and it is a fungus anyway. TwitchingPuffer already puffs |
| RUT_HeatsinkFungus | the_forge | fungus (tree-class) |
| RUT_Plant_Wick / AB_TarPuddle / (new) edge chemotroph ring flora | the_sump | 'feeds directly on the tar's own chemistry rather than the sun' — chemotrophs; water is not their input |
| (new) welcome-blanket thermophile mats | the_scald new_defs | mats on boiling saline; saline never soaks, and a mat has no 'top' |
| (new) the Glowers | the_scarlands new_defs | radiotrophic crust — radiation is the input |
| (new) radiotroph flora (dosimeter-lawn, vault-root trees) | wasteland new_defs | radiotrophic — as the Glowers |
| (new) chemical frosts ambiguously alive | nightside_ice new_defs | frost; 'does not grow' |
| (new) pillar-mason / mold-mat roof organism / salt-rimed blade flora (both seas) | terminator_sea + deeps new_defs | saline monocultures; salt kills the trigger |
| (new) weep-mat / drip-garden corduroy mats | weeping_stones new_defs | a mat; no top, and dew-quantity water |
| (new) parasitic root-mat flora | the_webwork new_defs | terrain/art, a mat |
| (new) Greatbole living tower | the_greentide new_defs | owned whole by GREENTIDE_MECHANICS_1 (mineable heartwood, regrowth crush, sealant) — the giant's growth is that item's C#, and the FALL is the kit's; never double-book |
| RUT_Placeholder_GreentideGiantTree | (our def, placeholder) | placeholder for the Greatbole; inherits its NONE, and 'never quite stable on its own roots' is the kit's fall |
| RUT_TwinkleSpikeTestPlant | (our def) | test article, 'do not place in the campaign' |
| (new) sweetline trees / wreck-shade flora pockets / seep-oil deposits | arid_shrubland, fall_line, the_fever_wood new_defs | the first is RUT_SweetlineTree above; the other two are authoring/terrain, not species |

## Counts

Tallied from the tables above by the script that rendered them (not by hand).

| variant | plants |
|---|---|
| `GLUT` | 13 |
| `FLUSH` | 2 |
| `SLIME` | 9 |
| `TINDER` | 3 |
| `BURST` (ruled default) | 58 rows (one row bundles 7 un-rostered RSW_ port plants) |
| `BURST?` (contaminated, ruling owed) | 10 |
| **gets the mechanic** | **95 rows** |
| `NONE` (deliberately excluded) | **98 named plants/commissions** in 36 rows |

Of the three variants ruled 2026-09-20: GLUT 13, SLIME 9, TINDER 3. FLUSH (ruled
2026-09-10) 2. Everything else that soaks is the ruled default.

## UNMEASURED

Stated as ignorance, not as zero.

- **Which defName the game loads for the four SW port crops** — the rosters say
  `Plant_Chakroot_Wild` / `Plant_HubbaGourd_Wild` / `Plant_Nysyllin_Wild` / `Plant_Bloddle`;
  our defs say `RSW_Plant_*`. Needs the def dump (`measure`), not this file.
- **`Plant_Bubblespore_Wild`'s description** (SW donor, not in our defs) — GLUT assigned on
  roster placement alone.
- **Where the seven `RSW_DesertPortMisc_Plants.xml` plants grow** — no roster row names them.
- **Whether donor trees (mangroves, jungle tree, slimy trees) soak and charge the same way
  understory does** — the design doc treats trees generically except for the Greentide's
  kit-owned FALL; nothing here changes that, and no engine member was checked (RimSage is
  Desktop-only per CLAUDE.md; no engine claim is made in this file).
- **Not ruled (cards owed on `EXPLOSIVE_PLANT_GROWTH_1`):**
  1. The contaminated trait — does UV/a Burn kill the charge; is the chaff a spore filth
     that applies Contagion-touched? (ten plants sit at `BURST?` pending this.)
  2. Does the Greentide extract, "which charges plants to burst", override a GLUT plant to
     BURST? (Recommended yes — the extract is the deliberate weaponised form; unruled.)
  3. Card #5 (do truce pools soak) is still open but is now low-stakes — see emergent
     consequence 3.
