# Cathar

**defName**: `RSW_RimMandrakeCathar` (verified present in
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`, which measures
69 `XenotypeDef`s). Matrix: `Jawa_WildsteamClan: R`, `Pirate: R` — **rare**, so a Cathar is
a once-in-a-while sighting and will be looked at closely when it happens.

## Sourced text (Wookieepedia)

**Current canon** (`/wiki/Cathar`). The Cathar were a **catlike, felinoid humanoid sentient
species**. Members possessed **fur and manes, slitted eyes and noses, tufted ears, a mouth
with teeth, and clawed hands**. They were **powerful, swift, and fierce fighters**.
🔑 **"Cathars have very sensitive hearing, even more so than Twi'leks or humans."** That is
the one explicit sensory superlative canon gives them.

🔴 **The canon infobox is almost entirely empty** — `height`, `length`, `mass`, `skincolor`,
`eyecolor`, `distinctions`, `lifespan`, `origin`, `habitat`, `diet` and `language` are all
blank. Only `class = Feline` and `haircolor = Brown, Red` are filled. **So there is no
canonical Cathar height, mass, lifespan or eye colour to cite.** Anything stating one is
either Legends or invented.

**Legends** (`/wiki/Cathar/Legends`) is where the substance lives, and it is what the def's
own `<description>` is lifted from verbatim ("a planet of savannas and rough uplands … great
warriors and dedicated, efficient predators"). Legends infobox: **height males 1.8 m, females
1.6 m**; **skin colour "Gold to yellow-brown with dark stripes"**; distinctions
**"Lion-like aliens"**; origin **Cathar**; language **Catharese**; lifespan in bands —
child 1–11, young adult 12–17, adult 18–49, middle age 50–65, old 66–89, **venerable 90+**
(i.e. a roughly human lifespan, which is why the def carrying *no* lifespan gene is correct).
Legends body text: **fur-covered bodies with thick manes**; **prominent, retractable claws
that could deliver powerful killing attacks**; **on average 1.5 to 1.9 meters tall**; "these
traits made them the perfect **hand-to-hand specialists**"; **born into a litter**;
biologically similar to the Bothan. Two subspecies, **Juhani** and **Myr Rho**, both
**"notably less catlike than mainline Cathar"** — a canonical licence for a more human-faced
variant, if one is ever wanted.

**Behaviour and culture (Legends).** High moral values learned from family and society;
known for **loyalty, passion, and temper**. **They mated for life** — when a mate died the
survivor never took another. On the homeworld they lived in **cities built into giant trees**,
organised into **clans governed by "Elders"**, with hero-stories carved into the trunks.
Their religion included the **"Blood Hunt"**, in which a warrior individually fought entire
nests of **Kiltik** to gain honour and purge inner darkness. Catharese emphasised some words
**with a growl**. Females were **prized as slaves**, males "generally regarded as too
uncontrollable for slavery." The homeworld was devastated by the Mandalorians at the **Battle
of Cathar**, killing **over 90 percent of the species** — a survivor-diaspora species, which
sits well with rare placement in a scavenger clan and among pirates.

## Visual brief

🔴 **The two continuities show genuinely different animals, and the def sits on the Legends
side while its art sits on the canon side.** Both are documented below; the reference of
record for the *lion* read is `wookieepedia_legends_infobox.jpg`.

**`wookieepedia_legends_infobox.jpg` (the Legends infobox, a painted TCG piece) — the
strongest single reference.** It settles the palette the def gets wrong:
- **Body fur golden-orange to yellow-brown**, warm and saturated, with **darker olive-brown
  shading over the muzzle, brow and shoulders** — matching "gold to yellow-brown with dark
  stripes" exactly. There is **no red and no grey anywhere on this animal.**
- **A true feline muzzle**, projecting forward from the face with a black leathery nose pad,
  visible upper and lower fangs, and a fringed chin ruff — this is a lion's head, not a human
  head with cat features.
- **A heavy dark mane worn as thick ropes/dreadlocks** swept back off the skull, distinctly
  darker than the body coat.
- **Amber/gold eyes with round pupils**, set forward under a shelf brow.
- **Tufted, pointed, backswept ears** — the tufts are long and visible, confirming "tufted
  ears" as a silhouette feature rather than a detail.
- **Fur covers the entire torso and arms**, and the hands are broad with visible claws.

**`wookieepedia_sylvar_and_males.jpg`** (comic panel, Sylvar with two males of the more
common subspecies) adds the **sexual dimorphism, and it is large**: the two males have full
maned lion faces with **white/cream manes and beards** and heavy muzzles; **Sylvar, the
female, has a much flatter, more humanoid face**, pale cream-yellow skin, **white head-hair
worn long rather than a mane**, no beard, and large pointed tufted ears. **A female Cathar is
not a smaller male Cathar** — the same lesson the Hutt entry records for life stages.

**`wookieepedia_cathar_jedi.jpg`** (painted Legends piece) agrees on structure while shifting
hue: a **pale cream/white-furred** individual with the same projecting muzzle, amber eye,
large tufted ears and a long-fingered clawed hand. Confirms fur hue varies individually
(gold, cream, white) while **muzzle + mane + tufted ears stay constant**. That constancy is
the fact to preserve; the hue is not.

**`wookieepedia_canon_twins.jpg`** (the *current canon* infobox image, the Cathar criminal
twins from "Tall Tales") is the outlier and must be labelled as such: these two read as
**near-human**, with warm pinkish-tan skin, ordinary human-shaped faces and flat noses,
**no muzzle at all**, and only **grey-white fur along the jaw and temples** plus slitted eyes
suggesting the species. It is a stylised flash-animation design. It is kept because it is the
current-canon infobox, but **taken alone it would produce a Cathar with no feline silhouette
whatsoever** — and if the owner wants the recognisable Cathar, the three Legends images win.

**`donor_current_sprite.png` is the finding.** It is
`RimMandrakeSW/OR/Things/Pawn/Humanlike/Heads/Cathar/Male_Head_south.png` (512×512; the
folder holds male/female × 3 facings plus `*m.png` mask variants). Correctly a **greyscale
tintable mask**, so its lack of colour is not a defect and the palette findings above belong
on the *skin genes*. What it lacks is **shape**: it is a **plain human ovoid head** with two
ordinary dot eyes and a tiny inverted-triangle nose. **No muzzle, no mane, no fur texture, no
fangs, no jaw ruff, no ear tufts.** The only other Cathar-specific art on disk is
`SWX/Pawn/HeadAttachments/cathar/CatNose_{east,south}.png` — a nose overlay, with **no north
facing** — and the ears come from the generic `Ears_Pointed` gene, which is elf ears, not
tufted feline ears. **In game today a Cathar is a tinted human with a cat nose.** The single
most defining canon feature — the projecting muzzle and mane — is not represented at all.

## Source URLs

- https://starwars.fandom.com/wiki/Cathar — current canon; wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Cathar&format=json&prop=wikitext`
  (4,985 chars, 2026-09-15). Article carries `{{Species-stub}}`.
- https://starwars.fandom.com/wiki/Cathar/Legends — Legends; wikitext via the same API
  endpoint with `page=Cathar/Legends` (15,006 chars, 2026-09-15). Infobox figures
  (1.8 m / 1.6 m, gold to yellow-brown with dark stripes, lifespan bands) cite
  *Ultimate Alien Anthology* and *Coruscant Nights II: Street of Shadows*.
- https://static.wikia.nocookie.net/starwars/images/8/8c/CatharBounties-TallTales.png
  (File:CatharBounties-TallTales.png → `wookieepedia_canon_twins.jpg`)
- https://static.wikia.nocookie.net/starwars/images/a/a9/CatharDefender-TCGMaM.png
  (File:CatharDefender-TCGMaM.png → `wookieepedia_legends_infobox.jpg`)
- https://static.wikia.nocookie.net/starwars/images/b/b1/SylvarAndEscorts-TOTJR2.jpg
  (File:SylvarAndEscorts-TOTJR2.jpg → `wookieepedia_sylvar_and_males.jpg`)
- https://static.wikia.nocookie.net/starwars/images/e/ed/CatharJediDrawCloser-JATM.jpg
  (File:CatharJediDrawCloser-JATM.jpg → `wookieepedia_cathar_jedi.jpg`)
- ⚠️ All four image files are served as **WebP** despite `.png`/`.jpg` extensions on the
  wiki; they were re-encoded to real JPEG locally so they open. Content is unaltered
  otherwise.
- NOT fetched this pass: `https://www.starwars.com/databank/` — no Cathar species Databank
  page was attempted.

## Candidate images

- `wookieepedia_legends_infobox.jpg` — **the reference of record.** Painted full-torso
  golden-orange Cathar mid-roar in jungle: settles muzzle, dark rope mane, amber eyes,
  tufted ears, gold-to-yellow-brown fur, clawed hands.
- `wookieepedia_sylvar_and_males.jpg` — comic panel establishing **sexual dimorphism**
  (maned/bearded male lion faces vs a flatter, mane-less, long-white-haired female).
  Stylised line and palette; its value is the male/female contrast.
- `wookieepedia_cathar_jedi.jpg` — painted Legends piece, a cream/white-furred individual;
  confirms hue varies while muzzle, mane, tufted ears and clawed hands do not.
- `wookieepedia_canon_twins.jpg` — **negative/weak reference, kept deliberately.** The
  current-canon infobox image, but a near-human stylised design with no muzzle. Do not use
  it alone to establish appearance.
- `donor_current_sprite.png` — the shipped head mask. Evidence of the gap, not of canon.

## Def-versus-canon contradictions (report only — not fixed here)

1. 🔴 **Skin-colour genes contain no gold or yellow, and add red and grey that nothing
   sources.** Def carries `Skin_DeepRed`, `Outland_Skin_Red`, `Outland_Skin_DeepBrown`,
   `Outland_Skin_PaleBrown`, `Skin_SlateGray`. Canon skincolor is **empty**; Legends is
   **"gold to yellow-brown with dark stripes."** `Skin_DeepRed`/`Outland_Skin_Red` and
   `Skin_SlateGray` are unsourced inventions, and the one colour every reference image agrees
   on — **gold/yellow-brown** — is absent from the gene list entirely.
2. 🔴 **No dark stripes anywhere.** The Legends skin cite is explicitly *striped*; the def has
   no stripe/marking gene and the head art has no stripe pattern. Same failure class as the
   anooba's "varying tones of gray."
3. 🔴 **Retractable claws are absent.** Legends gives "prominent, retractable claws that could
   deliver powerful killing attacks" and calls Cathar "the perfect hand-to-hand specialists";
   the def has only `AptitudeStrong_Melee` and no natural-weapon / claw gene.
4. **Very sensitive hearing is absent.** The single explicit canon sensory superlative
   ("even more so than Twi'leks or humans") has no gene.
5. ⚠️ **`AptitudeStrong_Shooting` is unsourced and cuts against canon**, which frames the
   species as melee/hand-to-hand specialists. `AptitudePoor_Animals` is likewise unsourced for
   a species canon calls "dedicated, efficient predators."
6. ✅ **Correct restraint worth recording:** the def invents **no** body-size and **no**
   lifespan gene. Canon has no height or lifespan at all, and the Legends bands top out at
   "venerable 90+" and 1.5–1.9 m — i.e. human — so `Body_Standard` with no lifespan gene is
   right. Do not "fix" this by adding one.
7. ⚠️ **Art gap, not a def error:** `Ears_Pointed` supplies elf ears where canon specifies
   **tufted** feline ears, and the only Cathar-specific overlay on disk (`CatNose`) has no
   north facing.
8. ✅ **Namer is correct** — `RSW_KoTOR_NamerCathar` reads
   `RimMandrakeSWNames/SWX/Cathar/{First,Last,Nick}`, all three files present, contents
   Cathar-appropriate (`Xyrbak`, `Morbirr`, `Mandorr`). No wrong-species namer here.

## ruling

(empty — owner has not reviewed this race yet)
