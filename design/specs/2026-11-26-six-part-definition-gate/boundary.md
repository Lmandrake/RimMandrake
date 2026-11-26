# BOUNDARY: the door into the build reads the six-part bar, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/concept_tree.py` (`six_part`, `six_part_errors`, `six_sheet_errors`, the six-part
branch of `lint`, `build` and `write`). Item `RIMMANDRAKE_TOUGHEN_DESIGNER_ENTRY_GATE_VAGUE_BUILDS_CHOKED`. His words
(2026-11-17): *"I think we need to be much tougher about how well defined an item needs to be before it's allowed into
the build step. Designer isn't being harsh enough in terms of imprecision and completeness."* The definition is the
six-part bar of `design/specs/2026-11-16-designer-cleanse-and-bar-definition.md` §3, argued with him in
`RIMMANDRAKE_UPGRADE_DESIGNER_CLEANSE_SIXTY_FOUR_BARS_LOCKED`. Each promise has a test of its own name in
`src/RimMandrake/rimflow/selftest_definition_gate.py`. The acceptance test on the real proposals is
`src/RimMandrake/rimflow/acceptance/definition_gate_accept.py`.

## ACCEPTS

- **a-six-part-tree.** A `tree.json` whose leaves carry `says`: the cleanse apply's output
  (`designer_cleanse.py apply --write`) or a six-part draft written by `concept_tree.py write`. Beside the leaves:
  `whole`, `checks`, `rules`, `meetings`, and the apply's `design_version`, `signature`, `capabilities`, `cleanse`.
- **an-old-tree.** A tree of the old kind (`experience`, `false_pass`, `red` leaves): the locked trees of Pyrelands,
  FlowWorks, Explosive Knockback, Gimme Some Slack, Graffiti and Leaning Scrub, and old fixtures.
- **models.** `models.md` in the concept folder, or the cleanse proposal's `cleanse/models.md`: the headings that an
  `unknown` meeting may name.

## DOES NOT SURVIVE

- A bar whose words are vague but whose parts are all filled passes this gate. Whether a part is good (an accept
  picture that truly departs from the literal wording, a control that truly rules out the cheapest other
  explanation) is the whole-mod check's, the exam's and the coverage judge's (his card of 2026-11-23: all three).
- A Designer run that writes `tree.json` by hand, not through `write`, may leave a tree of the old kind. `lint` still
  passes an old tree, so that the locked trees keep their gate. The Write brief and `write` are the guard.
- A north-star line is not mapped to a bar of a six-part tree: the whole bar carries the root, and the whole-mod check
  hunts a sourced core promise omitted or weakened (the old tree mapped each line to a leaf's `root`).
- The whole bar's reload and second order are read by words: a bar that names them in words this page does not list
  is refused (a repair of the regex, not of the bar), and a sentence that names them without running them passes.
- The flyer rule is not read from a six-part bar's words: a cleansed bar names `Pawn_FlightTracker` and the
  owner-present rule in its `sees` (measured 2026-11-26: a flight-word refusal refused 2 of Cauldron's 10 good bars).

## PROMISES

- **six-part-tree-passes.** A six-part tree with every part filled, one whole bar, a meeting for each shared thing and
  every bar on a `## does` line lints with no refusal.
- **every-part-is-required.** Removing `meant.figurative`, `range`, a `sees` part or the `accept` pictures, or a `lazy`
  that is none of the reject pictures, is refused, and the refusal starts `definition:` and names the part. A bar id that is
  not text, or a `whole` on a bar that is not true or false, is refused, never a crash.
- **no-number-in-a-bar.** A digit or a percentage in `says`, an `accept` or a `reject` picture is refused, naming it.
- **one-whole-bar.** A tree with no whole bar is refused; a whole bar that does not name a reload and a second order
  of the main actions is refused, naming what it lacks. The words are read from its `says`, `accept`, `range.varies`,
  `sees.start` and `sees.on`, never from the reset step or what `range` leaves out; "no reload" and "in order to" do
  not count.
- **shared-thing-has-a-meeting.** Two bars that touch one thing with no meeting that names them both are refused.
- **one-kind-of-leaf.** A tree that mixes a six-part bar with a leaf of the old kind is refused, naming the old leaf.
- **sheet-maps-every-bar.** A bar on no `## does` line, or a `[core]` line anywhere on the sheet, is refused.
- **new-mod-draft-is-six-part.** `write` refuses a mod draft of the old kind (naming the six-part bar) and writes
  nothing; it writes a six-part draft whose tree then lints clean. `legacy=True` (fixtures only) and a dry walk still
  write the old kind.
- **old-tree-unchanged.** A good tree of the old kind lints with no `definition:` refusal.
