# Lasat

**defName**: `RSW_RimMandrakeLasat` (`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
🔴 **Its `<description>` field is the single character `e`** — a placeholder that was
never filled in. That is a shipping-visible defect: the xenotype's in-game
description tooltip reads "e".

## Sourced text (Wookieepedia)

**Canon.** Lasats were a humanoid sentient species native to the Wild Space planet
**Lira San**, though the species had settled the Outer Rim world of **Lasan**
(adopted homeworld). Infobox: class **humanoid**; **skin colour light brown, gray,
purple**; **hair colour dark purple**; **eye colour blue, green, yellow**;
distinctions **"impressive height, prehensile feet, strength and agility"**; language
Lasat. Height, mass and lifespan are **blank in the canon infobox — do not invent
them**.

Biology and appearance: Lasats were notable for their impressive height, strength
and agility, **with muscular digitigrade legs enabling them to run faster, jump
higher and farther, and move more quietly than humans**. Their **large finger pads
and prehensile toes assisted them in climbing**. Their **large eyes and ears
afforded them superior sight and hearing over humans and other humanoids**. They had
the strength to open a powered-down blast door. 🔑 **A height of two meters tall was
considered BELOW-average for a Lasat** — so 2 m is the floor, not the norm.

🔑 **The fur patterns of a Lasat varied from individual to individual, and could
change as they aged. NO TWO LASAT HAD THE SAME STRIPING.** Some humans considered a
Lasat's strong odour unbearably offensive. Ezra Bridger's first read on one was
"You some kind of hairless Wookiee?" — i.e. furred, but far less shaggily than a
Wookiee.

Culture: the **Boosahn Keeraw**, the Lasat warrior way — when one is defeated by a
superior foe, he gifts his weapon.

**Legends (a genuinely different species, see the visual brief).** Infobox:
**height 1.2–1.9 meters**; hair colour light brown; **diet carnivorous**;
distinctions **heat-dissipating ears** and **large eyes for twilight vision**;
origin Lasan. Text: coming from an arid world with extensive deserts, the Lasat
developed features to protect them from the climate — **pointed ears that assisted
with heat dissipation** and **thin fur to insulate their bodies at night**; the fur
was brown, males usually had longer fur, and it **covered the entire body except the
face, hands and tail** (so Legends Lasat have a **tail**). **Small nasal and oral
openings, but large eyes to improve their nightvision.** Society was nomadic with
mud-and-brick city-states; individuals **did not use pronouns when referring to
themselves**, preferring proper names.

⚠️ **The two height figures contradict each other outright**: canon says 2 m is
below average; Legends says the whole range is 1.2–1.9 m. Canon governs appearance
in this repo, so treat Lasat as **taller than a human, 2 m+**.

## Visual brief

🔴 **Canon Lasat and Legends Lasat are not the same creature, and the repo's
xenotype is chasing neither cleanly.** Look at the images in this order.

**`wookieepedia_zeborrelios_cgswg.png` and `wookieepedia_lasat_zeb_fathead.jpg` are
the references of record** (Garazeb "Zeb" Orrelios, *Star Wars Rebels* CGI). They
agree completely:

- **The body is FURRED and TIGER-STRIPED, not skin-coloured.** Base coat is a
  desaturated grey-violet; over it run **broad dark charcoal/near-black transverse
  bands** on the forearms, the shins/thighs, and across the muzzle and brow. This
  is the single biggest thing a colour-list-driven prompt gets wrong — "gray" and
  "purple" are both true, *simultaneously and in bands*. The prose actually says so
  ("no two Lasat had the same striping") and it is easy to miss in a colour field.
- **Ears are enormous, pointed, set high and wide on the skull, and swept
  outward/upward** with a visible tuft. They read closer to a lynx's or a bat's
  than a cat's, and they are the loudest silhouette feature after the shoulders.
- **The head is a deep, heavy MUZZLE, not a flat face.** Pronounced brow ridge,
  broad flat nose at the muzzle tip, and a wide mouth with visible canines. Green
  eyes, forward-set, large.
- **Massive shoulders and chest tapering to a narrow waist**, with long heavy arms
  and **very large hands ending in black claws**. The upper body is the mass.
- 🔑 **Legs are DIGITIGRADE.** A long backwards-angled shank, the heel carried well
  off the ground, and **big splayed three-toed feet with black claws**. This is
  canonical (`digitigrade`, `prehensile toes`) and it is the body-plan feature a
  human-skeleton RimWorld pawn cannot express at all. Document the compromise; do
  not pretend it isn't one.
- Facial fur reads as chops/sideburns running down the cheeks into the jaw.

**`wookieepedia_chava_and_gron_as_prisoners.png`** (an in-show frame, two elderly
Lasat under stormtrooper guard) is the **individual-variation reference and it is
important**: the two Lasat in it look markedly *unlike* Zeb and unlike each other.
Gron (tall, standing) is a **pale mauve/pink-lavender** with a bald crown and much
fainter markings; Chava (short, hunched, robed) is a **dull olive-grey** with white
head hair and a heavy brow. Both keep the huge pointed ears and the deep muzzle.
**So the constants are ears, muzzle, brow and bulk; the variables are hue and
stripe pattern** — exactly as the "no two Lasat had the same striping" line says.

**`wookieepedia_lasat_jaro_tapal.jpg`** (Jaro Tapal, *Jedi: Fallen Order*) is a
**flat purple** Lasat — uniform lavender-violet skin/short fur, bald crown,
pointed ears, a short chin beard, and **noticeably more human proportions**
(ordinary shoulders, no visible arm or leg fur, clothed limbs). It confirms the
"purple" colour cite and shows the species *can* be rendered nearly stripe-free —
but it is the least characteristic of the four and should not be the primary target.

🔴 **`wookieepedia_lasat_legends_ae.jpg` is a NEGATIVE REFERENCE — keep it, do not
copy it.** This is the Legends *Alien Encounters* line drawing, and it depicts a
completely different creature: **lean, gaunt, hunched, goblin-like**, with a
smooth hairless dome, a small flat-featured face with **huge round staring eyes**,
narrow shoulders, thin limbs, and **ordinary plantigrade human feet in shoes**.
No stripes, no muzzle, no bulk, no digitigrade leg. It matches the Legends
infobox (1.2–1.9 m, thin fur, "large eyes for twilight vision") and matches
nothing about the canon Lasat. **If a sprite ever comes back looking like this,
it has been generated from the Legends article.**

## Must show
- [ ] Body is furred and tiger-striped — a desaturated grey-violet base coat with broad dark charcoal/near-black transverse bands, not a flat single colour
- [ ] Ears are enormous, pointed, set high and wide on the skull, swept outward/upward with a visible tuft
- [ ] Head is a deep, heavy muzzle (not a flat face), with a pronounced brow ridge and visible canines
- [ ] Massive shoulders and chest tapering to a narrow waist, with large hands ending in black claws
- [ ] Legs are digitigrade, with big splayed three-toed feet and black claws
- [ ] Hue and stripe pattern vary by individual (no two Lasat identical) — not the flat-purple Jaro Tapal look or the gaunt, goggle-eyed Legends design

## Engine limits
- **Striping cannot be expressed by a single-channel tint mask.** A banded/patterned coat
  needs art (multiple regions or a baked texture), not a flat skin-colour gene.
- **Digitigrade legs with prehensile toes are a body-plan feature a human-skeleton RimWorld
  pawn rig cannot express as things stand.**

**Xenotype-versus-canon contradictions to fix:**

- 🔴 **`RSW_CatharHead`.** The Lasat borrows the Cathar head. Cathar are a
  *feline* species; canon Lasat are classed only as `humanoid` and read as a
  deep-muzzled ursine/simian design with bat-like ears. A cat face is the wrong
  head, and it is the most visible error in the def.
- 🔴 **No striping anywhere in the gene list.** `RSW_Skin_Lavender` and
  `RSW_Skin_SlateBlue` are flat single-tone skins. The canonical Lasat is
  *banded*, and the wiki says so explicitly. This is the highest-value fix.
- ⚠️ **`Outland_Chest_Fur` under-covers.** Fur in the images is on the **forearms,
  hands, thighs, shins and face**, not just the chest.
- ⚠️ **Hair colours `Hair_DarkBlack` and `RSW_Hair_DarkBlue` are unsourced** — the
  canon infobox lists **dark purple only** (`Outland_HairColor_DarkPurple`, which
  is present and correct).
- ⚠️ **`WoundHealing_Slow` and `Superclotting` have no canon basis** in either
  article. Nothing says Lasat heal slowly or clot unusually.
- ✅ Correct and well-sourced: `RSW_AbilityGene_JumpLegs` ("jump higher and
  farther"), `MeleeDamage_Strong` + `Body_Hulk` + `RSW_BodySizeGene_bigger`
  (strength, impressive height, opens blast doors), `DarkVision` (large eyes,
  superior sight / Legends nightvision), `Ears_Pointed`, the yellow/green big-eye
  genes (canon eyecolor blue/green/yellow), `NakedSpeed` (runs faster and quieter
  than humans). `BS_Diet_Carnivore` is sourced **from Legends only** — the canon
  infobox leaves diet blank.
- **Not representable, and worth writing down rather than hiding**: digitigrade
  legs, prehensile toes, large finger pads, and the Legends tail.

## Source URLs

- https://starwars.fandom.com/wiki/Lasat (canon article; direct HTML is
  Cloudflare-walled — wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Lasat&format=json&prop=wikitext`,
  29,008 chars, 2026-09-15)
