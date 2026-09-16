# Muun

**defName**: `RSW_RimMandrakeMuun` (verified present in
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`, line 1265 —
that file is GENERATED, do not hand-edit).
Assigned `Jawa_AscendantHelix: S`, `Jawa_HuttCartel: R`.

## Sourced text (Wookieepedia)

Canon infobox: **height "just under 2 meters"** (`Endless Vigil`); skin colour **pale
pink**, **gray**, **pink**, **white**, and **green** (the last only from a Martin Fisher
tweet confirming a screen appearance); distinctions **elongated skulls**, **flat nose**,
**three hearts**; origin **Muunilinst**; habitat **snowy mountains**. **Mass and lifespan
are UNSOURCED — do not invent them.** Hair colour and eye colour are both blank in the
infobox.

> Muuns were a thin, tall humanoid species with elongated heads who ran the InterGalactic
> Banking Clan throughout the waning days of the Galactic Republic and into the New
> Republic Era.

Appearance, verbatim from the article body:

- *"The Muuns were a tall, pale humanoid species … **The species' elongated skulls added to
  their height.** Muuns hairless heads featured **small eyes over a long, shallow nose,
  often giving their speech a nasal quality.** Their **small ears were also flat, and were
  found underneath their skullcap.**"*
- *"Their **thin arms were of normal length**, featuring **five-digit hands. The last two
  fingers of their hands were much shorter than the others.**"* — arm length is *normal*;
  it is the skull and the legs that are exaggerated.
- *"**Unlike some other humanoid species, in Muuns females did not possess prominent
  breasts.**"*
- *"Underneath their slim waist were a pair of **very long, thin legs**."*
- **The average Muun was just under 2 meters tall; Nix Card was 2.46 meters** — so
  individual variation upward is canonical and sourced.

**Behaviour and abilities:**
- *"They were a very intelligent species, known to have **incredible mathematical
  capabilities**,"* used in running the InterGalactic Banking Clan.
- *"Although good at financial strategy, they were considered to be **inept at warfare**,"*
  and *"their **cowardice was also considered legendary**, so during the Clone Wars the
  IGBC used the Iotran Guard and IG-series battle droid army to fight for them."*
  ⚠️ Both of those are sourced to a **German fan-magazine "Database" column**
  (`OSWM 121`/`122`) rather than to a film or novel — weaker sourcing than the rest of the
  article, flagged rather than dropped.
- 🔑 **Force sensitivity is canonical and sourced**: *"The species were able to have a
  connection to the Force, and use it"* (`Endless Vigil`). **Darth Plagueis, apprentice of
  Darth Tenebrous and master of Darth Sidious, was a Muun** — the species has produced a
  Dark Lord of the Sith. If Force powers ever land, the Muun is a species where a psychic
  gene is *defensible*.
- **Three hearts** is the one exotic internal-anatomy fact (infobox, `Endless Vigil`).
- Muuns build *"their empire high amidst snowy mountain peaks"* on Muunilinst; in the New
  Republic era they were still working for the Banking Clan, and several were seen
  relaxing in a **mud bath** at a spa on Lanupa.

🔴 **Repo def contradictions — this def is the roughest of the five in this batch:**

1. ⚠️ **`iconPath` is `UI/Icons/Xenotypes/Genie` — the VANILLA RimWorld Genie icon.**
   Every other species in this batch points at a real
   `RimMandrakeSW/OR/OuterRim/XenotypeIcons/Xenotype_<Species>` file. There is **no Muun
   art anywhere in `src/`** (searched: no texture, no gene icon, no xenotype icon, no name
   files). The Muun is the only species in this batch with **zero dedicated art**.
2. **`Outland_Skin_Sandstone` + `Outland_Skin_Granite` are the only skin genes** — tan and
   grey stone tones. Canon is **pale pink / grey / pink / white / green**. The pale-pink
   and white readings that dominate every reference image are absent, and the images show
   skin far paler and cooler than sandstone.
3. **`AptitudeStrong_Medicine` and `AptitudeRemarkable_Crafting` are unsourced.** Nothing
   in the article makes Muuns healers or artisans. The sourced aptitude is
   *mathematical/financial* — `AptitudeRemarkable_Intellectual` is right and well earned.
4. **`Immunity_Weak` + `WoundHealing_Slow` + `Delicate` are unsourced.** The article gives
   the Muun no fragility; it gives them **cowardice and military ineptitude**, which is a
   behavioural trait, not a constitution. `AptitudePoor_Shooting`/`AptitudePoor_Melee` do
   capture "inept at warfare" correctly.
5. **The description contains a typo that will ship**: *"known for running the InterGalactic
   **Ganking** Clan."* Should be **Banking**.
6. ⚠️ **`RSW_Head_quarren` is NOT a Quarren squid-face** — checked the GeneDef rather than
   guessing from the name: it is labelled **"oval head" / "enlarged, egg-shaped forehead"**
   and forces `RSW_Male_Egghead`/`RSW_Female_Egghead`, whose art lives at
   `SWX/Pawn/HeadType/quarren/*_Egghead`. As a donor for an elongated Muun skull it is
   **defensible**; it is simply generic and shared with other species, and it is an **egg,
   not the tall back-swept cone the references show.** No contradiction — recorded so the
   next reader does not raise a false alarm from the defName.
7. The def **omits Force sensitivity entirely** — the one place canon would support a
   psychic gene, and unlike the Rakata case (psychic genes on a Force-blind species) this
   is an omission rather than an error. Recorded for the owner's judgement, not as a fix.

## Visual brief

**The Muun is defined by ONE silhouette: a very tall, near-emaciated figure whose skull
continues upward and backward past where a human head stops.** Get the skull and the
leg length right and the species reads; get them wrong and it is just a thin bald human.

**Head** (best read: `wookieepedia_san_hill_aotc.jpg`, a film-resolution close-up):
- **The cranium is a tall, smooth, hairless dome that sweeps up and BACK**, roughly
  doubling the height of the head above the brow. It is **not** a sphere and not a
  forward-bulging egg — the mass goes over and behind the skull, like a swept-back helmet.
- **Skin is mottled pale grey-pink, not flat**: irregular darker freckles and blotches
  scatter over the cranium and cheeks, and there are **fine vertical creases down the
  cheeks and long horizontal creases across the brow.** An untextured flat-pink Muun is
  the failure mode.
- **Eyes are small, dark, deep-set under heavy hooded lids**, set low and close relative
  to the enormous cranium. There is no visible brow ridge — just a crease.
- **The nose is long and shallow with almost no bridge**, running as a narrow ridge down
  the centre of the face to small nostrils sitting well above a **small, thin-lipped,
  down-turned mouth.** The whole face is compressed into the lower third of the head.
- **The ear is a small flat disc set low and far back on the side of the head** — barely a
  feature, matching *"small ears … flat … underneath their skullcap."*
- **The neck is long, thin and tendon-lined**, and it is *part of the silhouette* — the
  head sits on a stalk.

**Body** (best read: `wookieepedia_infobox_arden_beckwith.jpg` full-figure, and
`wookieepedia_mudbath_bare_torso.jpg` for what is actually underneath the clothes):
- **Extremely gaunt.** The mud-bath still is the only image in the set showing an
  **unclothed** Muun torso, and it shows a **narrow chest with ribs and sternum plainly
  visible, sharply defined collarbones, and no chest musculature.** It also **confirms the
  no-prominent-breasts text visually.**
- **Arms are very long-looking but the article says "of normal length"** — the impression
  of length comes from how thin they are and from the **long thin fingers.** Hands are
  five-digit with **the last two fingers markedly shorter**; in the San Hill close-up the
  hand reads as three long fingers plus a thumb at a glance, which is that shortening.
- **Legs are the genuinely elongated limb** — "very long, thin legs" under a slim waist.
  Height comes from legs plus skull, not from torso.
- Overall proportion at ~2 m: **narrow, vertical, brittle-looking.** `Body_Thin` +
  `RSW_Body_gaunt` in the def is the right instinct.

**Body vs. clothing** (the Muun is nearly always robed, and the robe is doing a lot of the
silhouette work):
- Arden Beckwith wears a **high-collared wrapped tunic with a tabard over it, a narrow
  belt, and a long open-fronted skirted coat, plus knee boots.** Bare skin visible: head,
  neck, hands, and one lower leg. **The wide-shouldered look is the garment, not the
  body** — underneath, per the mud-bath still, the shoulders are bony and narrow.
- San Hill wears a **dark robe with a heavy shawl collar and a pale green neck-ring/collar
  band.** 🔴 **That green band is clothing, not anatomy** — it sits at the base of the long
  neck and is easy to mistake for a fleshy collar or throat sac. It is not.
- The mud-bath Muun wears **only a towel on the head.** That is the image to trust for
  anatomy.

**`donor_current_sprite.png` is NOT Muun art.** There is no Muun art in the repo. This file
is a copy of `SWX/Pawn/HeadType/quarren/Male_Egghead_south.png` (512×512, RGBA), the shared
head forced by the `RSW_Head_quarren` gene the Muun xenotype uses — **weak evidence, and
included only so the owner can see what a Muun currently looks like in game.** It is a
greyscale tint mask (correct for a RimWorld humanlike head; colour comes from the skin
gene). What it captures: a bald, hairless, enlarged rounded cranium with the face pushed
low, and two small simple eyes. What is **missing**: the skull is a **plain vertical egg,
not swept back**; there is **no nose, no mouth, no ear, no mottling and no creasing**; and
because it is a head sprite on a standard RimWorld body, **the long-legged narrow
silhouette — half of what makes a Muun a Muun — is not represented at all.**

## Source URLs
- https://starwars.fandom.com/wiki/Muun — canon article. Direct HTML is Cloudflare-walled;
  wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Muun&format=json&prop=wikitext`
  (15,061 chars, 2026-09-15). Source of every fact above.
- https://starwars.fandom.com/wiki/Muun/Legends — Legends article also fetched (23,786
  chars, 2026-09-15); **nothing was taken from it**, because the canon article is
  substantive and its own "Behind the scenes" already flags that the FFG sourcebook
  `Endless Vigil` misidentifies Scipio as the Muun homeworld (the homeworld is
  **Muunilinst**).
- https://static.wikia.nocookie.net/starwars/images/2/2c/Muun_FDEV_Arden_Beckwith.png
  (File:Muun_FDEV_Arden_Beckwith.png, the canon infobox image →
  `wookieepedia_infobox_arden_beckwith.jpg`)
- https://static.wikia.nocookie.net/starwars/images/7/75/SanHillPledge-AOTC.png
  (File:SanHillPledge-AOTC.png, *Attack of the Clones* →
  `wookieepedia_san_hill_aotc.jpg`)
- https://static.wikia.nocookie.net/starwars/images/1/17/Femalemuun.jpg
  (File:Femalemuun.jpg, captioned on the article *"A bare-chested Muun relaxing in a mud
  bath"*, from *Skeleton Crew* → `wookieepedia_mudbath_bare_torso.jpg`)
- https://static.wikia.nocookie.net/starwars/images/6/6c/Plagueis-TheAcolyte.png
  (File:Plagueis-TheAcolyte.png → `wookieepedia_plagueis_acolyte.jpg`)
- NOT fetched this pass: a `starwars.com/databank` Muun species page was not attempted.

## Candidate images
- `wookieepedia_san_hill_aotc.jpg` — **the reference of record for the head.**
  Film-resolution close-up of San Hill: the back-swept cranium, the mottled pale grey-pink
  skin with freckling and creases, the small hooded eyes, the long shallow bridgeless
  nose, the small flat low-set ear, the long thin neck, the long unequal fingers. Waist-up
  and robed.
- `wookieepedia_infobox_arden_beckwith.jpg` — **the reference of record for proportion.**
  The canon infobox image; a full standing figure that settles overall height, the narrow
  vertical silhouette and the long legs. Heavily clothed, so read proportion here and
  anatomy elsewhere.
- `wookieepedia_mudbath_bare_torso.jpg` — **the only unclothed anatomy in the set, and
  therefore the reference of record for the torso.** A live-action Muun reclining in a mud
  bath with arms spread: visible ribs and sternum, bony collarbones, no chest muscle, no
  breasts. ⚠️ Weak in other respects — the figure is half-submerged in mud, back-lit
  through steam, and the head is under a towel, so it says nothing about the skull.
- `wookieepedia_plagueis_acolyte.jpg` — **very weak evidence, kept for completeness only.**
  Darth Plagueis in *The Acolyte*: the frame is almost entirely black, with only one
  orange-lit eye and a sliver of cheek legible. It confirms nothing about colour or
  proportion and should not be used as a colour reference.

## ruling
(empty — owner has not reviewed this race yet)
