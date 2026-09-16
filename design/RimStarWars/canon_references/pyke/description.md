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

🔴 **The single thing this entry exists to settle: on a Pyke, THE BIG PALE DOME IS OFTEN A
HOOD, AND THE FISH FACE IS USUALLY NOT A MASK. Prose gets this exactly backwards.** The
canon text says masks are *"frequently worn,"* which invites an artist to draw the whole head
as a helmet — but the article's **own infobox image is named `File:Pykes_are_fish.png`** and
shows bare piscine faces, and the concept art shows the cranium's covering peeling back to
reveal bare skin. Getting this wrong produces either a robot-looking helmet-head or a naked
skull with no cowl.

**What is BODY (skin), settled from `wookieepedia_concept_art.jpg` — a three-panel character
design sheet, the most diagnostic image in the set:**
- **The cranium is bare skin: pale white-blue, smooth, glossy, and faintly VEINED**, swelling
  up and back from the brow into a **tapered point at the top-rear.** Fine blue-purple
  capillary tracery is visible across it. It is anatomy, not a shell.
- **The face is undersized and sits low on the front of that skull** — canon's "undersized
  face," and the whole reason the species reads as unsettling.
- **Eyes are large, slanted, almond-shaped and set wide**, amber-brown in the concept art,
  black in *The Book of Boba Fett*, magenta in the comic. **Large relative to the face, small
  relative to the skull.**
- **A pair of fleshy, tapering BARBELS hangs down from the corners of the jaw** — soft
  whisker-like appendages, roughly the length of the chin. **These are flesh, they hang and
  move, and they are present on both the concept-art head and the *Outlaws* and *Boba Fett*
  faces.** They are the species' most distinctive soft feature and the easiest thing for a
  text-only prompt to miss entirely.
- **The mouth is a broad, down-turned lipless slit** low on the face. The concept art's
  right-hand panel shows it **gaping open with rows of small teeth** and a fleshy interior —
  so it does open wide.
- **Small pointed ear-fin flaps** sit at each side of the head, at about eye level.
- **The neck**: **long and sinuous** on the tall form; **short and bloated** on the piscine
  form — canon says both, and `wookieepedia_gorak_palas_outlaws.jpg` is the short-necked one.
- **Skin colour, from the images:** pale white-blue and grey (concept art, *Boba Fett*),
  saturated **blue-violet** (Gorak Palas). No image in this set shows beige or the
  teal-with-pink variant.
- **Body build:** the tall form is **narrow, elongated and stooped** (`…concept_art.jpg`
  centre panel; `…syndicate_capo_comic.jpg`), with long thin arms and long slender fingers.
  The short-necked form can be **heavy and thick-set** — Gorak Palas is visibly obese.

**What is CLOTHING, and this is where prose blurs:**

| Feature | Body | Clothing / gear |
|---|---|---|
| Pale, tapered, veined cranium | ✅ **skin** | |
| Mottled dark-green/grey textured covering over the back and sides of the skull, with scalloped flanges at the nape | | ✅ **a fitted cowl/hood.** The concept-art side panels show it wrapping the skull and leaving the face bare |
| Snug leather-look **skullcap** over the crown (Gorak Palas, and the *Boba Fett* group) | | ✅ **cap** |
| Large slanted eyes, jaw barbels, ear flaps, down-turned mouth | ✅ **skin** | |
| Cream/bone **face plate with goggles and a vertical breathing tube** (the right-hand figures in `…unmasked_piscine.jpg`; the *Clone Wars* trio; the comic capo) | | ✅ **respirator mask** — this is the "mask" of the canon text, and it covers only the FACE |
| Layered robes, wide-shouldered mantles, gold-trimmed coats, ruff collars, brooches, bracelets | | ✅ garments — status dress, varies per individual |
| Armour plates, pauldrons, greaves, boots (*Clone Wars* guards) | | ✅ armour |

- 🔑 **`wookieepedia_infobox_unmasked_piscine.jpg` contains BOTH states in one frame**, which
  is why it is the reference of record: the four foreground figures show **bare grey piscine
  faces** (big black eyes, bulbous snout, hanging barbels, ear flaps) under **cloth caps**,
  while the two figures at the right wear **actual cream respirator masks with mouth tubes
  over hooded heads.** Compare them side by side and the body/clothing line is unmistakable.
