# Mirialan

**defName**: `RSW_RimMandrakeMirialan` (`src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`).
Note the `<label>` is lowercase `mirialan` where every neighbouring xenotype
capitalises its label — cosmetic, but visible in the UI.

## Sourced text (Wookieepedia)

Mirialans were a **long-lived, near-human species** native to the planet **Mirial**
in the Outer Rim. Infobox: class **near-human**; **skin colour blue, brown, green,
olive, pink, purple, yellow**; **hair colour black, brown, green, purple**; **eye
colour blue, brown, green, purple**; distinctions **facial tattoos**; **lifespan
centuries**; **habitat desert or wastelands**. Height and mass are **blank — do not
invent them**.

Biology and appearance: Mirialans were distinguishable by their **yellow-green or
purple coloured skin and geometric facial tattoos**. Though **typical Mirialans had
green skin**, some had blue, yellow, pink, purple, olive or brown skin.

🔑 **Most had traditional geometric tattoos on their faces which symbolized personal
achievements** — so the markings are earned, individual, and not uniform across the
species. (Compare Pantoran tattoos, which are *golden* and mark clan/family — the two
species' markings look nothing alike and must not be conflated.)

**Unusual abilities.** *"Mirialans possessed enhanced reflexes and were also
incredibly flexible and agile, traits which aided them in activities such as
lightsaber combat."* As a near-human species they were **capable of reproducing with
humans and having human-Mirialan hybrid offspring**. **Mirialans were also long-lived,
with a lifespan that could stretch into centuries** (*The Acolyte: The Visual Guide*).

**Environment, which matters and is easy to get backwards.** Their natural habitat
was **desert or wastelands**, with **Mirial itself having a COLD and dry climate of
deserts**. A Mirialan is adapted to a *cold* desert, not a hot one. The species had a
strong connection with the natural world and typically believed in the Force; the
Jedi Order included several Mirialans (Luminara Unduli, Cyslin Myr, Katri, Vernestra
Rwoh, Barriss Offee, and the fallen Seventh Sister).

## Visual brief
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."**
Removed: the flat-shaded Ady Sun'Zee illustration (`wookieepedia_adysunzee_yttransparent.png`) and the stylised game render
of a green diplomat (`wookieepedia_mirialan_diplomat.png`, formerly the infobox reference). Added two live-action images of
Luminara Unduli (Mary Oyaya, *Attack of the Clones*): `wookieepedia_luminara_closeup_aotc.jpg` (face close-up) and
`wookieepedia_luminara_fullbody.png` (full-length promotional still). `wookieepedia_luminaraunduli_swm41.png` (realistic
painting of Luminara and a second Mirialan) stays.

🔴 **Where live action disagrees with the deleted images:** the cartoon/game references gave a **vivid lime/yellow-green**
or **lavender** skin. The only live-action Mirialan skin is a **muted yellow-ochre to olive-gold** — a real skin tone
with a faint green-yellow cast, matte, with natural pores and shading. Treat vivid lime and lavender as the stylised
extremes of the sourced hue list (blue, brown, green, olive, pink, purple, yellow), not the look to render.

**The prose says "facial tattoos" and stops. The images are specific:**
- 🔑 **The markings are GEOMETRIC — small diamonds in a lattice/grid**, never curves, script or tribal flourishes. On
  Luminara the chin carries a **diamond-lattice block** directly below the lower lip; the painting adds forehead and
  outer-eye marks on the second figure.
- 🔑 **They are near-black / a darker tone of the skin, never gold.** Gold facial tattoos are the Pantoran feature —
  the specific cross-contamination to watch for, since both species are in this mod.
- **Placement:** chin block below the lower lip (most reliable); forehead centre above the brow; outer eye corners and
  cheekbones.
- **Lips are darkened** (near-black on Luminara) and eyes are human (Luminara's read deep blue).
- **Everything else is human**: human proportions, five-fingered hands, human features, no ridges or horns. Both
  live-action and painted figures wear close head coverings, so the images say little about hair.

**`donor_current_sprite.png` — this one is GOOD NEWS.** It is the greyscale RimWorld head mask behind
`RSW_MirialanHead`, and it **already carries the canonical markings baked in**: a diamond above the brow, a small
chevron/diamond cluster between the eyes, and a **diamond-lattice block on the chin below the mouth**. Greyscale is
correct for a humanlike head mask (tinted at runtime from the skin-colour gene). The only shortfall is that the mark is
one fixed pattern shared by every Mirialan, where canon says the tattoos **symbolize personal achievements** and so
differ per individual — a variation opportunity, not an error.

## Must show
- [ ] Facial markings are geometric — small diamonds in a lattice or grid — never curves, script or tribal flourishes
- [ ] Markings are near-black or a darker tone of the skin — never gold (gold is the Pantoran feature)
- [ ] Placement: a diamond-lattice block on the chin below the lower lip, plus forehead and outer-eye/cheekbone marks
- [ ] Skin is a natural matte yellow-ochre to olive-gold (other sourced hues allowed) — not vivid cartoon lime or lavender
- [ ] Otherwise fully human proportions and features; darkened lips
- [ ] Realistic rendering: natural skin texture and lighting as in the live-action film, no outlines, no cartoon shading

## Engine limits
none known

**Xenotype-versus-canon findings:**

- ✅ **Correct and well-sourced**: `RSW_MirialanHead` (carries the geometric facial
  markings — see above); the hair-colour set `Hair_DarkBlack` / `Hair_DarkBrown` /
  `Outland_HairColor_BrightSage` / `Outland_HairColor_DarkPurple` matches the canon
  black/brown/green/purple list **exactly**; `Outland_Evasive` and
  `Turn_Gene_Duelist` are a fair reading of "enhanced reflexes… incredibly flexible
  and agile… aided them in lightsaber combat"; `Body_Standard` is right for a
  near-human.
- ✅ **Skin set is nearly complete**: `Skin_DeepYellow`, `Outland_Skin_Yellow`,
  `Outland_Skin_Lime`, `Outland_Skin_PaleLime`, `Outland_Skin_PaleSage`,
  `Outland_Skin_DeepViridian`, `Outland_Skin_DeepAzure`, `Outland_Skin_Azure`,
  `Outland_Skin_PalePurple`, `Outland_Skin_Pink`, `Outland_Skin_PalePink` cover
  green, yellow, blue, purple and pink. ⚠️ **`brown` and `olive` are in the canon
  infobox but absent from the gene list**, and the greens skew bright — canon calls
  the typical case **yellow-green**.
- 🔴 **The centuries-long lifespan is sourced canon and is NOT represented.** There
  is no longevity or slow-ageing gene in the list. This is the clearest
  canon-versus-def gap for this species.
- ⚠️ **`MinTemp_SmallIncrease` may be backwards — verify its direction against the
  gene def before trusting it.** Mirial is canonically a **cold** and dry desert
  world. If `MinTemp_SmallIncrease` raises the minimum comfortable temperature
  (i.e. makes the pawn *less* cold-tolerant), it contradicts the homeworld;
  `MaxTemp_SmallIncrease` for a desert species is fine either way. Flagging the
  tension rather than asserting the mechanic — read the def.
- ⚠️ **Unsourced, no canon basis found**: `Turn_Gene_Certain`,
  `Beard_NoBeardOnly`, `Hair_Grayless`. `RSW_statgene_PsyHarmonize` is an
  *interpretation* of "a strong connection with the natural world and typically
  believed in the Force" — defensible flavour, but note that Force-sensitivity is
  not stated as a species-wide biological trait; several notable Mirialans were
  Jedi, which is not the same claim.

## Source URLs

- https://starwars.fandom.com/wiki/Mirialan (canon article; direct HTML is
  Cloudflare-walled — wikitext pulled via
  `https://starwars.fandom.com/api.php?action=parse&page=Mirialan&format=json&prop=wikitext`,
  36,347 chars, 2026-09-15)
- https://static.wikia.nocookie.net/starwars/images/3/39/LuminaraUnduli-SWM41.png → `wookieepedia_luminaraunduli_swm41.png` (⚠️ this line previously cited the file as `wookieepedia_luminaraunduli_swm41.png` and claimed it was "already on disk under that name... re-verified this pass" — it never was. Corrected 2026-09-16 against the actual directory listing.)
- https://static.wikia.nocookie.net/starwars/images/e/eb/Luminara1.jpg/revision/latest?cb=20070322160411 → `wookieepedia_luminara_closeup_aotc.jpg`
- https://static.wikia.nocookie.net/starwars/images/0/00/LuminaraUnduli-SWE.png/revision/latest?cb=20160912051446 → `wookieepedia_luminara_fullbody.png`
- NOT fetched this pass: `Star Wars: Alien Archive` (source of the "yellow-green"
  skin line), *Star Wars: The Acolyte: The Visual Guide* (source of the
  centuries lifespan), and *Star Wars: The Visual Encyclopedia* (source of the
  desert/wasteland habitat) — all cited by the article but only reachable as
  print sources.

## Candidate images
- `wookieepedia_luminara_closeup_aotc.jpg` — **the reference of record.** Live-action *Attack of the Clones* close-up of
  Luminara Unduli: yellow-ochre skin, near-black diamond-lattice chin tattoo, darkened lips, blue eyes, head covering.
  File `Luminara1.jpg` — https://static.wikia.nocookie.net/starwars/images/e/eb/Luminara1.jpg/revision/latest?cb=20070322160411
- `wookieepedia_luminara_fullbody.png` — live-action promotional still (*Encyclopedia*), full length with lightsaber:
  human build and proportions, chin tattoo. File `LuminaraUnduli-SWE.png` —
  https://static.wikia.nocookie.net/starwars/images/0/00/LuminaraUnduli-SWE.png/revision/latest?cb=20160912051446
- `wookieepedia_luminaraunduli_swm41.png` — realistic painting (*Star Wars Magazine* 41) of Luminara and a second
  Mirialan: golden-yellow skin, near-black chin and forehead diamonds. File `LuminaraUnduli-SWM41.png` —
  https://static.wikia.nocookie.net/starwars/images/3/39/LuminaraUnduli-SWM41.png
- `donor_current_sprite.png` — the repo's own greyscale `RSW_MirialanHead` mask. Kept as a **positive** reference: it
  already carries canonically-placed forehead, inter-brow and chin-lattice diamond markings.

## ruling

(empty — owner has not reviewed this race yet)
