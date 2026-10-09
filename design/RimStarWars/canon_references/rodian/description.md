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
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."** Deleted: the stylised Alien Archive print (`wookieepedia_alien_archive_illustration.jpg`) and the *Clone Wars* mother-and-child (`wookieepedia_female_and_child.jpg`). Added live-action: a Rodian child (*Book of Boba Fett*), a New Republic Rodian officer and a Rodian civilian (*The Mandalorian* S3), and a behind-the-scenes photo of the original Greedo mask. The Battlefront II render (`infobox_fullbody`) stays as the full-body gear reference.

🔴 **The live-action heads overturn two of this entry's old corrections — trust them:**
- **Eyes are GLOSSY BLACK (or very dark violet) hemispherical domes**, wet and reflective with hard specular highlights, set wide and bulging past the skull. Every live-action head (`child_bobf`, `officer_mando`, `greedo_unmasked`) is black; the civilian (`scam_victim_mando`) is dark plum-violet. The old brief's "pale iridescent lavender-white" came from the game render and the deleted illustration — **it is the game's look, not the screen's.** Draw dark glossy eyes.
- **The antennae ARE prominent: two stalked, cupped SAUCER-DISH antennae on top of the head**, angled up and outward, often tinted yellow-ochre against the green (`officer_mando`, `child_bobf`). The crest of small fleshy spines runs between and behind them (`scam_victim_mando`, `officer_mando`). The old "two blunt nubs at the temples" was wrong for live action.
- **Snout:** a tapering conical muzzle ending in a small puckered, pursed-lipped mouth; smoother than the head but with fine wrinkles.
- **Skin:** green — from olive and sage to blue-green — **densely pebbled and ridged across the whole cranium** like reptile/toad skin, finer on the snout. Ears and antennae may go yellow-ochre.
- **Ears:** pointed, swept back, at the sides of the head below the antennae; clearly visible.
- **Hands:** long green fingers with suction-cup tips (`child_bobf`).
- **Clothing:** ordinary galactic dress — uniforms, bright layered civilian robes, field gear. No species costume.

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
`HeadAttachments/rodian/rodian_*.png` — two small temple nubs, i.e. the antennae —
now TOO small against the live-action saucer-dish antennae), `Skin_Green` / `RSW_Skin_DarkGreen`, `Outland_ScaleSkin`,
`Outland_Blood_Green` and `DarkVision` — so large eyes, green scaled skin, green
blood and low-light vision are all already modelled. **What is NOT modelled by any
file on disk: the glossy black wet sheen of the eyes, the stalked saucer-dish antennae, the crest of dorsal
skull-spines, and the suction-cup digits.** (`HeadAttachments/rodian/mohawk_*.png`
exists and is a small tuft, but it is wired to `RSW_Hair_rodian`, a hair gene, not
to the head — it is not the bony crest.)

## Must show
- [ ] Very large glossy BLACK (or very dark violet) hemispherical eyes, wet and reflective, bulging past the skull profile
- [ ] Two stalked, cupped saucer-dish antennae on top of the head, with a crest of small fleshy spines between and behind them
- [ ] A tapering conical snout ending in a small puckered pursed-lipped mouth
- [ ] Green (olive to blue-green) skin, densely pebbled and ridged over the cranium; pointed swept-back ears at the sides
- [ ] Long fingers with suction-cup tips; ordinary galactic clothing
- [ ] Realistic rendering: natural rubbery prosthetic-skin texture and lighting, no outlines, no cartoon shading

## Engine limits
none known — the glossy black eye sheen, the saucer-dish antennae, the dorsal spine crest, and the suction-cup digits are all missing art, not a pipeline limitation.

## Source URLs
- https://starwars.fandom.com/wiki/Rodian (Wookieepedia article; direct page HTML is
  Cloudflare-walled — wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Rodian&format=json&prop=wikitext`,
  67,886 chars, 2026-09-15)
- https://static.wikia.nocookie.net/starwars/images/d/d3/Rodian_DICE.png (File:Rodian_DICE.png, the infobox image → wookieepedia_infobox_fullbody.jpg)
- NOT fetched this pass: https://www.starwars.com/databank/rodians (official Databank).

## Candidate images
- `wookieepedia_officer_mando.jpg` — live-action, *The Mandalorian* ch. 21; New Republic Rodian officer, clearest adult head: black eyes, yellow saucer antennae, spine crest, pebbled green skin; file `Unidentified Rodian Officer MandoS3.png` — https://static.wikia.nocookie.net/starwars/images/d/d5/Unidentified_Rodian_Officer_MandoS3.png/revision/latest?cb=20230331152123
- `wookieepedia_scam_victim_mando.jpg` — live-action, *The Mandalorian* ch. 18; Rodian civilian in bright layered robes, dark violet eyes, blue-green skin; file `Rodian scam victim.png` — https://static.wikia.nocookie.net/starwars/images/a/ad/Rodian_scam_victim.png/revision/latest?cb=20230310012450
- `wookieepedia_child_bobf.jpg` — live-action, *The Book of Boba Fett* ch. 5; Rodian child close-up — juvenile head, saucer antennae, suction-tipped fingers; file `Rodian child BOBF.png` — https://static.wikia.nocookie.net/starwars/images/3/3f/Rodian_child_BOBF.png/revision/20220130192029
- `wookieepedia_greedo_unmasked.jpg` — behind-the-scenes photograph, *A New Hope*: the original Greedo mask being removed; head small in frame; file `GreedoUnmasked.jpg` — https://static.wikia.nocookie.net/starwars/images/8/8f/GreedoUnmasked.jpg/revision/latest?cb=20120615191722
- `wookieepedia_infobox_fullbody.jpg` — photoreal game render (*Battlefront II*), infobox file `Rodian DICE.png`: full-body Rodian in field gear. Its pale lavender eyes are the game's — the screen eyes are black — https://static.wikia.nocookie.net/starwars/images/d/d3/Rodian_DICE.png

## ruling
(empty — owner has not reviewed this race yet)
