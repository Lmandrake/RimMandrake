# FlowWorks: journal

The mod's memory for the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md` §5, "The steward and the journal").
The top part, **the mod as it stands**, is rewritten at every stage change and stays under two screens. Below it the
**history** is only added to. Test of this file: a restarted Conductor can do the next stage change from it alone.

FlowWorks is **not the pilot**: it advances beside Explosive Knockback, offline only (owner by card 2026-11-14, "All four
now, offline only"). Its table matches the pilot's columns (`design/concepts/ExplosiveKnockback/version/test_table.json`).

## The mod as it stands

- **Design Version 0.1.0, locked** on his word 2026-11-13 (`version/VERSION.json`: "Yes, lock the other four mods").
  Code exists and is large: `src/RimMandrake/FlowWorks/` (C# mod, a 325+ case C# SelfTest, about 168 Python selftests,
  a northstar proof harness).
- **Stage now:** Stage 1 finished by hand 2026-11-14 11:50 PST (`version/test_table.json`); Stage 2 by a throwaway
  program (`version/preflight.json`).
- **Bars:** 59 = 28 inventory rows of `record.json` + 31 leaves of `tree.json` (`coverage_judge.required_ids()`).
- **Judge corrections open:** none. FlowWorks has no `coverage_verdict.json` and no `coverage_fixes.json`; the Arbiter
  signed the 59-row checklist covered on 2026-11-05 (`tree.json` coverage). So the pilot's "six corrections" step is
  empty here.
- **Held look statements for this mod:** 81 rows in four files of `design/RimMandrake/validation_holding/` (2026-11-12:
  56 rows; 2026-11-13 morning: 18; 2026-11-13 dig interface: 2; 2026-11-13 evening: 5). [measured, row count]
- **Waiting on:** nothing yet (row 2 in progress).

### The vision (his root paragraph, approved 2026-11-04, OWNER:1793794915205594887; eight lines in `version/vision.md`)

1. Dig canals, pits, moats and trenches; the liquids already on the map (water, tar, fuel, slime) flow in and settle at one level.
2. Every liquid comes from a real supply: the pond drops and refills slowly; a body at the map edge is endless.
3. Its main job is deadly earthworks: moats, covered pit traps, sluices and drawbridges you fill, drain and set alight when you choose.
4. Judged first on one raid: raiders swim a deep moat under a raised drawbridge and tire, a sluice drains it, the drained
   hole holds them as prisoners, and chemfuel pumped in from above is lit by a colonist tossing a flame from the rim.
5. A pit reads as a hole with deep walls; ladders, climbing gear and jumps are the only ways in and out; raiders make a
   ladder to fetch comrades who fell in.
6. Ground within two squares of a filled canal is wetted, so plants there have water; wetted ground is never standing water.
7. Pipes, pumps, tanks and hoses are one network moving the same real litres from the same supply.
8. Every feature has superb Mod Settings; no worldgen, no multiplayer.

### His words on this mod (verbatim; ledger ids in `record.json` decisions and `sheet.md` "his words")

- 2026-11-04, the flagship (OWNER:1793794915205594887): "Filled water moat has raiders swimming across it (getting tired
  swimming in deep water), then water drains and they become Prisoners in a prisoner pit for awhile (prisoner mechanic),
  then chemfuel gets pumped in from above and the burning moat mechanic. All with a drawbridge on top that's raised."
- 2026-11-04, wetting (OWNER:1793794389686592719): "Two squares away from the canal should become "wetted" … This isn't the
  same as flood water … Wetted ground means the plants have access to water."
- 2026-11-04, three raid scenes (OWNER:1793794392567351532): the moat; the covered pit trap onto spikes and the makeshift
  ladder under arrows; the island bridges whose winch is destroyed ("Not today").
- 2026-11-04 (OWNER:1793796507483890758): concept budgets are advisory.
- 2026-11-05, by card: "(b) you click 'capture' from the rim as now, but a drained moat (or pit) counts as a prison without
  a bed." · "a new order where a colonist walks to the rim and tosses a flame onto the square the player picks."
