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
| R5 | **Default max colonist dig 8 m, a setting from 2 to 20 m.** Lakes keep their own floors (ceiling settable to 125 m; their shape is R11). The 0.5 m dig step stays | card, on the epic |
| R6 | **Everything in one big rebuild:** exactly-level water, the metres-and-litres rewiring (`LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD`), the very-shallow look, deeper digs (T1) and the relative-depth rules | card, on the epic |
| R7 | **The four rules keyed to "2 m deep" become relative to the height difference:** drowning, fall damage, spikes, shooting | card, on the epic |
| R8 | **Real z-level elevation (T4) is dead**, not deferred: no raised ground, hills, height line of sight, or cells above cells | card, on the epic |
| R9 | A north-star bar: every square of connected still water stands at the same surface height (to within 1 cm), read from game state, not the picture | owner said, `OWNER.jsonl` tsn 1792258162801304562; bar text not yet written into the walk file |
| R10 | **One kind of water** (natural-water engine doc, Option B2): every pond, lake, canal and pit is one kind; wet squares write the main terrain layer from one ladder of vanilla water terrains by depth; natural lakes get floors recorded at map creation, nothing on screen changes; rivers and oceans stay vanilla and limitless, never converted | card, on `WATER_NATURAL_DECIDE_ONE_SURFACE` |
| R11 | **Lake depth varies by lake and biome:** *"Vary it. Some lakes will be shallow and silted up. Others will be deep and chasm-like. Depends on the biome. The more mountainous, the deeper in general. The more plains-like, the smoother/shallower. They should also have some variation down there, not just a radial crater."* Replaces the radial slope and the 20 m / 50 m fixed numbers; ceiling to 125 m stays; 50 m only for mountainous/deep biomes | owner said, same item |
| R12 | **Pawns may swim in water 2 m or deeper**; non-water fluids keep the no-swim refusal; deep water stops being a barrier for pits and trenches | card, same item |
| R13 | **Limitless bodies are marked** in the readout: *"Any natural body of water that is supposed to be 'clearly limitless' should be so marked, so players aren't shocked."* Narrows ruling 35 (2026-09-17) | owner said, same item |

**Reversed by R5:** the morning's D5, *"the deepest pit stays 2 m"* (unified-depth spec §10). He reopened it himself the
same day by asking how deep players should dig. The walls-20%-over-the-head rule stays a visual rule only.

## 1. Work packages, in order

