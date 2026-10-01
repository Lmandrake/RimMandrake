# Grandfathered biomes scored against the Baroque bar (2026-10-01)

Scoring pass only (track a of the "top top shape" push). **Nothing is filed.** The bar is the nine
marks in `infrastructure/state/items/BAROQUE_BEDAZZLE_PROGRAM_1.md`, plus the 2026-10-01 rites question.
The method is the scorecard in `blackcrags_bedazzle_review_2026-09-30.md` §3/§11.

**Tiers.**
- **Free** is the `RM_` BiomeDef as its own mod ships it.
- **Campaign** is that def plus everything the Utinni layer adds: patches into the `RM_` def, campaign-only mods, and content wired only to the frozen `RUT_` twin. The twin carries today's world until the one terminal repaint, so content wired *only* to the twin is flagged: it must move onto the `RM_` def at the repaint or it is lost.

Read from `origin/main` at 2642b45e7. Rosters were parsed as XML elements, and the cast was judged from descriptions. Tile counts were not consulted. "Ruled, unbuilt" counts toward a mark and is labelled. Everything else cited is built in source.


## The Rot

Sources: `src/RimMandrake/TheRot/` (BiomeDef `Defs/BiomeDefs/RM_TheRot_Biome.xml`), twin
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheRot.xml`, cast patch
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_TheRot.xml` (targets `RM_TheRot`), sheet
`design/Jawa/worldbuilding/biomes/the_rot.md`, `rot_rm_cast_proposal_2026-09-24.md`.

| # | Mark | Free | Campaign | Why (source) |
|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | The Sheen (exposure lock, `RM_SheenCoating`, `RM_SheenProtection` stat), warm ground, accelerated rot, and the treasure conscience (`RM_RotTreasureConscience`, a thought for selling Rot treasure). `TheRot/Defs`, `EnvironmentalHazards` extensions on the BiomeDef. |
| 2 | Discoverable technology | PARTIAL | PARTIAL | `RM_AdvancedFungi` is one generic research project (*"cooling to exploding"*). The brews and symbionts are recipes, not something the biome teaches. Built. |
| 3 | Unique resources | **HIT** | **HIT** | The teas (`RM_AgelessCap`, `RM_RegenerantVeil`, `RM_EuphoricCrown`), four symbiont brews (`RM_Sym_*`), the toxic injection, blast-spore chemfuel, mushroom leather. All built. |
| 4 | Surprising creatures | PARTIAL | PARTIAL | Free inline cast is 8 `AA_` Alpha Animals donor rows (`MayRequire="sarg.alphaanimals"`), none ours. Campaign adds the skerrith (a mantis that passes as a cap) and the grellik (a weevil in partnership with its fungus), but these are ported Biomes! Team inventions still on `RSW_`, not owned inventions. |
| 5 | GIANT beast | PARTIAL | PARTIAL | `AA_MycoidColossus` and `AA_AnimaColossus` are wired in the free def, but they are donor. The campaign adds `RSW_Thrumbungus` (bs 4). No colossus of our own. |
| 6 | Gravship touch | MISS | MISS | Nothing in `TheRot/` or the twin mentions the ship. |
| 7 | Soundscape | MISS | MISS | No SoundDef in `TheRot/`. The pale tree's sound-on-destroy is the only sound hook. |
| 8 | Interesting weather | **HIT** | **HIT** | `RM_SheenFall`, `RM_SheenStorm` and `RM_SheenMist` together carry 30 of 39 weather weight, plus `RM_SporeCloud` (condition and incident). Built. |
| 9 | Relationship to the gods | PARTIAL | PARTIAL | `RM_PaleTree` is built: a psylinkable meditation focus that is *"sacred to a wandering creed of the wild"*. The campaign's Wildsteam wiring (sheet §Owed) is unbuilt. ⚠ The free-tier description says *"a faint, tugging sense of the Force"*, which is Star Wars IP inside an `RM_` def. |

**Free: 3 HIT / 4 PARTIAL / 2 MISS. Campaign: 3 HIT / 4 PARTIAL / 2 MISS.**