- 2026-11-12 and 11-13, live looks at under-liquid pits: 81 held rows (above), e.g. "Tar is not nearly dark enough (fix)",
  "It's as though each case is independently set in these variables, badly (major fix)", "please ensure they can only be
  placed where there are two sides adjacent to solid ground, to avoid "covered pit bridges" being built."
- 2026-11-13 09:55 PST, on Explosive Knockback: "Melee shove is a great idea, but it belongs in FlowWorks, not here."
  (proposed for the next version, `version/next_version/README.md`; his now-or-next call is open)
- 2026-11-13 ~9:45 PM PST: "The vast grid of options when I selected Digging was... daunting and not how the game usually
  is." (RIMMANDRAKE_DESIGN_FLOWWORKS_DIG_INTERFACE_CONSOLIDATION; his Problem-or-Divergent call is open)

### Oddities (things a reader would otherwise get wrong)

1. **Three bar vocabularies.** The 59 checklist rows are the bars of 0.1.0. The sheet's `[floor:…]` lines (mod_settings,
   tick_cost, worldgen, multiplayer) and the 22 lines of `floor.json` are floor lines every mod meets, not among the 59.
   The older north-star bars in `northstar/` and the walk doc are a third list, not reconciled with the 59.
2. **The inventory's `proof` field reads `stale` (20), `missing` (7) or `exercised_unrecorded` (1)**: it records
   proof-run freshness on 2026-11-05, not whether a test exists.
3. **Three inventory rows are `impl: absent`** at the lock: `inv_prison_no_bed`, `inv_toss_flame`,
   `inv_raider_fetch_fallen`, and `inv_irrigation` is `unknown`. Their leaves (`drained_hole_is_a_prison`,
   `toss_flame_from_rim`, `raiders_fetch_their_fallen`, `canal_wets_two_squares`) are owed code, not owed tests.
4. **`stage.json` is the only locked file that moved since the lock** (blob `3af342069` → `34f93a515`; state, not a bar).
   The seven bar files are byte-identical to `version/bars.md`. `VERSION.json`'s caveat names the old block
   (CONCEPT_LOCK_UNBLOCK_SIGNER_NEVER_CALLED); `stage.json` now reads an OWNER HOLD instead. [measured 2026-11-14]
5. **Every live scene's tier says "quicktest"**, but the `tier_reason` of 25 of 31 leaves is one boiler-plate sentence ("an
   on-screen look and a live state change: needs a running map"). Whether a faster test decides each is the Stage 4
   challenger's question; the reason is written, not shown true.
6. **The C# SelfTest is one console app holding most of the offline checks** (325+ cases); a Python wrapper
   `src/RimMandrake/Utils/selftest_flowworks_stock.py` builds it with Windows `dotnet.exe`. One run covers many bars.
7. **Another helper is changing water code** under `src/RimMandrake/FlowWorks` during this run; a red offline test today
   may be that work, not a regression.

## History (dated, added to only)

### 2026-11-14 11:24 PST, advance begins (rm-builder, detached, offline only)

Brief from the Conductor: rows 1 to 3 of the pilot table by hand (journal, finish Stage 1, Stage 2), throwaway scripts
only, stop before Stage 3; FlowWorks advances beside the pilot, so its counts are its own. Owner, 2026-11-14: "We need to
get this going."

### 2026-11-14 11:28 PST, row 1 done: journal started

- **Cost:** about $1.9 of model spend (the harness budget line; tokens not separately measured), about 5 minutes wall.
  Nearly all of it reading: the spec, the pilot's journal and draft table, the version folder, `record.json`,
  `tree.json`, `scenes.json`, `sheet.md`, the four held-statement files.
- **Boring enough to automate:** "his words" (already in `record.json` decisions and `sheet.md` with ledger ids); the
  post-lock drift check (one `git hash-object` per pinned file against `bars.md`); counting held rows per mod; the
  `proof`/`impl` census of the inventory.
- **Needed judgment:** which oddities would trip a cold reader (three bar vocabularies, `proof: stale` is not "no test",
  absent rows owe code not tests); seeing that the pilot's correction step is empty for this mod.

