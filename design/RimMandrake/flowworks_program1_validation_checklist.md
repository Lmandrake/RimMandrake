# FlowWorks program 1 — grouped validation checklist (excavation+liquids merge)

Status: **DRAFT — agent-drafted, not owner-validated.** Per `design/RimMandrake/
north_star_validation_spec.md`, a DRAFT checklist cannot fail or green a mod;
this file exists to satisfy §20's caution in `flowworks_mod_definition.md`
("the validation unit grows... His accepted mitigation — grouping every line
under its mechanic — still holds") before the real `## north star` sections in
`design/validation_walks/RimMandrake/Pits.md` and `FlowWorks.md` are merged
into one walk under whatever the rename lands as. It does not replace either
walk file, and does not itself bind anything — promotion into a real `##
north star` section still needs his validation per that spec's §1/§6.

**Why this file exists separately rather than editing the walk files in
place**: the merge (ruling 18) hasn't landed in code or in the walk-file
structure yet — `Pits.md` and `FlowWorks.md` are still two files for two
mods, and FOUNDRY_BOOKKEEPING lane doesn't own rewriting either walk's live
`## north star` DRAFT section mid-build. This is the union, read for planning
`FLOWWORKS_BUILD_PROGRAM_1`'s verify pass and for whoever merges the walks.

**Provenance of every line below**: `pit_*` and `pitcell_*`/`fitting_*`/
`digsite_*` lines are copied verbatim from `design/validation_walks/RimMandrake/
Pits.md`'s existing DRAFT `## north star`. `canal_*`/`source_*`/`slime_*`/
`irrigated_*` lines are copied verbatim from `FlowWorks.md`'s. No new
must-show claim is invented here — only grouping and a program tag are added,
per the north-star spec's own rule that "an agent distils... and adds no new
claims."

## Group: Excavation primitive (depth D, fill F) — Lane A

- [ ] `digsite_stage_legible` (Pits) — an unfinished dig site reads as
      excavation in progress; stage is apparent without selecting it.
      **PROGRAM 1** — the dig-to-depth designator is Lane A's.
- [ ] `canal_reads_as_dug_channel` (FlowWorks) — a dug channel reads as
      excavated ground with walls, not a path or a floor.
      **PROGRAM 1** — Lane D art candidate, no adoptable precedent (spec §13).
- [ ] `canal_dry_reads_as_obstacle` (FlowWorks) — an unfilled channel is
      legible as an obstacle to crossing, no tooltip needed.
      **PROGRAM 1** — this is the pathCost-30 ladder (ruling 17/18), directly
      covered by the item's `## verify` check 5.

## Group: Pulse engine / fill and overflow — Lane A

- [ ] `canal_partial_fill_distinct` (FlowWorks) — a partly filled canal is
      distinguishable at a glance from a full one.
      **PROGRAM 1** — this is ruling 5's tier ladder, folded into the D/F
      primitive (ruling 18); vanilla's depth-tier ramp art carries it near-free
      (spec §13/§21).
- [ ] `canal_fill_spreads_along_itself` (FlowWorks) — liquid in an
      incompletely filled canal spreads through the channel rather than
      pooling where it entered.
      **PROGRAM 1** — this is the sort-deepest-first-then-overflow algorithm
      (ruling 19), covered by the item's `## verify` checks 2-3.
- [ ] `canal_holds_only_the_channel` (FlowWorks) — liquid stays inside the
      dug channel, not on open ground beside it. Expected to FAIL until the
      channel-constraint fix (spec §6) lands.
      **PROGRAM 1** — the single biggest correctness gap named in the spec;
      Lane A owns the channel-aware walk that replaces vanilla `Flood`'s
      unconstrained gating.
- [ ] `canal_reads_as_same_liquid_as_source` (FlowWorks) — a filled canal
      reads as the same substance as the body it came from.
      **PROGRAM 1** — falls out of the unified primitive; no separate mechanism.

## Group: Stock / body model — Lane B

- [ ] `source_strained_state_visible` (FlowWorks) — a drawn-down source is
      visibly strained, distinct from full, at a glance.
      **PROGRAM 1** — Lane D art candidate (no precedent anywhere in repo,
      spec §13); Lane B supplies the state it renders.
- [ ] `source_body_recedes_visibly` (FlowWorks) — the parent body is visibly
      smaller after supplying a canal.
      **PROGRAM 1** — ruling 4's stock model, recession rule in spec §5,
      directly covered by the item's `## verify` check 2 (conservation).

## Group: Defense — fire (fuse/detonation) — deferred

- [ ] `canal_burning_reads_as_burning_liquid` (FlowWorks) — a lit flammable
      canal reads as the liquid surface alight, not ordinary ground fire.
      **DEFERRED to program 2** — fire, per BENCH's lane note.
- [ ] `canal_fire_reaches_source` (FlowWorks) — fire is visibly present at
      the source, not only in the channel.
      **DEFERRED to program 2** — fire.

## Group: Defense — slime / capture — deferred

- [ ] `slime_reads_as_viscous_not_water` (FlowWorks) — slime reads as
      opaque and viscous, never tinted water.
      **DEFERRED to program 2** — capture/ladders/shooting exception per
      BENCH's lane note; slime's viscosity-drives-escape link is ruling 18's
      "F × the liquid's viscosity" row, which is capture machinery.
- [ ] `slime_occupant_below_surface` (FlowWorks) — a pawn caught in a slime
      canal is not drawn standing on the surface.
      **DEFERRED to program 2** — same reason; kin to `pit_occupant_below_
      floor` below.

## Group: The sprung trap / capture (Pits) — deferred

- [ ] `pit_reads_as_hole` (Pits) — a sprung pit reads as a dark hole at play
      zoom, label hidden.
      **DEFERRED to program 2** — capture/art, and ruling 27 explicitly
      sequences the pit's own art pass after the merge.
- [ ] `pit_not_vanilla_trap` (Pits) — does not read as vanilla's spike trap.
      **DEFERRED to program 2** — same, ruling 27.
- [ ] `pit_occupant_below_floor` (Pits) — a captured pawn is not drawn
      standing at floor level.
      **DEFERRED to program 2** — capture; this is Pits' existing mechanic,
      untouched by Lane A/B's engine work.
- [ ] `pit_occupied_distinguishable` (Pits) — occupied and empty sprung pits
      are distinguishable at a glance.
      **DEFERRED to program 2** — capture/art.
- [ ] `pit_reads_at_size` (Pits) — a pit larger than one cell fills its own
      footprint.
      **DEFERRED to program 2** — art, ruling 27.

## Group: Covered / armed state (Pits) — deferred

- [ ] `pit_covered_invisible` (Pits) — a covered pit is invisible at play
      zoom.
      **DEFERRED to program 2** — art, ruling 27; also touches the roofed-pit
      contradiction of ruling 25 (rain-vs-cover), which is not Lane A/B's.
- [ ] `pit_covered_seam_at_max_zoom` (Pits) — carries a seam/discoloration at
      maximum zoom.
      **DEFERRED to program 2** — same.

## Group: Prisoner pit cell (Pits) — deferred

- [ ] `pitcell_gate_state_legible` (Pits) — gate open vs closed is visible on
      the building itself.
      **DEFERRED to program 2** — gates, per BENCH's "gates/sinks/fill-in"
      deferral.
- [ ] `pitcell_occupant_visible` (Pits) — a held prisoner is discernible as
      down in the cell, not standing on it.
      **DEFERRED to program 2** — capture.

## Group: Fittings (Pits) — deferred

- [ ] `fitting_reads_distinct` (Pits) — spiked, oiled, poison and water
      fittings are distinguishable from each other and from bare.
      **DEFERRED to program 2** — ruling 19's consequence that `CompPitFitting`'s
      `Water` fitting becomes a liquid row is explicitly capture/absorption
      work, not Lane A/B.

## Group: Irrigation — deferred, unassigned lane

- [ ] `irrigated_ground_visibly_differs` (FlowWorks) — ground/plants beside
      a filled canal visibly differ from ground away from it.
      **DEFERRED** — not named in Lane A-E of BENCH's note at all. Flag for
      BENCH: either fold into a future lane or confirm it stays out of program
      1 deliberately. The mechanism is cheap (spec §11's `SoakFactorAt` +
      Harmony postfix on `Plant.GrowthRate`, already built in FloodedCanyon)
      but "cheap to build" is not the same claim as "in scope for program 1."

## cannot show (must NOT be true of any program-1 screenshot)

- [ ] `never_liquid_on_open_ground` (FlowWorks) — liquid standing on ground
      the player never dug. **PROGRAM 1** — this is exactly what
      `canal_holds_only_the_channel` above is fixing; the two are the same
      defect stated as a positive and a negative claim.
- [ ] `never_gravel_path` (FlowWorks) — a channel that reads as a gravel
      road. **PROGRAM 1** — Lane D art.
- [ ] `never_full_source_after_heavy_draw` (FlowWorks) — a source that
      looks untouched after filling a long canal. **PROGRAM 1** — Lane B
      conservation, covered by item `## verify` check 2.
- [ ] `never_snared_standing` (Pits) — a pawn snared upright on a labelled
      tile. **DEFERRED to program 2** — capture/art, ruling 27.

## New lines this merge adds (not in either source walk, agent-proposed only)

These are candidates, not must-show lines — they name the two-owners-one-cell
hazards Lane E exists to close and have no precedent line in either walk to
copy from. Promote or reject before validating; they bind nothing here.

- `dig_refuses_onto_pit_cell` — digging a canal designator onto a cell a Pits
  building occupies is refused or produces an explicit, single-owner
  conversion; it must never silently produce a cell both systems think they
  own (spec §19's named hazard). **PROGRAM 1** — Lane E, covered by item
  `## verify` check 4.
- `canyon_flood_does_not_erase_a_dug_canal` — a canyon-flood cycle does not
  `SetTerrain` over a cell the player has dug into a canal
  (`CANYON_FLOOD_ERASES_CANALS_1`). **PROGRAM 1** — Lane E, covered by item
  `## verify` check 4.

## What "program 1 claims" means here

A line marked **PROGRAM 1** is a claim this program intends its `## verify`
checks (see `infrastructure/state/items/FLOWWORKS_BUILD_PROGRAM_1.md`) to
cover by the time the program closes — it is not yet wired to any
`component(..., shows=[...])` call, because no `validation.py` exists yet for
the merged engine (spec ruling 24's own admission: rebuilding the walk/
validator against the new primitive is owed work, not done work). Wiring
`shows=` and validating the checklist with the owner is what turns these rows
from a plan into a bar, per `north_star_validation_spec.md` §§1-6, and is
explicitly NOT program 1's to finish for the deferred groups above.