**Rites:** none. The pale tree is the obvious host (a meditation/communion rite before it,
appeasing whichever god sits closest to the Wildsteam's grove), but nothing is pitched.

**Biggest gaps.**
1. **Sound and ship are blank.** A warm, exhaling jungle has no voice, and nothing touches the hull. Sheen settling on the ship is the natural pitch.
2. **The free cast is all donor.** The 2026-09-24 proposal (move 10 `RSW_` rows to `RM_`) is not applied in source. Until it is, the free tier has no owned creature and no owned giant.
3. **Tech is generic.** One research project for the whole biome. The symbionts (*"how you join the biome"*) are the natural thing it could teach.

## Fever Wood

Sources: `src/RimMandrake/FeverWood/` (BiomeDef `Defs/BiomeDefs/RM_FeverWood.xml`, 31 C# files), twin
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_FeverWood.xml`, cast patch
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_FeverWood.xml` (targets `RM_FeverWood`; 10 canon
`RSW_` animals plus chak-root, hydenock and jogan), sheet `the_fever_wood.md` and the 2026-09-23/24 roster docs.

| # | Mark | Free | Campaign | Why (source) |
|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | Mirror pools that swallow drinkers (`RUT_FeverWoodMirrorPool`, `RUT_FeverWood_MirrorBreak`), ground refusal, the two-front lure stakes (`RM_MapComponent_TwoFrontLure`, stake/haul/foul-pool jobs), the kurreth ant-hive dungeon. All built. |
| 2 | Discoverable technology | PARTIAL | PARTIAL | Holding a sekkulaath in a tank (`RM_SekkulaathTank`) is husbandry, and `RM_MakeRadioactiveSuppressant` is a recipe. There is no research project, so nothing is learned here and kept. |
| 3 | Unique resources | **HIT** | **HIT** | Thornbug nectar, vaulm lacquer, drommath sap, murrelith plumage, sekkulaath cream and spleen chemicals, ossagrel sap, seep oil, potter's clay. Built. |
| 4 | Surprising creatures | **HIT** | **HIT** | Owned and inline: the thornbug that yields only while it is safe, the vaulm that sets into armour, the ollareth whose scream rouses the crown, the drommath that inflates when handled. Built. |
| 5 | GIANT beast | **HIT** | **HIT** | The sekkulaath, the elder under the pools. It is met as six tentacle limbs (`RM_Sekkulaath_Feeler/Snare/Lash/Porter/Sentinel/Bloom`, `RM_CompTentacleLimb`/`Eye`), and the Bloom shows the eye. Built. |
| 6 | Gravship touch | MISS | MISS | Nothing in `FeverWood/` or the twin. |
| 7 | Soundscape | **HIT** | **HIT** | The crown's bird calls are sustainers (`RM_FeverWoodBirds.xml`), and the Sentinel limb cuts them dead: *"That silence is the loudest warning"* (`RM_MapComponent_TentacleWatch.cs`). Built. |
| 8 | Interesting weather | MISS | MISS | `Clear` 30, `Fog` 10, `Overcast` 2, `DryThunderstorm` 1. All vanilla. |
| 9 | Relationship to the gods | MISS | MISS | Neither the sheet nor the source mentions a god, a precept or a shrine. |

**Free: 5 HIT / 1 PARTIAL / 3 MISS. Campaign: 5 HIT / 1 PARTIAL / 3 MISS.**

**Rites:** none. The pools are the natural altar: something enormous is listening, and the
Porter limb gives back what the great thing stripped. An offering rite at the pool's edge
(feeding, Ishko or Rekko) would turn that into liturgy.

**Biggest gaps.**
1. **No god at all.** A biome built around an elder being in the water has no place in the lore layer.
2. **Sky and ship are vanilla.** The weather is vanilla fog. A still, hot canopy has its own sky (sap-haze, hum-fog), and nothing touches the ship.
3. ⚠ **Tier leak:** `RM_` descriptions cite *"canon dianoga"* (`RM_SekkulaathSpleenChemicals`, `_Snare`, `_Lash`, `_Sentinel`). That is Star Wars IP in the free mod.

## Greentide

Sources: `src/RimMandrake/Greentide/` (BiomeDef `Defs/BiomeDefs/RM_Greentide_Biome.xml`), twin
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Greentide.xml`, cast patch
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_Greentide.xml` (targets `RM_Greentide`; 23 canon
`RSW_` rows plus the canopy swinger), `RUT_RoilLock_BiomeWiring.xml`, `RUT_GreentideWetBulbLock_BiomeWiring.xml`,
`src/RimUtinni/GreentideRaidAnt/`, sheets `the_greentide.md`, `greentide_risk_reward_2026-09-22.md`, `greentide_tree_roster_2026-09-22.md`.

| # | Mark | Free | Campaign | Why (source) |
|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | Churnmud that mires and swallows (`RM_MapComponent_TerrainMire`, `_MudSwallow`, `_CrossBiomeChurnmud`), buried caches you dig out, the frenzy disease, and the fever mark on survivors. Built. |
| 2 | Discoverable technology | PARTIAL | PARTIAL | Toxin sealant stops a greatbole regrowing, and the stench-smoke grenade is a recipe. No research project, and nothing is learned here and kept. |
| 3 | Unique resources | **HIT** | **HIT** | Greatbole hardwood and heartwood, sap resin, `RM_ToxinSealant`, skerrel gall, stench spore extract, and the tree roster's fruits (brakkel, tumbel, sarquin, wollick). Built. |
| 4 | Surprising creatures | PARTIAL | **HIT** | The owned trio is built: the skerrel gall-swarm, the krannock (a moss-furred beetle that drops from the canopy), and the greatbole grub (passes as a pile of fruit). But they arrive through plant-reaction spawns, and the free `wildAnimals` is **7 vanilla filler rows** (Warg, Muffalo, Elephant, Cobra, Megaspider, Rat, Hare). The campaign adds 24 patched rows and the raid ant. |
| 5 | GIANT beast | PARTIAL | PARTIAL | The colossus is a tree, `RM_Greatbole` (mineable heartwood). There is no giant beast in the free tier. The campaign has fambaa and beldon (bs 6) at trace commonality, and both are canon donors. |
| 6 | Gravship touch | MISS | MISS | Nothing. |
| 7 | Soundscape | **HIT** | **HIT** | The humming grove: `RM_Hum_Thalquith_Low/Mid/High` (`Defs/SoundDefs/RM_GreentideHummingGrove.xml`). The Warg also carries a silence aura. Built. |
| 8 | Interesting weather | MISS | **HIT** | The free weather is vanilla. The roil overlay's C# lives in the free mod (`RM_WeatherOverlay_GreentideRoil.cs`), but only `RUT_RoilWeather` uses it. The campaign adds the roil, the roil lock and the wet-bulb lock (*"sweat does nothing here"*). |
| 9 | Relationship to the gods | MISS | MISS | No god, precept or shrine in the source or the sheets. |

**Free: 3 HIT / 3 PARTIAL / 3 MISS. Campaign: 5 HIT / 2 PARTIAL / 2 MISS.**

**Rites:** none. The fever mark already singles out survivors, so a rite that marks or consecrates them is a natural pitch. Nothing is filed.

**Biggest gaps.**
1. **The free roster is vanilla filler.** Under Q11a the free mod must stand alone, and the owned trio never shows up in `wildAnimals`.
2. **The free sky is vanilla while the roil sits in the campaign.** The roil is not IP, so it can move down to the free tier.
3. **No giant beast and no god.** The greatbole is a tree.

## Gelatinous Slime

Sources: `src/RimMandrake/GelatinousSlime/` (BiomeDef `Defs/BiomeDefs/GelatinousSlime.xml`, 12 C# files), twin
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Slime.xml`, `src/RimUtinni/UtinniPatches/Patches/Slime_Rename.xml`
(labels only). **No `WildAnimals_` patch targets either Slime def.** Sheets `the_slime.md`, `the_slime_gene_lists.md`.

| # | Mark | Free | Campaign | Why (source) |
|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | Slimification (`Slimification.cs`, alert), field conversion of your farms (`MapComponent_SlimeFieldConversion`), slime visitors, and the gene archive. ⚠ Conversion is gated on the biome laying `RM_Slime_Grass` (`Source/SlimeExposure.cs` ~l.121). The frozen twin `RUT_Slime` lays `AB_Slime`/`AB_RichSlime` and carries no extensions, so conversion does not fire there until the repaint moves the world onto `RM_GelatinousSlime`. |
| 2 | Discoverable technology | **HIT** | **HIT** | `RM_SlimeChemistry` and `RM_GeneSeeking`: *"the body is a library… learn to ask it for a specific entry"*. The gene seeker samples it and injects what it finds, and the result is 58 genes you keep. Built. |
| 3 | Unique resources | **HIT** | **HIT** | Raw slime, slime blocks (stuff), slime meal, the antidote, and the gene archive's entries. Built. |
| 4 | Surprising creatures | **HIT** | **HIT** | The gelatid is a lobe of the body that herds by day and pools at night. The campaign adds the slime grazer (`RUT_SlimeGrazer`) and 9 `AA_`/2 `GR_` donors with Slime-law names. |
| 5 | GIANT beast | **HIT** | **HIT** | `RM_Titanoslime` (bs 6, five life stages, an engulf maneuver, *"a hill of green jelly that has learned to go and fetch"*). It is inline in both defs. |
| 6 | Gravship touch | MISS | MISS | Nothing. |
| 7 | Soundscape | MISS | MISS | `Ambient_NightInsects_Standard` only. A body you live on has no audible digestion, though a gene does (`RM_Gene_B16_AudibleDigestion`). |
| 8 | Interesting weather | **HIT** | **HIT** | `RM_Weather_SlimeRain` carries 30 of 86 weight. (The frozen twin is `Clear` 60 plus vanilla.) |
| 9 | Relationship to the gods | MISS | MISS | Nothing. |

**Free: 6 HIT / 0 PARTIAL / 3 MISS. Campaign: 6 HIT / 0 PARTIAL / 3 MISS.** The campaign layer adds nothing of its own beyond names.

**Rites:** none. A rite of being read is the obvious one: a willing offering of a genome to the library, held by Ozzik (venting) or Oomo.

**Biggest gaps.**
1. **The campaign layer is empty.** There is no `WildAnimals_` patch, no campaign mechanic and no god, and the frozen `RUT_Slime` twin is an Alpha Biomes shell. Today's world plays a much poorer Slime than the free mod.
2. **No sound, no ship, no god** for a biome that is literally a mind filing entries.
3. ⚠ **Tier leak:** `RM_` gene names carry Star Wars IP (`RM_Gene_B2_VestigialLekku`, `_B4_BanthaSnore`, `_B12_StartleJawaese`).

## Weeping Stones

Sources: `src/RimMandrake/WeepingStones/` (BiomeDef `Defs/BiomeDefs/RM_WeepingStones_Biome.xml`, 18 C# files),
`src/RimMandrake/OasisMaker/`, `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_WaterTruce.cs`, twin
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_WeepingStones.xml`, cast patch
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_WeepingStones.xml` (targets `RM_WeepingStones`; 8 canon desert
`RSW_` rows), sheets `weeping_stones.md` and `weeping_stones_shine_options_2026-09-24.md` (verdicts).

| # | Mark | Free | Campaign | Why (source) |
|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | The stocked pool: pen zones where you stock, feed, net and harvest, and cull the vhorrin (`RM_Zone_PoolPen`, `RM_MapComponent_PoolStock`). Plus the water truce with animal retribution (`RM_WaterTruceExtension`, `RM_MapComponent_WaterTruce`). Built. |
| 2 | Discoverable technology | PARTIAL | PARTIAL | The oasis-maker machines (`src/RimMandrake/OasisMaker/`, `RM_CompOasisMaker`) are the right shape: an ancient machine, found as treasure, that slowly grows an oasis. But it is a separate mod, it is not taught by this biome, and the quests to obtain or sabotage it are ruled, unbuilt. Pool husbandry has no research project. |
| 3 | Unique resources | **HIT** | **HIT** | Seep salt, seep stone, dewgourd and bladder fruit, pool-fry baskets, murrin broth, karrek paste, huldu fat, the cull feast (5 recipes, 8 eat-thoughts). Built. |
| 4 | Surprising creatures | **HIT** | **HIT** | The loomu, a boneless grey thing that repeats what it hears at the bank. The ivvol, a doormat-sized floor-thing whose ridge of eyes counts. The sillik, which licks the weep-faces. All 17 are owned and inline. |
| 5 | GIANT beast | **HIT** | **HIT** | `RM_Gorrask` (bs 15), a stone-crab too big for any canyon it did not carve. The placid tirbak (bs 3.5) sits below it. Built. |
| 6 | Gravship touch | MISS | MISS | Nothing. |
| 7 | Soundscape | MISS | MISS | No SoundDef and no `soundsAmbient`. The loomu's mimicry is description only. Wind-hour, the obvious register, was ruled DEAD (*"nah"*, 2026-09-24). |
| 8 | Interesting weather | MISS | MISS | `Clear` 70, `Fog` 25, `Sandstorm` 6. Vanilla. The weeping faces are terrain, not sky. |
| 9 | Relationship to the gods | MISS | PARTIAL | Free: nothing. Campaign: the sheet makes the oasis the **Oomo** water-archetype ground, and a sacred register runs through it (`weeping_stones.md` l.19, l.109, l.200). Oasis landmarks carry it as whispers (`StructureInjectionsRUT`). That is lore with no precept. |

**Free: 5 HIT / 1 PARTIAL / 3 MISS. Campaign: 5 HIT / 2 PARTIAL / 2 MISS.**

**Rites:** none. ⚠ The rites register (`design/Jawa/salvation_rites_2026-10-01.md` §B6) lists *"The pool rites, wind-hour"* as PITCHED. But wind-hour was **ruled DEAD** on 2026-09-24 (shine options verdict 4), so that row is stale. The open question is a non-wind-hour rite of Oomo at the truce water: an oath kept at the pool would fit the retribution law.

**Biggest gaps.**
1. **Sky and sound are vanilla**, and the obvious register (wind-hour) is dead. A replacement has to be invented.
2. **No god in the free tier.** The Oomo tie is campaign prose only.
3. **The oasis machines live in another mod** and are not this biome's discovery, and the quests that would make them treasure are unbuilt.

## The Sump

Sources: `src/RimMandrake/TheSump/` (BiomeDef `Defs/BiomeDefs/RM_TheSump_Biome.xml`), twin
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Sump.xml`, cast patch
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_Sump.xml` (targets `RM_TheSump`; adds only `RSW_Hssiss`),
`BiomeArrivalLetters_TheSump.xml`, `src/RimUtinni/UtinniPatches/Defs/ResearchProjectDefs/RUT_Sump_Research.xml`,
sheets `the_sump.md`, `sump_fauna_roster_2026-09-24.md` and `sump_flora_roster_2026-09-24.md`, and the live `SUMP_*` items.

| # | Mark | Free | Campaign | Why (source) |
|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | Tar moats with fuse posts (`RUT_TarMoat`, `RUT_MoatFusePost`), a dig-strata lottery (`RUT_DigStratumTable`), the tar-vault seal (`RM_Comp_TarVaultSeal`), the pit belch, and the deep black mere genstep. Built. |
| 2 | Discoverable technology | MISS | PARTIAL | Free: no research. Campaign: `RUT_GaslightChemistry` is built (*"the same reaction the Sump's own geysers do"*). `RUT_TarRendering` says of itself *"Unwired flavor tech for now"*. |
| 3 | Unique resources | **HIT** | **HIT** | Korveth pitch, tar-cured leather, seepwax, brommet wool, skarrid hide, and three chitins. Campaign adds sumpgas. Built. |
| 4 | Surprising creatures | **HIT** | **HIT** | The sump-mouse moves in files, and its bent trails show where the tar is thin. The skellarn is a twilight flier on four spike-stilts. The skarrid is *"a bulge slightly too small to be the thing everyone fears"*. Owned and inline. |
| 5 | GIANT beast | MISS | MISS | The largest resident is the gulveth (bs 1.5). The feared tar beast exists only as a bulge and a dread (`RUT_BeastBulge`, `DEPLOY_HOLD`'d). The absence may be deliberate, but no colossus exists. |
| 6 | Gravship touch | MISS | PARTIAL | Campaign: an arrival letter, *"The Ship Remembers the Sump"*, in which the ship's memory warns you about the thin tar. It is a letter, not a mechanic. |
| 7 | Soundscape | MISS | MISS | No SoundDef and no `soundsAmbient`. |
| 8 | Interesting weather | MISS | **HIT** | `RUT_SumpWeather` and `RUT_SumpDuskLock` (the sun sits just below the horizon, forever) **ship in the free mod but are wired only to `RUT_Sump`** (`Patches/RUT_SumpDuskLock_BiomeWiring.xml`), so the free def runs vanilla `Fog`/`Clear`. ⚠ The campaign HIT lives on the twin only. |
| 9 | Relationship to the gods | MISS | MISS | Nothing in source or sheet. |

**Free: 3 HIT / 0 PARTIAL / 6 MISS. Campaign: 4 HIT / 2 PARTIAL / 3 MISS.**

**Rites:** none. The ship's memory of others sinking here is the natural seed: a rite for the drowned, held at the mere (Rekko, consolation).

**Biggest gaps.**
1. **No giant, by design or by omission.** The feared tar beast is the biome's whole dread, and it never surfaces. Decide whether it ever does.
2. **The dusk is wired to the twin only.** Re-wire it to `RM_TheSump`, or the free tier keeps vanilla fog and the campaign loses the dusk at the repaint. ⚠ Defs named `RUT_` also ship inside an `RM_` mod (`RUT_SumpWeather`, `RUT_SumpDuskLock`, `RUT_TarPitBelch`, `RUT_GenStep_*`), which is a tier-grammar slip.
3. **Sound, gods and free tech are all blank.**

## Miasma

Sources: `src/RimMandrake/Miasma/` (BiomeDef `Defs/BiomeDefs/RM_Miasma.xml`), twin
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Miasma.xml`, cast patch
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_Miasma.xml` (targets `RM_Miasma`; 14 `RSW_` rows, including the sea-fish
juveniles), `RUT_Miasma_PollinationGate.xml`, sheets `the_miasma.md`, `miasma_fauna_roster_2026-09-23.md` and `miasma_flora_roster_2026-09-23.md`.

| # | Mark | Free | Campaign | Why (source) |
|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | The gradient axis and the surge, when the sea shoves up the channels (`RUT_GenStep_GradientAxis`, `RUT_GradientSurge`, `RUT_Surge`). Warden-mother succession and crèche nurseries (`RM_WardenMotherSuccession.cs`, `RUT_GenStep_CrecheScatterer`). Fever-forging on survival (`Patches/RUT_Miasma_ForgeOnSurvival.xml`). Plant predation (`RM_CompPlantPredator`). Built. |
| 2 | Discoverable technology | PARTIAL | PARTIAL | What you keep is your body: fever-forged traits and hardened immunities (`RUT_FeverForged_*`, `RUT_HardenedImmunity_*`). It is a real "you keep it" mark, but it is not a technology, and there is no research project. |
| 3 | Unique resources | **HIT** | **HIT** | Delta salt (*"the one the stills need most"*), delta silt, and the mangal flora (thessamor, brelloch, ilbareen and others). Built. |
| 4 | Surprising creatures | **HIT** | **HIT** | The karravel, karrimeth and karrolun scuttler carpets, and the fever swarm, a drifting gold haze that is an animal. The campaign adds the crèche juveniles of the sea's fish. ⚠ The karrobel and the fever swarm are invented, non-canon species, yet they are authored in `mandrake.rut.patches` and sit `MayRequire`-gated in the free def (`RM_Miasma.xml` l.235-236), so **the free mod loses both** without the campaign. |
| 5 | GIANT beast | **HIT** | **HIT** | `RM_WardenMother` (bs 8), barnacled and older than anything else in the shallows, the reason nobody goes out onto the open water. Built. |
| 6 | Gravship touch | MISS | MISS | Nothing. |
| 7 | Soundscape | MISS | MISS | The haze weather says *"Sound is muted"*, but its own comment leaves `ambientSounds` *"intentionally empty… a sound-design content call"* (`Defs/WeatherDefs/RUT_MiasmaWeather.xml` l.40). |
| 8 | Interesting weather | **HIT** | **HIT** | `RUT_MiasmaWeather` is a permanent green-gold haze that *"never, ever rains"*, locked by `RUT_MiasmaWeatherLock` (wired inline in `RM_Miasma.xml` l.104). It is joined by `RUT_SurgeWeather`. Built. |
| 9 | Relationship to the gods | MISS | MISS | The sheet calls the nurseries *"sacred-adjacent"* and says harming one is *not* sacrilege (`the_miasma.md` l.218). No god is attached. |

**Free: 6 HIT / 1 PARTIAL / 2 MISS. Campaign: 6 HIT / 1 PARTIAL / 2 MISS.**

**Rites:** none. The warden mothers and their crèches are a ready shrine: a rite that takes in a warden's young, or one held at the crèche at surge-tide (Oomo, the nursed stranger), is a natural pitch.

**Biggest gaps.**
1. **No voice.** The haze is written as muting sound, and nothing plays.
2. **No god and no ship.** The *"Working's breath"* in the weather text points at a lore hook that no god holds.
3. **Two invented species sit on the wrong tier.** Move the karrobel and the fever swarm to `RM_` so the free roster stands alone (Q11a). ⚠ `RUT_`-prefixed defs ship inside this `RM_` mod (weather, conditions, hediffs, gensteps), which is a tier-grammar slip.

## Webwork

Sources: `src/RimMandrake/Webwork/` (BiomeDef `Defs/BiomeDefs/RM_Webwork_Biome.xml`), twin
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Webwork.xml`, `src/RimUtinni/UtinniPatches/Defs/ThingDefs*/RUT_WebworkStructures.xml`,
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_Webwork.xml` (**empty by ruling**: all 4 SW rows cut 2026-09-24),
`WildPlants_Webwork.xml` (adds the tooke-trap), sheets `the_webwork.md` and the roster docs.

| # | Mark | Free | Campaign | Why (source) |
|---|---|---|---|---|
| 1 | Unique mechanic | PARTIAL | **HIT** | Free: nest scatter (`RM_GenStep_WebworkNest`), egg-clutch relay, loom-binding (`RM_LoomBound`), and sun scald in a jungle whose water is inside the plants. The signature, **the creeping web front** (`RM_FrontCreepExtension`), is on the twin only. The free def deliberately leaves it off until `WEBWORK_WEB_STRUCTURES_1` ports the structures (`RM_Webwork_Biome.xml` l.26). ⚠ Campaign HIT is twin-only. |
| 2 | Discoverable technology | MISS | MISS | No research project. The loom-spit "gun" is the ollathrix's own spinneret, not a player technology. |
| 3 | Unique resources | **HIT** | **HIT** | Tavrosk liquor, brimlock water (the river, drunk out of a plant), ollathrix eggs, quarrok chitin, fellome pods. Built. |
| 4 | Surprising creatures | **HIT** | **HIT** | The vennick *"read as a current, not as animals"*. A cravvet parked on a stain marks a fresh kill site. The sivvern hunts in silence. All 6 are owned, and the campaign's SW cast was cut by ruling. |
| 5 | GIANT beast | PARTIAL | PARTIAL | `RM_Ollathrix` is *"a spider the size of an elephant"*, the shadow seconds before it lands, but it is only bs 2.6. A true colossus is absent. |
| 6 | Gravship touch | MISS | MISS | Nothing. |
| 7 | Soundscape | **HIT** | **HIT** | The biome is defined by silence: `soundsAmbient` is `RM_Webwork_Hush`, with `RM_Webwork_Thrum` beside it (`Defs/SoundDefs/RM_WebworkSoundscape.xml`), and `RM_MapComponent_SenseWeb` in CreatureBehaviors. Built. |
| 8 | Interesting weather | MISS | MISS | `Clear` 50 plus vanilla rain and fog. |
| 9 | Relationship to the gods | MISS | MISS | Nothing. |

**Free: 3 HIT / 2 PARTIAL / 4 MISS. Campaign: 4 HIT / 1 PARTIAL / 4 MISS.**

**Rites:** none. A biome that drank its river suggests a water-giving rite: offering brimlock water back (Oomo), or a binding vigil against the shadow (Sh'kaar, warding).

**Biggest gaps.**
1. **The free tier lacks its own signature.** The web front lives on the twin, pending `WEBWORK_WEB_STRUCTURES_1`, and it is lost at the repaint unless it moves.
2. **No tech, no weather, no god, no ship.** Four blank marks.
3. **No colossus.** The ollathrix is a big spider, not a giant.

## Rust Cathedral

Sources: `src/RimMandrake/RustCathedral/` (BiomeDef `Defs/BiomeDefs/RM_RustCathedral_Biome.xml`, Hum and Walls C#), twin
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_RustCathedral.xml`, `src/RimUtinni/RustCathedralRoaches/`.
**No patch targets either def.** Sheets `the_rust_cathedral.md` and `the_rust_cathedral_SCALD_HISTORY_amendment_draft.md`.

| # | Mark | Free | Campaign | Why (source) |
|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | The hum, a biome *attitude* that moves through mood bands and answers how you behave (`Source/Hum/RM_MapComponent_BiomeAttitude.cs`, `RUT_RustCathedralAttitude`). Living bolts that behave differently when watched (`HarmonyPatch_WatchedBolts`). Deep-drilling draws a cathedral response (`RUT_DeepDrillCathedralResponse`), and live pattern-metal is gated (`HarmonyPatch_GateLivePatternMetal`). Built. |
| 2 | Discoverable technology | MISS | MISS | Smartsteel is described as *"self-assembling, self-repairing"* once, and now *"just very good metal"*. Nothing is learned from it. |
| 3 | Unique resources | **HIT** | **HIT** | Dead smartsteel (mineable vein and item), live pattern-metal, cathedral deck plate, roach shell, the bolt-shed curiosity. Built. |
| 4 | Surprising creatures | **HIT** | **HIT** | The living bolt (*"a bolt with legs, or a gear with opinions"*), the cathedral roach (a mechanoid that cleans), and the coolant eel, which you fish out as a bad catch (`RM_CathedralFishing`). Built. |
| 5 | GIANT beast | MISS | MISS | The largest resident is bs 0.22. Nothing colossal; the garrison is mechanoids. |
| 6 | Gravship touch | MISS | MISS | Nothing. (The `ResearchRetag` gravtech rows only mention the biome.) |
| 7 | Soundscape | **HIT** | **HIT** | The hum is three layered SoundDefs, `RUT_HumLayerDrone/Tense/Alarm` (`Defs/SoundDefs/RUT_HumLayers.xml`), driven by the attitude bands. Bolts do a resonant dance. Built. |
| 8 | Interesting weather | MISS | MISS | `Clear` 90, `DryThunderstorm` 4. An eternal noon with no sky of its own. |
| 9 | Relationship to the gods | PARTIAL | PARTIAL | Sacred walls are scattered and watched (`RUT_SacredWall_Conduit`, `GenStep_ScatterSacredWalls`), and the sacrilege economics are ruled (sheet l.145, l.333). The campaign adds the Warscar pilgrim camps' *"a god's deathbed"* (specced). No god is named and there is no precept. |

**Free: 4 HIT / 1 PARTIAL / 4 MISS. Campaign: 4 HIT / 1 PARTIAL / 4 MISS.**

**Rites:** none. The sheet calls this *"the first of many sacred moments"*, so the rite slot is the most obvious one on the planet: a rite of *manners* before the sacred core, or a resonant-dance rite. It is unpitched.

**Biggest gaps.**
1. **The sacred register names no god.** "A god's deathbed" needs a god and a rite, and this biome is the best-prepared for one.
2. **No colossus and no sky.** A "garrison" biome with no giant is missing its centrepiece mech.
3. **Smartsteel teaches nothing.** "Self-repairing alloy" is a ready discoverable technology. ⚠ Many `RUT_` defs ship inside this `RM_` mod (`RUT_LivingBolt` is inline in the free def), which is a tier-grammar slip.

## Lantern Deeps

Sources: `src/RimMandrake/LanternDeeps/` (BiomeDef `Defs/Biomes/RM_LanternDeeps.xml`, a pocket-map layer entered from
other biomes). **There is no `RUT_` twin.** Cast patch `src/RimUtinni/UtinniPatches/Patches/WildAnimals_LanternDeeps.xml`
(targets `RM_LanternDeeps`; 8 ported Biomes! Team cave rows). Also `RUT_LanternDeepGateKyber.xml`,
`RUT_LanternDeepGateKotorStygium.xml` and `RUT_LanternstoneKotorCrystals.xml`. Sheets `the_lantern_deeps.md` and `lantern_deeps_flora_names.md`.

| # | Mark | Free | Campaign | Why (source) |
|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | A persistent pocket cavern opened from a lanternstone emergence or a ruined mineshaft (`RM_LanternDeepGenerator`, `GenStep_ScatterCavePortal`/`MineshaftPortal`). Darkness lit only by lanternstone (`MapComponent_LanternDeepDarkness`). Deep-flora regrowth, and pocket-map growth rates. Built. |
| 2 | Discoverable technology | PARTIAL | PARTIAL | Lanternstone can be sown (`RM_Lanternstone_Sowable`), so you take a light that grows home with you. But no research project teaches it, and kyber is *"crafting material only"* (sheet l.137, `FORCE_POWERS_ARE_V2_1`). |
| 3 | Unique resources | **HIT** | **HIT** | Lanternstone (rock, chunks, walls, volatile crystal formations) and puffer tendrils. The campaign adds kyber and stygium gates (`RUT_LanternDeepGateKyber.xml`, `…KotorStygium.xml`). Built. |
| 4 | Surprising creatures | MISS | **HIT** | **The free def's `wildAnimals` is empty.** Every resident is patch-added by the campaign. Campaign: the soulchime, a larva armoured in crystal shards that stuns with its mind; the drinker, a near-silent blood-moth; the glowbulb, a slug lit by its own oil. They are ported Biomes! Team inventions, not owned. |
| 5 | GIANT beast | MISS | PARTIAL | Free: no fauna. Campaign: the grabber (`RSW_BovineBeetle`, bs 4, *"a small room-sized blob"* with one great pincer) is the largest, and it is ported, not owned. |
| 6 | Gravship touch | MISS | MISS | Nothing. Being underground is the obvious reason, but it is still unaddressed. |
| 7 | Soundscape | **HIT** | **HIT** | `RUT_DeepHum` and `RM_DeepChorus` (`Defs/SoundDefs/RM_DeepAmbience.xml`): the deeps *hum*. Built. (A `RUT_` def inside an `RM_` mod.) |
| 8 | Interesting weather | PARTIAL | PARTIAL | `RM_DeepCalm` at 100: *"The air under the mountain does not move. No penalties or modifiers."* It is unique because there is no sky, but nothing happens in it. |
| 9 | Relationship to the gods | MISS | MISS | The sheet's *mindstone*, *"aware"*, is the obvious hook, but it appears nowhere in `src/`. |

**Free: 3 HIT / 2 PARTIAL / 4 MISS. Campaign: 4 HIT / 3 PARTIAL / 2 MISS.**

**Rites:** none. The mindstone is a found-rite seed: a rite performed in the dark before an aware stone, a natural fit for the Rites tab's darkness gate.

**Biggest gaps.**
1. **The free tier has no animals at all.** It is the worst free roster of the twelve, and it breaks Q11a outright.
2. **No god, though the sheet wrote one.** The aware mindstone is unbuilt.
3. **The calm is inert.** An underground "weather" could be air that changes: cold breath, crystal-song surges.

## Pyrelands

Sources: `src/RimMandrake/Pyrelands/` (BiomeDef `Defs/BiomeDefs/Pyrelands.xml`, 24 C# files), `src/RimUtinni/PyrelandsMechanics/`.
**There is no `RUT_` twin.** Cast patch `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml` (targets `RM_Pyrelands`; it
**replaces** the free `wildAnimals`, then adds 7 `RSW_` and 6 `RUT_` rows). Also `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Races/RUT_PyrelandsFauna.xml`
and `AshStorms_Pyrelands.xml`. Sheet `the_pyrelands.md`, with the `PYRELANDS_*` items.

| # | Mark | Free | Campaign | Why (source) |
|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** | **HIT** | It burns on its own schedule. Ember grass regrows in under a day and dries to tinder. Burns bank ash in four layers (`RM_FE_Ash_Trace` through `_Deep`), and the burn line and firebreaks are tracked (`MapComponent_BurnLine`). Lightning makes fulgurite (`Patch_LightningStrike_Fulgurite`). Built. |
| 2 | Discoverable technology | PARTIAL | PARTIAL | The firefoam sprayer (`RM_FE_FirefoamSprayer`) is the biome's answer to fire, but it is a building, not something learned. No research project. |
| 3 | Unique resources | **HIT** | **HIT** | Fulgurite and scorch fruit, which grow out of fire (`Patch_FireTick_AshAndScorchFruit`). The campaign adds furnace hide and the flame harvest (`IncidentWorker_FlameHarvest`). Built. |
| 4 | Surprising creatures | MISS | **HIT** | **The free `wildAnimals` is 13 vanilla rows** (Hare, Rat, Gazelle … Warg). The free mod carries the *machinery* for its stars (`RM_FireHawk_CarryEmber`, `RM_FurnaceBeast_ThermalCycle`, `CompFireHawkSpread`, the `RM_FurnaceHerd` world object), but the creatures are `RUT_` defs in UtinniPatches. Campaign: a fire hawk that carries embers to spread the burn, a flamefang that beds down ahead of the fire front, and a fire wasp that lives inside the heat. |
| 5 | GIANT beast | MISS | PARTIAL | Campaign: `RUT_FurnaceBeast` (bs 3.2) is migratory megafauna and *"a slow thermal capacitor on legs"*, with a world-map herd. It has presence but not colossal size. Free: none. |
| 6 | Gravship touch | MISS | MISS | Nothing. |
| 7 | Soundscape | MISS | MISS | `Ambient_NightInsects_Standard`. A burning savanna is silent. |
| 8 | Interesting weather | **HIT** | **HIT** | `RM_FE_Weather_AshFall` (14), `RM_FE_Weather_Cinderfall` (4), `RM_FE_BlackRain` (3), and dry thunder at 20. The campaign adds volcanic ash. Built. |
| 9 | Relationship to the gods | MISS | **HIT** | Campaign: the deep tribes' fire rite is **built** (`LordJob_RUT_FireRite.cs`, `PyrelandsFireRiteHook.cs`), with fire raids. It is the only biome of the twelve whose god-layer is real code. It is another faith's rite, not the Salvation's. |

**Free: 3 HIT / 1 PARTIAL / 5 MISS. Campaign: 5 HIT / 2 PARTIAL / 2 MISS.**

**Rites:** the deep tribes' fire rite exists, but it is theirs: ruled 2026-10-01, *a Salvation colony cannot learn other faiths' rites*. There is **no found rite** for the Salvation. The natural Salvation pitch is a rite of the burn line, an offering made to a fire you set.

**Biggest gaps.**
1. **The free tier's creatures live in the campaign.** Eight invented, non-canon species (fire hawk, furnace beast, flamefang, fire wasp, emberscythe, sytheclaw, barbslinger, ashwallow) are `RUT_`, so the free roster is vanilla while the free mod ships their AI. Q11a says they belong on `RM_`.
2. **No sound.** Crackle, roar and the hush after a burn are an obvious register.
3. **No colossus.** The furnace beast (bs 3.2) could be grown into one.

## Nightside Ice

Sources: `src/RimMandrake/NightsideIce/`, which holds **one BiomeDef** (`Defs/BiomeDefs/RM_NightsideIce.xml`, label *"the
Sleeping Ice"*) and a settings class, nothing else. Twin `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_NightsideIce.xml`. Cast patch
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_NightsideIce.xml` (targets `RM_NightsideIce`; adds the mahllik, `RSW_CaveLemming`).
`AncientDangerGenSteps_AmbientDoctrine.xml` *prevents* shrines on both defs. Sheet `nightside_ice.md`, owner-ratified, with
§4c, the tunneler slate, ratified 2026-09-24.

| # | Mark | Free | Campaign | Why (source) |
|---|---|---|---|---|
| 1 | Unique mechanic | **HIT** (ruled, unbuilt) | **HIT** (ruled, unbuilt) | Thermal sensing: *"the player is the loudest thing on the hemisphere"*. Tunnelers are a moving underground threat with a live surface tell, scaling off your heat output, which §4c calls something no game has done. Calving that gives up what the ice swallowed. Nothing is built. |
| 2 | Discoverable technology | PARTIAL (ruled, unbuilt) | PARTIAL (ruled, unbuilt) | *"Cold as a resource: free superconduction, refrigeration, heat rejection"* and the electrojet tap (§7). These are uses, not something taught. |
| 3 | Unique resources | **HIT** (ruled, unbuilt) | **HIT** (ruled, unbuilt) | Dirty ice (melt and filter), and calving inclusions: machine parts, cocoons, *"the well-provisioned dead"* (§7 ⭐). |
| 4 | Surprising creatures | **HIT** (ruled, unbuilt) | **HIT** (ruled, unbuilt) | ⭐ *The one-move animal*: it saves for a century, moves exactly once, and is inert forever after (§4). Also the tunneler slate (§4c). Built today: 7 `AA_` donor rows at commonality 0.002–0.03, plus the mahllik in the campaign. |
| 5 | GIANT beast | **HIT** (ruled, unbuilt) | **HIT** (ruled, unbuilt) | ⭐ *"Organisms here grow to enormous scale… A ridge is an organism. A boulder field is one organism."* The planet's best-argued giant has no def. |
| 6 | Gravship touch | MISS | MISS | Nothing. A landed ship is the hottest thing on the hemisphere, and that is unclaimed. |
| 7 | Soundscape | MISS | MISS | No sound. The canon anchor, *"tunnels that make the wind sing"*, is cited in §4c but not ruled as sound. |
| 8 | Interesting weather | **HIT** (ruled, unbuilt) | **HIT** (ruled, unbuilt) | The §4b table: thaw pulse, rime-fall, the reconnection storm (radiation up, circuits surge), and aurora-clear. Built today: `Clear` 100. |
| 9 | Relationship to the gods | MISS | MISS | Nothing. Shrines are explicitly prevented. |

**Free: 6 HIT / 1 PARTIAL / 2 MISS, all ruled and unbuilt; 0 HIT as built. Campaign: the same, plus one built ported grazer.**

**Rites:** none. *Perfect, indefinite preservation… a deep record of all who fell here* (§7), and §4b's *lost soul* (save them or bury them), point at a burial rite in the ice (Rekko, the mourning).

**Biggest gaps.**
1. **Nothing is built.** It is the best-designed and least-built of the twelve: a whole ratified sheet over an empty mod.
2. **The free roster is 7 trace donor rows.** The one-move animal, the tunnelers and the ridge-organism all need defs.
3. **No god, no sound, no ship.** The thermal law hands it a ship touch for free.

## Summary

Scores are HIT / PARTIAL / MISS out of nine.

| Biome | Free | Campaign | Biggest gap |
|---|---|---|---|
| The Rot | 3 / 4 / 2 | 3 / 4 / 2 | No sound and no ship, and the free cast is all `AA_` donor (the 10-row `RM_` migration proposal is unapplied) |
| Fever Wood | 5 / 1 / 3 | 5 / 1 / 3 | No god for an elder being in the pools; vanilla sky |
| Greentide | 3 / 3 / 3 | 5 / 2 / 2 | Free `wildAnimals` is 7 vanilla filler rows; the roil is campaign-only |
| Gelatinous Slime | 6 / 0 / 3 | 6 / 0 / 3 | No sound, ship or god; the campaign layer adds nothing |
| Weeping Stones | 5 / 1 / 3 | 5 / 2 / 2 | Vanilla sky and silence, and wind-hour (the obvious register) is ruled dead |
| The Sump | 3 / 0 / 6 | 4 / 2 / 3 | No giant (the tar beast never surfaces); the dusk is wired to the twin only |
| Miasma | 6 / 1 / 2 | 6 / 1 / 2 | Muted with no sound; two invented species on the wrong tier |
| Webwork | 3 / 2 / 4 | 4 / 1 / 4 | The web front (its signature) is twin-only; no tech, weather or god |
| Rust Cathedral | 4 / 1 / 4 | 4 / 1 / 4 | A sacred register with no named god or rite; no colossus |
| Lantern Deeps | 3 / 2 / 4 | 4 / 3 / 2 | **The free def has zero animals**; the mindstone god-hook is unbuilt |
| Pyrelands | 3 / 1 / 5 | 5 / 2 / 2 | 8 invented creatures are `RUT_`, so the free roster is vanilla while the free mod ships their AI |
| Nightside Ice | 6 / 1 / 2 *(ruled, unbuilt; 0 built)* | same | **Nothing is built.** The mod is one BiomeDef under a fully ratified sheet |

**Across all twelve.**
- **Gravship touch (mark 6) is MISS in all 12 free tiers.** The only campaign touch is the Sump's *"The Ship Remembers"* letter (PARTIAL).
- **Relationship to the gods (mark 9) is the next-weakest.** Only the Pyrelands' campaign tier HITs, through another faith's built fire rite. The Rot (pale tree) and the Rust Cathedral (sacred walls) are PARTIAL. Nine of twelve free tiers MISS.
- **Rites: no grandfathered biome teaches the Salvation a found rite.** Each section names the natural seed. ⚠ The register's Weeping Stones row (*"pool rites, wind-hour, PITCHED"*, `salvation_rites_2026-10-01.md` §B6) is stale, because wind-hour was ruled DEAD on 2026-09-24.
- **Discoverable technology (mark 2):** only the Slime HITs (gene seeking). Everywhere else it is recipes or husbandry.
- **Free rosters broken against Q11a** (*"rich enough to stand alone"*): Lantern Deeps (empty), Greentide and Pyrelands (vanilla filler), the Rot and Nightside Ice (donor only), and Miasma (two invented species gated on the campaign).
- **Content wired to the frozen twin only, which is lost at the repaint unless moved:** the Greentide roil and wet-bulb locks, the Sump dusk lock, and the Webwork front creep.
- **Tier leaks:**
  - Star Wars IP inside `RM_` text: the Rot's pale tree (*"the Force"*), Fever Wood's sekkulaath (*"canon dianoga"*), and Slime genes (`…VestigialLekku`, `…BanthaSnore`, `…StartleJawaese`).
  - `RUT_`-prefixed defs shipping inside `RM_` mods: the Sump, Miasma, Rust Cathedral and Lantern Deeps.

## Recommended sitting order

Worst first, by built free-tier strength, with the cheapest big win noted.

1. **Nightside Ice.** 0 of 9 built. The sheet is ratified, so this sitting is mostly movement 4 (ticket and commission), plus marks 6, 7 and 9.
2. **Lantern Deeps.** The free tier has no animals at all. Its roster fill comes first, then the mindstone as god and rite.
3. **Pyrelands.** Five free misses. Moving 8 invented `RUT_` creatures to `RM_` repairs marks 4 and 5 at once. Then sound and a Salvation rite of the burn line.
4. **The Sump.** Six free misses. Decide whether the tar beast ever surfaces (mark 5), move the dusk onto `RM_TheSump`, then sound and gods.
5. **Webwork.** Four misses. Port the web front to the free def (`WEBWORK_WEB_STRUCTURES_1`), then weather, tech and god.
6. **Greentide.** Its free roster is vanilla filler, and the roil should move down. The campaign tier is already strong.
7. **Rust Cathedral.** Four misses, but the best-prepared god slot on the planet (*"the first of many sacred moments"*), so it is a quick rite win. It also needs a colossus.
8. **The Rot.** The cast migration is already proposed (apply it). Then sound and ship.
9. **Fever Wood.** Three misses: god, weather, ship. A strong spine.
10. **Weeping Stones.** Three misses. It needs a non-wind-hour sound and sky, and to make the Oomo tie real.
11. **Gelatinous Slime.** Three misses (sound, ship, god). The free tier is near the bar, but the campaign layer is empty.
12. **Miasma.** The strongest of the twelve (6 HIT). Sound and god only.