- ⚠️ **One honest uncertainty, flagged rather than guessed:** in
  `wookieepedia_tall_cranium_masked.jpg` (*The Clone Wars*) the tall pale dome could be read
  as either a bare cranium or a helmet/hood. By analogy with the concept art — same design
  lineage, hood over bare skull — **it most likely reads as a hood over the cranium, with the
  goggles and mouth tube as separate worn gear.** That is an **inference, not a sourced
  fact.** The face plate is definitely worn.

**`donor_current_sprite.png` is `.../Heads/Pyke/Normal_south.png` (512×512, RGBA) — a
greyscale tint mask** (correct for a RimWorld humanlike head; colour comes from the skin
gene). **This is real, dedicated Pyke art and it is the best donor sprite in this batch.**
What it gets right, and it gets the hard part right: **a tall tapered cranium with a small
pale face pushed down to the bottom of it**, plus two thin slanted eyes — the
oversized-cranium/undersized-face proportion, which is the species' defining trait, is
actually there. What is **missing**: **no jaw barbels** (the species' most distinctive soft
feature); **no mouth**; **no ear flaps**; the taper comes to a **sharp point at the top**
rather than sweeping up-and-back; and the two small prongs at the base of the head read as
jaw hardware rather than as the hanging barbels they should be. It also cannot show the
**long sinuous neck**, and there is **no Pyke body art on disk**, so the lanky proportion is
unrepresented. `Normal_east.png` and `Normal_north.png` exist alongside it.

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
- https://static.wikia.nocookie.net/starwars/images/a/a5/Pykes.png
  (File:Pykes.png, *The Clone Wars* → `wookieepedia_tall_cranium_masked.jpg`)
- https://static.wikia.nocookie.net/starwars/images/2/26/PykeSyndicateCapo-SWQ04.png
  (File:PykeSyndicateCapo-SWQ04.png → `wookieepedia_syndicate_capo_comic.jpg`)
- Not used: `File:Unlimited-LomPyke.png`, captioned on the article *"Examples of two forms of
  the Pyke species' body"* — it is a trading-card render (526×478) and was resolved but not
  downloaded this pass. **Worth a later pass: it is the wiki's own side-by-side of the two
  physiological groups.**
- NOT fetched this pass: a `starwars.com/databank` Pyke species page was not attempted.

## Candidate images
- `wookieepedia_infobox_unmasked_piscine.jpg` — **the reference of record.** The canon
  infobox image (1480×810, live-action *Book of Boba Fett*), and the file the wiki itself
  named `Pykes_are_fish.png`. Shows the **short-necked piscine form's bare faces** — grey,
  big black eyes, bulbous snout, hanging jaw barbels, ear flaps under a fitted cap — **and**,
  in the same frame, two genuinely **masked** figures for comparison. This single image
  settles the body-versus-clothing question.
- `wookieepedia_concept_art.jpg` — **the reference of record for the head's anatomy.** A
  three-panel design sheet: two large head studies (mouth closed, then gaping with teeth)
  plus a full-figure. Settles that the **cranium is bare veined skin under a cloth cowl**,
  and gives the cleanest read of the barbels, the slanted eyes and the undersized face.
  Concept art, so treat it as design intent rather than final screen appearance.
- `wookieepedia_gorak_palas_outlaws.jpg` — the **short-necked, heavy-set** variant in
  game-render quality: blue-violet skin, scarring around one eye, barbels, skullcap, and a
  gold-trimmed teal coat with a ruff collar. Waist-up. Best colour reference in the set.
- `wookieepedia_tall_cranium_masked.jpg` — *The Clone Wars* trio, full figures: the **tall
  form's** proportions, long limbs, armour and boots. ⚠️ **Whether its pale dome is cranium
  or hood is not settled by this image** (see the flag above); stylised animation, so treat
  the palette as the show's.
- `wookieepedia_syndicate_capo_comic.jpg` — a comic panel of a masked Pyke capo leaning on a
  rail: useful only for **posture and the magenta eye colour**, since the whole head is
  covered by cowl and respirator. Weakest of the set.

## ruling
(empty — owner has not reviewed this race yet)
