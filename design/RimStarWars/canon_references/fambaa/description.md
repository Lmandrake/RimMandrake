# Fambaa

**defName**: `Fambaa` (third-party, mlie.starwarsanimalcollection, not vendored — see Watch out)

## Sourced text (Wookieepedia)
Pulled via the MediaWiki API (`action=parse&page=Fambaa&prop=wikitext`, direct
page URL was not tried after the API route worked cleanly) 2026-09-13.

- **Body plan**: quadruped amphibians with tough hides. Born with moist skin
  and gills; as they mature the gills vanish and the skin dries and
  thickens. A tail made of cartilage. Pillar-like limbs with strong joints
  to bear heavy loads, and broad feet with wide toes for stability and to
  stop them sinking into marshland.
- **Size**: height 4.3 meters (per the in-universe Databank).
- **Coloring**: skin color listed as **Brown** and **Green** (sourced to
  *Nexus of Power*); eye color **Yellow** (sourced to *The Phantom Menace*
  itself).
- **Classification**: non-sentient amphibian; herbivorous; habitat "grass
  plains"; native to Naboo and Onderon (biologists suspect Naboo merchants
  originally transplanted them to Onderon, alongside the similar
  falumpaset, though fossil evidence is thin).
- **Canon role**: Gungans use fambaas as beasts of burden and draft beasts
  for artillery, breeding herds in secret swamp pastures. Most famously,
  pairs of fambaas carried the two halves of a portable deflector shield
  generator (saddle + leather girth to hold the device, bridle for
  steering) into the **Battle of Naboo** on the Great Grass Plains,
  deployed alongside kaadu and falumpasets to support the Gungan Grand
  Army — this is their first and most iconic appearance, in *Star Wars:
  The Phantom Menace* (1999). Also used by Onderon rebels during the Clone
  Wars to haul heavy artillery (*The Clone Wars*, "Tipping Points"). One
  was part of a traveling sideshow act in "Bound for Rescue"; on Abafar
  fambaa meat is eaten as "Fambaa Delight" ("Missing in Action").
- **Behind the scenes**: early concept sketches showed a two-legged
  dinosaur-like creature; the four-legged design was approved later, and
  concept artist Terryl Whitlatch hand-drew its walk cycle for ILM
  animators.

## Visual brief
Unlike the Wyyyschokk and Peko-peko cases this library exists to catch,
**text and images agree closely here** — there is no dramatic
undersell/misread to flag. All four candidate images converge on the same
palette family the text names (brown/green):

- `wookieepedia_fieldguide.jpg` (*Wildlife of Star Wars: A Field Guide*
  painted illustration) shows the clearest "wild, unburdened" baseline: two
  fambaas browsing a tree, **yellow-green to khaki scaled hide** with
  darker olive mottling, a pale cream/white underside and inner legs, a
  long tapering cartilage tail, a single curved tusk jutting from the lower
  jaw, and reddish-orange eyes. This is the best single reference for
  natural skin pattern and body proportions (long low body, thick
  pillar-like legs, broad splayed toes).
- `wookieepedia_shieldgenerator.jpg` (`FambaaShield-SWE.png`, an official
  encyclopedia-style CG render pair) directly depicts the canon Battle of
  Naboo role: two fambaas side by side, each saddled with a red-brown
  leather harness and carrying one half of the deflector shield generator
  (a dish-shaped emitter on the left animal, a smaller focusing/receiver
  rig on the right). Skin here reads as smoother, **tan-olive/khaki**
  mottled hide — same family as the field guide painting, just smoother
  and less saturated.
- `wookieepedia_herd.jpg` (`Fambaas-SWE.jpg`) is the same CG render pair as
  `wookieepedia_shieldgenerator.jpg`, just re-cropped/re-composited on a
  green background rather than white — treat it as a duplicate confirming
  the tan-olive coloring and harness/shield-generator rigging, not an
  independent sighting.
- `wookieepedia_infobox.jpg` (`Fambaa.png`, the current wiki infobox art —
  comic/ink-illustration style) shows a **darker, more saturated olive
  green** warty/bumpy hide than the other three images, a wide tusked
  mouth, and the round dish shield-generator component strapped to its
  back. It is stylistically the outlier (flat comic inking vs. painted or
  CG-rendered elsewhere) but is still squarely in the same green-to-olive
  family the text names — a style difference, not a color contradiction.

**One minor, worth-flagging disagreement**: the sourced infobox eye color
is "Yellow" (cited to the film itself), but the *Field Guide* painting
gives the fambaa reddish-orange eyes. Neither the shield-generator CG
renders nor the flat infobox icon show eye color clearly enough to
arbitrate. Treat eye color as **uncertain between yellow and
reddish-orange**; do not commit to one without a clearer source.