- https://starwars.fandom.com/wiki/Lasat/Legends (Legends article; wikitext via the
  same `api.php?action=parse&page=Lasat/Legends&...` route, 4,938 chars, 2026-09-15)
- https://static.wikia.nocookie.net/starwars/images/a/a5/Zeb_Stormtrooper_Fathead.png → `wookieepedia_lasat_zeb_fathead.jpg`
- https://static.wikia.nocookie.net/starwars/images/9/93/JaroTapalClear-JediSurvivor.png → `wookieepedia_lasat_jaro_tapal.jpg`
- https://static.wikia.nocookie.net/starwars/images/0/07/Lasat-AE.png → `wookieepedia_lasat_legends_ae.jpg`
- `wookieepedia_zeborrelios_cgswg.png` and
  `wookieepedia_chava_and_gron_as_prisoners.png` were already on disk from an
  earlier pass; they correspond to `File:ZebOrrelios-CGSWG.png` (the canon
  infobox image) and `File:Chava_and_Gron_as_prisoners.png` on Wookieepedia.
- NOT fetched this pass: https://www.starwars.com/databank/lasat (the canon
  article's `{{Databank|lasat}}` citation, which is the source of the
  "impressive height, prehensile feet, strength and agility" distinctions line).

## Candidate images

- `wookieepedia_zeborrelios_cgswg.png` — **the reference of record.** The canon
  infobox image: Zeb Orrelios, full body, transparent background, *Rebels* CGI.
  Settles the striped grey-violet fur, the huge swept pointed ears, the deep
  muzzle and brow, the shoulder-heavy build, the clawed hands, and the
  digitigrade three-toed legs.
- `wookieepedia_lasat_zeb_fathead.jpg` — Zeb mid-fight with a stormtrooper.
  Second angle on the same individual; the best view of the **leg articulation,
  feet and claws** and of stripe contrast on the limbs. Also gives scale against
  a human-sized trooper.
- `wookieepedia_chava_and_gron_as_prisoners.png` — in-show frame of two elderly
  Lasat (Gron pale mauve, Chava olive-grey) with stormtroopers. **The
  individual-variation reference**: proves hue and marking vary widely while
  ears, muzzle and brow stay constant.
- `wookieepedia_lasat_jaro_tapal.jpg` — Jaro Tapal, *Jedi: Fallen Order*. A flat
  purple, near-stripeless, more human-proportioned Lasat. Confirms the "purple"
  colour cite; least characteristic of the set.
- `wookieepedia_lasat_legends_ae.jpg` — 🔴 **negative reference, kept
  deliberately.** The Legends *Alien Encounters* line art: a gaunt, hairless,
  goggle-eyed, plantigrade goblin figure that shares nothing but pointed ears
  with the canon Lasat. Do not use it as an appearance target.

## ruling

(empty — owner has not reviewed this race yet)
