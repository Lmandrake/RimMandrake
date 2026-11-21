# Results: the universal-mechanics ruling written into the rule texts (2026-11-21)

Item `RIMMANDRAKE_RULE_MECHANICS_ARE_UNIVERSAL_THE_BIOME_ONLY_SHOWCASES`. Detached BENCH run. The item stays open: the
Conductor closes it after his next cards.

## What changed where

**A. The reversed rule texts, corrected (the wrong text deleted, not superseded):**
- Root `CLAUDE.md` §Every mod ships superb Mod Settings: the line "We promise biome mechanics only inside our own
  biomes..." is deleted. The new line forbids a new biome check or cross-biome switch, and says the existing switches
  wait for his ruling. New section §A mechanic reads conditions, never the biome (ruled points 1 to 4, rule lines and
  pointers). "Read these first" points at `GUIDING_PRINCIPLES.md`.
- `design/RimMandrake/standing_rulings.md` §Every mod ships superb Mod Settings: the sentence "Biome mechanics are
  promised inside our own biomes only" is deleted. His 2026-10-15 words stay word for word, now as the ruling on
  testing. New section §Biome mechanics are universal: the four ruled points, the not-ruled list, his words of
  2026-11-21 and his three card answers.
- `src/RimMandrake/rimflow/concept_floor.json` `biome_scope` (standing, not waivable): now "mechanics written universal:
  a mechanic reads physical conditions, never which biome it is in; ... tested in game on its home biome only". Its
  reader is `concept_tree.py` (Gate A, at the Designer's stage 3). The 12 concept trees pin the floor by hash; they keep
  the old hash until their next stage-3 write. The stale-hash refusal now names its repair (write the tree again; read
  the changed floor lines). Only Contagion (held) sits at stage 3. The same line in
  `design/RimMandrake/concept_agent_design_2026-11-01.md` is corrected.
- `src/RimMandrake/rimflow/roles/designer_write.md`: "Others are biomes in scope only" is now "mechanics written
  universal"; the tree section has a new bullet: a mechanic in a leaf is written as conditions, never as a place; a
  converted mechanic has an offline leaf; in-game leaves run on the home biome only.
- `src/RimMandrake/rimflow/roles/designer.md`: the read list points at `GUIDING_PRINCIPLES.md` entry 1 and at the
  conversion list. It tells the Designer to write each new mechanic as conditions, and to name for each biome whether it
  depends on it, showcases it or is its source (marked as the Conductor's instruction; the principle "a biome earns a
  mechanic" is not ruled).
- `design/RimMandrake/biome_rulings.md`: a pointer section at the top.
- Bar gate: not built (not cheap; reason on `polish.md`).

**B. Held and advancing mods: not edited.** `conversion_list.md` holds one section per mod (33 mods and engines, plus
the rule-text rows and the dated design records that cite the old reading), each with its version on 2026-11-21. The
pipeline hands it over: the Designer's packet (`designer_stage.py` `conversion_section`) names the mod's section as
owed input when the mod's version is newer than its version on 2026-11-21, says "next version, never this one" for the
current version, and says UNMEASURED when the list or the version cannot be read. Page: `boundary.md` (5 promises);
test: `src/RimMandrake/rimflow/selftest_conversion_owed.py`, registered in `pipeline_tests.json` and in
`boundary_check.py` PAGES. Pyrelands 0.1.0 reads "not yet owed" (a test).

**C. `GUIDING_PRINCIPLES.md` at the repo root**, version 0: entry 1 (RULED: conditions, never the place), entry 2
(RULED: a visible effect with no meaning is removed, not confined), and "Proposed, not ruled" with the GPT review's
objection to each.

## What was left for his next card

- The six "Enable outside this biome" switches (and the other per-biome switches in the code census).
- Whether a dangerous mechanic is on by default on every map.
- The Scald exception: an exception, or physics of steam and hot water.
- The wording of the draft's principles 2 to 5, now in "Proposed, not ruled".
- Two lines the fresh reader moved to "Proposed": "a visible effect that implies a consequence tells the truth and is
  readable" (the Conductor's brief asked for it as ruled; it is not his words), and whether a NEW mechanic also owes the
  offline test (he required it at conversion only).
- Third-party and vanilla biomes; the format and authority of `GUIDING_PRINCIPLES.md`.
- His specific examples (Stillshade sun planet-wide; the Rot floor works anywhere and dies in Direct Sun; the geyser
  region removed) are the item's ticket work, not this run's.

## What the fresh reader found

One fresh Opus reader (it did not write the edits) read every changed sentence against his words and the four ruled
points. All his quotes were word for word. Five significant findings, all acted on:
1. Entry 2's first clause ("a visible effect that implies a consequence is true and readable") was not his words: moved
   to "Proposed, not ruled".
2. "Name for each biome: depends, showcases or source" makes the unruled draft principle 2 a duty: cut from
   `GUIDING_PRINCIPLES.md`; kept in `designer.md` as the Conductor's brief instruction, marked as such.
3. Entry 1 "Honours it" claimed the Rot floor and Direct Sun are already built without a biome check: corrected (the
   Rot mat is gated today, rows 14 and 15; Direct Sun reference removed).
4. Root `CLAUDE.md` lost the word "new" in "binds all new design and code": restored.
5. The offline test was written as owed by new mechanics too, which point 2 did not say: now "converted" everywhere.
Polish it listed: on `polish.md` (one line), and "Decorative atmosphere stays" added to the root line.

## Checks

- Published at `ecb17dcdd8` (`./publish`: 115 pipeline checks green; 1 red that was already red the same way on
  origin/main before the change, `acceptance/guard_pilot_launch_live_run_accept.py`: no game was free). The map's
  `foreign:` line, which lists that commit, landed in the commit after it.
- Lose-nothing check (`selftest_rule_files_lose_nothing.py check`): PASS after the map rows of the two corrected
  sections were updated and this run's commit was listed under `foreign:` (the Designer role files grew by the ruled
  lines).
- `selftest_conversion_owed.py`: red on the base (the functions absent; the rule texts not yet corrected: 5 failures),
  green now; 5 planted faults in `designer_stage.py` each turned it red.
- Green after the change: `selftest_concept_tree`, `selftest_designer_stage`, `selftest_designer_stage_reads`,
  `selftest_concept_owner_certify`, `selftest_coverage_calibration`, `selftest_designer_first_version_rules`,
  `selftest_designer_cleanse`, `selftest_boundary_check`, `selftest_close_gate`, `selftest_conductor_authority`,
  `selftest_dispatcher`, `selftest_role_launch`, `selftest_rule_homes_in_briefs`, `selftest_self_fix_rule`,
  `selftest_touching_code_cost_rule`, `selftest_bar_rule_tuning_numbers`, `selftest_restart_now`,
  `selftest_owner_objections`. `code_review_status.py check` reads CLEAN for `designer_stage.py` and `concept_tree.py`.
