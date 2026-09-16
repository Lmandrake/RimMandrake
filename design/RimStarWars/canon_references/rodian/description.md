# Rodian

**defName**: `RSW_RimMandrakeRodian` (`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Assigned `Jawa_HuttCartel: S`, `Jawa_Junkers: S`, `Pirate: R`.

## Sourced text (Wookieepedia)
Rodians are a species of **reptilian humanoids**. Infobox: **height 1.75 meters**;
origin Rodia; habitat swamps; language Rodian. Skin color blue, green, orange,
red, turquoise, yellow; eye color blue, black, green, purple, red. Distinctions:
large and round pupil-less eyes, snouts, pointed ears, antennae, scaled and
usually green skin.

**Unusual abilities — this species is unusually well specified and the abilities
are all sensory.**
- 🔑 **Large pupil-less eyes that could see in the infrared spectrum.** The
  Pantoran Kevmo Zink suspected Rodians and his own people saw different spectra of
  light but was not sure where the divide lay (so the article marks the exact
  boundary as in-universe uncertain — do not sharpen it).
- 🔑 **Twin saucer-like antennae that detected vibrations and twitched atop their
  head.** Vibration sense, distinct from hearing.
- 🔑 **Suction cups.** The Rodian hand featured **five long, dexterous fingers with
  suction cups at the ends**; the pads helped them cope with swamp conditions and
  could be used to climb aquatic vegetation. **Their toes were a lot like their
  fingers: long and tipped by suction cups.**
- 🔑 **Could breathe air saturated with Clouzon-36 without a respirator**, despite
  being oxygen breathers.
- **The hand shape is asymmetric with human ergonomics**: an object designed for a
  Rodian would be uncomfortable for a human to use.

**Appearance.** Slender snouts (said to resemble those of **tapirs**), pointed
ears, and **a ridge of spines cresting their skulls**. Green — but sometimes red,
yellow or turquoise — scales covered their bodies, and their skin had a **rough,
pebbly texture, except on the snout and hands**. They were **cold blooded and had
green blood**. Rodians were **susceptible to vitiligo**. Females were physically
distinguished by their mammary glands, and some — like Greeata Jendowanian — were
capable of growing long tresses. **Rodians smelled rank to humans.**

## Visual brief
The three images agree closely on structure and correct the prose in two specific
places.

- 🔴 **"Pupil-less eyes" plus an eye-colour list of "blue, black, green, purple,
  red" reads as a DARK eye, and that is wrong.** In the full-body reference render
  the eyes are **large, hemispherical, pale iridescent lavender-white domes with a
  faint internal sheen** — they read as frosted glass or opal, lit from within, not
  as dark orbs. The Alien Archive plate independently shows the same pale
  luminous domes. So "purple" here means *pale opalescent violet*, not a dark
  purple eye. This is the single highest-value correction in the entry, because
  the eyes dominate the face at any size.
- **Eye SIZE is the silhouette.** The two eyes together occupy roughly the upper
  half of the face and bulge outward past the skull profile. Anything that draws
  them at humanlike scale loses the species.
- 🔴 **The "antennae" are much less prominent than the text implies, and the
  cranial crest is much more prominent.** The text lists "twin saucer-like
  antennae ... atop their head" and "a ridge of spines cresting their skulls" as
  co-equal, but in the reference render the top of the head carries **a
  conspicuous crest of small backswept fleshy knobs/spines**, while the antennae
  read as **two short, low, blunt nubs at the temples**, roughly level with the
  eyes rather than on the crown. A sprite that puts large saucer-dishes on top of
  the head over-reads the prose.
- **The snout is a smooth tapering cone**, noticeably smoother than the body — the
  "pebbly except on the snout and hands" text is visible: the snout and the backs
  of the hands are matte and fine-grained while the neck, crest and body carry a
  visible bumpy grain.
- **The colour is a mid-to-light yellow-green with darker green mottling**, not a
  flat green: the crest and the sides of the snout go darker, the throat lighter.
- **Ears are small, low, and pointed backward**, easily lost — they are not a
  read-at-a-glance feature and should not be exaggerated.
- **Rodians wear ordinary galactic clothing.** The reference render shows a
  Rodian in a canvas jacket, cargo trousers, boots, gloves, a shoulder harness and
  a rectangular field pack with a slung rifle. There is no species costume: a
  Rodian should read as *a person in workwear with a Rodian head*. The
  female-and-child image confirms the same for civilian dress. This matters for
  RimWorld, where the apparel layer does the work anyway.
- The Alien Archive plate is a stylized illustration (heavier outlines, pushed
  saturation) but agrees on eye scale, eye luminosity, crest, snout taper and the
  suction-tipped digits.

**donor_current_sprite.png is partial evidence, and the composite is better than
the file.** The copied file is
`SWX/Pawn/HeadType/rodian/Male_Rodian_south.png` — a **greyscale mask**, which is
correct for a RimWorld humanlike head (the game tints it from the skin-colour
gene, so its lack of colour is not a defect; the hue findings above belong on the
gene). Its silhouette is a good match: a domed cranium tapering smoothly to a
blunt snout. What the base file lacks is the eyes — it carries only two ordinary
small dots. **In the shipped composite that is compensated for**: the Rodian
xenotype's gene list includes `RSW_Eyes_Big` (a
`HeadAttachments/bigeyes/bigeyes*` overlay), `RSW_Headbone_rodian` (verified to be
`HeadAttachments/rodian/rodian_*.png` — two small temple nubs, i.e. the antennae,
correctly small), `Skin_Green` / `RSW_Skin_DarkGreen`, `Outland_ScaleSkin`,
`Outland_Blood_Green` and `DarkVision` — so large eyes, green scaled skin, green
blood and low-light vision are all already modelled. **What is NOT modelled by any
file on disk: the pale iridescent quality of the eyes, the crest of dorsal
skull-spines, and the suction-cup digits.** (`HeadAttachments/rodian/mohawk_*.png`
exists and is a small tuft, but it is wired to `RSW_Hair_rodian`, a hair gene, not
to the head — it is not the bony crest.)

## Must show
- [ ] Large, hemispherical, pale iridescent lavender-white eyes with a faint internal sheen — not dark orbs; occupy roughly the upper half of the face and bulge outward past the skull profile
- [ ] A conspicuous crest of small, backswept, fleshy knobs/spines atop the head — more prominent than the antennae
- [ ] Two short, low, blunt antenna nubs at the temples, roughly level with the eyes — not large saucer-dishes on the crown
- [ ] A smooth, tapering snout, noticeably smoother than the pebbly-textured body and hands
- [ ] Mid-to-light yellow-green skin with darker green mottling (crest and snout sides darker, throat lighter) — not a flat green
- [ ] Ordinary galactic workwear clothing, no species-specific costume

## Engine limits
none known — the pale iridescent eye quality, the dorsal spine crest, and the suction-cup digits are all missing art, not a pipeline limitation.

## Source URLs
- https://starwars.fandom.com/wiki/Rodian (Wookieepedia article; direct page HTML is
  Cloudflare-walled — wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Rodian&format=json&prop=wikitext`,
  67,886 chars, 2026-09-15)
