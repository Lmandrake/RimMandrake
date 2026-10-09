# Beldon

**defName**: `RSW_Beldon` (SWBestiary, texture folder `Beldon`)

## Sourced text (Wookieepedia)
Beldons are a large, non-sentient species native to the **gas giant
Bespin**, living in herds in its lower atmosphere — **not** an aquatic
plant-creature of Naboo (that assumption does not match canon; correcting
it here). Infobox distinctions: "**Orange** gas bladders, fleshy fins, long
tendrils." Infobox length / body-text *width*: **0.8–10 kilometers** (the page itself
uses both words for the same *Ultimate Star Wars* figure; extreme size range). Diet: atmospheric plankton and chemicals,
gathered with long body tendrils and metabolized into tibanna gas — the resource basis of Bespin's economy
(referenced directly in *Star Wars Battlefront II*: "If they make the
Tibanna Gas the Empire needs, the Beldons are mission critical.").

"Beldons measured anywhere from 0.8 to 10 kilometers in width, and they had
bodies filled with orange gas bladders that allowed them to float. These
creatures used their fleshy fins for propulsion. They were preyed upon by
velkers, and their remains often served as food for crab gliders."

Legends origin (*Galaxy Guide 2: Yavin and Bespin*, 1989), folded into
canon by *Ultimate Star Wars* (2015).

## Visual brief
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."** The flat purple Galactic Atlas drawing (`beldon_wookieepedia_1.jpg`) was deleted, as this entry's own ruling already ordered. The canon reference is the painted Wildlife of Star Wars field-guide plate `wookieepedia_woswfg.webp` (no live-action beldon exists); render it far more realistically than either that plate or the donor sprite.

What `wookieepedia_woswfg.webp` shows:
- **Body:** a huge cluster of several rounded, swollen, translucent-looking **orange-to-peach gas bladders**, each with paler highlights, fine dark speckling and a puckered, frilled crown — lumpy and organic, like a bunch of inflated sacs, not one smooth balloon.
- **Fins:** broad, thin, ragged orange membranous fins/flaps projecting sideways from the bladder cluster.
- **Underside:** a dense reddish-brown knobbly mass under the bladders, from which hangs a curtain of long, thin, dark tendrils.
- **Herd:** smaller individuals drift below the large one at a distance — same shape at reduced size.

The colour question is settled: **orange** (infobox text, the woswfg plate and the donor sprite all agree); the purple was a one-off stylised drawing. The canon 0.8–10 km size is unrenderable at sprite scale (see Engine limits).

## Must show
- [ ] Cluster of several rounded, swollen orange-to-peach gas bladders with paler highlights and fine dark speckling, not one smooth balloon
- [ ] Broad, thin, ragged orange membranous fins projecting from the sides
- [ ] Reddish-brown knobbly mass under the bladders with a curtain of long thin dark tendrils hanging below
- [ ] Orange colouring — never purple/lavender
- [ ] Realistic rendering: natural translucent, moist membrane texture and soft atmospheric lighting, no outlines, no cartoon shading

## Engine limits
The canon 0.8–10 km size range cannot be depicted at gameplay creature-sprite scale; the
entry treats this as an inherent, unrenderable fact rather than a "wrong size" defect to fix.

## Source URLs
- https://starwars.fandom.com/wiki/Beldon (Wookieepedia, text pulled via
  MediaWiki API `action=parse` 2026-09-13)
- https://static.wikia.nocookie.net/starwars/images/b/bc/Beldons-woswfg.jpg (File:Beldons-woswfg.jpg)

## Candidate images
- `wookieepedia_woswfg.webp` — painted plate from The Wildlife of Star Wars: A Field Guide (realistic painted illustration; the owner's chosen canon image 2026-10-08); file `Beldons-woswfg.jpg` — https://static.wikia.nocookie.net/starwars/images/b/bc/Beldons-woswfg.jpg/revision/latest?cb=20070123191252
- `donor_current_sprite.png` — our own SWBestiary donor sprite (`swanimals/Beldon/Beldon_east.png`): orange lumpy balloon body with dark tendrils, low quality; ruled 2026-09-14 as a good base

## ruling
**RULED** (owner, 2026-09-14, review sheet): `donor_current_sprite.png`

> "The images for the source material are all over the place. I think this is a pretty good rendition of it. https://static.wikia.nocookie.net/starwars/images/b/bc/Beldons-woswfg.jpg/revision/latest?cb=20070123191252 was clearly its inspiration, please see that and reproduce it rimworld-style."

**RULED** (owner, 2026-10-08, Greentide sheet 2026-10-05): the canon image is `wookieepedia_woswfg.webp` (https://static.wikia.nocookie.net/starwars/images/b/bc/Beldons-woswfg.jpg); the purple `beldon_wookieepedia_1.jpg` is to be ignored entirely. Verbatim:

> "This is a tricky one. Please regenerate the Canon creature based on the current donor art. I know it's low quality.  It comes from here, and you should add this as the actual canon image: https://static.wikia.nocookie.net/starwars/images/b/bc/Beldons-woswfg.jpg/revision/latest/scale-to-width-down/1000?cb=20070123191252 Please realize that in a much more realistic manner. Totally ignore the weird purple drawings you currently have as the canon database entry."
