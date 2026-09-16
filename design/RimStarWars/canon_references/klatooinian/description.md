# Klatooinian

**defName**: `RSW_RimMandrakeKlatoonian` (`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Assigned `Jawa_HuttCartel: A` — abundant, one of the Cartel's two visual mainstays
alongside the Hutts themselves.

⚠️ **Spelling: the repo's defName and texture folder say "Klatoonian"
(`RSW_RimMandrakeKlatoonian`, `SWX/Pawn/HeadAttachments/klatoonian/`), but the
canonical Star Wars spelling is "Klatooinian"** — two `o`s, then `i`. This
directory uses the canonical spelling; the defName is cited as-is above and must
NOT be renamed ahead of `NAMING_SCHEME_EXECUTION_1` (project CLAUDE.md: old names
migrate under that item, never opportunistically).

## Sourced text (Wookieepedia)
Klatooinians are a sentient **humanoid** species from the planet **Klatooine** in
the Outer Rim Territories. Infobox: skin colour **green to brown**; habitat
**deserts and wastelands**; distinctions "**imposing brows**", "**toothy
underbites**". No height, mass, lifespan or eye colour is given in the infobox —
🔴 **do not supply a Klatooinian height from anywhere; the canon article does not
have one.**

Klatooinians were common throughout the galaxy. They were **distinguishable
through their prominent brows and visible teeth**. Klatooinians possessed **a
strong build, which made them useful laborers**. Their skin colour ranged from
**green to brown**, and they had **green blood**. Their natural habitat was desert
or wasteland.

**Unusual abilities.** The canon article is short and gives exactly one
non-obvious trait: 🔑 **Klatooinians could also be Force-sensitive.** Green blood
is the only other physiological distinctive. There is no attested special sense,
resistance or regeneration — do not invent one to fill the entry out. (Their
famous cultural fact — indentured service to the Hutts — is not in the body text
of the article as fetched and is therefore NOT recorded here as canon; see the
Source URLs note.)

## Visual brief
The three images agree tightly, which is unusual and useful: this is a species
where the prose and the pictures do not fight.

- **Colour: a desaturated grey-green to olive**, with darker mottling in the
  creases and a slightly warmer, browner cast on the high points of the face. The
  infobox's "green to brown" is honest, but the images sit firmly toward the
  **grey-green** end rather than brown, and the saturation is low — a mud-green,
  not a bright green.
- 🔑 **The brow is the feature.** A heavy bony shelf runs straight across above the
  eyes and projects forward far enough to shadow them completely. The infobox's
  "imposing brows" is exactly right and should be pushed rather than softened: at
  small sizes the brow shelf is what distinguishes a Klatooinian from a generic
  alien tough.
- 🔑 **The underbite is the second feature, and it is a specific shape.** The lower
  jaw juts forward past the upper, and **two small tusk-like teeth are visible at
  the corners of the mouth even at rest** — pointing up, not down. This is the
  "toothy underbite" and it is always visible.
- **Deep jowl folds run along the jaw line** from below the ear to the chin, and the
  whole face is heavily wrinkled and creased — a jowly, pugnacious, dog- or
  pug-like arrangement. The muzzle region is short, broad and slightly upturned.
- **Small, dark, deep-set eyes**, lost under the brow shelf.
- **Bald cranium** — none of the three individuals has hair; the reference wears a
  knitted cap, which reads as clothing, not hair.
- **The body is fully, unremarkably humanoid** and the build is thickset but not
  monstrous — "strong build" means a heavy labourer, not a giant. Proportions in
  all three images are within human range.
- **Dress is ordinary spacer/labourer workwear**: in the reference image, a pale
  grey-white long-sleeved tunic, a hood/cowl bunched at the neck, a shoulder
  bandolier with a holster pouch, dark trousers and soft boots. The live-action
  raider image shows the same register — layered desert practicality. **A
  Klatooinian should read as a person in workwear with a heavy-browed, undershot,
  jowly grey-green head.**
- The **live-action raider** and the **Don Klatoo** images independently confirm the
  brow shelf, the underbite tusks and the jowl folds, so all three are species
  traits rather than one costume's choices.

**donor_current_sprite.png is weak evidence.** The copied file is
`SWX/Pawn/HeadAttachments/klatoonian/Jowls_south.png`: a pale chevron of jowl
lines, and nothing else. **There is no Klatooinian head sprite on disk** —
`SWX/Pawn/HeadType/` has no `klatoonian` directory — so the species is a vanilla
RimWorld head with overlays. Verified from the xenotype's gene list, what IS wired:
`RSW_Face_jowls` (this file), `Body_Hulk`, `Hair_BaldOnly`,
`Outland_Skin_PaleBrown`, `RSW_Skin_PaleOrange` and `RSW_Skin_DarkGreen`. So a
bald, hulking, green-or-pale-brown pawn with jowl lines lands. 🔴 **What no file on
disk supplies: the imposing brow shelf and the toothy underbite — i.e. both of the
two features the infobox names as the species' distinctions.** Note also that
`RSW_Nose_Dog` and `RSW_Nose_SmallPig` textures exist in the same
`klatoonian/` folder and would give the short upturned muzzle, but the Klatooinian
xenotype's own gene list does not include them.

## Must show
- [ ] Skin reads desaturated grey-green to olive (a mud-green, not bright green), with darker mottling in the creases
- [ ] Heavy bony brow shelf runs straight across above the eyes and projects forward far enough to shadow them completely
- [ ] Underbite: the lower jaw juts forward past the upper, with two small tusk-like teeth visible at the mouth corners, pointing up
- [ ] Deep jowl folds run along the jaw line from below the ear to the chin
- [ ] Small, dark, deep-set eyes lost under the brow shelf
- [ ] Bald cranium — no hair on any of the three sourced individuals

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Klatooinian (Wookieepedia article; direct page HTML
  is Cloudflare-walled — wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Klatooinian&format=json&prop=wikitext`,
  18,691 chars, 2026-09-15). ⚠️ This is a **short article** — the fetched body text
  for biology is a single paragraph, which is why this entry carries fewer sourced
  facts than the Rodian or Trandoshan entries. A later pass should try
  https://starwars.fandom.com/wiki/Klatooinian/Legends for the fuller Legends
  treatment (indenture to the Hutts, subspecies) and label anything from it
  explicitly as Legends.
