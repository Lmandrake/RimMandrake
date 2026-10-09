# Borcatu

**defName**: `RSW_Borcatu` (vendored in SWBestiary, texture folder `Borcatu`)

## Sourced text (Wookieepedia)
Two separate pages. The **Disney Infinity 3.0** page (https://starwars.fandom.com/wiki/Borcatu)
carries a `{{Top|ncc}}`/`{{Noncanon}}` banner (non-canon, not canon) and says
only "a type of creatures that was found in the galaxy"; it notes the species
debuted in the 1994 Legends book *Creatures of the Galaxy* and reappeared as
a placeable Toy Box creature in *Disney Infinity 3.0* (2015).

The **Legends** page (https://starwars.fandom.com/wiki/Borcatu/Legends,
source *Creatures of the Galaxy*, 1994) holds the biology: non-sentient,
**0.2 - 0.5 m long**, skin colour "Variable", distinctions "digging claws,
scales, powerful jaws", origin **Escabar** (original habitat the deserts of
**Serhan**, in its northeast), diet scavenger and cannibal, habitats burrows,
deserts, forests, slums. "Small, bad-tempered scavengers" that spread from
c. 150 BBY by stowing away on starships; "a scaly, thick hide which may have
evolved to help resist sandstorms", sharp teeth and claws used to burrow or
defend, vicious, fighting and cannibalizing each other when short of food.
Hard to exterminate: "mottled, dark skin made effective camouflage", pups
only a few centimeters long, very efficient metabolism, capital ships could
host dozens unnoticed.

## Visual brief
**The two candidate images disagree sharply, and this is the important finding
for this creature** — same species, two incompatible body plans:

- The **1994 *Creatures of the Galaxy* illustration** (the original Legends source) shows a **pangolin/armadillo-like creature**:
  a body covered in large, overlapping, pointed scales (a pinecone/artichoke
  texture), a long tapering snout with visible whiskers, small stubby
  clawed legs, and a short spiked tail. Grayscale line art, no color given.
- The **2015 Disney Infinity 3.0 toy-figure render** (low-poly, stylized)
  shows a completely different animal: a **reddish-brown, mottled quadruped**
  with a cat/boar-like face (fangs visible, pale claws/toes, pale eyes), tall
  pointed ears or horns, and a long spiked quill or horn projecting
  backward off the haunches/tail — no scale texture at all, smooth mottled
  hide instead.

These are not two angles of the same design — the scaled pangolin-esque body
and the smooth-hided mottled quadruped cannot both be "the" borcatu. The Legends
page does say scales ("digging claws, scales, powerful jaws"; "scaly, thick
hide"), so the 1994 art is the one the prose supports; the Disney Infinity
figure is a non-canon design.

**The current donor sprite** (`donor_current_sprite.png`) is mottled
reddish-brown with a spiky tail, pointed ears, and clawed feet — it tracks
the *Disney Infinity* render reasonably closely (same color family, same
spiked tail, same general silhouette) and is the closer of the two candidate
designs. A reviewer should be aware the 1994 original sourcebook art (scaled,
pangolin-like) looked nothing like either the donor sprite or the Disney
Infinity figure.

## Must show
*Rewritten 2026-10-09 to the canon_check leniency lesson (`Transient/canon_check_leniency_2026-10-09.md`): body plan, colour layout and a negative, each checkable on a 256px sprite. Grounded in the `## ruling` below (owner 2026-09-14 picked `donor_current_sprite.png`: "Mix #1 and #2 together to regenerate our own. #3 is HORRIBLE, ignore."), i.e. the donor sprite and the Disney Infinity render, with the 1994 pangolin art set aside.*
- [ ] BODY PLAN: a small four-legged scavenger with clawed feet; a cat/boar-like head with a fanged mouth and tall pointed ears (or horn-like projections); a long spiked quill/horn projecting backward off the haunches/tail
- [ ] COLOUR LAYOUT: reddish-brown body, mottled darker all over (the Legends text's camouflaging "mottled, dark skin"); pale claws/toes
- [ ] Smooth mottled hide, not overlapping pointed pangolin-style scales
- [ ] Cat/boar-like fanged face with powerful jaws
- [ ] NEGATIVE: not the 1994 pangolin/armadillo design (no pinecone scales, no whiskered tube snout); not scaled pangolin-grey; not a plain cat or boar (must carry the backward spiked quill)

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Borcatu (Wookieepedia, fetched via the
  MediaWiki API `action=parse&prop=wikitext` endpoint, 2026-09-13)
- https://starwars.fandom.com/wiki/File:BorcatuDisneyInfinity.png
- https://starwars.fandom.com/wiki/File:Borcatu-CotG.jpg

## Candidate images
- `donor_current_sprite.png` — this repo's current shipped sprite (SWBestiary
  mod, east-facing base variant): mottled reddish-brown quadruped, spiky
  tail, pointed ears, clawed feet — closer to the Disney Infinity design than
  to the 1994 sourcebook art.
- `wookieepedia_disneyinfinity.jpg` — the *Disney Infinity 3.0* Toy Box
  render: low-poly, reddish-brown mottled quadruped, cat/boar-like fanged
  face, tall pointed ears/horns, long spiked tail-quill, pale claws.
- `wookieepedia_creaturesofthegalaxy.jpg` — grayscale scan from the 1994
  *Creatures of the Galaxy* sourcebook (original species debut): a
  pangolin/armadillo-scaled creature with a long whiskered snout, small
  stubby legs, short spiked tail — visually unrelated to the Disney Infinity
  design; no color information given.

## ruling
**RULED** (owner, 2026-09-14, review sheet): `donor_current_sprite.png`

> "Appears to be a very rare creature reference image-wise. Mix #1 and #2 together to regenerate our own. #3 is HORRIBLE, ignore."
