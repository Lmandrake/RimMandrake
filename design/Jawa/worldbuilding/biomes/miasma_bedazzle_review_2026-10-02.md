# The Miasma: bedazzle review (grandfathered sitting, turn 1 drafted)

Program: `BEDAZZLE_TOP_SHAPE_PROGRAM_1`, track (a), worst-first, sitting 12, **the last grandfathered sitting**.
Item to be filed by the parent (`MIASMA_SCORING_SITTING_1` shape).

_BENCH design pass, 2026-10-02. Twelfth and last sitting of the grandfathered track, in the order of
`grandfathered_bedazzle_scores_2026-10-01.md` (§ Miasma; sitting order row 12, "the strongest of the twelve,
sound and god only"). The sheet `the_miasma.md` is frozen (`BIOME_FREEZE_FABLE_REVIEW_1`, 2026-09-07; amended
2026-09-23 at a sitting for the warden mother). Already ruled and **not re-argued here**: the biome, the drain
and the lifeboat; the breath-tide surge and the moving salt line; the three rings of refuge; the warden mother
who lumbers in the water, cannot reach dry land and is befriended by freeing the young she cannot reach, who
dies of age and whose young inherit her (2026-09-23); the swim rule and canals; the four `karr-` scuttlers and
the composter as one clade; the stranded as a condition of the nursery's young, not a species; the carnivorous
plants that eat scuttlers, never a colonist; fever-forging; the attar (*"owner's pick"*) replacing the cut
medicine; the Wildsteam pilgrimage; and the three kit cards of 2026-09-12. The seven hard bans of sheet §6
bind every slate row; the ones that bite hardest: **no gene machine** (the Slime owns it), **the rainbow flora
never lies**, **no medicine economy**, **no clockwork tide**, **no rain**, and **no virus authorship in
player-facing text**._

Sources read, all in the BENCH clone: `src/RimMandrake/Miasma/` (BiomeDef `Defs/BiomeDefs/RM_Miasma.xml`, every
def file, `About.xml`, the six `Source/*.cs` by grep, `RM_MiasmaMod.cs` settings), the shared kit's
`GameCondition_EnvironmentalWeather.cs` and settings, the frozen twin
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Miasma.xml`, the cast patch
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_Miasma.xml` and `RUT_Miasma_PollinationGate.xml` (each op's own
xpath resolved), `RUT_FeverSwarm.xml`, `RUT_Karrobel.xml`, `RUT_DeltaLoam.xml`, every other `src/` file naming the
biome or its donor `AB_MiasmicMangrove` (`BiomeNames_Ashkarr.xml`, `BiomeDescriptions_Ashkarr.xml`,
`AncientDangerGenSteps_AmbientDoctrine.xml`, `FishTypesStrip_NoFishBiomes.xml`, `BiomeCastEvictions_WildBiomes.xml`,
`AnimalBiomeDuplicates_Generated.xml`, `JawaWorld_BiomeMix.xml`), `RSW_BiomesTeamPort_Races.xml`, the sheet, the
fauna and flora rosters of 2026-09-23, `rosters/the_miasma.json`, `kits/miasma_kit_spec.md`, the open items
(`MIASMA_FIRST_SCRIPT_1`, `MIASMA_MECHANICS_1`, `MIASMA_SHIPPING_NAMES_1`) and the closed ones
(`MIASMA_RM_MOD_BUILD_1`, `MIASMA_FAUNA_FLOOR_ROSTER_1`, `MIASMA_FLORA_ROSTER_1`, `MIASMA_KARRATHIL_POLLINATION_GATE_1`,
`MIASMA_SCUTTLER_PREDATION_1`, `WARDEN_MOTHER_BEFRIENDING_1`, `WARDEN_MOTHER_SUCCESSION_1`), the register
`design/Jawa/salvation_rites_2026-10-01.md`, the ledger's 2026-10-02 rulings, and the Slime and Weeping Stones
reviews for shape. Rosters were parsed as XML elements; the creature census reads descriptions; art was searched
with `artpipe_state.py find`; three cast names were checked against Wookieepedia's search API (probe *dewback*
returns its page).

## 0. The Miasma in plain words (for the card)

The Miasma is where the dayside's last rivers reach a dying salt sea: a forest of mangal trees standing on
stilt-roots in brackish channels, under a green-gold haze that never lifts and never rains. Everything ends up
here: the water, the war's old poisons, and the life running from a sea that grows saltier every year. Every
few days a storm shoves the sea miles up the channels and the salt line moves; what you built on fresh ground
may be standing in brine tomorrow, and the receding water leaves the sea's young stranded in pools. The ground
crawls with little armoured scuttlers that everything eats, and carnivorous plants eat them too. The air makes
you sick, and surviving the sickness here sometimes leaves you stronger. In the shallows lives the warden
mother, an enormous barnacled sea elder too old for the open sea, guarding a nursery she cannot leave the water
to protect: free a young one stranded on dry ground and she stops hunting you, and when she dies of age her
young are yours. Its plants are rainbow-coloured and honestly harmless, and its mud refines into a beauty oil
that the sheet calls the planet's loveliest luxury. The place is meant to sound like clicking shells and
swarm-hum, but today it makes no sound of its own, it does nothing to your ship, and no god is tied to it,
though one faction makes pilgrimages to it as a last hope.

## 1. What is there: ruled vs built

### The best-built mechanic kit of the twelve, with three of its own creatures in the wrong mod

