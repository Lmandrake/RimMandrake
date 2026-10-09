# Feeorin

**defName**: `RSW_RimMandrakeFeeorin`
(`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Note `<chanceToUseNameMaker>0</chanceToUseNameMaker>` — the `RSW_KoTOR_NamerFeeorin`
namer is declared and then never fires.

## Sourced text (Wookieepedia)
⚠️ **The canon `Feeorin` article is a stub** (2,546 chars, tagged `{{Species-stub}}`)
and contains no biology section at all. **Everything substantive is on
`Feeorin/Legends`** — the page-title trap. Both are cited below, and which page each
fact comes from is marked.

**Canon page.** Feeorins are a sentient species **with thick tendrils hanging from the
back of their heads**. Infobox: skin **blue** (*Darth Maul* (2017) 1) or **green**
(*Rebels Magazine* 31, "Off the Rails"); eyes **yellow**; sole distinction **head
tendrils**. **Height, mass, lifespan, origin, habitat, diet and language are all
EMPTY** — no homeworld is sourced in canon, and no measurement of any kind exists. Do
not invent one. Attested individuals: **Warjak**, a gladiator who held the title of
champion of the Outer Rim Carve-up during the early Imperial era (*Ezra's Gamble*), and
**Zira**, a female pirate ("Off the Rails"). First canonical appearance: *Ezra's
Gamble*, a *Star Wars Rebels* junior novel by Ryder Windham, 2014.

**Legends page** (`Feeorin/Legends`), *Biology and appearance*, in full: the average
Feeorin had **thick tendrils hanging from the backs of their heads (similar to those of
the amphibious Nautolans) and much smaller and thinner ones hanging from their face**.
They had **mottled skin ranging from yellow to green and blue, with a few individuals
even having jet-black or white skin pigmentation**. **The Feeorin could live for up to
four hundred years, and due to a unique metabolism, they grew stronger with age rather
than weaker.** **Curiously, some Feeorins had noses while others lacked any nasal
openings.**

**Behaviour** (Legends). The Feeorin believed the spirits of their fallen **Elders**
resided at the **Sanctum of the Exalted** on **Odryn**, where they forged the planet's
seasons; outsiders present there was a violation of the **Rime Feeorin**, the species'
ancient code. **Feeorin names are mostly simple, no more than 4 or 5 letters.**

## Visual brief
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."**
No live-action Feeorin exists. Added three realistic Legends depictions: a painted head study from the *Knights of the Old Republic Campaign Guide* (`wookieepedia_feeorin_kotorcg_legends.jpg`), Raven Mimura's *Ultimate Alien Anthology* painting (`wookieepedia_feeorin_uaa_legends.png`), and the near-photoreal game CGI gladiator Tarko-se from *The Force Unleashed II* (`wookieepedia_feeorin_tfu2_tarkose.png`). The only canon image, the *Darth Maul* (2017) 1 comic panel, is KEPT ONLY as animated/negative reference for the canon tendril count — it is not a style target.

**`wookieepedia_feeorin_kotorcg_legends.jpg` — the realistic reference of record for the head** (painted bust):
- **Skin is a cool slate blue-grey-teal**, smooth and leathery with fine wrinkling.
- **The face is heavily ridged and craggy**: a heavy furrowed brow ridge, deep vertical and diagonal creases from the eyes down the cheeks, a broad flat nose ridge, a wide downturned mouth and a heavy jaw, with **short thick fleshy barbels/tendrils hanging from the chin and jaw**. Small, deep-set amber eyes.
- 🔴 **Two thick, smooth head-tails** (lekku-like) sweep back from the crown and hang over the shoulders, banded with gold rings — **two, not a dozen.**

**`wookieepedia_feeorin_tfu2_tarkose.png`** (game CGI, *The Force Unleashed II*, Tarko-se roaring): **olive/yellow-green leathery skin**, the same ridged brow and creased face, **thick head-tails and jaw tendrils**, an enormous open mouth, a massive armoured gladiator's build.

**`wookieepedia_feeorin_uaa_legends.png`** (realistic painting, full body): 🔴 **mauve-grey to lilac-purple skin**, a ridged bald head with **several thick head-tails** falling to the shoulders and short chin tendrils, a heavy broad-shouldered body in a red jumpsuit with a blaster rifle.

🔴 **The realistic and animated versions disagree on the tendrils and the colour.** The canon comic (`wookieepedia_feeorin_2017darthmaul1.png`) draws **a dozen or more ropy tendrils** in a paler yellow-green over a **turquoise-cyan** body. The realistic Legends depictions draw **two to a few thick head-tails plus short jaw barbels**, on **slate blue-grey, olive-green or mauve-purple** skin. Constant across all four: bald ridged skull, heavily creased craggy face, heavy jaw, head-tails from the back of the skull, and a big, powerful build. 🔴 **Purple IS attested** (UAA painting), so the def's `Skin_Purple` is not baseless after all — it is the Legends painting's colour.

🔴 **`donor_current_sprite.png` is essentially empty.** It is a 4 KB, almost entirely
transparent canvas carrying **two small black curved eye marks and nothing else** — no
head, no tendrils, no jaw, no skin. Whatever the mod renders for a Feeorin today, this
file is not it, and the species' one defining feature (the tendril mass) has no art
here at all. Do not treat this as evidence about anything except that art is owed.

## Must show
- [ ] Thick head-tails sweeping back from the crown of a bald skull and hanging over the shoulders (two to several in the realistic depictions; a dozen in the canon comic)
- [ ] Short thick fleshy barbels/tendrils hanging from the chin and jaw
- [ ] Heavily ridged, craggy face: heavy furrowed brow, deep vertical/diagonal cheek creases, heavy jaw, small deep-set eyes
- [ ] Leathery skin in the blue-grey/teal to olive-green range (mauve-purple also attested)
- [ ] Big, broad-shouldered, thick-limbed, visibly powerful build
- [ ] Realistic rendering: leathery wrinkled skin under natural lighting, no outlines, no comic shading

## Engine limits
none known — the entry records no shader or mask constraint for this head; the current
donor sprite is an essentially blank canvas (two eye marks only), which is a missing-art
gap rather than a rendering constraint.

## Def-versus-canon (flagged)
- 🔴 **`DiseaseFree` + `TotalHealing` are unsourced and enormous.** Canon says only
  that a unique metabolism made them **grow stronger with age rather than weaker**.
  That is a strength-over-time trait, not disease immunity and not total regeneration.
  These two genes are the largest invented power in this entry.
- 🔴 **`Outland_EggLayer` is unsourced.** Nothing in either the canon or Legends
  article says Feeorin lay eggs.
- 🔴 **`Eyes_Red` and `Outland_Eye_Orange` are unsourced.** The only canon eye colour
  is **yellow**, which `Outland_Eye_Yellow` correctly provides — the other two should
  be justified or dropped.
- 🔴 **`Skin_Purple` is unsourced in the text (though the UAA painting is mauve-purple), and GREEN — one of only two canon colours — is
  missing.** The list is `Skin_Blue`, `Skin_Purple`, `RSW_Skin_Turquoise`. Green
  (*Rebels Magazine* 31) has no gene; jet-black and white (Legends outliers) have none
  either; and **no gene expresses the sourced mottling**.
- ⚠️ **`Aggression_Aggressive`, `Turn_Gene_TraitGrandeur`, `AptitudePoor_Plants`,
  `AptitudePoor_Medicine` are unsourced.** Two attested individuals — a gladiator and a
  pirate — are a thin basis for a species-wide aggression gene, and neither article
  says anything about plants or medicine.
- ⚠️ **`chanceToUseNameMaker` is 0**, so Feeorin pawns get default names while canon
  gives a specific naming convention (**simple names of 4–5 letters**) and the mod
  already ships a namer for them.
- ⚠️ **The species' strength trait is modelled as flat, not age-scaling.**
  `MeleeDamage_Strong` + `Robust` + `Body_Hulk` + `RSW_BodySizeGene_bigger` make a
  Feeorin strong at every age; canon's distinctive point is that they get **stronger as
  they get older**. Whether RimWorld can express that is a separate question, but the
  divergence should be a recorded choice rather than an accident. Also note **no height
  or mass is sourced**, so `bigger`/`Hulk` rest on the images and the gladiator cite,
  not on a number.
- ✅ Correct and canon-supported: **`RSW_Headbone_nautolan`** (the Legends text names
  Nautolan tendrils explicitly — a good call), **`RSW_Beard_chintendril`** (the smaller
  thin facial tendrils), **`RSW_FacialRidges_bumpy`** and **`Jaw_Heavy`** (both visible
  in the image), **`RSW_lifespan_quad`** (400 years ≈ 4× human — sourced),
  **`Hair_BaldOnly` + `Beard_NoBeardOnly`** (bald), **`RSW_Skin_Turquoise`** (matches
  the image closely).
- Unmodelled canon variant: **some Feeorin have noses and some have no nasal openings
  at all** — a genuine sourced split with no representation.

## Source URLs
- https://starwars.fandom.com/wiki/Feeorin (canon article — a **stub**; wikitext via
  `https://starwars.fandom.com/api.php?action=parse&page=Feeorin&format=json&prop=wikitext`,
  2,546 chars, 2026-09-15)
