## spec

Design Version: FlowWorks 0.2.0 (next, Divergent or Polish; moves no 0.1.0 bar). Filed by the FlowWorks ticket sweep of 2026-11-22
(RIMMANDRAKE_SWEEP_FLOWWORKS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE), which merged these older tickets into this one, one
cause or one file group. Each old ticket's prose is in `infrastructure/state/items/closed/<ID>.md` and its history in
`rimflow show <ID>`; read the one you work on to its end before you build.

FlowWorks 0.2.0: build wetting as the thin film (two squares damp beside a canal, the wetness probe, the downhill garden spill), after the one-state design.

## merged tickets

- `FLOWWORKS_WETTING_BUILD_TWO_SQUARES_DAMP` (proposed): FlowWorks: ground within two squares of a filled canal is wetted by Stillsand's spilled-water technique; plants use it up and drink flood water down (concept leaves canal_wets_two_squares, wetting_is_not_flood; scene sc_wetting)
  - sweep reading: wetting moved to 0.2.0 by his card OWNER:1794721673433243094 (next_version/README.md); item re-targeted
  - its check: two squares beside water read damp in 0.2.0
- `FLOWWORKS_WETPROBE_BUILD_READ_THE_DAMP_FIRST` (proposed): FlowWorks: bridge read of per-cell wetting level, cause and per-plant water drawn; refuses when wetting is off (concept instrument leaf wetness_probe; orders before FLOWWORKS_WETTING_BUILD_TWO_SQUARES_DAMP)
  - sweep reading: re-targeted to FlowWorks 0.2.0 with the wetting bars by his card 2026-11-14 'Move wetting to 0.2.0'
- `CANAL_SPILL_WIRE_GARDEN_GROWS_DOWNHILL` (proposed): Canal overflow (built 3cf4fdf12f, CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED) does not yet feed Explosive Growth or leave wet ground: (1) wire the sheet's Soaked dL into ExplosiveGrowthAPI.SoakCells (spec canal_overflow_flooding_2026-10-21.md lines ~182/321; CanyonFlood and SoakZone already call it); (2) leave visible wet ground where a sheet soaked or dried, fading over time (not a per-cell disc lattice: see WETSAND_STAIN_FIX_READS_AS_POLKA_DOTS); (3) a demo savegame for the owner: one map, an overfilled canal spilling downhill across bare ground, crops and wild plants, so he watches it run, soak, and the growth burst after; this is also that item's H1 L4 look. Not urgent: 'at some point'.
  - sweep reading: Explosive Growth soak + wet ground from the sheet is wetting; wetting moved to 0.2.0 by his card 2026-11-14
  - files: `src/RimMandrake/FlowWorks/Source/Sheet`

## his words (as recorded on the merged tickets)

- on `FLOWWORKS_WETTING_BUILD_TWO_SQUARES_DAMP`: Move wetting to 0.2.0
- on `FLOWWORKS_WETPROBE_BUILD_READ_THE_DAMP_FIRST`: "Move wetting to 0.2.0" (card 2026-11-14)
- on `CANAL_SPILL_WIRE_GARDEN_GROWS_DOWNHILL`: owner note 2026-11-04: wet ground is shared with Stillsand's spilled-water technique; card 2026-11-14 "Move wetting to 0.2.0"

## verify

Acceptance test: none as one command, 0.2.0 work: the 0.2.0 Designer pass rewrites the wetting tests to the thin film first (version/next_version/README.md).

## criteria

- Each merged ticket above is fixed with its check passing (red first where it is a fix), or dropped with its evidence.
- No locked 0.1.0 bar is loosened or edited by this work.

## refs

item: FLOWWORKS_WETTING_BUILD_TWO_SQUARES_DAMP
item: FLOWWORKS_WETPROBE_BUILD_READ_THE_DAMP_FIRST
item: CANAL_SPILL_WIRE_GARDEN_GROWS_DOWNHILL
