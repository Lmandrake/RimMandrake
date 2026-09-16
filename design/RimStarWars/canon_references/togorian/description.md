# Togorian

**defName**: `RSW_RimMandrakeTogorian` (verified present in
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Matrix placements `Jawa_WildsteamClan: S`, `Pirate: R`, `TribeCivil: R`.

⚠️ Togorian is one of the five species `design/Jawa/race_regen_architecture.md` §4.2
calls "deferred"; the def is present and placed, so `RACES_TODO.md` treats it as IN.
Not resolved here.

## Sourced text (Wookieepedia)

**Canon.** The article is a **stub** (2,325 chars of wikitext, `{{Species-stub}}`),
and this is nearly all of its body text:

> "**Togorians** were a sentient species of large, **feline** beings with
> **digitigrade feet**. Their bodies were covered in **short, thick fur** that could
> be **brown, white, orange or red with stripes**, and their **eyes could be yellow
> or green with a yellow hue**. Togorians had **retractable claws**, and were a
> **proud race. They moved with grace and spoke with a sibilant voice.**"

Infobox (canon): class **feline**; **hair (fur) black, brown, orange, white**; **eyes
green, yellow**; origin the **Togoria system**. **No height, mass, lifespan, habitat
or diet is given in canon** — UNMEASURED. Named individuals: **H'sishi**, a female
Togorian who owned the Amon Yinchom Dojo (*Thrawn*); **Jak'zin**, a male **Jedi
Knight** who encountered Count Dooku on Sullust (*Age of Republic — Count Dooku* 1).

**Legends** (`Togorian/Legends` — richer than canon, tag as Legends if used):

- **Height: males 1.8–2.0 meters, females 1.6–1.75 meters.** **Lifespan up to 79
  standard years.** Origin **Togoria**.
- "As a species, they were **large bipeds, with retractable claws on their hands and
  feet**. … They were covered in **gray-white to black fur, often with more colorful
  spots or stripes**. They had **extremely dense bone tissue, allowing them to endure
  greater physical trauma than beings with similar physiques**."
- They were "a feline **warrior** species", "known for their association with the
  **Mandalorians**, and the unique cultural divisions between their sexes. Both male
  and female Togorians were also noted for their **strong sense of honor**."
- **Society:** evolved as **nomadic hunters**; flying reptiles called **liphons**
  preyed on them, and they **domesticated the smaller flying mosgoths as mounts** for
  mutual protection. A rift then opened — **males wanted to continue as nomads,
  females wanted permanent camps** — which is the "cultural division between the
  sexes" the article leads on.
- Talon Karrde, quoted: *"I don't advise shooting a Togorian. It only makes them
  angry."*

**Unusual abilities.** Three, all from Legends: **retractable claws on hands *and*
feet**; **extremely dense bone tissue** giving above-normal trauma tolerance; and
**mosgoth riding** as a cultural rather than biological trait. Canon adds only the
claws. **Nothing in either canon gives a Togorian night vision, enhanced smell or
Force affinity** — do not invent them.

## Visual brief

Four images: the canon infobox (a comic panel), a painted RPG bust, a painted
Legends full figure and an inked line drawing. **They agree on the head and on the
stance, and they contradict the def's colour handling completely.**

- 🔑 **A true feline muzzle, not a furry human face.** Every image shows a short
  broad cat muzzle projecting forward from a flat brow, with a **small triangular
  leathery nose**, a defined philtrum and mouth, and **long white whiskers sweeping
  out from the muzzle sides** (`wookieepedia_male_torso_tfucg.jpg` has six-plus per
  side, longer than the head is wide). Whiskers appear in three of the four images
  and are **absent from all prose** — image evidence only, and they matter for
  silhouette.
- 🔑 **Upright pointed ears set high on the skull, with interior and tip tufts.** The
  TFUCG bust reads as a **lynx** — sharply tufted. The comic panel's are shorter and
  rounder. High and pointed is the constant; low or round-set is wrong.
- 🔑 **Eyes green or amber-yellow with visible vertical slit pupils**, set forward
  and close, under a heavy shelf brow that gives a permanently narrowed, scowling
  read. This matches the infobox's "green, yellow" exactly.
- 🔑 **A heavy ruff / mane of longer fur around the neck, cheeks and chest**,
  distinct from the short body coat, plus longer fringe fur down the outside of the
  forearms. Present in all four images and in **both sexes** — the canon infobox
  image is **H'sishi, a female**, and she carries a full ginger mane down the neck
  and arms. Do not make the mane a male-only feature.
- 🔑 **Digitigrade hind limbs, clearly drawn.** `wookieepedia_gg4_illustration.jpg`
  and `wookieepedia_legends_fullbody.jpg` both show a **long tarsus with a raised
  heel and weight carried on the toes**, ending in a broad three-to-four-toed foot
  with **long curved claws**. The canon text says "digitigrade feet" and the art
  agrees; this is a genuine body-plan difference from a RimWorld humanlike and any
  sprite is going to have to compromise on it (say so rather than hide it).
- **Hands are large with long curved claws**, drawn extended in the two action
  pieces and sheathed in the bust — consistent with "retractable".
- **Build: tall, heavy, top-heavy, wide-shouldered, forward-hunched**, with a thick
  neck and long arms. Consistent with the Legends 1.8–2.0 m male and with the def's
  `RSW_BodySizeGene_big`.
- **A long furred tail** is clearly drawn in `wookieepedia_infobox_thrawn_comic.jpg`,
  hanging behind the right leg. **No prose in either canon mentions a tail**, and it
  is not visible in the other three images (which are a bust and two front-on poses).
  Treat as **image-attested, prose-silent** — probably present, and a sprite that
  omits it is not provably wrong.

🔴 **Fur is STRIPED, and the prose colour list badly undersells it.** This is the
same failure the anooba entry exists to catch.
- `wookieepedia_male_torso_tfucg.jpg` shows **grey-white fur with strong dark tabby
  banding** across the crown, the cheeks, the shoulders and down the chest — a
  mackerel-tabby pattern, not a wash.
- The canon prose does carry it ("brown, white, orange or red **with stripes**") and
  Legends adds "often with **more colorful spots or stripes**", but the **infobox
  colour field lists only flat colours** — black, brown, orange, white — which is
  what a text-only prompt would read, and it would produce a flat-coloured cat.
- The comic panel (`wookieepedia_infobox_thrawn_comic.jpg`) is flat ginger with no
  stripes, so **unstriped individuals exist**; but the striped case is the one both
  prose lines call out, and the repo has no way to draw it at all (below).
- 🔴 **Grey-white is the Legends primary** ("gray-white to black fur") and is the
  colour of the clearest reference image. It is **absent from the def's colour
  genes.**

**No donor sprite exists, and what the game will actually draw is a vanilla human
head with fur on it.** There is no `togorian/` texture directory anywhere under
`src/RimStarWars/StarWarsRaces/Textures/`. The xenotype's only appearance gene is
`RSW_Furskin_shortfur`, whose `forcedHeadTypes` are `RSW_shortFurskin_Average1-3`,
`_Narrow1-3`, `_Heavy1-3`, `_Gaunt` — and every one of those points at a **base-game
RimWorld texture**, e.g. `Things/Pawn/Humanlike/Heads/FurCovered_Average1_Normal`
(`Defs/HeadTypeDefs/SW_HeadTypes.xml:1017-1018`). **That is a human face with fur,
with no muzzle, no whiskers, no slit pupils and no mane.** So the species' single
defining trait — that it is *feline* — is not represented on disk, and
`donor_current_sprite.png` is absent because there is no repo art to put there.

### 🔴 Def-versus-canon contradictions (report only, do not fix)

- 🔴 **The fur-colour genes are on the wrong channel and will do nothing.**
  `RSW_Furskin_shortfur` declares `<skinIsHairColor>false</skinIsHairColor>` and its
  description says outright that it "**uses the pawn's 'skin' color instead**"
  (`Defs/GeneDefs/SW_Genes.xml:1806-1815`). The Togorian xenotype supplies **five
  hair-colour genes** (`Hair_LightOrange`, `Hair_ReddishBrown`, `Hair_MidBlack`,
  `Hair_BrightRed`, `Outland_HairColor_DarkOrange`) and **zero skin-colour genes**,
  plus `Hair_BaldOnly` so no hair is drawn at all. **Predicted result: fur rendered
  in a default human skin tone, with all five canon-ish colours inert.** Verify in
  game before acting on it — but it is the single most consequential finding here.
- 🔴 **No feline head type.** A proper feline head *already exists in this mod* —
  `Heads/Cathar/{Male,Female}_Head_*.png` plus a `cathar/CatNose_*.png` attachment —
  and the Togorian does not use it. It borrows only the Cathar **icon**
  (`iconPath: RimMandrakeSW/OR/OuterRim/XenotypeIcons/Xenotype_Cathar`) while
  rendering with vanilla furred *human* heads. Cathar is a separate species with its
  own def (`RSW_RimMandrakeCathar`) and its own row in `RACES_TODO.md`, so the shared
  icon is also a mislabel.
- 🔴 **No stripe or marking gene of any kind.** Canon and Legends both call out
  stripes (and Legends spots); the def has no pattern gene, no `*_striped` head
  variant and no marking attachment. A Togorian will be flat-coloured, which is
  exactly the error this library was built to catch.
- **No grey/grey-white colour** among the colour genes, though Legends makes it the
  species primary and the clearest reference image is grey-white.
- **Nothing represents retractable claws** (canon *and* Legends, hands and feet) or
  **digitigrade feet** — the latter is asserted in the def's own `<description>` and
  then unimplemented. `Robust` + `Pain_Reduced` are a fair stand-in for Legends'
  "extremely dense bone tissue"; that one is fine.
- 🔴 **`AptitudePoor_Intellectual` and `AptitudePoor_Social` are contradicted by
  canon.** The canon stub's characterisation is "**a proud race. They moved with
  grace and spoke with a sibilant voice**"; Legends adds a "strong sense of honor".
  The two named canon Togorians are a **dojo owner** and a **Jedi Knight**. Nothing
  sources a deficit in either stat.
- **`Aggression_Aggressive` is only half sourced** — a warrior species with an
  honour code and a "shooting one only makes them angry" reputation is not the same
  as baseline aggression. Recorded as thin, not wrong.
- **`MaxTemp_SmallIncrease` is unsourced.** Nothing describes Togoria as hot or
  Togorians as heat-adapted; the fur gene's own `ComfyTemperatureMin -10` points the
  other way. On a desert world the heat bonus is convenient, so flag it as a
  gameplay choice rather than canon.
- **`Ears_Cat` cannot be verified from this repo** — it is referenced by the
  xenotype and by `gen_races_mod.py` but **defined nowhere in `src/`**, so it comes
  from a dependency mod. Whether a Togorian actually gets cat ears in game is
  therefore not answerable from disk.
- **Two typos in the shipped def text**: `<description>` reads "**Togirian** were a
  sentient species of large, feline beings with **digitgrade** feet" — the species
  name is Togorian and the word is digitigrade. The file is generated, so the fix
  belongs in `gen_races_mod.py`, not the XML.

## Must show
- [ ] Short, broad, forward-projecting feline muzzle with a small triangular leathery nose and long white whiskers sweeping out from its sides
- [ ] Upright, high-set, pointed ears with interior/tip tufts
- [ ] Green or amber-yellow eyes with visible vertical slit pupils, set forward and close under a heavy brow
- [ ] A heavy ruff/mane of longer fur around the neck, cheeks and chest, present on both sexes
- [ ] Fur is striped (tabby banding), not a flat solid colour — grey-white with dark banding is the best-attested pattern
- [ ] Digitigrade hind limbs with a raised heel, ending in a broad multi-toed foot with long curved claws

## Engine limits
none known — the entry attributes the current render (a vanilla furred-human head with no muzzle, whiskers, slit pupils or mane) to the def's gene choices (`RSW_Furskin_shortfur` pointing at base-game furred-human `HeadTypeDef`s, and a fur-colour gene wired to the wrong channel) rather than to a pipeline constraint; a proper feline head already exists in the mod (Cathar) and is simply not used here.

## Source URLs

- https://starwars.fandom.com/wiki/Togorian — canon article, a **stub**. Direct HTML
  is Cloudflare-walled; wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Togorian&format=json&prop=wikitext`
  (200, **2,325 chars** — genuinely that short, not truncated, 2026-09-15).
- https://starwars.fandom.com/wiki/Togorian/Legends — Legends article, same API route
  (200, 15,856 chars, 2026-09-15). **The heights, lifespan, dense bone tissue,
  grey-white fur, spots, Mandalorian association, mosgoth domestication and the
  sex-based cultural split are all Legends-only** — the canon stub carries none of
  them. Exactly the `/Legends` case the agent brief warns about.
- https://static.wikia.nocookie.net/starwars/images/5/50/Togorian-Thrawn3.png (File:Togorian-Thrawn3.png, canon infobox image, H'sishi in *Thrawn* 3 → `wookieepedia_infobox_thrawn_comic.jpg`)
- https://static.wikia.nocookie.net/starwars/images/0/02/TogorianTorso-TFUCG.png (File:TogorianTorso-TFUCG.png, "a male Togorian", *The Force Unleashed Campaign Guide* → `wookieepedia_male_torso_tfucg.jpg`)
- https://static.wikia.nocookie.net/starwars/images/4/44/Togorian.jpg (File:Togorian.jpg, Legends infobox image → `wookieepedia_legends_fullbody.jpg`)
- https://static.wikia.nocookie.net/starwars/images/c/cd/Togorian_GG4.jpg (File:Togorian GG4.jpg, *Galaxy Guide 4* line art → `wookieepedia_gg4_illustration.jpg`)
- NOT fetched this pass: no `starwars.com/databank` page for Togorian was attempted;
  the canon stub cites none.

## Candidate images

- `wookieepedia_male_torso_tfucg.jpg` — **the reference of record for the head.** A
  painted three-quarter bust of a male: grey-white **mackerel-tabby striping** across
  crown, cheeks, shoulders and chest; long white whiskers; tufted lynx ears; **green
  slit-pupilled eyes**; pink-brown triangular nose; heavy white cheek ruff. This is
  the image that settles stripes-versus-flat and it is the one to draw from.
- `wookieepedia_infobox_thrawn_comic.jpg` — **the canon infobox and the reference of
  record for the tail and the female case.** A comic panel of H'sishi: flat ginger
  fur, long mane down neck and arms, green eyes, upright ears, and a **clearly drawn
  long furred tail**. Comic art, so flat colour and simplified line — treat palette
  as the colourist's, and note it is an **unstriped** individual.
- `wookieepedia_legends_fullbody.jpg` — **the reference of record for the body plan.**
  A painted full figure, front-on: heavy top-heavy build, hunched shoulders, huge
  clawed hands, and unmistakable **digitigrade legs** with a long raised heel. The
  olive-khaki fur here is an outlier against every colour either canon lists — treat
  the hue as an artefact of the source art, not as an attested colour.
- `wookieepedia_gg4_illustration.jpg` — inked line art, action crouch. No colour at
  all, so useless on palette, but the best image for **claws and feet**: long curved
  claws extended on both hands and both feet, digitigrade stance, open fanged mouth.
  Late-1980s RPG-sourcebook style, so proportions are exaggerated.

## ruling

(empty — owner has not reviewed this race yet)
