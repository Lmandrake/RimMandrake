# CRACKEDLANDS_MECHANICS_BUILD_1 — the Swale, surveys, fossils-in-the-walls, the giants' behaviors, the soundscape

Ruled at `FLOODEDCANYON_BEDAZZLE_SITTING_1` (2026-09-28, full accept).
Authorities: the 2026-09-28 amendment in `the_cracked_lands.md` +
`floodedcanyon_bedazzle_review_2026-09-28.md` §4 + the cast bible. Separate from
`CRACKEDLANDS_RULED_CONTENT_1` (the defs) so each has its own catcher. The flood
engine, FlowWorks and the explosive-growth engine are BUILT — everything here
leans on existing machinery. `FLOOD_WITNESS_EVENT_1` keeps the witness quest and
the arm-the-flood verb; do not duplicate.

## 1. THE SWALE (the crown ruling — marks 2+3+1)

- `RM_Swale`: FlowWorks canal variant, intentionally graded + perforated —
  while it carries water, adjacent cells (1–2 ring) climb the fertility ladder
  (sand → soil → rich soil, CAPPED, slow, only while fed). Terrain-swap
  machinery is the flood engine's own recede logic.
- Fills free at each flood; feedable from a cistern between floods.
- 🔴 **Tier shape, owner-ruled verbatim shape**: a NORMAL buildable in FlowWorks
  (RM_ tier) — but in the Utinni campaign it is LOCKED until DISCOVERED in this
  biome (an unlock earned here that then travels with the ship — the
  discoverable technology, shaped for transient gravship players). Unlock
  persistence is world-level (WorldComponent flag or hidden research), never
  map-level.

## 2. The survey + cistern loop (transient-player shaped)

- Per-visit payoff, no slow ladder: veqma blush and sleeper clusters are
  immediately readable tells; a prospect action at a read site yields a
  hidden-water SURVEY (sellable, §11's "exceptionally valuable thing") or is
  dug same-visit into a CISTERN — a FlowWorks source that yields slowly and
  refills each flood; crack-wax in the build recipe (the lining, priced into
  construction — no runtime loss model, FlowWorks has none and none is being
  added).

## 3. Fossils in the walls

- GenStep seeding fossil-bearing strata mineables into canyon wall faces,
  biased low/deep; **the flood re-cuts**: on recede, fresh seams roll along the
  wetted wall line (the map component's soaked-cell list exists).
- Yields the content item's fossil family. Every visit digs fresh — the
  gravship rhythm.

## 4. The giants' behaviors

- **Muttavaq**: sleeping = reads as terrain (mounded pan field slightly out of
  pattern; art carries it); wake via the built `CompWaterWakeTrigger` family
  when the flood reaches it; awake = neutral, unstoppable, walking-weir feeding
  with FlowWorks depth edits along its trail (machinery the flood already
  drives); digs in + seals where it stands at the dry. Killing one asleep is
  easy, shameful, rich (crack-wax + meat bonanza).
- **Uttaqar**: crag-walls range, cave-mouth spawns; self-petrifying wounds per
  the donor read, re-voiced. No shared band with the muttavaq.

## 5. The soundscape (mark 7) + the herald sky (mark 8)

- Replace `SoundDefOf.TinyBell`: 3–4 bespoke chime tones staged by
  distance-to-flood (the lead time is already a Mod Settings number — hooks
  exist); wind-in-the-slots ambient; ticking flats as the Sealed wake; tarruq
  calls that STOP a beat before the chimes. Vanilla SFX reuse/retint first.
- **Peakstorm Light** WeatherDef: clear and dry here while the northern skyline
  flickers with the Contagion's storm (sky color + distant strike SFX; ZERO
  precipitation by construction — ban 5); the flood clock biases its chime
  window to follow it. Optional second: wet-clay wind (pre-chime, no
  precipitation).

## 6. Salvage strikes, ledges, toll gate, bloom market (§12 tails)

- Post-recede salvage scatter on the soaked-cell list, fast-decaying; rival
  Jawa crawler-crew VISITOR incident (not a raid) for the same mud.
- Refuge ledges as mapgen/KCSG features (the witness event depends on ledges
  existing); Hutt toll gate site piece (template machinery proven here —
  `MOISTURE_FARM_TEMPLATES_1`).
- Bloom market: post-bloom trade-caravan bias + price factors. Do LAST.

## Watch out

- New .cs needs its `<Compile Include>` line (silent no-compile).
- The Swale's fertility writer must be bounded (cap, rate, only-while-fed) or
  it terraforms the biome out of its own premise.
- 🔴 No pawn dive verb anywhere in this item — the wax suit is the content
  item's, and it is terrain survival only.
- Every mechanic gets its Mod Settings toggle, defaults = shipped behavior.
- Build order: weathers/sound hooks after the rename lands or against current
  names — coordinate with `CRACKEDLANDS_FULL_RENAME_1`.

## verify

- Quicktest: a fed Swale raises adjacent fertility and stops at the cap; the
  Utinni lock holds until the discovery fires, then persists across maps;
  cistern refills at flood; fresh fossil seams after a recede; muttavaq wakes
  when water reaches its pan (state reads, never unattended screenshot hunts);
  chime tones stage with distance; Peakstorm Light precipitates nothing.
