# Designer packet: Stage 3, Write

The launcher injects this file with `designer.md` and `designer_scene_contract.md`. You write `sheet.md`, the tree,
`plan.md`, `scenes.json` and `floor.json`. Stage 3 is `done` when `concept_tree.py lint` passes and `designer_stage.py
check` accepts the scenes, the showcase set and the floor.

🔑 Stage 1 approves the root text **before** this stage: his approval, or a delegated Evidence-for-Ask approval
(`designer.md`). Write the tree once, against that root. Then stages 4 and 5 examine, sign and gate the tree at that version.

## The sheet

`sheet.md` is what he reads: a short owner-facing view with compact source ids (`OWNER:<tsn>`, a leaf id). The complete
evidence lives in `record.json` and the tree. Use these sections, in this order and with these names:

```
## his words     verbatim, with the date
## does          - [leaf:<id>] ... | - [floor:<line>] ... | - [waived:<wN>] ... | - [advisory] ...
## does not      - [leaf:<id>] ... (the leaf has cannot_show) | - [floor:<line>] ... | - [waived:<wN>] ...
## waived        his words, one line each
## open          - [core] ... blocks the gate; plain lines do not
## delegated     what you chose for him
## pruning       - <leaf id>: the citation that answers the pruning question
## later         optional: what he put off to v2
```

The sheet is plain bullets under the `# ` title and these sections. `lint` refuses anything else, such as a fence, a
`---`/`===` line, HTML, an `&entity;` or a link. The refusal names the line. A dry walk's sheet adds `## root`. `lint`
accepts `## root` only in a dry walk's sheet.

## The tree

Write draft JSON, then run `python3 src/RimMandrake/rimflow/concept_tree.py write design/concepts/<Mod> --draft <file>`.
The draft holds `subject, kind, root_ref, floor_off, exam_waived, waived, advisory, leaves`. The writer stamps the rest,
voids any signature, and refuses the fields `oracle`, `tier`, `guard` and `budget`. (The launcher owns `budget`. You
propose only the oracle and the tier.) Then run `lint <dir>`.

- `experience`: what an observer sees, in plain words, with the observer named. A constraint is
  `<limit> <unit> on <test machine>`.
  - The leaf says who is looking, at what zoom, in which state and across which variants (a finite, grouped set).
  - The leaf also says what it reads as and what it must not read as. Write at most one "must not read as" line per
    promise.
  - Some "must not read as" lines are neither his words nor the plain opposite of the promise. Such a line is a tip
    for the judge. Such a tip never needs its own test.
- Write a mechanic in a leaf as the conditions it reads: "the mat dies in Direct Sun", not "on Rot maps only"
  (`GUIDING_PRINCIPLES.md` entry 1). A mechanic left unloaded outside its parent biome for load says so, with its
  reason. In-game leaves run on the home biome. No leaf is owed off the home biome.
- `false_pass`: a named wrong world, the worker's cheapest way to fake this leaf.
- `red`: the broken version of the mod this leaf catches, in plain words (hose: "water stops after the first cell").
  If you cannot name one, the leaf is decoration: cut it.
