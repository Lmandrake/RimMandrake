# Echani

**defName**: `RSW_RimMandrakeEchani` (verified present in
`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`). Matrix:
`Empire: R` — **rare**, Imperial-only. Canonically apt: Echani martial art and Echani
double-bladed vibroblades were what the **Emperor's Royal Guard** trained and fought with.

## Sourced text (Wookieepedia)

🔴 **Current canon is a near-empty stub and its infobox is completely blank.** `/wiki/Echani`
(1,873 chars total) says only that the Echani "were a sentient species that lived in the
galaxy," that **they shared their name with a form of martial art**, and recounts one Echani
man at the Valo Republic Fair nearly being mauled by targons. **Every infobox field —
class, height, mass, skincolor, haircolor, eyecolor, distinctions, lifespan, origin, habitat,
diet, language — is empty.** First canon mention: the 2021 novel *The High Republic: The Rising
Storm*. **So there is no canonical Echani appearance, size or lifespan whatsoever.** Everything
below is Legends, and the def's own `<description>` is lifted verbatim from the Legends
biology paragraph.

**Legends** (`/wiki/Echani/Legends`). **Near-Human** species from the **Inner Rim** planet
**Eshan**. Infobox: skin **"Chalk-pale, dark"**; hair **"White, dark"**; eyes **Silver**;
distinctions **"Light skin, white hair and eyes, remarkable familial similarity"**; subspecies
**Thyrsians**. **Height, mass and lifespan are all blank in the Legends infobox too** — so
even Legends gives no figure for any of the three.

Body text:
- **"The Echani had similar anatomy to that of humans, but were physically distinct due to
  their light skin, white hair and silver eyes."**
- 🔑 **"They exhibited among themselves a remarkable similarity to each other in their body
  type and facial features, with close family members such as siblings often appearing
  indistinguishable to an outside observer."** This is listed as a *distinction*, i.e. it is
  as defining as the white hair.
- 🔑 **The Thyrsian subspecies is the opposite colour.** "The Thyrsian subspecies of the
  Echani, in contrast, shared few of these traits, **possessing dark hair and skin**, rather
  than the white hair and silver eyes the Echani became known for." The **Sun Guard** arose
  from them. `/wiki/Thyrsian` calls their appearance **"a diametric contrast"** and
  **"almost polar-opposite"** to the Echani, listing skin **Dark, Pale** and hair **Dark**.
- **"It was believed that the Echani were a result of Arkanian experimentation with the Human
  genome"** — the in-universe explanation for the familial resemblance.

🔴 **The one ability everyone attributes to them is explicitly NOT biological, and the article
says so in as many words:** *"Due to the all-encompassing use of combat in all levels of their
culture, Echani Generals were seen by others as having the ability to predict their opponent's
next move. **This was not a biological trait inherent to the Echani or their subspecies.**
Instead, it arose from a culture where combat was seen as the truest form of communication."*
Any gene implementing Echani precognition would be a canon error by construction.

**Behaviour and culture (Legends).** *"To the Echani, battle is a means of communication — it
is an art, in the truest sense of the word."* A **matriarchal, caste-based** society; the
**Six Sisters** confederacy of six worlds governed by the **all-female Echani Command** council.
They developed a **kinetic communication style** and **"can instantly identify an individual
through subtle shifts in body language."** *"Echani culture held the belief that to know one
fully, you must fight them."* **Duels are rituals and "do not allow for armor or anything that
restricts movement."** They **read feelings and emotion through combat** — "a combat between
two people said more than hours of talking." Because siblings are often indistinguishable,
**reading body movement to tell like individuals apart became an essential requirement.**

**Combat and craft (Legends).** 🔑 They **focused on unarmed combat and melee weapons** and
were **"considered excellent craftsmen of these weapons"** — galaxy-standard **vibroswords were
based on Echani designs**, and **Echani-made double-bladed vibroblades** were used by the
Emperor's Royal Guard. **Echani personal energy shields** were widely popular in Meetra Surik's
era. They **largely eschewed heavy armor, preferring light armor, and trained in minimal
clothing**; their style **"focused more on agility and movement,"** avoiding anything hampering
freedom of movement. A Mandalorian mercenary was **disgusted** at their "light" weapons; they
held a long rivalry with the Mandalorians.

## Visual brief

There are only three usable references and **no full-body reference exists in this
directory** — all three are portraits or stylised. Say so rather than over-reading them.

**`wookieepedia_legends_infobox_raskta.jpg`** (the Legends infobox, Raskta Lsu, painted):
- **Skin is cool pale with a distinct blue-grey cast** — not a warm human pale. In the
  shadowed areas it reads faintly lilac/blue. "Chalk-pale" is the right word.
- **Long, thick, loose silver-white hair**, mid-value grey in shadow, high-value white at the
  edges.
