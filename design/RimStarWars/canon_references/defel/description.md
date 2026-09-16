# Defel

**defName**: `RSW_RimMandrakeDefel` (verified in
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`, line 391 —
that file is GENERATED, do not hand-edit). Matrix placement `Pirate: S` — some, among
the pirates, which suits a species whose canon jobs are **mercenary** and **fortune
hunter**.

🔴 **The shipped def has no description at all.** Its `<description>` element contains
a single period: `<description>.</description>`. Every other species in the file
carries real prose. See "Repo def versus canon".

## Sourced text (Wookieepedia)

Two continuities, and both are needed here — the **canon** article is very thin
(4,585 chars of wikitext and flagged `{{Update}}`) while **`Defel/Legends`** carries
almost all of the substance. Both are marked below.

### Canon

Defels are a **sentient species whose members had the ability to become almost
invisible by bending light around themselves**. The infobox's only listed distinction
is **"Ability to absorb visible light."** Hair colour **brown**; eye colour **black**
or **red**. Skin colour, height, mass, lifespan, origin, habitat, diet and language
are all **blank in the canon infobox** — recorded as absent, not guessed.

Body plan: **brown fur, two red eyes, sharp teeth, and two elongated ears that were
pointed upwards**. Two sexes, male and female. **Defels had the ability to bend light
around themselves to become practically invisible. Elderly Defel, however, tended to
lose that ability.** They had **a good sense of smell, being able to scent at least a
molecule of blood from six miles away**. **They could feast on sentient species, but
preferred the meat liquified.**

Two quotes are worth having, because they say how other characters *perceive* a Defel
— which is a design constraint, not flavour:

> "Passive-aggressive apex predator. Wonderful." — Chelli Aphra

> "Got that creepy shadow aura trick going on with the fur." — Chelli Aphra, on Glahst
> Ombra's hiding ability

Named individuals: **Arleil Schous**, a male Defel fortune hunter, a patron of
Chalmun's Spaceport Cantina in 1 BBY when Luke Skywalker and Obi-Wan Kenobi arrived
(his is the canon infobox image, and the species' first appearance — *A New Hope*);
**Glahst Ombra**, a female Defel mercenary hired by the Son-tuul Pride, killed **and
skinned** by Imperial Lieutenant-Inspector Magna Tolvan. The wiki files the species
under **Category:Canine sentient species**.

### Legends (`Defel/Legends`) — where the mechanism is explained

**Colloquially known as "Wraiths."** Native to the Outer Rim planet **Af'El**, they
**appeared to most other species as shadows, re-enforcing the misconception that they
were chameleon-like beings or "living shadows."**

🔑 **The whole appearance is a consequence of their star.** Af'El is a **large,
high-gravity** world orbiting the **ultraviolet supergiant Ka'Dedus**. Af'El has **no
ozone layer**, so ultraviolet light passes freely to the surface, while other
wavelengths are **mostly blocked by heavy gases in the atmosphere**. Therefore **all
lifeforms on Af'El see in ultraviolet ranges but are blinded by all but the dimmest
light in other wavelengths.** Defels **normally wore a visor when they left Af'El** and
expected daylight at their destination. **Compared to other species they could see
exceptionally well in the dark.**

🔑 **They are not actually black — they are brightly coloured in a band you cannot
see.** "Though they were nearly invisible in normal light, Defel were actually
**colorful** beings. Viewed under **ultraviolet** light, their **fur appeared in colors
ranging from yellow to blue**. Their **snouts appeared green, with orange, gill-like
slits at the base of their jawlines.**" The Legends infobox states this as skin colour
**"Green (exposed skin at snout) and orange (at jawline) in ultraviolet light"** and
hair colour **"Blue to yellow in ultraviolet light, black to dark brown in visible
light."**

**Size (Legends only): 1–1.5 meters, averaging 1.3 meters tall and NEARLY AS WIDE** —
"short, stocky beings." **Lifespan 90 years.** Distinctions: **absorption of visible
light, light-blindness, claws.** **Elderly Defel lost their ability to absorb light,
fading to a dull dark brown under visible light** — so the canon "elderly lose it"
line has a specific visual consequence.

The Legends quote makes the concealment concrete and mechanical:

> "There was no danger. Humans need movement to see. Not-moving shadows are of no
> concern." — an unidentified Defel

## Visual brief

🔴 **This species has TWO appearances and the five references split cleanly between
them. Rendering one and calling it the Defel is the failure mode.** They look almost
nothing alike, and the difference is not "lighter or darker fur" — it is whether the
figure has *internal detail at all*.

### Mode 1 — the wraith. This is the one that is easy to get wrong.

`wookieepedia_infobox_arleil_schous.jpg` (the **canon infobox image**, Arleil Schous in
the Mos Eisley cantina) is the purest reference and it shows something a text prompt
will not produce from the phrase "brown fur":

- **The figure is a featureless black void.** The fur is so dark that **all internal
  detail is gone** — no fur strands, no muscle, no shading, no colour. Light does not
  fall on it and roll off; it goes in and does not come back. Against a dim wall it
  reads as **a hole in the image**.
- **The only things you can see are two glowing RED eyes and a mouth of bared, sharp,
  pale fangs.** Nothing else in the head resolves. That is the entire face.
- **The silhouette is what identifies it**: two tall, pointed, upward ears notched
  against the background, and a broad shaggy head outline.
- **A faint warm rim-light along one edge is the only evidence the fur is shaggy at
  all** — and it matters, because it is the one cue that this is a hairy animal and not
  a shadow. Keep a rim, lose the interior.

⚠️ **Do NOT render this as "dark grey fur" or "black fur with visible strands."** Fur
you can see the strands of is the opposite of the effect. The canon text is "absorb
visible light" and the image obeys it literally.

`wookieepedia_galaxy_guide_4.jpg` is the single most useful image in the directory
because **it shows both modes on one body at once.** It is a black-and-white ink plate
in which the figure's **left side is drawn as a solid black silhouette with zero
internal line work**, while its **right side is drawn as ordinary shaggy fur with full
hatching, visible strands, and a lit muzzle**. Whether or not the artist meant it as
a depiction of partial absorption, it is the clearest available statement of what the
two states look like on the same anatomy, and it is the image to hand anyone drawing
this species.

`wookieepedia_glahst_ombra.jpg` (the canon female mercenary, from *Doctor Aphra*) is the
third data point and it **does not agree with pure black**: the face is a **dark
desaturated teal / blue-black**, not neutral, with **glowing orange-red eyes** and a
wide mouth of **long white triangular fangs**, under a hood. So in comic rendering the
absorbed state is given a **cool blue-green cast** rather than being pure black. If a
single palette must be chosen for the wraith state, **very dark desaturated
blue-green-black with a red-orange eye glow** covers both this and the cantina still;
pure neutral black covers only the still.

### Mode 2 — seen properly. A shaggy canine biped.

`wookieepedia_ultimate_alien_anthology.jpg` and the right half of the Galaxy Guide
plate agree closely, and `wookieepedia_male_female_pair.jpg` (a comic panel with a
male and a female together) is consistent with them:

- **Warm mid-to-dark brown shaggy fur** over the whole body, longer and tufted at the
  shoulders, elbows, cheeks and ears.
- **A canine/bat head**: a short wrinkled muzzle, a **broad mouth of triangular fangs**,
  and **two tall pointed ears** carried erect and tufted at the tips — the ears are the
  species' most reliable silhouette feature and are present in every single image.
- **Long arms reaching to or below the knee**, ending in **large hooked claws** —
  cream/bone coloured and disproportionately long, on both hands and feet. Claws are a
  listed Legends distinction and the images make them prominent.
- **A stooped, hunched, forward-leaning posture** with the head carried low — never
  upright and human.
- ⚠️ **Confirmation of the visor**: the Ultimate Alien Anthology figure wears an
  **orange-lensed band across the eyes**, which is exactly the Legends detail that a
  Defel offworld in daylight wears a visor. Note that this means **the reference image
  hides the eyes** — its eye colour tells you nothing.
- The Anthology figure also wears white shoulder plates, a chest harness with a gold
  medallion and a belt with pouches; the Galaxy Guide figure wears a bandolier. Those
  are individual kit, not species traits.
- **Stockiness**: the Legends text says 1.3 m **and nearly as wide**, but ⚠️ **none of
  the images render a Defel as notably wide.** The Anthology and Galaxy Guide figures
  are lean, long-limbed and gaunt. This is a genuine prose-versus-image disagreement;
  on the library's rule, **trust the images on appearance** — draw a lean, long-armed,
  hunched biped, and treat "nearly as wide" as a stat-block artifact.
- `wookieepedia_male_female_pair.jpg` renders both sexes as **greyish-brown furred
  canine humanoids with red eyes**, the female distinguished only by gold jewellery.
  🔑 **No anatomical sexual dimorphism is depicted or described anywhere** — unlike the
  Chagrian or Devaronian, there is nothing to build a male/female art split around.
  Note also the small **dark silhouetted figure standing in the doorway** in the
  background of that panel, which reads as a Defel in the wraith state and is a nice
  demonstration of the two modes appearing in one frame.

**The ultraviolet colouring is a fact you can use, and no image shows it.** No
reference here depicts a Defel under UV — yellow-to-blue fur, green snout, orange
jawline slits are **text-only**. If the owner ever wants a Defel that is visibly
*interesting* rather than a black smear, that palette is canonical and unused.

**`donor_current_sprite.png` is the weakest donor art in this library so far.** It is
`SWX/Pawn/HeadAttachments/defel/teeth_south.png` and it is, in its entirety, **four
tiny teardrop-shaped fangs** on a transparent field — a small greyscale overlay a few
pixels across, sitting where a mouth would be. There is a matching `teeth_east.png`
and **that is the complete inventory of Defel-specific art in the repo** — no head, no
body, no fur, no ears, no claws, no `_north`. So the mod currently represents a Defel
as **an otherwise ordinary RimWorld humanoid with a dog nose, pointed ears, fur skin
and four little teeth**, assembled from generic genes. Everything in this brief —
the void-black wraith state, the hunched long-armed posture, the hooked claws, the
tufted erect ears, the visor — is **unrepresented**. It is not weak evidence about
appearance so much as evidence that the appearance has not been attempted.

## Repo def versus canon

🔴 **The species' single defining trait is entirely absent from the def.** The infobox's
only listed distinction, the first clause of the article, the reason the species has a
nickname, and the thing every quote about them refers to, is **bending/absorbing
visible light to become practically invisible**. `RSW_RimMandrakeDefel` contains **no
invisibility, concealment, stealth, light or shadow gene of any kind.** What it does
carry is the incidental trim: `RSW_Face_pointyteeth`, `RSW_Nose_Dog`, `Ears_Pointed`,
`Eyes_Red`, `Furskin`. A player meeting this xenotype has no way to learn the species
is a wraith. This is the finding to act on.

🔴 **The def ships with no description.** `<description>.</description>` — one period.
Whatever generated it had nothing to write, and unlike Chagrian, Devaronian, Ewok and
Falleen (all of which carry real prose) a player reading the xenotype in-game is told
nothing at all. The canon first sentence would fix it outright.

⚠️ **`AptitudeTerrible_Intellectual` is unsupported by anything in either continuity.**
Canon Defels are a **mercenary** and a **fortune hunter**; they are called an "apex
predator" and hold a conversation on-page; Legends gives them a language, a homeworld
astronomy, and offworld travel habits. Nothing in either article suggests low
intelligence. `AptitudeTerrible_Medicine` is likewise unsourced. These read as flavour
invented to balance a stealth species that was then never given the stealth.

⚠️ **Hair colour genes include reddish tones that canon does not attest.**
`Hair_DarkSaturatedReddish` and `Hair_DarkReddish` sit alongside `Hair_MidBlack` and
`Hair_DarkBlack`. Canon fur is **brown**; Legends is **black to dark brown in visible
light**. The two black genes are right, brown is missing, and reddish is invented.
(`Hair_BaldOnly` is also present alongside them, which with `Furskin` is presumably how
fur tint is driven — noted, not called an error.)

⚠️ **No scent gene.** "Able to scent at least a molecule of blood from six miles away"
is a specific, striking canon ability with an obvious RimWorld analogue, and there is
nothing for it.

⚠️ **`Body_Standard` versus "nearly as wide."** `RSW_BodySizeGene_small` is well
matched to 1–1.5 m, but Legends explicitly describes a **stocky** build. Note the
images do not support the stockiness either (see visual brief), so this is a low-
confidence finding — flagged for completeness rather than as a correction.

**Well matched, recorded so a later pass does not undo them**: `BS_Diet_Carnivore` and
`RSW_statgene_predator` (canon: feast on sentient species, prefer meat liquified,
"apex predator"), `StrongStomach` / `RobustDigestion` (same), `DarkVision` (canon: see
exceptionally well in the dark), `Nearsighted` (a plausible stand-in for the canonical
**light-blindness**, though the real trait is wavelength-specific rather than
distance-based), `Eyes_Red`, `Ears_Pointed`, `Furskin`, `RSW_Nose_Dog`,
`RSW_Face_pointyteeth` and `AptitudeStrong_Melee` (claws) — all supported.

## Source URLs

- https://starwars.fandom.com/wiki/Defel — canon article. Direct page HTML is
  Cloudflare-walled; wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Defel&format=json&prop=wikitext`
  (4,585 chars, 2026-09-15). ⚠️ **Thin and flagged `{{Update|Obi-Wan 2}}` by the wiki.**
- https://starwars.fandom.com/wiki/Defel/Legends — the Legends article, and the source
  of the Af'El astronomy, the ultraviolet colouring, the size, the lifespan and the
  visor. Pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Defel/Legends&format=json&prop=wikitext`
  (12,768 chars, 2026-09-15). It carries a `{{Citation}}` maintenance banner.
- https://static.wikia.nocookie.net/starwars/images/b/b6/ArleilSchous.jpg —
  File:ArleilSchous.jpg, the **canon infobox image** → `wookieepedia_infobox_arleil_schous.jpg`
- https://static.wikia.nocookie.net/starwars/images/3/3c/Defel_GG4.jpg —
  File:Defel_GG4.jpg, *Galaxy Guide 4: Alien Races* plate → `wookieepedia_galaxy_guide_4.jpg`
- https://static.wikia.nocookie.net/starwars/images/b/b1/Defel-UAA.png —
  File:Defel-UAA.png, *Ultimate Alien Anthology*, the **Legends infobox image** →
  `wookieepedia_ultimate_alien_anthology.jpg`
- https://static.wikia.nocookie.net/starwars/images/c/cf/GlahstOmera-2016DoctorAphra15.png —
  File:GlahstOmera-2016DoctorAphra15.png, *Doctor Aphra* (2016) 15 →
  `wookieepedia_glahst_ombra.jpg`
- https://static.wikia.nocookie.net/starwars/images/d/d8/Shoto_Eyefire_and_consort.png —
  File:Shoto_Eyefire_and_consort.png, a male and female Defel →
  `wookieepedia_male_female_pair.jpg`
- Not fetched this pass: no `https://www.starwars.com/databank/defel` page is cited by
  the article; the canon infobox's citations are to *Star Wars: Absolutely Everything
  You Need to Know*, *A New Hope*, and IDW/Marvel comics, all print.
- **Unsourced in canon, recorded as absent rather than guessed**: height, mass,
  lifespan, origin, habitat, diet, language, skin colour. *(Legends supplies height
  1–1.5 m, lifespan 90 years, origin Af'El, language Defel — marked as Legends
  throughout, never presented as canon.)*

## Candidate images

- `wookieepedia_infobox_arleil_schous.jpg` — **the reference of record for the wraith
  state.** The canon infobox image: Arleil Schous in the cantina, a featureless black
  shape with two glowing red eyes and bared pale fangs, with a single warm rim-light
  edge betraying shaggy fur. This is the appearance the species is *for*.
- `wookieepedia_galaxy_guide_4.jpg` — **the most useful image here.** A B&W ink plate
  showing one body with the left side rendered as a solid black void and the right side
  as fully-hatched shaggy fur: both modes, same anatomy, one frame. Also the clearest
  read on the hooked claws, the fanged muzzle, the erect tufted ears and the hunched
  long-armed posture.
- `wookieepedia_ultimate_alien_anthology.jpg` — the **Legends infobox image**: a
  full-body brown-furred Defel in kit. Best reference for fur colour, limb proportion
  and claw shape, and the only image confirming **the visor**. ⚠️ Because the visor
  covers the eyes, this image is **not** evidence about eye colour.
- `wookieepedia_glahst_ombra.jpg` — the canon female mercenary from *Doctor Aphra*.
  Comic rendering, so treat line and palette as the artist's; its value is showing the
  absorbed state as **dark blue-green-black with an orange-red eye glow** rather than
  neutral black, and confirming the long white fangs.
- `wookieepedia_male_female_pair.jpg` — a comic panel with a male and a female Defel
  together, plus a wraith-state Defel silhouetted in the doorway behind them. Kept
  because it establishes that **no anatomical dimorphism is depicted**, and because it
  shows both modes in one panel.
- `donor_current_sprite.png` — the repo's own art, and **weak evidence**:
  `SWX/Pawn/HeadAttachments/defel/teeth_south.png` is four tiny greyscale fangs and,
  with its `_east` sibling, is the complete inventory of Defel art on disk. Documents
  that the appearance has not been authored rather than telling you anything about it.

## ruling

(empty — owner has not reviewed this race yet)