**Net read**: a broad, low-slung, thick-legged quadruped with mottled
brown-to-olive-green reptilian/amphibian hide, pale cream underside, a
tusked wide mouth, a long tapering tail, and (in its canon military role) a
red-brown leather saddle harness carrying shield-generator hardware. No
text/image mismatch on the core color family — brown-and-green is
confirmed by every candidate image, just at different saturations and
stylizations.

## Must show
- [ ] Broad, low-slung, thick pillar-like-legged quadruped body
- [ ] Mottled brown-to-olive-green reptilian/amphibian hide
- [ ] Pale cream/white underside and inner legs
- [ ] Long, tapering cartilage tail
- [ ] A single curved tusk jutting from the lower jaw
- [ ] Broad feet with wide, splayed toes

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/api.php?action=parse&page=Fambaa&format=json&prop=wikitext
  (Wookieepedia current-canon page, wikitext pulled 2026-09-13)
- https://static.wikia.nocookie.net/starwars/images/b/b6/Fambaa.png (current
  wiki infobox illustration)
- https://static.wikia.nocookie.net/starwars/images/2/28/Fambaa-woswfg.jpg
  ("Wildlife of Star Wars: A Field Guide" painted illustration)
- https://static.wikia.nocookie.net/starwars/images/e/e3/FambaaShield-SWE.png
  (encyclopedia-style CG render pair, shield generator halves)
- https://static.wikia.nocookie.net/starwars/images/8/8f/Fambaas-SWE.jpg
  (same CG render pair, green-background crop)
- Donor mod `mlie.starwarsanimalcollection` (Steam Workshop, current 1.6
  release id 3497316713, legacy id 2903582351) — fetched the current
  workshop page directly; its own description confirms *"The release of
  RimWorld 1.6 added improved support for Asset Bundles. To avoid doubling
  the size of the mod, it was re-released using only Asset Bundles"* — i.e.
  loose per-creature textures no longer ship at all. Fambaa is listed among
  the mod's creature roster, but no preview screenshot on the workshop page
  is labeled or identifiable as specifically showing a Fambaa. **No
  donor-mod sprite obtained this pass.**
- General web search for a *Phantom Menace* film screencap of the Battle of
  Naboo fambaa/shield-generator charge did not surface a usable still —
  results returned toy/merchandise photography (FAO Schwarz exclusive
  action figure), video-game wiki pages (*Star Wars Galactic
  Battlegrounds*), and YouTube unboxing videos rather than a clean frame
  grab. **No film still obtained this pass** — the sourced text still
  confirms the Battle of Naboo appearance is in the film itself (Wookieepedia
  lists `{{Film|I}} {{1st}}` as its first appearance), a search-summary tool
  claim that fambaas "only appear in video games" is contradicted by that
  primary source and should be disregarded.

## Candidate images
- `wookieepedia_infobox.jpg` — current Wookieepedia infobox art (comic/ink
  style): dark saturated olive-green warty hide, tusked mouth, shield
  generator dish strapped to its back via harness.
- `wookieepedia_fieldguide.jpg` — "Wildlife of Star Wars: A Field Guide"
  painted illustration, two fambaas browsing a tree in the wild (no
  harness): yellow-green/khaki scaled hide, pale cream underside, single
  curved tusk, reddish-orange eyes, long tapering cartilage tail. **Best
  reference for natural body plan and hide pattern.**
- `wookieepedia_shieldgenerator.jpg` — official CG render pair in canon
  military rig: tan-olive mottled hide, red-brown leather saddle harness,
  each animal carrying one half of the deflector shield generator (dish
  emitter / receiver rig). **Best reference for the canon shield-carrier
  role.**
- `wookieepedia_herd.jpg` — the same CG render pair as
  `wookieepedia_shieldgenerator.jpg`, re-cropped on a green background;
  redundant confirmation, not an independent sighting.
- **No donor-mod (`mlie.starwarsanimalcollection`) sprite included** — the
  mod is not present on this machine, its current 1.6 release packs all
  creature art in Asset Bundles rather than loose textures (confirmed from
  the mod's own workshop description), and no labeled preview screenshot of
  a Fambaa specifically was found. Revisit if the mod is ever installed
  locally or a labeled preview surfaces.
- **No film still included** — genuine search effort made (see Source
  URLs) but no usable Phantom Menace battle-scene frame grab was found this
  pass.

## ruling
(empty — owner has not reviewed this creature yet)
