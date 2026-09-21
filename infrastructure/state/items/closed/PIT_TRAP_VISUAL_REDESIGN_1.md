# PIT_TRAP_VISUAL_REDESIGN_1 — four-depth legibility, after the FlowWorks merge

**Re-scoped 2026-09-16.** This was a design sitting to decide what a pit looks
like in the covered, sprung and occupied states. Two of the owner's own rulings
that day changed what is left of it:

- **The specification half is DELIVERED.** The Pits validation walk's `## must
  show` list is VALIDATED and binds at hash
  `145a6b5d90729cb4647c73762c1685886164f5ef612d2495fdc6338755402991` — twelve
  lines covering covered (`pit_covered_invisible`,
  `pit_covered_seam_at_max_zoom`), sprung (`pit_reads_as_hole`,
  `pit_not_vanilla_trap`), occupied (`pit_occupant_below_floor`,
  `pit_occupied_distinguishable`, `pitcell_occupant_visible`), footprint
  (`pit_reads_at_size`), the dig site (`digsite_stage_legible`), fittings
  (`fitting_reads_distinct`), the gate (`pitcell_gate_state_legible`), and the
  cannot-show (`never_snared_standing`). Those are the acceptance bar. They do
  not need re-deciding, and they survive the merge.
- **The art half is PARKED behind the merge**, by ruling 27 (owner, 2026-09-16):
  *"Merge first, then fix the pit inside FlowWorks. Consolidation precedes the
  pit's art pass, so sprites are drawn once, against final def names and knowing
  they must read at four depths."*

## The design spec already exists and awaits his ruling

`design/RimMandrake/pit_trap_visual_interface_spec.md` (2026-09-14) is written:
the five states, the top-down depth grammar borrowed from Anomaly's PitGate
(near-black mouth, one lit inner-wall strip, disturbed-earth spoil rim,
`FloorEmplacement` altitude), a Pyrelands-tuned warm palette, the 2x2 stance,
and **three directions as cards** — A Painted Hole, **B Layered Well
(recommended)**, C Marked Ground — each with its sprite count and its trade
stated. It is a ruling away from being actionable, not a blank sitting.

⚠️ It predates ruling 19 by two days, so it fakes ONE depth, not four.

**Inference, not a measurement — from the spec's own sprite counts:** ruling 19
does not void that recommendation, it sharpens it. Direction A pays for depth by
multiplication (6 variant composites × 4 depths ≈ 24 full repaints, since the
depth read is painted into each composite). Direction B does not: the expensive
rim planes are shared and only the mouth-wall gradient varies, so four depths
costs roughly four gradient rings on top of the existing ~10-11. If depth must be
legible, B gets cheaper relative to A, not more expensive. Worth putting to him
that way when he rules.

## spec

One question is left, and nothing else owns it: **how do four depths read on
screen?**

Ruling 19 (owner, 2026-09-16) set the ladder at **shallow, mid, deep,
SUPERDEEP**, with SUPERDEEP as the trapping level and natural sources treated as
SUPERDEEP. The must-show list predates that ruling and asserts only footprint
(`pit_reads_at_size`) — it says nothing about depth. So:

1. Can a player tell shallow from mid from deep from SUPERDEEP at play zoom,
   top-down, with no tooltip and no click?
2. LAW 2 forbids the obvious answer. Depth *never* affects sight or shooting, so
   there is no elevation model, no height offset, no perspective — depth is
   purely a visual property of a flat cell carrying an integer. Whatever reads as
   "deeper" has to do it inside that constraint.
3. Liquid crosses it. Terraces may be filled to varying depths, and rain fills
   unroofed excavations (ruling 25) — so a cell must communicate depth AND fill
   at once, and a covered pit full of liquid is a live visual contradiction that
   ruling 25 explicitly reopened.
4. Does the four-depth read need its own must-show lines added to the walk? If
   yes, they go through the same validation gate — an agent may draft, only the
   owner promotes.

Follow the owner's design loop for this class of call: offline PNG mockup options
first, he picks, then a palette pass. Never a single in-engine guess.

## verify

```
PROVE   the owner has seen mockup options for the four-depth read and picked a
        direction — a rendered set at play zoom, not a description
EXPECT  a direction plus either new must-show lines drafted for his promotion, or
        his explicit word that footprint legibility alone is enough
LIES    any mockup that earns its depth read from height, perspective, shadow
        cast upward, or anything else that is an elevation model in disguise —
        LAW 1 and LAW 2 are the things being guarded here
```

## criteria

The owner has picked a four-depth visual direction and the walk either carries
his promoted must-show lines for it or records his word that it needs none.

## not chasing

- Drawing the sprites. Ruling 27 puts that inside FlowWorks, after the merge,
  against final def names.
- Re-deciding covered / sprung / occupied / footprint. Validated and hash-bound;
  reopening them is rework.

## Watch out

- **Every def path and line number in this item's earlier body is going stale by
  design.** The merge renames these defs, which is the whole reason ruling 27
  sequences art after it. Re-measure against FlowWorks' defs before citing
  anything; do not carry a `RM_OpenPit_*` name forward on faith.
- Two engine-side gaps were MEASURED 2026-09-13 and are real regardless of the
  merge: `GraphicData` carries no `<drawSize>` override anywhere, so a def bigger
  than 1x1 draws its texture in one corner of its own footprint; and
  `Building_OpenPit` draws only the FIRST occupant via
  `IThingHolderWithDrawnPawn`, so a multi-capacity pit's second held pawn is
  simulated but never rendered. Both bite any footprint increase immediately.
- The covered state's invisibility is the owner's own ruled design
  (`design/Jawa/covered_pit_traps_spec.md` §3, 2026-08-30), not a defect. The
  defect is the missing tell: that spec asks for "a slight seam/discoloration at
  high zoom for the player's own eye" and the shipped terrain mimic is a
  pixel-perfect copy with no tell at all. `pit_covered_seam_at_max_zoom` is that
  gap, now binding.
- The current placeholder is vanilla's own `TrapSpikeArmed` texture. New art gets
  its own def-local `texPath`; never edit the vanilla file.
