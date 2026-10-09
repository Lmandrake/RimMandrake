# Sith Kissai (Red Sith)

⚠️ **Renamed 2026-09-20** (`XENOTYPE_CANON_CORRECTION_1`): defName and label both
carried the false "(Pureblood)" — purebloods are hybrids, this caste is not one.
Owner ruled the full fix; the ripple was swept across `src/`. The commentary
below about the label being "questionable" predates that fix and now describes
resolved history, not a live defect.

**defName**: `RSW_RimMandrakeSithKissai`, label `Sith Kissai (Red Sith)`
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
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."** No live-action, photoreal or film depiction of the Sith species exists (Wookieepedia's `Images of Sith (species)` holds only SWTOR game portraits, comics and sourcebook paintings; `Kissai` has no image category). The two ink/comic images were deleted: `wookieepedia_jatm_sith_group.jpg` (*Jedi Academy Training Manual* plate, file `Massassi-JATM.jpg` — also the Kissai infobox, though named for the Massassi) and `wookieepedia_kissai_infobox_variant.jpg` (comic panel `Kissai_1.jpg`). What remains is **realistic painted art only**: the *Journal of Master Gnost-Dural* timeline painting of both castes (`wookieepedia_massassi_and_kissai_jmgd.jpg`, new), the *Book of Sith* Sith King Adas, and the Sorcerer of Tund painting.

**What the painted references show (render it this way — natural skin, real light, not comic ink):**
- **Saturated red skin**, from deep brick-crimson to a warmer red-tan; some individuals pinker (sourced: "some members … retained more pink shades of skin tone in adulthood").
- **Eyes:** yellow-gold to glowing pale under a heavy bony brow (painted art); canon's colour list includes yellow and white.
- **Facial tendrils:** fleshy tendrils hang from the cheeks/jaw and chin — in the JMGD painting short and goatee-like on the human-proportioned priest/noble figure, long, many and dreadlock-like on the Massassi warrior beside him. ⚠️ The old brief's "very long horizontal cheek tendrils sweeping sideways" came from the deleted JATM ink plate; **no remaining realistic image shows that sideways sweep** — treat it as one illustrator's reading.
- **The priestly caste is the most human-proportioned**: a near-human face and build (JMGD centre figure: dark hair, goatee tendrils, gold pauldrons), set against the hulking spiked Massassi.
- **Dress:** heavy hooded robes and gold-trimmed regalia for priests (Sorcerer of Tund), gold ornamented pauldrons and armour (JMGD).
- ⚠️ The ornamented ring-clasped tendrils, forehead lozenge markings and pink-mauve comic palette were all sourced from the deleted comic panel and are **no longer supported by an image** — the pink variant stays sourced in text.

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

## Must show
- [ ] Saturated red skin (deep crimson to red-tan), a pinker variant allowed
- [ ] Yellow-gold or pale glowing eyes under a heavy bony brow
- [ ] Fleshy tendrils hanging from the cheeks/jaw and chin
- [ ] Near-human face and build for the priest caste — distinctly less monstrous than the spiked Massassi warrior caste
- [ ] Hooded robes and gold-trimmed regalia for priests
- [ ] Realistic rendering: natural painted-skin texture and lighting, no outlines, no comic ink or cartoon shading

## Engine limits
none known

## Def-versus-canon (flagged — not fixed)

`RSW_RimMandrakeSithKissai` is the **best-formed of the three Sith
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
  `XENOTYPE_CANON_CORRECTION_1` — flagged, not yet renamed (the `NAMING_SCHEME_EXECUTION_1` gate closed 2026-08-31).

## Source URLs
- https://starwars.fandom.com/wiki/Kissai — wikitext via
  `https://starwars.fandom.com/api.php?action=parse&page=Kissai&format=json&prop=wikitext`,
  8,204 chars, 2026-09-15. (`page=Kissai/Legends` → `missingtitle`; the base page is
  already the Legends article, tagged `{{Top|leg}}`.)
- https://starwars.fandom.com/wiki/Sith_(species)/Legends — 127,967 chars,
  2026-09-15. Shared anatomy and the caste hierarchy.
- https://starwars.fandom.com/wiki/Sith_(species) — canon article, 7,414 chars,
  2026-09-15. Source of the Sorcerers of Tund line.
- https://static.wikia.nocookie.net/starwars/images/6/63/Sorcerer_of_Tund_EGF.jpg → `wookieepedia_sorcerer_of_tund.jpg` (777×1000)
- https://static.wikia.nocookie.net/starwars/images/e/ef/SithKingAdas-BoSSFtDS.png → `wookieepedia_sith_king_adas.jpg` (1122×1526)
- https://static.wikia.nocookie.net/starwars/images/8/8d/Massassi_and_Kissai.jpg → `wookieepedia_massassi_and_kissai_jmgd.jpg` (1182×626)
- NOT fetched: no `starwars.com/databank` page exists for Kissai; not attempted.

## Candidate images
- `wookieepedia_massassi_and_kissai_jmgd.jpg` — **the reference of record.** Realistic painted timeline art, *The Journal of Master Gnost-Dural* / Timeline 12, file `Massassi and Kissai.jpg`: red Sith of both castes together — near-human priest/noble with goatee tendrils and gold pauldrons beside a spiked, tendril-maned Massassi — https://static.wikia.nocookie.net/starwars/images/8/8d/Massassi_and_Kissai.jpg/revision/20180817170438
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