`src/RimMandrake/Miasma/` (`mandrake.rm.miasma`, `MIASMA_RM_MOD_BUILD_1`, composed into the Baroque Biomes mod;
six C# files, about 900 lines, plus the shared Environmental Hazards kit) ships: its own biome worker; the
**gradient axis** (fresh to brackish to brine water bands, a salt-crust repaint of land the brine reaches, and the
ilbareen that dies in place as a **salt-line gauge**); the **breath-tide surge** (storm-weighted, never scheduled,
`gradientSurgeEnabled`); the **stranding pools** that leave the sea's juveniles behind, one in four of them carrying the
**stranded deformation**; the **permanent haze** (`RUT_MiasmaWeatherLock` forcing `RUT_MiasmaWeather`: no rain,
green-gold sky, vanilla's noxious-haze overlay, a low exposure carrier, mangals thrive while it runs);
**fever-forging** (seven diseases patched to leave a minor boon, a hardened immunity or one of five strange-tier
traits on survival); the **warden mother** whole (bs 8, water-locked, territorial anchor round her placed crèche,
befriended by freeing the young she cannot reach, **succession** to her young at death, `wardenSuccessionEnabled`
and a self-tame slider); **plant predation** (`RM_CompPlantPredator`, the five carnivorous plants eat scuttlers);
the **arthropod floor** (karravel, karrimeth, karrolun, one shared vermin pool); and **19 invented plants**
(four mangals, six rainbow blooms, five predators, four muck-and-silt) with delta salt and delta silt as harvests.
The campaign layer adds the frozen twin `RUT_Miasma` (33 rows), the 15-row cast patch onto `RM_Miasma`, the
**pollination gate** (`RUT_Miasma_PollinationGate.xml`: the thessamor and quennath can only spread where the fever
swarm is), and the two `RUT_` creatures below.

### 🔴 The systemic defects of the last sittings: checked, and the Miasma carries all three

- **(a) Ratified-but-unbuilt creatures: yes, a smaller gap than most, but real.**
  1. **Six owner-ruled imports are on neither Miasma def** (`rosters/the_miasma.json`, *"owner review 2026-09
     (round2 move mapping)"*, frozen 2026-09-10): the blarth (a Hutt pet, dual-listed as faction stock), the
     blixus, the **bogwing** (*"miasma flyer"*; only a body def exists in `src/`, no race), the marsh haunt, the
     sando aqua monster (a bottom-walking adult), and the **giant ambush frog** `JRWBeelzebufo`, which the owner
     ruled be **renamed and redefined as ours** (*"non-SW: keep the giant-ambush-frog body plan, new name +
     alienized art"*, card 2026-09-10). **No def, name or art for the frog exists anywhere** (`src/` and
     artpipe: zero hits). Under the stopped-evictions ruling these are review rows for this sitting, not sweeps:
     the frog is the one that is unambiguously ours to build; the five donor/canon rows belong on the campaign
     patch, and the sando adult conflicts with the json's own note that the wild roster *"carries only the YOUNG
     side"* (and with *"no second giant"*), so it is flagged, not slated.
  2. **The free nursery is two juveniles.** The fauna roster (§4) measured that 11 of the sea roster's 18 beasts are
     invented, so their young belong in the free tier; `SEA_BEASTS_TIER_RULING_1` moved two (rust nipper, silt
     lamprey: `RM_RustNipperJuv`, `RM_SiltLampreyJuv`, 0.25 each). The other invented sea beasts have no juvenile
     at all, so the free Miasma's *"juveniles swarm the shallows"* is two species; the warden's crèche spawns
     the same two.
  3. **Art.** 🔴 **The giant has no art**: `RM_WardenMother`'s texPath resolves to nothing (its own header; artpipe
     `warden mother`: zero hits), so the biome's centrepiece draws as nothing in both tiers, and the visible
     ageing her succession needs (*"a player surprised by her death means this was built wrong"*) cannot be shown.
     The **karrobel** has a finished render (artpipe `done/rutkarrobel_v1_south`) and **no PNG in `src/`**.
     Four plants have no texture folder in `src/` (ilbareen and its dead form, ismerrow, nemreth, braskeen); each
     has artpipe registry lines to check first. The three free scuttlers and the fever swarm have one facing each.
- **(b) Invented-name content in the campaign tier: yes, and the free mod depends on it.**
  - **The karrobel** (`RUT_Karrobel`, the composter whose castings are the delta loam, `RUT_DeltaLoam`) and **the
    fever swarm** (`RUT_FeverSwarm`, the vector and only pollinator) are invented, franchise-free creatures
    authored in `mandrake.rut.patches` and wired into the **free** def under `MayRequire="mandrake.rut.patches"`.
    A free player has no composter, no loam and no swarm. Both headers say a later pass should port them; none has.
  - 🔴 **The biome's central bargain is campaign-only.** The pollination gate (*"you cannot have the trees without
    the fever"*) is a campaign patch naming the campaign's swarm, so in the free mod the mangals spread freely and
    the bargain does not exist. (And in both tiers it is half a bargain: the swarm carries no disease; the fevers
    come from the biome's `diseaseMtbDays`, so killing the swarm costs the trees and cleans nothing.)
  - **Three campaign "Star Wars" rows are not Star Wars.** `WildAnimals_Miasma.xml` calls its 15 rows *"genuine Star
    Wars"*, but `RSW_PodWorm` 0.5, `RSW_CrestedDragon` 0.4 and `RSW_AaroxisDendoria` 0.3 are **Biomes! team ports**
    (`RSW_BiomesTeamPort_Races.xml`, `BMT_FAUNA_ABSORPTION_1`, renamed `BMT_` to `RSW_`), and Wookieepedia's search
    returns no page for any of them. The same misnomer as today's Wildpawn/Wildpod correction
    (`ALPHA_ANIMAL_PORTS_RM_TIER_1`); whether such ports go to `RM_` is that item's ruling, not this sitting's.
- **(b′) The inverse leak: campaign and franchise text inside the free mod.**
  - 🔴 **The free def's salt line names a campaign terrain.** `RM_Miasma`'s gradient axis (`landTerrain`) and its
    stranding pools (`dryTerrain`) both name `RUT_Jawa_SaltCrust`, which is defined only in
    `src/RimUtinni/UtinniPatches/Defs/TerrainDefs/JawaSaltCrust.xml`, **with no guard**. Without the campaign the
    biome's signature mechanic, the salt line moving over the land, has no terrain to paint (a cross-reference
    error at load and a dead repaint). This is the worst tier defect in the Miasma.
  - `About.xml`'s description (player-facing in the mod list) names Star Wars, the campaign, and seventeen
    canon and `RSW_` defNames; it reads as a build log. The thessamor's description names **the Grey Sea**, a
    campaign place.
  - `RUT_`-prefixed defs ship inside the free mod: both weathers, the lock, the surge condition and incident, five
    hediff files, two gensteps, the crèche marker and the keyed strings. A rename, not a move (the scores doc's
    third gap).
- **(c) Campaign patches that replace a free list or gate on a donor or frozen def: no replace; the cast patch
  adds.** `WildAnimals_Miasma.xml` is a `PatchOperationConditional` + `PatchOperationAdd` onto
  `RM_Miasma/wildAnimals` (its xpath resolved): it adds 15 rows and replaces nothing. The pollination gate adds a
  modExtension to four plant defs (two donor mangals for the twin, two of ours). But every campaign op that carries
  a Miasma **ruling** targets only the donor `AB_MiasmicMangrove`: the label and description, the ancient-shrine
  denial (`AncientDangerGenSteps_AmbientDoctrine.xml`, `preventGenSteps ScatterShrines` on the donor only, the
  Slime's and Fever Wood's family) and the world biome mix. Our def carries its own label and description; the
  shrine denial does not reach `RM_Miasma` or the twin.
- **(d) Banned weather: clean in practice.** Ban 5 (*"no rain"*): the free def still lists `Rain` 10,
  `RainyThunderstorm` 5 and `FoggyRain` 4, but the permanent lock forces the haze with no settings switch
  (`GameCondition_EnvironmentalWeather`), and both Miasma weathers carry `rainRate 0`. Inert rows, listed for
  tidiness, not a breach. Ban 6 (no virus authorship): clean, no player-facing text names an author.
- **(e) Mod Settings:** rarity, warden succession and the self-tame chance here; surge, weather pulse and hazard
  damage on the shared kit's screen. **Plant predation, the pollination gate and the stranded deformation have no
  switch.** Listed, folded into row 0.
- **(f) Heat kind: owed.** Median 42.8 °C (30 to 59), sun median +39° (sheet §0): an extreme-heat biome with no
  declared heat kind. Under a permanent haze it reads as **ambient** (shade under the canopy does little); that is
  a ruling for the heat program (`SOLAR_HEAT_EXPOSURE_1`), noted here.

### Fauna, merged (inline + patch-added), read as XML elements, census by description

**Free tier, `RM_Miasma/wildAnimals` (16 rows, `animalDensity 6.5`):** ours: karravel 3.5 (the sliding carpet),
karrolun 1.2 (the hand-sized harvest), karrimeth 0.8 (the clicking mass), rust-nipper and silt-lamprey young 0.25
each; campaign-gated: fever swarm 0.9, karrobel 0.6; donors (Alpha Animals, VFE Insectoids 2): swarmling 0.7,
black swarmling 0.5, lockjaw, mantrap, raptor shrimp 0.2 each, decay drake, helixien, slurrypede, thermadon 0.1
each. **A free install without the donors and the campaign has five rows: three scuttlers and two juveniles.** The
warden mother is not a roster row: the crèche genstep places her (0.4 to 0.6 per 10k cells, brine shallows),
with a 35% chance of stranded young beside her.

**Campaign patch-adds to `RM_Miasma` (15 rows):** runyip 0.5, shiro 0.4, anooba, grank, whisperbird 0.3 each,
vornskyr 0.15, zakkeg 0.05 (canon, ported); pod worm 0.5, crested dragon 0.4, aaroxis 0.3 (**Biomes! ports, not
canon**, above); mee young 0.4, faa, laa and yobshrimp young 0.3 each, opee sea killer young 0.05 (canon nursery).

**The frozen twin, `RUT_Miasma` (33 rows):** the same cast under donor and `RSW_` names, plus five rows the roster
evicted (kreetle, yobshrimp adult, gembug, blood shrimp, plasmorph). Deleted at the repaint.

**Flora:** 20 free rows, all ours but the Rot's nogtyl (cross-mod, gated); no donor flora. Not a roster gap; four
art gaps (above).

**Multi-homed:** the swarmlings, helixien and decay drake are donor rows shared with other wild biomes (sitting
rows, not sweeps); no owned creature of ours is cast elsewhere.

### Ruled mechanics, built and unbuilt

- **Built (free):** gradient axis and salt-line gauge; surge; stranding pools and the deformation; the haze lock;
  fever-forging; the warden mother, her crèche, befriending and succession; plant predation; the scuttler pool.
- **Built (campaign):** the pollination gate; the composter and its loam; the fever swarm; the canon cast and the
  canon nursery.
- **Ruled, unbuilt:**
  1. 🔴 **The attar** (sheet §7, *"owner's pick, replacing the cut medicine"*: *"an expensive oil that restores
     beauty… Artists use it as a glaze… the vain use it as a balm"*). Delta silt is harvested and its description
     promises the attar; **no attar def, no recipe, no still exists** (searched). The owner's own resource pick is
     the biggest unbuilt mechanic here.
  2. **The young calls** (fauna roster §6, steps 3 and 4: the stranded young cries, audible and locatable, and she
     lumbers toward the call): the befriending core is built (closed `WARDEN_MOTHER_BEFRIENDING_1`), the call is
     not. It is also the biome's one sound the sheet already promised.
  3. **Her death foreshadowed** (fauna roster §6a): visible ageing art, owed with her art.
  4. **The flotsam yard** (sheet §7: *"everything the rivers carry that doesn't rot washes into the roots"*): the
     thrannock plant names it; no flotsam table, genstep or post-surge salvage exists.
  5. **The nursery trade** (sheet §7: eggs and young of the sea's roster, *"priced in the mothers' memory"*): unbuilt.
  6. **The arthropod harvest as a food industry** (sheet §7): the karrolun is huntable meat; no trap, recipe or
     dish names it.
  7. **The Wildsteam pilgrimage and Bitterleaf's shrine-stills** (sheet §8): campaign prose only.
- **Hard bans, checked:** 1 no gene machine: clean. 2 the rainbow flora never lies: clean (the predators are a
  separate clade and eat scuttlers only). 3 no medicine economy: clean (no medicine def; the attar is the luxury).
  4 no clockwork tide: clean (storm-weighted MTB). 5 no rain: clean in practice (d). 6 no virus authorship: clean.
  7 no Earth fauna or flora: clean on our rows.
- **Unruled marks:** a ship touch (6), a sound (7), a god and a rite (9), and a learned technology (2).

### Mechanisms already in `src/` that the slate can reuse (searched before proposing)

- `RM_GradientAxisExtension` + `RM_GradientAxisRepaint`: a salinity value per cell and a repaint that kills a
  named plant and leaves a dead one; anything that should *read* or *mark* the salt line.
- `RM_GradientSurgeExtension` + `RUT_Surge` + `RUT_SurgeWeather`: a storm-weighted front with a recede; anything
  that should arrive with the surge.
- `RM_StrandingPoolsExtension`: pools found after a recede, juveniles placed, a decay clock; the place a stranded
  young (and its call) already lives.
- `RM_CompTerritorialAnchor`, `RM_CompWaterLocked`, `RM_JobGiver_AnchorDefense`, `RM_CompCrecheYoungLedger`,
  `RM_HediffComp_SelfTameOnRecord`, the succession code: a water-bound giant with a ledger of the young it is owed.
- `RM_HediffComp_ForgeOnSurvival`: anything that should leave a permanent mark on a survivor.
- `RM_PollinationGateExtension` (Harmony on `WildPlantSpawner.CalculatePlantsWhichCanGrowAt`): spread gated on a
  nearby animal.
- `RM_CompVerminBreeder` + `RM_MapComponent_VerminPopulation`: one population, many draws.
- `RM_MapComponent_ProximitySoundscape` (the Greentide's): a per-object sound.
- The Rites tab in `mandrake.rut.rites` (`src/RimUtinni/Rites/`); the found-rites row is register §d's spec.

## 2. Scorecard

Ruled counts as HIT; built is reported beside it. Marks come from the scores doc, re-read against the sheet, the
two rosters and the source. **No mark moves**; three HITs are qualified (marks 3, 4, 5).

| # | Mark | Free (ruled) | Campaign (ruled) | Built today | Note |
|---|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | gradient axis and salt-line gauge, surge, stranding pools, haze lock, fever-forging, plant predation | the salt line paints a **campaign terrain**; without the campaign it has nothing to paint |
| 2 | Discoverable technology | PARTIAL | PARTIAL | fever-forged boons (your body keeps it); no research project | not a technology; bans 1 and 3 close the obvious routes (genes, medicine) |
| 3 | Unique resources | **HIT** (thin) | **HIT** | delta salt and delta silt, harvested, **with no recipe or use**; delta loam (campaign only) | the owner's own pick, **the attar, is unbuilt**; the flotsam yard, the nursery trade and the arthropod industry are unbuilt |
| 4 | Surprising creatures | **HIT** (qualified) | **HIT** | free: three scuttlers of ours, two juveniles, the warden, nine donor rows; campaign: the swarm, the composter, 15 patch-adds | the free mod's most surprising creature (the swarm) and its composter are campaign-gated; the six round-2 imports are on neither def, and the ruled remade frog is not built |
| 5 | GIANT beast | **HIT** (no art) | **HIT** (no art) | the warden mother, bs 8, water-locked, befriended, succession | the best-storied giant of the twelve; **she renders as nothing**, and the young's call and her ageing are unbuilt |
| 6 | Gravship touch | MISS | MISS | 0 | |
| 7 | Soundscape | MISS | MISS | no ambient sound on the biome or either weather | the sheet names its sounds (§9); the young's call is ruled and unbuilt |
| 8 | Interesting weather | **HIT** | **HIT** | permanent green-gold haze, the surge weather | ban 5 holds in practice; the inert `Rain` rows are tidiness |
| 9 | Relationship to the gods | MISS | MISS | 0 | the Wildsteam worship it (another faith, prose only); no Salvation god, precept, shrine or rite |

**Free 6 HIT / 1 PARTIAL / 2 MISS. Campaign 6 HIT / 1 PARTIAL / 2 MISS** (as the scores doc read). Still the
strongest of the twelve on marks, but the last sitting finds the same shape as the eleven before it underneath:
the free mod **leans on the campaign** (its salt-line terrain, its swarm, its composter and its central bargain
all live in `mandrake.rut.patches`), the giant is **built and invisible**, and the owner's own resource pick (the
attar) **was never made**. Then the usual blanks: ship, sound, god, and a tech that is only half one.

**Rite: none today.** The scores doc's seed: *"a rite that takes in a warden's young, or one held at the crèche at
surge-tide (Oomo, the nursed stranger)"*. Oomo may be full by the end of today (§6); §6 answers the seed with a
god that has room.

## 3. Roster fill

### The gaps, read from the sheet's rings (§4), the rosters and Q11a only

The sheet's rings are all staffed in design; the gaps are tier, the free nursery, the ruled imports and art. No
new species is needed except the one the owner already ruled (the frog). Every fill is free tier unless canon.

| ring (sheet §4) | free tier today | campaign today | fill |
|---|---|---|---|
| The nursery | two juveniles (rust nipper, silt lamprey) | + mee, faa, laa, yobshrimp, opee young (canon) | **young for four more of our invented sea beasts**, all of whose adults are already `RM_` in `mandrake.rm.terminalbiomes` (`RM_SeaBeasts_Invented.xml`): crimson opee, thornback colo, shale gorger and reefback young, juvenile-locked by the `MIASMA_NURSERY_KINDS_1` pattern; add them to the stranding list and the crèche's young. No new species: the young of adults that exist |
| The warden mothers | built, no art | same | **her art** (water-bound, barnacled, visibly old, with an aged variant for the foreshadowing), and **the young's call** (§4 row 0) |
| The stranded | the condition, built | same | none owed |
| The crusty arthropods | karravel, karrimeth, karrolun | + karrobel | **port the karrobel to `RM_`** (with `RUT_DeltaLoam`, and wire its finished render) |
| The composters | (campaign-gated) | karrobel | same row as above |
| The fever-swarms | (campaign-gated) | fever swarm | **port the swarm to `RM_`**, and move the pollination gate into the free mod for its own mangals, so the bargain exists without the campaign |
| Round-2 imports (owner, 2026-09-10) | none | none | **the giant ambush frog, remade as ours** (ruled: *"keep the giant-ambush-frog body plan, new name + alienized art"*): free tier, one home, a root-maze ambusher of the fresh end that eats scuttlers and stranded young; name drafted at build under the noncanon naming process (not invented here). The **bogwing** (the *"miasma flyer"*, real flight by the standing rule), **blarth**, **blixus** and **marsh haunt**: canon or donor, campaign patch rows, each needs a race def first (the bogwing has only a body). The **sando aqua monster** adult: flagged, not slated (the roster's own *"only the young side"*, and *"no second giant"*) |
| ⚠ Tier hygiene | — | pod worm, crested dragon, aaroxis are Biomes! ports labelled Star Wars | for `ALPHA_ANIMAL_PORTS_RM_TIER_1`'s family; listed, not slated |

**The art debt:** the warden mother (none at all), the karrobel (render finished, unwired), four plants (ilbareen
and its dead form, ismerrow, nemreth, braskeen: artpipe registry lines exist, check before queueing), and the four
nursery young. The scuttlers and swarm have south facings only.

**The giant needs no new story; she needs a body and a voice, and one more decision.** The warden mother already
has the best story of the twelve (rescue the young she cannot reach; she dies of age; her young inherit her).
What she lacks is to be **seen** (art), **heard** (the call that brings her and that a colony learns to listen
for), and the one decision the sheet already ruled into the economy and nobody built: **the nursery trade**. Three
options for the card, none rewriting her:

- **The Mother's Price** (BENCH; recommended). Sheet §7's *"eggs and young of the sea's roster, priced in the
  mothers' memory"*, made a decision. A stranded young is worth a fortune to buyers (the Deepwater vigil wants
  them for the sea; margin traders want them for the pens). When the colony finds one, it can carry it home to
  her (befriending, built) **or sell it**: a trader caravan arrives for any stranded young the colony holds. Sell
  one and **her crèche remembers** (the built `RM_CompCrecheYoungLedger` already counts the young she is owed):
  she never tolerates the colony again, and the succession never comes. Readable: the call keeps going while the
  young sits in your pen; the buyer's letter; her ledger in the inspect pane. **Reuses:** the crèche ledger, the
  stranding pools, the tolerance state, trader arrivals. New: the call, the buyer, a price. Size M.
- **The Grounded Mother** (BENCH). When she dies of age, her body does not sink: it **grounds** in the shallows
  as a barnacled reef that the scuttlers swarm and the surge cannot move. Her shell plates are the only
  brine-proof plating on the planet: **a ship-grade hull plate** for the gravship. But her young (yours, by
  succession) **guard the carcass**: strip it and the young you inherited turn from you. Scavenger against
  loyalty, on the biome's own giant. Ties the giant to the ship. Size M to L.
- GPT's giant idea, if it offers one (§5).

## 4. The slate

Proposed for owner turn 1. Row 0 executes existing rulings (the sheet's §7 attar, the fauna roster's rulings of
2026-09-23, the round-2 frog ruling, Q11a, the Mod Settings law); rows 1 onward need his word. Nothing here
directs the Working, makes a flower lie, sells a cure, schedules the tide, rains, or names a plague's author.

**0. Land what was already ruled.** Three parts, all named and ruled.
- **0a. The free mod stands alone (tier, `mandrake.rm.miasma`):**
  - **the salt crust:** give the free mod its own salt-crust terrain (or guard the reference), so the gradient
    axis and the stranding pools paint without the campaign; the campaign keeps `RUT_Jawa_SaltCrust` on the twin;
  - **port the karrobel and the fever swarm to `RM_`** (with the delta loam), drop their `MayRequire` gates, and
    **move the pollination gate into the free mod** for its own mangals (the campaign patch keeps only the donor
    pair for the twin);
  - **the free nursery:** young for four invented sea beasts whose adults are already `RM_` (crimson opee,
    thornback colo, shale gorger, reefback), on the roster, the stranding list and the crèche;
  - **the remade frog** (ruled 2026-09-10): a free-tier root-maze ambusher, named under the noncanon process;
    and the four round-2 canon/donor imports onto the campaign patch where a race def exists (the bogwing needs
    one, and flies);
  - **text:** rewrite `About.xml`'s description as a player-facing description (no Star Wars, no campaign, no
    defNames); take *"the Grey Sea"* out of the thessamor; rename the `RUT_` defs that ship in the free mod to
    `RM_` (the scores doc's third gap); drop the inert `Rain`, `RainyThunderstorm` and `FoggyRain` rows;
  - **Mod Settings:** switches for plant predation, the pollination gate and the stranded deformation.
- **0b. The giant, seen and heard:**
  - **the warden mother's art**, with a visibly aged variant for her last season (the foreshadowing the roster
    requires); check the artpipe first (searched today: zero hits);
  - **the young's call** (fauna roster §6 steps 3 and 4: a stranded young cries, audible and locatable, and she
    lumbers toward it as far as water goes). This is also the biome's first sound.
- **0c. The ruled economy:**
  - 🔴 **the attar** (sheet §7, the owner's pick): a still that refines delta silt into the attar, with its two
    uses: a **glaze** that raises a finished artwork's beauty and a **balm** that fades scars (a cosmetic,
    never a medicine: it heals nothing, ban 3), and a luxury price;
  - **delta salt** a use (the sheet: *"the one the stills need most"*): an input to the attar still;
  - **the flotsam yard:** a post-surge salvage drift along the root-lines (a table of river-borne goods washed
    into the roots, restocked by each surge);
  - **the arthropod harvest:** a scuttler trap and one dish.
- **0d. Wire the finished art:** the karrobel's render; the four plants' renders if finished (check first).
Size L (mostly defs and art; the real C# is the attar's glaze and balm, the flotsam drift, the call, and the
settings wiring).

| order | package | marks | reuses | size |
|---:|---|---|---|---|
| 1 | **The giant's decision** (§3): the Mother's Price (sell a stranded young and her crèche never forgives) or the Grounded Mother (her dead body a reef of brine-proof hull plate her inheriting young guard). | 5 (and 6 for the Grounded Mother) | `RM_CompCrecheYoungLedger`, the tolerance state, the stranding pools, the succession, trader arrivals | M (M to L) |
| 2 | **Decay cells** (tech; §5 idea 3, GPT): a learned generator that makes power from rotting goods in beds of delta loam, silt ceramic and delta salt, usable anywhere. | 2, 3 | delta salt and silt (a use at last), delta loam, `CompPowerPlant`, `CompRottable` | M |
| 3 | **The Last Dry Deck** (ship; §5 idea 1, GPT): a surge strands a combing crew and their workshop; carry them and their gear to Bitterleaf, or leave them. | 6, 8 | the surge state, Odyssey's carried occupants, a quest | M |
| 4 | **What the Scuttlers Say It Is Worth** (sound; §5 idea 2, GPT): appraise unopened flotsam lots by the sound the scuttlers make in them before you bid. | 7, 3 | the flotsam yard (row 0), the scuttler population, a lot container | S (after row 0) |
| 5 | **A Salvation rite** (§6 R1 or R2, or GPT's Recall). | 9 | the stranding pools and deformation (R1), the anchor radius (R2) | M (L for the Recall) |
| 6 | **Art commission:** the warden mother and her aged variant, the four nursery young, the remade frog, the karrobel wiring, four plants, the attar still and its goods. Check the artpipe first. | all | artpipe | — |

Held in the doc: **the First Egg Above Water** (§5 idea 5) is offered on the card as a pick-any option, not slated
(it adds a species that crosses from sea to land, close to the ruled *"the stranded are not their own species"*).

🔴 **Sequencing:** row 0 first. The giant's decision needs her art and the young's call; the appraisal needs the
flotsam yard; decay cells need delta salt and loam in the free mod; R1 needs the call. `MIASMA_FIRST_SCRIPT_1`
should be run against row 0's state (and its bars should include the salt crust painting with the campaign absent).

## 5. GPT consult: five ideas

Consult: `Transient/bedazzle_gpt_enrich_2026-10-02/miasma_gpt.md` (prompt beside it, `miasma_gpt.prompt.md`), run
2026-10-02 under the standing rule (`BEDAZZLE_TOP_SHAPE_PROGRAM_1`, ruling 2026-10-01): exactly five ideas,
different from each other (GPT's own check: verbs embark / appraise / wire / revoke / protect; systems gravship
manifests / salvage valuation / electrical generation / ritual incidents / wild reproduction) and from every other
biome's signature, which the prompt listed in full, **including today's rulings** (Webwork, Greentide, Rust
Cathedral, the Rot, the Fever Wood, the Weeping Stones' Refused Toll) **and every Slime pitch still on its unruled
card**. Gods offered: Ishko, Sh'kaar, Rekko, Ta'Baa, and Oomo as possibly full. Model `gpt-6.1-sol`, high effort,
via `gpt_consult.py`, answered first try (started 14:45, written 15:00 PDT; the harness moved the long call to the
background at 600 s and it finished there). GPT cites Odyssey's carried occupants and RimWorld's refugee quests,
Outer Wilds' signalscope, Dredge, Raft's biorefiner, Fertile Fields, Anomaly's void provocation, VFE Ancients'
burst signals, Terra Nil and Biotech reproduction; its links are not verified here. **GPT offered one rite** (idea
4, Rekko) and **one new creature** (idea 5). It offered no weather, and it declared the heat kind **ambient**,
matching §1 (f).

**Names checked:** ⚠ **vorrsalt** passes `check_pseudo_sw_name.py` and Wookieepedia's search, but fails the stem
rule (*vorr-* is taken by *vorrel*, 40 uses, and *vorrugath*); the card calls them "decay cells". ⚠ **evrith** is an
Echani surname in `src/RimStarWars/StarWarsRaces/.../Echani/Last.txt`; not used on the card. *Last Dry Deck*
returns zero files.

| # | GPT's idea | mark | tier | size | BENCH read |
|---|---|---|---|---|---|
| 1 | **The Last Dry Deck:** during a surge a flotsam crew retreats along the last roots to your landed ship, dragging two workshop frames, and asks for passage to Bitterleaf with its livelihood; taking them costs deck space or freight as the approach floods; refusing leaves them visibly trying worse. | 6 | free | M | **The ship mark in the biome's own voice**: the surge is what makes the ask, and the cost is real deck. A one-off rescue rather than a standing rule. Nearest neighbour is the Weeping Stones' Pilgrim Passage (a permanent corridor); this is finite. ⚠ He has rejected *"ship-centric gimmicks with no biome voice"*; this one has it. **On the card**. |
| 2 | **What the Scuttlers Say It Is Worth:** combing crews auction unopened flotsam lots; your appraiser listens as the scuttlers feed in them (chatter: rotting goods; taps on broad surfaces: metal) and you bid on an estimate, then open it. | 7 | free | S | **The only sound idea any sitting has offered that changes a purchase**, and it lives on the biome's starred creature. Depends on the ruled, unbuilt flotsam yard. Narrow, but honest. **On the card**. |
| 3 | **Vorrsalt cells (decay cells):** learned from a dead meter still reading current in a Bitterleaf compost bed; beds of delta loam, silt ceramic and delta salt make electricity from ordinary rot; usable anywhere; spoiled freight becomes power. | 2 | free | M | **GPT's first pick and the best tech fit of the twelve sittings' pattern** (learned here from local materials, usable everywhere, powerful and paid for in feedstock and electrodes). Gives delta salt its use. Clear of ban 1 (it collects rot, it directs nothing) and ban 3 (not medicine). **On the card**, recommended in its question. |
| 4 | **Rekko's Recall of the Written-Off:** at a river-mouth disposal depot, an inscription under condemnation stamps; performing it strikes out a disposal verdict and calls an old reclamation operation that collects loose metal and then dismantles powered structures, the ship included, until it is driven off. | 9 | campaign | L | **Dramatic and risky, which he likes, and Rekko's.** But it is not about the Miasma (the depot is a backdrop), it needs reclaimer machines and a force budget, and it spends the same last Rekko slot as BENCH's Second-Hand Young (§6 R1). **On the card** as the third rite. |
| 5 | **The First Egg Above Water:** one stranded species survives onto land; a pair nests in delta loam under the rainbow flowers; a collector bids for the founders while a Wildsteam pilgrim begs you to protect the nest through the next surge, until the first land-born young lays its own egg. | 4 | free | M | **The sheet's own soul made playable** (*"on the verge of something… it's being worked out"*): the breakthrough happening once, in your care. But it adds a species, and the owner ruled *"the stranded are the sea nursery's failures, not their own species"*; GPT's name collides. **On the card** as a pick-any option, not recommended. |

GPT's ranking: decay cells first, the scuttler appraisal second.

## 6. Discoverable rites

Per `design/Jawa/salvation_rites_2026-10-01.md` (e): found at a site with a reason to be there, learned through
the Rites tab's found-rites row (`mandrake.rut.rites`), performable anywhere after. Campaign tier. The binding
rulings: **no god is evil**; **a rite gives cohesion, never a power**; **favour shows only through events, world
state and subtle odds**, voiced by the Narrator; a rite's effect may be a dramatic, risky world event. **Per-god
cap: five** (by card 2026-10-02 09:23 PDT).

**Cap count, by hand from the register's tables B2, B4, B7 to B15** (found rites only; B4's controlled waking
counted for Zizzik as the register does; read from origin/main at the time of writing, 2026-10-02 ~14:45 PDT):

| God | Found rites | Count |
|---|---|---|
| Ishko | Dark Vigil (B2), Charged Reed, Stall-Hold (B7), the Sinking (B14) | 4, one slot |
| Ohm | Engine Hour, Last Track, Deserter's Welcome (B7), the Answering (B8), the Stranger's Overhaul (B12) | **5, at cap** |
| Oomo | Sunning, Chime Vigil, Filtered Cup, Unspilled March (B7) (the Unlit Wedding is a variant) | 4, one slot ⚠ **treated as full**: a Slime rite for Oomo is being added to the register right now |
| Mob'Unloo | Blind Offering (B2), Storm's Receipt, Cold Ledger (B7), Mob'Unloo's Price (B14), the Refused Toll (B15) | **5, at cap** |
| Sh'kaar | Snuffing (B2), Anvil Gift, Shade Tithe (B7), Felled Noon (B10) | 4, one slot |
| Ozzik | Lightless Burial (B2), Salted Keeping, Flawed Masterwork (B7), Ceded Room, Open Boast (B11) | **5, at cap** |
| Zizzik | controlled waking (B4), Kept Mistake, Capping (B7), Nine Faults (B8), Struck Glass (B9) | **5, at cap** |
| Rekko | Unfinished Laid Down, Inherited Wreck, Mud Claim (B7), Mending Weld (B12) | 4, one slot |
| Ta'Baa | the Returned, Shadow Walk, Vindication Walk (B7), the Unjoining (B13) | 4, one slot ⚠ the Slime card pitched its last slot (the Walked-Off Reading); not offered here |

**The scores doc's seed (Oomo, the nursed stranger at the crèche) is closed** if the Slime takes Oomo's last
slot; nothing here depends on him. No god is the Miasma's by the sheet; the Wildsteam's worship is another faith.
⚠ He has answered "none" at three of the last five sittings, so two are offered, each built on a mechanic the
Miasma already ships, and the card says "none" is a fine answer (by write-in).

**Not taken, and why:** carrying a stranded young back to its mother (that is the built befriending; a rite that
repeats a mechanic adds nothing); flotsam salvage after a surge (the Mud Claim owns post-recede salvage for
Rekko); a vigil for the surge's exhale (stillness vigils are taken); drinking or offering brine (offering water,
and Oomo); a funeral for the dead warden (her death is already the succession's content, and grief rites are
taken); exposing yourself to the fever to be forged (sickness-as-gift is the biome's built mechanic, and a rite
that grants a boon is a power); anything with the rainbow flora (ban 2: it never lies, so a rite cannot make it
a test).

### R1. The Second-Hand Young, for Rekko: the discarded rewoken (PITCHED)

- **Grounding:** Rekko of the Second Hand is salvage, repair and the discarded rewoken. The Miasma's stranded are
  the sea's discards: young the surge left in a drying pool, some deformed (gills leathered, fins splaying into
  feet that do not quite work: *"the almost-breakthrough given a face"*, sheet §4). A deformed young cannot go
  back to the sea; its mother will not have it. It is the most Rekko thing on the planet: a life the world threw
  away, half-made into something new.
- **Found:** on the salt crust behind a drained pool, a ring of hand-dug wet hollows, each lined with mangal
  leaves, and in the last one the dried, carefully wrapped body of a deformed young that did not make it; on a
  thrannock stake beside it, scratched: *it walked a little*.
- **Asks:** a deformed stranded young (the built deformation hediff) is carried **away from the water**, kept
  alive by hand in a dug wet hollow, and walked by the participants every day **until it walks on its own**:
  through one full surge-and-recede, while the haze sickens the keepers. The rite completes when it stands on
  dry ground unaided and is adopted by the colony.
- **Risk (the point):** the young calls the whole time, so a warden mother whose crèche is on the map **hears it
  and comes as far as the water lets her**: any keeper within her reach is in her target set, and if the colony
  had befriended her, keeping a young from the water costs that tolerance; a surge may flood the hollow; the
  young may simply die (a readable letter, the wrapped body).
- **Outcomes (cohesion only):** shared memories by quality; the adopted young is an ordinary colony animal with
  its deformation for life (no power, no boon); Rekko's favour told by the Narrator (*what the sea threw out, the
  clan has rewoken*), shown only in his odds.
