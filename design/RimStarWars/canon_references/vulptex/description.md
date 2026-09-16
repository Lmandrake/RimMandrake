# Vulptex

**defName**: `RSW_Vulptex` (vendored in SWBestiary)

## Sourced text (Wookieepedia)
Vulptices (singular vulptex) were a non-sentient species of omnivorous,
gregarious canids native to the mineral world **Crait**, first appearing in
*Star Wars: The Last Jedi* (2017). Fox-like in build, with a flexible body,
large upright pointed ears, and a bushy tail. Their single most distinctive
feature — called out explicitly in the infobox as "unique crystalline
bristles/spikes" — is a coat made of **white crystalline bristles**
covering the whole body, which jingle/tinkle audibly as they move and which
the species reportedly uses to communicate (rubbing bristles against stones
or each other to make pack-specific sound patterns). Eye color is given
inconsistently by two production sources: **blue** (per the *TLJ* trailer)
and **red** (per *TLJ* behind-the-scenes footage) — Wookieepedia lists both.
Size: ~51 cm tall, ~1.2 m long, ~9.1 kg — a small animal, roughly
coyote/fox-sized rather than wolf-sized. Habitat: highland caves, canyons,
and salt flats on Crait; diet of tubers and small burrowing mammals dug from
under the salt crust. Live in family groups called skulks (3-4 families,
up to ~10 each; occasionally larger dens of up to ~100). Canon role: appear
during the Battle of Crait in *The Last Jedi* — a skulk hides in the
Resistance's abandoned rebel base, and one vulptex leads the escaping
Resistance survivors to a hidden exit, which Rey then widens with the Force.
**Behind the scenes**: per creature effects supervisor Neal Scanlan, the
in-universe explanation is that "they've fed off this planet for so long
that their fur has become crystalline... they've taken on the very surface
of the planet they live on" — i.e. the crystal coat is an adaptation to
Crait's crystalline salt-and-mineral surface, not incidental decoration.
Designers cited "crystal glass chandeliers" as a visual reference for the
coat's faceted, light-catching quality. The creature was built as a
practical animatronic for the film.

## Visual brief
All four candidate images agree closely with each other and with the text.
The vulptex is NOT a smooth-furred fox with sparkly highlights — the
"crystalline" coat is a bold, literal visual feature: individual bristles
read as hard, faceted, glass-like **shards/spikes** standing up off the
body (most visible along the spine, shoulders, and especially the tail,
which is a dense brush of spike-like points rather than a soft fluffy
brush). The two studio/promotional renders (`wookieepedia_infobox.jpg`,
`wookieepedia_masterwork.jpg`) show this clearly in clean lighting: a
grey-blue-white coat with visible individual crystal facets catching cool
light, a long slender fox muzzle, very large upright triangular ears, a
long thin tail covered in the same spiked coat, and notably **long, thin
legs and an upright, almost deer-like stance** — taller and leggier than a
real-world fox, not low-slung. The two in-film screencaps
(`wookieepedia_craitsurface.jpg`, `wookieepedia_battlescreencap.jpg`)
confirm the same silhouette and coat under real film lighting/grading, and
also confirm the text's eye-color inconsistency firsthand: the cave shot
shows glowing **orange/amber** eyes, while the daylight battle shot shows
clearly **blue** eyes — the two production sources Wookieepedia cites are
not reconciled in the actual footage either, so both are genuinely correct
depending on shot/lighting.

**The donor sprite (`donor_current_sprite.png`) disagrees with canon on
nearly every visual axis.** It is a flat cartoon icon: a low-slung,
elongated, short-legged body (closer to a ferret or a lounging rabbit than
an upright fox), a smooth smoothly-shaded white coat with pale blue patches
and a solid black outline, and **no crystalline/faceted texture
whatsoever** — no spikes, no shard shapes, no faceted shading anywhere on
the body or tail. The white base color and cool blue tint are the only
things it gets right; the silhouette (should be tall/leggy/upright, is
low/long/crouched), the ear size (canon's ears are dramatically larger
relative to the head), and above all the signature crystalline bristle
texture (entirely absent) are all mismatched against every reference image.
Any regen should prioritize the spiked/faceted coat texture first — it's
the one feature that makes a vulptex recognizable as a vulptex rather than
a generic white fox — and correct the body proportions toward a taller,
longer-legged stance.

## Must show
- [ ] Coat reads as hard, faceted, glass-like crystal shards/spikes standing up off the body — not smooth fur
- [ ] Tail is a dense brush of spike-like crystalline points, not a soft fluffy brush
- [ ] Long, slender fox muzzle with very large, upright, triangular ears
- [ ] Long, thin legs and an upright, deer-like stance — taller and leggier than a real-world fox, not low-slung
- [ ] Coat colour is grey-blue-white with visible individual crystal facets

## Engine limits
none known — the donor sprite's mismatch (a low-slung, short-legged, smoothly-shaded body with no faceted texture at all) is recorded in the entry as an art/silhouette gap to correct in a regen, not as something the pipeline cannot render.

## Source URLs
- https://starwars.fandom.com/wiki/Vulptex (Wookieepedia article text, pulled
  via `starwars.fandom.com/api.php?action=parse&page=Vulptex&prop=wikitext`,
  2026-09-13)
- https://static.wikia.nocookie.net/starwars/images/7/7f/Vulptex-CGSWG.png (infobox render, *Star Wars: Creatures Great and Small*/CGSWG source)
- https://static.wikia.nocookie.net/starwars/images/8/80/Vulptex-Masterwork2018.png (Masterwork 2018 promotional render, sitting pose)
- https://static.wikia.nocookie.net/starwars/images/f/fb/Vulptex_2.png (in-film screencap, Crait cave/salt surface, night lighting)
- https://static.wikia.nocookie.net/starwars/images/9/9a/Crait_crystal_creature.png (in-film screencap, Battle of Crait, daylight, Millennium Falcon overhead)

## Candidate images
- `donor_current_sprite.png` — this repo's current shipped sprite (SWBestiary mod, east-facing base variant), flat white/pale-blue cartoon icon, low-slung body, no crystal texture
- `wookieepedia_infobox.jpg` — Wookieepedia infobox render, full standing side profile on white background, clearest single reference for the crystalline coat texture and leggy silhouette
- `wookieepedia_masterwork.jpg` — alternate promotional render, sitting pose on white background, shows tail and ear detail
- `wookieepedia_craitsurface.jpg` — in-film screencap, dark cave/salt-boulder environment, glowing orange/amber eyes
- `wookieepedia_battlescreencap.jpg` — in-film screencap, Battle of Crait daylight scene with Millennium Falcon overhead, clearly blue eyes

## ruling
**RULED** (owner, 2026-09-14, review sheet): `wookieepedia_infobox.jpg`
