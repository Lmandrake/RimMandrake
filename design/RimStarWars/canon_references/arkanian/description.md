# Arkanian

**defName**: `RSW_RimMandrakeArkanian`
(`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).

## Sourced text (Wookieepedia)
Arkanians are a **near-human**, **mammalian** sentient species native to the planet
**Arkania**. Infobox: **skin color "from tan to pale"**; **hair white**; **eyes
white**; **lifespan at least a standard century**; language Arkanian; a recognised
**subspecies, the Arkanian Offshoot**. Listed distinctions, all cited to *Disciples
of Harmony*: **pupil-less eyes, 3 fingers and a thumb** (i.e. four digits per hand),
**claw-like nails**, and **the ability to see into the infrared spectrum**. **No
height and no mass are sourced** — do not invent either.

*Biology and appearance*: Arkanians had **infrared vision as a result of evolving on
a frigid world**. **Most Arkanians resembled humans in many respects, save for pale
white eyes and clawed digits on each hand.** Seeing into the infrared **led to
extreme visual sensitivity but also allowed them to spy enemies via their body
heat**; helpful on a dark, cold homeworld, but **in certain environments many were
forced to wear polarized lenses or blinders**. Arkanian scientists had been **experts
in genetic engineering for thousands of years**, and after centuries of experimentation
produced **genetic offshoots**, whom they regarded as lesser shadows of themselves or
even slaves.

**Behaviour.** A **rigid caste system** expecting pure blood and a sharp logical mind,
which **looked down on any sign of weakness or flaw**. *"The most defining trait of
the Arkanian species was their arrogance which stemmed from their belief in their
genetic purity"* — they saw themselves as superior to all other species and **expected
subservience from outsiders**. **Scholarly pursuits were highly valued**, so many were
highly skilled scientists and academics; they were **not above selling biological
weapons to the highest bidder**, while a significant minority held that once
physiological and technological perfection is achieved one must also achieve moral
perfection. Offshoots were **bred in great variety as living experiments**, typically
short-lived, never regarded as "true Arkanians."

## Visual brief
The single canon image (two Arkanians, from *Disciples of Harmony*) is unambiguous and
it says the opposite of what most alien references say: **there is almost nothing
non-human to draw.**

- **Ordinary human build, ordinary human head, ordinary human facial proportions.**
  No head appendages, no ridges, no unusual ears, no snout. Both figures would pass as
  human at a glance and in silhouette. Whatever else is done here, the head type must
  not be sculpted into an alien shape.
- **Hair is pure white in both, and worn as ordinary hair** — long and loose past the
  shoulders on the female, short and swept back on the male. It is not a mane, not a
  crest, not fur.
- **The eyes are the read.** Pale, blank, **pupil-less** — no visible iris/pupil
  structure, just a light-toned eyeball. On the female they sit in noticeably
  **darkened, sunken orbits** with a reddish-shadowed rim, which reads as the one
  genuinely uncanny feature of the species and matches "extreme visual sensitivity."
- 🔴 **The two individuals differ substantially in skin tone, and both are inside the
  human range.** The female is a very pale, cool, almost bloodless white-grey; the
  male is a plainly warm mid-tan. This is the infobox's "tan to pale" span shown
  directly — so the range, not a single hue, is the fact to preserve. Nothing here is
  blue, green, grey-alien or unnaturally saturated.
- **Hands read as slender and long-fingered** (the female's outstretched hand is the
  best view), and at this resolution the digits **cannot be counted reliably** — the
  three-fingers-plus-thumb and claw-nail details are text-sourced, not confirmed by
  this image. Say so rather than claiming the image shows them.
- **Dress is robed, layered, sober and scholarly** in both — earth tones, sashes,
  wrapped tunics, a lightsaber on the female. Consistent with the caste/academic
  culture text, and worth noting because for a near-human species the *costume* is
  much of what will make them read as Arkanian rather than human.

`donor_current_sprite.png` is the mod's current head: a plain oval face with a
white-grey hair cap and **two large solid-black eyes**. The face shape and the white
hair are right, and note the face here is **cream-tinted rather than greyscale**.
🔴 **The solid black eyes are the direct opposite of the canonical pupil-less
pale-white eye** and are the highest-value fix in this entry — verify whether those
eyes are baked into the head texture or supplied by the `Outland_Eye_White` render
node, because if they are baked they will override the correct gene.

## Must show
- [ ] Ordinary human head, build and facial proportions — no head appendages, ridges, or
  snout
- [ ] Hair pure white, worn as ordinary hair, not a mane or fur
- [ ] Eyes pale and pupil-less — no visible iris/pupil structure
- [ ] Skin tone spans tan to pale across individuals, not fixed to a single hue
- [ ] Darkened, sunken eye orbits with a reddish-shadowed rim

## Engine limits
none known

## Def-versus-canon (flagged)
- 🔴 **`Beauty_Pretty` + `Turn_Gene_HighBeautyStandard` have no canon basis.** The
  sourced defining trait is **arrogance from a belief in genetic purity**, plus a
  caste contempt for weakness — a social/attitude trait, not attractiveness. If a
  personality gene is wanted, that is the one canon supports.
- ⚠️ **`ArchiteMetabolism` is unsourced.** Nothing attests an exotic metabolism;
  the species' engineering prowess is *cultural and scientific*, practised on others.
- ⚠️ Baked black eyes on the head sprite vs. `Outland_Eye_White` (see above).
- ✅ Correct and canon-supported, worth keeping: `Hair_SnowWhite` + `Hair_Grayless`
  (white hair), `Outland_Eye_White` (pupil-less pale eyes), `Outland_Hands_Talons`
  (claw-like nails), `DarkVision` (infrared vision), `UVSensitivity_Mild` (extreme
  visual sensitivity / polarized lenses), `MinTemp_SmallDecrease` +
  `MaxTemp_SmallDecrease` (evolved on a frigid world), `Skin_Melanin1/2/3` (tan to
  pale — a good match to the two-individual span in the image), `Learning_Fast` +
  `AptitudeStrong_Intellectual` + `AptitudeStrong_Medicine` (scholarly, millennia of
  genetic-engineering expertise), `Body_Standard` (near-human).
- ⚠️ **Lifespan is sourced only as "at least a century"** and the def carries no
  lifespan gene, which is consistent — do not add a long-life gene on this evidence.
- Not representable, recorded so nobody "fixes" it: **three fingers and a thumb**.
- Unbuilt canon hook: the **Arkanian Offshoot** subspecies is a distinct, canonical,
  enslaved variant with no def of its own. Flagging as content that exists in canon,
  not as a defect.

## Source URLs
- https://starwars.fandom.com/wiki/Arkanian (article HTML Cloudflare-walled; wikitext
  pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Arkanian&format=json&prop=wikitext`,
  6,835 chars, 2026-09-15 — a short article, and everything above is in it)
- File:Arkanians_DoH.png — the infobox image, from *Disciples of Harmony* →
  `wookieepedia_arkanians_doh.png`
- Primary source behind nearly every infobox field: *Disciples of Harmony*.

## Candidate images
- `wookieepedia_arkanians_doh.png` — **the reference of record, and the only canon
  image on disk.** Two full-body Arkanians side by side (illustrated, *Disciples of
  Harmony*): a female with long white hair, very pale skin, blank pale sunken eyes and
  a lightsaber; a male with short white hair and plainly tan skin. Because it shows
  two individuals at opposite ends of the tone range, it settles "tan to pale" as a
  *span* rather than a hue. Painted illustration, so treat brushwork as the artist's;
  treat the near-human anatomy and the white hair / blank eyes as authoritative.
- `donor_current_sprite.png` — the mod's current head, for comparison only. Correct in
  shape and hair; see the visual brief on the eyes.

## ruling
(empty — owner has not reviewed this race yet)
