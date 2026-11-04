# Designer packet: Stage 3, Write

Injected with `designer.md` and `designer_scene_contract.md`. You write `sheet.md`, the tree, `plan.md`, `scenes.json`
and `floor.json`. Stage 3 is `done` when `concept_tree.py lint` passes and `designer_stage.py check` accepts the scenes
and the floor. 🔑 Ask him to approve the root text **before** this stage (it is stage 1's result): the tree is written once,
against an approved root, and then examined, signed and gated at that version.

## The sheet

`sheet.md` is what he reads: a short owner-facing view with compact source ids (`OWNER:<tsn>`, a leaf id); the complete
evidence lives in `record.json` and the tree. Sections, in this order and with these names:

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

The sheet is plain bullets: `lint` refuses any other `##` section, any other heading but the `# ` title, a tag in a heading,
a code fence, a `---`/`===` line, HTML, an `&entity;`, a link, a bracket that is unbalanced, nested or holds more than
letters, digits, spaces and `:-`, any line in `does`/`does not` that is not a tagged bullet, and a `[core]` tag anywhere but
`## open`. A dry walk's sheet adds `## root`, which `lint` accepts for a dry walk only.

## The tree

Draft JSON, then `python3 src/RimMandrake/rimflow/concept_tree.py write design/concepts/<Mod> --draft <file>`. The draft
holds `subject, kind, root_ref, floor_off, exam_waived, waived, advisory, leaves`; the writer stamps the rest, voids any
signature, and refuses Setter fields (`oracle`, `tier`, `guard`, `budget`). Then `lint <dir>`.

- `experience`: what an observer sees, in plain words, with the observer named. A constraint is
  `<limit> <unit> on <test machine>`. The leaf says who is looking, at what zoom, in which state, across which variants
  (a finite, grouped set), what it reads as and what it must not read as.
- `false_pass`: a named wrong world, the worker's cheapest way to fake this leaf.
- `red`: the broken version of the mod this leaf catches, in a plain sentence (hose: "water stops after the first cell").
  If you cannot name one, the leaf is decoration: cut it.
- `oracle_proposed` and `tier_proposed`: your offer. The Setter binds. Live needs `tier_reason`. Skills
  `rimworld-debug-testing` and `live-debugging-proof-harness` say what a quicktest, a bridge read or a live proof can show.
- One `walk` leaf per mod: a reload from a save made mid-way, a repeat of the core action, a second order of main actions.
  A walk leaf lists what the observer does, not only what they see.
- Whatever the mod needs measured and nothing can yet measure: an `instrument` leaf, depended on through `needs_instrument`.
- The tree has no field for a leaf's origin (`lint` refuses unknown leaf fields): the sheet line carries it.
- The floor is inherited by hash, never copied. State only where this mod differs (`floor_off`, with his words).

Turning what he says on looking into a line: `designer_examples.md` (the quotation table). "Looks ridiculous" alone is not a
leaf: write your candidate line and a reject picture and let him correct them; keep the scope he gave it.

## floor.json: per-line applicability

`concept_floor.json` is the bar every mod inherits. `floor.json` in the folder gives every floor line one status:

```
{"lines": {"<line id>": {"status": "applicable"}, "clickable": {"status": "not_applicable",
  "evidence": "nothing is drawn larger than its cell: src/.../Things.xml has only 1x1 defs"},
  "memory": {"status": "applicable", "evidence_mode": "compressed", "establishes": "..."}, ...}}
```

- `applicable`: it is tested. A numeric line may say `evidence_mode` `measured` (default), `compressed`, `decomposed` or
  `inferred`, and then `establishes` names which properties that run establishes and which stay inferred; a 30-day soak
  is never required (no long runs).
- `not_applicable` with `evidence`: the object or behaviour the line is about does not exist in this mod (no selectable
  art, no motion, no visible states). It is not a waiver, needs no owner words, and cannot excuse a failed applicable
  line. `mod_settings`, `log`, `load_order`, `naming`, `text`, `test_isolation`, `dlc`, `worldgen` and `multiplayer`
  apply to every mod.
- `disabled`: an authorised exception, only with a matching `floor_off` in the tree carrying his words. A standing
  ruling (`waivable: false`) cannot be disabled: no multiplayer support, no worldgen of any kind, every DLC assumed,
  biomes in scope only, no live flight test without him, our names, superb Mod Settings.
- Basic checkout covers the canonical supported list. Removal: document its consequences (`save_compat`); executing a
  removal test, and external compatibility, are extended checks that run only when asked.
- Numeric lines stay advisory until calibrated; calibration is the Arbiter's, per line.

## plan.md

Structure, reuse, order (instrument leaves first), risks, three designs if there is a real choice. Its proof obligations
are not disposable: every scene lives in `scenes.json` (checked), and every missing script entry point, control or
restoration step is a filed build item named in that scene's `entry_point_item`. You write no code.

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation; the rules are in `designer.md`.
