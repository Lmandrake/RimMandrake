# Chiss

**defName**: `RSW_RimMandrakeChiss` (verified present in
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`). Matrix:
`Empire: R` — **rare**, and Imperial-only, so a Chiss in this campaign is an Imperial
officer-type sighting rather than a crowd filler.

## Sourced text (Wookieepedia)

**Current canon** (`/wiki/Chiss`). Chiss were **near-humans** — "their shape, features, and
dimensions were greatly similar to those of humans" — with these differences: **skin blue,
hair a shimmering blue-black, eyes a glowing red, and angular faces.** They were mistaken
for **Pantorans** (also blue-skinned) *except that Pantorans lack red eyes*. 🔑 Beyond
colouration: **"Chiss eyes were slightly better than those of humans, their visible spectrum
going into the infrared range. Additionally, their hearing was sharper and their reflexes
were faster."** The canon infobox's sole `distinctions` entry is **"Infrared vision."**
Origin **Csilla**; diet **omnivorous**; language **Cheunh**; described as **intimidating
beings**.

🔴 **The canon infobox has no mass and no lifespan**, and its `height` field is only the
relative note **"Much smaller than a Kilji"** — no figure. So **no canonical Chiss height,
mass or lifespan exists to cite.**

**Unusual abilities (canon).** Force-sensitivity, which the Chiss call **the Sight**, was
**"incredibly rare and manifested in limited abilities"**: **precognition = *Third Sight*,
telepathy = *Second Sight*.** **Force-sensitive Chiss were almost always female**, and
**their abilities diminished and eventually disappeared as they grew older.** Girls with the
ability were trained as **navigators** for the Chiss fleet through the Unknown Regions —
***ozyly-esehembo*, Cheunh for "sky-walker."** The existence of these Sights was among the
Ascendancy's best-kept secrets; Thrawn himself knew Third Sight well but did not know what
Second Sight could do.

**Behaviour / culture (canon).** Ruling class the **Aristocra**; legislature the **Syndicure**;
military the **Chiss Defense Force** and **Expansionary Defense Fleet**. Renowned in the
Unknown Regions for military might and a **non-intervention doctrine**, with a legend of being
**able to disable enemies without destroying them**. Eli Vanto on them: *"They're supposed to
be great warriors. Clever, resourceful, proud. Intensely loyal to one another, too."*
Outsiders who dislike them say **"blueskin."** Names are **three-part** (family / given /
social), e.g. Mitth'raw'nuruodo, shortened to a **core name** (Thrawn) in all but the most
formal use.

**Legends** (`/wiki/Chiss/Legends`) supplies the numbers and the environmental story the def
leans on. Infobox: **height 1.85 m (male), 1.7 m (female)** by 130 ABY; **skin colour "Blue to
silver"**; **hair black**; **eyes red**; distinctions **"Glowing red eyes"**;
**lifespan up to 80 standard years**; mass **empty**. Body text:
- 🔑 **"the shade of which depended on the oxygen content of their surroundings. The more
  oxygen present, the more intense the color of their eyes and skin tone."** A Chiss's blue is
  environment-variable, which is exactly why a single flat blue is wrong.
- **"While their hair was typically jet black, it did on rare occasions go gray with age
  (most Chiss believed that the development of gray hair was an indication of the siring of
  exceptional children)."**
- **A fully grown Chiss was typically between 1.6 and 2.1 meters**; average 1.7 m around
  36 ABY. **Male and female Chiss tended to be more powerfully built than Humans.**
- **They grew much faster than Humans: "a Chiss at the age of 10 held the physical maturity of
  a 20-year-old Human."** No adolescence; by ten they were ready for military service and
  cadet uniforms. **Up to 80 years, at which point venerable**; children 1–10, middle age
  51–62, old 63–79.
- **Csilla was once warm and tropical, then locked in a great ice age**; the Chiss survived
  by **living underground**, and **"their unique skin tone was the result of exposure to
  glacial minerals."** They built **cities among the glaciers** on **geothermal** power. This
  is the source that legitimises the def's cold-tolerance genes.
- **Highly reserved in their emotions**, rarely displaying feeling by smiling or warm
  gestures, and rarely vocal about anger or frustration.

## Visual brief

The four references agree on structure and **disagree on saturation in an informative way** —
and the Legends "blue to silver / oxygen-dependent" text explains the disagreement rather
than being contradicted by it.

**`wookieepedia_canon_infobox_thrawn.jpg`** (full-body canon infobox, *Rebels* CGI model,
1000×2630 — the best full-body reference in this directory):
- **Mid-tone cyan-leaning blue skin**, fairly desaturated and even, with cooler shadow
  under the jaw. Not a vivid cobalt.
- **Hair reads near-black with a blue sheen**, swept straight back off a high forehead —
  matching "shimmering blue-black" precisely. It is **not azure or bright blue.**
- **Eyes glow red** — a light-emitting red iris with no visible white sclera, sitting under a
  heavy straight brow.
- **Very angular face**: narrow, flat-planed cheeks, sharp cheekbones, straight jaw, thin
  **grey-mauve lips**. Nose and ears are ordinary human.
- **Build is ordinary human proportions** — tall and lean, no exaggerated mass. Consistent
  with `Body_Standard`.

**`wookieepedia_blue_skin_red_eyes.jpg`** (comic close-up) is the saturated end: **vivid
cobalt/periwinkle skin**, **jet-black hair**, **bright red irises with a light ring**, an
almost geometrically angular brow, and **dark blue-black lips**. High-oxygen end of the
Legends rule.

**`wookieepedia_legends_infobox.jpg`** (Legends infobox, two Chiss in scavenger/soldier gear)
is the **pale end and the most important corrective**: both figures are **grey-blue to
lavender, several steps toward silver**, clearly duller than the canon Thrawn cyan, with
**black hair** and **glowing red-orange eyes**. This is "blue to **silver**" made visible.

**`wookieepedia_chiss_females.jpg`** confirms it independently: two females with **pale,
almost silver-blue skin**, long **straight jet-black hair**, **glowing orange-red eyes**, and
**dark purple lips**, on the same angular bone structure.

🔑 **Reading across all four: the constants are (a) glowing red eyes with no white sclera,
(b) jet-black-to-blue-black hair, (c) an angular, flat-planed face — and the variable is the
blue itself, which runs cyan → cobalt → grey → near-silver.** A single fixed `Skin_Blue` is
the failure mode here.

**`donor_current_sprite.png` is weak evidence and is not a pawn sprite.** It is
`OR/OuterRim/XenotypeIcons/Xenotype_Chiss.png` (512×512 RGBA) — a **UI xenotype icon**, the
only Chiss-specific art in this repo. **There is no Chiss head, face or body art on disk at
all**: the def's head comes from `Outland_SvelteHead`, a gene that is **not defined in this
repo** (it resolves to the external Outer Rim – Galactic Diversity mod), so nothing here
authors the angular face canon calls out. Skin and eye colour come from the generic
`Skin_Blue` / `Eyes_Red` genes.

## Must show
- [ ] Glowing red eyes with no visible white sclera
- [ ] Hair reads jet-black to blue-black, not bright azure
- [ ] Angular, flat-planed face with sharp cheekbones and a straight jaw
- [ ] Skin blue, but the exact shade varies across individuals from cyan to cobalt to
  grey/near-silver — not a single fixed hue
- [ ] Ordinary human body proportions

## Engine limits
none known

## Source URLs

- https://starwars.fandom.com/wiki/Chiss — current canon; wikitext via
  `https://starwars.fandom.com/api.php?action=parse&page=Chiss&format=json&prop=wikitext`
  (18,490 chars, 2026-09-15). Appearance cites *Thrawn* (novel) and the 2018 Topps Masterwork
  Grand Admiral Thrawn card; the Sight cites *Thrawn: Alliances* and *Thrawn: Treason*.
- https://starwars.fandom.com/wiki/Chiss/Legends — Legends; wikitext via the same endpoint
  with `page=Chiss/Legends` (115,214 chars, 2026-09-15). Height/lifespan cite *Legacy Era
  Campaign Guide* and *Alien Anthology*; the glacial-mineral skin-tone origin cites
  *The Unknown Regions*; the oxygen-dependent shade and gray-hair note cite *Alien Anthology*.
- https://static.wikia.nocookie.net/starwars/images/f/ff/Thrawn_fullbody.png
  (File:Thrawn fullbody.png → `wookieepedia_canon_infobox_thrawn.jpg`)
- https://static.wikia.nocookie.net/starwars/images/1/1b/Aralani-Thrawn6.png
  (File:Aralani-Thrawn6.png, the article's "The Chiss had blue skin and red eyes" figure →
  `wookieepedia_blue_skin_red_eyes.jpg`)
- https://static.wikia.nocookie.net/starwars/images/6/6a/Chiss_EtU.png
  (File:Chiss EtU.png, the Legends infobox → `wookieepedia_legends_infobox.jpg`)
- https://static.wikia.nocookie.net/starwars/images/a/a3/ChissFemales-FF137.png
  (File:ChissFemales-FF137.png → `wookieepedia_chiss_females.jpg`)
- ⚠️ All four are served as **WebP** despite `.png` extensions; re-encoded to real JPEG
  locally, content otherwise unaltered.
- NOT fetched this pass: a starwars.com Databank Chiss page was not attempted.

## Candidate images

- `wookieepedia_canon_infobox_thrawn.jpg` — **the reference of record.** Full-body canon
  infobox render; settles blue-black swept hair, glowing red sclera-less eyes, angular
  flat-planed face, grey-mauve lips, ordinary human build and height.
- `wookieepedia_blue_skin_red_eyes.jpg` — comic close-up, the **saturated cobalt** end of the
  skin range with jet-black hair. Stylised line; palette is the point.
- `wookieepedia_legends_infobox.jpg` — Legends infobox, the **pale grey-to-silver-blue** end.
  The single most useful image for showing the blue is a *range*, not a value.
- `wookieepedia_chiss_females.jpg` — independent confirmation of the pale end plus long
  straight jet-black hair and dark purple lips.
- `donor_current_sprite.png` — **the xenotype UI icon, not a sprite.** Documents that no
  Chiss pawn art exists in this repo.

## Def-versus-canon contradictions (report only — not fixed here)

1. 🔴 **`PsychicAbility_Deaf` directly contradicts canon.** Chiss Force-sensitivity is *rare*,
   not *absent*: canon documents the Sight (Third Sight/precognition, Second Sight/telepathy),
   that Force-sensitive Chiss are **almost always female**, and that they are trained as
   **sky-walker navigators**. A blanket psychic-deaf gene makes a canonical Chiss archetype
   unreachable. Same failure class as the Rakata entry's psychic genes, inverted.
2. 🔴 **Infrared vision — the only entry in the canon infobox's `distinctions` field — has no
   gene.** Neither do the two other explicit canon senses: **sharper hearing** and **faster
   reflexes**. The def has no dark-vision/night-vision analogue and no reflex/move-speed gene.
   These are the species' three mechanical facts and all three are missing.
3. 🔴 **Hair colour is wrong.** Def carries only `Outland_HairColor_DarkAzure`. Canon is
   **"shimmering blue-black"**, Legends is **"typically jet black"**, and all four reference
   images show near-black. Azure is a bright blue and no source supports it.
4. 🔴 **`Hair_Grayless` contradicts a specific sourced detail.** Legends: Chiss hair
   **"did on rare occasions go gray with age,"** and Chiss read gray hair as a mark of having
   sired exceptional children. The def forbids it outright.
5. ⚠️ **A single `Skin_Blue` cannot express the canonical range.** Legends gives **"blue to
   silver"** with **shade varying by ambient oxygen**, and the images run cyan → cobalt →
   grey → near-silver. Compare the Cathar and Duros defs, which each carry three or four skin
   genes; the Chiss has one.
6. ⚠️ **Fast maturity is unrepresented.** Legends states a 10-year-old Chiss has the physical
   maturity of a 20-year-old human, with no adolescence and military service at ten. No gene.
7. ⚠️ **`Turn_Gene_HighBeautyStandard` + `AptitudeStrong_Social` + `Turn_Gene_NaturalLeader`
   are unsourced and cut against canon temperament**, which is **"highly reserved in their
   emotions,"** rarely smiling or making warm gestures. `AptitudeStrong_Intellectual` is well
   supported (tactical reputation, "clever, resourceful"); the social cluster is not.
8. ✅ **Sourced and correct — do not "fix" these:** `MinTemp_LargeDecrease` /
   `MaxTemp_SmallDecrease` are supported by Csilla's great ice age, underground survival and
   glacier cities (Legends); `Eyes_Red` matches both continuities; `Body_Standard` correctly
   invents no body size where canon gives no height and Legends gives a human 1.6–2.1 m; and
   **no lifespan gene** is right, Legends' 80-year cap being ordinary human.
9. ✅ **Namer is correct and unusually good.** `RSW_ChissNameGenerator` assembles
   multi-syllable multi-part names from `OR/OuterRim/Chiss/ChissNameparts1-14.txt`, matching
   canon's three-part family/given/social structure, and `<chanceToUseNameMaker>999</…>`
   forces it. No wrong-species namer here.

## ruling

(empty — owner has not reviewed this race yet)
