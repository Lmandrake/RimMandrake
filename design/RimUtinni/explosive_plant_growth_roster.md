# Explosive plant growth — per-plant roster

_Generated 2026-09-21 against the owner's 2026-09-21 ruling set (`design/Jawa/worldbuilding/explosive_plant_growth_design.md` §9, rulings 1–7, recorded in §0, §3, §4 and §7). Regenerated, not edited: the plant list and the per-row evidence carry over from the 2026-09-20 roster; every variant is re-derived under ruling 4 (water scarcity decides). Supersedes the 2026-09-20 assignment in full._

Item: `EXPLOSIVE_PLANT_GROWTH_1`. Design only; no def, mod or C# edited.

## The rulings this roster obeys

**The axis** — owner, 2026-09-20 (design doc §8), verbatim:

> *"It's less about the biome and more about the plants IN that biome having different
> behaviors. Still comes out to differences between biomes, but it really should be
> driven all by plant genetics / identity / adaptation to the intense sunlight and lack
> of water. So this is about 'plants that are contaminated'."*

**The rule on that axis** — owner, 2026-09-21 (design doc §3, ruling 4): **water scarcity
decides.** A plant whose own identity is adaptation to SCARCE water gets `BURST` — it gets
one chance in years and spends everything on it. A plant that lives permanently wet gets
`CHURN`. The driest places hold the most violence; the wet jungles hold none. And ruling 1:
broad growth, rare drama — nearly every plant swells when soaked; only a designed minority
detonates.

So: **the terminal moment is a property of the plant def, never of the BiomeDef.** This
file lists plants, one row each, and assigns each a variant on the strength of that plant's
own identity — its def, its label/description, its sheet role, and above all **how it
relates to water**. Where the same plant grows in several biomes it carries the same variant
everywhere. `where rostered` is evidence of what the plant is, never the reason. ⛔ There is
no per-biome column and there must never be one.

**Ruling 6 as it lands on this file:** plants in the Greentide, the Miasma and the Fever
Wood run at ×10 ambient and never detonate (design doc §0). Under the plant axis that is a
consequence, not an input: every plant those rosters carry is a wet-living plant and so
churns by ruling 4 anyway. The one seam — a dry-adapted plant rostered INTO a wet biome — is
named in the hard-calls section, not papered over here.

Standing carve-outs, unchanged, because they are ALSO plant-identity facts once read that
way:
- `PLANT_GROWTH_SPEC.md` R-G5 exempt list (anima, Gauranlen, ambrosia, quest-timed plants,
  and any plant whose `growDays` is already under ~1 day) — an exempt plant never soaks.
- R-G3 / R-H2b: the terminator (poison forest) stays stunted; `biomes/deep_desert.md` §6
  HARD BAN 4: no fast growth in the deep desert. In plant terms: the plants whose identity
  IS "adapted to no water" do not charge.
- Fungal plants do not soak: the Sheen is not water (taxonomy).

🄸 INVENTED, carried from the 2026-09-20 roster and NOT an owner ruling: the **hoarder**
reading of the water axis — a succulent stores the soak instead of spending it, so it never
charges (`NONE`). It is the first entry in the hard-calls section because ruling 4 could
be read the other way.


## The variants, as plant properties

All keys are plant properties. Ruled dates are the design doc's.

| key | what the plant does at the top | ruled | this file |
|---|---|---|---|
| `CHURN` | **the default** — swell past natural size → strain → crack open and slump; drops its produce and the husk; sows a ring of sprouts that grow and split in their turn. Endless. **Respects built ground**: sprouts take fields, stockpiles and open dirt, never floors or interiors. Threatens nothing directly | 2026-09-21 | the large majority |
| `BURST` | **the rare violent top** — swell → tremble → pop; chaff shockwave, minor blunt/cut + knockdown (lethality ceiling: injury+knockdown); premium produce scattered; husk as low-grade fuel; **the sown ring ignores zones** | 2026-09-20 (shape), 2026-09-21 (who: dry-adapted only) | dry-adapted plants only |
| `TINDER` | a Burst whose debris is fuel — husk, chaff, a ring of quickgrass | 2026-09-20 | fire-loop plants |
| `RUPTURE` | **the contaminated top** — not a pop but a rupture: a spreading red gas/fog cloud; emits red slimes and ocular entities plus little sprouts around it; vile; extra mutation hediffs for any pawn in the cloud without 100% vacuum protection. The plant is manufacturing, not reproducing | 2026-09-21 | contaminated plants |
| `SLIME` | a top whose sown ring turns the ground to slime rather than sprouts | 2026-09-20 | slime-fed plants |
| `FLUSH` | no surface spectacle; growth runs INSIDE the giant — bark swells, boughways re-route, thornbug nectar glut | 2026-09-10 | the Fever Wood giants |

⚠️ **`GLUT` is retired** (owner, 2026-09-21): the fruit dump is part of the default Churn.
Every plant that carried `GLUT` on 2026-09-20 is now a `CHURN` plant with a heavy produce
yield, and its row says so.

And the non-variant:

| key | meaning |
|---|---|
| `NONE` | this plant never acquires SOAKED; it grows at the ambient tier only (×4 planet-wide, ×10 in the three wet biomes), or is exempt from that too where the spec says so |

🄸 INVENTED, this file: "heavy produce yield" on a former-GLUT row means the Churn's drop is
sized as the old glut was — a crop-scale dump, not a single plant's harvest. The number is
build's.


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

