# FlowWorks depth: the one big rebuild (PLAN, 2026-10-17)

Epic: `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG`. This is the build plan for everything the owner ruled on 2026-10-17. It
orders the work, estimates it, says what each package needs live, and lists what he must look at. Nothing in code, defs,
the bridge or the game was touched to write it. Code sites are file:line at `9196261f3` (re-grepped for this plan).

**Every agent-day figure here is an ESTIMATE, not a measurement.** An agent-day is one focused coding agent day
including selftests, with no live game time unless the row says so. Sources: `flowworks_level_surface_2026-10-17.md`
(4 to 7 days), `flowworks_elevation_feasibility_2026-10-17.md` (T1 3 to 5, T2 3 to 6), `flowworks_unified_depth_2026-10-17.md`
(Scheme A 2 to 3). Overlaps are removed below, so the total is less than their sum.

## 0. What he ruled (2026-10-17, by question card unless marked)

| # | ruling | ledger |
|---|---|---|
| R1 | Water is **exactly level**: each connected body holds exact decilitres and has one surface height | card, note on `WATER_SURFACE_REPAIR_LEVEL_OR_BUST` |
| R2 | A **new very-shallow water look under 25 cm** (new art; he sees it first) | same |
| R3 | **Redraw scene S5** with level-water numbers | same |
| R4 | **The depth readout**: hole depth and water depth as two figures, water volume in parentheses | owner said, `DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE` |
| R5 | **Default max colonist dig 8 m, a setting from 2 to 20 m.** Lakes keep their own ruled floors (20 m default, to 125 m; 50 m for very large lakes and oceans). The 0.5 m dig step stays | card, on the epic |
| R6 | **Everything in one big rebuild:** exactly-level water, the metres-and-litres rewiring (`LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD`), the very-shallow look, deeper digs (T1) and the relative-depth rules | card, on the epic |
| R7 | **The four rules keyed to "2 m deep" become relative to the height difference:** drowning, fall damage, spikes, shooting | card, on the epic |
| R8 | **Real z-level elevation (T4) is dead**, not deferred: no raised ground, hills, height line of sight, or cells above cells | card, on the epic |
| R9 | A north-star bar: every square of connected still water stands at the same surface height (to within 1 cm), read from game state, not the picture | owner said, `OWNER.jsonl` tsn 1792258162801304562; bar text not yet written into the walk file |

**Reversed by R5:** the morning's D5, *"the deepest pit stays 2 m"* (unified-depth spec §10). He reopened it himself the
same day by asking how deep players should dig. The walls-20%-over-the-head rule stays a visual rule only.

## 1. Work packages, in order

| WP | item | what | ESTIMATE (agent-days) | needs live |
|---|---|---|---|---|
| **P1** | `WATER_SCENES_PROVE_AFTER_THE_CREEP_FIX` | Deploy the `fe309aefe` DLL (game down), rerun S2, S5 and S6 of `northstar/water_scenes_walk.py`, record with modcheck. Proves the dry-front fix that the solver will replace, and gives a baseline | 0.5 | deploy + bridge, ~15 min cold load |
| **P2** | `PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH` | The owed live proofs of the built climb work: pocket grid, cliff masks, ramp, ladder; a raid against a base ringed by a sheer trench; a row proving the per-request mask swap holds under 1.6's multithreaded pathfinding while masks rebuild | 1 to 3 | bridge; minimal list where it can, full list for the raid |
| **P3** | `WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES` | The level-surface solver (level-surface design Option 1): body volume in decilitres, one surface per body from a floor-height histogram, depth = surface − floor on read; bodies split and merge by connectivity **below** the surface; mouth pace kept; ponds first, then canals and joins; a diagnostic that reports the largest surface gap per body in metres; save migration with a logged before/after per body | 4 to 7 | none to build; P9 proves it |
| **P4** | `LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD` | The metres-and-litres rewiring (unified spec §7.2) done **in the same pass** as P3: `RM_Volume` constants, `FillTier` by metres of water, "five" deleted, one burn rate, `sourceBudgetMultiplier` deleted, strings in metres, Python oracle reads C# constants. Fold `LAKE_FLOOR_TUNE_TEN_TO_FIFTY_METRES` in here (same bed code and settings) | 1.5 to 2.5 on top of P3 (the shared files are counted once) | none |
| **P5** | `PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT` | T1 deeper digs: split `Superdeep` (4) from `MaxDigDepth` (setting, default 16 notches = 8 m, range 4 to 40); dig job, designator and workgiver read the grid, not the terrain; "dig to N m" designator; pocket bands and masks sized by the largest climb limit, not the dig cap; wall-face arrays to about 8 notches, saturating; pawn sink by the drop below the near lip; floor tint per depth band past 2 m; rain loop by the cell's own depth. Cap sites listed in the item | 3 to 5 | none to build |
| **P6** | `DIG_COST_TUNE_DEEP_IS_A_MEGAPROJECT` | Keep today's work curve (3,200 × the notch being cut); settings text in metres; lowering the cap never shallows a dug cell. Inside P5's pass | 0.25 | none |
| **P7** | `PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE` | R7's four rules relative (forms in §3), plus pit rooms by person-band pocket without the 2 m clause | 3 to 5 | none to build |
| **P8** | `DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE` | The readout on the solver's numbers: "Hole 7 m (ledge 4 m) · Water 2.37 m (4,740 L)"; floors to 0.5 m, water to two decimals | 0.5 to 1 | bridge, in P9 |
| **P9** | `VERY_SHALLOW_WATER_RESKIN_HE_SEES_FIRST` + `WATER_DEPTH_RESKIN_HE_LOOKS_FIRST` | Art: the under-25 cm look (R2); the wall band on wet canals and deep-lake tints (already filed); the deeper wall faces and floor tints from P5. **One review for him covering all of it** | 1 to 2, plus his look | his look (sheet or in-game shot) |
| **P10** | the epic | Integration: selftests and the Python oracle in lockstep; S5 redrawn with level numbers (R3) and re-sealed; one staged savegame showing S5, S6 and the 4/7/7/4 square; the R9 bar written into `design/validation_walks/RimMandrake/FlowWorks.md` `## north star` for his re-validation; deploy and a full live walk | 1.5 to 3 (about 1 of it live) | deploy + bridge + his look |