- https://starwars.fandom.com/wiki/Feeorin/Legends (**where the biology actually is**;
  wikitext via
  `https://starwars.fandom.com/api.php?action=parse&page=Feeorin/Legends&format=json&prop=wikitext`,
  8,119 chars, 2026-09-15)
- File:Feeorin-2017DarthMaul1.png — the canon infobox image, from *Darth Maul* (2017) 1
  → `wookieepedia_feeorin_2017darthmaul1.png`
- NOT on disk: the Legends article's inline images (Rav, a Feeorin with cybernetics; and
  a second unnamed Feeorin). Both would be worth fetching if a second reference is
  wanted, since the single canon image cannot show variation.

## Candidate images
- `wookieepedia_feeorin_kotorcg_legends.jpg` — **realistic reference of record for the head.** Painted bust, *Knights of the Old Republic Campaign Guide* (Legends): slate blue-grey skin, ridged craggy face, chin barbels, two banded head-tails; file `Feeorin KotORCG.jpg` — https://static.wikia.nocookie.net/starwars/images/5/54/Feeorin_KotORCG.jpg/revision/latest?cb=20081230050606
- `wookieepedia_feeorin_tfu2_tarkose.png` — near-photoreal game CGI, *The Force Unleashed II*, the gladiator Tarko-se: olive-green, head-tails, massive build; file `Feeorin gladiator.png` — https://static.wikia.nocookie.net/starwars/images/3/3b/Feeorin_gladiator.png/revision/latest?cb=20131122094546
- `wookieepedia_feeorin_uaa_legends.png` — realistic painting by Raven Mimura, *Ultimate Alien Anthology* (Legends), full body: mauve-purple skin, several head-tails, heavy build; file `Feeorin-UAA.png` — https://static.wikia.nocookie.net/starwars/images/9/98/Feeorin-UAA.png/revision/latest?cb=20250228013340
- `wookieepedia_feeorin_2017darthmaul1.png` — **COMIC, kept as animated/negative reference only** for the canon tendril count: full-body Feeorin from *Darth Maul* (2017) 1, turquoise-cyan skin, a dozen-plus paler green tendrils; file `Feeorin-2017DarthMaul1.png`.
- `donor_current_sprite.png` — **negative reference only.** An essentially blank 4 KB canvas with two eye marks; see the visual brief.

## ruling
(empty — owner has not reviewed this race yet)
