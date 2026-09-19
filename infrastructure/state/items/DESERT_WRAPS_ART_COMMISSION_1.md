# DESERT_WRAPS_ART_COMMISSION_1

## Spec
Owner (2026-09-09, verbatim on the event): commission art INSPIRED BY the
Sand People mod's two genuinely-new asset families, then he unsubscribes:
1. Desert wrap apparel with FULL body-type coverage (Fat/Female/Hulk/
   Male/Thin × 3 directions) — the production value our absorbed Tusken
   set lacks.
2. A "devolved" head shape (custom HeadTypeDef geometry).

🔴 LEGAL LINE: original art only. Written design-capture (already taken
while subscribed) + OUR OWN absorbed Sovereign-Tusken art as style
anchor. Never their PNGs as image inputs — no derivatives.

Process (owner-design-loop): CANDIDATES first — 3-4 wrap style options +
2 head-shape options, south-facing, contact sheet to the owner; his pick
then fans out to the full body-type × direction matrix via
generating-rimworld-sprites.

## Placement plan (the "where in our races" the owner asked for)
- Wrap apparel ThingDef + textures → src/RimStarWars/Armoury (the
  weapons/apparel cell; sits beside the absorbed GS_SandP_Hood set,
  RSW_ prefix, own defNames — not tied to the donor-gated KotOR hold).
- Devolved HeadTypeDef (+ gene if gated) → src/RimStarWars/StarWarsRaces
  (headtypes live with races — the SovSith precedent), offered to the
  RSW_RimMandrakeTusken xenotype.
- Campaign wiring (RUT_Jawa_DeepDesert_* pawnkinds wear the wraps; head
  frequency on the tribe) → src/RimUtinni/UtinniPatches, per the
  engine/content doctrine.

## Candidates (2026-09-09, FOUNDRY)
Contact sheet: `Transient/DESERT_WRAPS_ART_COMMISSION_1_candidates_2026-09-09.png`
(4 wrap styles + 2 head shapes, south-facing, labeled). Source PNGs (real
alpha, generated via `codex_image.py generate` per the `generating-rimworld-sprites`
skill — Codex now returns native alpha on this install, no chroma-key needed)
sit beside it at `Transient/desert_wraps_candidates/*.png`.

Style inputs used: this item's own `design/Jawa/desert_wraps_design_capture.md`
(prose-only capture, no donor pixels) plus our own absorbed
`src/RimStarWars/Armoury/Textures/SWApparel/Sovereign_Tuskens/{Wraps,SandHead_south}.png`
as style anchor — described in prompts, never passed as image input to avoid
any derivative-of-our-own-derivative ambiguity, and the donor mod's own PNGs
were never opened. All 6 candidates are original generated art.

- Wrap A "Spiral Wrap" — grayscale/neutral, Stuff-dyeable, thick outline +
  converging spiral seam bands (closest to the Rimwars mod's own grammar per
  the capture doc, redrawn from scratch).
- Wrap B "Banded Wrap" — overlapping horizontal cloth bands, warm tan, uneven
  hem.
- Wrap C "Segmented Raider" — armored/segmented plates over a wrap base, more
  rugged register.
- Wrap D "Draped Shawl" — loose flowing drape, cream, softer trader read.
- Head 1 "Blunt Bucket Head" — flat squared crown, cylindrical taper, heavy
  jaw-shadow mass, blank dot eyes (closest to the capture doc's measured
  geometry delta from vanilla).
- Head 2 "Elongated Ridged Skull" — domed elongated crown with brow ridges;
  a genuinely different "devolved" direction, not a minor tweak of Head 1.

**The pick LANDED 2026-09-10** (ledger 05:57:04Z / 05:59:13Z): *"ALL FOUR
wrap styles ship... 'stunning, we need all of them'"* and BOTH head shapes
ship — 4 wraps + 2 option heads, full body-type × direction matrix
**buildable now**. This line said "do not build, awaits the pick" for 8 days
after the pick; unblocked at the 2026-09-18 decay sweep.

## Matrix state (wave 3, 2026-09-19)
**49 of 66** texture files placed. **Spiral, Banded, Segmented are 15/15**
(Male/Female/Fat/Hulk/Thin × south/north/east). **Draped is 2/15, HeadPot 1/3,
HeadRidged 1/3**. Wave 3 generated NOTHING: the Codex imagegen quota wall was
still up, and its reset is **22:52 local (PDT)**, not the "10:52 PM" that wave 2
recorded as already past — 10:52 PM *is* 22:52. Probe cost one call.

