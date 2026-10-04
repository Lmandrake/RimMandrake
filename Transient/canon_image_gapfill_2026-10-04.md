# Canon image gap-fill — 2026-10-04

Owner request: the canon library showed nothing for Gorg; fill canon-beast gaps from Wookieepedia (canon and /Legends).

## Root cause (gorg)
There was **no gorg entry in the library at all** — not empty images, a missing directory. None of
`RSW_Gorg`, `RSW_LongtailGorg`, `RSW_FrilledGorg` had one, so the sheet printed "no canon-library
entry". The library was built from a 45-creature list and never covered the ~200 SWBestiary race
defs ported later (MLIE_FAUNA_ABSORPTION_1). Fixed: `gorg/` (canon `Gorg` + `Gorg/Legends`, 4
images incl. the purple `Gorg-WoSW.png`, brief + Must show written by viewing) and `longtailgorg/`
(no separate article; long-tailed variety per `Gorg/Legends`, 3 film images). `RSW_FrilledGorg`:
no Wookieepedia title ("Frilled newt" is a different animal) — looks invented by the donor mod.

**Gorg is several looks, not one** (owner follow-up): `gorg/` now lists six canon variants
(purple four-eyed; pale grinning; hammer-headed; spiky-backed; fin-tailed; spotted long-tailed
film gorg), each with its source image, including the Dutch wiki's `Gorgs1.jpg` (four gorgs
hanging in a market). **Our defs can carry several looks already:** `RSW_Gorg` has
`alternateGraphics` base + A–E (6 slots), `RSW_LongtailGorg` base + A–D, `RSW_FrilledGorg`
base + A–C — but every slot is the same donor silhouette recoloured, so they vary colour only.
Giving each slot a distinct canon shape needs new art per slot (proposal; cosmetic change needs
the owner's word).

Note: the wiki CDN serves WebP whatever the file is named; pulled files are named `.webp`.

## Summary
- Swept every non-humanlike race def under `src/RimStarWars` (249; juvenile/larva/pupa variants
  folded into the parent → 179 base creatures checked). Sanity probe: `bantha` resolved canon +
  Legends with 8 candidate images before any subject ran.
- **64 creatures filled** (63 new entries incl. hand-written `gorg` and `longtailgorg`, plus
  `blurrg`, the one existing entry with no images, now 4), **201 images added**, canon and /Legends both read;
  Legends images are labelled as Legends in each entry's `## Candidate images`.
- Library: 138 → 201 entries, 583 → 784 reference images. All 784 registered in the art ledger
  (`art.py backfill canon`, 201 new canon variant events), so review sheets show them.
- ⚠️ New script-made entries carry sourced text, Source URLs and captioned images, but their
  **Visual brief and Must show are OWED** (no agent viewed those images). `gorg` and
  `longtailgorg` were viewed and written in full.
- ⚠️ Identity is by exact Wookieepedia title + creature infobox. One collision found and dropped
  (screecher). The rest were not cross-checked against our def descriptions.
- Existing entries: only `blurrg` had no images; the other 45 creature entries all had some.

## Still missing — no Wookieepedia title matched (114)
Most look invented by donor mods (Mlie, VE-style biome packs) or by us. They are listed for the
owner, not filed. A guessed-title miss does not prove a creature is non-canon, but each was
searched by label and defName: Baseopsis, Diplocaulus, Holcorobeus, Platyhystrix, Protosolpuga, Protovermes, Scavrats, Segnosaurus, Termitotron, aaroxis dendoria, abyssal colo, acid slug, alpha wraid, basilisk, bloodletter petrel, bloodrop larvae, bloodrop pupa, bokka, bunker bug, chikka, crested dragon, crimson opee, crystal crab, crystal fairy mole, diggerpede, drazzik, drinker, durrok, elder sando, excretor, facet moth, fang leaf, feral grazer, feral nerf, foundry beetle, frilled gorg, gastro toad, gembug, glowbulb, glowtail, grabber, grellik, groundrunner, ikee, imperial toad, jellypot, jewel beetle, karrask, khorrak, korrum, kroffa, kudda, lanternwhale, maguana, mahllik, mature fleshbeast, maxolotl, megakrill, megaphorid, megapleura, moornak, moss beetle, mullgoth, mutagenic norphea, mutating tumorfish, mutating tumorfish fry, mutating tumorfish spawn, nizzek, ommok, onnik, ossik, pod worm, polluwog, puffmite, pustule hornet, pustule hornet, pustule queen, pustule queen, reefback, royal rhino beetle, rust nipper, sacapillar, sand leaper, sand stalker, sandpillar, sarlacc swimmer, scrap-nest bird, shade whale, shale gorger, shatterjaw beetle, silt lamprey, skerrith, skorra, smog moth, smog pupa, starmaw, storm sando, tellurox, thornback colo, thrumbungus, thunderstep, thurra, truffle mole, ulgga, vekka, vent stalker, vosska, vozzik, vurra, war wyrm, yanker, yooka, zakkro, zhakka.

## Per creature
| creature | defName | entry before | images before → after | sources | notes |
|---|---|---|---|---|---|
| frilled gorg | `RSW_FrilledGorg` | — | 0 → 0 | — | no exact Wookieepedia title for: frilled gorg, Frilled Gorg |
| longtail gorg | `RSW_LongtailGorg` | — | 0 → 3 | Legends `Gorg/Legends` + canon `Gorg` (hand-built, shares gorg images) | no exact Wookieepedia title for: longtail gorg, Longtail Gorg |
| gorg | `RSW_Gorg` | — | 0 → 4 | canon `Gorg`; Legends `Gorg/Legends` | filled |
| aaroxis dendoria | `RSW_AaroxisDendoria` | — | 0 → 0 | — | no exact Wookieepedia title for: aaroxis dendoria, Aaroxis Dendoria |
| abyssal colo | `RSW_AbyssalColo` | — | 0 → 0 | — | no exact Wookieepedia title for: abyssal colo, Abyssal Colo |
| acid slug | `RSW_AcidSlug` | — | 0 → 0 | — | no exact Wookieepedia title for: acid slug, Acid Slug |
| Baseopsis | `RSW_Baseopsis` | — | 0 → 0 | — | no exact Wookieepedia title for: Baseopsis |
| basilisk | `RSW_Basilisk` | — | 0 → 0 | — | no exact Wookieepedia title for: basilisk, Basilisk |
| blarth | `RSW_Blarth` | — | 0 → 3 | canon `Blarth`; Legends `Blarth/Legends` | filled |
| blixus | `RSW_Blixus` | — | 0 → 2 | canon `Blixus`; Legends `Blixus/Legends` | filled |
| bloodletter petrel | `RSW_BloodletterPetrel` | — | 0 → 0 | — | no exact Wookieepedia title for: bloodletter petrel, Bloodletter Petrel |
| bloodrop larvae | `RSW_BloodropLarvae` | — | 0 → 0 | — | no exact Wookieepedia title for: bloodrop larvae, Bloodrop Larvae |
| drinker | `RSW_BloodropMoth` | — | 0 → 0 | — | no exact Wookieepedia title for: drinker, Bloodrop Moth |
| bloodrop pupa | `RSW_BloodropPupa` | — | 0 → 0 | — | no exact Wookieepedia title for: bloodrop pupa, Bloodrop Pupa |
| blurrg | `RSW_Blurrg` | blurrg | 0 → 4 | canon `Blurrg`; Legends `Blurrg/Legends` | filled |
| bogwing | `RSW_Bogwing` | — | 0 → 3 | canon `Bogwing`; Legends `Bogwing/Legends` | filled |
| bokka | `RSW_Bokka` | — | 0 → 0 | — | no exact Wookieepedia title for: bokka, Bokka |
| grabber | `RSW_BovineBeetle` | — | 0 → 0 | — | no exact Wookieepedia title for: grabber, Bovine Beetle |
| brain worm | `RSW_BrainWorm` | — | 0 → 2 | canon `Brain worm`; Legends `Brain worm/Legends` | filled |
| bunker bug | `RSW_BunkerBug` | — | 0 → 0 | — | no exact Wookieepedia title for: bunker bug, Bunker Bug |
| mahllik | `RSW_CaveLemming` | — | 0 → 0 | — | no exact Wookieepedia title for: mahllik, Cave Lemming |
| chikka | `RSW_Chikka` | — | 0 → 0 | — | no exact Wookieepedia title for: chikka, Chikka |
| colo claw fish | `RSW_ColoClawFish` | — | 0 → 4 | canon `Colo claw fish`; Legends `Colo claw fish/Legends` | filled |
| pustule hornet | `RSW_ColonyPustuleHornet` | — | 0 → 0 | — | no exact Wookieepedia title for: pustule hornet, Colony Pustule Hornet |
| pustule queen | `RSW_ColonyPustuleHornetQueen` | — | 0 → 0 | — | no exact Wookieepedia title for: pustule queen, Colony Pustule Hornet Queen |
| fang leaf | `RSW_Creature_Mantrap` | — | 0 → 0 | — | no exact Wookieepedia title for: fang leaf, Creature_Mantrap |
| crested dragon | `RSW_CrestedDragon` | — | 0 → 0 | — | no exact Wookieepedia title for: crested dragon, Crested Dragon |
| crimson opee | `RSW_CrimsonOpee` | — | 0 → 0 | — | no exact Wookieepedia title for: crimson opee, Crimson Opee |
| crystal crab | `RSW_CrystalCrab` | — | 0 → 0 | — | no exact Wookieepedia title for: crystal crab, Crystal Crab |
| crystal fairy mole | `RSW_CrystalFairyMole` | — | 0 → 0 | — | no exact Wookieepedia title for: crystal fairy mole, Crystal Fairy Mole |
| diggerpede | `RSW_Diggerpede` | — | 0 → 0 | — | no exact Wookieepedia title for: diggerpede, Diggerpede |
| Diplocaulus | `RSW_Diplocaulus` | — | 0 → 0 | — | no exact Wookieepedia title for: Diplocaulus |
| drazzik | `RSW_Drazzik` | — | 0 → 0 | — | no exact Wookieepedia title for: drazzik, Drazzik |
| durrok | `RSW_Durrok` | — | 0 → 0 | — | no exact Wookieepedia title for: durrok, Durrok |
| elder sando | `RSW_ElderSando` | — | 0 → 0 | — | no exact Wookieepedia title for: elder sando, Elder Sando |
| excretor | `RSW_Excretor` | — | 0 → 0 | — | no exact Wookieepedia title for: excretor, Excretor |
| faa scalefish | `RSW_Faa` | — | 0 → 3 | canon `Faa`; Legends `Faa/Legends` | filled |
| facet moth | `RSW_FacetMoth` | — | 0 → 0 | — | no exact Wookieepedia title for: facet moth, Facet Moth |
| falumpaset | `RSW_Falumpaset` | — | 0 → 2 | canon `Falumpaset`; Legends `Falumpaset/Legends` | filled |
| feral grazer | `RSW_FeralGrazer` | — | 0 → 0 | — | no exact Wookieepedia title for: feral grazer, Feral Grazer |
| feral nerf | `RSW_FeralNerf` | — | 0 → 0 | — | no exact Wookieepedia title for: feral nerf, Feral Nerf |
| puffmite | `RSW_FleeceSpider` | — | 0 → 0 | — | no exact Wookieepedia title for: puffmite, Fleece Spider |
| foundry beetle | `RSW_FoundryBeetle` | — | 0 → 0 | — | no exact Wookieepedia title for: foundry beetle, Foundry Beetle |
| skerrith | `RSW_FungalMantis` | — | 0 → 0 | — | no exact Wookieepedia title for: skerrith, Fungal Mantis |
| grellik | `RSW_FungalWeevil` | — | 0 → 0 | — | no exact Wookieepedia title for: grellik, Fungal Weevil |
| gastro toad | `RSW_GastroToad` | — | 0 → 0 | — | no exact Wookieepedia title for: gastro toad, Gastro Toad |
| gelagrub | `RSW_Gelagrub` | — | 0 → 3 | canon `Gelagrub`; Legends `Gelagrub/Legends` | filled |
| gembug | `RSW_Gembug` | — | 0 → 0 | — | no exact Wookieepedia title for: gembug, Gembug |
| glowbulb | `RSW_GlowSlug` | — | 0 → 0 | — | no exact Wookieepedia title for: glowbulb, Glow Slug |
| glowtail | `RSW_Glowtail` | — | 0 → 0 | — | no exact Wookieepedia title for: glowtail, Glowtail |
| gornt | `RSW_Gornt` | — | 0 → 3 | canon `Gornt`; Legends `Gornt/Legends` | filled |
| granite slug | `RSW_GraniteSlug` | — | 0 → 2 | canon `Granite slug`; Legends `Granite slug/Legends` | filled |
| great devourer | `RSW_GreatDevourer` | — | 0 → 1 | canon `Great Devourer` | filled |
| groundrunner | `RSW_Groundrunner` | — | 0 → 0 | — | no exact Wookieepedia title for: groundrunner, Groundrunner |
| gutkurr | `RSW_Gutkurr` | — | 0 → 4 | canon `Gutkurr`; Legends `Gutkurr/Legends` | filled |
| Holcorobeus | `RSW_Holcorobeus` | — | 0 → 0 | — | no exact Wookieepedia title for: Holcorobeus |
| hrumph | `RSW_Hrumph` | — | 0 → 4 | canon `Hrumph`; Legends `Hrumph/Legends` | filled |
| hssiss | `RSW_Hssiss` | — | 0 → 4 | canon `Hssiss` | filled |
| igitz | `RSW_Igitz` | — | 0 → 1 | canon `Igitz` | filled |
| ikee | `RSW_Ikee` | — | 0 → 0 | — | no exact Wookieepedia title for: ikee, Ikee |
| imperial toad | `RSW_ImperialToad` | — | 0 → 0 | — | no exact Wookieepedia title for: imperial toad, Imperial Toad |
| iridonian reek | `RSW_IridonianReek` | — | 0 → 4 | canon `Reek`; Legends `Reek/Legends` | filled (canon name is "reek") |
| jakobeast | `RSW_Jakobeast` | — | 0 → 2 | canon `Jakobeast`; Legends `Jakobeast/Legends` | filled |
| Jamel | `RSW_Jamel` | — | 0 → 3 | canon `Jamel` | filled |
| jellypot | `RSW_Jellypot` | — | 0 → 0 | — | no exact Wookieepedia title for: jellypot, Jellypot |
| jewel beetle | `RSW_JewelBeetle` | — | 0 → 0 | — | no exact Wookieepedia title for: jewel beetle, Jewel Beetle |
| jimvu | `RSW_Jimvu` | — | 0 → 1 | canon `Jimvu` | filled |
| karrask | `RSW_Karrask` | — | 0 → 0 | — | no exact Wookieepedia title for: karrask, Karrask |
| khorrak | `RSW_Khorrak` | — | 0 → 0 | — | no exact Wookieepedia title for: khorrak, Khorrak |
| k'lor'slug | `RSW_Klorslug` | — | 0 → 4 | canon `K'lor'slug`; Legends `K'lor'slug/Legends` | filled |
| korrum | `RSW_Korrum` | — | 0 → 0 | — | no exact Wookieepedia title for: korrum, Korrum |
| kowakian monkey-lizard | `RSW_KowakianMonkeyLizard` | — | 0 → 4 | canon `Kowakian monkey-lizard`; Legends `Kowakian monkey-lizard/Legends` | filled |
| krayt dragon | `RSW_KraytDragon` | — | 0 → 4 | canon `Krayt dragon`; Legends `Krayt dragon/Legends` | filled |
| krykna | `RSW_Krykna` | — | 0 → 4 | canon `Krykna` | filled |
| kudda | `RSW_Kudda` | — | 0 → 0 | — | no exact Wookieepedia title for: kudda, Kudda |
| Kwi | `RSW_Kwi` | — | 0 → 2 | canon `Kwi` | filled |
| kybuck | `RSW_Kybuck` | — | 0 → 4 | canon `Kybuck`; Legends `Kybuck/Legends` | filled |
| laa scalefish | `RSW_Laa` | — | 0 → 3 | canon `Laa`; Legends `Laa/Legends` | filled |
| lanternwhale | `RSW_Lanternwhale` | — | 0 → 0 | — | no exact Wookieepedia title for: lanternwhale, Lanternwhale |
| lava flea | `RSW_LavaFlea` | — | 0 → 3 | canon `Lava flea`; Legends `Lava flea/Legends` | filled |
| loth-cat | `RSW_Lothcat` | — | 0 → 4 | canon `Loth-cat`; Legends `Loth-cat/Legends` | filled |
| lylek | `RSW_Lylek` | — | 0 → 4 | canon `Lylek`; Legends `Lylek/Legends` | filled |
| maguana | `RSW_Maguana` | — | 0 → 0 | — | no exact Wookieepedia title for: maguana, Maguana |
| kroffa | `RSW_Maligoat` | — | 0 → 0 | — | no exact Wookieepedia title for: kroffa, Maligoat |
| marsh haunt | `RSW_MarshHaunt` | — | 0 → 1 | canon `Marsh haunt` | filled |
| massiff | `RSW_Massiff` | — | 0 → 4 | canon `Massiff`; Legends `Massiff/Legends` | filled |
| mature fleshbeast | `RSW_MatureFleshbeast` | — | 0 → 0 | — | no exact Wookieepedia title for: mature fleshbeast, Mature Fleshbeast |
| maxolotl | `RSW_Maxolotl` | — | 0 → 0 | — | no exact Wookieepedia title for: maxolotl, Maxolotl |
| mee scalefish | `RSW_Mee` | — | 0 → 4 | canon `Mee`; Legends `Mee/Legends` | filled |
| megakrill | `RSW_Megakrill` | — | 0 → 0 | — | no exact Wookieepedia title for: megakrill, Megakrill |
| megaphorid | `RSW_Megaphorid` | — | 0 → 0 | — | no exact Wookieepedia title for: megaphorid, Megaphorid |
| megapleura | `RSW_Megapleura` | — | 0 → 0 | — | no exact Wookieepedia title for: megapleura, Megapleura |
| moornak | `RSW_Moornak` | — | 0 → 0 | — | no exact Wookieepedia title for: moornak, Moornak |
| moss beetle | `RSW_MossBeetle` | — | 0 → 0 | — | no exact Wookieepedia title for: moss beetle, Moss Beetle |
| mott | `RSW_Mott` | — | 0 → 4 | canon `Mott`; Legends `Mott/Legends` | filled |
| mullgoth | `RSW_Mullgoth` | — | 0 → 0 | — | no exact Wookieepedia title for: mullgoth, Mullgoth |
| mutagenic norphea | `RSW_MutagenicNorphea` | — | 0 → 0 | — | no exact Wookieepedia title for: mutagenic norphea, Mutagenic Norphea |
| mutating tumorfish | `RSW_MutatingTumorfishAdult` | — | 0 → 0 | — | no exact Wookieepedia title for: mutating tumorfish, Mutating Tumorfish Adult |
| mutating tumorfish fry | `RSW_MutatingTumorfishFry` | — | 0 → 0 | — | no exact Wookieepedia title for: mutating tumorfish fry, Mutating Tumorfish Fry |
| mutating tumorfish spawn | `RSW_MutatingTumorfishSpawn` | — | 0 → 0 | — | no exact Wookieepedia title for: mutating tumorfish spawn, Mutating Tumorfish Spawn |
| mynock | `RSW_Mynock` | — | 0 → 4 | canon `Mynock`; Legends `Mynock/Legends` | filled |
| neebray | `RSW_Neebray` | — | 0 → 4 | canon `Neebray`; Legends `Neebray/Legends` | filled |
| nerf | `RSW_Nerf` | — | 0 → 4 | canon `Nerf`; Legends `Nerf/Legends` | filled |
| nizzek | `RSW_Nizzek` | — | 0 → 0 | — | no exact Wookieepedia title for: nizzek, Nizzek |
| ommok | `RSW_Ommok` | — | 0 → 0 | — | no exact Wookieepedia title for: ommok, Ommok |
| onnik | `RSW_Onnik` | — | 0 → 0 | — | no exact Wookieepedia title for: onnik, Onnik |
| opee sea killer | `RSW_OpeeSeaKiller` | — | 0 → 4 | canon `Opee sea killer`; Legends `Opee sea killer/Legends` | filled |
| ossik | `RSW_Ossik` | — | 0 → 0 | — | no exact Wookieepedia title for: ossik, Ossik |
| pikobis | `RSW_Pikobis` | — | 0 → 3 | canon `Pikobi`; Legends `Pikobi/Legends` | filled |
| Platyhystrix | `RSW_Platyhystrix` | — | 0 → 0 | — | no exact Wookieepedia title for: Platyhystrix |
| pod worm | `RSW_PodWorm` | — | 0 → 0 | — | no exact Wookieepedia title for: pod worm, Pod Worm |
| polluwog | `RSW_Polluwog` | — | 0 → 0 | — | no exact Wookieepedia title for: polluwog, Polluwog |
| Protosolpuga | `RSW_Protosolpuga` | — | 0 → 0 | — | no exact Wookieepedia title for: Protosolpuga |
| Protovermes | `RSW_Protovermes` | — | 0 → 0 | — | no exact Wookieepedia title for: Protovermes |
| Pufferpig | `RSW_Pufferpig` | — | 0 → 3 | canon `Puffer pig` | filled |
| pustule hornet | `RSW_PustuleHornet` | — | 0 → 0 | — | no exact Wookieepedia title for: pustule hornet, Pustule Hornet |
| pustule queen | `RSW_PustuleHornetQueen` | — | 0 → 0 | — | no exact Wookieepedia title for: pustule queen, Pustule Hornet Queen |
| qormot | `RSW_Qormot` | — | 0 → 1 | canon `Qormot` | filled |
| reefback | `RSW_Reefback` | — | 0 → 0 | — | no exact Wookieepedia title for: reefback, Reefback |
| royal rhino beetle | `RSW_RoyalRhino` | — | 0 → 0 | — | no exact Wookieepedia title for: royal rhino beetle, Royal Rhino |
| runyip | `RSW_Runyip` | — | 0 → 4 | canon `Runyip`; Legends `Runyip/Legends` | filled |
| rust nipper | `RSW_RustNipper` | — | 0 → 0 | — | no exact Wookieepedia title for: rust nipper, Rust Nipper |
| sacapillar | `RSW_Sacapillar` | — | 0 → 0 | — | no exact Wookieepedia title for: sacapillar, Sacapillar |
| sand leaper | `RSW_SandLeaper` | — | 0 → 0 | — | no exact Wookieepedia title for: sand leaper, Sand Leaper |
| vekka | `RSW_SandLion` | — | 0 → 0 | — | no exact Wookieepedia title for: vekka, Sand Lion |
| sandpillar | `RSW_SandPillar` | — | 0 → 0 | — | no exact Wookieepedia title for: sandpillar, Sand Pillar |
| sand stalker | `RSW_SandStalker` | — | 0 → 0 | — | no exact Wookieepedia title for: sand stalker, Sand Stalker |
| sando aqua monster | `RSW_SandoAquaMonster` | — | 0 → 4 | canon `Sando aqua monster`; Legends `Sando aqua monster/Legends` | filled |
| sarlacc swimmer | `RSW_SarlaccSwimmer` | — | 0 → 0 | — | no exact Wookieepedia title for: sarlacc swimmer, Sarlacc Swimmer |
| Scavrats | `RSW_Scavrat` | — | 0 → 0 | — | no exact Wookieepedia title for: Scavrats, Scavrat |
| scrap-nest bird | `RSW_ScrapNestBird` | — | 0 → 0 | — | no exact Wookieepedia title for: scrap-nest bird, Scrap Nest Bird |
| screecher | `RSW_Screecher` | — | 0 → 0 | — | NAME COLLISION: Wookieepedia `Screecher` is a Kirtania rain-forest animal (one line, no image); ours is a pollution-mutated corvid. No entry created. |
| scurrier | `RSW_Scurrier` | — | 0 → 4 | canon `Scurrier`; Legends `Scurrier/Legends` | filled |
| Segnosaurus | `RSW_Segnosaurus` | — | 0 → 0 | — | no exact Wookieepedia title for: Segnosaurus |
| shaaks | `RSW_Shaak` | — | 0 → 4 | canon `Shaak`; Legends `Shaak/Legends` | filled |
| shade whale | `RSW_ShadeWhale` | — | 0 → 0 | — | no exact Wookieepedia title for: shade whale, Shade Whale |
| shale gorger | `RSW_ShaleGorger` | — | 0 → 0 | — | no exact Wookieepedia title for: shale gorger, Shale Gorger |
| shatterjaw beetle | `RSW_ShatterjawBeetle` | — | 0 → 0 | — | no exact Wookieepedia title for: shatterjaw beetle, Shatterjaw Beetle |
| shiro-trap | `RSW_ShiroTrap` | — | 0 → 2 | canon `Shiro-trap` | filled |
| thunderstep | `RSW_ShrublandGiant` | — | 0 → 0 | — | no exact Wookieepedia title for: thunderstep, Shrubland Giant |
| shyrack | `RSW_Shyrack` | — | 0 → 2 | Legends `Shyrack/Legends` | filled |
| silt lamprey | `RSW_SiltLamprey` | — | 0 → 0 | — | no exact Wookieepedia title for: silt lamprey, Silt Lamprey |
| skalders | `RSW_Skalder` | — | 0 → 2 | canon `Skalder`; Legends `Skalder/Legends` | filled |
| sketto | `RSW_Sketto` | — | 0 → 3 | canon `Sketto`; Legends `Sketto/Legends` | filled |
| skorra | `RSW_Skorra` | — | 0 → 0 | — | no exact Wookieepedia title for: skorra, Skorra |
| smog moth | `RSW_SmogMoth` | — | 0 → 0 | — | no exact Wookieepedia title for: smog moth, Smog Moth |
| smog pupa | `RSW_SmogPupa` | — | 0 → 0 | — | no exact Wookieepedia title for: smog pupa, Smog Pupa |
| starmaw | `RSW_Starmaw` | — | 0 → 0 | — | no exact Wookieepedia title for: starmaw, Starmaw |
| storm sando | `RSW_StormSando` | — | 0 → 0 | — | no exact Wookieepedia title for: storm sando, Storm Sando |
| strill | `RSW_Strill` | — | 0 → 2 | canon `Strill`; Legends `Strill/Legends` | filled |
| tee muss | `RSW_TeeMuss` | — | 0 → 1 | canon `Tee-muss`; Legends `Tee-muss/Legends` | filled |
| tellurox | `RSW_TelluroxRace` | — | 0 → 0 | — | no exact Wookieepedia title for: tellurox, Tellurox |
| Termitotron | `RSW_Termitotron` | — | 0 → 0 | — | no exact Wookieepedia title for: Termitotron |
| thornback colo | `RSW_ThornbackColo` | — | 0 → 0 | — | no exact Wookieepedia title for: thornback colo, Thornback Colo |
| thrumbungus | `RSW_Thrumbungus` | — | 0 → 0 | — | no exact Wookieepedia title for: thrumbungus, Thrumbungus |
| thurra | `RSW_Thurra` | — | 0 → 0 | — | no exact Wookieepedia title for: thurra, Thurra |
| truffle mole | `RSW_TruffleMole` | — | 0 → 0 | — | no exact Wookieepedia title for: truffle mole, Truffle Mole |
| yanker | `RSW_TunnelSnake` | — | 0 → 0 | — | no exact Wookieepedia title for: yanker, Tunnel Snake |
| ulgga | `RSW_Ulgga` | — | 0 → 0 | — | no exact Wookieepedia title for: ulgga, Ulgga |
| urusai | `RSW_Urusai` | — | 0 → 4 | canon `Urusai`; Legends `Urusai/Legends` | filled |
| uvak | `RSW_Uvak` | — | 0 → 4 | canon `Uvak` | filled |
| varactyl | `RSW_Varactyl` | — | 0 → 4 | canon `Varactyl`; Legends `Varactyl/Legends` | filled |
| vent stalker | `RSW_VentStalker` | — | 0 → 0 | — | no exact Wookieepedia title for: vent stalker, Vent Stalker |
| voorpak | `RSW_Voorpak` | — | 0 → 4 | canon `Voorpak`; Legends `Voorpak/Legends` | filled |
| vosska | `RSW_Vosska` | — | 0 → 0 | — | no exact Wookieepedia title for: vosska, Vosska |
| vozzik | `RSW_Vozzik` | — | 0 → 0 | — | no exact Wookieepedia title for: vozzik, Vozzik |
| vurra | `RSW_Vurra` | — | 0 → 0 | — | no exact Wookieepedia title for: vurra, Vurra |
| war wyrm | `RSW_WarWyrm` | — | 0 → 0 | — | no exact Wookieepedia title for: war wyrm, War Wyrm |
| womp rat | `RSW_WompRat` | — | 0 → 4 | canon `Womp rat`; Legends `Womp rat/Legends` | filled |
| woolamander | `RSW_Woolamander` | — | 0 → 4 | canon `Woolamander`; Legends `Woolamander/Legends` | filled |
| worrt | `RSW_Worrt` | — | 0 → 4 | canon `Worrt`; Legends `Worrt/Legends` | filled |
| wraid | `RSW_Wraid` | — | 0 → 2 | canon `Wraid` | filled |
| alpha wraid | `RSW_WraidAlpha` | — | 0 → 0 | — | no exact Wookieepedia title for: alpha wraid, Wraid Alpha |
| pale yobshrimp | `RSW_Yobshrimp` | — | 0 → 2 | canon `Yobshrimp`; Legends `Yobshrimp/Legends` | filled |
| yobshrimp | `RSW_YobshrimpLand` | — | 0 → 2 | canon `Yobshrimp`; Legends `Yobshrimp/Legends` | filled |
| yooka | `RSW_Yooka` | — | 0 → 0 | — | no exact Wookieepedia title for: yooka, Yooka |
| zakkro | `RSW_Zakkro` | — | 0 → 0 | — | no exact Wookieepedia title for: zakkro, Zakkro |
| zhakka | `RSW_Zhakka` | — | 0 → 0 | — | no exact Wookieepedia title for: zhakka, Zhakka |
| ysalamir | `SWPotF_RaceDef_ysalamir` | — | 0 → 4 | canon `Ysalamiri`; Legends `Ysalamiri/Legends` | filled (canon name is "ysalamiri"; label search missed it) |
