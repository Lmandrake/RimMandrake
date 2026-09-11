# Map generator round 4 — the chooser, as OPTIONS (Fable design pass, not ruled)

Item: `infrastructure/state/items/MACRO_GENERATOR_V0_1.md`. Round 3's comparator
sheet graded **FAIL, 0 of 8 premises readable** (verdict landed in
`MAPGEN_ROUND3_VERDICT_LANDING_1`, 2026-09-10). The verdict's own criterion for
this item: *its next round is designed against the three defects, not against
corpus stats.* This is that design — three candidate directions, each carried
to a full 8-premise set, drawn as silhouettes on one sheet so the owner can
grade the IDEAS with the painter taken out of the picture.

**Nothing here is built, rendered through `mapgen_paint.py`, or emitted to GL.**
Painter round 4 stays held per the verdict; `MAPGEN_GL_SHEET_1` stays the lead.
The parent spec this amends: `map_generator_chooser_spec.md` (rules 1-11).

## What to LOOK at

`design/RimMandrake/map_generator_round4_options/sheet.png` — three rows of
eight 250² premise silhouettes (sand plain / rock / floor / one hydrology
mark / one white anchor ring), captioned with the premise sentence. Drawn by
`premise_silhouettes.py` from `premises.json` in the same folder; the JSON is
the source of every shape parameter, this doc is the argument.

| row | what it is | what a grade on it settles |
|---|---|---|
| **A** | the eight round-3 plans (seeds 1-8, their landform/orientation/footprint/anchor copied into `premises.json`) drawn literally as shape — same orientations, same anchor cells | the control. If A reads here and not on the painted sheet, the painter is the gap; if A does not read even as shape, the chooser is |
| **B** | a chooser whose unit of choice is a **shape class**, not a landform id; eight classes, no two maps alike | whether topology-as-the-premise is what makes an idea visible |
| **C** | the five arid corpus maps' premises transposed into deep-desert vocabulary, plus three from the wider study list | the ceiling: if hand-authored premises don't read as silhouettes, no chooser will |

**First grading question, unchanged from the item:** *can you see the one idea
at thumbnail size?* Second: *which row's ideas can you see?* Third, only for
row A: *do you see the difference between A1/A3/A4/A8, and between A5/A6?*

## What the silhouettes already say (my read; his overrides)

Row A, before any painter touches it: four canyons are one diagonal within
20°, two sinkholes are one pit, and the anchors sit **off the feature** — A1's
"head" is a ring in open sand beside a channel that has no head (it runs edge
to edge), A2's "lee foot" is inside the rock, A4's "head" hugs the top border.
So defect 3 (interchangeable canyons) and half of defect 2 (a premise that
names a place the map does not have) are **chooser defects**, visible with no
painting at all. That is consistent with the verdict's sequencing (settle
painter-vs-content with the GL sheet) but adds: whatever the GL sheet says
about rendering, the chooser has its own round owed.

## The three defects, and what each option does about them

| defect (verdict) | A: as-is | B: shape classes | C: corpus transposed |
|---|---|---|---|
| 1 gestalt vs corpus — in-band on stats, reads as nothing | — | quiet-field + bulk gates (§R1, §R2) | corpus SCALE (C5's gulch is 0.40 of the map, above rule 10's Canyon cap) |
| 2 choke-point premises invisible | — | "only way through" is legal only on shapes that HAVE a through (§R3) | the door is drawn where the eye lands: the gap, the ford, the dam |
| 3 canyons interchangeable | — | sample (landform × shape) without replacement; grain moves to meso (§R4) | each map is a different archetype by construction |

## Option B in full — the topology-shape chooser

**The unit of choice becomes a shape class.** A landform id says what GL draws;
a shape class says what the eye finds. Eight classes fit the deep desert's
surviving vocabulary (Canyon, Sinkhole, Rift, LoneMountain, DesertPlateau,
Crater, Caldera — after `deep_desert.md` §6 bans remove Cirque, SecludedValley,
Gorge, Oasis and the coast group):

| class | landform(s) | the eye should find | anchor positions | "only way through" legal? |
|---|---|---|---|---|
| CHANNEL-THROUGH | Canyon | one dark band edge to edge, a pale floor thread inside, one knot where the walls bulge in | `narrows` | yes — at the narrows |
| CHANNEL-BOX | Canyon | a band that enters from one edge and STOPS, rounded head | `head` | no — it is a dead end; the premise is shelter, not passage |
| STEP | DesertPlateau | half the map one tone, half another, one cliff line between | `cliff_foot`, `rim` | no — the premise is above/below |
| BARRIER | DesertPlateau | a dark wall edge to edge with ONE pale gap | `breach` (new position, §open calls) | yes — at the breach |
| PIT | Sinkhole | one dark disc in an empty field | `pit_floor`, `lip` | no — you go down, not through |
| RING-BREACH | Crater, Caldera | a dark ring, floor inside, one gap in the rim | `rim_breach`, `ring_centre` | yes — at the breach |
| ISLAND | LoneMountain | one small dark mass, nothing else | `lee_foot`, `flank_shelf` | no |
| TRENCH | Rift | two thin scarps, wide floor between | `shoulder`, `floor_centre` | no |

Rules added to the chooser spec (numbered on from rule 11):

