# Sith Zuguruk (Pureblood) — and the shared anatomy of the Sith species

**defName**: `RSW_RimMandrakeSithZ`, label `Sith Zugurak (Pureblood)`
(`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Assigned `Jawa_AscendantHelix: R`.

🔴 **The canon spelling is Zuguruk, not "Zugurak."** The Wookieepedia article is
`Zuguruk`; `Zugurak` returns `missingtitle` from the API. The likely origin of the
repo's spelling is that the article's own infobox **image file is named
`File:Zugurak.png`** while the article title, the body text and the caption
*inside* that image all read **Zuguruk**. Renaming is owed under
`XENOTYPE_CANON_CORRECTION_1`, where the owner rules bug vs deliberate departure (the `NAMING_SCHEME_EXECUTION_1` gate closed 2026-08-31,
so nothing is waiting on it). The entry does not adopt the typo.

🔑 **This entry doubles as the shared-Sith anatomy reference**, because the repo
ships three separate xenotypes (Kissai, Massassi, Zuguruk) that canon treats as
**castes of one species**. `sith_pureblood/` and `massassi/` point back here for
everything in "Shared across every Sith caste" below.

## Sourced text (Wookieepedia)

### Shared across every Sith caste — the baseline
The definitive sentence, from the Castes section: **"All Sith castes were
red-skinned humanoids with distinctly sharp, predatory features and tentacle
beards."** ("Each caste was sometimes referred to as a subspecies of Sith.") The
castes named are **Zuguruk (engineers), Kissai (priests), Massassi (warriors),
Grotthu (slaves)**; the caste system was rigid — *"There was no transitioning from
one to the other."*

Full shared anatomy, from `Sith (species)/Legends` §Biology and appearance:

- **Skin crimson**; infants a lighter shade of red; typically a dark red, but some
  members retained **more pink shades in adulthood**. Infobox skin range:
  **charcoal, obsidian, red.**
- **Sharp, fierce predatory profiles and features all over the body**, including
  **bone spurs protruding from under the skin at various locations, like the
  elbows.**
- **A notable pair of cheek tendrils hanging down from high cheekbones.** These are
  expressive: slight curling = rejuvenated attitude, stroking the right tendril =
  thoughtfulness, quivering = anger. Also described as "tentacle beards."
- **Cranial horns, pointed teeth, simian mouths below small noses**, and **glowing
  yellow eyes covered by cartilaginous eyebrow-stalks.**
- Chin is variable: **some Sith had long bony chins, others less prominent chins
  that receded from the mouth.**
- 🔑 **"Most Sith had three clawed digits on each hand, and three on each foot; two
  forward facing and one backward facing."** Tridactyl, clawed, with a *reversed*
  hind digit. Five-digit individuals existed (Sek'nos Rath).
- **Commonly left-handed** — their signature weapon, the *lanvarok*, was built only
  for left-handed use.
- Infobox: hair **black, brown, red**; eyes **black, orange, red, white, yellow**;
  language Sith; origin **Korriban**, later Ziost (adopted c. 27,700 BBY) and
  Dromund Kaas (possible propaganda).
- **Unusual ability, species-wide:** the Sith had so high a rate of Force-sensitivity
  that **the entire species was considered strongly Force-sensitive**, from a
  **symbiotic relationship with the dark side** — they derived sustenance directly
  from it and empowered it in turn.
- **No height, mass or lifespan is given for the species as a whole** — UNSOURCED at
  species level. Only the individual castes carry numbers (Kissai 1.8 m / ≤60 yr;
  Massassi 1.9 m / ≤50 yr).

### Zuguruk specifically
> *"Their engineers, the Zuguruk, are loyal, but they build far too many burial
> mounds and too few battleships."* — Sorzus Syn

The Zuguruk were **a caste of the Sith**, from **Korriban** in the Stygian Caldera,
**the second-highest caste** in the traditional system, acting as **engineers**
responsible for **burial mounds and battleships**. Under the Dark Jedi they were
redirected from tumuli to warships by Sorzus Syn. Tasked with **the design and
construction of machines, engines and buildings.**

Biology, verbatim: **"The Zuguruk were quite similar to other castes within the
Sith species: humanoid in form, with their skin spanning hues from crimson to
obsidian. Unlike the other subspecies, at least some of the Zuguruk had Human-like
hands with five digits, instead of the usual tridactyl hands."**

🔑 **That five-digit hand is the ONLY physical trait canon gives the Zuguruk that
is not simply "the same as other Sith."** Height, mass, lifespan, eye colour and
hair colour are all blank in the infobox — UNSOURCED. The wiki itself flags the
five-digit hand as a possible art error: *"The picture of a Zuguruk featured in the
Book of Sith depicts him with Human-like, five-fingered hands, while the Sith were
supposed to be a tridactyl species."*

## Visual brief

**`wookieepedia_zuguruk_bookofsith.jpg` is the reference of record**, and it is the
*only* dedicated Zuguruk image in existence. What it shows:

- **A tall, lean, upright humanoid** in a grey knee-length sleeveless tabard over
  dark leggings with segmented greaves and heavy boots, plus a forearm bracer — an
  **artisan/engineer silhouette, not a warrior's**. This is worth preserving: the
  Zuguruk read is *technician*, and the def's construction/mining aptitudes are the
  right instinct.
- 🔴 **The skin in this image reads warm mid-brown / tan-ochre, NOT crimson.** But
  this is a *Book of Sith* illustration painted on aged parchment with a heavy sepia
  wash over the whole plate, and the article text next to it says **crimson to
  obsidian**. Here the images and the prose disagree and the **prose wins**, because
  the discolouration is demonstrably a property of the page, not the subject — the
  parchment ground is the same ochre. Do not read a brown Sith out of this image.
  (This is the one place in the entry where the usual "trust the image" rule is
  suspended, and the reason is stated so the call can be checked.)
- **Bald, high-domed cranium**; dark sunken orbital sockets; a broad flat nose;
  heavy brow. Facial features are small in the reproduction (282×490) — no cheek
  tendril is clearly resolvable, and **no cranial horn is visible.**
- 🔑 **The right hand is spread open and reads as FIVE digits** — confirming the one
  Zuguruk-exclusive trait, and confirming they are ordinary-proportioned fingers,
  **not elongated ones.**
- **The caption lettered into the illustration reads "Zuguruk."** The image file is
  named `Zugurak.png`. Both are visible in the same artifact; the caption is the
  species name.

**`wookieepedia_three_sith_castes.jpg`** (`File:ThreeSith-BOS.png`, the
`Sith (species)/Legends` infobox) is the best single image of the shared caste
anatomy — three Sith in dark robes:

- **All three are bald with high smooth crowns and no cranial horns visible.**
- **The central figure has heavy vertical bony ridging down the forehead and
  cheeks** and a long bony chin — the "distinctly sharp, predatory features."
- **The right-hand figure has clear paired cheek tendrils** hanging from high
  cheekbones down past the jaw — the "tentacle beard."
- **The left-hand figure has neither prominent ridging nor visible tendrils** — a
  smooth-faced Sith. Canon supports this variation (some had receding chins, and
  hybrids lost features), so **the three castes are not visually uniform even within
  one illustration.**
- 🔴 **Skin in this reproduction reads pale violet-grey/lavender, not red at all** —
  the plate is lit by a magenta-violet sky and colour-shifted throughout. Same
  judgement as above: prose wins on hue, image wins on structure.

**`wookieepedia_canon_sith_aphra29.jpg`** (`File:Sith-2020DoctorAphra29.png`) is the
**canon-continuity** Sith, and it is the strongest single hue reference: a
saturated **red-skinned** hooded figure. Note the canon infobox is much thinner than
Legends — skin **red and tan**, distinctions only **tentacles** and **frequent use
of the dark side**, everything else blank. Canon has no caste system on the page at
all: the three castes are a **Legends-only** structure. 🔑 **The repo ships a
Legends taxonomy; that is a design choice the owner should know he has made.**

**`wookieepedia_sith_youngling.jpg`** (`File:Sith_child.png`) confirms the "infants
a lighter shade of red" line and shows the juvenile proportions.

**`wookieepedia_sith_pureblood_swtor.jpg`** and
**`wookieepedia_seknos_rath_fivedigit.jpg`** are the *hybrid* Sith Pureblood look
(SWTOR-era), not the Red Sith species. Kept as **calibration, not as reference for
the pureblood castes** — canon is explicit that Purebloods "were thought to be very
different from the original Sith species as a whole," with dilute traits (Exal
Kressh had only red skin, yellow eyes and Force-sensitivity — no tendrils, no
eyebrow-ridges), and some Purebloods have *extra* pairs of cheek tendrils that the
original species never had. Sek'nos Rath is the sourced **five-digit** Sith, i.e.
the trait is not unique to Zuguruk in practice.

## Must show
- [ ] A tall, lean, upright engineer/artisan silhouette (tabard, leggings, greaves, boots, forearm bracer) — not a warrior's build
- [ ] Skin read as crimson to obsidian per the sourced text — trust the prose over the two colour-distorted plates (sepia parchment wash; violet lighting), and use the saturated red canon image as the hue anchor instead
- [ ] Bald, high-domed cranium with a broad flat nose and heavy brow; no cranial horn is visible in any reference
- [ ] The right hand shows five ordinary-proportioned digits, not elongated ones — the one Zuguruk-exclusive trait
- [ ] Paired cheek tendrils hanging from high cheekbones down past the jaw are canonical but not uniform — some individuals in the same reference image are smooth-faced with no visible tendrils
- [ ] Heavy vertical bony ridging down the forehead/cheeks and a long bony chin appear on some individuals, not all — facial sharpness is variable across the caste

## Engine limits
none known

⚠️ **No `donor_current_sprite.png`.** The three Sith xenotypes render from shared
mod genes, not species art: `RSW_Head_Bone` forces `RSW_Male_HeavyBoneNormal` /
`RSW_Female_HeavyBoneNormal`, and **this xenotype does not even use that** — see
below. Nothing on disk in this repo compares canon against current in-game art.

## Def-versus-canon (flagged — not fixed)

`RSW_RimMandrakeSithZ`, genes as shipped:

- 🔴 **Skin: `Outland_Skin_DeepOrange`, `Skin_Orange`, `Outland_Skin_Brown`,
  `Outland_Skin_PaleBrown`. There is no red skin gene at all.** Canon Zuguruk skin
  is **crimson to obsidian**, and the species-level rule is "all Sith castes were
  **red-skinned**." This xenotype cannot roll a red Sith. It is the single worst
  defect in the batch, and it looks like it was written from the sepia-washed
  `Zugurak.png` illustration rather than from the text beside it.
- 🔴 **`ElongatedFingers`.** The one Zuguruk-exclusive canon trait is **five
  human-like digits instead of the usual three** — a *count*, not a length. No gene
  expresses digit count, so the trait is absent and a different, invented trait is
  in its place.
- 🔴 **`Head_Gaunt` (vanilla) instead of `RSW_Head_Bone`.** Kissai and Massassi both
  get `RSW_Head_Bone`; canon says the sharp bony predatory features are **shared by
  all castes.** Zuguruk is the caste canon calls "quite similar to other castes,"
  and it is the one given a plain human head.
- 🔴 **No psychic or Force gene whatsoever.** Canon: *the entire Sith species* was
  considered strongly Force-sensitive, from a symbiotic dark-side relationship.
  Kissai gets `PsychicAbility_Enhanced` + `Turn_Gene_LatentPsychic`; Zuguruk and
  Massassi get nothing. The species-level fact is expressed on one caste out of three.
- ⚠️ **`AptitudeStrong_Cooking`** — unsourced. Canon Zuguruk build machines, engines,
  buildings, tumuli and battleships. `AptitudeStrong_Construction` and
  `AptitudeStrong_Mining` are well sourced; `AptitudePoor_Social` and
  `AptitudePoor_Artistic` are not (they *designed* burial monuments).
- ⚠️ **`Hair_BaldOnly`.** The species infobox gives hair **black, brown, red**. The
  images do show bald crowns throughout, so this is defensible as a *look* — but it
  is a choice contradicting a sourced field, and it forecloses the red-haired Sith.
- ⚠️ **No cheek-tendril gene** (`RSW_Beard_chintendril` is present — good — but paired
  with `Beard_NoBeardOnly`), **no bone-spur gene, no cranial-horn gene, no clawed
  tridactyl hands, no eyebrow-stalk gene, no left-handedness.** Every one of these is
  sourced shared-Sith anatomy and none is represented in any of the three xenotypes.
- ⚠️ **No lifespan gene**, so Zuguruk get a human lifespan. Canon gives no Zuguruk
  lifespan, so this is not wrong — recorded only so it is not later "corrected"
  from the Kissai/Massassi numbers, which belong to those castes.
- The `<description>` has a **double space** in `"Zugurak  were"`.

## Source URLs
- https://starwars.fandom.com/wiki/Zuguruk — wikitext via
  `https://starwars.fandom.com/api.php?action=parse&page=Zuguruk&format=json&prop=wikitext`,
  5,459 chars, 2026-09-15. (`page=Zugurak` → `missingtitle`.)
- https://starwars.fandom.com/wiki/Sith_(species)/Legends — same API route,
  127,967 chars, 2026-09-15. Source of all shared-caste anatomy above.
- https://starwars.fandom.com/wiki/Sith_(species) — canon article, 7,414 chars,
  2026-09-15. (`page=Sith_species` is a redirect stub of 28 chars.)
- https://static.wikia.nocookie.net/starwars/images/8/8f/Zugurak.png → `wookieepedia_zuguruk_bookofsith.jpg` (282×490)
- https://static.wikia.nocookie.net/starwars/images/7/78/ThreeSith-BOS.png → `wookieepedia_three_sith_castes.jpg` (430×243)
- https://static.wikia.nocookie.net/starwars/images/d/da/Sith-2020DoctorAphra29.png → `wookieepedia_canon_sith_aphra29.jpg` (762×1025)
- https://static.wikia.nocookie.net/starwars/images/e/e9/Sith_child.png → `wookieepedia_sith_youngling.jpg` (229×262)
- https://static.wikia.nocookie.net/starwars/images/9/9c/Sith_Pureblood.jpg → `wookieepedia_sith_pureblood_swtor.jpg` (267×608)
- https://static.wikia.nocookie.net/starwars/images/1/1b/SeknosRath-ForceStorm1.jpg → `wookieepedia_seknos_rath_fivedigit.jpg` (250×296)
- NOT fetched: `https://www.starwars.com/databank/` has no Sith-species page; not attempted.

## Candidate images
- `wookieepedia_zuguruk_bookofsith.jpg` — **the only Zuguruk image in canon or
  Legends.** Engineer silhouette, five-digit right hand, "Zuguruk" lettered in the
  plate. **Negative on hue** (sepia parchment wash, not brown skin).
- `wookieepedia_three_sith_castes.jpg` — best shared-caste anatomy image: bony
  facial ridging, long bony chin, paired cheek tendrils, bald crowns, and
  within-image variation. **Negative on hue** (violet colour cast).
- `wookieepedia_canon_sith_aphra29.jpg` — the hue reference: saturated red skin,
  canon continuity.
- `wookieepedia_sith_youngling.jpg` — juvenile, lighter red, per the sourced line.
- `wookieepedia_sith_pureblood_swtor.jpg` — **negative reference.** Hybrid Sith
  Pureblood, not the Red Sith species; canon says Purebloods differ substantially.
- `wookieepedia_seknos_rath_fivedigit.jpg` — the sourced five-digit non-Zuguruk
  Sith; shows the trait is not caste-exclusive in practice.

## ruling
(empty — owner has not reviewed this race yet)
