# Dathomirian

**defName**: `RSW_RimMandrakeDathomirian`, label `Dathomirian`
(`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
⚠️ **Matrix tier `—`**: the def ships but its
`race_faction_assignment.prefill.json` entry is **empty `{}`** — no faction spawns
it. `RACES_TODO.md` records that whether this is a deliberate cut-but-not-deleted or
an oversight is not written down anywhere found.

🔑 **Dathomirian is a hybrid/derived population, and three different things get
conflated into "how a Dathomirian looks." This entry separates them:**
**(a) Zabrak inheritance**, **(b) Dathomirian skin and horn dimorphism**, and
**(c) markings — which split again into NATURAL striping, APPLIED tattoo, and
CLOTH.** The last is where a text prompt goes wrong: a Nightsister is not
red-skinned, she is a pale-skinned woman wrapped in red cloth.

## Sourced text (Wookieepedia)

### (a) Zabrak inheritance — Dathomirians are a subspecies of Zabrak
From `Zabrak` (canon): Zabraks were **near-humans** that *"had evolved to be tough
due to the nature of their homeworld Iridonia."* Sourced Zabrak traits, all of which
a Dathomirian inherits:

- 🔑 **Two hearts**, *"which allowed them to pump oxygenated blood around their
  systems more quickly than other species meaning they could go faster for longer."*
  An **endurance** trait, explicitly — not a strength or toughness trait.
- **Carnivorous diet.**
- 🔑 **"Some Zabraks possessed a ring of small, vestigial horns that ran from high on
  their brow round to the back of their head."** *"The horns of males were generally
  more developed than those of females, although horn placement, length, and
  thickness varied enormously across the species."* Note **ring** and **vestigial**:
  the horns encircle the crown, they are not two forward-facing devil horns.
- Infobox distinctions: **vestigial horns, two hearts, facial tattoos.**
- **Zabraks could be Force-sensitive.** Language **Zabraki**.
- The two Zabrak subspecies are **Dathomirian** and **Iridonian**.
  (⚠️ `RACES_TODO.md` already records that `RSW_RimMandrakeIridonian` names a demonym,
  not a species — this is the same tree.)

### (b) Dathomirian skin, hair, eyes and horns
*"Dathomirians, also known as Dathomirian Zabraks and culturally as Dathomiri or
Dathmiri, were a subspecies of Zabrak native to the planet **Peridea** in the distant
past and the world of **Dathomir** afterward."* On Peridea they founded the **Witch
Kingdom of the Dathmiri** and **rode the purrgil** through hyperspace.

*"Dathomiri showed considerable sexual dimorphism."* Verbatim:

- 🔑 **"Female Dathomiri had white, blue, or gray skin with various hair types."**
  The infobox adds **tan** (females only, *The Mandalorian* Chapter 13).
- 🔑 **"Male skin was commonly orange or yellow. Few had red skin."** Maul is
  explicitly cited as one of the **few** red ones — i.e. **Maul's red is the rare
  case, not the species default.**
- 🔑 **"Male Dathomirians had horns, whereas females did not."** Cranial horns are
  listed in the infobox distinctions as **males only**, cited to the official
  `starwars.com` Databank.
- Hair colour: **"Various (females only)"** — the infobox gives no male hair colour
  at all, consistent with the males being depicted bald.
- Eye colour, all sourced: **black, brown, gold, green, red, silver, teal, violet,
  yellow.** An unusually wide sourced range.
- **Height, mass and lifespan are all UNSOURCED** — the infobox fields are blank and
  the body gives no figure. Do not invent any of the three.

### (c) Markings — the part that must be got right
Verbatim, and read the subject of each clause carefully:

> *"The Dathomiri had **tattoos** on their body that represented their **tribal
> heritage**. The **male** Zabraks, particularly those belonging to the
> **Nightbrothers**, had **natural striping** which they **embellished with
> tattoos**. The **females**, particularly those belonging to the **Nightsisters**,
> had **more subtle tattoos** that were **in contrast to their pale skin**."*

So:

- **Natural striping is a male trait** — it is pigmentation, present without any
  ritual, and the tattoo work is laid *on top of* it. A male Dathomirian stripped of
  all body paint is still striped.
- **Female markings are tattoo, not pigment**, and are described as **subtle** and
  read by **contrast against pale skin** — the opposite design problem to the males.
- 🔑 **Tattoo material is sourced**: *"Tattoos were made using the **mushling**. The
  pods of the mushling were **boiled down into a yellow paste**, and then mixed with
  pigments, like **clay and ash**, to create a variety of colors."* Clay-and-ash
  pigment is why the female markings read chalky grey rather than ink-black.
- ⚠️ **Nothing found sources the Nightsisters' red garments as anything other than
  clothing**, and nothing found says the female pallor is magically induced — canon
  lists white/blue/gray/tan as **skin colour** fields on the species. Treat pallor as
  skin, red as cloth.

### Unusual abilities
*"Many Dathomiri were Force-sensitive, including the witches that lived on their
native planet. **Some male Dathomiri were capable of rudimentary Force abilities**,
while **a few, like Savage Opress and Maul, were exceptionally good at manipulating
the Force due to their training.**"*

🔑 Read the gradient: **not** a uniformly powerful Force species. Females (the
witches) are the Force-practising side; ordinary males get *rudimentary* ability; the
two famous exceptions are attributed to **training**, not to blood. Anything modelling
Dathomirians as innately strong psykers overshoots the source.

## Visual brief

**`wookieepedia_dathomirian_infobox.jpg`** (`File:Dathomiri.png`, 1100×1200) is the
**reference of record** and it is exactly the right image for this species, because
it shows a male and a female side by side:

- **Female (left)**: **bone-white to pale pearl-grey skin**, completely **hairless
  and hornless**, a narrow long skull, dark eyes, and **soft dusky-grey shading
  around the eye sockets and over the brow** — the "subtle tattoos in contrast to her
  pale skin," and it reads as smudged pigment, not as ink line-work. Lean, long-limbed
  build. Costume is dark leather with red panels.
- **Male (right)**: **warm red-orange skin** with **black striping radiating across
  the face** and, on the crown, **a ring of short dark horns** encircling the top of
  the skull rather than projecting forward. **Yellow eyes.** Bald. Bulkier than the
  female through chest and shoulders. So the two sexes differ in **skin hue, horns,
  marking style and build** all at once.

**`wookieepedia_dathomirian_wallpaper.jpg`** (`File:Shatterpoint-Dathomirianwallpaper.png`,
1002×1602, captioned by the wiki *"Examples of male and female Dathomiri"*) widens the
palette and confirms the sourced fields:

- **Foreground male: saturated golden-YELLOW skin with heavy black striping and a
  full crown of dark horns.** This is the "commonly orange or yellow" male the text
  describes and the corrective to assuming every male Dathomirian is Maul-red.
- **Background female: grey-green skin with bold black facial markings** — a
  Talzin-type. Her markings are **much less subtle** than the infobox female's, so
  "subtle" is a tendency, not a rule.
- **A third figure, a bald male with pale skin in red robes** — again showing the
  **red is the garment.**

**`wookieepedia_nightsisters.jpg`** (`File:Nightsisters-SWE.jpg`, 936×704, five
Nightsisters together) is the single most useful image for the (c) distinction, and
🔴 **this is where a text-only prompt fails hardest:**

- **Every one of the five has chalk-white to cool bone-grey skin.** None is
  red-skinned.
- 🔑 **The red is entirely CLOTH** — strips of red and rust-orange fabric wound in
  spirals up the legs and arms, red hoods, red bodices, red wraps. From a distance the
  whole group reads red; the skin underneath is white. **A "red Nightsister" is a
  wrapping, not a pigment.**
- **Dark grey markings radiating from the eyes** across the cheekbones and temples on
  every face, kohl-like and soft-edged — consistent with clay-and-ash pigment.
- **Hair varies as sourced**: platinum-white bobs, white braids, dark hair under
  hoods.
- **Eyes are pale with warm red or amber irises** on several — inside the sourced list.
- ⛔ **No horns on any of the five**, confirming the females-only-hornless rule.
- Build: uniformly **slender and long-limbed.**

**`wookieepedia_nightbrother_archer.jpg`** (`File:NightbrotherArcher.png`, 2560×2560,
the highest-resolution image in this entry) is the best male reference and it carries
one finding of its own:

- 🔑 **A ring of short, blunt, dark horns around the upper circumference of the skull**
  — exactly the sourced "ring of small vestigial horns from high on the brow round to
  the back of the head." Best confirmation of the horn *arrangement* anywhere in the
  set. They are small and stubby, not long spikes.
- 🔑 **Heavy dark-brown-to-black striping running over the face, scalp, chest,
  shoulders and arms**, following the body's contours — this is the **natural
  striping**, and note it is **not confined to the face**: the text says "on their
  body."
- 🔑 **A chalk-WHITE circular sigil painted on the sternum, sitting clearly on top of
  the striping** — the "embellished with tattoos" layer, visibly a different material
  and colour from the stripes under it. This image lets the two layers be told apart,
  which is the whole point of the (c) split.
- ⚠️ **His skin is a weathered dusty brown-grey, not orange, yellow or red.** That is
  outside the three sourced male colours. The image is from *Jedi: Fallen Order*, whose
  Nightbrothers are deliberately desaturated. Recorded as **widening** the observed
  male range rather than as an error — but the *sourced* fields remain orange/yellow/
  rarely-red.
- Pale, near-white eyes; bald; minimal grey loincloth.

**`wookieepedia_mother_talzin.jpg`** (`File:Mother_Talzin_SWDL.png`, 1440×1800) is
kept as a **negative reference for the ordinary Dathomirian**: Talzin is the
Nightsister Clan Mother, and her look (elongated skull, horn-like head ornaments,
green-grey pallor, elaborate robes) is a leader's regalia plus one individual's
morphology. Do not generalise it.

⚠️ **No `donor_current_sprite.png`.** The Dathomirian xenotype has species head art in
the mod (`RSW_DathomirianHead` forces eight head types,
`RSW_Dathomirian_{Male,Female}0-3`, and `RSW_ZabrakHornsMale` supplies five horn
textures `OR/OuterRim/Genes/Headbone/Zabrak0-4`), but **none of those textures is in
this repo** — they live in the deployed mod folder under
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`. Nothing here compares
canon against the sprite the player sees.

## Must show
- [ ] Female: bone-white to pale pearl-grey skin, hairless and hornless
- [ ] Male: warm red-orange, golden-yellow, or (rarely) red skin, with black striping and a ring of short, stubby horns encircling the crown (not two forward-facing devil horns)
- [ ] Male natural striping runs across the face, scalp, chest, shoulders and arms, not just the face
- [ ] Female markings read as soft, smudged grey/dark tattoo shading in contrast to pale skin, not bold ink line-work (though bolder-marked females are also attested)
- [ ] Nightsister red is cloth — strips of red/rust fabric wound over chalk-white to bone-grey skin, never a skin pigment
- [ ] Horns present only on males; females are hornless

## Engine limits
none known — no species-specific shader or mask constraint is recorded for this head in the entry or brief (no `donor_current_sprite.png` exists in-repo to check against).

## Def-versus-canon (flagged — not fixed)

`RSW_RimMandrakeDathomirian`. The `<description>` is unusually good — it states the
Zabrak subspecies relationship and the horn/skin dimorphism correctly. The gene list
does not follow it:

- 🔴 **`RSW_FemalePaleSkin` is `(200,200,200)` light grey and is the ONLY female skin
  gene.** Canon gives females **white, blue, gray AND tan** — four sourced colours.
  Blue and tan cannot roll at all, and the single grey misses the bone-**white** that
  the sourced Dooku line makes iconic (*"There was a woman. With bone-white skin."*).
- 🔴 **Male skin genes are `RSW_MaleOrangeSkin`, `RSW_MaleRedSkin`,
  `RSW_MaleYellowSkin` — all three weighted alike.** Canon: *"Male skin was commonly
  orange or yellow. **Few** had red skin."* Red should be rare; as shipped it is one
  chance in three.
- 🔴 **No striping or tattoo gene of any kind.** The species' two infobox distinctions
  are **cranial horns** and **facial tattoos**; only the horns are represented
  (`RSW_ZabrakHornsMale`). The **natural male striping** — sourced, and the most
  recognisable thing about a Dathomirian male — has no gene, and neither do the
  females' subtle tattoos. This is the largest gap in the def.
- 🔴 **`Hair_Gray` is the only hair gene, and it applies to both sexes.** Canon gives
  females **"various" hair types** (the images show platinum-white, white braids and
  dark hair) and gives males **no hair colour at all** — the males are consistently
  bald. `Outland_BaldMale` is present, which is right; forcing every female to grey
  hair is not.
- 🔴 **No two-hearts, endurance or carnivore gene.** *Two hearts letting them "go
  faster for longer"* is the flagship sourced Zabrak physiology and is absent. `Robust`
  and `Outland_ThickSkin` gesture at "evolved to be tough" but express toughness, not
  the sourced **stamina**.
- 🔴 **`Turn_Gene_TraitGrandeur` and `Aggression_HyperAggressive`.** Nothing sources
  either. Canon's behavioural material is about **tribal heritage, witch clans and
  Force practice**; hyper-aggression is Maul's and Savage Opress's characterisation
  being read back onto a whole population, and Opress is explicitly a
  **magically-augmented** individual.
- ⚠️ **`Turn_Gene_LatentPsychic` applies uniformly to both sexes.** Canon is graded:
  the **witches** (female) are the Force practitioners, **some males** manage only
  *rudimentary* abilities, and the famous exceptions are attributed to **training**.
  A flat species-wide latent psychic gene flattens the sourced dimorphism — and the
  Force dimorphism is arguably the most interesting thing about the species.
- ⚠️ **`Outland_LowFertility`** — unsourced. Canon has the Nightsisters as a large
  clan and the Nightbrothers as a substantial male village population.
- ⚠️ **`MeleeDamage_Strong`, `Turn_Gene_Duelist`, `Pain_Reduced`** — unsourced as
  species traits.
- ⚠️ **Both `Body_Standard` and `Body_Hulk` are listed.** Canon's dimorphism is in
  **horns, skin and markings**; the images show males only modestly bulkier. A hulk
  body is not sourced, and no gene ties either body to a sex.
- ⚠️ **No lifespan or height gene** — correct by omission, since canon sources none.
  Recorded so a later pass does not invent one.
- ⚠️ **`nameMaker` is `RSW_NamerPersonPureblood`** — the **Sith Pureblood** namer, on
  a Zabrak subspecies with no Sith ancestry. Wrong-species namer, the same class of
  defect the earlier batch found on `RSW_RimMandrakeIthorian`
  (`RSW_KoTOR_NamerSullustan`).
- ⚠️ **`factionlessGenerationWeight` is 0 and no faction places it**, so as shipped
  this xenotype can never appear. Consistent with the matrix's empty entry; noted so
  the owner can decide.
- ✅ Correct and sourced: `RSW_ZabrakHornsMale` (males only, five horn textures,
  matching the sourced male-only horns and *"placement, length and thickness varied
  enormously"*), `RSW_DathomirianHead`, `Beard_NoBeardOnly`, `Outland_BaldMale`.

## Source URLs
- https://starwars.fandom.com/wiki/Dathomirian — wikitext via
  `https://starwars.fandom.com/api.php?action=parse&page=Dathomirian&format=json&prop=wikitext`,
  37,379 chars, 2026-09-15. Canon article (no `{{Top|leg}}`).
- https://starwars.fandom.com/wiki/Zabrak — same API route, 38,602 chars, 2026-09-15.
  Source of all Zabrak-inheritance material.
- `https://www.starwars.com/databank/dathomirian` — cited *by* the Wookieepedia
  infobox as the source for cranial horns (males only). ⚠️ **Not independently
  fetched this pass**; the horn claim is taken from the article's citation of it, and
  is corroborated by the article body and by every image.
- `Nightsister` and `Nightbrother` are both **redirects** (26 and 27 chars) — no
  separate species-appearance article to pull.
- https://static.wikia.nocookie.net/starwars/images/d/d2/Dathomiri.png → `wookieepedia_dathomirian_infobox.jpg` (1100×1200)
- https://static.wikia.nocookie.net/starwars/images/9/9c/Shatterpoint-Dathomirianwallpaper.png → `wookieepedia_dathomirian_wallpaper.jpg` (1002×1602)
- https://static.wikia.nocookie.net/starwars/images/4/40/Nightsisters-SWE.jpg → `wookieepedia_nightsisters.jpg` (936×704)
- https://static.wikia.nocookie.net/starwars/images/7/72/NightbrotherArcher.png → `wookieepedia_nightbrother_archer.jpg` (2560×2560)
- https://static.wikia.nocookie.net/starwars/images/5/5d/Mother_Talzin_SWDL.png → `wookieepedia_mother_talzin.jpg` (1440×1800)

## Candidate images
- `wookieepedia_dathomirian_infobox.jpg` — **the reference of record.** Male and
  female side by side; settles the whole dimorphism in one frame: hornless pale-grey
  hairless female with soft grey eye-shading, versus horn-ringed red-orange male with
  black facial striping and yellow eyes.
- `wookieepedia_nightbrother_archer.jpg` — **best male reference**, and the only image
  that lets **natural striping** and **applied paint** be told apart (dark contour
  stripes with a chalk-white sigil laid over them). Best view of the horn **ring**.
  ⚠️ Its dusty brown-grey skin is outside the three sourced male colours — treat the
  hue as this game's art direction, not as canon.
- `wookieepedia_nightsisters.jpg` — 🔑 **the image that corrects the most common error.**
  Five Nightsisters, all chalk-white-skinned; **all the red is cloth.** Confirms
  hornless females, varied hair, and soft grey radiating eye-markings.
- `wookieepedia_dathomirian_wallpaper.jpg` — wiki-captioned "Examples of male and
  female Dathomiri." Confirms the **yellow** male (the commonest sourced colour) and a
  grey-green boldly-marked female, i.e. "subtle" is a tendency, not a rule.
- `wookieepedia_mother_talzin.jpg` — **negative reference.** Nightsister Clan Mother:
  her elongated skull, ornament horns and green-grey pallor are one individual plus
  regalia, not a species baseline.

## ruling
(empty — owner has not reviewed this race yet)