- **Readable signs:** the deformation on the young, the call (owed with the giant's row 0), the hollow, the
  warden's approach in the water, the Narrator's line.
- **Collision check:** the Unfinished Laid Down (Rekko, B7) **lays down** a half-transformed thing at the burn
  line; the Second-Hand Young **raises** one. The built befriending **returns** a whole young to its mother; this
  keeps a broken one she will not take. It spends Rekko's last slot and depends on the young's call being built.

### R2. The Mother's Blind Side, for Ishko: the prepared approach (PITCHED)

- **Grounding:** Ishko is hiding, ambush and the prepared dark. The Miasma's haze mutes sound and softens light
  (*"sound is muted, light is soft"*, its own weather text): the one place on the dayside where the bright hours
  hide you. The most dangerous thing in the biome is a giant who cannot leave the water and kills anything in
  reach.
- **Found:** in the brine shallows at a crèche's edge, a single mangal stake driven into the crèche ground, wrapped
  in a Jawa clan's cloth, the cloth bleached by years; on the bank behind it, a line of shallow body-shaped hollows
  pressed into the root-mud, where a party lay waiting for the tide.
- **Asks:** the participants wait hidden in the root-maze for the surge's recede, then **cross into the warden
  mother's reach while she is on the far side of her crèche**, drive a marked stake into the crèche ground, and
  get out **without her seeing them**. Every participant must be inside her anchor radius at the moment the stake
  goes in.
- **Risk (the point):** she is bs 8 and lethal within reach; a participant she sees is in her target set until he
  leaves the water; the root-maze slows everyone (`movementDifficulty 4`); a surge mid-rite drowns the way out. If
  the colony has befriended her, the rite is pointless (she ignores you), so it is a rite for a colony that has
  not, or for her successor's crèche before the young have consented.
- **Outcomes (cohesion only):** shared memories by quality; the stake stays in the crèche ground as a readable
  mark; Ishko's favour told by the Narrator, shown only in his odds. Nothing taken from the crèche (harming a
  crèche is not sacrilege, but everything living remembers it: the rite touches nothing).
