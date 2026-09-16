# Gand

**defName**: `RSW_RimMandrakeGand`
(`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
🔴 Its `<description>` is the single character `.` — an empty description shipping to
players.

## Sourced text (Wookieepedia)
Gand are an **insectoid** sentient species native to the planet **Gand**. Infobox:
**skin brown** (*The Empire Strikes Back*); **eyes SILVER** (*The Empire Strikes Back*)
— the only eye colour ever sourced; language Gand; **two subspecies, the Breathing Gand
and the Non-breathing Gand** (*Star Wars: The Build the Millennium Falcon* 43).
**Height, mass, lifespan, distinctions, habitat and diet are all EMPTY** — there is no
sourced measurement of a Gand anywhere in the article. Do not invent one.

*Biology and appearance*, in full: **Gand were a stocky, three-fingered, two-toed,
insectoid sentient species with brown skin whose heads featured a pair of large, silver
compound eyes.** Two subspecies: **one that breathed ammonia**, the compound making up
most of their homeworld's atmosphere, **and another that did not breathe at all,
drawing its sustenance by absorption from its food intake and approximating speech by
modulating the sounds of its flatulence**. **Ammonia-breathing Gand had to wear
respirators over their mouths in order to breathe in oxygen-rich environments.**
Genetically, Gand were **distantly related to the Kel Dor and Tognath**, who similarly
wore masks off their homeworlds.

**Behaviour and abilities.** *"You cannot surprise a Gand. We see the moves before they
happen."* — Zuckuss (*Bounty Hunters* 20). **Some Gand were findsmen, a mystic tradition
dating back centuries on their fog-shrouded homeworld, known for their uncanny tracking
skills** — note **some**, not all. **It was against Gand tradition for them to leave
their homeworld.** Per the article's naming custom: *"If they spoke their last name, it
often meant they were remotely ashamed."* The notable member is **Zuckuss**, a bounty
hunter and one of the first traditional findsmen to leave Gand.

## Visual brief
Two very different views of the same individual (Zuckuss), and together they settle the
species — including the thing the iconic image hides.

- 🔴 **The famous Gand silhouette is a MASK, not a face.** `wookieepedia_zuckuss_sideshow.png`
  (the infobox image) is a full-body figure in a long brown leather coat with a
  **hard tan helmet-like respirator carrying two huge round goggle lenses and a ribbed
  cylindrical breathing apparatus over the mouth**. Nothing of the head is visible. If
  a reference chain starts at the infobox, the species gets built as "guy in a gas
  mask."
- **The head underneath is a smooth chitinous insect skull.** `wookieepedia_masklesszuckuss_bountyhunters15.png`
  shows it bare: **an elongated, backward-sweeping cranium with heavy folded/wrinkled
  plating**, no hair, no nose, no external ears.
- **Two enormous domed compound eyes set on the SIDES of the head**, occupying much of
  the skull's width — pale, glassy, faceted, and canonically **silver**. They are the
  species' defining feature and they are lateral, not front-set.
- **A small, complex, faceted central face with mandible-like structures** below and
  between the eyes where a human nose and mouth would be. No lips.
- **The body is bare-chestable and hard-surfaced**: the maskless panel shows a
  muscular-looking torso whose surface is **segmented and seamed with visible plate
  joints and cracks**, not skin. Consistent with "insectoid."
- **Build: stocky and barrel-chested with short thick limbs.** `wookieepedia_gand_fdev.png`
  is the best single reference in the folder because it shows the **bare chitin head
  with only a small mouth-respirator** — proving the mask can be a mouthpiece rather
  than a full helmet — plus **thick, blunt, few-fingered ochre hands** and the stocky
  proportions in one image.
- **Colour is warm tan / ochre / khaki-brown**, with greener-yellow tints at the edges
  in the comic panel and a golden cast to the eye dome. "Brown" undersells how yellow
  and sandy it reads. Nothing in any image is dark green or slate red.

`donor_current_sprite.png` is the mod's current Gand head, and it is **the best donor
art in this batch**: a greyscale mask (correct — runtime-tinted by the skin gene)
showing a broad flattened chitinous cranium with vertical ribbing, **two large lateral
compound eyes rendered as stippled honeycomb ovals**, and a small central face with
paired mandible-like lower structures. It gets the lateral compound eyes, the chitin
plating and the mandibles right. What it misses versus the images: the cranium is
**too broad and flat** rather than elongated and swept back, and the eyes are flush
rather than **domed and proud of the skull**. The respirator is a separate gene
(`RSW_HeadAttachment_gandmask`), so its absence here is expected.

## Def-versus-canon (flagged)
- 🔴 **`<description>` is `.`** — literally one period. Every other race in this file
  ships prose. This is a player-visible defect and the cheapest fix in the batch.
- 🔴 **No eye-colour gene at all.** **Silver compound eyes** are the single most
  distinctive sourced Gand feature — the only eye colour ever cited — and nothing in the
  gene list expresses it.
- 🔴 **`RSW_BodySizeGene_small` is unsourced.** The infobox height field is **empty**;
  the sourced word is **"stocky"**, and Zuckuss reads as roughly human-scale but broad
  in every image. Small-and-stocky is a different creature from stocky.
- 🔴 **`RSW_lifespan_half` is unsourced.** The lifespan field is **empty**. Nothing
  says Gand are short-lived.
- 🔴 **Two of the five skin genes are unsourced**: `RSW_Skin_DarkGreen` and
  `RSW_Skin_SlateRed`. The only sourced colour is **brown**, and the images are a warm
  tan/ochre that `Outland_Skin_Brown`, `Outland_Skin_PaleBrown` and
  `Outland_Skin_Sandstone` already cover well.
- 🔴 **The findsman tracking ability is unrepresented, and the aptitudes point the
  wrong way.** The def gives `AptitudeStrong_Construction` + `AptitudeStrong_Crafting`,
  neither sourced anywhere. What canon actually attests is **uncanny tracking and
  precognitive perception** ("we see the moves before they happen") — which in RimWorld
  terms is shooting/hunting/perception, not building. `PsychicAbility_Enhanced` +
  `Turn_Gene_MeditationNeed` do carry the mystic side well, so half the idea is already
  there; the aptitudes contradict it.
- ⚠️ **The ammonia-breathing / respirator dependency is cosmetic only.** The mask
  exists as a head attachment, but no gene makes an oxygen atmosphere a problem. It is
  the species' defining mechanical fact and it is currently decoration. Also note
  **both subspecies are collapsed into one xenotype** — the non-breathing subspecies is
  canonically distinct (absorbs sustenance from food intake, speaks by modulating
  flatulence).
- ⚠️ **`Turn_Gene_VoiceDryad` applies a subspecies trait to the whole species** — the
  unusual vocalisation is specifically the **non-breathing** Gand.
- ⚠️ **`DarkVision`, `MinTemp_SmallIncrease`, `Pain_Reduced`, `Beauty_VeryUgly`,
  `Outland_FamiliarScent`, `Outland_EggLayer` are all unsourced.** A *fog-shrouded*
  homeworld is not a dark or cold one, and no reproductive mode is attested.
- ⚠️ **`Hands_Pig`**: canon is **three-fingered and two-toed**. Verify that this gene
  actually yields three digits; the `_fdev` image shows thick blunt few-fingered hands
  consistent with it, but the count is not confirmable from the art.
- ✅ Correct and canon-supported: `RSW_Head_gand` + `RSW_HeadAttachment_gandmask`,
  `RSW_butchergene_insectmeat` + `Outland_InsectBody` (insectoid),
  `PsychicAbility_Enhanced` + `Turn_Gene_MeditationNeed` (the findsman mystic
  tradition), `Hair_BaldOnly` + `Beard_NoBeardOnly`, `Outland_Skin_Brown` /
  `PaleBrown` / `Sandstone`.

## Source URLs
- https://starwars.fandom.com/wiki/Gand (article HTML Cloudflare-walled; wikitext via
  `https://starwars.fandom.com/api.php?action=parse&page=Gand&format=json&prop=wikitext`,
  14,867 chars, 2026-09-15)
