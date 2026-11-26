# Designer packet: Stage 3, Write

The launcher injects this file with `designer.md` and `designer_scene_contract.md`. You write `sheet.md`, the tree,
`plan.md`, `scenes.json` and `floor.json`. Stage 3 is `done` when `concept_tree.py lint` passes and `designer_stage.py
check` accepts the scenes, the showcase set and the floor.

🔑 Stage 1 approves the root text **before** this stage: his approval, or a delegated Evidence-for-Ask approval
(`designer.md`). Write the tree once, against that root. Then stages 4 and 5 examine, sign and gate the tree at that version.

## The sheet

`sheet.md` is what he reads: a short owner-facing view with compact source ids (`OWNER:<tsn>`, a bar id). The complete
evidence lives in `record.json` and the tree. Write it as plain bullets under the `# ` title:

```
## his words     verbatim, with the date
## does          - [leaf:<bar id>] the bar's says, one line per bar
## later         optional: what he put off to the next version
```

Every bar is on one `## does` line, and every `## does` line names a bar. A `[core]` line anywhere blocks the gate.
Other sections (the definition, the costs, the edges) are his reading. `lint` does not check their prose.

## The tree: six-part bars

His words (2026-11-17): *"I think we need to be much tougher about how well defined an item needs to be before it's
allowed into the build step. Designer isn't being harsh enough in terms of imprecision and completeness."* The door into
the build reads one definition of a bar: the six-part bar (`design/specs/2026-11-16-designer-cleanse-and-bar-definition.md`
§3, and `designer_cleanse.md`). `concept_tree.py write` refuses a mod draft with leaves of the old kind
(`experience`, `false_pass`, `red`). `lint` judges each bar part by part, with the same checks as the cleanse pass.

Write draft JSON, then run `python3 src/RimMandrake/rimflow/concept_tree.py write design/concepts/<Mod> --draft <file>`.
The draft holds `subject, kind, root_ref, floor_off, exam_waived, waived, advisory, leaves, whole, checks, rules,
meetings` (and `capabilities` when you keep an inventory). The writer stamps the rest and voids any signature. Then run
`lint <dir>`. Each refusal starts `definition:` and names the bar, the part and what passes.

Three kinds of statement, never mixed:

- a **bar** (a leaf): an experience a player would notice, without which he would reject this version. Only bars decide
  a pass, and no bar holds a number;
- a **check** (`checks`: `{id, what}`): a regression reading that we keep. It may hold a number;
- a **rule** (`rules`: `{id, rule, touches}`): a choice we made about how to build it. A builder may attack it.

Each bar has these parts. `lint` refuses a bar that lacks one:

- `id`: a letter, then letters, digits or `_`. The sheet names it as `[leaf:<id>]`.
- `says`: one sentence: who notices what, where. Write a mechanic as the conditions it reads ("the mat dies in Direct
  Sun", not "on Rot maps only"; `GUIDING_PRINCIPLES.md` entry 1).
- `meant`: `{intent, source, figurative}`. `source` is his words by event, a standing ruling, or `delegated: from
  what`. `figurative` lists each word not to be held literally: `{word, stands_for, accept}` (`[]` when no word is
  figurative). "A line of fire" held literally is the fault that this part prevents.
- `accept` and `reject`: two or more pictures each. One accept picture departs from the literal wording. One reject
  picture satisfies the literal wording.
- `lazy`: the laziest build that satisfies the words, word for word one of the reject pictures; or `none: <why the
  words are tight>`.
- `range`: `{varies, left_out}`: the situations it holds across, and what is left out.
- `sees`: `{instrument, start, on, control, reset}`: the cheapest instrument that truly tells pass from fail, what must
  be switched on for its reading to count, and a control against the cheapest other explanation. A live-only bar
  (`live_only: true`) adds `live_only_why`: why nothing cheaper can see it.
- `touches`: every state, geometry or moment it shares with other bars and rules.
- `live_only`: `true` or `false`.

Beside the bars:

- `whole` names the one whole bar: the mod complete, every mechanic on, nothing locked, across its cycle, with a
  mid-way reload and a second order of the main actions. `lint` refuses a whole bar that does not say both.
- `meetings`: one per thing that two or more bars or rules touch, `{thing, members, holds_together, why}`.
  `holds_together` is `argued` (say it), `measured` (cite it) or `unknown` (name the `## ` heading of `models.md`
  that would settle it).

🔴 **A bar is an experience a player would notice, never a tuning number** (owner, 2026-11-16).
- No `says`, `accept`, `reject` or figurative `accept` pins a number, a percentage, a count of asset variants or
  "every field". Numbers go in `range` or `sees`, or in a check. `lint` refuses the number and names it.
- A bar that must re-pass after a renormalization or a new art variant is not a bar. Say the experience instead
  ("nothing in this biome feeds a forager", "the Doublemaw outruns a colonist"). His words: `design/RimMandrake/
  standing_rulings.md` §A passing bar is an experience.
- In-game bars run on the home biome. No bar is owed off the home biome. A bar that needs worldgen is refused.
- A flyer's flight is read from `Pawn_FlightTracker` state, never live-tested without him (`sees` says so).

To turn what he says on looking into a bar, use `designer_examples.md` (the quotation table). "Looks ridiculous" alone
is not a bar. Write your candidate `says` and a reject picture, and let him correct them. Keep the scope that he gave
his remark. The floor is inherited by hash, never copied. State only where this mod differs (`floor_off`, with his
words).

A locked tree of the old kind (`experience`, `false_pass`, `red` leaves) still lints as before. Its next version is
written in six-part bars.

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

`plan.md` holds structure, reuse, order (the instruments that `sees` and `models.md` name first), risks, and three designs if there is a real choice.
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
Interaction checks and the whole bar stay. Orthogonality (the rule of very different functionality) chooses showcases
and deletes nothing.

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation; the rules are in `designer.md`.
