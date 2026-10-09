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

The current (canon) article body does **not** mention domestication by Jawas
or Tusken Raiders. The **Legends** article does say Tusken Raiders domesticated
anoobas as pets and guard animals, and calls the Citadel pack "striped"
(https://starwars.fandom.com/wiki/Anooba/Legends). The article's actual
domestication examples are all non-Tatooine-native individuals (Embo, a
Kyuzo bounty hunter).

## Visual brief
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."** The Clone Wars animated frame (`wookieepedia_citadel.jpg`) and the inked Alien Archive infobox illustration (`wookieepedia_infobox.jpg`) were deleted. No live-action or photoreal anooba exists on film; the only REAL physical depiction is the mounted anooba head prop at Dok-Ondar's Den of Antiquities, Star Wars: Galaxy's Edge (`wookieepedia_galaxysedge_prop.jpg`). The full-body anatomy reference is the painted Star Wars Bestiary plate (`wookieepedia_bestiary.jpg`).

What the realistic prop shows (head and neck only):
- **Skin:** bare, deeply wrinkled, leathery pink-to-flesh-brown skin over the muzzle, jaw and throat, folded in heavy creases down the neck — NOT a furred face.
- **Hair:** a coarse pale grey-white shaggy mane on the crown and back of the head/neck only.
- **Mouth:** long open jaw with a heavy, protruding lower jaw, ragged lips and many uneven yellowed fangs.
- **Eyes:** small, deep-set, dark, under a heavy wrinkled brow.

🔴 **The realistic prop and the illustrations DISAGREE, loudly.** The Bestiary painting (and the deleted animated/illustrated images) show a furred hyena-like beast with blue-grey coat and tiger-like dark stripes; the physical prop shows a bare, wrinkled, pink-brown skinned head with only a pale mane. Per the owner's ruling the realistic look wins where they conflict: render the face, muzzle and neck as bare wrinkled leathery skin with a pale shaggy mane, and treat the striped grey coat as belonging to the body (which no realistic source shows). Body anatomy comes from the Bestiary plate:
- **Large, erect, pointed ears** with pink/red-toned interior skin.
- **Spiky dorsal mane** of longer fur from the skull down the spine.
- **Long, thin, low-carried or curled tail**, rat- or lizard-like, not a canine brush.
- **Sloped hyena posture**: front legs longer and heavier than the hind legs.
- **Prominent lower jaw** with a chin tusk and visible fangs.

**donor_current_sprite.png is weak evidence**: it is the ONLY anooba art
present on disk in this repo's SWBestiary mod, and it is a Dessicated
(corpse) variant only — there is no live/default sprite for RSW_Anooba on
disk at all right now. A desiccated corpse pose cannot show fur color, stripe
pattern, ear shape, or live posture reliably, so it should not be used to
validate or invalidate any of the canon findings above; it mainly documents
that this creature's live sprite still needs to be authored.

## Must show
*Rewritten 2026-10-09 to the canon_check leniency lesson (`Transient/canon_check_leniency_2026-10-09.md`): body plan, colour layout and a negative, each checkable on a 256px sprite. Grounded in the Galaxy's Edge prop (face/neck, realistic look wins per the 2026-10-08 owner ruling in the visual brief) and the Bestiary plate (body anatomy).*
- [ ] BODY PLAN: a canine-like quadruped in a sloped hyena stance: front legs longer and heavier than the hind legs so the back slopes down to the rump; a long thin rat- or lizard-like tail carried low or curled, not a canine brush
- [ ] COLOUR LAYOUT: muzzle, jaw, throat and neck are bare, deeply wrinkled, leathery pink-to-flesh-brown skin folded in heavy creases (not a furred face); a coarse pale grey-white shaggy mane on the crown, running down the spine as a spiky dorsal ridge; the body coat (shown only in the Bestiary plate) grey with darker stripes
- [ ] Large, erect, pointed ears with pink/red-toned interior skin
- [ ] Heavy protruding lower jaw with many uneven yellowed fangs and a chin tusk jutting from it
- [ ] Small, deep-set, dark eyes under a heavy wrinkled brow
- [ ] Realistic rendering: natural wrinkled skin and coarse hair texture and lighting, no outlines, no cartoon shading (owner ruling 2026-10-08: "That's realistic, not these cartoon versions you keep using")
- [ ] NEGATIVE: not a dog, wolf or plain hyena (no furred face, no bushy tail, no level back); not the blue-grey cartoon of the deleted animated frame

## Engine limits
none known

## Source URLs
- https://starwars.fandom.com/wiki/Anooba (Wookieepedia article; direct page HTML
  is Cloudflare-walled — text pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Anooba&format=json&prop=wikitext`)
- https://static.wikia.nocookie.net/starwars/images/3/34/Anooba-Bestiary.jpg (bestiary painting, saved as wookieepedia_bestiary.jpg)
- https://www.starwars.com/databank/anooba (official Databank text, fetched successfully; no image URL was present in the fetched markup)
- Search snippets only, not directly fetched/verified this pass:
  https://www.swgbeasts.com/pets/Anooba (Star Wars Galaxies beast page),
  https://thecompletedog.fandom.com/wiki/Anooba, https://aliens.fandom.com/wiki/Anooba

## Candidate images
- `wookieepedia_galaxysedge_prop.jpg` — REAL physical prop: mounted anooba head at Dok-Ondar's Den of Antiquities, Star Wars: Galaxy's Edge (Traveler's Guide to Batuu); file `Anooba TGTB.jpg` — https://static.wikia.nocookie.net/starwars/images/1/14/Anooba_TGTB.jpg/revision/latest?cb=20211204175440
- `wookieepedia_bestiary.jpg` — painted Star Wars Bestiary, Vol. 1 plate (illustration, not animation): full-body striped blue-grey anooba, the only full-anatomy canon reference; file `Anooba-Bestiary.jpg` — https://static.wikia.nocookie.net/starwars/images/3/34/Anooba-Bestiary.jpg/revision/latest?cb=20241106025626
- `donor_current_sprite.png` — our own SWBestiary desiccated-corpse sprite; weak evidence (see Visual brief)

## ruling
(empty — owner has not reviewed this creature yet)