- **Readable signs:** her facing and reach drawn in the water, the hidden state on each participant, the stake.
- **Collision check:** the Dark Vigil and the Stall-Hold (Ishko) are **stillness**; this is **an approach**: a
  counted-coup on the biome's giant, hidden by daylight haze rather than the dark. ⚠ It plays only where a warden
  crèche is on the map (it is learned here and performable anywhere a dangerous anchor guards ground; elsewhere it
  is weaker). It spends Ishko's last slot.

GPT offered one rite, **Rekko's Recall of the Written-Off** (§5 idea 4): on the card as the third rite option; it
competes with R1 for Rekko's one slot.

## 7. Draft turn-1 card

Plain language, no def names in option labels, headers 12 characters or fewer, every question ends in "?", no
option is a "none" (the write-in line covers that; above question 4 say "none" is a fine answer there), option
descriptions short. Above the card, read him §0's description of the Miasma, per the standing rule that he is
never assumed to remember. Say in one line above it that **the Miasma is still the strongest of the twelve, but
the free mod cannot stand on its own: its moving salt line paints a ground that only exists in the campaign, and
its fever swarm, its loam-making burrower and the "no trees without the fever" rule all live in the campaign too;
the warden mother is fully built and has no art at all, so she is invisible; and the beauty oil you picked as the
Miasma's luxury was never made.**