Resume with `DW_WORKERS=4 python3
src/RimStarWars/Armoury/_artsrc/desert_wraps_candidates_2026-09-09/work/gen_matrix_parallel.py`
then `process_matrix.py` in the same folder; both skip what already exists, so
they resume with no argument list. The 17 owed cells are the 13 remaining
`wrap_D_weathered__*` (Male_east; Female/Fat/Hulk/Thin × south/north/east) and
the 4 `head_H{1,2}_*__{north,east}`.

Look at it: `/mnt/d/Luke/dev/Rimworld/Transient/DESERT_WRAPS_matrix_wave2_2026-09-18.png`

### 🔴 `bodytype_refs/*.png` are NOT valid `validate_sprite` references
They are synthetic solid rounded rectangles (`make_bodytype_refs.py`) serving as
a scale/position *target* for `conform_sprite`, which fits art to them while
preserving the art's own aspect. Run `validate_sprite --reference
bodytype_refs/<BodyType>.png --candidate <cell>` and **43 of 49 cells REJECT** on
span/aspect/origin — an instrument artifact, not a defect. ⛔ Do not act on that
number. The control that settles it: our own **shipped** donor wrap
`Textures/SWApparel/Sovereign_Tuskens/Wraps.png` REJECTs against the same box
with 6 blocking problems (+50% on *both* axes). Wave 2's own `process_matrix.py`
never did a reference-vs-candidate run either — it passes `--reference <final>
--describe`, i.e. the file against itself, which is a tautology, so "placed and
validated" in the wave-2 line was never a span check.

**What IS checkable offline, and the measured result over all 49 cells
(2026-09-19):** canvas 512×512 → 0 bad · alpha-1–31 fringe reaching >2% of canvas
beyond the silhouette → **0** · non-achromatic (maxsat ≥ 0.02) → **0** · unclean
corners → 0 · duplicate pixel-hashes → **0** (the only 4 dup groups are the
deliberate bare-path `Wraps.png` = `Wraps_Male_south.png` inventory graphic) ·
every cell fills ≥90% of its body box on at least one axis. Remaining: 6 cells
overrun their body box by **2–4 px** (all the wave-1 `*_Male_south` masters plus
the two head souths, which came through a different path) — sub-1% of a 512
canvas, inside the box's own corner radius, not worth re-churning.

**Pipeline fix landed this wave:** `process_matrix.py` now snaps alpha < 32 to 0
**after** `conform_sprite`, not only before it. The downscale averages thin wisps
of real art against transparency into alpha 1–31 — invisible on screen, but 112–131
such pixels pushed `Banded/Wraps_Male_east` and `Spiral/Wraps_Female_east` ~50 px
past their silhouette, inflating the bbox by 3.0% and 6.8% of canvas. Both were
REJECT-grade on that reference-independent check and are now clean. Flooring
before conform cannot catch these, because conform is what creates them.

### Placement and wiring: DONE (committed 69d611682), no bridge needed
- Apparel ThingDefs — `src/RimStarWars/Armoury/Defs/ThingDefs/RSW_DesertWraps.xml`:
  4 × `RSW_DesertWrap_{Spiral,Banded,Segmented,Draped}`, no `colorGenerator` so
  Stuff-colour tints them, `wornGraphicPath` per style (RimWorld appends
  `_<BodyType>_<facing>`), tag `RUT_DesertWrap`.
- HeadTypeDefs + genes — `src/RimStarWars/StarWarsRaces/Defs/HeadTypeDefs/DesertWraps_DevolvedNomadHeads.xml`:
  6 HeadTypeDefs (Male/Female × Pot/Ridged, plus 2 abstract bases) and 2 GeneDefs,
  deliberately **unwired** per the owner's "don't change our aliens xenotypes yet".
- Tribe wiring — `src/RimUtinni/UtinniPatches/Patches/DesertWrapsApparelWiring.xml`:
  `PatchOperationAdd` of `RUT_DesertWrap` onto the four `RUT_Jawa_DeepDesert_*`
  pawnkinds' `apparelTags`.

Still owed: (a) the 17 generation cells above, once quota resets; (b) the live
in-game visual check — a DeepDesert pawn wearing each wrap, as a savegame review
— which **needs the bridge and was not this wave's to do**.

## Verify
Candidates sheet reviewed by owner; picked styles produce the full
matrix passing validate_sprite; defs load on minimal list; DeepDesert
pawnkinds spawn wearing wraps in a quicktest.

## Criteria
Owner-picked art shipped at the three placements above; no asset
traceable to the unsubscribed mod's files.