- **R1 Quiet field.** Every deletion the plan writes is already the promise
  ("any relief outside the canyon walls" is in all eight round-3 plans); round
  3 broke it — the painter's plain is rock/gravel blobs at the landform's own
  contrast, which is why the landform vanishes. Make it a GATE like
  connectivity: the fraction of non-plain terrain outside the landform's
  footprint mask ≤ a threshold, computed offline on the grid, refusing the
  render. Threshold: **UNMEASURED** — take it from the five arid corpus grids
  (Blood Gulch and Deserted Trader will set it), never from a generated map.
- **R2 Bulk.** The feature's minimum cross-section ≥ 0.08 of the map edge
  (20 cells at 250²); a linear feature below that is a fence rail (rule 5.5
  #7). Rule 10's footprint ranges stay, but the Canyon cap (0.30) is an open
  call — see C5.
- **R3 Premise follows shape.** The premise template is drawn from the shape
  class row, never from a free list; "only way through" exists only where the
  row says yes. A3/A4/A6/A7's sentences ("the only way through is at the
  head/lip/ring centre") become unwritable.
- **R4 Distinctness by construction.** The 8-seed batch samples
  (landform, shape class) pairs without replacement, then seeds the rest.
  Orientation of a linear feature is free over 360°; rule 11's wind grain
  binds the **meso** yardang texture (`scatter.py`), not the macro landform —
  the sheet's "every shape points the same way" is about yardangs, and a
  canyon is not a yardang. This reverses rule 11 as written: open call.
- **R5 Anchor on the silhouette.** The anchor cell is resolved on the drawn
  feature (the knot, the head cap, the gap, the ring centre), never by the
  edge-distance rule alone — `_anchor_cell_frac` is why A1/A2/A4 are off-feature.

## Option C in full — the corpus transposed

Each of the five arid corpus premises the chooser spec §C already wrote,
re-spoken in deep-desert nouns and drawn at the corpus's own scale, plus three
archetypes from the study-first list. This is the **ceiling test**, not a
chooser: if these do not read as silhouettes, the problem is not choosing.

| # | corpus | transposed premise | what it needs that the sheet/spec lacks |
|---|---|---|---|
| C1 | In Memory of Rain | a dead river braids in from the north and dies in the salt basin it once filled | `deep_desert.md` field 8 names no salt pan or dead river, so rule 2 gives DryLake weight 0; the sheet's §4 flood-bloom and §7 mineral salts imply both. An **amendment** (allowed under the freeze — adds detail, changes no ruling) |
| C2 | Deserted Trader | one rock stands in a wide gap, and the halt in its shade is empty | "no roads" (§8) — a halt, not a waystation on a road |
| C3 | Lush River | every green thing on the map hugs one brine line down the canyon floor | hydrology as a LINE, not a stamp; the green line IS the visible idea |
| C4 | Point Sea | a tongue of plateau pushes into the sand; the only shelter is the cove in its lee | a PENINSULA shape for DesertPlateau (rock into sand, where the corpus had land into water) |
| C5 | Blood Gulch | one red gulch corner to corner; the only way across is the narrows | footprint 0.40 — above rule 10's Canyon range |
| C6 | Ruined Dam | a rockfall dammed the canyon; the dry reservoir behind it is a salt pan | history as terrain: the dam is a narrows that closes, the reservoir a salt pan with a cause |
| C7 | Dragons Fall | something fell out of the west and the ring it made is the only shade; the debris ray points home | a DIRECTIONAL feature (the ray) — the first premise with a heading a player can read |
| C8 | the Dead City | the whole map is the floor of one sinkhole; the plain is a rim you only see from below | footprint 0.55 — the map inside the feature, not the feature inside the map |

## Open calls for the owner

1. **Which row's ideas can you see?** Keep/cut per tile on the sheet, as the
   item's PROVE line asks — this is the grade that decides round 4's shape.
2. **Rule 11 (wind grain).** Grain on the macro landform (as written: all
   canyons within 30°) or grain on the meso yardang texture only (R4)? The
   frozen sheet's §9 line is satisfied either way; the difference is whether
   four canyon maps are allowed to point four ways.
3. **Rule 10 scale.** Blood Gulch's gulch is ~0.4 of its map; the spec caps
   Canyon at 0.30. Raise the cap toward the corpus, or keep the corpus as an
   outlier?
4. **`deep_desert.md` field 8 amendment** to name salt pans and dead
   riverbeds, so DryLake can survive rule 2 on this sheet (C1, C6). Without it
   the deep desert has no basin premise at all.
5. **New anchor position `breach` for DesertPlateau** (B4); rule 3's table
   has `rim` and `cliff_foot` only.
6. **Whether a silhouette row becomes a standing part of every comparator
   sheet** — the sheet showing the plan as pure shape beside its render. It
   costs seconds and is the only instrument that separates the chooser from
   the painter without a game load.
7. **R1's threshold** is unmeasured. Measuring it is a small FOUNDRY task on
   the five corpus grids; it should not be guessed here.

## Not in this pass

The painter (held), the GL emitter's mapping of shape classes onto GL knobs
(`MAPGEN_GL_SHEET_1` owns the GL side; a shape class maps to one shipped graph
plus 2-3 knobs, same as `landform_params` does today), structures, residents,
dressing, micro texture, the LLM plan author. `corpus_stats.py` is untouched
and stays a regression instrument, never the bar.
