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

**The prose says "facial tattoos" and stops. The images are far more specific, and
the specifics are the whole point of this entry.**

Across all three references the markings are the same *kind* of thing:

- 🔑 **The markings are GEOMETRIC LOZENGES — diamonds, chevrons and diamond-lattice
  bands — never curves, script or tribal flourishes.** A row or cluster of small
  diamonds is the motif that recurs in every image.
- 🔑 **They are rendered in a DARKER TONE OF THE PERSON'S OWN SKIN COLOUR (or
  near-black), not gold.** A green Mirialan carries dark-green marks; a purple one
  carries deep-violet marks; a yellow one carries near-black marks. **Gold facial
  tattoos are the Pantoran feature, and putting them on a Mirialan is the specific
  cross-contamination to watch for**, since both species are in this same mod.
- **Placement is consistent**: centre of the forehead above the brow; flanking the
  outer corners of the eyes and along the cheekbone; and a vertical block or
  lattice on the chin directly below the lower lip. The chin block and the forehead
  mark are the two most reliable.
- **Everything else is human.** Ordinary human proportions, ordinary five-fingered
  hands, human hair, human eyes, no ridges, no horns, no non-human features
  whatsoever. Mirialan appearance work is **skin hue plus face markings and nothing
  else** — which is also exactly what the def's own description claims, and it is
  correct.

Per-image:

- **`wookieepedia_mirialan_diplomat.png`** (the canon infobox image) is a
  **vivid yellow-green** Mirialan woman, full body: dark-green diamond marks
  centred on the forehead, arcs of small marks at the outer eyes and cheekbones, and
  a diamond cluster on the chin. Green hands, human build. This is the "typical
  green skin" case.
- **`wookieepedia_adysunzee_yttransparent.png`** (Ady Sun'Zee, a Mirialan Jedi) is
  the **purple** case and the clearest close-up: **lavender-violet skin**, with a
  band of deep-violet chevrons/diamonds across the forehead, diamond clusters
  at the outer eye corners, and a diamond lattice on the chin and jawline.
  **Green eyes, violet brows and deep-violet lips.** Stylised comic linework, so
  treat the outline as the artist's, but the marking vocabulary and placement match
  the other two exactly.
- **`wookieepedia_mirialan_luminara_swm41.png`** (Luminara Unduli and a second
  Mirialan, painted) is the **golden-yellow** case: near-black diamond marks in a
  vertical column on the chin below the lip, plus forehead and outer-eye marks on
  the second figure. Both wear head coverings, so this image says little about hair.
  It confirms the marking style survives across a third skin hue and a third
  art medium.

**`donor_current_sprite.png` — this one is GOOD NEWS and should be recorded as
such.** It is the greyscale RimWorld head mask behind `RSW_MirialanHead`, and it
**already carries the canonical markings baked in**: a diamond above the brow,
a small chevron/diamond cluster between the eyes, and a **diamond-lattice block on
the chin below the mouth** — precisely the canonical placement. Being greyscale is
correct and expected for a humanlike head mask (the game tints it at runtime from
the skin-colour gene), so the absence of colour here is not a defect. The marking
*geometry*, which is the part text prompts get wrong, is right. The only shortfall
is that the mark is one fixed pattern shared by every Mirialan pawn, where canon
says the tattoos **symbolize personal achievements** and therefore differ per
individual — a variation opportunity, not an error.

## Must show
- [ ] Facial markings are geometric lozenges — diamonds, chevrons and diamond-lattice bands — never curves, script or tribal flourishes
- [ ] Markings render in a darker tone of the pawn's own skin colour (or near-black) — never gold (gold is the Pantoran feature and must not be conflated with it)
- [ ] Marking placement: a mark centred on the forehead above the brow, marks flanking the outer eye corners/cheekbones, and a vertical block or lattice on the chin below the lower lip
- [ ] Skin hue reads yellow-green (the typical case) or one of the other sourced hues — blue, brown, olive, pink, purple, yellow
- [ ] Otherwise fully human proportions — five-fingered hands, human hair, human eyes, no ridges or horns
- [ ] The shipped head graphic already carries the forehead, inter-brow and chin-lattice diamond markings baked in at the correct canonical placement — this is a passing state to confirm, not a defect to fix

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
- https://static.wikia.nocookie.net/starwars/images/3/39/LuminaraUnduli-SWM41.png → `wookieepedia_mirialan_luminara_swm41.png` (already on disk under that name from an earlier pass; re-verified this pass)
- `wookieepedia_mirialan_diplomat.png` corresponds to `File:Mirialan_Diplomat.png`,
  the canon infobox image; `wookieepedia_adysunzee_yttransparent.png` corresponds
  to `File:AdySunZee-YTtransparent.png`. Both were already on disk from an earlier
  pass and were verified against the article's own file list this pass.
- NOT fetched this pass: `Star Wars: Alien Archive` (source of the "yellow-green"
  skin line), *Star Wars: The Acolyte: The Visual Guide* (source of the
  centuries lifespan), and *Star Wars: The Visual Encyclopedia* (source of the
  desert/wasteland habitat) — all cited by the article but only reachable as
  print sources.

## Candidate images

- `wookieepedia_mirialan_diplomat.png` — **the reference of record.** The canon
  infobox image: a full-body vivid yellow-green Mirialan with dark-green geometric
  face markings on forehead, outer eyes and chin. Best single image for skin hue
  plus marking placement together.
- `wookieepedia_adysunzee_yttransparent.png` — Ady Sun'Zee, close-up, **purple**
  skin with deep-violet chevron/diamond markings, green eyes. **The best view of
  the marking geometry**; stylised linework, so read the shapes not the rendering.
- `wookieepedia_mirialan_luminara_swm41.png` — Luminara Unduli plus a second
  Mirialan, painted, **golden-yellow** skin with near-black chin and forehead
  diamonds. Third hue, third medium, same marking vocabulary — which is what makes
  the vocabulary canonical rather than one artist's habit.
- `donor_current_sprite.png` — the repo's own greyscale `RSW_MirialanHead` mask.
  Kept as a **positive** reference: it already carries canonically-placed
  forehead, inter-brow and chin-lattice diamond markings. Its limitation is that
  the pattern is fixed for all Mirialans where canon makes it individual.

## ruling

(empty — owner has not reviewed this race yet)