Re-read 2026-09-21 for the water-relationship calls (descriptions quoted in rows):
`RSW_DesertPortMisc_Plants.xml`, `RSW_DesertPortB_Plants.xml`, `RUT_PollutedFlora.xml`,
`RUT_RotSporeKit_Flora.xml` (RustPuff), `PLANT_GROWTH_SPEC.md` R-G5, and the Alpha Biomes
workshop defs for `AB_HardyGrass` and `AB_Aaklac`.

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


## Roster — plants that get the mechanic

One row per plant (or per unbuilt `(new)` sheet commission). `where` is where the rosters place it — evidence only, never the reason. The reason is always the plant, and the deciding question is always the plant's relationship to water.

### BURST — dry-adapted: one chance in years, spent all at once — 7 plants

The rare top. A plant is here only when its own def or sheet says its identity is adaptation to scarce water AND it spends rather than stores (a hoarder is `NONE`, see the carve-out above).

| plant | variant | where rostered | why THIS plant |
|---|---|---|---|
| `(new) bloom crop` | `BURST` | the_cracked_lands new_defs | the flagship: born in §10b, contracted to `RUT_BloomBurst`. A crop that exists only because a flood came after years of nothing and must seed before the ground cracks again — the type specimen of "one chance in years, spend everything". The boom-bust die-off and the bloom harvest are the sheet's, not a variant |
| `Plant_HubbaGourd_Wild` | `BURST` | desert, the_greentide | def (`RSW_Plant_HubbaGourd_Wild`, RSW_ twin): 'a hardy gourd crop native to the planet Tatooine… exported to other worlds with arid environments where it thrived in such harsh conditions' — a dry-world staple whose identity IS thriving on scarce water; a gourd is a spender (fruit, not a water store). ✅ **RULED 2026-09-21** — it keeps `BURST` in the Greentide. Owner: *"A dry plant in the greentide can burst."* There is no never-detonate ground; the wet biomes are quiet because of what grows there. |
| `RG_Plant_AridGrass` | `BURST` | arid_shrubland | ReGrowth def: 'wild grass. Grows in arid regions where there is little light and minimally fertile ground' — word-for-word the same habitat text as `RSW_Scrubgrass`, so it gets the same call: arid regions named as habitat is the water-scarcity identity. (The sheet's 'struggling grass' is what a spender looks like between soaks) |
| `RSW_Scrubgrass` | `BURST` | (our def, `RSW_DesertPortMisc_Plants.xml`) — in NO roster JSON | def: 'wild grass that grows in arid regions where there is little light and minimally fertile ground' — the description names arid regions as its habitat, which is the water-scarcity identity. Contrast `RSW_Dunegrass` (CHURN below), whose description says 'grows anywhere' |
| `RUT_TwistingThornwood` | `BURST` | poison_forest, the_cracked_lands | def (`RUT_PollutedFlora.xml`): 'a large species of tree found in polluted arid environments' — the family's stated habitat is arid; the thorn family is the Cracked Lands' own violence. Not a hoarder (a thorn tree, no succulence). Inert in the poison forest (never soaks) |
| `RUT_TwistingThornweed` | `BURST` | the_cracked_lands | 'a bush-sized plant related to the thornwood tree, hardy enough to survive on heavily polluted ground' — same family, same arid identity; a thornweed ring sown into a doorway is the encroachment the Burst is for |
| `RUT_TwistingThorngrass` | `BURST` | the_cracked_lands | 'similar to grass yet covered in small thorn-like structures… related to the twisting thornwood and thornweed' — the family carries the identity; grass-scale burst |

### TINDER — fire-loop genetics (a Burst whose debris is fuel) — 3 plants

Burst-shaped, so these must also be dry-adapted under ruling 4 — and they are: the Pyrelands fire loop (R-H3) is a rain-flush-then-cure cycle, a scarce-water strategy by definition.

| plant | variant | where rostered | why THIS plant |
|---|---|---|---|
| `RM_FE_Plant_Quickgrass` | `TINDER` | the_pyrelands (c=4.0) | the Rakatan feral forage crop whose days-clock green→gold IS R-H3's fire loop — flush on the rain, cure to fuel, burn, repeat: a dry-adapted spender whose burst debris (husk, chaff, a quickgrass ring) is the fire's supply line in one event |
| `RM_FE_Plant_EmberGrass` | `TINDER` | (our def, `src/RimMandrake/Pyrelands`) — not in the roster JSON | fire-ecology grass by name and kit; same genetics as quickgrass |
| `RM_FE_Plant_ScorchFruit` | `TINDER` | the_pyrelands new_defs (built) | spoils-in-a-day scorch-fruit wired into FireEcologyHook.cs; a fire-cycle plant, so its burst debris is fuel |

### RUPTURE — contaminated: the bioweapon at open throttle — 9 plants

Ruled 2026-09-21. The question the 2026-09-20 roster held these on (does a Burn cook the charge; is the chaff a spore filth) is answered by the ruling's shape: a contaminated plant does not burst at all, it ruptures — red gas/fog cloud, red slimes, ocular entities, little sprouts, mutation hediffs without 100% vac protection. Water relationship is irrelevant here: contamination overrides the scarcity axis, because the plant is not reproducing but manufacturing.

| plant | variant | where rostered | why THIS plant |
|---|---|---|---|
| `AB_HalfAlienTree` | `RUPTURE` | the_contagion | 'the half-transformed trees — the infection front, advancing in Blooms, burned back in Burns'. THE contaminated plant: the owner's own worked example of "plants that are contaminated" |
| `AB_AlienTree_Polluted` | `RUPTURE` | the_contagion | donor mutated variant, front-line texture; contaminated |
| `AB_AlienTree` | `RUPTURE` | the_contagion | ocular trees, the peaks; fully transformed — contaminated. The ocular entities the rupture emits are what this tree already is |
| `AB_AlienGrass` | `RUPTURE` | the_contagion | ocular grass; contaminated |
| `AB_RedLeaves` | `RUPTURE` | the_contagion | aberration, 'not even 100% carbon based'; contaminated |
| `AB_RedPlantsTall` | `RUPTURE` | the_contagion | aberration; contaminated |
| `AB_TentacularPlant` | `RUPTURE` | the_contagion | 'rattle before a Burn' — already reads the sky; contaminated. Whether a Burn defuses a charging rupture is no longer a roster question: the ruling gives the top, and a Burn-vs-charge interaction is build's to propose |
| `AB_GlobularPlant` | `RUPTURE` | the_contagion | drips red sap; contaminated — the sap is the red cloud in a droplet |
| `RUT_RustPuff` | `RUPTURE` | the_contagion (moved from the_rot 2026-09-20) | def (`RUT_RotSporeKit_Flora.xml`): 'a large puffball mushroom that bursts at a touch into a cloud of flaky, rust-coloured spores'; the owner's move note in `the_contagion.json`: *'hatches occular creature when damaged'*. A plant that already emits a cloud and hatches an ocular thing has the rupture's shape by the owner's own hand — contamination overrides its fungal def (hard call, listed) |

### SLIME — slime-fed genetics (the ring converts ground) — 9 plants

Unchanged from 2026-09-20. These plants live in slime floodwater (`slime_flood`), so under ruling 4 they are wet-living; their top is the SLIME variant regardless. 🄸 INVENTED, this file: read SLIME as Churn-shaped (split, not pop) with the ring converting ground — the design doc's variant table no longer says which shape it takes (see the design-doc findings in the hard-calls section).

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

### FLUSH — the giants (growth runs inside the trunk) — 2 plants

Unchanged from 2026-09-20. Both are Fever Wood plants, so ruling 6 (×10 ambient, never detonate) and FLUSH (no surface spectacle) agree by construction.

| plant | variant | where rostered | why THIS plant |
|---|---|---|---|
| `Plant_HydenockTree_Wild` | `FLUSH` | the_fever_wood, the_greentide | SW wroshyr-analog giant hardwood; the Fever Wood canton works its crown. A giant's growth runs INSIDE — bark swells, boughways re-route. Carries FLUSH in the Greentide too (the kit's fall is separate and size-triggered) |
| `AB_KeeningCordax` | `FLUSH` | the_fever_wood, poison_forest | 'interim single-tile body for the tower-trunks' — it IS the Fever Wood giant until the authored tree lands, so it carries the giant's variant. In the poison forest it never soaks (trace water), so FLUSH there is inert — the model working as ruled |