**1. Build first** (header `Build first`) — *What should be built first for the Miasma?*
- **Land what was already decided (recommended):** make the free mod stand alone (its own salt ground, the
  swarm and burrower moved in, more sea young, the frog remade as ours), give the warden mother art and her
  young's cry, and build the beauty oil and the flotsam beach. *Why: every idea below stands on these.*
- **Land it and add the giant's choice together:** Buys: the warden mother gets her trade decision in the same
  batch. Costs: a bigger first batch.
- **New ideas first, landing later:** Buys: new marks sooner. Costs: the free Miasma keeps depending on the
  campaign, and the giant stays invisible.

**2. The giant** (header `The giant`) — *What choice should the warden mother put in front of the clan?*
- **The mother's price (recommended):** a stranded young is worth a fortune to buyers. Carry it home to her, or
  sell it. Sell one and her nursery remembers: she never tolerates you again and her young never become yours.
  *Why: it is your sheet's "nursery trade, priced in the mothers' memory", made a trader's choice.*
- **The grounded mother:** when she dies of age her body grounds in the shallows as a reef, and its shell is the
  only brine-proof hull plate on the planet. Her young, now yours, guard it: strip it for the ship and they turn
  from you. Buys: a ship tie. Costs: a larger build; the choice comes once, late.

