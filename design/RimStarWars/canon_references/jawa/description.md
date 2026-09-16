# Jawa

**defName**: `RSW_MandrakeJawa` (the campaign Jawa, `src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/MandrakeJawaXenotype.xml`).
A second, donor-derived `RSW_RimMandrakeJawa` also ships in
`RimMandrakeXenotypes.xml` but is assigned to NO faction in the owner's
race/faction matrix (`design/Jawa/worldbuilding/review/race_faction_assignment.prefill.json`
lists `RimMandrakeJawa: {}` while `MandrakeJawa` carries
`Jawa_IndigenousTribes: A`, `Jawa_HuttCartel: R`) — the campaign Jawa is the live one.

## Sourced text (Wookieepedia)
Jawas are a sentient, humanoid species indigenous to the desert planet Tatooine.
**Height 1 meter; mass 30 kilograms; lifespan 80 standard years** (infobox,
sourced). Habitat desert, diet omnivorous, languages Jawaese and Jawa Trade Talk.
Infobox gives skin color **Black**, hair color **Black**, and eye color
**Yellow / Orange / Red**. Origin Tatooine.

What Jawas hid underneath their heavy robes was subject to much speculation from
the colonists who settled on Tatooine, with rumors claiming they were giant
rodents or devolved humans. **Although most Jawas were typically small, measuring
only one meter in height, some individuals were significantly taller** — one such
abnormal Jawa was almost as tall as a 3PO-series protocol droid, a model
measuring 1.71 meters. Jawas had **striking glowing eyes, which the explanation
for or purpose of are unknown** (the article states the cause is unexplained in
canon — do not invent one).

**The robe is a life-worn garment with an age-grammar.** When Jawas began to
walk they were given moisture-regulated and insulated robes that they would wear
their whole life. Their robes were originally hemmed to the armpit; as they
mature, the hem is lowered to cover their bodies. Most Jawas measured their
height by the number of hems their robes had had — **an average adult Jawa
usually had five or six hems in their robes.** This is a directly usable art
note: an adult robe should read as a garment repeatedly let out, with visible
successive hem lines, and a child's robe should be short.

Two sensory attestations about the body under the robe, both from named
in-universe observers rather than a narrator: according to the gangster Adwin
Charu, Jawas had **a musky, animal odor** which he likened to a fraternity of
wet rats; according to Peli Motto, Jawas were **quite furry**. "Furry" is
therefore attested only as one character's remark, not as an anatomical
statement — treat it as canon-flavored testimony, not as a licence to draw an
exposed pelt.

## Visual brief
Four independent images (a photographic four-figure reference render, a stylized
Alien Archive illustration, an in-show Mandalorian-era off-world individual, and
a taller-individuals still) agree on the silhouette and disagree sharply on
palette. **On palette, trust the images: "Black" skin in the infobox is not a
skin color at all.**

- 🔴 **The infobox "skincolor = Black" is the VOID INSIDE THE HOOD, not pigment.**
  In every image the interior of the cowl is a flat, featureless, absolutely
  opaque black — no face, no muzzle, no chin, no jaw, no nose, nothing but the
  two glowing eyes floating in it. Any sprite that paints a *dark-skinned face*
  inside the hood is wrong; the correct read is that the hood interior is unlit
  black and the eyes are the only feature. This is exactly the class of error
  a text-only prompt makes from the word "Black".
- **Two glowing eyes, ovoid, close-set, no visible pupil or sclera structure** —
  they read as two lamps, not as eyes with anatomy. Color: **yellow** in the
  four-figure reference and the Alien Archive plate; **red-orange** in the
  off-world Mandalorian-era individual. Both are attested by the infobox
  (Yellow / Orange / Red) AND independently by image, so red-eyed and
  yellow-eyed Jawas are both correct and either is safe to ship.
- **Robe color is NOT one color.** The four-figure reference render is a warm
  mid-**brown** (chocolate-to-russet, film-canonical). The off-world Mandalorian
  individual is a desaturated **grey-brown/charcoal**, visibly dust-caked and
  much colder. The Alien Archive plate is pushed to hot **rust-orange** for
  graphic effect. So the honest range is warm brown to cold dusty grey-brown;
  bright saturated orange is illustration licence, not the canonical hue.
- **The cowl is a soft, fabric peak, not a rigid cone.** In all four it is a
  loose hood pulled well forward so the brow line overhangs the eyes, with the
  fabric slumping into an irregular point or fold at the crown. Some individuals
  have the hood peaked high and forward; others have it collapsed almost flat.
  Do not draw a stiff wizard cone.
- **Hands are always covered, and covered in two different ways.** The
  four-figure reference shows fitted **dark leather gloves**; the off-world
  individual shows coarse **cloth mitts with heavily frayed cuffs** and no
  separate fingers. Both are canonical; neither shows bare skin.
- **The hem is frayed/fringed** at the floor in the reference render and the
  off-world individual, consistent with the let-out-hem lore above.