### CHURN — the default: swell, split, die, fruit, sow, repeat

Everything that soaks and is neither dry-adapted, contaminated, slime-fed, fire-loop nor a giant. The Churn respects built ground, so none of these threatens a wall; the pressure is the churn itself. Sub-grouped by the water reading that put the plant here.

**Wet-living — heavy produce yield (the former `GLUT` rows).** Each of these was assigned GLUT on 2026-09-20 as "soak-native genetics: sheds and resets, never pops". Under the retired key that is exactly a Churn with a heavy produce yield, and the reasoning stands unchanged.

| plant | variant | where rostered | why THIS plant |
|---|---|---|---|
| `Plant_MujaFruit_Wild` | `CHURN` (heavy produce, former GLUT) | the_greentide | SW fruit bush rostered only under the Greentide fruit law; its identity IS the fruit that yearns to be eaten — a fruit-bearer that evolved under permanent soak: wet-living, so it churns, and the Churn's fruit drop is a glut |
| `Plant_JoganTree_Wild` | `CHURN` (heavy produce, former GLUT) | the_fever_wood, the_greentide | SW fruit tree; fruit-crown economy on both sheets. Fruit-crowned jungle native → wet-living. Its trunk's fate (the Greentide crack-and-FALL) is the Greentide kit's size-triggered event, not this engine's |
| `AB_SugarFamewort` | `CHURN` (heavy produce, former GLUT) | the_greentide | 'sweet free-calorie groundcover' — the fruit law in groundcover form; wet-living |
| `RUT_GiantLeaf` | `CHURN` (heavy produce, former GLUT) | the_fever_wood, the_greentide | `RUT_CavernsFlora.xml`: 'grows low in the jungle understory, broad enough to shelter a grown man from the rain' — rain is its habitat, so permanent wet is its baseline |
| `Plant_FelucianGlowspore_Wild` | `CHURN` (heavy produce, former GLUT) | the_greentide | Felucia jungle canopy tree (SW donor); Felucia is canon's fungal rain-jungle — permanent wet is its genetics. (Fungal in canon, tree-class in def: it is rostered as a soaking jungle tree, not on the Sheen; the fungal carve-out is about the Rot's not-water) |
| `AB_JungleTree` | `CHURN` (heavy produce, former GLUT) | the_greentide, the_webwork | Alpha Biomes jungle canopy; wet-living |
| `Plant_Bubblespore_Wild` | `CHURN` (heavy produce, former GLUT) | the_greentide | rostered as Greentide floor cover only; its def description is UNMEASURED here (SW donor, not in our defs). CHURN is the default, so this is the safe assignment either way; confirm from the def dump before wiring the yield |
| `AB_MangroveTree` | `CHURN` (heavy produce, former GLUT) | the_miasma | 'the trees run the plumbing' — a mangal stands in water permanently: the type specimen of wet-living. Mangroves drop propagules: that IS the Churn's sow step |
| `AB_MangrovePalm` | `CHURN` (heavy produce, former GLUT) | the_miasma | mangal family, as AB_MangroveTree |
| `AB_ParasiticMangrove` | `CHURN` (heavy produce, former GLUT) | the_miasma | mangal family, as AB_MangroveTree |
| `Plant_Reeds` | `CHURN` (heavy produce, former GLUT) | weeping_stones | water-margin blade; a margin native is wet-living. Consequence: even if the truce pools count as a soak (card #5, unruled), the reeds beside them churn quietly and never pop — the sacred water stays quiet by the plant's genetics, not by a biome exception |
| `(new) digestive-accelerant fruit` | `CHURN` (heavy produce, former GLUT) | the_greentide new_defs | the fruit that yearns, as a def of its own — the type specimen of the heavy-produce Churn |
| `(new) blade-flora with bladder-fruit` | `CHURN` (heavy produce, former GLUT) | weeping_stones new_defs | margin fruit-bearer; as Plant_Reeds |

**Wet-living or wet-tolerant by def — the jungle, marsh, moss and fern rows.**

| plant | variant | where rostered | why THIS plant |
|---|---|---|---|
| `Plant_Chakroot_Wild` | `CHURN` (heavy produce) | desert, the_fever_wood, the_greentide | def (`RSW_Plant_Chakroot_Wild`, RSW_ twin): 'grew in the marshlands of the planet Erysthes' — a marsh root is wet-living by its own text, whatever tile the desert roster puts it on. A root crop churning is the ruled water-for-food pump |
| `AB_Aaklac` | `CHURN` | desert, the_webwork | Alpha Biomes def: 'a rare, huge flower which can be found in the deepest jungles' — a deep-jungle flower, wet-living. (The 2026-09-20 row called it an 'alien arid form'; the def says the opposite) |
| `RG_Plant_TropicalChokevine` | `CHURN` | the_webwork | 'the thicket churns against itself — hostile vine mass'; tropical by name, wet-living. The Webwork sheet's own word for what this plant does is *churn* (§4c) — the default top IS the sheet's mechanic: split, sow a ring of chokevine in the gap you were using |
| `AB_TangleTea` | `CHURN` | the_webwork | churn understory, tangle-form; as chokevine |
| `Plant_TookeTrap_Wild` | `CHURN` | the_greentide, the_webwork | predatory SW jungle plant; nothing dry-adapted in it. A churn sowing a ring of traps is encroachment with teeth, on open ground only |
| `GRimMoss` | `CHURN` | the_cracked_lands | moss is a moisture plant by physiology — it grows where water lingers, the opposite of a scarce-water spender. Churn scale on a tiny plant is build's call |
| `AB_GreenRockFern` | `CHURN` | weeping_stones | a fern — shade-and-moisture form; wet-tolerant |
| `AB_Gomphoeria` | `CHURN` | the_fever_wood, the_webwork | alien groundcover; nothing in its identity refuses or hoards water — default |
| `AB_Iashiphus` | `CHURN` | the_fever_wood | alien groundcover; default |
| `(new) pale flowers (web-tracing bloom)` | `CHURN` | the_webwork new_defs | route-signal bloom; default |
| `(new) rainbow flora suite` | `CHURN` | the_miasma new_defs | 3–4 genuinely benign blooms (ban 2: never a trap) — a Churn that sows flowers; benign stays benign, and never detonates |

**Crops, herbs and generic forms — no water identity either way (the default by rule).**

| plant | variant | where rostered | why THIS plant |
|---|---|---|---|
| `Plant_Bloddle` | `CHURN` | dune_sea + deep_desert | def (`RSW_Plant_Bloddle`, RSW_ twin): 'grown in the hydroponic gardens' — a Tatooine crop, but its stated cultivation is water-fed, not drought-adapted. Inert on the deep-desert tile (HARD BAN 4, never soaks); churns where irrigated |
| `Plant_Nysyllin_Wild` | `CHURN` | arid_shrubland | def: 'a healing herb grown as a common crop plant across the galaxy' — a generalist crop; default |
| `Plant_HealrootWild` | `CHURN` | arid_shrubland | RimWorld herb; default |
| `Plant_Brambles` | `CHURN` | arid_shrubland | thorny holdout; a bramble ring on open dirt is encroachment; default |
| `Plant_Ripthorn` | `CHURN` | arid_shrubland | Biotech alien thorn, 'forbids rather than flees'; default with teeth |
| `Plant_Bush` | `CHURN` | arid_shrubland | generic shrub; default |
| `Plant_ShrubLow` | `CHURN` | arid_shrubland | stand-in for the fuzz; default until the fuzz def lands |
| `AB_HardyGrass` | `CHURN` | desert, the_cracked_lands | Alpha Biomes def: 'wild grass. Grows anywhere there is a little light and minimally fertile ground' — a generalist, not a dry specialist; 'hardy' is not 'adapted to scarce water' |
| `RG_Plant_CreepStern` | `CHURN` | arid_shrubland | alien low form; default |
| `RG_Plant_Dervish` | `CHURN` | arid_shrubland | alien low form; default |
| `(new) the fuzz` | `CHURN` | arid_shrubland new_defs | knee-high graze-adapted canopy plant — its stated adaptation is grazing pressure, not water; default |
| `(new) venomvine` | `CHURN` | arid_shrubland new_defs | fortress flora; its identity is defence, not water. A sown venomvine ring on open ground is the fortress growing |
| `(new) defending shade plants` | `CHURN` | desert new_defs | thorn/venom patch flora; identity is defence. Hard call: a desert patch plant may turn out dry-adapted when its def is written — the default holds until the def says so |
| `(new) twisted trees + shade-line grasses/mosses` | `CHURN` | the_cracked_lands new_defs | our own Cracked Lands vegetation, one commission mixing trees with shade-line mosses (moisture plants). Default until the defs land; hard call — the twisted trees may earn BURST on their own text |
| `AB_BloodBouquet` | `CHURN` | poison_forest, the_contagion | 'spine-armored seed rolls to the burn line and dies as fertilizer' — a seed-discharging plant, but nothing in it is a scarce-water adaptation; the rolling seed is the Churn's sow step in its native form. NOT contaminated: it is the Contagion's own uncontaminated seeder (hard call, listed). Inert in the poison forest |
| `RSW_Dunegrass` | `CHURN` | (our def, `RSW_DesertPortMisc_Plants.xml`) — in NO roster JSON | def: 'wild grass. Grows anywhere there is a little light and minimally fertile ground' — the label says dune, the description says generalist; the description is the identity (hard call, listed) |
| `RSW_Starvine / RSW_EmberCarpet / RSW_Whirlbloom / RSW_VellaraBloom / RSW_SweetbarkTree` | `CHURN` | (our defs, `RSW_DesertPortMisc_Plants.xml`) — in NO roster JSON | defs: 'takes a long time to grow, but is very frost-resistant' (×2), 'a beautiful bluish flower', 'a rare, huge flower… popular in gardening', 'a whimsical tree with a sugary trunk' — frost-, colour- and sugar-identities, none of them water; default, pending a roster row |

**Heat-, pollution- and glow-adapted — an adaptation that is not a water adaptation.**

| plant | variant | where rostered | why THIS plant |
|---|---|---|---|
| `Plant_Fireweed` | `CHURN` | the_forge | heat-proof fibre plant (Odyssey); heat-adapted is not dry-adapted — the Forge's plants are starved of water by rock, not shaped by drought. Reachable only by irrigation (the Forge's rain flashes off the rock) |
| `RUT_FireLavender` | `CHURN` | the_forge | 'adapted to survive off the glow of magma' — its adaptation is an energy source, not water |
| `AB_TinkleGrass` | `CHURN` | the_forge | ash-skirt ground cover; default |
| `AB_FirevineTree` | `CHURN` | the_forge | pyroclastic donor tree; default |
| `IronScruff_PrimordialGrass` | `CHURN` | the_forge | geyser flora — geyser water is its habitat, if anything wet-living; default |
| `IronScruff_PrimordialTallGrass` | `CHURN` | the_forge | as PrimordialGrass |
| `IronScruff_Bindweed` | `CHURN` | the_forge | as PrimordialGrass |
| `AB_GlowingGrass` | `CHURN` | forsaken_crags | glow-carpet grass; light-adapted, not water. Reachable by irrigation only (crags trickle is below threshold) |
| `AB_GiantGamma` | `CHURN` | forsaken_crags | natural-sunlamp giant; default |
| `AB_ToxicGamma` | `CHURN` | forsaken_crags | gamma family; default |
| `AB_GiantSeptimum` | `CHURN` | forsaken_crags | fibre giant; default |
| `AB_WildRadagast` | `CHURN` | forsaken_crags | glow-berry; default |
| `AG_Gamma` | `CHURN` | forsaken_crags | gamma family; default |
| `AG_Septimum` | `CHURN` | forsaken_crags | septimum family; default |
| `Plant_GrayGrass` | `CHURN` | wasteland | Biotech pollution grass — POLLUTION-adapted, which is neither the Contagion's contamination nor a water adaptation; default. Inert on the brine tile |
| `Plant_Toxipotato` | `CHURN` | wasteland | mutant crop gone feral; default |
| `Plant_TreePolux` | `CHURN` | wasteland | polux tree; default |
| `VRE_PoluxBush` | `CHURN` | wasteland | polux kin; default |
| `AB_ToxiBulb` | `CHURN` | wasteland | pollution-marked; default |
| `AB_WeepingToxberry` | `CHURN` | wasteland | pollution-marked; default |
| `RG_Plant_ToxiGrass` | `CHURN` | wasteland | pollution-marked; default |
| `RG_Plant_TallToxiGrass` | `CHURN` | wasteland | pollution-marked; default |
| `AB_ToxiGrass` | `CHURN` | the_blue_desert | pollution grass; default. Inert on hydrocarbon ground, churns if irrigated |
| `PoisonPlantTallGrass` | `CHURN` | the_blue_desert | pollution grass; default |
| `PoisonShrub` | `CHURN` | the_propane_lakes | pollution shrub; default |

