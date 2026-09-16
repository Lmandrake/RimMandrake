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
eopie Akkani happily ate meat scraps during his exile on Tatooine. Lifespan
~90 standard years. Canon role: Tatooine's default pack/transport animal for
moisture farmers and locals — seen ridden and laden with cargo baskets/saddle
gear in *The Phantom Menace* (hauling podracer parts), *Obi-Wan Kenobi*, and
multiple *Clone Wars* episodes; also found on Saleucami, Zardossa Stix, and
Batuu. Behind the scenes: the eopie design began as a retouched production
painting of the kaadu (the creature that was ultimately reassigned to the
Gungans of Naboo instead).

## Visual brief
The candidate images agree closely with each other and diverge sharply from
the donor sprite's color. Eopies read as **pale — cream, dusty tan, or a
pinkish-grey** skin tone, never brown. The body plan is unmistakably
camel-like: a long, low-slung barrel body on four thin legs, each ending in
small clawed/hoofed toes, topped by a genuinely elongated **trunk-like
snout** (more tapir/small-elephant trunk than a simple long muzzle) with one
large dark eye set well back on the head. None of the images show visible fur
or hair — the hide reads smooth-to-leathery, not woolly. Every reference shows
the eopie loaded with practical tan/brown leather cargo saddlebags and woven
wicker panniers strapped across its back and neck, which is core to its
in-universe role as a pack animal, though that's harness/tack rather than a
body feature. The stylized "EOPIES!" cartoon thumbnail is a much lower-fidelity
source (flat shading, exaggerated cartoon eyes) but still agrees on the pale
tan color and the long trunk-snout silhouette, so it corroborates rather than
contradicts the higher-fidelity images.

**The current donor sprite (`donor_current_sprite.png`) gets the color
roughly right** — it's a similar pale dusty pink-grey — **but the shape is
wrong**: it's a rounded, legless blob with a stubby trunk-snout, no visible
legs, no saddle/pack gear, and none of the long low camel-backed silhouette
every reference image shows. Any regen should keep the pale skin tone but
give the body a longer, lower quadruped silhouette with visible legs and the
distinctive trunk-like snout reading clearly against the body.

## Must show
- [ ] Pale skin tone — cream, dusty tan, or pinkish-grey — never brown
- [ ] Long, low-slung, camel-like barrel body on four thin legs with small clawed/hoofed toes
- [ ] Elongated trunk-like snout (closer to a tapir or small elephant trunk than a simple long muzzle)
- [ ] One large dark eye set well back on the head
- [ ] Smooth-to-leathery hide with no visible fur or hair

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Eopie (Wookieepedia article text, pulled
  via `starwars.fandom.com/api.php?action=parse&page=Eopie&prop=wikitext`,
  2026-09-13)
- https://static.wikia.nocookie.net/starwars/images/1/11/Eopie-FFp67.png (Wookieepedia infobox render — full profile with saddle/pannier gear)
- https://static.wikia.nocookie.net/starwars/images/f/f7/Eopie.jpg (on-set/production photo comparison of two eopies, front and side view, cream/tan skin)
- https://static.wikia.nocookie.net/starwars/images/c/ce/Eopies.jpg (stylized "EOPIES!" SW Kids YouTube thumbnail — lower-fidelity cartoon style but corroborates color and trunk-snout silhouette)

## Candidate images
- `donor_current_sprite.png` — this repo's current shipped sprite (SWBestiary mod, `Eopie_east` base variant), pale pinkish-grey blob with stubby trunk, no visible legs or pack gear
- `wookieepedia_infobox.png` — Wookieepedia infobox render, full profile, pale grey-pink hide, elongated trunk-snout, wicker/leather cargo panniers on back
- `wookieepedia_screencap.jpg` — two eopies front/side, cream-tan skin, camel-like low body, laden with saddlebags and a bridle/lead line
- `wookieepedia_herd.jpg` — stylized cartoon still (SW Kids "EOPIES!" video thumbnail), lower fidelity but agrees on pale tan color and trunk-snout shape, shows big prominent eyes

## ruling
**RULED** (owner, 2026-09-14, review sheet): `wookieepedia_infobox.png`

> "We have a regenerated Eopie that is pretty good, but it has legs. We should remove and regenerate it to the new spec level."
