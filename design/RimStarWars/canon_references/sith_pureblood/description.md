# Sith Kissai (Pureblood)

**defName**: `RSW_RimMandrakeSithKissaiPureblood`, label `Sith Kissai (Pureblood)`
(`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Assigned `Jawa_AscendantHelix: R`.

🔑 **Read `../sith_species/description.md` first.** Kissai is a **caste of the Sith
species**, not a species of its own, and all the shared anatomy — red skin, bone
spurs, cheek tendrils, cranial horns, simian mouth, glowing yellow eyes under
cartilaginous eyebrow-stalks, three clawed digits per hand and foot,
left-handedness, species-wide Force-sensitivity — lives in that entry and is not
repeated here. Only what is **Kissai-specific** is below.

## Sourced text (Wookieepedia)

The whole of the Kissai article's *Biology and appearance* section is **two lines
long**, and this is the headline finding:

> **"Like most members of the Sith species, the Kissai were red-skinned humanoids
> with distinctly sharp, predatory features and tendrils on both sides of their
> chins."**

🔴 **Canon establishes NO physical trait that distinguishes a Kissai from a
mainline Sith.** Every appearance statement on the page is explicitly a
restatement of the shared species baseline ("like most members of the Sith
species…"). Compare the other two castes, which each do have an exclusive: Massassi
are taller/hulking with solid pupil-less yellow eyes, and Zuguruk have five-digit
hands. **The Kissai's distinguishing characteristics are entirely occupational.**
The owner needs this, because the repo ships Kissai as a separate xenotype with a
separate gene list, and canon gives no visual basis for the separation.

What the Kissai page *does* add, all from the `Knights of the Old Republic Campaign
Guide` infobox:

- **Height 1.8 meters.**
- **Skin colour: red.** (One value only — not the species' full charcoal/obsidian
  range.)
- **Eye colour: yellow.**
- 🔑 **Lifespan: up to 60 standard years.** Short-lived by galactic standards.
- Languages: **Basic and Sith.**
- Height aside, **mass is UNSOURCED**; hair colour, feathers and distinctions are
  all blank in the infobox.

Role and behaviour — the substance of the caste:

- **The priest class in the Sith caste system.** The Kissai **studied the nature of
  the dark side of the Force and practised ancient Sith sorcery and alchemy.**
- They were **a subspecies of the Sith species who were enslaved by exiled Dark
  Jedi on Korriban.**
- Presumed to have originated on **Korriban**, with an ancestry running back to
  roughly **100,000 BBY**.
- In the shared caste hierarchy (`Sith (species)/Legends`): the Kissai are **the
  priestly caste**, Zuguruk the engineers and second-highest caste, Massassi the
  warriors, Grotthu the slaves; the system was rigid — *"There was no transitioning
  from one to the other."*
- **Unusual abilities**: nothing Kissai-exclusive. The species-level fact carries
  it: the entire Sith species was considered **strongly Force-sensitive** through a
  **symbiotic relationship with the dark side**. Sorcery and alchemy are the
  Kissai's *practice*, not a separate biological gift.
- Canon (not Legends) adds one relevant line, from `Sith (species)`: **"priests of
  the Sith species founded the Sorcerers of Tund"** on Tund — and that group became
  associated with the **light** side. Worth having: a Kissai-descended order need not
  be dark-side.

## Visual brief

🔴 **The single most important visual finding: Wookieepedia's Kissai infobox image
is a MASSASSI image.** The `Kissai` article's infobox is
`[[File:Massassi-JATM.jpg]]` — the same file the `Sith (species)/Legends` article
captions **"The priestly Kissai and warrior Massassi castes"** and the `Massassi`
article also uses. So the wiki does not have a Kissai-only reference image either.
Anyone building Kissai art from "the Wookieepedia Kissai picture" is building from a
picture of two castes at once, and the file is *named* for the other one.

**`wookieepedia_jatm_sith_group.jpg`** (`File:Massassi-JATM.jpg`, 473×690, from the
*Jedi Academy Training Manual*) is nonetheless the best available image and it is a
strong one on the shared anatomy:

- **Saturated blood-red skin** across the whole figure, and the same red on the
  background figure — the hue reference the prose asks for.
- **Glowing white/blank eyes with no visible iris or pupil**, set under a heavy
  brow. (The prose says *yellow*; this artist rendered them white-hot. Canon's
  species eye-colour list does include **white**, so this is inside canon rather
  than against it — but the yellow is far better attested.)
- 🔑 **Extremely long horizontal cheek tendrils** sweeping out sideways from the
  cheekbones, well past the width of the head — nearly whisker-like, not the short
  chin-goatee that "chin tendrils" suggests. **This is the read to hit**, and it is
  the feature a text-only prompt gets wrong: the tendrils come off the **cheekbones**
  and are **long**.
- **Dark, near-black facial markings** radiating around the eyes and across the
  cheeks — read as either pigmentation or ritual marking; the text does not say
  which, so treat as costume rather than skin.
- **Heavy hooded robe with a gold ornamental headband** and broad gold-patterned
  stole panels down the front — the priestly dress. The head itself is fully hooded,
  so **crown shape, cranial horns and baldness are not visible in this image.**

**`wookieepedia_kissai_infobox_variant.jpg`** (`File:Kissai_1.jpg`, 336×449, comic
panel) is the only file on the Kissai page actually named for the caste, and it adds
real detail the JATM plate hides:

- **Pink-mauve rather than deep crimson skin** — matching the sourced line that
  "some members of the species retained more pink shades of skin tone in adulthood."
- **White eyes with small dark pupils** under a pronounced hard bony brow ridge.
- 🔑 **Tendrils in TWO places**: a pair on the cheeks/jowls *and* a **single heavy
  central chin tendril** hanging below the mouth. Both are **decorated with metal
  rings/clasps** — the cheek tendrils carry hooked ornaments and the chin tendril a
  ring. Ornamented tendrils are a priest-caste dressing cue and cheap to reproduce.
- **A dark diamond/lozenge marking on the centre of the forehead**, plus a smaller
  one above it — ritual marking, not anatomy.
- **Deeply furrowed, weathered skin texture** across the cheeks.
- Hooded again, so no crown information.

**`wookieepedia_sith_king_adas.jpg`** (`File:SithKingAdas-BoSSFtDS.png`, 1122×1526)
is the highest-resolution Sith figure available and belongs here as calibration —
Adas was the one Sith to attain monarch. It is **not a Kissai** and is labelled as
such below.

⚠️ **No `donor_current_sprite.png`.** The Kissai xenotype has no species art of its
own: it renders from `RSW_Head_Bone`, which forces `RSW_Male_HeavyBoneNormal` /
`RSW_Female_HeavyBoneNormal`, plus `RSW_Beard_chintendril`, whose texture is
**`SWX/Pawn/HeadAttachments/feeorin/chintendril`** — the tendril art is **borrowed
from the Feeorin**. Nothing in this repo lets canon be compared against the sprite
that actually appears in game.

## Def-versus-canon (flagged — not fixed)

`RSW_RimMandrakeSithKissaiPureblood` is the **best-formed of the three Sith
xenotypes** — it has a namer, a Sith head, tendrils, a psychic gene and red skin —
but:

- 🔴 **No lifespan gene, so Kissai live a human lifespan.** Canon: **up to 60
  standard years**, which is *shorter* than a RimWorld human. The mod has lifespan
  genes (`RSW_lifespan_nine`, `RSW_lifespan_half`), so this is expressible and
  simply absent.
- 🔴 **`Skin_SlateGray` is in the Kissai skin pool.** The Kissai infobox gives skin
  colour as **red, and only red**. Charcoal/obsidian belongs to the *species* infobox,
  not to this caste — and `Skin_Orange` / `Outland_Skin_DeepOrange` come from the
  **Massassi** infobox. The three castes' colour pools have been mixed together.
- 🔴 **`Outland_DeceleratedPregnancy` against a 60-year lifespan.** A shorter-lived
  species with a *longer* gestation is the wrong direction, and nothing sources it.
- ⚠️ **`Hair_BaldOnly`.** The species infobox gives hair **black, brown, red**. Every
  Kissai image is hooded, so baldness is neither confirmed nor denied by the art —
  but the gene forecloses a sourced field.
- ⚠️ **`Outland_Evasive`** — unsourced. Kissai are the sedentary priest caste; the
  warrior caste is Massassi.
- ⚠️ **`Outland_RidgedSkin` + `Outland_ThickSkin`.** Ridged skin is a reasonable stand-in
  for the sourced bone spurs and predatory ridging. But **thick skin is the trait
  canon assigns to MASSASSI** — *"extremely tough skin; powerful cauterizing agents
  such as cyanogen silicate were needed"* — and the Massassi xenotype does **not**
  carry `Outland_ThickSkin` while this one does. The trait is on the wrong caste.
- ⚠️ **No height gene** (`Body_Standard` only) against a sourced **1.8 m** — fine as
  a baseline, recorded so it is not later confused with the Massassi 1.9 m/2–3 m.
- ⚠️ Sourced-but-absent, shared with the other two castes: **cranial horns, bone
  spurs at the elbows, cartilaginous eyebrow-stalks, three clawed digits per hand and
  foot, simian mouth, pointed teeth, left-handedness.** None has a gene in any of the
  three Sith xenotypes.
- ✅ Well sourced and correctly present: `PsychicAbility_Enhanced`,
  `Turn_Gene_LatentPsychic`, `Turn_Gene_FastNeuralHeat`, `Turn_Gene_MeditationNeed`
  (sorcery/alchemy practice + species-wide Force-sensitivity), `Outland_Eye_Yellow`,
  `Skin_DeepRed` / `Outland_Skin_Red`, `RSW_Beard_chintendril`,
  `Aggression_Aggressive` (canon: "a proud and violent species").
- ⚠️ **Naming**: the caste is a *caste*, so the label's "(Pureblood)" is questionable —
  canon is explicit that **Sith Purebloods are hybrids and "were thought to be very
  different from the original Sith species as a whole."** A Kissai is a **Red Sith**,
  not a Pureblood. All three castes carry "(Pureblood)" in their label and
  `RSW_NamerPersonPureblood` as their namer. Governed by
  `NAMING_SCHEME_EXECUTION_1` — flagged, not renamed.

## Source URLs
- https://starwars.fandom.com/wiki/Kissai — wikitext via
  `https://starwars.fandom.com/api.php?action=parse&page=Kissai&format=json&prop=wikitext`,
  8,204 chars, 2026-09-15. (`page=Kissai/Legends` → `missingtitle`; the base page is
  already the Legends article, tagged `{{Top|leg}}`.)
- https://starwars.fandom.com/wiki/Sith_(species)/Legends — 127,967 chars,
  2026-09-15. Shared anatomy and the caste hierarchy.
- https://starwars.fandom.com/wiki/Sith_(species) — canon article, 7,414 chars,
  2026-09-15. Source of the Sorcerers of Tund line.
- https://static.wikia.nocookie.net/starwars/images/1/1f/Massassi-JATM.jpg → `wookieepedia_jatm_sith_group.jpg` (473×690) — **the Kissai article's own infobox image, named for the Massassi.**
- https://static.wikia.nocookie.net/starwars/images/0/02/Kissai_1.jpg → `wookieepedia_kissai_infobox_variant.jpg` (336×449)
- https://static.wikia.nocookie.net/starwars/images/6/63/Sorcerer_of_Tund_EGF.jpg → `wookieepedia_sorcerer_of_tund.jpg` (777×1000)
- https://static.wikia.nocookie.net/starwars/images/e/ef/SithKingAdas-BoSSFtDS.png → `wookieepedia_sith_king_adas.jpg` (1122×1526)
- NOT fetched: no `starwars.com/databank` page exists for Kissai; not attempted.

## Candidate images
- `wookieepedia_jatm_sith_group.jpg` — **the reference of record, with a caveat.**
  The Kissai article's infobox image, but the file is `Massassi-JATM.jpg` and the
  species article captions it as showing **both** the Kissai and Massassi castes.
  Settles: saturated blood-red skin, glowing pupil-less eyes, **very long horizontal
  cheek tendrils**, dark radiating facial markings, hooded gold-trimmed priestly
  robes. Head crown not visible.
- `wookieepedia_kissai_infobox_variant.jpg` — the only file named for the caste.
  Adds the **pink-mauve skin variant**, **metal rings ornamenting the tendrils**, a
  **separate central chin tendril below the paired cheek ones**, a forehead lozenge
  marking, and heavy skin furrowing. Comic linework, so treat palette as the
  artist's.
- `wookieepedia_sorcerer_of_tund.jpg` — the Sorcerers of Tund, **founded by Sith
  priests** per the canon article. Useful for the priestly-order costume read.
  ⚠️ **Weak evidence on anatomy**: the figure is heavily robed and masked, and the
  order was largely non-Sith by the time depicted.
- `wookieepedia_sith_king_adas.jpg` — **negative reference for caste, positive for
  species.** The highest-resolution Sith figure available (1122×1526) and the best
  look at bony facial structure, but Adas is a **Sith King**, not a Kissai; do not
  copy his regalia onto a priest.

## ruling
(empty — owner has not reviewed this race yet)