**Emergent consequences worth knowing, none of them a variant:**
1. The Webwork's "churn" (sheet §4c) needs no rule at all now: it is `RG_Plant_TropicalChokevine` and `AB_TangleTea` running the default top, whose name is the sheet's word.
2. The Weeping Stones truce-pool card (#5) is defused by genetics: the margin plants churn and never pop even if pools soak.
3. The three wet biomes contain, by roster, exactly one Burst plant (`Plant_HubbaGourd_Wild` in the Greentide) and no TINDER or RUPTURE plant — so ruling 6 ("never detonate") holds by plant identity — and the one apparent exception is the correct behaviour, ruled 2026-09-21: a dry plant in the Greentide bursts.
4. The Contagion holds all nine RUPTURE plants and one CHURN plant (`AB_BloodBouquet`); the poison forest's shared rows are inert there (never soaks).

## Roster — plants that deliberately do NOT

`NONE`: never acquires SOAKED. Grouped by the identity reason; every plant named is on the planet by a roster row or is a def we ship.

| plant(s) | where rostered | why NOT — the plant's identity |
|---|---|---|
| Plant_Ambrosia | weeping_stones | R-G5 exempt — a deliberately scarce drug source |
| RUT_PaleTree | (our def, RotSporeKit) — the_rot new_defs 'pale tree' | anima reskin; R-G5 exempt (ritual pacing, not botany) |
| RUT_PaleMoss | (our def) | grows only under the pale tree; exempt with it |
| **RUT_DyingCreep** | (our def, `RUT_DyingCreep.xml`) — the creep pushed uphill | 'a tongue of red Contagion-creep… within hours it blackens and dies' — growDays 0.1. R-G5's under-a-day clause exempts it, and the carve-out says an exempt plant never soaks. Contaminated by fiction, but it has no charge to rupture with: it is already dying on arrival. Moved here from the 2026-09-20 `BURST?` group (hard call, listed) |
| RSW_Ollim | (our def, `RSW_ExtremeDesertSignatureFlora.xml`) | 400-day bone-white deep-desert tree grown 'where the faintest hint of buried moisture fed a single cell' — its identity is the opposite of fast growth; deep_desert.md HARD BAN 4 in plant form |
| RSW_LightPipeNub | (our def) | 'not a leaf and it has never been one' — silica glass; no water metabolism |
| (new) glass-nub light-pipe flora / silverbole | dune_sea new_defs | deep-desert signature flora; HARD BAN 4 |
| AB_GiantStikehr | dune_sea + deep_desert, forsaken_crags | 'dry standing form' — a drought form that stands, not spends; 🄸 hoarder reading (see hard call 1) |
| RUT_SweetlineTree | (our def, AshkarrFlora) — arid_shrubland new_defs | 'a single ancient giant, centuries old, growing only where the moisture-light trade balances exactly' — as the ollim: its identity is balance, not surge |
| AB_GargantuanLithops | the_cracked_lands | stone-mimic succulent — a water-HOARDER. 🄸 Hoarders store the soak instead of spending it; they never charge (hard call 1) |
| RG_Plant_CrimsonCushion | arid_shrubland | cushion form = hoarder (🄸, hard call 1) |
| (new) ultracactus | desert new_defs | cactus = hoarder (🄸, hard call 1) |
| Plant_MagmaCactus | the_forge | cactus = hoarder (Odyssey) (🄸, hard call 1) |
| RUT_ScorchedStars | the_scarlands, wasteland | 'rounder cacti covered in sharp spines' — hoarder (🄸, hard call 1) |
| RUT_TreeMartyr | poison_forest | 'yucca-related plant adapted to poisoned soils' — a yucca is a hoarder, and its weeping form 'sweats' water it is holding in; and it is a terminator plant besides (never soaks) |
| (new) staggerseed cycle plant | desert new_defs | its own corpse-dispersal cycle mechanic; never double-book a plant that already has a life-cycle event |
| (new) transparent fractal flora (ferns, dandelion-heads, fuzzballs) | the_blue_desert new_defs | each is already a butane charge with its own warm-detonation comp — the same rule: a plant that already detonates is not given a second detonation |
| AB_CrystalHorn / AB_CrystalFlower / AB_FrostLeaf / AB_RimeNodules | the_blue_desert, the_propane_lakes, poison_forest | crystal flora 'regrows daily from the fuel snow' — hydrocarbon-fed, not water-fed; water is not their trigger |
| AB_RavenNettle / AB_RedBugloss / AB_GiantToxicFlower / (new) dark crust phototroph films | poison_forest (RedBugloss also the_webwork) | terminator phototrophs — black/red, sealed-world palette. R-G3 restated as genetics: their identity is trace-water adaptation, so they stay stunted, and RedBugloss stays inert in the Webwork too |
| AB_GiantAgariTox | poison_forest | toxic fungal form — fungal |
| every `RUT_*` Rot plant: Skulltop, Dewshrooms, FruitingBodies, Nuitae(+Marsh), Wrinklecap(+Marsh), Arpeau, GreenArpeau, Nogtyl(+Marsh), FlakespireFungus, Pusmelon, Sagecrust, BleedingTooth, CrimsonCap, GreyLady, Shinecap, Brightbell, VioletWimple, MortalMorelPlant(+Growable), MoonlessStripesPlant, DulcisPlant, BlastpodShroom, FurnaceCap, AgelessCap, RegenerantVeil, EuphoricCrown, FalseFruit | the_rot, weeping_stones (Dewshrooms), the_miasma (Nogtyl), the_forge (Sagecrust) | FUNGAL. The soak trigger is water; the Sheen/milk is not water (taxonomy), and a fungus in the Miasma or on the Forge is still a fungus. Nogtyl 'grows fast enough to see' by its own def — that is its identity already, not this engine. BlastpodShroom's volatile pods are its own thing. (`RUT_RustPuff` is the one Rot-kit fungus NOT here: the owner moved it into the Contagion as a hatcher of ocular things, so it ruptures) |
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

Tallied from the tables above by the script that rendered them (not by hand). "rows" counts table rows; "plants" expands the one bundled row (five un-rostered RSW_ port plants in one CHURN row).

| variant | rows | plants |
|---|---|---|
| `CHURN` (default; 13 of them heavy-produce former GLUT) | 66 | 70 |
| `BURST` (dry-adapted) | 7 | 7 |
| `TINDER` (Burst-shaped, fire-loop) | 3 | 3 |
| `RUPTURE` (contaminated) | 9 | 9 |
| `SLIME` | 9 | 9 |
| `FLUSH` | 2 | 2 |
| **gets the mechanic** | **96** | **100** |
| `NONE` (deliberately excluded) | 37 rows | 99 named plants/commissions |

Detonating tops (BURST + TINDER) are 10 of 100 plants — 10%. Ruling 1's "designed minority" is met; the Churn is 70% of everything that soaks.

## What changed from the previous assignment

**Before → after, per key** (2026-09-20 roster → this file; plants, bundled rows expanded):

| key | before | after | movement |
|---|---|---|---|
| `BURST` | 58 | 7 | 51 → CHURN; `RG_Plant_AridGrass` and `RSW_Scrubgrass` stay/arrive on their own def text; the thorn family and the hubba gourd stay; the bloom crop stays |
| `BURST?` | 10 | 0 | 9 → RUPTURE, 1 (`RUT_DyingCreep`) → NONE |
| `GLUT` | 13 | 0 (retired) | 13 → CHURN, each marked heavy produce |
| `CHURN` | — | 70 | new default |
| `RUPTURE` | — | 9 | new |
| `SLIME` | 9 | 9 | unchanged |
| `TINDER` | 3 | 3 | unchanged |
| `FLUSH` | 2 | 2 | unchanged |
| `NONE` | 98 | 99 | +`RUT_DyingCreep` |

Two rows were re-read against their defs and found to have been misdescribed on 2026-09-20: `AB_Aaklac` ("alien arid form" — the def says "the deepest jungles") and `AB_HardyGrass` (the def says "grows anywhere", not hardy-arid). Both are CHURN with corrected evidence. The seven-plant RSW port bundle is split into three rows because its plants no longer share a variant.

**The hard calls** — where a human should check the judgement:

1. 🄸 **The hoarders stay `NONE`, not `BURST`** — `AB_GargantuanLithops`, `RG_Plant_CrimsonCushion`, `(new) ultracactus`, `Plant_MagmaCactus`, `RUT_ScorchedStars`, `AB_GiantStikehr` (and `RUT_TreeMartyr`, which is a terminator plant regardless). Ruling 4 says "adaptation to scarce water → BURST"; a succulent IS adapted to scarce water. This file keeps the 2026-09-20 roster's invented distinction — a spender (ephemeral, bloomer, annual grass) gets one chance and spends it; a hoarder stores the soak and never charges — because the ruling's own mechanism clause ("spends everything on it") describes the spender, and because no ruling touched the hoarder class. If the owner wants the deserts more violent, this is the single lever: six plants become BURST at a stroke. Not guessed toward BURST, per the brief.
2. **`RUT_RustPuff` → `RUPTURE` despite a fungal def.** The fungal carve-out's reason is that the Sheen is not water; the Contagion's water is red rain, which qualifies. The owner himself moved the puffball into the Contagion with the note "hatches occular creature when damaged" — that is the RUPTURE spawn list. Its def description ("the spores… harm nothing") is now stale against his move and should be rewritten when the def is next touched. The alternative call is NONE (fungal).
3. **`RUT_DyingCreep` → `NONE`, not `RUPTURE`.** growDays 0.1; R-G5's under-a-day clause exempts it and exempt plants never soak. It is contaminated by fiction but has no charge — it dies within hours of arriving. The alternative is a RUPTURE with no charge phase (instant rupture on soak), which would be a new mechanic and is not authored here.
4. **The twisting thorn family → `BURST`.** The only def text is "found in polluted arid environments" (thornwood) and "hardy enough to survive on heavily polluted ground" (thornweed). Arid habitat is read as the water-scarcity identity; pollution-tolerance alone would not have been enough (the wasteland's pollution plants are CHURN). Three plants ride on one adjective; if the owner wants the Cracked Lands' violence carried by the bloom crop alone, these three drop to CHURN.
5. **`RSW_Scrubgrass` and `RG_Plant_AridGrass` → `BURST`; `RSW_Dunegrass` and `AB_HardyGrass` → `CHURN`.** The descriptions decide, not the labels: the first two say "grows in arid regions", the second two say "grows anywhere". A dune-grass that churns and a scrub-grass that bursts will look arbitrary to a player reading labels; the fix, if wanted, is the def text, not this roster.
6. ✅ **CLOSED 2026-09-21 by the owner** — *"A dry plant in the greentide can burst."* The plant axis wins outright; the gourd keeps `BURST` and the Greentide roster keeps the gourd. Nothing is re-sourced. The original statement of the call follows, as the reasoning that produced it.
   **`Plant_HubbaGourd_Wild` is a BURST plant rostered in the Greentide** (`the_greentide.json`, c=0.8, "§4 fruit law — SW gourd"). Ruling 6 says nothing in the Greentide detonates; ruling 4 says a Tatooine arid staple bursts. The plant axis wins in this file (the variant is the plant's), which leaves the seam to be closed one of two ways — the Greentide roster drops or re-sources the gourd, or the design doc states that soak never forms in a ×10 biome (finding B below). Not this file's to close.
7. **`AB_BloodBouquet` → `CHURN`.** Its identity is seed-discharge ("spine-armored seed rolls to the burn line"), which under the old model argued for the Burst. Under water scarcity it is neither dry-adapted nor contaminated, so it churns; the rolling seed is its Churn's sow step. The alternative — that it is contaminated after all and should RUPTURE — is a fiction call the sheet does not make.
8. **The Forge's heat plants → `CHURN`.** `Plant_Fireweed`, `RUT_FireLavender` and the ash-skirt set live nearly without water (the Forge's rain flashes off rock), which could be read as scarce-water adaptation. Their defs name heat and magma-glow as the adaptation, not water; kept on the default.
9. **Two unbuilt commissions held at the default pending their defs:** `(new) twisted trees + shade-line grasses/mosses` (Cracked Lands) and `(new) defending shade plants` (desert). Either may earn BURST on its own text when written; a commission mixing trees with mosses should be split then.
10. **SLIME's shape.** The design doc's variant table (§3) now defines SLIME only as "a top whose ring turns the ground to slime"; the 2026-09-20 wording was "the Burst pays its harvest, but…". Slime plants are wet-living, so under ruling 4 they would churn; this file 🄸 reads SLIME as Churn-shaped with a slime ring. If the owner meant the pop to survive, that is a one-line correction in §3.

**Design-doc findings** (`explosive_plant_growth_design.md`, reported not fixed — the design doc is not this task's output):

- **A.** §9 opens "Six rulings came out of it" and then indexes seven.
- **B.** §0 says the ×10 ambient "replaces soak-bursting in those biomes entirely", but §1's `miasma_axis` row still reads "fresh side only — the surge line decides which half blooms", i.e. a soak-and-bloom in the Miasma, and player irrigation / the Greentide extract remain listed as universal soak routes. The doc does not say whether SOAKED can form at all inside a ×10 biome. That is exactly the question hard call 6 needs answered.
- **C.** Ruling 6 is phrased as a biome rule ("plants in the Greentide, the Miasma and the Fever Wood… never detonate") while §8 forbids the biome as an input. It is reconcilable only as a property of those biomes' WATER (river_steam / miasma_axis / Fever Wood water do not soak) plus the fact that their rostered plants are wet-living — and §1 has only been brought into line for `river_steam`.
- **D.** §7's 2026-09-20 entry still opens "**The Burst is the ruled default terminal moment**" and §8's "RULED as asked" table still assigns "Fruit-glut" — both statements are false under §3 as reshaped, and per the owner's deletion rule (2026-09-09) should be rewritten as history ("was the default until 2026-09-21") or removed, not left standing as present tense.
- **E.** §3's variant table describes TINDER as "a Burst whose debris is fuel", which under ruling 4 requires TINDER plants to be dry-adapted. The doc never says so; this file supplies the reading (the fire loop is a rain-flush-then-cure cycle). Worth one sentence in §3.
- **F.** The hoarder exclusion (hard call 1) is not among the carve-outs §3 lists and exists only in this roster. Either the design doc adopts it or this roster is the only place a reader will learn that cacti do not charge.

## UNMEASURED

Stated as ignorance, not as zero.

- **Which defName the game loads for the four SW port crops** — the rosters say
  `Plant_Chakroot_Wild` / `Plant_HubbaGourd_Wild` / `Plant_Nysyllin_Wild` / `Plant_Bloddle`;
  our defs say `RSW_Plant_*`. Needs the def dump (`measure`), not this file.
- **`Plant_Bubblespore_Wild`'s description** (SW donor, not in our defs) — CHURN is the
  default so the assignment is safe; the heavy-produce sizing rides on roster placement alone.
- **Where the seven `RSW_DesertPortMisc_Plants.xml` plants grow** — no roster row names them.
- **Whether donor trees (mangroves, jungle tree, slimy trees) soak and charge the same way
  understory does** — the design doc treats trees generically except for the Greentide's
  kit-owned FALL; nothing here changes that, and no engine member was checked (RimSage is
  Desktop-only per CLAUDE.md; no engine claim is made in this file).
- **Not ruled (cards owed on `EXPLOSIVE_PLANT_GROWTH_1`):**
  1. The hoarder reading (hard call 1): does a succulent charge at all, and if it does, is it
     a Burst? This file keeps the 2026-09-20 invention (NONE) because no ruling touched it.
  2. Does the Greentide extract, "which charges plants to burst", override a CHURN plant to
     BURST? (Recommended yes — the extract is the deliberate weaponised form; unruled. Under
     ruling 7 that would be the expensive, unreliable weaponize verb in its purest form.)
  3. Whether player irrigation inside a ×10 biome soaks at all (design-doc finding B below).
  4. Card #5 (do truce pools soak) is still open but is now near-zero stakes — emergent
     consequence 2.
