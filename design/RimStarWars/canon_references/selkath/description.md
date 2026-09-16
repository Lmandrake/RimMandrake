# Selkath

**defName**: `RSW_RimMandrakeSelkath` (verified present in
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`, line 1638 —
that file is GENERATED, do not hand-edit).
Assigned `Jawa_DeepwaterCompact: S`, which is the only sensible faction for them: the
Selkath is an **aquatic** species and Wookieepedia files it under `Category:Aquatic
sentient species`.

## Sourced text (Wookieepedia)

⚠️ **The canon article is a `{{Species-stub}}` with no "Biology and appearance" section at
all.** All of the anatomy below therefore comes from the **Legends** article, and is marked
as such. This is the page-title trap the brief warns about, in a slightly different shape:
the canon page exists and is real, but it is thin, and everything about how a Selkath
*looks* lives in `Selkath/Legends`.

**Canon article** (`starwars.fandom.com/wiki/Selkath`):
- Infobox: skin colour **grey**, **pink**, **yellow**; eye colour **black**; distinctions
  **aquatic species**; habitat **aquatic**; origin **Manaan**; language **Galactic Basic
  Standard**. **Height, mass, lifespan: all blank — UNSOURCED in canon.**
- *"The Selkath were a species of aquatic beings native to the planet Manaan. The species
  was **most comfortable underwater and preferred to be immersed in liquid.**"*
- 🔑 *"Because of the Selkath's water-dwelling nature, **their chest armors were fitted with
  misting vents in order to keep their skin moist.**"* — a *clothing* fact, and the reason
  an off-world Selkath needs gear at all.
- *"Historically … the Selkath were **devoted to preserving their native oceans and taking
  care of the ill.** For that reason, other species regarded them as a **peaceful and
  helpful people.**"* Their production of **bacta** is a business a senator thought worth
  sabotaging for.
- Canon *individuals* run against the species reputation: Chata Hyoki and Mantu worked as
  **bounty hunters** and *"brought shame to their people's reputation."* Dooku, to Mantu:
  *"your people were once a peaceful race. How far they have fallen."*
- Behind the scenes: first appeared in Legends (KotOR, 2003); entered canon via Chata Hyoki
  in *The Clone Wars* "Pursuit of Peace"; **first live-action appearance in *The Acolyte*
  "Lost / Found" (2024)**, the character Peex Curando.

**Legends article** (`starwars.fandom.com/wiki/Selkath/Legends`) — the source of all
anatomy and the only numbers that exist:
- Class **Amphibian**. **Height 1.5 meters** (`Knights of the Old Republic Campaign
  Guide`). **Lifespan up to 100 standard years** (same source). **Mass is UNSOURCED.**
- Skin colour **blue, green or pink**; language **Selkatha**.
- 🔑 *"They resembled **anthropomorphic sting rays** and had blue, pink, or green-colored
  skin, **which was patterned for underwater camouflage**, and their **mouths were bracketed
  by cephalic lobes.** They tended to **stroke these during conversation**, analogous to the
  Human habit of stroking facial hair, such as mustaches."*
- 🔑 *"**Female Selkath differed from males by the presence of tendrils on the back of their
  heads.**"* — the only sourced sexual dimorphism, and the repo def has no gene for it.
- 🔑 **Unusual ability, and it is real**: *"**All members of the Selkath race had
  retractable, venom-tipped claws.** Similar to the Wookiees, the use of these claws in any
  form of combat or attack was considered **dishonorable and a sign of madness**; to do this
  was to give in to animal instincts unbecoming of a sentient species."* The Selkath at
  Hrakert Station, driven insane by the Progenitor, *"reacted primitively and used their
  claws to strike down Republic technicians."*
- *"As an aquatic species, the Selkath were **skilled swimmers.**"*
- Religion/ancestry: **the Progenitor**, a large female firaxan shark, was *"seen as a
  deity-like figure to the Selkath and believed to be their evolutionary ancestor,"* able to
  emit a **sonic wailing that drives both firaxan sharks and Selkath insane.**
- Culture: strict **neutrality**, enforced by the Ahto City Civil Authority; a monopoly on
  **kolto**, a healing liquid patients could be **immersed in, in tanks**; *"The Selkath
  considered it rude to approach someone showing no signs of wishing to speak."*

🔴 **Repo def contradictions and gaps:**

1. 🔴 **The def has no representation of the species' single defining trait — the need to
   be wet.** Canon: *"most comfortable underwater and preferred to be immersed in liquid,"*
   with **misting vents built into their armour to keep the skin moist.** The gene list has
   `NakedSpeed` and `MaxTemp_SmallDecrease`, which are at best oblique. This is the one
   place a real gene would earn its keep, and it is the biggest gap in the def.
2. **`RSW_BodySizeGene_small` and `Body_Hulk` are in the same gene list**, alongside
   `Body_Standard`. Legends puts the species at **1.5 m — genuinely small** — so the small
   body-size gene is right and `Body_Hulk` is the odd one out. Every reference image shows a
   **slender, narrow-shouldered** figure; none shows bulk.
3. **`Outland_EggLayer` is UNSOURCED.** Neither article says anything about Selkath
   reproduction.
4. **No gene for the female head-tendrils**, which is the only canonical sexual dimorphism
   the species has, and which is exactly the kind of thing a `renderNodeProperties`
   attachment could carry (the mod already does this for the cephalic lobes — see below).
5. **Skin genes miss PINK**, which both articles list (canon: grey/pink/yellow; Legends:
   blue/pink/green). The def covers yellow, sage, viridian, blue, azure and mid-grey —
   green, blue, yellow and grey are all fine; **pink is the omission.**
6. **No medicine aptitude**, for a species canonically *"devoted to … taking care of the
   ill,"* holding a galactic monopoly on a healing compound, and associated with bacta. Not
   an error, but a striking omission — especially since the **Muun** def in this same batch
   carries an *unsourced* `AptitudeStrong_Medicine` that canon does not support. The
   aptitude appears to be on the wrong species.
7. **`Outland_Scalebody`** is a rough fit: Legends calls the skin *"patterned for underwater
   camouflage"* and classes the species **Amphibian** (not reptile). The images show a
   **reticulated / net-like mottling** and a **smooth, slightly rubbery** surface — closer to
   a ray's hide than to scales.

**What the def gets right, recorded so it is not "fixed" by mistake:**
🔑 **`Outland_Hands_VenomTalons` is CORRECT and sourced** — *"retractable, venom-tipped
claws"*, and the reference images show long curved claws on the fingertips. ⚠️ Two caveats
worth attaching to it: the claws are **Legends-only** (canon says nothing about them), and
Legends is explicit that **using them in combat is dishonourable and a mark of insanity** —
so a Selkath pawn clawing raiders is canonically a Selkath who has *lost it*. That is a
flavour note the owner may want, not a defect. `RSW_Head_selkath` and `RSW_Beard_fishmouth`
are real, dedicated Selkath art.

## Visual brief

**Read it as a HAMMERHEAD, or as the article says, an "anthropomorphic sting ray" — a
slender humanoid body carrying a broad, laterally-flattened head that is much wider than the
shoulders are deep.** All four reference images agree closely on this, across a 20-year gap
in art styles, so the shape is stable.

**Head — the whole species:**
- **A broad, flattened, dome-crowned skull that spreads sideways into two large downward-
  hanging CEPHALIC LOBES flanking the mouth.** The lobes are the defining feature. They hang
  like heavy soft jowls or a moustache of flesh, curving forward and down past the jaw line,
  and in `wookieepedia_legends_concept_art.jpg` the near lobe reaches below the chin. Legends
  says Selkath **stroke them while talking** — they are soft, mobile tissue, not bone.
- **The crown sweeps up and back into a low crest**, widest across the top, narrowing toward
  the front — a hammerhead cephalofoil profile.
- **The mouth sits at the front-underside between the lobes**: a small, wide, lipless slit,
  in a slightly protruding beak-like snout. In the KotOR render small teeth are visible.
- **Eyes are small, dark/black, and set far apart on the SIDES of the head**, at the outer
  base of the crest — placed like a fish's, not a primate's. From straight ahead you see
  little of them; from three-quarters, one. **Small eyes on a very wide head is the
  proportion to hit.**
- **Skin pattern is the second most important read, and it is NOT flat.** Legends says the
  skin was *"patterned for underwater camouflage"* and the images show exactly that:
  `wookieepedia_legends_infobox_kotor_fullbody.jpg` has a **reticulated, net-like dark
  tracery** over a pale blue-grey cranium; `wookieepedia_infobox_mantu_canon.jpg` has
  **irregular maroon/dark-red blotches** over pale grey-pink, running onto the hands too.
  **A single-colour Selkath is the failure mode.**
- **There is no nose** — at most a pair of small nostril slits above the mouth. **No hair
  anywhere.** No external ears.
- **The neck is short and heavily creased/folded** where the head meets the shoulders.
- ⚠️ **The female head-tendrils are textually canon (Legends) and NOT VISIBLE in any image
  in this set** — every figure here reads as male or unspecified. Treat the tendrils as
  sourced but visually unconfirmed, and note they would sit on the **back** of the head,
  i.e. a RimWorld `_north` feature.

**Body:**
- **Slender and narrow**, at **1.5 m distinctly short** — the head is a large fraction of the
  total silhouette. Shoulders are narrow and sloping; there is no chest bulk.
- **Arms are long and thin**, and **the hands are the second sourced feature**: long tapering
  fingers ending in **long, curved, pale claws** (the venom talons). In the KotOR render the
  claws are as long as the last finger joint.
- 🔑 **The feet are large, splayed and paddle-like, with two or three broad flattened toes
  ending in blunt hooflike claws** — clearly a swimmer's foot, and visible bare in both
  full-body images even when the leg is booted. **This is a distinctive silhouette element
  that prose never mentions and that a text-only prompt will never produce.**
- Posture is slightly stooped and forward-leaning, head carried low.

**Body vs. clothing** — every Selkath in this set is dressed, and the outfit is *functional*
(canon: misting vents to keep the skin moist):
- `wookieepedia_infobox_mantu_canon.jpg` (Mantu, canon): the **grey-and-orange plated
  bodysuit, shoulder caps, ribbed orange midriff band, belt with pouches, thigh holster,
  knee pads and boots** are all worn. **Bare skin: the head and the hands only** — and the
  hands' maroon blotching matches the head, which is how you can tell where the glove ends.
- `wookieepedia_legends_infobox_kotor_fullbody.jpg`: **plated chest panel, dark bodysuit,
  forearm bracers and tall boots** are worn; **the head, the hands and the bare splayed feet
  are skin.** Note the boots stop above the ankle **precisely so the paddle feet stay
  free** — that is a costume design decision responding to the anatomy, and it is a good
  argument for keeping the feet visible.
- `wookieepedia_legends_concept_art.jpg`: **black-and-cream bodysuit with a black chest
  plate/harness and gloves.** 🔴 The **stiff upright collar rising behind the head is part of
  the garment, not a fin or a frill** — it is easy to mistake for anatomy, and it is not.
  The gloves also hide the claws entirely.

**`donor_current_sprite.png` is a COMPOSITE I assembled, not a single file**, and it is
included because the head alone is misleading: it is
`SWX/Pawn/HeadType/selkath/fishy_male_south.png` with
`SWX/Pawn/HeadAttachments/selkath/fishyjowls_male_south.png` alpha-composited over it (both
512×512, RGBA). That is how the game builds the head, and **the mod is doing the right thing
here**: the cephalic lobes are modelled as a separate **head attachment** (`fishyjowls_*`,
male and female, all four facings, plus `*m` mask variants) driven off `RSW_Head_selkath`,
with the mouth on `RSW_Beard_fishmouth`. What the composite gets right: **a broad flattened
skull, wide-set eyes at the sides, and the two down-hanging lobes flanking a wide down-turned
mouth** — the species' defining shape is genuinely present, which is more than most entries
in this batch can say. What is **missing**: the crown is a **flat-topped rounded pentagon
rather than a swept-back crest**; the lobes are short stubs rather than the long soft
forward-curving pads the references show; the eyes are simple dots with no dark sclera; and —
🔴 **because these are single-channel greyscale tint masks, the reticulated camouflage
patterning cannot be produced by a skin-colour gene at all.** Patterning needs a second
render node or a baked variant, so if the owner wants it, that is new art, not a colour
change. There is **no Selkath body art on disk**, so the short stature, the claws and the
paddle feet are unrepresented.

## Source URLs
- https://starwars.fandom.com/wiki/Selkath — canon article, a `{{Species-stub}}`. Direct
  HTML is Cloudflare-walled; wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Selkath&format=json&prop=wikitext`
  (6,100 chars, 2026-09-15). Source of the canon skin/eye colours, the aquatic habitat, the
  misting-vent armour, and the peaceful-healers reputation.
- https://starwars.fandom.com/wiki/Selkath/Legends — Legends article, via
  `…&page=Selkath/Legends&…` (24,332 chars, 2026-09-15). **Source of the ONLY height
  (1.5 m) and lifespan (up to 100 years) figures, the sting-ray/cephalic-lobe anatomy, the
  camouflage patterning, the female head-tendrils and the venom-tipped claws.**
- https://static.wikia.nocookie.net/starwars/images/e/e7/Mantu-TCWCEJtB.png
  (File:Mantu-TCWCEJtB.png, the **canon** infobox image →
  `wookieepedia_infobox_mantu_canon.jpg`)
- https://static.wikia.nocookie.net/starwars/images/5/59/Selkath_KotOR.png
  (File:Selkath_KotOR.png, the **Legends** infobox image →
  `wookieepedia_legends_infobox_kotor_fullbody.jpg`)
- https://static.wikia.nocookie.net/starwars/images/e/e9/Selkath_concept.png
  (File:Selkath_concept.png → `wookieepedia_legends_concept_art.jpg`)
- https://static.wikia.nocookie.net/starwars/images/4/43/Selkath.png
  (File:Selkath.png → `wookieepedia_legends_headshot.jpg`)
- https://static.wikia.nocookie.net/starwars/images/0/03/MantuDetail-SWE.png
  (File:MantuDetail-SWE.png → `wookieepedia_mantu_detail_encyclopedia.jpg`)
- NOT fetched this pass: no image of **Peex Curando** from *The Acolyte* was retrieved, so
  **the first live-action Selkath is not represented in this set.** Worth a later pass — it
  would be the highest-fidelity reference available and could settle the female tendrils and
  the skin patterning. Also not fetched: `File:Selkath_female.jpg`, which the Legends article
  captions *"A female Selkath and her distinctive head-tendrils"* — it was resolved
  (318×402) but not downloaded, and **it is the one image that would confirm the tendrils.**
  Both are named here so the gap is actionable rather than invisible.

## Candidate images
- `wookieepedia_legends_infobox_kotor_fullbody.jpg` — **the reference of record.** The
  Legends infobox image, full standing figure at 500×1230: settles the hammerhead crest, the
  hanging cephalic lobes, the beak-like mouth with teeth, the side-set black eye, the
  **reticulated camouflage patterning**, the long curved fingertip claws, and the **large
  splayed paddle feet.** A game render (KotOR-era), so treat surface finish as the engine's.
- `wookieepedia_infobox_mantu_canon.jpg` — **the reference of record for CANON**, since it
  is the canon article's own infobox image. Mantu in full armour: pale grey-pink skin with
  **maroon blotch patterning** carried onto the hands, and a clean read of the lobes in
  three-quarter view. Everything below the neck is armour.
- `wookieepedia_legends_concept_art.jpg` — 800×1300 concept art, the best read of the
  **crest sweeping up and back** and of the lobes at full length. ⚠️ The upright collar
  behind the head is costume, not anatomy, and the gloves hide the claws. Concept art, so it
  is design intent rather than final appearance.
- `wookieepedia_legends_headshot.jpg` — a head-and-shoulders view; useful as a second angle
  on the lobes and mouth, adds nothing the two above do not.
- `wookieepedia_mantu_detail_encyclopedia.jpg` — an encyclopedia detail crop of Mantu.
  Redundant with the canon infobox image; kept for completeness.

## ruling
(empty — owner has not reviewed this race yet)