### 2026-11-14 11:50 PST, row 2 done: Stage 1 finished by hand

The table: `version/test_table.json` (read view `version/test_table.md`), same columns as Explosive Knockback's. Made by
`version/advance_scripts/make_table.py` and `held_place.py` (throwaway; kept only as provenance for the Stage 2 program).

- **Runnable tests, measured by running every one today** (offline only; the game was never touched):
  - C# SelfTest, one full run: **1,337 cases ok, 0 failed, 531 s**. Two cases are defined in source but never reached
    (`Sheet_runs_back_into_the_canal_when_it_is_drawn_down_relief_…`, `LadderClimb_slow_only_on_the_art_D…`).
  - Python selftests under `src/RimMandrake/FlowWorks` (169 incl. the kernel oracle): **159 pass, 10 red, ~1,360 s**.
    Red and deciding a bar: `northstar/selftest_flowworks_northstar.py` (settings classes missing from
    `site_spec.SETTINGS_SOURCES`), `Tools/selftest_liquid_looks.py`, `selftest_natives_drink_own_water.py` (RM_TheChill:
    RM_PropaneDeep → RM_Liquid_Propane blocked), `validation_v2.py --offline` (O2: `digLabourMultiplier` C# default
    None, table 4.0; O8; O-LIVE-NEG X4_pit_wall_over_head). Red but not mapped to a bar (harness or look tests):
    `selftest_extensions.py`, `selftest_lines_proof.py`, `selftest_flowworks_call_sites.py` (55/56),
    `selftest_flowworks_looks_round.py` (tar tint), `selftest_flowworks_readout_proof_parity.py`, `selftest_hose_port.py`,
    `selftest_review_map.py`. Another helper is editing water code: some reds may be that work.
- **Counts (measured, `test_table.md`):** 59 bars. **51 already had at least one runnable test** (an offline test that
  ran, or an in-game scene whose entry function exists). **49 have a built offline deciding test; 44 of them all green
  today.** 25 have every deciding test runnable today. 2 have no offline decider at all (`moat_raid_sequence`,
  `walk_moat_season`: the game alone decides them). In-game scenes: 29, entry exists 14, absent 15.
  Offline tests: 78 built (74 green, 4 red), 6 specified for Stage 3 (wetting, wetness probe, toss flame, fetch fallen,
  bedless prison care, dig-time arithmetic).
- **Judge corrections:** none to apply (no verdict file; Arbiter signed 2026-11-05).
- **Held statements:** all 81 rows placed (`held_statements` in the table): 58 on a bar and a test; 10 are harness,
  process, rule or answered-question rows with no bar; **13 have no 0.1.0 bar** (the geyser hot tub and its bubbles, 9 rows; liquid coating on pawns and washing it
  off, 3; the dig-interface consolidation, 1): questions for him, below.
- **Settings sweep moved offline:** FlowWorks' in-game "sweep" is `validation_v2.py`'s live L2 `settings_default` read.
  Every default it compares is decidable offline: `T_SETTINGS_SWEEP_OFFLINE` = C# `SettingsReset/MachinerySettings/
  Settings` cases + `selftest_settings_registry.py` + `selftest_settings_search.py` + the northstar selftest's registry
  rows + `validation_v2.py --offline` O2. The game keeps only `sc_walk`'s master switch off and on mid-game; L2 stays a
  harness precondition, not a bar. No bar text edited. **It is red today** (O2 and the northstar registry rows).
- **Cost:** about $4.0 (harness budget $1.9 → $5.9), 22 minutes wall, of which ~9 min C# suite and ~20 min Python sweep
  ran in the background in parallel with the mapping.
- **Boring enough to automate:** running every selftest and recording rc and seconds; per-case C# results by prefix;
  checking each scene's entry function exists; row counts of held files; rendering the md view.
- **Needed judgment:** which C# case families and which Python selftests decide which bar (the regex groups in
  `make_table.py`; a judge should challenge them); telling mod tests from harness tests; placing 81 held rows (which bar,
  or "no bar"); recognising that FlowWorks' "settings sweep" is the L2 live read and that O2 already decides it offline.
