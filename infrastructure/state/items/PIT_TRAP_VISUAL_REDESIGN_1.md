# PIT_TRAP_VISUAL_REDESIGN_1 — design the pit trap's real interface (covered / sprung / occupied)

Owner, live 2026-09-13, after watching a covered-pit-trap capture demoed on a
quicktest: *"Looks like it was working. But we need to think now about very
deeply what it looks like. It can't just be a simple trap graphic you get
stuck on. So we need a big dark pit. File a Bench ticket to thoroughly dream
up the interface for this."* Also asked directly: *"Do we support 2x2
pits?"* and *"And how does it show covering yet?"* — both answered below,
MEASURED against the actual code, not guessed.

## Where this actually stands today (verified, not assumed)

- **Covered/armed state**: intentionally invisible by design (this WAS the
  owner's own idea, `design/Jawa/covered_pit_traps_spec.md` §3, ruled
  2026-08-30) — `Building_OpenPit.Print()` (`Source/Holding/
  Building_OpenPit.cs:93-105`) prints the surrounding TerrainDef's own
  texture over the pit (`TerrainMimicPrinter.PrintTerrainMimic`) while
  `covered == true`. The spec's own text (line 42) calls for "a slight
  seam/discoloration at high zoom for the player's own eye" as a subtle
  tell — the shipped `TerrainMimicPrinter` implementation does not do this;
  it is a pixel-perfect terrain copy with **no tell at all**, a real gap
  between spec intent and what's built.
- **Sprung/uncovered state**: `Spring()` (`Building_OpenPit.cs:230`) sets
  `covered = false`, which falls through to `base.Print()` — the def's own
  static graphic. There is **no distinct sprung texture or animation** —
  before arming, after arming-but-uncovered, and after springing all render
  identically.
- **The actual texture**: every pit-related ThingDef (`RM_OpenPitBase`,
  `Pit_OpenPits.xml:32-35`; `RM_PitCellBase`, `Pit_Cell.xml:58-61`;
  `RM_PitDigSiteBase`, `Pit_DigSites.xml:29-32`) points at
  `Things/Building/Security/TrapSpikeArmed` — **vanilla RimWorld's own
  64x64px spike-trap icon**, reused as an explicitly-flagged placeholder
  (`Pit_OpenPits.xml`'s own header comment: "A real art pass is explicitly
  deferred to the campaign layer per covered_pit_traps_spec.md section 9").
  This is exactly the owner's complaint: it reads as a small vanilla trap
  icon, not "a big dark pit."
- **2x2 support**: the *trap* pits (`RM_OpenPit_Bare/Spiked/Oiled/Poison/
  Water/Oubliette`, all descending from `RM_OpenPitBase`) are hardcoded
  `<size>(1,1)</size>` (`Pit_OpenPits.xml:44`) — no multi-cell trap exists
  today. BUT the *prisoner-cell* variants already ship 2x2:
  `RM_PitDigSite_CellDouble` and `RM_PitCell_Double`
  (`Pit_Cell.xml:36,91`, both `<size>(2,2)</size>`), and every mechanism a
  bigger trap pit would need is ALREADY footprint-generic, not 1x1-hardcoded:
  `Building_OpenPit.MaxOccupants` scales off `def.size.x * def.size.z`
  (`Building_OpenPit.cs:56-64`), `CompPitCoverTrigger.RunScan` sums mass over
  the whole `OccupiedRect()` (`CompPitCoverTrigger.cs:50-72`), and
  `TerrainMimicPrinter` already iterates every occupied cell
  (`Building_TerrainMimicCover.cs:22-32`). A 2x2 (or larger) trap pit def
  could be dropped in today with NO C# changes to occupancy/trigger/
  camouflage. Two real gaps block it from looking right immediately:
  1. `GraphicData` has no `<drawSize>` override anywhere, and `drawSize`
     defaults to `(1,1)` — a 2x2 (or bigger) def would draw its texture in
     only one corner of its own footprint, not fill it.
  2. `Building_OpenPit.cs:29-35`'s own comment: it draws only the FIRST
     occupant via `IThingHolderWithDrawnPawn` — a 2-capacity pit's second
     held pawn is simulated/held but never rendered.

## spec

A design session (BENCH) to dream up the real interface, not a solo art
swap:
1. What should covered/armed actually look like — keep the terrain-mimic
   invisibility (per the owner's own ruled design), add the spec's own
   "subtle seam" tell that was never built, or something else entirely?
2. What should SPRUNG look like — the owner's own words, "a big dark pit,"
   not a reused vanilla trap icon. Needs an actual texture (or a
   procedural/shader dark-hole treatment) sized to actually read as a hole,
   not a 64px icon.
3. Whether pit SIZE should be a design lever (the mechanism already
   supports 2x2 for free per the code path above) — bigger trap-pit
   variants, and if so what the multi-occupant rendering gap (only the
   first held pawn draws) needs to become before that's shippable.
4. How an occupied-but-uncaptured moment (the mid-fall/struggle state,
   `PitEscapeUtility`) should read differently from an empty sprung pit, so
   a player can tell at a glance whether someone's actually down there.
5. Follow the owner's own design loop for this kind of call: offline PNG
   mockup options first, he picks, then a palette pass — not a single
   in-engine guess.

## verify

```
PROVE   the owner has seen mockup options and picked a direction (or asked
        for another iteration) — a rendered set of options, not a
        description of what could be built
EXPECT  a concrete art/implementation plan: what asset(s) are needed, what
        C# (if any) changes (drawSize override, multi-occupant rendering),
        and whether a size upgrade is in scope for v1 or deferred
LIES    a plan that claims "just swap the texture" without addressing the
        drawSize-defaults-to-(1,1) gap on anything bigger than 1x1, or one
        that quietly drops the camouflage mechanic the owner already ruled
```

## criteria

The owner has picked a direction (covered look, sprung look, size stance)
and a build item exists naming what it needs, OR the owner has explicitly
said the current placeholder is fine for now.

## not chasing

Actually implementing the chosen direction — this item is the DESIGN
sitting; a build item follows once the owner picks.

## Watch out

- `TrapSpikeArmed` is VANILLA's own texture — swapping it in-place would
  also change every vanilla spike trap's look unless the new art gets its
  own def-local `texPath`. Give the new graphic its own path; don't edit
  the vanilla file.
- The five other `RM_OpenPit_*` variants (Spiked/Oiled/Poison/Water/
  Oubliette) all inherit `RM_OpenPitBase`'s graphicData — a fitting-specific
  look (spikes visible through the cover, oil sheen, etc.) needs each
  variant's own override, not just the base def.
- `RM_PitCell_Double`/`RM_PitDigSite_CellDouble` already ship as 2x2 with
  their OWN graphicData (not checked in depth here) — confirm whether they
  already handle multi-cell drawSize correctly before assuming the
  drawSize gap applies uniformly; it was confirmed for the base/trap defs,
  not independently re-verified for the existing 2x2 cell defs.
- `Building_OpenPit.cs:29-35`'s single-occupant-draw limitation is a
  pre-existing, documented gap (not introduced by this ticket) — any size
  increase for TRAP pits inherits it immediately.
