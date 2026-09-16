# Trandoshan

**defName**: `RSW_RimMandrakeTrandoshan` (`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Assigned `Jawa_HuttCartel: S`, `Jawa_Junkers: S`.

## Sourced text (Wookieepedia)
Trandoshans are sentient **reptilian** humanoids. Infobox: **height up to 2.1
meters**; origin Trandosha; habitat forest or jungle; skin colour green, yellow,
brown, orange, cream, gray, red; eye colour green, yellow, orange, purple;
distinctions "scaly skin".

**Body plan.** Trandoshans ranged **from tall and fairly gaunt to short and more
rotund** — a genuinely wide build range, not one physique. They were powerful
beings and had **long thin arms that ended in either three thick digits, or four
thin digits, including a thumb** (both hand counts are canonical). They had **a
pair of eyes set back on a pointed skull, and a jaw filled with pointed teeth**.
**Some Trandoshans even had a crown of feathers atop their skulls.** They **hatched
from eggs**, with individuals sharing a clutch calling each other **clutchmates**.
They used their **sharp claws to climb tall trees** in the forests or jungles they
naturally inhabited. They **often walked barefooted, and had feet with three
digits each**. Skin colour could vary wildly; some individuals had patterning —
one named Smug had brownish-orange skin with **red stripes on his face**.

**Unusual abilities.** 🔑 **They were able to regrow their limbs if they were
severed, and regrow lost scales.** 🔴 With one sourced limit: **a plasma blast
could prove so damaging that a Trandoshan's scales were never able to regrow.**
Both halves matter — the regeneration is real, and it is defeatable by energy
damage specifically.

**Behavior.** **The base urges of a Trandoshan brain included rage, fury, and
aggression, but a Trandoshan could rise above those tendencies** — the article is
explicit that the aggression is a substrate, not a destiny (there are Trandoshan
Jedi, e.g. Sskeer). **However, the rare Magrak Syndrome would bring them back out
over time.**

## Visual brief
🔴 **The infobox distinction "scaly skin" and the body text's "smooth, scaly skin"
are directly contradicted by every image, and the images win.** The reference
render (Bossk, full body) shows conspicuously **coarse, large, raised, overlapping
plate-scales** — most pronounced on the forearms, the backs of the hands and the
whole lower leg and foot, where individual scales are big enough to count. Nothing
about it reads "smooth". A sprite built from the word "smooth" will lose the
species' texture entirely. Trust the images: **Trandoshan skin is armour-plated
and heavily textured.**

From the reference render:
- **Colour is a warm tan/olive/khaki with a yellow-green cast and brown mottling**,
  darkening on the crown and the scale ridges — not the flat green the skin-colour
  list invites.
- **The head is a broad, heavy reptilian skull with a wide flat muzzle**, no
  external ears, a low ridged crown, and **a jaw of many small pointed teeth
  visible even with the mouth closed** — the teeth are part of the resting face.
- **The eyes are small, deep-set and set well back**, orange-red with slit pupils
  — small eyes on a big skull, the same proportion trap as the Hutt.
- 🔴 **"Long thin arms" is contradicted too.** The reference individual's arms are
  thick and heavily muscled, not thin. Given the text's own "tall and gaunt to
  short and rotund" range, the honest statement is that arm mass varies and the
  best-known individual is at the heavy end — but nothing on file supports
  *thin* as the default.
- **Hands: three thick digits ending in long, dark, curved claws.** Feet: three
  thick digits, bare, also clawed. The claws are dark keratin against pale
  scales — high contrast, and a read-at-a-glance feature.
- **Trandoshans wear ordinary clothing over the scaled body**, and characteristic-
  ally leave forearms and lower legs BARE so the scales show. In the reference
  render a yellow flight suit stops at the elbow and mid-shin. That
  bare-extremities convention is worth keeping: it is how the scale texture stays
  visible under apparel.
- The **live-action** image (Dokk Strassi) is the palette contrast: markedly
  **greyer and cooler**, with the scales reading as slate-and-tan rather than
  khaki, and a much more pronounced brow/crown ridge. So the range spans warm
  khaki-tan to cool grey-tan; both are canon.
- **No feathers** on any of the three individuals — the "crown of feathers" is
  attested in text only and is evidently a minority trait, not the default. Do not
  add feathers on the strength of the sentence alone.
- The **Topps illustration** agrees on the plate-scale texture, the wide toothy
  muzzle and the clawed three-digit hands, at a stylized level.

**donor_current_sprite.png is weak evidence.** The copied file is
`SWX/Pawn/HeadType/trandoshan/Male_Trandoshan_south.png` — a **greyscale mask**,
which is correct and expected for a RimWorld humanlike head (the game tints it
from the skin-colour gene, so its lack of colour is not a defect and the hue
findings above belong on the gene). Shape-wise it is a broad rounded skull with a
short muzzle and a suggestion of teeth, which is roughly right; but it carries
**no scale texture at all** — the single feature the images insist on — and its
eyes are ordinary small dots rather than deep-set slit-pupilled. A separate
`HeadAttachments/trandoshan/ridgedcrown_{south,east,north}.png` exists and
supplies a small central crown ridge plus two brow ridges, which does add the
crown/brow read. **Nothing on disk supplies the plate-scale texture, the visible
resting teeth, or the clawed three-digit hands and feet.**

## Must show
- [ ] Coarse, large, raised, overlapping plate-scale texture, most pronounced on the forearms, backs of the hands, and lower legs/feet — not smooth skin
- [ ] Warm tan/olive/khaki colour with a yellow-green cast and brown mottling, OR the cooler grey-tan live-action variant — never a flat green
- [ ] Broad, heavy reptilian skull with a wide flat muzzle, no external ears, and small pointed teeth visible even with the mouth closed
- [ ] Small, deep-set, orange-red eyes with slit pupils
- [ ] Three thick digits on hands and feet ending in long, dark, curved claws that contrast against the paler scales
- [ ] No feathers

## Engine limits
none known — the donor sprite's greyscale mask is correct/expected (the game tints it from the skin-colour gene); the missing plate-scale texture, visible resting teeth and clawed digits are recorded as absent art, not as something the pipeline cannot render.

## Source URLs
- https://starwars.fandom.com/wiki/Trandoshan (Wookieepedia article; direct page HTML
  is Cloudflare-walled — wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Trandoshan&format=json&prop=wikitext`,
  61,279 chars, 2026-09-15)
