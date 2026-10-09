# Pyke

**defName**: `RSW_RimMandrakePyke` (verified present in
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`, line 1507 —
that file is GENERATED, do not hand-edit).
Assigned `Jawa_HuttCartel: S`, `Pirate: R`.

## Sourced text (Wookieepedia)

Canon infobox: skin colour **beige**, **green**, **gray**, **light blue**, **teal with pink
accents**; eye colour **blue**, **magenta**, **purple** (the body text adds **black**);
distinctions *"**elongated, tapered skull with an undersized face**"* and *"**piscine**"*;
origin **Oba Diah**; language **Galactic Basic Standard** and **Pyke**. **Height, mass and
lifespan are ALL blank in the infobox and UNSOURCED in the body — do not invent them.** The
body text says only that *"most were slimmer and taller than most humans."*

🔑 **The species has TWO distinct physiological groups, and that is stated in the lead:**

> The species had two distinct physiological groups. While both shared elongated heads, one
> group was characterized by their **oversized craniums with undersized faces**, while the
> other bore **more humanoid proportions with piscine features.**

Appearance, verbatim:

- *"the Pykes were humanoid, although **most were slimmer and taller than most humans.** They
  had **two long, lanky legs**, and two arms that ended in **three, four, or five-fingered
  hands.**"* ⚠️ **Digit count is genuinely inconsistent across sources — do not assert one.**
- *"Their heads were **large and elongated, with a tapered skull and a proportionately
  undersized face**, a feature which some other species found **unsettling.**"*
- *"Pykes had **two narrow, almond-shaped eyes** which could be blue, magenta, purple, or
  black in color. Their heads rested upon **elongated, sinuous necks.**"*
- *"Pykes had **yellow** or **green blood.**"* Sexes: at least male and female.
- **The second group:** *"Some Pykes had **smaller craniums** than others of the species, as
  well as **short bloated necks**, and five or four fingers. Whereas others … had a range of
  skin tones including gray and green, these individuals might possess **teal skin with pink
  accents** or a gray-green coloration like their tall brethren.
  🔑 **Beneath the masks frequently worn by the species, the short-necked Pykes' faces
  resembled fish.**"*
- 🔑 **The canonical reason for the masks**: *"The atmosphere of the planet **Kessel** could
  provoke **lethal allergic reactions** in Pykes if they were exposed to it for too long,
  necessitating the wearing of **special protective gear** if they remained there
  long-term."* So the mask is **environmental equipment**, not a cultural face-covering, and
  it is **not universal** — the article says masks are *"frequently"* worn.

**Behaviour:**
- The **Pyke Syndicate** *"was the main focus of the Pyke economy and the galaxy's
  preeminent supplier of **spice**"* — narcotics **mined by slaves** on Kessel and elsewhere.
  Quote from the article: *"Syndicates rise and fall, but the Pykes are a family."*
- **Unusual abilities: none recorded.** No Force sensitivity, no venom, no natural weapon.
  The exotic biology is the **skull/face proportion**, the **two body forms**, **yellow or
  green blood**, and the **Kessel-atmosphere allergy.** Do not invent an ability.

🔴 **Repo def contradictions:**

1. **The def's description gets the headline right and the def's genes do not deliver it.**
   *"Distinguished by their unsettlingly large heads and undersized faces"* is a good, sourced
   paraphrase — but the gene list has **no representation of the second physiological group
   at all.** Canon splits the species into tall-cranium and short-necked-piscine forms; the
   xenotype is a single form.
2. **`AptitudeStrong_Plants` is unsourced and probably a misreading of "spice."** Spice in
   canon is **mined** — the article says *"mined by slaves on the planet Kessel"* — not grown.
   Nothing makes a Pyke a botanist.
3. **`Hands_Pig` (two-digit hooves) contradicts the sourced range.** Canon gives Pyke hands
   **three, four, or five** fingers. Two-toed hooves are outside the range, and the article's
   images show slender many-fingered hands.
4. **`Aggression_Aggressive` + `Turn_Gene_MotivationLow` are unsourced as species traits.**
   The Pykes' canonical character is *criminal-syndicate organisation and family loyalty*,
   not innate aggression or apathy.
5. **`Outland_ThickSkin` is unsourced.** If anything, canon gives the species a *fragility* —
   a lethal atmospheric allergy on their own main work site.
6. **`AptitudePoor_Intellectual` is unsourced** for a species running the galaxy's largest
   narcotics cartel.
7. **The def has no representation of the Kessel allergy**, which is the single most
   mechanically-interesting canon fact about them (a species that needs breathing gear in
   certain atmospheres is a natural RimWorld gene).

**What the def gets right:** `RSW_Body_gaunt` + `Body_Thin` + `RSW_BodySizeGene_big` matches
*"slimmer and taller than most humans"* with *"two long, lanky legs."* `RSW_PykeHead` is real,
dedicated Pyke art (see below). `Hair_BaldOnly`/`Beard_NoBeardOnly` is correct. The skin set
(`Outland_Skin_Sage`, `Outland_Skin_PaleBlue`, `Skin_LightGray`) covers green/light-blue/gray
well — **missing beige and the teal-with-pink-accents variant.** The three
`AddictionResistant_*` genes are not in Wookieepedia but are a defensible *game* inference
from a spice-cartel species; flagged as invented rather than wrong.

## Visual brief
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."** The *Clone Wars* trio (`wookieepedia_tall_cranium_masked.jpg`) and the comic capo panel (`wookieepedia_syndicate_capo_comic.jpg`) were deleted. The target is now the live-action *Book of Boba Fett* prosthetic look (`infobox_unmasked_piscine`, `capo_bobf`, `boss_bobf`, `traveler_bobf`, `courier_bobf`), with the painted concept sheet and the photoreal *Outlaws* render as supporting evidence.

**What the live-action heads show (trust these on appearance):**
- **Skin:** pale grey-blue to slate grey, matte-to-slightly-moist, with fine wrinkling around the eyes and snout. Gorak Palas (*Outlaws*) is a more saturated blue-violet; same anatomy.
- **Eyes:** large, glossy, solid BLACK almond eyes, slanted and set wide on a broad flat brow. (Concept art paints them amber-brown; screen is black.)
- **Snout:** a broad, bulbous, drooping fish-like snout/upper lip with wide flat nostril folds, overhanging a small down-turned mouth.
- **Barbels:** two fleshy, pinkish, tapering tendrils hang DOWN FROM THE SNOUT / upper lip (not from the jaw corners as the old brief said), roughly chin length, curving outward; on the capo they are thick and fleshy.
- 🔴 **Cranium — where live-action and animation disagree loudly:** on screen the head is **compact and rounded, wrapped tight in a fitted leather-look cap/cowl with seams**; there is **no towering pale veined dome**. The tall tapered bare cranium exists only in the concept sheet (`wookieepedia_concept_art.jpg`, under a cowl) and in the deleted *Clone Wars* art. Render the live-action proportion: a large rounded skull hidden under a snug cap, not an elongated spike.
- **Masks are worn gear:** the courier (`courier_bobf`) wears a rust-orange respirator face plate with goggles and twin side breathing tubes under a pointed hood — this is the "mask" of canon, and it covers only the face.
- **Clothing:** layered dull-brown/olive rough-woven robes, dark tunics with a single vertical ochre stripe, belts and holsters for soldiers; status Pykes wear rich blue or black gold-trimmed coats with high collars and epaulette-like trim (`boss_bobf`, Gorak Palas).
- **Build:** humanoid, average height in live action, gloved hands; Gorak Palas shows a heavy, thick-set variant.

**`donor_current_sprite.png`** (`.../Heads/Pyke/Normal_south.png`, 512×512 greyscale tint mask) has the tall tapered spike cranium of the animated design and no barbels, mouth or snout — it now disagrees with the live-action target on the head silhouette as well as the missing features.

## Must show
*Rewritten 2026-10-09 to the canon_check leniency lesson (`Transient/canon_check_leniency_2026-10-09.md`): body plan, colour layout and a negative, each checkable on a 256px sprite. Grounded in the live-action *Book of Boba Fett* images the visual brief names (owner ruling 2026-10-08: "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic.").*
- [ ] BODY PLAN: humanoid, slim build; head is a compact rounded skull wrapped in a snug seamed cap or cowl — no tall spiked bare dome
- [ ] COLOUR LAYOUT: pale grey-blue wrinkled skin on the face; large, glossy, solid black slanted almond eyes set wide on a broad flat brow, the darkest element of the face
- [ ] Broad bulbous drooping fish-like snout with flat nostril folds over a small down-turned mouth
- [ ] Two fleshy pinkish barbels hanging down from the snout/upper lip to about chin length
- [ ] Layered rough robes or gold-trimmed status coats; any respirator face plate (goggles + side tubes) is worn gear
- [ ] Realistic rendering: natural prosthetic-skin texture and lighting, no outlines, no cartoon shading
- [ ] NEGATIVE: not the animated *Clone Wars* Pyke (no towering tapered bare cranium, no barbel-less mouthless face), not a human with a tint

## Engine limits
none known — the donor head is a correctly-tinted greyscale mask; the missing barbels, mouth and ear flaps are absent art, not a pipeline limitation.

## Source URLs
- https://starwars.fandom.com/wiki/Pyke — canon article. Direct HTML is Cloudflare-walled;
  wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Pyke&format=json&prop=wikitext`
  (28,956 chars, 2026-09-15). Source of every fact above. ⚠️ The article carries a
  `{{MultipleIssues|expand|image}}` banner — the wiki itself flags it as needing expansion
  and better images.
- https://static.wikia.nocookie.net/starwars/images/a/a8/Pykes_are_fish.png
  (**File:Pykes_are_fish.png — the canon infobox image**, from *The Book of Boba Fett* →
  `wookieepedia_infobox_unmasked_piscine.jpg`)
- https://static.wikia.nocookie.net/starwars/images/e/ea/Pyke-concept.jpg
  (File:Pyke-concept.jpg, concept art → `wookieepedia_concept_art.jpg`)
- https://static.wikia.nocookie.net/starwars/images/5/5c/GorakPalas-Outlaws.png
  (File:GorakPalas-Outlaws.png, *Star Wars Outlaws* → `wookieepedia_gorak_palas_outlaws.jpg`)
- Not used: `File:Unlimited-LomPyke.png`, captioned on the article *"Examples of two forms of
  the Pyke species' body"* — it is a trading-card render (526×478) and was resolved but not
  downloaded this pass. **Worth a later pass: it is the wiki's own side-by-side of the two
  physiological groups.**
- NOT fetched this pass: a `starwars.com/databank` Pyke species page was not attempted.

## Candidate images
- `wookieepedia_infobox_unmasked_piscine.jpg` — live-action, *The Book of Boba Fett*; canon infobox image, file `Pykes are fish.png`: bare-faced Pykes under caps beside two respirator-masked ones — https://static.wikia.nocookie.net/starwars/images/a/a8/Pykes_are_fish.png
- `wookieepedia_capo_bobf.jpg` — live-action, *Book of Boba Fett* ch. 7; Pyke capo head and shoulders, clearest face/barbels; file `PykeCapo-BoBFCh7.png` — https://static.wikia.nocookie.net/starwars/images/1/10/PykeCapo-BoBFCh7.png/revision/latest?cb=20220212021257
- `wookieepedia_traveler_bobf.jpg` — live-action, *Book of Boba Fett* ch. 2; Pyke traveller close-up, cap and barbels; file `PykeTraveler-TribesOfTatooine.png` — https://static.wikia.nocookie.net/starwars/images/b/b1/PykeTraveler-TribesOfTatooine.png/revision/20220126041016
- `wookieepedia_boss_bobf.jpg` — live-action, *Book of Boba Fett* ch. 3; seated Pyke boss in blue gold-trimmed coat; file `Unidentified Pyke boss.png` — https://static.wikia.nocookie.net/starwars/images/0/0e/Unidentified_Pyke_boss.png/revision/20220128051458
- `wookieepedia_courier_bobf.jpg` — live-action, *Book of Boba Fett* ch. 6; masked Pyke courier, respirator plate and soldier robes; file `PykeCourier-BoBFCh6.png` — https://static.wikia.nocookie.net/starwars/images/a/ad/PykeCourier-BoBFCh6.png/revision/latest?cb=20220204031206
- `wookieepedia_concept_art.jpg` — realistic painted concept sheet (design intent, not final screen look): cowled bare veined cranium, open and closed mouth; file `Pyke-concept.jpg` — https://static.wikia.nocookie.net/starwars/images/e/ea/Pyke-concept.jpg
- `wookieepedia_gorak_palas_outlaws.jpg` — photoreal game render, *Star Wars Outlaws*; Gorak Palas, heavy-set blue-violet variant; file `GorakPalas-Outlaws.png` — https://static.wikia.nocookie.net/starwars/images/5/5c/GorakPalas-Outlaws.png

## ruling
(empty — owner has not reviewed this race yet)
