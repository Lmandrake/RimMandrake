# Dianoga

**defName**: `RSW_Dianoga` (vendored in this repo's own `src/RimStarWars/SWBestiary` mod)

## Sourced text (Wookieepedia)
Dianoga ("trash squid" is the related/subspecies name used for Death Star
tank-dwelling specimens specifically) are large, sentient, omnivorous
cephalopods native to the swampy planet Vodran in the Si'Klaata Cluster
(Hutt Space). Body plan: **seven suckered tentacles**, an eyestalk, a mouth
of sharp teeth, and several hearts. Length 7-10 meters. Skin color is
**deep purple** on a mature adult, but dianoga can actively change color and
pattern for camouflage — turning black, gray, or even transparent. Blood has
a blue tint. They can regenerate lost limbs and have excellent hearing.
Hermaphroditic, with individuals able to identify as female, "diangous" (the
most common gender), or male. Diet: omnivorous — fish, crabs, bones, and
aquatic plants. Entirely water-dependent (can survive brief stretches in open
air but will dry out). Society: a primitive tribal culture with its own
complex humming language that carries through water and scares off prey;
they venerate water and believe in reincarnation.

Canon role: the most famous dianoga is the unnamed one living in the Death
Star's trash compactor in *A New Hope* ("There's something alive in here" —
Luke Skywalker). Other named/attested appearances: a dianoga in the flooded
wreck of a derelict *Venator*-class Star Destroyer on Bracca (*The Bad
Batch*), a dianoga family in the Bracca Badlands during the High Republic
Era, and dianoga living in the SoroSuub refinery's water tanks on Sullust
(*Star Wars Battlefront*).

## Visual brief
All three candidate images agree and clearly show the canon body plan: a
small stalked eye (a single eye, dark reddish, atop a thin stalk) sits above
a bulbous head/body mass; below that, a large circular mouth ringed with
sharp teeth sits at the center where the limbs converge; several long, thin,
tapering tentacles hang/radiate downward from the body. Coloration in the
clean infobox render is a deep maroon/purple-brown with a wrinkled, ridged
skin texture — matching "deep purple" in the text. The Sullust refinery
still shows the same tentacled silhouette lit gold underwater. The "Toothy"
jar image (a juvenile specimen preserved in a tank at a theme-park
prop/display) shows mottled olive-green through murky liquid — consistent
with the text's claim that dianoga can shift color/pattern, not a
contradiction of the purple default.

**The current donor sprite (`donor_current_sprite.png`) does NOT match the
canon body plan at all.** It depicts a four-legged, tailed creature with a
single eyestalk on top of its head — the eyestalk is the only correct detail
carried over. There are no tentacles, no central toothy maw, and the
overall silhouette reads as a legged mammal/reptile rather than a hanging
cephalopod with seven suckered limbs. This is a clear, high-confidence
mismatch: any regen must replace the legged body with a radial mass of long
thin tentacles beneath a small eyestalk, in deep purple/maroon tones, with a
visible toothed central mouth.

## Must show
- [ ] Single dark reddish eyestalk (a small stalked eye) atop a bulbous head/body mass
- [ ] Large circular mouth ringed with sharp teeth at the center where limbs converge
- [ ] Several long, thin, tapering tentacles radiating/hanging downward — not four legs and a tail
- [ ] Deep maroon/purple-brown base coloring with a wrinkled, ridged skin texture

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Dianoga (Wookieepedia article text, pulled
  via `starwars.fandom.com/api.php?action=parse&page=Dianoga&prop=wikitext`,
  2026-09-13)
- https://static.wikia.nocookie.net/starwars/images/d/df/Dianoga_BF.png
  (*Star Wars Battlefront* infobox render, clean full-body reference)
- https://static.wikia.nocookie.net/starwars/images/f/f8/Dianoga-BF.png (a
  dianoga in the SoroSuub refinery water tanks on Sullust, *Battlefront*)
- https://static.wikia.nocookie.net/starwars/images/d/d3/Dianoga_SWGE-D23_video.jpg
  ("Toothy," a juvenile dianoga on display, Galaxy's Edge D23 promo still)

## Candidate images
- `donor_current_sprite.png` — this repo's current shipped sprite (SWBestiary
  mod, east-facing base variant) — a legged, tailed creature with an
  eyestalk; does not match the tentacled cephalopod body plan
- `wookieepedia_infobox.png` — *Battlefront* infobox render, clean full-body
  shot showing eyestalk, central toothed mouth, and radiating tentacles in
  deep purple-maroon
- `wookieepedia_sullust_refinery.jpg` — a dianoga in the SoroSuub refinery
  water tanks on Sullust, confirms silhouette underwater/backlit
- `wookieepedia_toothy_swge.jpg` — a juvenile specimen ("Toothy") on display
  in a tank, mottled olive-green coloring, consistent with the species'
  color-changing camouflage ability

## ruling
**RULED** (owner, 2026-09-14, review sheet): `wookieepedia_infobox.png`

> "Yup. Mixture of #2 dominant with some hints of #1 is needed on how to Rimworld-ify it. And #3/#4 are inspiration for the Star Wars Cuisine mod!"