- https://static.wikia.nocookie.net/starwars/images/0/0c/Klatooinian_Barada_Databank.png (File:Klatooinian_Barada_Databank.png, the infobox image → wookieepedia_infobox_barada.jpg)
- https://static.wikia.nocookie.net/starwars/images/8/87/Klatooinian_drinking_Spotchka.png (File:Klatooinian_drinking_Spotchka.png → wookieepedia_raider_liveaction.jpg)
- https://static.wikia.nocookie.net/starwars/images/2/2c/Don-Klatoo.png (File:Don-Klatoo.png → wookieepedia_don_klatoo.jpg)
- NOT fetched this pass: https://www.starwars.com/databank/klatooinian (official Databank).

## Candidate images
- `wookieepedia_infobox_barada.jpg` — **the reference of record.** The infobox image
  (File:Klatooinian_Barada_Databank.png): a full-body Klatooinian on a transparent
  background, costume-photography fidelity. Settles the desaturated grey-green hue,
  the projecting brow shelf, the undershot jaw with two upward corner tusks, the
  jowl folds, the bald head, and the ordinary tunic/bandolier/boots workwear.
- `wookieepedia_raider_liveaction.jpg` — a live-action Klatooinian raider drinking
  spotchka (Mandalorian era). Independent modern-production confirmation of brow,
  underbite and jowls, and a good example of layered desert dress.
- `wookieepedia_don_klatoo.jpg` — a third individual; useful because it makes the
  brow/underbite/jowl combination three-for-three across different sources and
  media.

## ruling
(empty — owner has not reviewed this race yet)
