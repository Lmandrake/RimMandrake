# Neimoidian

**defName**: `RSW_RimMandrakeNeimoidian` (verified present in
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`, line 1355 —
that file is GENERATED, do not hand-edit).
Assigned `Jawa_AscendantHelix: S`. Has a dedicated name-maker
(`RSW_KoTOR_NamerNeimoidian`) and name lists on disk under
`Languages/English/Strings/RimMandrakeSWNames/SWX/Neimoidian/`.

## Sourced text (Wookieepedia)

Canon infobox: class **Humanoid**; skin colour **beige**, **green**, **gray**; eye colour
**red-gold**; distinctions **noseless faces**, **bony fingers**, **lanky bodies**; origin
**Neimoidia** plus the colonised **Purse Worlds** (Cato Neimoidia, Deko Neimoidia, Koru
Neimoidia); language **Pak-Pak**. **Height is blank in the infobox but sourced in the body
text; mass and lifespan are UNSOURCED — do not invent them.**

> They had smooth noseless faces, mottled green-gray skin, and large red-gold eyes.

Appearance, verbatim:

- *"They had **smooth, mottled green-gray skin** and **large, red-gold eyes with a pupil
  that split it horizontally.**"* 🔑 **The horizontally-split pupil is the single most
  distinctive eye feature and the repo def does not have it.**
- *"Some Neimoidians had a **beige** skin and **the color could evolve over the years.** For
  example, Nute Gunray had a **gray** skin at the beginning of the Clone Wars before turning
  **green** at the end of the conflict."* — colour drift with age is canonical.
  *"Neimoidians could be susceptible to **vitiligo**."*
- **Height: 1.9 to 2.11 meters** (Databank entries for Lott Dod and Lok Durd). *"Adult
  individuals were known to be tall."*
- *"Neimoidians had **brown blood** and **long, bony hands with five pointed fingers, one of
  which was an opposable thumb.**"*
- *"Although many Neimoidians were lean, **obese individuals were not unheard of.**"*
- *"They looked very similar to the **Duros** because the two species were **genetically
  linked.** In fact, the Neimoidian homeworld of Neimoidia was discovered and colonized by
  Duros. Over the millennia, the Duros of Neimoidia evolved because of the **more humid
  atmosphere and heavier gravity** of their planet."*
- *"Neimoidian body language included **a great deal of cringing.**"*

**Life cycle — canon and load-bearing:**
- *"The Neimoidians spent the **first seven years of their life as 'grubs,' maggot-like
  larvae** that were forced to compete with each other over a limited food supply."* They
  are confined to **huge communal hives** where there is little food, *"and the greediest
  were usually the ones who survived."* *"It was possible that they **never emerged from
  their maggot state** because of a lack of food and became **drones**."*

**Behaviour and abilities:**
- 🔑 *"The **brains** of the Neimoidian species were **specifically wired for
  calculation**, creating personalities often lambasted as cowardice when, in fact, it was
  a **strong survival instinct based on risk and percentages.**"* The article states this
  three separate ways, and explicitly frames the greedy-coward reading as an **in-universe
  slur**: *"A **racist cliché** about the Neimoidians was to portray them as a devious and
  obese plutocrat, fattened by his greed."* To the Neimoidians risk assessment *"was a
  proud facet of their society."*
- *"**But not all Neimoidians were cowards.** For example, the **Neimoidian Royal Guards**
  were military units composed of Neimoidians … intensely loyal to their people."*
- Many were **paranoid**; shipboard Neimoidians *"rarely left the command bridge to avoid
  another colleague gaining more power."* Society is **hierarchical and vertical**, obsessed
  with **status**, and — the visually critical part — *"their status and wealth were also
  reflected in a **combination of clothing and headgear.**"*
- They *"relied heavily on **droids** for many manual tasks, especially those that could be
  dangerous,"* and a high-ranking Neimoidian is *"virtually impossible to see … without
  being surrounded by battle droids or bodyguards."*
- **Unusual abilities: none.** No Force sensitivity, no venom, no natural weapon. The
  exotic biology is **brown blood**, the **maggot/grub larval stage**, and the
  **calculation-wired brain**. Do not invent an ability.

🔴 **Repo def contradictions:**

1. 🔴 **`RSW_butchergene_lizardskin` + `Outland_Scalebody` give the Neimoidian SCALED
   skin. Canon says "smooth" twice** — *"smooth noseless faces"* and *"**smooth**, mottled
   green-gray skin."* Every reference image shows smooth, soft, mottled and *wrinkled*
   skin — the texture is **creased and blotched, never scaled.** This is the clearest
   repo-versus-canon appearance error in this batch.
2. **The def description says "large orange eyes"; canon says "large red-gold eyes with a
   pupil that split it horizontally."** `RSW_Eyes_HugeRed` gets the size and roughly the
   hue, but **the horizontal split pupil — the feature — is absent from both the
   description and the gene list.**
3. **`Turn_Gene_Terrified` + `Delicate` encode the cowardice slur as biology.** Canon spends
   several paragraphs saying the opposite: it is calculation, the species regards it as a
   virtue, the "obese greedy coward" portrayal is named as a **racist cliché**, and the
   **Royal Guard** exists as a counter-example. `AptitudeStrong_Intellectual` is exactly
   right and well sourced ("brains wired for calculation"); the fear genes are the part to
   question. Note also that `AptitudeStrong_Social` sits awkwardly beside `Turn_Gene_Terrified`
   in the same list.
4. **`Outland_AcceleratedPregnancy` runs against the canonical life cycle.** Canon gives the
   Neimoidian a **seven-year larval grub stage** in a communal hive — an unusually *slow*
   and *externalised* development. `Outland_EggLayer` is defensible as a stand-in for that
   (grubs must hatch from something), but "accelerated" is the wrong direction, and nothing
   in RimWorld's gene set currently represents the hive-competition stage that canon says
   forms the entire species' character.
5. **No body-scale or height gene** for a species canonically **1.9–2.11 m**. `Body_Thin`
   catches "lanky" but not "tall."

**What the def gets right, recorded so it is not "fixed" by mistake:**
`Outland_Blood_Brown` is **correct and sourced** (canon: brown blood). `ElongatedFingers`
matches *"long, bony hands with five pointed fingers."* `RSW_DurosHead` is **canon-supported,
not a lazy donor** — the article states the two species look very similar because they are
genetically linked and Neimoidia was colonised by Duros. The warm-temperature genes
(`MinTemp_SmallIncrease`, `MaxTemp_SmallIncrease`) fit Neimoidia's *"more humid
atmosphere."* `Hair_BaldOnly` / `Beard_NoBeardOnly` are correct — the species is hairless
in every image. The skin-colour set (`Outland_Skin_DeepGreen`, `Skin_Green`,
`Outland_Skin_PaleGreen`, `RSW_Skin_DarkGreen`, `Skin_LightGray`) genuinely covers the
canonical green-to-grey range; **only beige is missing.**

## Visual brief

🔴 **THE MOST IMPORTANT THING ABOUT NEIMOIDIAN REFERENCE IMAGES: the tall horned/mitred
shape everyone remembers is a HAT. It is not the skull.** A text-only prompt for
"Neimoidian" reliably produces a creature whose *head* is cone-shaped or horned, and that is
wrong. Canon states the headgear is **status clothing** — *"their status and wealth were
also reflected in a combination of clothing and headgear"* — and
`wookieepedia_infobox_encyclopedia.jpg` proves it by showing **three Neimoidians in three
completely different hats.** Strip the hat and the head underneath is consistent.

**The actual head, under the hat** (best read: `wookieepedia_officer_lostfound_liveaction.jpg`,
a live-action close-up):
- **A tall, narrow, vertically-elongated skull that TAPERS DOWNWARD** — widest across the
  smooth domed cranium at the brow, narrowing through hollow cheeks to a small chin. The
  opposite taper from a Pyke. Hairless, no ears visible.
- **Skin is mottled grey-green with irregular darker patches**, and it is **soft, smooth and
  heavily CREASED** — long vertical creases down the cheeks, crow's-foot creases radiating
  from the outer eye corners, horizontal brow furrows. **Creased and blotchy, never scaled.**
- **Eyes are large, wide-set, deep-set in dark sockets, and red-orange**, with the
  **horizontally-split pupil** canon describes — a dark horizontal bar across a glowing iris.
  They are the only high-contrast feature in the face and should read from a distance.
- **No nose at all** — canon's "noseless faces." At most a pair of small dark nostril holes
  low on the centre line. **Do not draw a nose bridge.**
- **The mouth is small, thin-lipped and set low**, turned down at the corners, with
  **several short vertical ridges running down the chin/jaw below it** — this is what the
  def's `FacialRidges` is presumably reaching for, and it is visible in every image.
- **The neck is thin.** In the live-action still it is entirely covered by a ribbed collar.

**Body:**
- **Tall (1.9–2.11 m) and lanky**, narrow-shouldered, with a **long thin torso.** Canon
  allows obese individuals, so a fat Neimoidian is *canonical variation*, not an error — but
  the default is lean.
- **Hands are the second-best feature after the eyes**: long, thin, bony, with **five
  pointed fingers** and prominent knuckles, held clasped or steepled. In
  `wookieepedia_infobox_encyclopedia.jpg` the hands are the only skin visible below the
  neck on two of the three figures.
- **Posture is a canonical trait, not artistic license** — canon says *"Neimoidian body
  language included a great deal of cringing."* The figures stand stooped, shoulders
  rounded forward, hands drawn in to the chest.
- **Skin below the head is essentially never visible.** Every Neimoidian in this set is
  covered from collar to floor.

**BODY vs. CLOTHING — the explicit split a sprite artist needs:**

| Feature | Body | Clothing |
|---|---|---|
| Tall horned / mitred / cone headdress, side flaps, upswept prongs | | ✅ **hat** — varies per individual and by rank |
| Domed hairless cranium, downward-taper, hollow cheeks | ✅ | |
| Ribbed high collar / neck-ring with gold cords | | ✅ garment |
| Red-orange split-pupil eyes, creased mottled grey-green skin, noseless face, chin ridges | ✅ | |
| Breathing mask with round filters (the left figure in the encyclopedia group) | | ✅ **worn apparatus**, not a face |
| Floor-length layered robes, ribbed/quilted texture, wide draped sleeves | | ✅ garment — this is where the "wide" silhouette comes from |
| Long bony five-pointed-finger hands | ✅ | |
| Crested helmet, pauldrons, gauntlets, chest plate (Royal Guard) | | ✅ **armour** |

- `wookieepedia_rune_haako_fullbody.jpg`: the brown-black **wing-shaped headdress with two
  upswept prongs and two down-curving side flaps** is a hat; the olive under-robe and the
  ribbed dark over-robe with slashed sleeves are garments. **Bare skin: face and hands
  only.**
- `wookieepedia_officer_lostfound_liveaction.jpg`: same shape of hat in navy, with a
  **ribbed blue turtleneck collar and gold cords** below it. 🔴 The gold cords are jewellery
  and the collar is knitwear — neither is anatomy.
- `wookieepedia_royal_guard.jpg`: the **grey crested helmet with a spine, the pauldrons, the
  gauntlets and the plated chest** are all armour. The **grey** face beneath is skin, and it
  confirms the grey end of the canonical colour range plus the vertical jaw ridges. This is
  also the image that disproves "all Neimoidians are cowards."

## Must show
- [ ] Tall, narrow, vertically-elongated skull that tapers downward from a domed brow to a small chin — NOT a horned/mitred cone shape (that shape is a hat, worn over the head, and varies per individual)
- [ ] Smooth, soft, mottled grey-green skin, heavily creased (long vertical cheek creases, crow's-feet, brow furrows) — never scaled
- [ ] Large, wide-set, deep-set red-orange eyes with a horizontally-split pupil (a dark horizontal bar across the iris)
- [ ] Noseless face — no nose bridge, at most small dark nostril holes low on the centre line
- [ ] Small, thin-lipped, downturned mouth with several short vertical ridges on the chin/jaw below it
- [ ] Long, thin, bony hands with five pointed fingers and prominent knuckles, often held clasped or steepled in a stooped, cringing posture

## Engine limits
none known

**There is no Neimoidian head or body art in the repo** — the only Neimoidian texture on
disk is `RimMandrakeSW/OR/OuterRim/XenotypeIcons/Xenotype_Neimoidian.png`, a UI icon, and
the xenotype borrows `RSW_DurosHead`. **No `donor_current_sprite.png` is included**, because
there is no Neimoidian-specific art to show; in game a Neimoidian currently wears a Duros
head, which canon does support as a near-relative but which will not carry the split pupils
or the chin ridges.

## Source URLs
- https://starwars.fandom.com/wiki/Neimoidian — canon article. Direct HTML is
  Cloudflare-walled; wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Neimoidian&format=json&prop=wikitext`
  (45,506 chars, 2026-09-15). Source of every fact above. The Legends variant was **not**
  fetched — the canon article is long and fully sourced, so nothing needed it.
- https://static.wikia.nocookie.net/starwars/images/b/b0/NeimoidiansSWE.png
  (File:NeimoidiansSWE.png, the canon infobox image → `wookieepedia_infobox_encyclopedia.jpg`)
- https://static.wikia.nocookie.net/starwars/images/f/f1/Rune_Haako_full_body.png
  (File:Rune_Haako_full_body.png, captioned on the article *"Rune Haako, a typical
  Neimoidian"* → `wookieepedia_rune_haako_fullbody.jpg`)
- https://static.wikia.nocookie.net/starwars/images/5/5f/NeimoidianOfficer-LostFound.png
  (File:NeimoidianOfficer-LostFound.png, from *The Acolyte* "Lost / Found" →
  `wookieepedia_officer_lostfound_liveaction.jpg`)
- https://static.wikia.nocookie.net/starwars/images/c/cd/Neimoidian_Guard.png
  (File:Neimoidian_Guard.png → `wookieepedia_royal_guard.jpg`)
- NOT fetched this pass: `https://www.starwars.com/databank/neimoidian` is cited by the
  article as the source for the "Humanoid" class, but was not fetched directly.

## Candidate images
- `wookieepedia_officer_lostfound_liveaction.jpg` — **the reference of record for the head.**
  1206×1608 live-action close-up: the downward-tapering skull, the mottled grey-green
  *creased* (not scaled) skin, and the best available read of the **red-orange
  horizontally-split pupils.** Everything from the collar down is clothing.
- `wookieepedia_infobox_encyclopedia.jpg` — **the reference of record for the
  hat-is-not-a-head point.** The canon infobox image: three Neimoidians side by side in
  **three different headdresses**, one of them also wearing a **breathing mask**, showing
  that headgear is status dress and varies. Also the best view of the long bony hands and
  of the range of robe colours.
- `wookieepedia_rune_haako_fullbody.jpg` — full standing figure, described by the article
  itself as *"a typical Neimoidian."* Settles overall proportion and the stooped, hands-in
  posture. ⚠️ **Almost the entire figure is robe** — useful for silhouette-with-clothes, near
  useless for anatomy below the neck.
- `wookieepedia_royal_guard.jpg` — a Neimoidian Royal Guard in armour: the **grey** skin
  variant, the vertical jaw ridges, and canonical proof that the species has real soldiers.
  Stylised (*The Clone Wars* animation), and heavily helmeted, so treat line quality as the
  medium's.

## ruling
(empty — owner has not reviewed this race yet)