- File:Zuckuss_Sideshow.png — the infobox image (a Sideshow collectible figure of
  Zuckuss, masked) → `wookieepedia_zuckuss_sideshow.png`
- The maskless Zuckuss panel from *Bounty Hunters* 15 →
  `wookieepedia_masklesszuckuss_bountyhunters15.png`
- A painted Gand illustration → `wookieepedia_gand_fdev.png`
- Primary sources behind the infobox: *The Empire Strikes Back* (skin brown, eyes
  silver), *Star Wars Character Encyclopedia: Updated and Expanded* (insectoid, origin),
  *Star Wars: The Build the Millennium Falcon* 43 (the two subspecies).

## Candidate images
- `wookieepedia_gand_fdev.png` — **the reference of record**, and the most useful image
  in the folder: a full-body painted Gand in a grey-blue coat and tan trousers with the
  **bare ochre chitin head exposed and only a small ribbed mouth-respirator**. Settles
  the domed lateral compound eye, the folded cranial plating, the tan/ochre palette, the
  thick blunt hands and the stocky barrel-chested proportions all at once.
- `wookieepedia_masklesszuckuss_bountyhunters15.png` — the *Bounty Hunters* 15 comic
  panel of **Zuckuss with no mask at all**: the clearest view of the elongated
  swept-back skull, the huge glassy side-mounted compound eyes, the faceted mandibled
  central face, and the seamed plate-like torso. Comic art with heavy rendering, so
  treat palette as the colourist's; treat the anatomy as authoritative.
- `wookieepedia_zuckuss_sideshow.png` — the infobox image: Zuckuss **fully masked** in a
  long brown coat. ⚠️ **Useful as costume reference and as a warning, not as a body
  reference** — it shows the species' famous silhouette while hiding every anatomical
  feature the entry above is about. Small in frame.
- `donor_current_sprite.png` — the mod's current head mask, and the strongest donor art
  in this batch. See the visual brief for the two shape corrections.

## ruling
(empty — owner has not reviewed this race yet)
