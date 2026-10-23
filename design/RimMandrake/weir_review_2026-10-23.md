# Weir review — 2026-10-23

Items: `WEIR_LOOK_REDESIGN_WHITEWATER_FROZEN_SOLID`, `WEIR_CATCH_FIX_NO_FREE_FISH`. Owner, 2026-10-23 (walk):
*"the weir. What the heck? This is horrible. Static white water that doesn't match anything. (needs to be an animated
effect). A single blue tint above it. How does this even work? I think we need a weir review, completely."* and
*"And weirs just generate fish occasionally? No... they should just capture anything floating downstream. No auto fish
capture."*

## How it worked until this review (plain words)

Code: `src/RimMandrake/FlowWorks/Source/Rivers/RM_Weir.cs`; def `RM_BankWeir` in `Defs/Rivers/RM_BankWorks.xml`; looks
in `Defs/Rivers/RM_BankWeirStyles.xml`; art sources `art_source/Weir/`.

- **Placement.** A 1x2 wall with one end in moving water and one on the bank; more sections chain end to end across
  the river into one wall. Nothing checks that the wall crosses the current: one laid along the shore (the second walk
  screenshot) is accepted.
- **Water level: there is none.** The current model (`RM_MapComponent_RiverCurrent`) has no depth or level. The weir's
  "pool" is a set of cells (8 upstream, 3 wide) where the current's lane drops one step, so things drift slower and the
  water is easier to cross. Nothing rises.
- **The teal rectangle** was one fixed texture, `RM_BankWeirWater_<facing>`, a 1x3 cell strip printed centred on the
  weir's wet cell: a flat calm tint on the upstream cell and a frozen white-foam picture on the downstream cell. It was
  not the pool (8x3 cells) and knew nothing about the water: with the current running along the wall it was drawn on
  dry bank (screenshot 2).
- **Fish and "drift" from nowhere.** Every 6 game hours the run's head rolled 80 % x fish stock for 2-5 fish from the
  river's water body (charged to the fishing stock), and a one-in-four roll for one biome "drift" item (`RM_RiverDriftDef`: logs,
  reeds…), both created out of thin air on the bank end. That is the "auto fish" he saw.
- **What really floats.** The surface current already carries loose items and corpses (and swept pawns) downstream
  cell by cell. A weir cell is not standable, so anything carried into the wall stops in the cell just upstream of it
  — and simply sat there.
- Breach, wear, stake cascade, silt-traps and the four looks (Scrapper/Industrial/Modern/Futuristic) are unchanged
  by this review. The 2026-10-17 weir looks sheet is a **prefill** (no human ruled on it); its picks are all `A` =
  what is installed, so keeping the installed looks keeps them.

## What a weir should do

1. **Catch only what the river brings.** Each holding section watches its *intake*: the in-current cells whose flow
   step lands on the wall (exactly where the carry stops a thing). A loose item or corpse lying there is lifted onto
   the bank end of the run's head, as the catch pile, up to the held-catch cap; past the cap it stays jammed against
   the wall. Pawns (living) are never moved. The catch is placed on ground with no current, so it never drifts off
   again. Nothing is ever created: no fish, no drift. (`RM_RiverDriftDef` rows stay as data, unused, for the open
   question below.)
2. **Calms the water upstream** — unchanged mechanically (the slack-current pool). **No tint**: the model has no
   raised level to draw, and a flat rectangle lied about it. The pool shows through its effect (slow drift, easy
   crossing) and the inspect line.
3. **White water, animated, only where water really falls.** A 12-frame looping flip-book of tumbling foam on the
   downstream cell of each wet section, drawn in real time (`drawerType MapMeshAndRealTime`, frame from real time, so
   it moves like vanilla river water, also while paused), rotated so the crest is on the wall and the foam runs
   downstream. Drawn only when the current crosses the wall and the downstream cell is water; a wall the current runs
   along gets none. **Scaled to flow:** margin lane = light, slower foam; centre lane = full; flood surge = brighter,
   faster, reaching further downstream. Foam is a translucent off-white so the map's own water colour shows through
   (every water colour on the planet). Frames are procedural (`art_source/Weir/whitewater_frames.py`), seamless in
   time, one set for all four looks (water is look-free); the per-look crest sheet (`RM_BankWeirSpill_*`) is kept.

## Mod settings (WORKS section)

| setting | default | replaces |
|---|---|---|
| Weirs catch what floats into them | on | "Weirs catch fish", "Weirs catch drift", catch interval, drift chance (removed) |
| Weir holds at most N items | 30 | unchanged |
| Animated white water below weirs | on (off = no foam drawn) | the static texture |
| Weir calms N squares upstream | 8 | unchanged |

All-off degrades gracefully: the wall still arrests the current and things pile against it.

## Open questions for the owner

- **Biome drift:** should rivers carry biome-relevant flotsam *onto* the map now and then (entering at the upstream
  edge, floating down, catchable by a weir or anyone)? That would revive card 2's drift as real floating things.
- **Placement:** refuse a weir laid along the current (it dams nothing)?
- **Fish:** a weir as a fish *trap* would be a separate building with an explicit trap rule — not built.
