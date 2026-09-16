# Dragonsnake

**defName**: `RSW_Dragonsnake` (vendored, our own — `src/RimStarWars/SWBestiary`,
custom `Dragonsnake` BodyDef built on vanilla Core per
`src/RimStarWars/SWBestiary/Defs/Bodies/RSW_MlieWaveC_Bodies.xml`)

## Sourced text (Wookieepedia)
Large, predatory reptiles that dwell in the murky waters of swamp-covered
planets, including Dagobah and Nal Hutta (also documented on Dxun-adjacent
swamp settings in some secondary sources, though Wookieepedia's own citations
tie the species specifically to Dagobah and Nal Hutta, not Dxun). Serpentlike
bodies with sharp fangs, capable of excreting a lethal toxin; voracious but
unable to digest metal (per *The Empire Strikes Back*, R2-D2 was spat back
out). Length ~7 meters, mass up to 200 kg. Hunts by hiding under muddy water
and among gnarltree roots, ambushing prey then dragging it back under. First
identified as "Dragonsnake" in the Clone Wars episode guide for "Hunt for
Ziro" (Obi-Wan Kenobi fights one on Nal Hutta). Reappeared on Dagobah in *The
Empire Strikes Back* (the R2-D2 encounter) and, much more recently, in *The
Mandalorian and Grogu* — a dragonsnake owned by the Hutt Twins on Nal Hutta
fights Din Djarin, injuring him with venom before being fed the Twins
themselves. Individual "Bright-Eyes" on Dagobah displayed a degree of
sentience (*From a Certain Point of View: Return of the Jedi*).

## Visual brief
**The three canon sources disagree sharply on body plan, and none of them
match our current donor/vendored sprite closely.**

- `wookieepedia_huntforziro.jpg` (Clone Wars, "Hunt for Ziro", Nal Hutta): a
  thick, segmented, armor-plated body with NO visible limbs, a bony/skeletal
  jawless-looking skull with prominent fangs, and rows of glowing
  yellow-green bioluminescent spots down the body. Olive/dark-khaki color.
  Reads as an eel/worm-like ambush predator, not a "snake with legs."
- `wookieepedia_visualencyclopedia.jpg` (Star Wars Adventure Journal-style
  illustration, labeled "DRAGONSNAKE" on a map): a lean, green, spotted
  quadruped with small clawed forelimbs and hindlimbs, a long tapering tail,
  and an elongated toothy crocodilian head with a pronounced brow ridge —
  this is the source closest in body plan to a "dragon" and closest to our
  donor sprite (both have four small limbs), but the color is bright green
  with pale spots, not our sprite's tan/khaki.
- `wookieepedia_mandalorianandgrogu.jpg` (*The Mandalorian and Grogu*, Nal
  Hutta pit): a massive, pale bone-white/gray, LIMBLESS eel-like serpent —
  multiple huge coils breach the water, with a skull-like elongated head and
  a mouth full of long fangs dripping venom. No legs are visible anywhere on
  the body. This is the newest, most "current canon" screen appearance and it
  contradicts the quadruped read from the encyclopedia illustration.
- `donor_current_sprite.png` (our own in-game sprite,
  `Dragonsnake_Swimming_south.png`): a lean tan/khaki quadruped with small
  clawed limbs, dark spotted markings, and an alligator-like toothy skull
  head — body-plan-wise it agrees with the visual-encyclopedia illustration
  (four legs) but its muted tan coloring matches none of the three canon
  images, which run olive-with-glowing-spots, bright green, or bone-pale.

**Net read**: canon dragonsnakes are consistently serpentine/reptilian with a
elongated toothy skull, but disagree on whether they have visible legs at all
(illustration: yes: small quadruped legs / both screen appearances: no
visible limbs, pure coiling serpent) and on color (olive-glowing, bright
green, bone-pale, vs. our tan). This is a real candidate-image disagreement
for the owner to rule on — likely resolution is either "keep our quadruped
body plan but recolor" or "cut the legs to match the two screen
appearances."

## Must show
Honest framing: the three canon images disagree sharply on body plan (limbless eel-like
serpent in two, a small-legged quadruped in the third) and on color — only what all three
agree on is listed as testable.
- [ ] Elongated, toothy, skull-like/crocodilian head with prominent, visible fangs
- [ ] Long serpentine/reptilian body plan
- [ ] Shown as an aquatic ambush predator, partially submerged in murky swamp water

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Dragonsnake (Wookieepedia, wikitext pulled
  2026-09-13 via `action=parse&prop=wikitext`)
- https://static.wikia.nocookie.net/starwars/images/6/67/Dragonsnake-HFZ.jpg (Hunt for Ziro screencap)
- https://static.wikia.nocookie.net/starwars/images/c/cc/Dragonsnake-SWGA.jpg (infobox illustration, labeled Star Wars Adventure Journal-derived map art)
- https://static.wikia.nocookie.net/starwars/images/5/52/DinDjarinDragonsnakeFaceoff-TMaG.png (The Mandalorian and Grogu)
- `src/RimStarWars/SWBestiary/Textures/swanimals/Dragonsnake/Dragonsnake_Swimming_south.png` (our own donor/current sprite)

## Candidate images
- `donor_current_sprite.png` — our own current in-game sprite (south-swimming
  pose), tan/khaki quadruped, small clawed limbs, dark spots, gator-like head.
- `wookieepedia_huntforziro.jpg` — Clone Wars "Hunt for Ziro" screencap:
  limbless, segmented, olive body with glowing yellow-green spots, bony
  skull-like head, no legs visible.
- `wookieepedia_visualencyclopedia.jpg` — illustrated map/bestiary art
  labeled "DRAGONSNAKE": bright green spotted quadruped with small clawed
  legs, long tail, crocodilian head.
- `wookieepedia_mandalorianandgrogu.jpg` — *The Mandalorian and Grogu*
  screencap: massive pale bone-white limbless serpent, multiple coils,
  skull-like head with venom-dripping fangs.

## ruling
**RULED** (owner, 2026-09-14, review sheet): `wookieepedia_huntforziro.jpg`

> "#2 for coloration and glowing-seeming spots. But much less cartoonish, more like seriousness of #3."