**3. New marks** (header `New marks`) — *Which new ideas should be built (pick any)?*
- **Decay cells (recommended):** learned here from an old meter still reading current in a compost bed: beds of
  the delta's loam, salt and silt that turn rotting goods into electricity, buildable anywhere. Spoiled freight
  becomes power. *Why: a learned tech made of local stuff that travels, and it finally gives the delta's salt a
  use.*
- **The last dry deck:** a surge strands a salvage crew and their workshop; they reach your landed ship as the way
  floods and ask passage to the delta town with their gear. Make deck room, dump freight, or leave them to try
  worse. Buys: the ship mark in the delta's own voice. Costs: a medium build.
- **What the scuttlers say it's worth:** crews auction unopened flotsam lots; your appraiser listens to the little
  scuttlers feeding inside (chatter means rotting goods, tapping means metal) before you bid. Buys: a sound that
  changes what you pay. Costs: needs the flotsam beach first.
- **The first egg above water:** one stranded sea species survives onto land and nests under the rainbow flowers;
  a collector bids for the pair while a pilgrim begs you to guard the nest through the next surge. Buys: the
  breakthrough the place is waiting for. Costs: adds a species, close to your ruling that the stranded are not one.

**4. Rite** (header `Rite`) — *Which rite should the Salvation find at the Miasma?*
- **The second-hand young, for the god of salvage (recommended):** keep a deformed stranded young, one its
  mother won't take back, alive by hand away from the water until it walks, while it cries and she comes as far
  as the water lets her. Costs: needs the young's cry; that god's last free rite. *Why: built from the
  biome's own stranding.*
- **The mother's blind side, for the god of ambush:** in the haze, the party slips into the warden mother's reach
  while she is turned away, drives a marked stake into her nursery ground and gets out unseen. Anyone she sees is
  hunted. Buys: a counted-coup on the giant. Costs: pointless once you have befriended her; that god's last slot.
- **The recall of the written-off, for the god of salvage:** a found disposal order, struck out in the rite, calls
  an old salvage operation that strips loose metal and then your powered buildings, the ship included, until
  driven off. Buys: a dramatic, risky day. Costs: a large build, not tied to the Miasma; the same last slot.

Held off the card (in the doc only): nothing beyond the slate.