- 🔴 **A leaf is an experience a player would notice, never a tuning number** (owner, 2026-11-16).
  - No leaf, oracle, scene expect or `would_pass` pins a tuning number. Tuning numbers are yield rates, stat values,
    MarketValues, speeds, sizes and any number a renormalization changes.
  - No leaf, oracle, scene expect or `would_pass` pins an asset-variant count, or "every field of every row" of a def.
  - A bar that must re-pass after a renormalization or a new art variant is not a bar. Say the experience instead ("nothing
  in this biome feeds a forager", "the Doublemaw outruns a colonist"). The mod's selftest owns a def's declared numbers.
  A judge's gap on one is advisory only (`bar_rule.py`). His words: `design/RimMandrake/standing_rulings.md` §A passing
  bar is an experience.
- `oracle_proposed` and `tier_proposed`: your offer. Every tier but `offline` needs `tier_reason`:
  `concept_tree.py lint` asks for a `tier_reason` on every tier except `offline`. Skills
  `rimworld-debug-testing` and `live-debugging-proof-harness` say what a quicktest, a bridge read or a live proof can show.
- One `walk` leaf per mod: reload a mid-way save, repeat the core action, and reorder the main actions.
  A walk leaf lists what the observer does, not only what they see. A walk leaf asks for no weeks and no season of play
  (`design/RimMandrake/standing_rulings.md` §Season-long play is play testing).
- When the mod needs a measurement that no instrument can make yet, write an `instrument` leaf. Other leaves depend on
  the instrument leaf through `needs_instrument`.
- The tree has no field for a leaf's origin, and `lint` refuses unknown leaf fields. The sheet line carries the origin.
- The floor is inherited by hash, never copied. State only where this mod differs (`floor_off`, with his words).

To turn what he says on looking into a line, use `designer_examples.md` (the quotation table). "Looks ridiculous" alone
is not a leaf. Write your candidate line and a reject picture, and let him correct them. Keep the scope that he gave his
remark.

## floor.json: per-line applicability

`concept_floor.json` is the bar every mod inherits. `floor.json` in the folder gives every floor line one status:

```
{"lines": {"<line id>": {"status": "applicable"}, "clickable": {"status": "not_applicable",
  "evidence": "nothing is drawn larger than its cell: src/.../Things.xml has only 1x1 defs"},
  "memory": {"status": "applicable", "evidence_mode": "compressed", "establishes": "..."}, ...}}
```

- `applicable`: the line is tested. A numeric line may set `evidence_mode` to `measured` (default), `compressed`,
  `decomposed` or `inferred`. A line in `compressed`, `decomposed` or `inferred` mode also sets
  `establishes`. `establishes` names which properties that run establishes and which stay inferred. A 30-day soak (30 in-game days of advance in one live test) is never required.
  A live test may make a long clock advance when the colony is safe (`design/RimMandrake/debug_process.md` §A long clock advance).
- `not_applicable` with `evidence`: this mod lacks the line's object or behaviour (no selectable art, no
  motion, no visible states). A `not_applicable` line is not a waiver and needs no owner words. The status cannot
  excuse a failed applicable line. `mod_settings`, `log`, `load_order`, `naming`, `text`, `test_isolation`, `dlc`,
  `worldgen` and `multiplayer` apply to every mod.
- `disabled`: an authorised exception, only with a matching tree `floor_off` that carries his words. A standing ruling
  (`waivable: false`) cannot be disabled.
  - Standing rulings are no multiplayer support, no worldgen of any kind and every DLC assumed.
  - Others are mechanics written universal, no live flight test without him, our names and superb Mod Settings.
- Basic checkout covers the canonical supported list. For removal of the mod from a save, document its consequences
  (`save_compat`). A removal test and external compatibility are extended checks that run only when asked.
- Numeric lines stay advisory until calibrated. Calibration is the Conductor's, per line, on measured runs.

## plan.md

`plan.md` holds structure, reuse, order (instrument leaves first), risks, and three designs if there is a real choice.
The proof obligations of `plan.md` are not disposable. Every scene lives in `scenes.json` (checked). Every missing script entry point
or control step is a filed build item, named in that scene's `entry_point_item`. A missing restoration step is never a
build item, because a reset is the harness's job (`designer_scene_contract.md`, "Reset is housekeeping"). You write no code.

When the coverage judge's gaps return a run here, the run ends by writing `coverage_fixes.json`. The file holds one claim
with evidence per gap that the run fixed (`designer_lock.md` item 3). An unclaimed gap is judged still open.

## The showcase set

`scenes.json` also holds the ordered `showcases` and `coverage_rest` lists (`designer_scene_contract.md`, "The showcase
set"). Showcase 1 is his flagship. Each next showcase is the greedy pick: the scene that covers the most new
capabilities, with only very different functionality. Stop when every built or in-scope inventory capability is covered.
Covered means a showcase exercises the capability, or `coverage_rest` names its cheaper scene or leaf check. Run
`designer_stage.py showcases <dir>` before `done`.
Interaction checks and the `walk` leaf stay. Orthogonality (the rule of very different functionality) chooses showcases
and deletes nothing.

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation; the rules are in `designer.md`.
