# Acklay

**defName**: `RSW_Acklay` (SWBestiary, texture folder `Acklay`)

## Sourced text (Wookieepedia)
Acklays were non-sentient, amphibious, reptilian crustaceans native to the
planet Vendaxa. Infobox facts: **skin color Green** (cited to *Attack of the
Clones*), height 3.05 meters, class "amphibious reptilian crustacean."
Distinctions: grappling hands, stretchy stomachs, razor-sharp teeth,
protective bony nodules, hardened skin-covered claws, **six legs**, **three
eyes**. Habitat: grassland and water on Vendaxa; diet carnivore.

"The acklay was a non-sentient mix of crustacean and reptile with amphibious
traits... The gigantic creature was protected by a hard, shell-like carapace
of bony nodules. They walked on six hardened, skin-covered claws, and had
grappling hands. Its mouth was filled with razor-sharp teeth, and used an
organ beneath its chin to sense the body electricity given off by its prey,
which it would then spear with its pointed legs. The species had stretchy
stomachs and three eyes."

Acklays were used as execution beasts by the Geonosians in the Petranaki
Arena on Geonosis, most famously the three-acklay scene in *Attack of the
Clones* (Obi-Wan Kenobi, Anakin Skywalker, Padmé Amidala). Surprisingly
agile despite their size; strong enough to bite through a polearm and smash
a stone pillar.

## Visual brief
Both candidate images and the infobox agree tightly: **the acklay is GREEN**
(mottled olive/sage-green to yellow-green, sometimes with a paler
cream/yellow underside), a spider-crab body plan with a long upward-curving
neck ending in a crested, elongated toothy head, and **six** thin, sharp,
multi-jointed legs radiating from a small central body — two of the six
function as raised grappling "arms" with hooked claws, the other four are
walking/spearing legs. No visible shell/carapace plates are obvious in
either image (the "bony nodules" read more as skin texture/ridges than
armor plating). Both images are consistent on green coloration; no
disagreement between the two canon images.

**Disagreement with our own art**: the current SWBestiary donor sprite
(`donor_current_sprite.png`) renders the Acklay in **blue-teal**, not green.
Body plan (long curved neck, crested head, six spindly legs) matches canon
well — the color does not. This is the same failure mode as the Wyyyschokk
case: our render invented a color the source material does not support.
Every source checked (infobox skincolor field, both Wookieepedia images)
says green; nothing supports blue-teal. Flagging for owner ruling — canon
color should very likely be corrected to green on any regen.

## Source URLs
- https://starwars.fandom.com/wiki/Acklay (Wookieepedia, text pulled via
  MediaWiki API `action=parse` 2026-09-13)
- https://static.wikia.nocookie.net/starwars/images/a/a8/Acklay-JTS.png (File:Acklay-JTS.png, infobox image)
- https://static.wikia.nocookie.net/starwars/images/e/e2/Acklay.png (File:Acklay.png, "profile view of an acklay")

## Candidate images
- `acklay_wookieepedia_1.jpg` — current Wookieepedia infobox render
  (File:Acklay-JTS.png): green-grey mottled body, open toothy mouth, long
  curved neck, six thin clawed legs, one pair raised as grasping arms.
  Strongest/most recent canon depiction.
- `acklay_wookieepedia_2.jpg` — older profile illustration (File:Acklay.png,
  cited as "A profile view of an acklay"): green body with tan/cream
  underside and legs, same long-necked six-legged crested-head silhouette,
  small tail nub. Confirms the green coloring and body plan from a second,
  independent illustration.
- `donor_current_sprite.png` — our own SWBestiary donor sprite (`swanimals/
  Acklay/Acklay_east.png`): matches the body plan (curved neck, crested
  head, six spindly legs) but renders in blue-teal instead of canon green —
  see Visual brief disagreement above.

## ruling
**RULED** (owner, 2026-09-14, review sheet): `acklay_wookieepedia_2.jpg`

> "Yes, let's regenerate to something more like #2. But the donor current is really quite good. It would just be nice to get more of that surface texture on it."
