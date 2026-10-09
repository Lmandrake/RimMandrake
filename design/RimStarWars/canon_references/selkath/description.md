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
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."** Deleted: the two *Clone Wars* Mantu renders (`wookieepedia_infobox_mantu_canon.jpg`, `wookieepedia_mantu_detail_encyclopedia.jpg`) and the two KotOR game renders (`wookieepedia_legends_infobox_kotor_fullbody.jpg`, `wookieepedia_legends_headshot.jpg`). The gap the old entry named is now closed: **Peex Curando from *The Acolyte* is the first live-action Selkath** (`wookieepedia_peex_curando_acolyte.jpg`), backed by its painted design art (`wookieepedia_peex_curando_concept_acolyte.jpg`) and the realistic KotOR concept painting (`wookieepedia_legends_concept_art.jpg`).

**Read it as an "anthropomorphic sting ray" — a slender humanoid body under a broad, heavy, forward-thrust head.**

**Head, from the live-action prosthetic (trust it on appearance):**
- **A large smooth-domed cranium that slopes forward and down into a broad blunt snout** — in profile like a manta's head or a hammerhead's rounded nose, wider than it is tall.
- **Two thick fleshy cephalic lobes hang straight down from the corners of the mouth**, like soft walrus tusks of flesh, reaching below the chin. Soft, mobile tissue (Legends: Selkath stroke them while talking).
- **Two nostril pits on the front of the snout**; a wide lipless mouth beneath them, hidden between the lobes.
- **Eyes are small, set far back on the SIDES of the head** — amber-brown with a dark pupil in live action (the old "black" came from game renders), deep-set in a wrinkled socket.
- 🔴 **Skin pattern — where the realistic and animated versions disagree loudly:** the live-action skin is **slate blue-grey divided into irregular polygonal plates by a network of pale cracks**, like turtle skin or dried mud, over the whole cranium and snout. The deleted *Clone Wars* Mantu had **maroon blotches on grey-pink** — that look is gone. The KotOR concept and the Acolyte design art agree with a blue-grey to blue-green base with darker mottling/tracery. **A single flat colour is still the failure mode.**
- **The throat and neck underside are pale tan-beige and deeply wrinkled/folded**, contrasting with the grey plated head. No hair, no external ears.
- ⚠️ **The female head-tendrils are textually canon (Legends) and still NOT VISIBLE in any image in this set.**

**Body:**
- **Slender and narrow, distinctly short (Legends: 1.5 m)**, head a large fraction of the silhouette; narrow sloping shoulders.
- **Long thin arms, long tapering grey fingers** (claws sourced in Legends; hidden by gloves in the concept painting).
- 🔑 **Large splayed paddle-like feet with two or three broad flattened toes** — visible bare below the leg wraps in the Acolyte design art and in the KotOR concept. A swimmer's foot; keep it visible.

**Body vs. clothing:** Peex wears **layered taupe/oatmeal Jedi-style robes with a crossed tunic and cloth belt** (the Acolyte design art adds wrapped leggings and a woven orange belt); the KotOR concept wears a black-and-cream bodysuit whose **stiff upright collar behind the head is garment, not a fin**.

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

## Must show
*Rewritten 2026-10-09 to the canon_check leniency lesson (`Transient/canon_check_leniency_2026-10-09.md`): body plan, colour layout and a negative, each checkable on a 256px sprite. Grounded in the live-action Peex Curando (*The Acolyte*), its painted design art, the KotOR concept painting and the Legends text (owner ruling 2026-10-08: "That's realistic, not these cartoon versions you keep using.").*
- [ ] BODY PLAN: slender, short (1.5 m) humanoid with narrow sloping shoulders under a large, heavy, forward-thrust head; long thin arms with long thin fingers; large splayed paddle-like feet with broad flattened toes
- [ ] Head: large smooth-domed head sloping forward into a broad blunt snout with two nostril pits — manta/hammerhead-like, wider than tall
- [ ] Two thick fleshy cephalic lobes hanging straight down from the mouth corners to below the chin
- [ ] Small amber-brown eyes set far back on the SIDES of the head
- [ ] COLOUR LAYOUT: slate blue-grey skin divided into irregular polygonal plates by pale cracks over cranium and snout; pale tan, deeply wrinkled throat and neck — never one flat colour, never maroon blotches
- [ ] Realistic rendering: natural prosthetic-skin texture and lighting, no outlines, no cartoon shading
- [ ] NEGATIVE: not the animated *Clone Wars* Selkath (no maroon blotches on grey-pink, no small black game-render eyes), not a bulky build, not a human with a tint

## Engine limits
The head is built from single-channel greyscale tint masks (`RSW_Head_selkath` + `fishyjowls` attachment), so a skin-colour gene cannot produce the reticulated/blotched camouflage patterning — that needs a second render node or a baked variant, which is new art, not a colour change.

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
- https://static.wikia.nocookie.net/starwars/images/e/e9/Selkath_concept.png
  (File:Selkath_concept.png → `wookieepedia_legends_concept_art.jpg`)
- https://static.wikia.nocookie.net/starwars/images/8/83/PeexCurando-DayEpisodeGuide.jpg
  (File:PeexCurando-DayEpisodeGuide.jpg, live-action *The Acolyte* → `wookieepedia_peex_curando_acolyte.jpg`)
- https://static.wikia.nocookie.net/starwars/images/1/16/PeexCurando-ArtOfAcolyte.png
  (File:PeexCurando-ArtOfAcolyte.png, *The Art of Star Wars: The Acolyte* → `wookieepedia_peex_curando_concept_acolyte.jpg`)
- NOT fetched: `File:Selkath_female.jpg` (318×402, a *Dawn of the Jedi* comic panel) — the one image that would show the female tendrils, but it is a comic, so it was left out under the realism ruling.

## Candidate images
- `wookieepedia_peex_curando_acolyte.jpg` — **the reference of record.** Live-action, *The Acolyte*: Peex Curando head and shoulders — cracked polygonal blue-grey head skin, hanging lobes, nostril pits, amber side eye, wrinkled tan throat, robes; file `PeexCurando-DayEpisodeGuide.jpg` — https://static.wikia.nocookie.net/starwars/images/8/83/PeexCurando-DayEpisodeGuide.jpg/revision/latest?cb=20250606035059
- `wookieepedia_peex_curando_concept_acolyte.jpg` — realistic painted design art, *The Art of Star Wars: The Acolyte*: full-body Peex in robes, splayed paddle feet visible; file `PeexCurando-ArtOfAcolyte.png` (286×421) — https://static.wikia.nocookie.net/starwars/images/1/16/PeexCurando-ArtOfAcolyte.png/revision/latest?cb=20260227034340
- `wookieepedia_legends_concept_art.jpg` — realistic KotOR concept painting, 800×1300: full figure, crest/snout profile, lobes at full length, splayed feet; the collar is costume. File `Selkath concept.png` — https://static.wikia.nocookie.net/starwars/images/e/e9/Selkath_concept.png

## ruling
(empty — owner has not reviewed this race yet)