| WP | item | what | ESTIMATE (agent-days) | needs live |
|---|---|---|---|---|
| **P1** | `WATER_SCENES_PROVE_AFTER_THE_CREEP_FIX` | Deploy the `fe309aefe` DLL (game down), rerun S2, S5 and S6 of `northstar/water_scenes_walk.py`, record with modcheck. Proves the dry-front fix that the solver will replace, and gives a baseline | 0.5 | deploy + bridge, ~15 min cold load |
| **P2** | `PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH` | The owed live proofs of the built climb work: pocket grid, cliff masks, ramp, ladder; a raid against a base ringed by a sheer trench; a row proving the per-request mask swap holds under 1.6's multithreaded pathfinding while masks rebuild | 1 to 3 | bridge; minimal list where it can, full list for the raid |
| **P3** | `WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES` | The level-surface solver (level-surface design Option 1): body volume in decilitres, one surface per body from a floor-height histogram, depth = surface − floor on read; bodies split and merge by connectivity **below** the surface; mouth pace kept; ponds first, then canals and joins; a diagnostic that reports the largest surface gap per body in metres; save migration with a logged before/after per body | 4 to 7 | none to build; P9 proves it |
| **P4** | `LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD` | The metres-and-litres rewiring (unified spec §7.2) done **in the same pass** as P3: `RM_Volume` constants, `FillTier` by metres of water, "five" deleted, one burn rate, `sourceBudgetMultiplier` deleted, strings in metres, Python oracle reads C# constants. Fold `LAKE_FLOOR_TUNE_TEN_TO_FIFTY_METRES` in here (same bed code and settings; its ceiling only, the floor shape is P11) | 1.5 to 2.5 on top of P3 (the shared files are counted once) | none |
| **P5** | `PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT` | T1 deeper digs: split `Superdeep` (4) from `MaxDigDepth` (setting, default 16 notches = 8 m, range 4 to 40); dig job, designator and workgiver read the grid, not the terrain; "dig to N m" designator; pocket bands and masks sized by the largest climb limit, not the dig cap; wall-face arrays to about 8 notches, saturating; pawn sink by the drop below the near lip; floor tint per depth band past 2 m; rain loop by the cell's own depth. Cap sites listed in the item | 3 to 5 | none to build |
| **P6** | `DIG_COST_TUNE_DEEP_IS_A_MEGAPROJECT` | Keep today's work curve (3,200 × the notch being cut); settings text in metres; lowering the cap never shallows a dug cell. Inside P5's pass | 0.25 | none |
| **P7** | `PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE` | R7's four rules relative (forms in §3), plus pit rooms by person-band pocket without the 2 m clause | 3 to 5 | none to build |
| **P8** | `DEPTH_READOUT_BUILD_TWO_NUMBERS_NOT_ONE` | The readout on the solver's numbers: "Hole 7 m (ledge 4 m) · Water 2.37 m (4,740 L)"; floors to 0.5 m, water to two decimals. **Plus the limitless mark (R13):** sea and edge rivers read "Open water, never runs dry"; limited bodies show none | 0.75 to 1.5 | bridge, in P10 |
| **P9** | `VERY_SHALLOW_WATER_RESKIN_HE_SEES_FIRST` + `WATER_DEPTH_RESKIN_HE_LOOKS_FIRST` | Art: the under-25 cm look (R2); the wall band on wet canals and deep-lake tints (already filed); the deeper wall faces and floor tints from P5. **One review for him covering all of it** | 1 to 2, plus his look | his look (sheet or in-game shot) |
| **P14** | `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` (BENCH, re-scoped) | **One-water terrain ladder (R10):** one ladder by water depth for lakes and dug water (under 25 cm → 0.5 → 1 → 1.5 → 2 m+ → deep tints); wet dug squares on the base layer, not temp (gives dug water fishing and ice); full natural lakes unchanged; things on squares that change band; 1.5 m band takes chest-deep affordances; save migration | 2.5 to 3.5 (about 1 overlaps P3/P4) | none to build; live rows in P10 |
| **P11** | `LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP` | **Natural floors (R10, R11):** every limited lake recorded at map creation (books only); per-lake, per-biome-roughness floor generator with irregular variation (seeded, deterministic); ceiling to 125 m, 50 m only for mountainous/deep biomes; propose the roughness table for his approval | 2 to 3.5 | his look at floor variety |
| **P12** | `DEEP_WATER_BUILD_SWIM_OR_SINK` | **Deep swimming (R12):** passable deep band, swim speed, exhaustion and drowning (one rule with P7's V2), apparel/weight, animals, non-swimmer pathing; non-water fluids refuse; barrier re-check of every pit/trench/moat item | 3 to 5 (+0.5 live) | bridge, minimal list |
| **P13** | `FISH_ROLL_MEND_PONDS_BORN_BARREN` | **The vanilla water-body traps** (engine doc §2.3): fish re-roll as a body grows; fish and fishing-zone squares return when a dried pond refills; body split refresh; plant hysteresis | 1 to 1.5 | live rows in P10 |
| **P10** | the epic | Integration: selftests and the Python oracle in lockstep; S5 redrawn with level numbers (R3) and re-sealed; one staged savegame showing S5, S6 and the 4/7/7/4 square; the R9 bar written into `design/validation_walks/RimMandrake/FlowWorks.md` `## north star` for his re-validation; deploy and a full live walk | 1.5 to 3 (about 1 of it live) | deploy + bridge + his look |

**Total (ESTIMATE): about 26 to 48 agent-days, midpoint about 37** (was 17 to 33 before the natural-water rulings;
P11-P14 add about 8 to 13 net of the P14/P3 overlap, P8 +0.25 to 0.5, and P10 0.5 to 1.5 more live for the new rows). Of that, about 4 to 7 days are live (P1, P2, P12, P10), and the art and the lake floors wait on his look. A single agent working in order is the safe shape (the same files recur in P3 to P7).

## 2. Dependency order

```
P1 ─┐                 (live, now; independent of code)
P2 ─┼──────────────────────────────┐   (live; gates SHIPPING deeper digs, not coding them)
    │                              │
P3 + P4 (one pass) ──> P14 ──> P11 ──> P5 + P6 ──> P7 + P12 ──> P8 ──> P10 (deploy, walk, his look)
                        │                  │                                ^
                        └── P13 ───────────┼────────────────────────────────┤
P9 art ────────────────────────────────────┴── (any time; P5 adds wall/floor looks) ─┘
```

- P14 right after P3: P3 writes the surface, P14 decides how it is drawn and what vanilla sees. P11 needs P3's bodies
  and P4's bed settings. P13 needs P14 for dug water (it fixes natural ponds regardless). P12 lands with P7 (one
  drowning rule) and needs P14's deep band.

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

