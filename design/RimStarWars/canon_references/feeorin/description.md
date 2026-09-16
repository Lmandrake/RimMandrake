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
One canon image (*Darth Maul* (2017) 1), and it is worth more than the prose:

- **A dense mass of thick, ropy tendrils erupting from the back and sides of the skull
  and hanging past the chest**, some to the waist. There are many — a dozen or more,
  not two or three — and they read as heavy, muscular and slightly flattened, exactly
  the Nautolan arrangement the Legends text names. **This is the species, visually.**
- **The tendrils are a distinctly different, paler, yellower green than the body.**
  A two-tone head/tendril split, not a uniform colour. Additional short thin tendrils
  frame the lower face.
- **The cranium is bald, smooth and swept-back**, with the tendril roots forming a
  raised collar around the back of the head; no hair anywhere.
- **The face is heavily ridged**: strong brow, deep vertical and diagonal creases down
  the cheeks, a heavy squared jaw, small deep-set eyes. Grim and craggy rather than
  smooth-alien.
- **Big, broad-shouldered, thick-limbed, visibly powerful build** — a defined muscular
  torso under a wrapped sleeveless tunic, sashes, and heavy tall boots. Consistent with
  the gladiator/champion citation and with "grew stronger with age."
- 🔴 **The body is turquoise-cyan, and the def's `Skin_Purple` appears nowhere in
  canon.** The image is a cool blue-green (a "blue" cite in practice reading as
  turquoise); the other sourced colour is green. **The sourced texture is MOTTLED**, so
  a flat single tone is wrong even when the hue is right.
- Comic art with heavy inking and flat spot colour — treat line weight and exact
  saturation as the artist's; treat the tendril mass, the ridged face, the bulk and the
  blue-green family as authoritative.

🔴 **`donor_current_sprite.png` is essentially empty.** It is a 4 KB, almost entirely
transparent canvas carrying **two small black curved eye marks and nothing else** — no
head, no tendrils, no jaw, no skin. Whatever the mod renders for a Feeorin today, this
file is not it, and the species' one defining feature (the tendril mass) has no art
here at all. Do not treat this as evidence about anything except that art is owed.

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
- 🔴 **`Skin_Purple` is unsourced, and GREEN — one of only two canon colours — is
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
- `wookieepedia_feeorin_2017darthmaul1.png` — **the reference of record, and the only
  canon image on disk.** A full-body Feeorin from *Darth Maul* (2017) 1: turquoise-cyan
  skin, a heavy mass of paler green head tendrils falling past the chest, a deeply
  ridged craggy face with a heavy jaw, a powerful build in a wrapped sleeveless tunic,
  sashes and tall boots. Comic panel with a background, so it is not a clean plate.
- `donor_current_sprite.png` — **negative reference only.** An essentially blank 4 KB
  canvas with two eye marks; see the visual brief.

## ruling
(empty — owner has not reviewed this race yet)
