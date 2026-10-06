# Tauntaun

**defName**: `Tauntaun` (donor: Star Wars Animal Collection (Continued), packageId `mlie.starwarsanimalcollection`; the donor's own def, no owned port yet, no `RSW_` twin). Cast in the Nightside Ice via `src/RimUtinni/UtinniPatches/Patches/WildAnimals_NightsideIce.xml` at 0.03 (visitor-dying, owner card 2026-10-01). Donor sprite: `design/Jawa/fauna/sprites/Tauntaun.png`.

## Sourced text (Wookieepedia, pulled via API)
Tauntauns were a species of semi-sentient **reptomammals** native to the snowy plains of Hoth.
Infobox: height 1.3 to 2 m at the shoulder (Star Wars Encyclopedia) and 2.7 m total (Galaxy of
Creatures); hair colour brown (Inquisitors 1) or **white** (Encyclopedia); eye colour dark;
habitat snowy plains; diet lichen, small ice plants, Hoth hogs, ice scrabblers; 15 subspecies.
Mass, lifespan and skin colour are unsourced and deliberately absent.

Biology: thick skin; **sure-footed and furry**, with **scaly skin beneath heavy layers of fur**;
layers of fatty blubber; secrete thick pungent oils; **long claws** for climbing ice and
scraping lichen; **tails help keep balance while running**; **horns used for combat if
necessary**. Live birth (young are "taunlets"). They survive Hoth's daytime cold but cannot
handle the night, which falls below -60 C. Wild herds of about 25, led by a female matriarch;
they burrow into snow for warmth and shelter in glacial caves heated from below. Omnivores.
Swift, docile, up to 90 kph; migratory; prey of the wampa; domesticated as Rebel mounts.

## Visual brief
Three images viewed. `wookieepedia_tauntaun_swe.png` (Star Wars Encyclopedia render, 397x675,
front view) and `wookieepedia_tauntaun_riders_boxart.png` (Legion box art, 600x940, rider, 3/4
front) agree on the animal; `donor_current_sprite.png` (128x128) does NOT.
- **Bipedal, upright, digitigrade-to-plantigrade**: a long vertical **neck** carrying the head
  high, a **narrow chest and bulging pale belly**, two **short folded forearms with clawed
  hands held against the chest**, two **long powerful legs ending in big broad three-toed
  feet with long pale claws**. Reads as a tall, slim, kangaroo/raptor-like biped, NOT a
  quadruped and NOT a goat.
- **Head**: long narrow face with a **pig-like flat snout and two big nostrils**, small
  downturned mouth, **dark deep-set eyes**, **two large pointed ears** and **two thick ridged
  horns that curl around and forward beside the face like a ram's** (horns brown-grey,
  ridged).
- **Coat**: dirty **off-white to pale grey** (box art: darker slate blue-grey with a grey-white
  belly and a small **goatee-like tuft under the chin**). Shaggy fur on head, neck and
  chest; leaner on the shins; bare scaly grey skin on feet.
- **Tail**: a **long thin tail tapering to a point**, held low and slightly curved, used for
  balance (render: bare grey, narrow; box art: thicker, curving up).
- Third image, `wookieepedia_wampa_eats_tauntaun_tesb.png` (film still, 1600x800), is a
  **skeleton of a tauntaun in the wampa's cave**: weak evidence for body plan only (long neck,
  curved ribcage, long skull with horn cores). Use it for nothing about colour.
- **Donor sprite contradicts canon**: it is a tiny, front-facing, stubby white-grey creature
  with a small face under a tall pale spiralled cone/horn rising straight up. No ram horns
  curled at the sides, no long neck, no biped legs and feet, no tail. Treat the donor as a
  NEGATIVE reference for shape. Follow the canon renders.
- Prose vs images: prose says brown or white fur; the renders show off-white (Encyclopedia) and
  slate grey (box art). Both are canon-attested; white-to-pale-grey is the safe default for the
  Nightside Ice.

## Must show
- [ ] Upright bipedal posture on two long legs, with a long vertical neck, narrow chest and pale rounded belly
- [ ] Two short folded forearms with clawed hands held against the chest
- [ ] Head with flat pig-like snout and big nostrils, small dark deep-set eyes, two pointed ears
- [ ] Two thick ridged horns curling back, around and forward beside the face like a ram's
- [ ] Shaggy off-white to pale grey fur on head, neck and body; scaly grey skin on the feet
- [ ] Big broad splayed three-toed feet with long pale claws
- [ ] A long thin pointed tail held low for balance
- [ ] Not a goat, deer, horse or camel: no hooves, no quadruped stance, no single central horn

## Engine limits
none known. (Rider and saddle in the box art are not part of the animal. Smell and burrowing are not drawable.) Biped body plan is a shape question for the sprite only; the race def's body type is not asked about here.

## Source URLs
- https://starwars.fandom.com/wiki/Tauntaun (text via `api.php?action=parse&page=Tauntaun&prop=wikitext`, 22,164 chars, fully read)
- https://static.wikia.nocookie.net/starwars/images/9/9c/Tauntaun-SWE.png (saved as `wookieepedia_tauntaun_swe.png`)
- https://static.wikia.nocookie.net/starwars/images/e/ec/SWL40_Tauntaun_Riders_Unit_Epxansion_box_art.png (saved as `wookieepedia_tauntaun_riders_boxart.png`)
- https://static.wikia.nocookie.net/starwars/images/9/9a/WampaChompTauntaun-TESB.png (saved as `wookieepedia_wampa_eats_tauntaun_tesb.png`)

## Candidate images
- `wookieepedia_tauntaun_swe.png` : Encyclopedia render, front view, white. Best anatomy reference.
- `wookieepedia_tauntaun_riders_boxart.png` : painted 3/4 view with rider, slate-grey coat, chin tuft, curled tail.
- `wookieepedia_wampa_eats_tauntaun_tesb.png` : film still, tauntaun skeleton only (weak).
- `donor_current_sprite.png` : MLIE donor, 128x128. Contradicts canon shape (see Visual brief).

## ruling
(empty — owner has not reviewed this entry)