**Total (ESTIMATE): about 17 to 33 agent-days, midpoint about 24.** Of that, about 3 to 5 days are live (P1, P2, P10),
and the art waits on his look. A single agent working in order is the safe shape (the same files recur in P3 to P7).

## 2. Dependency order

```
P1 ─┐                 (live, now; independent of code)
P2 ─┼──────────────────────────────┐   (live; gates SHIPPING deeper digs, not coding them)
    │                              │
P3 + P4 (one pass) ──> P5 + P6 ──> P7 ──> P8 ──> P10 (deploy, walk, his look)
                         │                         ^
P9 art ──────────────────┴── (any time; P5 adds wall/floor looks) ─┘
```

- P3 and P4 first: P5's flow side (the `b < 5` band loop and sort keys) disappears once the solver lands.
- P5 before P7: the relative rules need deeper steps to be worth testing.
- P8 needs the solver's surface. P9 can run from day one in parallel; it only needs his look before P10 ships.
- **P2 must pass before a build with deeper digs ships.** Coding P5 does not wait for it.

## 3. Defaults picked (veto-able; the docs' recommendations)

He did not rule these. Each stands until he says otherwise.

| # | question | default | his other option | source |
|---|---|---|---|---|
| V1 | dig cost by depth | **keep the curve**: each half-metre costs more (one 7 m square ≈ 5½ digger-days; his 4/7/7/4 square ≈ 45) | flat cost per notch past 2 m (≈ 27 days for the square) | play Q10, feasibility Q2 |
| V2 | drowning | **when the water covers the head** (over 0.9 H standing; over 0.2 H lying down), unless it can reach water it can climb to | today's "any liquid in a 2 m pit" | play Q3, §2.4 |
| V3 | fall damage | **by metres fallen**: today's damage up to 2 m, +50% a metre past that, capped at 4× at 8 m; blunt damage, never instant death | one fall size at every depth | play Q4, §2.5 |
| V4 | spikes | **any cell with a sheer drop of 2 m or more to a neighbour** (relative, per R7) | any cell at least 2 m deep (absolute) | feasibility T2; play Q5 |
| V5 | shooting from a pit | **blocked only when the shot line crosses ground higher than both ends by more than a person's height** (a cliff edge between them); two pawns on one basin floor fight normally | keep "anyone 2 m down shoots only neighbours" | play Q8, feasibility T2 |
| V6 | pit rooms | **a person-band pocket**, the 2 m clause dropped (a sheer 1.5 m pocket is a prison room too) | keep "2 m and a pocket" | play §5 item 5 |
| V7 | pictures | floor: four bands by absolute depth; walls: five looks by the step to each neighbour (0.5, 1, 1.5, 2, over 2 m); pawn sink capped at the lip | more floor bands (GPT suggested six) | play §2.3, feasibility §3 |
| V8 | readout format | "Hole 7 m (ledge 4 m) · Water 2.37 m (4,740 L)" | another wording | feasibility §3.3 |

