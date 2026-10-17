# Dragonsnake

**defName**: `RSW_Dragonsnake` (vendored, our own — `src/RimStarWars/SWBestiary`,
custom `Dragonsnake` BodyDef built on vanilla Core per
`src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml`)

## Sourced text (Wookieepedia)
Large, predatory reptiles that dwell in the murky waters of swamp-covered
planets, including Dagobah and Nal Hutta (Wookieepedia's citations tie the species
to those two; no Dxun source). Serpentlike
bodies with sharp fangs, capable of excreting a lethal toxin; voracious but
unable to digest metal (per *The Empire Strikes Back*, R2-D2 was spat back
out). Length 7 meters, mass up to 200 kg (*Star Wars Bestiary Vol. 1* — a reference-book baseline; the
film animal below is far longer). Considered untameable (*Visual Encyclopedia*), yet the Hutt Twins keep one. Hunts by hiding under muddy water
and among gnarltree roots, ambushing prey then dragging it back under. First
identified as "Dragonsnake" in the Clone Wars episode guide for "Hunt for
Ziro" (Obi-Wan Kenobi fights one on Nal Hutta). Reappeared on Dagobah in *The
Empire Strikes Back* (the R2-D2 encounter) and, much more recently, in *The
Mandalorian and Grogu* — a dragonsnake owned by the Hutt Twins on Nal Hutta
fights Din Djarin, injuring him with venom before being fed the Twins
themselves. Individual "Bright-Eyes" on Dagobah (female, mottled blue-gray skin, yellow eyes) displayed a degree of
sentience (*From a Certain Point of View: Return of the Jedi*, "The Light That Falls";
https://starwars.fandom.com/wiki/Bright-Eyes), so tan/green/olive is not the whole palette.
**Legends** (https://starwars.fandom.com/wiki/Dragonsnake/Legends): length 2-6 m, brown/green/grey skin,
red/black/scarlet/dark-brown eyes, semi-sentient, omnivorous.

## Visual brief
**Owner ruling 2026-10-17 (canon blog-image review sheet, verbatim):** "Split into two official versions. The two pale versions let's call Dragonsnake_albino. The Jedi Fallen Order four variants lets accept as the canon Dragonsnake. Comission both in our Star Wars fauna mod. Remove the huntforziro and cisualencyclopedia versions as crude and cartoonish. Regenerate the "must have" descriptions from these two new creature specs."
The dragonsnake is now TWO official creatures. This entry is the canon **Dragonsnake**, defined by the
*Jedi: Fallen Order* concept sheet; the pale limbless serpent of *The Mandalorian and Grogu* is the separate
**Dragonsnake_albino** (`../dragonsnake_albino/description.md`). The animated *Clone Wars* frame and the
*Galactic Atlas* illustration were deleted as "crude and cartoonish".

**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."**

- `wookieepedia_concept_jfo.jpg` — *Jedi: Fallen Order* (Respawn) painted photoreal concept sheet, four variants with a stormtrooper for scale — THE canon Dragonsnake. A long, low, crocodile-like QUADRUPED with short splayed clawed limbs, a narrow toothy gharial-crocodile snout with fangs projecting outside the jaw, a dorsal row of short spines, a very long tapering eel-like tail (some variants with a fin or spined fan at the tip), dark olive-to-slate scaly hide with moss/algae patches, a pale ridged ventral belly, and — in the third variant — scattered bioluminescent yellow-green spots plus a glowing throat sac. Length several times a human. The four variants differ in tail tip and spotting; all four are canon.
- `donor_current_sprite.png` (our own sprite): tan/khaki quadruped with small clawed limbs, dark spots, gator-like head — body plan agrees with the concept sheet, colour does not.

## Must show
*Regenerated 2026-10-17 from the owner's split ruling: the Jedi: Fallen Order four variants are the spec.*
- [ ] BODY PLAN: a long, low crocodilian quadruped with short splayed clawed limbs and a very long tapering eel-like tail, the tail a large share of the total length; head held low and forward
- [ ] Narrow toothy crocodile/gharial snout with fangs projecting outside the jaw
- [ ] COLOUR LAYOUT: dark olive-to-slate scaly hide over the back, flanks and tail; a pale ridged belly underneath, the lightest area of the body (glowing yellow-green spots are allowed — one of the four canon variants has them)
- [ ] Dorsal row of short spines along the back
- [ ] Realistic rendering: wet scaly reptile hide and natural lighting, no outlines, no cartoon shading (owner ruling 2026-10-08)
- [ ] NEGATIVE: not pale or limbless (that is Dragonsnake_albino); not a tan/khaki gator (the donor's colour)

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Dragonsnake (Wookieepedia, wikitext pulled
  2026-09-13 via `action=parse&prop=wikitext`)
- https://static.wikia.nocookie.net/starwars/images/d/df/DragonsnakeConcept-JFO.jpg/revision/latest?cb=20230603191742 (*Jedi: Fallen Order* concept sheet)
- `src/RimStarWars/SWBestiary/Textures/swanimals/Dragonsnake/Dragonsnake_Swimming_south.png` (our own donor/current sprite)

## Candidate images
- `donor_current_sprite.png` — our own current in-game sprite (south-swimming pose), tan/khaki quadruped, small clawed limbs, dark spots, gator-like head.
- `wookieepedia_concept_jfo.jpg` — REALISTIC painted concept art, *Jedi: Fallen Order*, four quadruped variants — THE canon Dragonsnake (owner 2026-10-17); file `DragonsnakeConcept-JFO.jpg` — https://static.wikia.nocookie.net/starwars/images/d/df/DragonsnakeConcept-JFO.jpg/revision/latest?cb=20230603191742

## ruling
**RULED** (owner, 2026-09-14, review sheet): `wookieepedia_huntforziro.jpg`

> "#2 for coloration and glowing-seeming spots. But much less cartoonish, more like seriousness of #3."
(The 2026-09-14 pick named `wookieepedia_huntforziro.jpg`; that image was deleted by the 2026-10-17 ruling below.)

**RULED** (owner, 2026-10-17, canon blog-image review sheet):
> "Split into two official versions. The two pale versions let's call Dragonsnake_albino. The Jedi Fallen Order four variants lets accept as the canon Dragonsnake. Comission both in our Star Wars fauna mod. Remove the huntforziro and cisualencyclopedia versions as crude and cartoonish. Regenerate the "must have" descriptions from these two new creature specs."

Done: pale images moved to `dragonsnake_albino/`; `wookieepedia_huntforziro.jpg` and `wookieepedia_visualencyclopedia.jpg` deleted; both entries' Must show regenerated; commission filed as rimflow item `DRAGONSNAKE_PAIR_BUILD_ONE_PALE_ONE_PROPER`.
