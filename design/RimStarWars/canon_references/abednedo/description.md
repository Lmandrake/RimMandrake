# Abednedo

**defName**: `RSW_RimMandrakeAbednedo`
(`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).

## ✅ INDEPENDENTLY RE-VERIFIED — 2026-09-20

Re-sourced from the live web by an agent **forbidden from reading this library**, so this is corroboration rather than an echo. Source: Wookieepedia **raw wikitext** via the Fandom API (the rendered pages sit behind a Cloudflare wall; wikitext gives the infobox and its `<ref>` citations verbatim), with the CANON and LEGENDS pages kept apart.

- canon infobox skin **brown / cream / gray / orange / pink / tan**, one named work per value — CONFIRMED verbatim.

⚠️ **Text only.** No infobox image was rendered or pixel-sampled, so any claim in this entry that rests on how a picture *looks* is untouched by this pass and remains unmeasured.

---

## Sourced text (Wookieepedia)
Abednedos are a **humanoid, mammalian** sentient species native to a planet also
called Abednedo, in the **Colonies** region. Infobox: **no height, mass or lifespan
is sourced** — do not invent one. Skin color is a wide individual menu: **brown**
(*The Force Awakens*), **cream** (*Star Wars: Uprising*), **gray** (*TFA Visual
Dictionary*), **orange** (*IDW Adventures* 5), **pink** and **tan** (*Visual
Dictionary*). Hair color: blond, brown, gray, white. Eye color: black, blue, brown,
green. Sole listed distinction: **dangling mouth tendrils** (*Star Wars: Aliens of
the Galaxy*). Language **Abednedish**, which has its own writing system.

Body plan, verbatim in substance from *Biology and appearance*: those who were brown
often had **skin mottled with gray**. They had **fleshy, thin nostrils** and **black
eyes, which sat in sockets protruding from the side of their elongated head** — the
eyes are laterally placed on outboard bulges, not front-set in a human face. They
possessed **wattles, or facial tendrils, remnants of sensory organs that helped their
ancestors navigate underground in the dark**. They could grow hair **above their eyes
and on the side and back of their heads** (blond, brown, gray, white). Arms terminate
in **five digits**; **legs end in three**. One individual, the scavenger "Crusher"
Roodown, was **significantly larger than all other known Abednedo** — an attested
outsize variant, not the norm.

**Behaviour and abilities.** Gregarious and clever; their **curiosity, acceptance of
other species, and skill with languages** made them a common galactic sight. Many
speak Basic. **A colonial species — they had migrated and adapted to dominate many
worlds.** Strong supporters of the New Republic. No superhuman ability, no toughness
claim, no combat aptitude is attested anywhere in the article.

## Visual brief
**The head is the entire species read.** All three canon images agree tightly, and
what they show is more specific than the prose:

- **A long, forward-projecting, downward-tapering snout** that hangs well below the
  jawline and ends in a blunt, slightly hooked, fleshy tip. The skull is a smooth
  elongated dome with **no visible brow, no external ears, no hair on the crown**.
  The silhouette is closest to a **tapir or a shoebill**, not a human head.
- **Eyes on the SIDES of two prominent outboard bulges** near the top of the head,
  half-lidded, small, dark. In `wookieepedia_brasmon_kee.jpg` the sockets are
  distinctly separate raised pods with a valley between them. This is the single
  detail a text-only prompt will get wrong — it will put two human eyes on the front
  of the face.
- **Two long, thin, pendulous tendrils hanging from the underside of the snout**,
  roughly level with the tip. They read as slender fleshy whiskers, not as a beard
  and not as a moustache — clearest on Brasmon Kee, present but shorter on Cai
  Threnalli.
- **Hair, where present, is a long droopy fringe from the SIDES and back of the head
  only** — Brasmon Kee has a full white lateral mane framing the snout. The crown is
  always bare. So "bald" and "no beard" are both wrong as a total description: the
  species is crown-bald *with* side hair.
- **Skin reads mottled and blotched**, not flat: fine dark speckling and patchy
  discoloration over a base tone, with the wrinkles concentrated around the eye pods
  and the base of the snout.
- 🔴 **The palette on screen is grey-cream, NOT orange.** Cai Threnalli (the infobox
  image, and the character actually seen in *The Force Awakens*) is a pale
  **grey-cream/bone** with grey mottling. Slowen-Lo is a darker **grey-brown**.
  Brasmon Kee is a warm **pink-tan**. Nothing in the three images is orange. Orange
  is a sourced *possible* color from a single comic, and treating it as the default
  is the failure mode here.

`donor_current_sprite.png` is a **greyscale head mask** (runtime-tinted by the
skin-colour gene, so its lack of colour is correct and not a defect). Shape-wise it
captures the elongated crown dome and the two lateral eye pods, and it has a small
squared muzzle — but the **snout is far too short and blunt** (it stops at the jaw
rather than hanging below it), and the **tendrils are absent entirely**, reduced to
two tiny nubs at the mouth. Since tendrils are the species' *only* infobox-listed
distinction, this is the highest-value correction available. There are also no eye
markings and no mottling texture.

## Must show
- [ ] Long, forward-projecting, downward-tapering snout hanging below the jawline with
  a blunt, slightly hooked, fleshy tip
- [ ] Eyes set on the sides of two separate raised bulges near the top of the head, not
  front-facing on a flat face
- [ ] Two long, thin, pendulous tendrils hanging from the underside of the snout
- [ ] Crown always bald; any hair grows only from the sides and back of the head
- [ ] Skin reads mottled and blotched, not a flat single tone
- [ ] Palette is grey-cream/bone, grey-brown, or pink-tan — never orange

## Engine limits
none known

## Def-versus-canon (flagged)
- 🔴 **No grey or cream skin gene.** The list carries `Skin_Orange`,
  `Outland_Skin_PaleOrange`, `Outland_Skin_PalePink`, `Outland_Skin_Brown`,
  `Outland_Skin_PaleBrown`, `Skin_Melanin1/3/5` — i.e. the whole orange-to-brown
  band, and **not** the grey-cream that the on-screen Abednedo actually is.
- 🔴 **`AptitudeStrong_Construction` and `AptitudeStrong_Mining` have no canon
  basis** and pull against what *is* sourced: linguistic skill, cleverness,
  gregariousness, sociability. Nothing in the article makes them miners or builders.
- ⚠️ `Outland_ThickSkin` and `WoundHealing_Slow` are unsourced inventions; no
  toughness or frailty trait is attested.
- ⚠️ `DarkVision` is an over-read: the wattles are sourced as remnants of organs
  that helped **their ancestors** navigate underground — not as a present-day sense.
- ⚠️ `Hair_BaldOnly` loses the canonical **side-and-back hair** (see Brasmon Kee);
  `Body_Hulk` in the list is defensible only as the "Crusher" Roodown outlier.

## Source URLs
- https://starwars.fandom.com/wiki/Abednedo (article HTML Cloudflare-walled; wikitext
  pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Abednedo&format=json&prop=wikitext`,
  30,172 chars, 2026-09-15)
