# Eopie

**defName**: `RSW_Eopie` (vendored in this repo's own `src/RimStarWars/SWBestiary` mod)

## Sourced text (Wookieepedia)
Eopies were quadruped mammalian herbivores native to the desert planet
Tatooine, tough and acclimated to the endless desert, and domesticated by the
planet's inhabitants as transports and beasts of burden — though bad-tempered,
stubborn, and prone to breaking wind under a heavy load. Average height ~1.75-2
meters. Their rough skin protected them from the heat of Tatooine's twin suns,
and their hooves were adapted to climbing rocky cliffs. The trunked mouth
secretes an adhesive spit the eopie layers over its own eyes (and a parent
lays over a young eopie's head) as sandstorm protection. Though herbivorous,
eopies can eat meat with no ill effects (as with banthas) — Obi-Wan Kenobi's
eopie Akkani (named in the comic *Obi-Wan* 1, not in the show) happily ate meat scraps during his exile on Tatooine
(*Obi-Wan Kenobi*, "Part I"). Lifespan
~90 standard years. Eopies are protective of their young (young travel in a parent's shadow to keep cool; *Galaxy of Creatures*, "Eopie").
A **horned eopie** subspecies lives on At Achrann (*Skeleton Crew*, "Can't Say I Remember No At Attin") —
a separate variant, not the Tatooine design. **Legends** (https://starwars.fandom.com/wiki/Eopie/Legends):
cameloid, skin brown, pale or white. Canon role: Tatooine's default pack/transport animal for
moisture farmers and locals — seen ridden and laden with cargo baskets/saddle
gear in *The Phantom Menace* (hauling podracer parts), *Obi-Wan Kenobi*, and
multiple *Clone Wars* episodes; also found on Saleucami, Zardossa Stix, and
Batuu. Behind the scenes: the eopie design began as a retouched production
painting of the kaadu (the creature that was ultimately reassigned to the
Gungans of Naboo instead).

## Visual brief
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."** The cartoon Star Wars Kids "EOPIES!" thumbnail (`wookieepedia_herd.jpg`) was deleted. Every remaining image is the realistic prequel-era CGI/puppet design: `wookieepedia_infobox.png` (Official Star Wars Fact File render) and `wookieepedia_screencap.jpg` (front and side model sheet).

What the realistic images show:
- **Skin:** smooth, finely wrinkled, leathery hide with no fur — pale grey-lavender to pinkish-grey on the infobox/fact-file render, cream-white on the model sheet, mottled darker grey on the legs and flanks with knot-like bumps at the joints. (The canon article gives no colour; Legends lists brown, pale and white.)
- **Body:** camel-like — tall thin legs (taller than the old brief's "low-slung" wording implied), a barrel body sloping from high haunches, a long forward-thrust horizontal neck.
- **Head:** a long drooping trunk-like snout ending in a rounded pink-tipped nose; one large amber-to-dark eye with heavy wrinkled lids set well back on each side; a few sparse bristles on top of the head.
- **Feet:** broad splayed pads with three or four thick blunt claw-toes, wrinkled like an elephant's foot.
- **Tack:** leather saddlebags, wicker panniers and a rope bridle in every image — harness, not body.

**The current donor sprite (`donor_current_sprite.png`) gets the colour roughly right but the shape is wrong**: a rounded legless blob with a stubby trunk, none of the tall thin-legged camel silhouette.

## Must show
*Rewritten 2026-10-09 to the canon_check leniency lesson (`Transient/canon_check_leniency_2026-10-09.md`): body plan, colour layout and a negative, each checkable on a 256px sprite. Grounded in both images.*
- [ ] BODY PLAN: four tall, very thin, stilt-like legs (leg length clearly greater than body depth) under a short barrel body that is higher at the haunches; a long neck thrust FORWARD roughly level with the back (not raised upright); a long head that ends in a drooping trunk-like snout pointing down-forward
- [ ] COLOUR LAYOUT: pale all over (cream-white, grey-lavender or pinkish-grey); legs and flanks mottled slightly darker grey; snout tip pink; never brown
- [ ] Feet: wide flat splayed pads with 3-4 thick blunt toes, elephant-like, visibly broader than the thin legs above them; knobbly bumps at the knees
- [ ] One large heavy-lidded eye set far back on each side of the long head
- [ ] Smooth, finely wrinkled leathery hide with no visible fur (a few sparse bristles on the head only)
- [ ] Realistic rendering: natural wrinkled leathery skin texture and lighting, no outlines, no cartoon shading
- [ ] NEGATIVE: not a camel (no hump, no fur, no upright S-neck, no split hooves); not an elephant or tapir (no tusks, no big ears, no stocky pillar legs); not a legless or short-legged blob

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Eopie (Wookieepedia article text, pulled
  via `starwars.fandom.com/api.php?action=parse&page=Eopie&prop=wikitext`,
  2026-09-13)
- https://static.wikia.nocookie.net/starwars/images/1/11/Eopie-FFp67.png (Wookieepedia infobox render — full profile with saddle/pannier gear)
- https://static.wikia.nocookie.net/starwars/images/f/f7/Eopie.jpg (on-set/production photo comparison of two eopies, front and side view, cream/tan skin)

## Candidate images
- `donor_current_sprite.png` — this repo's current shipped sprite (SWBestiary mod, `Eopie_east` base variant), pale pinkish-grey blob with stubby trunk, no visible legs or pack gear
- `wookieepedia_infobox.png` — REALISTIC render (infobox; *The Official Star Wars Fact File* Part 67), full profile, pale grey-pink hide, trunk-snout, panniers; file `Eopie-FFp67.png` — https://static.wikia.nocookie.net/starwars/images/1/11/Eopie-FFp67.png/revision/latest?cb=20221017052712
- `wookieepedia_screencap.jpg` — REALISTIC model sheet, front and side, cream-white hide, saddlebags and bridle (same image as file `Eopie.jpg`, *Episode I Insider's Guide*) — https://static.wikia.nocookie.net/starwars/images/f/f7/Eopie.jpg/revision/latest?cb=20081009000836

## ruling
**RULED** (owner, 2026-09-14, review sheet): `wookieepedia_infobox.png`

> "We have a regenerated Eopie that is pretty good, but it has legs. We should remove and regenerate it to the new spec level."

**REDO** (owner, 2026-10-04, doubles sheet `Transient/art_doubles_compare_2026-10-04.decisions.json`, item ART_VERSION_WRANGLING_1) on `swanimals/Eopie/Eopie` (variants A–E and `Eopie_j` marked "redundant with above"):

> "B is closest but still pretty bad. Please look at Canon imagery."