**Natural water, defaulted (veto-able; not asked; the natural-water docs' recommendations):** fish in dug water by the
game's size rule (follows R10); the same fish return when a dried pond refills; reeds survive short pump cycles; fish
live in lakes as well as seas, caught not seen; no beach ring (owner card 2026-10-18: drained means
dry); a river below a dam keeps flowing (rivers stay vanilla, R10). The steeper-lake question is superseded by R11.

**Still unasked (cards owed; none blocks P3 to P6):** raiders facing a trench they cannot cross (play Q7: scaling
ladders, a perfect wall, or they leave; now with swimmable moats, R12); a big creature in a slot narrower than itself
(Q6); ~~water over a creature's head stops non-swimmers (Q2)~~ answered by R12; who must go down for tending and rescue (Q11); an alert for our own colonist
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
10. **Deep water is no longer a barrier (R12).** A flooded trench, moat or prisoner pit is swimmable to its lip; only the
    sheer-wall climb rule holds. Flagged on `PIT_SUPERDEEP_COLLAPSE_1`, `PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH`,
    `HUTT_SLAVE_PIT_TEST_SITE_1`, `PIT_TEMPERATURE_SOFTENING_1`; P12 records a verdict per site.
11. **The base-layer switch (P14)** touches every place that stages canal water and every reader that assumes the fill
    is temp terrain (looks, mouseover, the dig workgiver). Other mods will now see canals as real water (wanted).
12. **Vanilla identity checks on `WaterDeep`** (roads, mods): making deep water enterable (P12) must not swap the def
    identity those checks rely on.

## 5. What he must look at

1. One art review (sheet with true scale, or in-game shots): the under-25 cm water look, the wall band on wet canals,
   deep-lake tints, the five wall faces by drop, the floor tints past 2 m.
2. One staged savegame (P10): S5 redrawn with level numbers, the S6 pond, and the 4/7/7/4 square dug and filled, each
   with the readout and the per-body surface-gap diagnostic.
3. The veto list in §3 (one card, eight lines).
4. The unasked cards in §3, raiders first (it decides whether P2's raid finding is a bug or a feature).
5. The north-star bars to re-validate, including the new level bar (R9) and a narrowed limitless bar (R13).
6. **Lake floor variety (P11):** a flat-biome and a mountainous-biome map with lakes drawn down, and the roughness table.
7. **Live proofs owed for the natural-water rulings** (P10 walk, minimal list, no flyers): a colonist swims across a
   3 m lake and climbs out (P12); fish caught from a fishing zone on a dug 100+ square pond (P13 + P14); a dug canal
   freezes and thaws with its water picture intact (P14); a flood over a wet canal (P14).

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
- `WATER_NATURAL_DECIDE_ONE_SURFACE` is closed as decided (R10-R13); its work is P11-P14 and the P8 mark. The engine
  doc's proposed `WATER_LAYER_UNIFY_ONE_LADDER_FOR_ALL` was not filed: `POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD` was reused
  as P14.