- 🔑 **The eyebrows are DARK, not white.** A detail a text-only prompt would get wrong from
  "white hair": both this image and Brianna show dark brows over white hair.
- Eyes are pale and light-irised — consistent with "silver," though the resolution will not
  settle silver-vs-white.
- Human facial structure throughout: no non-human feature of any kind. **Near-human means
  near-human here** — the only species read is the colour scheme.

**`wookieepedia_handmaiden_brianna.jpg`** (Brianna the Handmaiden, game render) is the
important corrective and comes with a caveat: **her skin is a WARM light human tone**, not
chalk-white — clearly warmer than Raskta — with the same long straight **silver-white** hair
and **dark brows**, and light eyes. ⚠️ **The article states Brianna is *half*-Echani**, so she
is legitimately a blended reference; read her as the warm end of "light skin," not as the
species centre.

**`wookieepedia_echani_practice.jpg`** (stylised illustration of Echani training beneath a
Royal Guard helm) is the best behavioural reference in the set:
- Two figures in **mirrored, symmetrical, near-identical poses** — the "indistinguishable
  siblings" and "combat as conversation" ideas made visual in one image.
- **Chalk-white to pale-grey skin, short white hair**, human proportions.
- 🔑 **They are training in minimal clothing** — bare arms and legs, dark shorts, **wraps at
  the forearms and shins, and sandals.** This matches "trained in minimal clothing" and
  "eschewed heavy armor" exactly, and it is the strongest apparel cue for how an Echani pawn
  should be dressed.

🔑 **Reading across all three: the constants are silver-white hair, dark eyebrows, light eyes,
and ordinary human anatomy. The variable is how cold the pale is — blue-grey chalk to warm
human light.** And **none of the three shows a Thyrsian**, so the dark-skinned half of the
species has no image here at all.

**There is no `donor_current_sprite.png` — no Echani pawn art exists in this repo.** The
xenotype does not even carry a species icon: `<iconPath>UI/Icons/Xenotypes/Baseliner</iconPath>`
points at vanilla RimWorld's generic **Baseliner** icon, and there is no Echani head, face or
body texture anywhere in `src/`. What *does* exist is **Echani gear**, and it is
canon-appropriate: `Armoury/Textures/vibroblade_echani.png`,
`vibrosword_echani.png`, `vibroglaive_echani.png`, `Items/shield_echani1.png`,
`shield_echani2.png`, `SWApparel/MilitarySuit/echani`, `SWApparel/CombatSuit/echani`, and
`Items/Consumables/Stimulants/stim_echani/`. Vibroswords, vibroblades and personal shields are
precisely what the Legends text credits the Echani with; the gear side of this species is in
better shape than the pawn side.

## Source URLs

- https://starwars.fandom.com/wiki/Echani — current canon; wikitext via
  `https://starwars.fandom.com/api.php?action=parse&page=Echani&format=json&prop=wikitext`
  (1,873 chars, 2026-09-15). A stub with a wholly empty infobox.
- https://starwars.fandom.com/wiki/Echani/Legends — Legends, the substantive article; wikitext
  via the same endpoint with `page=Echani/Legends` (11,916 chars, 2026-09-15). Appearance cites
  *Darth Bane: Rule of Two* and *Galaxy at War*; culture and the "not a biological trait"
  disclaimer cite *KOTOR II: The Sith Lords*; weapons cite *Galaxy at War* and *KOTOR*.
- https://starwars.fandom.com/wiki/Thyrsian — the dark-skinned subspecies; wikitext via the
  same endpoint with `page=Thyrsian` (7,249 chars, 2026-09-15). Its infobox has **no image**,
  so no Thyrsian reference picture could be obtained.
- https://static.wikia.nocookie.net/starwars/images/d/d0/Raskta_Lsu.jpg
  (File:Raskta Lsu.jpg, the Legends infobox → `wookieepedia_legends_infobox_raskta.jpg`)
- https://static.wikia.nocookie.net/starwars/images/9/97/Handmaidenpromo.jpg
  (File:Handmaidenpromo.jpg, Brianna → `wookieepedia_handmaiden_brianna.jpg`)
- https://static.wikia.nocookie.net/starwars/images/d/d2/Echanipractice.jpg
  (File:Echanipractice.jpg → `wookieepedia_echani_practice.jpg`)
- ⚠️ All three served as **WebP** despite `.jpg` extensions; re-encoded to real JPEG locally.
- NOT fetched this pass: no starwars.com Databank page was attempted (the species is
  Legends-dominant and unlikely to have one).

## Candidate images

- `wookieepedia_legends_infobox_raskta.jpg` — **the reference of record**, and the coldest
  pale: blue-grey chalk skin, loose silver-white hair, **dark brows**, pale eyes. Portrait
  only, painted.