- File:CaiThrenalli-CGSWG.png — the infobox image → `wookieepedia_caithrenalli_cgswg.png`
- File:SlowenLo-CGSWG.png → `wookieepedia_slowenlo_cgswg.png`
- Brasmon Kee (Abednedo senator), the *Biology and appearance* inline image →
  `wookieepedia_brasmon_kee.jpg`
- NOT fetched this pass: https://www.starwars.com/databank/slowen-lo (official
  Databank, cited by the infobox for eye colour).

## Candidate images
- `wookieepedia_caithrenalli_cgswg.png` — **the reference of record.** The infobox
  image: Cai Threnalli, Resistance X-wing pilot, full body in orange flightsuit,
  transparent background. Settles the grey-cream mottled palette, the long tapering
  snout, the lateral eye pods and the crown-bald head.
- `wookieepedia_brasmon_kee.jpg` — the best *head* reference, and the only one
  showing hair: senator Brasmon Kee in a woven cap, pink-tan skin, a full white
  lateral mane, and the two long snout tendrils at full length. Photographed from a
  printed page (visible paper grain), so treat exact hue as approximate; treat the
  anatomy as authoritative.
- `wookieepedia_slowenlo_cgswg.png` — Slowen-Lo in white robes, a third individual at
  a darker grey-brown, confirming the head plan recurs while the hue shifts. Small in
  frame; useful mainly as corroboration and for full-body proportions (ordinary
  humanoid build, five-fingered hands).
- `donor_current_sprite.png` — the mod's current head mask, for comparison only. See
  the visual brief for what it gets wrong.

## ruling
(empty — owner has not reviewed this race yet)
