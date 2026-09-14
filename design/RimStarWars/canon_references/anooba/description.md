# Anooba

**defName**: `RSW_Anooba` (vendored in this repo's SWBestiary mod)

## Sourced text (Wookieepedia)
Anoobas are a species of vicious, carnivorous canine-like desert mammals found on
Tatooine, Nal Hutta, and throughout the Outer Rim. Quadrupeds reaching up to 2.7
meters in length. Body plan: a pronounced, protruding lower jaw with sharp teeth
and (on larger individuals) a chin tusk that juts from the lower jaw — small
anoobas lack this tusk; long claws and fangs; a long tail; thick patches of fur
running across the spine (a mane/ridge); hind legs noticeably smaller than the
front legs (a sloped, hyena-like stance); capable of a fearsome growl. Coloration
per the infobox is inconsistently sourced across different media: "varying tones
of gray" fur (Alien Archive / Databank), but also attested as black (Galaxy's
Edge fur samples) and blue (a specific Citadel-arc individual, "Citadel Rescue").
Eye color is sourced as blue or yellow depending on individual/source.

Behaviorally, wild anoobas travel in packs of 10–12, hunting by stabbing prey
with the chin tusk and then tearing it apart with claws and fangs. They are
trainable as pets, guard animals, or hunting animals. The bounty hunter Embo
(Kyuzo) domesticated an anooba named Marrok (one of the smaller, tusk-less
individuals) as a working companion during the Clone Wars era, and a later
individual named Keibu in the New Republic era. A pack of "dark anoobas" was
kept by the Phindian Osi Sobeck to hunt escaped prisoners at the Citadel on
Lola Sayu (Star Wars: The Clone Wars, "Citadel Rescue," S3E20, 2011) — one of
these killed Jedi Master Even Piell before Ahsoka Tano Force-pushed it off a
cliff. Sabine Wren later painted an anooba insignia on her Mandalorian armor.
The species concept originated with Terryl Whitlatch for The Phantom Menace as
a possible Tatooine creature, and was redesigned for The Clone Wars by David Le
Merrer; a new anooba (Keibu) has concept art by Aaron McBride for the 2026 film
Star Wars: The Mandalorian and Grogu. No Star Wars: Galaxies-specific detail
was found in this pass (search results reference the SWG beast database but a
direct fetch was not attempted — see Source URLs).

The wiki text does **not** mention domestication specifically by Jawas or
Tusken Raiders in the current article body — a general web search snippet
claimed Tusken Raiders domesticate anoobas, but that line does not appear in
the Wookieepedia wikitext pulled directly via the API, so it should be treated
as unconfirmed/secondary until a primary source is found. The article's actual
domestication examples are all non-Tatooine-native individuals (Embo, a
Kyuzo bounty hunter).

## Visual brief
The three candidate images agree with each other far more strongly, and more
specifically, than the prose summary suggests. All three show:
- **Large, erect, pointed ears** with visibly pink/red-toned interior skin —
  bat-like or donkey-like in proportion, not small hyena ears.
- **A spiky dorsal mane/ridge** of longer fur running from the back of the
  skull down the spine, distinct from the shorter body coat.
- **Tiger-like dark stripes over a blue-grey to grey body coat** — this is the
  single biggest thing the "varying tones of gray" text undersells. Every
  image (concept-art illustration, in-show 3D render, and a separate painted
  bestiary piece) independently shows banded/striped fur, not a flat gray or
  solid color. This is exactly the kind of feature a text-only prompt would
  invent wrong (cf. the Wyyyschokk case this library exists to prevent).
- **A long, thin, low-carried or curled tail**, out of proportion to a stocky
  hyena body — closer to a rat or lizard tail than a canine brush tail.
- **Large forward-set eyes**, yellow/amber in the CGI and bestiary pieces
  (agrees with the "Yellow" eye-color citation more than "Blue").
  Note wookieepedia_infobox.jpg is a hand-painted/illustrated concept-style
  piece (possibly a bestiary-book plate) rather than a film/show frame — treat
  its exact palette as one artist's interpretation, though it agrees closely
  with the separate wookieepedia_bestiary.jpg painting on stripe pattern, ear
  shape, and mane.
- **Sloped hyena posture**: front legs visibly longer/more developed than hind
  legs in all three images, confirming the "smaller hind legs" text detail.
- **Prominent lower jaw and tusk**, visible fangs, in all three.

wookieepedia_citadel.jpg (the in-show CGI frame, a pair of "dark anoobas" from
the Citadel) is the darkest/most desaturated of the three — near-black in low
purple lighting — but even here the dorsal mane spikes, ear shape, and tail
are consistent with the other two images. This is plausibly the "black"
color-cite individual type rather than contradicting the gray/blue-gray
majority.

**donor_current_sprite.png is weak evidence**: it is the ONLY anooba art
present on disk in this repo's SWBestiary mod, and it is a Dessicated
(corpse) variant only — there is no live/default sprite for RSW_Anooba on
disk at all right now. A desiccated corpse pose cannot show fur color, stripe
pattern, ear shape, or live posture reliably, so it should not be used to
validate or invalidate any of the canon findings above; it mainly documents
that this creature's live sprite still needs to be authored.

## Source URLs
- https://starwars.fandom.com/wiki/Anooba (Wookieepedia article; direct page HTML
  is Cloudflare-walled — text pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Anooba&format=json&prop=wikitext`)
- https://static.wikia.nocookie.net/starwars/images/d/df/Anooba.png (infobox image, saved as wookieepedia_infobox.jpg)
- https://static.wikia.nocookie.net/starwars/images/2/2c/Anooba-CR.jpg (Citadel Rescue in-show frame, saved as wookieepedia_citadel.jpg)
- https://static.wikia.nocookie.net/starwars/images/3/34/Anooba-Bestiary.jpg (bestiary painting, saved as wookieepedia_bestiary.jpg)
- https://www.starwars.com/databank/anooba (official Databank text, fetched successfully; no image URL was present in the fetched markup)
- Search snippets only, not directly fetched/verified this pass:
  https://www.swgbeasts.com/pets/Anooba (Star Wars Galaxies beast page),
  https://thecompletedog.fandom.com/wiki/Anooba, https://aliens.fandom.com/wiki/Anooba

## Candidate images
- `wookieepedia_infobox.jpg` — the Wookieepedia infobox portrait: a painted/illustrated
  full-body anooba on a transparent background, mid-snarl, showing striped
  blue-grey coat, spiky dorsal mane, large pink-interior ears, long thin tail,
  chin tusk and fangs, front-heavy hyena stance. From the Anooba infobox image
  (File:Anooba.png) on Wookieepedia.
- `wookieepedia_citadel.jpg` — an in-show CGI frame from The Clone Wars
  "Citadel Rescue" (S3E20), showing a pair of the dark/black Citadel anoobas
  crouched and snarling in low purple night lighting, confirming mane, ear,
  and tail shape from a different (darker) color individual. From
  File:Anooba-CR.jpg on Wookieepedia.
- `wookieepedia_bestiary.jpg` — a separate painted bestiary-style illustration
  (aged-paper background) of an anooba, agreeing closely with the infobox
  piece on stripe pattern, ear shape/color, mane, and posture. From
  File:Anooba-Bestiary.jpg on Wookieepedia.

## ruling
(empty — owner has not reviewed this creature yet)