- https://static.wikia.nocookie.net/starwars/images/7/72/Bossk_full_body.png (File:Bossk_full_body.png, the infobox image → wookieepedia_infobox_bossk.jpg)
- https://static.wikia.nocookie.net/starwars/images/1/1f/DokkStrassi-BoBFCE.png (File:DokkStrassi-BoBFCE.png → wookieepedia_dokk_strassi_liveaction.jpg)
- https://static.wikia.nocookie.net/starwars/images/0/0a/Trandoshan-2024ToppsSWHyperspace.png (File:Trandoshan-2024ToppsSWHyperspace.png → wookieepedia_topps_illustration.jpg)
- NOT fetched this pass: https://www.starwars.com/databank/trandoshans (official Databank).

## Candidate images
- `wookieepedia_infobox_bossk.jpg` — **the reference of record.** The infobox image
  (File:Bossk_full_body.png): a full-body Trandoshan in a flight suit on a
  transparent background, costume-photography fidelity. Settles the coarse
  overlapping plate-scales (against the prose's "smooth"), the warm khaki/olive
  colour, the wide toothy muzzle with visible resting teeth, the small deep-set
  orange slit-pupilled eyes, the three thick clawed digits on hands and bare feet,
  and the bare-forearm/bare-shin dress convention.
- `wookieepedia_dokk_strassi_liveaction.jpg` — a live-action Trandoshan (The Book of
  Boba Fett). **The palette contrast case**: much cooler and greyer than the
  reference, with a heavier brow/crown ridge — establishing the warm-to-cool range.
- `wookieepedia_topps_illustration.jpg` — a stylized card illustration; independent
  agreement on the plate-scale texture, muzzle and claws. Treat line and palette as
  the artist's.

## ruling
(empty — owner has not reviewed this race yet)