**Still unasked (cards owed; none blocks P3 to P6):** raiders facing a trench they cannot cross (play Q7: scaling
ladders, a perfect wall, or they leave); a big creature in a slot narrower than itself (Q6); water over a creature's head
stops non-swimmers (Q2, reopens ruling 26); who must go down for tending and rescue (Q11); an alert for our own colonist
stuck in a pit (Q12); plants on dug and drained ground (Q9, T3; **not** in this rebuild). Re-validating the hash-bound
north-star bars is his: `fill_tier_legible` (one more state for under 25 cm), `pit_depth_ladder_legible` and
`pawn_height_ladder_legible` (both name "four depths"), and the new R9 bar.

## 4. Risks

1. **Raiders against sheer trenches.** Under the masks, a base ringed by a sheer trench is unreachable to walking
   hostiles, and vanilla raid AI expects a path or a building to breach. A cliff is not a building. True at 2 m today;
   8 m makes it easier to build. P2's raid row must show what raiders actually do (stall, mill, leave) before P5 ships.
   The fix (scaling ladders, or his ruling that the moat is perfect) is the unasked Q7.
2. **Multithreaded pathfinding.** 1.6 batches path requests across threads. The per-request cliff-mask swap must hold
   the right array for the job's whole life while masks rebuild. Never run live. A wrong mask is a pawn walking down a
   7 m wall. P2 owns the proof.
3. **Bodies splitting and merging.** "Connected" means connected below the surface. A falling pond can split; a rising
   one can merge. The band merge tree (`RM_FlowKernel.cs`) is the place to get it from; the fuzz suites must cover it.
4. **Every whole-notch reader at once.** Pumps, burn, heat, drowning, mouseover, Level Holder, drilling reserves and the
   Python oracle all read notches today. P3 and P4 re-point them in one pass; the oracle must change in the same commit.
5. **Save migration.** One migration (body volumes, the view model marker, multiplier removal). Back up the Saves
   folder before the first load. Old builds cannot read a save with digs past 2 m correctly (downgrade unsupported).
6. **Fall damage gets weaker if the cap is raised alone.** `RM_PitTrapMath.FallDropScale` (`:503`) divides by the dig
   cap (`RM_SuperdeepTrap.cs:381`). P5 and P7 must land together, or falls soften for a while.
7. **Shooting is a hot path.** V5 walks the shot line in `CanHitTargetFrom`. Measure the cost on a busy map.
8. **Art waits on him.** P9's looks cannot ship without his look; ship order can hold P10 for it.
9. **Deep digging is slow by design (V1).** If he finds 45 digger-days dull in play, V1 is the dial.

## 5. What he must look at

1. One art review (sheet with true scale, or in-game shots): the under-25 cm water look, the wall band on wet canals,
   deep-lake tints, the five wall faces by drop, the floor tints past 2 m.
2. One staged savegame (P10): S5 redrawn with level numbers, the S6 pond, and the 4/7/7/4 square dug and filled, each
   with the readout and the per-body surface-gap diagnostic.
3. The veto list in §3 (one card, eight lines).
4. The unasked cards in §3, raiders first (it decides whether P2's raid finding is a bug or a feature).
5. The north-star bars to re-validate, including the new level bar (R9).

## 6. What this plan replaces

- `WATER_SURFACE_REPAIR_LEVEL_OR_BUST` is superseded by `WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES`; its live rerun moved
  to `WATER_SCENES_PROVE_AFTER_THE_CREEP_FIX`.
- `LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD`, `WATER_DEPTH_RESKIN_HE_LOOKS_FIRST` and `DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE`
  stay open as children of the epic; `LAKE_FLOOR_TUNE_TEN_TO_FIFTY_METRES` and `LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS`
  were absorbed into P4 (`flowworks_ticket_consolidation_2026-10-17.md`). The rewire item's "pit stays 2 m (D5)"
  is reversed (R5); its item file says so.
- `WATER_SCENES_JUDGE_S5_REDRAWN` is superseded by `WATER_SCENES_S5_JUDGE_THIRD_DRAFT`: S5's whole-notch gravity
  limits are wrong under level water; S5 is redrawn again in P10 before he approves it.
- Every other FlowWorks ticket's verdict: `design/RimMandrake/flowworks_ticket_consolidation_2026-10-17.md`.
- `PIT_SUPERDEEP_COLLAPSE_1` and `PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP` stay open; P2 discharges their live proofs.
- T4 (real elevation) is dead (R8).