- https://static.wikia.nocookie.net/starwars/images/d/d3/Rodian_DICE.png (File:Rodian_DICE.png, the infobox image → wookieepedia_infobox_fullbody.jpg)
- https://static.wikia.nocookie.net/starwars/images/1/1d/Rodians-Alien_Archive.jpg (File:Rodians-Alien_Archive.jpg → wookieepedia_alien_archive_illustration.jpg)
- https://static.wikia.nocookie.net/starwars/images/2/2a/MahteeWeeDunn-TCWCE.png (File:MahteeWeeDunn-TCWCE.png → wookieepedia_female_and_child.jpg)
- NOT fetched this pass: https://www.starwars.com/databank/rodians (official Databank).

## Candidate images
- `wookieepedia_infobox_fullbody.jpg` — **the reference of record.** The infobox
  image (File:Rodian_DICE.png): a full-body Rodian in field gear on a transparent
  background, game-render fidelity. Settles the pale iridescent domed eyes, the
  crest of backswept skull knobs, the small temple antenna nubs, the smooth
  tapering snout against pebbly body skin, the yellow-green mottling, and the
  fact that Rodians dress in ordinary workwear.
- `wookieepedia_alien_archive_illustration.jpg` — a stylized Alien Archive plate.
  Independent confirmation of eye scale and luminosity, crest and snout; treat its
  pushed saturation and heavy outlines as illustration style.
- `wookieepedia_female_and_child.jpg` — a female Rodian holding her infant son
  (Mahtee and Wee Dunn). Useful for the juvenile proportions and for confirming
  civilian dress; note the text's female distinction is mammary glands, which
  this image does not make a costume feature.

## ruling
(empty — owner has not reviewed this race yet)