- `wookieepedia_handmaiden_brianna.jpg` — the **warm** end of "light skin," same silver-white
  hair and dark brows. ⚠️ **Half-Echani by the article's own text** — a blended reference,
  labelled accordingly.
- `wookieepedia_echani_practice.jpg` — stylised, and the best **behaviour and dress**
  reference: mirrored identical poses, chalk-white skin, short white hair, minimal training
  clothing with forearm/shin wraps and sandals.
- ⛔ **No Thyrsian image was obtainable** — the subspecies page carries no infobox image. The
  dark-skinned half of the species is unillustrated here.
- ⛔ **No `donor_current_sprite.png`** — no Echani pawn art exists in this repo.

## Def-versus-canon contradictions (report only — not fixed here)

1. 🔴 **The Thyrsian half of the species is unreachable.** The Legends infobox lists skin
   **"Chalk-pale, *dark*"** and hair **"White, *dark*"**, and the Thyrsian subspecies — source
   of the **Sun Guard** — is explicitly **dark-haired and dark-skinned**, a "diametric
   contrast." The def carries only `Skin_LightGray`, `Skin_SheerWhite` and `Hair_SnowWhite`,
   with `Hair_Grayless` on top. No dark-skinned or dark-haired Echani can be generated.
2. 🔴 **"Remarkable familial similarity" — one of only three listed distinctions — has no
   gene.** Siblings appearing indistinguishable to outsiders is as canonical as the white hair,
   and nothing in the def expresses it.
3. 🔴 **`Turn_Gene_MeditationNeed` is unsourced and pushes the species in a direction canon
   explicitly forbids.** Nothing found gives Echani a meditation practice or need. Worse, the
   article goes out of its way to say the Echani ability to read and pre-empt an opponent
   **"was not a biological trait inherent to the Echani or their subspecies"** but a cultural
   product. Attaching an innate mystical/meditative gene biologises exactly what the source
   disclaims.
4. 🔴 **`Outland_LowFertility` cuts against the canon record.** Yusanis fathered the **six
   Handmaiden Sisters**, and the article states **"it was not at all unusual for children of
   the same parents to be born so as to be completely indistinguishable from one another"** —
   large, close, same-parent sibling sets. Nothing supports low fertility, and
   `Outland_DeceleratedPregnancy` is likewise unsourced.
5. 🔴 **`<combatPowerFactor>0.6</combatPowerFactor>` is internally inconsistent and
   canon-inverted.** A factor of 0.6 rates an Echani as substantially *weaker* than baseline
   for threat-point purposes, on the species canon holds up as the galaxy's melee benchmark —
   and in the same def that grants `MeleeDamage_Strong`, `Turn_Gene_Duelist` and
   `AptitudeRemarkable_Melee`. Echani is the only one of this batch's five carrying a
   `combatPowerFactor` at all.
6. ⚠️ **Eye colour is white where the source says silver.** `Outland_Eye_White` vs Legends
   infobox `eyecolor = Silver`; the `distinctions` field does say "white … eyes," so both are
   attested and this is minor — but silver is the specific cite.
7. ⚠️ **`Beauty_Pretty` + `Turn_Gene_HighBeautyStandard` and `AptitudePoor_Animals` are
   unsourced.** Nothing found addresses Echani beauty or animal handling.
8. ⚠️ **Dark eyebrows over white hair are visible in two of the three images** and are not
   expressible through `Hair_SnowWhite` alone. Worth noting for whoever authors the art.
9. ⚠️ **`iconPath` is vanilla `UI/Icons/Xenotypes/Baseliner`** — the Echani have no xenotype
   icon of their own, unlike the other four in this batch, which all point at
   `OR/OuterRim/XenotypeIcons/Xenotype_<Species>`.
10. ✅ **Well-sourced and correct — do not "fix" these:** `AptitudeRemarkable_Melee` +
    `MeleeDamage_Strong` + `Turn_Gene_Duelist` + `AptitudePoor_Shooting` (focus on unarmed
    combat and melee weapons, agility-based, disdained by Mandalorians for "light" weapons);
    `AptitudeStrong_Crafting` ("excellent craftsmen"; galaxy-standard vibroswords were
    Echani designs); `Hair_SnowWhite` and the pale skins for the mainline subspecies;
    `Body_Standard` and **no lifespan gene** — neither continuity gives Echani a height, mass
    or lifespan, so inventing either would be the error.
11. ✅ **Namer is correct** — `RSW_KoTOR_NamerEchani` reads
    `RimMandrakeSWNames/SWX/Echani/{First,Last,Nick}`, all present, contents
    Echani-appropriate (`Caelian`, `Inarin`, `Losor`). No wrong-species namer here.

## ruling

(empty — owner has not reviewed this race yet)
