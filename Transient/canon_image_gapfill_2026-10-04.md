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
| iridonian reek | `RSW_IridonianReek` | — | 0 → 0 | — | no exact Wookieepedia title for: iridonian reek, Iridonian Reek |
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