- **Gear is worn as crossed bandoliers over the chest**, not on a single belt:
  in the off-world individual, two straps cross at the sternum carrying a
  rectangular metal device with three lenses/dials, small tools, a canteen or
  pouch, and a large single-edged blade slung horizontally across the belly. The
  Alien Archive plate independently shows the same crossed-bandolier-plus-pouches
  arrangement plus a hand tool. **A Jawa reads as a walking tool rack** — that,
  not the robe alone, is the species' visual signature.
- **Feet**: the four-figure reference shows small dark feet emerging bare
  beneath the hem; the off-world individual shows wrapped/booted feet. Both
  attested.
- **Stature must read as SHORT and WIDE, not merely scaled-down.** In the
  four-figure reference the robes reach the floor and the body is roughly as
  wide as it is tall from waist down — a bell shape. The taller-individuals
  image confirms the lore's "some Jawas were significantly taller" and shows
  such individuals keeping exactly the same silhouette at larger scale, so a
  tall Jawa is not a differently-proportioned Jawa.

**donor_current_sprite.png is very weak evidence.** The only Jawa-specific art in
this repo's `StarWarsRaces` mod texture tree is
`SWX/Pawn/HeadAttachments/bigeyes/jawaeyes_yellow.png` (copied here) plus
sibling `jawaeyes_red.png`, `bigeyes*.png` and
`RimMandrakeSW/Jawa/jawaeyes_glow.png` — i.e. **an eye-glow overlay only**. There
is no Jawa head sprite, no robe/cowl sprite and no body art on disk at all: the
shipped Jawa is a vanilla humanlike head with a glowing-eyes attachment. The
copied file is a single small yellow blob and cannot validate or invalidate
anything above; it documents that the Jawa's whole authored appearance —
the hood with a black void interior, the hem grammar, the crossed bandoliers —
**does not exist as art yet.** For the player's own species that is the largest
art gap in the roster.

## Must show
- [ ] Hood interior reads as a flat, featureless, opaque black void — no visible face, muzzle, chin or nose, only the two glowing eyes
- [ ] Eyes are ovoid, close-set, no visible pupil or sclera structure, glowing yellow OR red-orange (either is correct)
- [ ] Robe colour falls in the warm-brown to cold-dusty-grey-brown range, not bright saturated orange
- [ ] Cowl is a soft fabric hood pulled forward over the brow, not a rigid cone
- [ ] Hands are always covered — leather gloves or frayed cloth mitts — never bare skin
- [ ] Gear worn as crossed bandoliers over the chest with pouches/tools, not a single belt

## Engine limits
none known — the missing hood/robe/bandolier art is a content gap (no sprite exists yet),
not a rendering constraint.

## Source URLs
- https://starwars.fandom.com/wiki/Jawa (Wookieepedia article; direct page HTML is
  Cloudflare-walled — wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Jawa&format=json&prop=wikitext`,
  42,432 chars, 2026-09-15)
- https://static.wikia.nocookie.net/starwars/images/b/bd/Jawas-SWApp.png (File:Jawas-SWApp.png → wookieepedia_four_jawas_reference.jpg)
- https://static.wikia.nocookie.net/starwars/images/1/1b/Jawa_scavengers-AA.jpg (File:Jawa_scavengers-AA.jpg → wookieepedia_alien_archive_illustration.jpg)
- https://static.wikia.nocookie.net/starwars/images/4/49/OffworldJawa-AG.png (File:OffworldJawa-AG.png → wookieepedia_offworld_jawa_mandalorian.jpg)
- https://static.wikia.nocookie.net/starwars/images/0/09/Jumbo_Jawas.png (File:Jumbo_Jawas.png → wookieepedia_tall_jawas.jpg)
- NOT fetched this pass: https://www.starwars.com/databank/jawa (official Databank; the
  Databank route worked for the anooba entry and should be tried in a later pass
  for a second independent text source).

## Candidate images
- `wookieepedia_four_jawas_reference.jpg` — the Wookieepedia infobox image
  (File:Jawas-SWApp.png): four Jawas standing together on a transparent
  background, photographic-quality costume render. **The single best reference in
  this entry** — it settles robe brown, the black hood void, yellow eye lamps,
  leather gloves, bare feet and the bell silhouette all at once, and shows four
  different hood drapes.
- `wookieepedia_alien_archive_illustration.jpg` — a stylized Alien Archive plate
  of five Jawas stripping a crate under Tatooine's twin suns. Illustration, so
  its hot rust-orange palette is graphic licence — but independently confirms
  crossed bandoliers, pouch load-out, hand tools, glowing yellow paired eyes and
  the cowl silhouette.
- `wookieepedia_offworld_jawa_mandalorian.jpg` — a full-body in-show off-world
  Jawa (Mandalorian era): **the contrasting palette case** — cold dusty
  grey-brown robe, RED eyes, frayed cloth mitts, and the clearest view of the
  crossed-bandolier gear rig (three-lens device, blade, canteen).
- `wookieepedia_tall_jawas.jpg` — taller-than-normal individuals, confirming the
  lore's abnormal-height Jawas keep the identical silhouette at larger scale.

## ruling
(empty — owner has not reviewed this race yet)
