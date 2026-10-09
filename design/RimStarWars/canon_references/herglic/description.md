# Herglic

**defName**: `RSW_RimMandrakeHerglic` (verified present in
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`, line 778 —
that file is GENERATED, do not hand-edit).
Assigned `Jawa_DeepwaterCompact: S` — some, in the water faction only, which fits: the
Herglic is a **cetacean** (Wookieepedia files it under `Category:Cetacean sentient
species` in both the canon and Legends article).

## Sourced text (Wookieepedia)

**Canon article** (thin — the species has no height, mass, lifespan or origin recorded in
canon; all four are **UNSOURCED**, do not invent them):

> The Herglics were a species of sentient, hulking aliens with **black skin, a wide
> mouth, oily eyes, and a blowhole.**

Canon infobox: skincolor **Black**; distinctions **"Wide mouth; rows of tiny, serrated
teeth; tiny eyes in large head; no neck or chin; blowhole; slick skin; cartilaginous
shoulders."** Body text repeats: *"dark, slick skin, and oily eyes. They had a large head
with no neck or chin and a wide mouth with tiny, serrated teeth. Herglics also had
cartilaginous shoulders and a blowhole on their heads."* Canon behaviour is entirely
circumstantial — Herglics mistreated by the Empire, sheltering in the Coruscant junkyard
Level 1782; one enslaved by Trandoshan slavers and sold to be a gladiator, dying in
training; Gor-kooda working muscle for a Sullustan crime lord on Akiva.

**Legends article** (this is where the numbers and the personality live):

- **Height 1.7–2.2 meters** (`Galaxy of Intrigue`). The only sourced size figure that
  exists for the species. **Mass and lifespan are UNSOURCED in both articles.**
- Skin colour **pale blue** *or* **black** (`Ultimate Alien Anthology`); the text adds
  that some, like Hamar-Chaktak, had **pale pink** skin, and *"a few Herglics, such as …
  Narloch, displayed **white stripes down the sides of their head and arms**."*
- Origin **Giju**; language **Herglese**; distinctions *"aquatic organs; massive size."*
- *"Herglics were large bipeds that appeared to have evolved from water-dwelling mammals.
  Most of the evidence of their waterborne ancestry had been bred out so that, for
  example, **fins and flukes were replaced with arms and legs.** They did, however, still
  **breathe through a blowhole on the top of their heads.**"* The `hauum` sound of a
  Herglic clearing its blowhole is a Herglese word used to preface a significant remark.
- 🔑 **"They were tall and extremely wide, and had smooth, hairless skin."** Width, not
  height, is the defining proportion: *"a Herglic would take up two seats in a restaurant,
  and the majority of doorways required some manoeuvring."*
- **Behaviour, and it is not what the repo def says.** *"Herglics were pleasant and
  peaceful, but they had an **addiction to gambling and games of chance**."* They were
  *"typically easygoing and enjoyed meeting new people and visiting exotic locations,"*
  *"natural explorers and traders"* with *"an inquisitive but practical nature and calm
  persona that helped them interact with other species."* They are also **sensitive about
  their size** and feel self-conscious in Human-scaled facilities.
- **Technologically advanced, early.** They developed **hyperdrive independently**, built
  the Herglic Trade Empire in the Colonies, joined the Republic in 13,000 BBY, and their
  scouts established the Rimma Trade Route in 5500 BBY. Archaeology on their colony worlds
  found *"nonfunctioning machines that appeared to harness gravity"* at a level *"not
  paralleled during the time of the Galactic Empire."* Herglics own casinos at Reaper's
  World and privately run the gamblers' world Tresidiss with Hutt-affiliated criminal
  groups.
- **Unusual abilities: none.** No Force sensitivity, no venom, no natural weapon is
  recorded in either article. The one distinctive organ is the **blowhole**; the one
  distinctive social unit is the **pod ("pakk")**, with family members prefixed by *pod*.
  Do not invent an ability.

🔴 **Repo def contradicts canon on three counts** (report only; the def is generated —
`RSW_RimMandrakeHerglic` carries `AptitudePoor_Social`, `AptitudePoor_Intellectual`,
`AptitudePoor_Medicine`):

1. **`AptitudePoor_Intellectual`** against a species that invented its own hyperdrive,
   ran a trade empire predating the Republic, and left gravity-manipulating machinery
   archaeologists cannot explain.
2. **`AptitudePoor_Social`** against *"pleasant and peaceful … easygoing and enjoyed
   meeting new people … calm persona that helped them interact with other species,"* and
   against a species defined by **trade**.
3. The def's own description — *"can hit like a wrecking ball … thick skin allows them to
   shake off most blunt attacks"* — is **mod flavour with no Wookieepedia support.** No
   source in either article gives the Herglic a combat aptitude or damage resistance.
   `MeleeDamage_Strong` + `Body_Hulk` + `Outland_ThickSkin` are all built on that
   invented line. The sourced trait the def *omits* is the **gambling addiction**, which
   is the species' one canonical vice and would sit naturally on a RimWorld trait.

The def's skin genes (`Skin_InkBlack`, `Skin_SlateGray`) are defensible for canon-black
but drop **pale blue**, **pale pink** and the **white-striped** variant that Legends
records.

## Visual brief
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."**
No live-action or photoreal Herglic exists (searched: Herglic and Herglic/Legends page images, "Images of Herglics" — every file is comic, RPG line art or painted RPG illustration). The three flat-coloured comic/line-art images (`qensog_comic`, `weapon_of_a_jedi`, `alien_encounters_fullbody`) were removed. The target is now the **realistic painted** Legends illustrations: `wookieepedia_legends_essential_atlas_painted.jpg` (Chris Trevas, head and shoulders), `wookieepedia_legends_ultimate_alien_anthology_painted.jpg` (full figure beside a Gran, Gungans and an H'nemthe — gives scale), `wookieepedia_legends_galaxy_of_intrigue_bodyguard.jpg` (full figure, hunched) and `wookieepedia_legends_infobox.jpg` (full figure).

🔴 **Where the painted look disagrees with the deleted comics:** the comics gave a flat slate-lavender / blue-purple skin. **The painted images give glossy, wet-looking near-black to charcoal skin with strong specular highlights** (Trevas, Ultimate Alien Anthology, infobox); only the Galaxy of Intrigue bodyguard is deep plum-purple. Read "black skin" as **glossy charcoal-black with a whale's wet sheen**, with dark purple as an allowed variant — never matte, never a pale lavender cartoon fill.

**Head — the whole species reads from it:**
- **A whale's head worn as a face.** One smooth bulbous dome, widest at the crown, sweeping forward into a **blunt rounded rostrum**; **no neck, no chin** — the skull sits straight on huge shoulders (every image agrees).
- **Mouth: a single wide lipless line** across most of the head's width, the lower lip a heavy rounded pouch beneath it (clearest in the Trevas painting).
- **Eyes small, set low and wide**, near the mouth-line corners, under heavy brow ridges; small nostril pits on the rostrum (Trevas). No external ears.
- ⚠️ **No image shows the blowhole** (canon text: top of the cranium). Textually canon, visually unconfirmed.
- **Markings:** `wookieepedia_legends_narloch_white_stripes.jpg` (graphite illustration, kept for this alone) shows **orca countershading** — black cranium and back, a hard-edged white eye-patch above and behind each eye, white throat and lower jaw. The painted images are uniformly dark. So: **uniform glossy dark is the norm; the orca pattern is a canon variant.**

**Body:**
- **Enormously wide and heavy, barrel-chested, hunched forward** with the head carried low in front of the shoulders (Ultimate Alien Anthology and Galaxy of Intrigue). Legends gives 1.7–2.2 m — in the Anthology group it stands about a head taller than a Gungan but is several times as wide: **a very broad person, not a giant.**
- **Shoulders are huge rounded masses with no clavicle shelf** (canon "cartilaginous shoulders"); **arms thick, tapering to broad paddle hands with short blunt claw-tipped digits** (Galaxy of Intrigue shows clawed fingertips). Digit count is unsettled — do not assert five.
- **Legs short, thick and column-like; feet broad, flat, toeless** (infobox). Skin smooth, hairless, slick.

**Clothing is easy to mistake for anatomy:** the painted figures wear sashes and wraps (infobox: olive sash), boots or shin guards (Galaxy of Intrigue: rust-red boots and bracers; Anthology: dark wraps, belt), an apron and goggles (Trevas). Bare anatomy is head, shoulders, arms and hands.

**`donor_current_sprite.png` is `.../Heads/Herglic/Herglic_south.png` (512×512, RGBA) — a greyscale tint mask,** correct for a RimWorld humanlike head (colour comes from the skin-colour gene). It gets right a large domed neckless head with a low brow lobe, two angled eyes set low and two nostril dots. **Missing: there is no mouth at all** — the wide lipless mouth-line is the species' most-cited feature; no blowhole (`_north`); eyes set high-central rather than wide and low. 🔴 A single-channel tint mask cannot produce the orca countershading, and it cannot produce the glossy specular sheen either — that needs baked shading in the head art. There is **no Herglic body art on disk**, so the "extremely wide" proportion is unrepresented.

## Must show
*Rewritten 2026-10-09 to the canon_check leniency lesson (`Transient/canon_check_leniency_2026-10-09.md`): body plan, colour layout and a negative, each checkable on a 256px sprite. Grounded in the canon/Legends text and the four painted Legends images named in the visual brief.*
- [ ] BODY PLAN: humanoid biped of human-scale height (1.7–2.2 m) but enormously wide: barrel-chested and hunched forward, head carried low in front of huge rounded shoulders, thick arms ending in broad paddle hands, short thick column legs
- [ ] Head: a whale's head worn as a face — one smooth bulbous dome sweeping forward into a blunt rounded rostrum, with no neck and no chin; no external ears
- [ ] Mouth: a wide lipless mouth-line spanning most of the head's width over a heavy rounded lower-lip pouch
- [ ] Eyes small, set low and wide under heavy brows, near the corners of the mouth-line
- [ ] COLOUR LAYOUT: glossy wet-looking charcoal-to-black skin all over (dark purple allowed) with specular highlights — not matte, not pale lavender; the orca pattern (white eye-patches, white throat and jaw) is only a canon variant
- [ ] Realistic rendering: smooth wet whale-like skin texture and natural lighting, no outlines, no cartoon flat colour (owner ruling 2026-10-08: "That's realistic, not these cartoon versions you keep using.")
- [ ] NEGATIVE: not a fat human with a tint (no nose, no chin, no neck, no hair), not a giant twice human height; not a fish or Mon Calamari (no fins, no goggle eyes on the sides)

## Engine limits
- A single-channel tint mask (the current head sprite's approach) cannot express the orca
  eye-patch/white-throat countershading, or the white-striped variant Legends records —
  that pattern needs new art or an additional render node, not a colour/gene change.

## Source URLs
- https://starwars.fandom.com/wiki/Herglic — canon article. Direct HTML is
  Cloudflare-walled; wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Herglic&format=json&prop=wikitext`
  (4,993 chars, 2026-09-15).
- https://starwars.fandom.com/wiki/Herglic/Legends — Legends article, via
  `…&page=Herglic/Legends&…` (14,756 chars, 2026-09-15). **Source of the only height
  figure and of the white-stripe, pale-blue and pale-pink variants.**
- https://static.wikia.nocookie.net/starwars/images/2/27/Narloch1.jpg
  (File:Narloch1.jpg → `wookieepedia_legends_narloch_white_stripes.jpg`)
- https://static.wikia.nocookie.net/starwars/images/f/fa/Herglic.jpg
  (File:Herglic.jpg, Legends infobox → `wookieepedia_legends_infobox.jpg`)
- NOT fetched this pass: `https://www.starwars.com/databank/` has no Herglic species page
  that was attempted.

## Candidate images
- `wookieepedia_legends_essential_atlas_painted.jpg` — **reference of record for the head.** Legends, *The Essential Atlas*, painted by Chris Trevas: glossy black whale head, blunt rostrum, wide lipless mouth over a lip pouch, small low eyes, nostril pits; wears goggles and an apron. File `Herglic TEA Trevas.jpg` — https://static.wikia.nocookie.net/starwars/images/d/de/Herglic_TEA_Trevas.jpg/revision/latest?cb=20130528160255
- `wookieepedia_legends_ultimate_alien_anthology_painted.jpg` — **reference of record for body and scale.** Legends, *Ultimate Alien Anthology*, painted by Jeremy Jarvis: full-figure black Herglic beside a Gran, two Gungans and an H'nemthe. File `Herglic with aliens.jpg` — https://static.wikia.nocookie.net/starwars/images/a/a7/Herglic_with_aliens.jpg/revision/latest?cb=20071029034954
- `wookieepedia_legends_galaxy_of_intrigue_bodyguard.jpg` — Legends, *Galaxy of Intrigue*, painted by Lee Phung: hunched full figure, deep plum-purple skin (the colour variant), clawed paddle hands, rust boots and bracers. File `HerglicBodyguard-GOI.jpg` — https://static.wikia.nocookie.net/starwars/images/a/a3/HerglicBodyguard-GOI.jpg/revision/latest?cb=20100304172817
- `wookieepedia_legends_infobox.jpg` — Legends infobox painting (*Alien Anthology*), full figure: glossy charcoal skin, hunched, flat toeless feet, olive sash. Low resolution (465×550). File `Herglic.jpg` — https://static.wikia.nocookie.net/starwars/images/f/fa/Herglic.jpg/revision/latest
- `wookieepedia_legends_narloch_white_stripes.jpg` — Legends graphite illustration (West End Games), half figure — **kept only for the orca countershading pattern**, which no painted image shows. Not a rendering-style target. File `Narloch1.jpg` — https://static.wikia.nocookie.net/starwars/images/2/27/Narloch1.jpg/revision/latest

## ruling
(empty — owner has not reviewed this race yet)
