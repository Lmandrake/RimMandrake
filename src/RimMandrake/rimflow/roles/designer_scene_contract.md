# Designer packet: the proof-scene contract

The launcher injects this packet at stage 0 (the script audit) and stage 3 (planning). The contract is data in
`scenes.json`, and `designer_stage.py` checks that data. The schema of `tree.json` rejects unknown fields. So write none
of this in `tree.json`.

## Exploration versus acceptance

- **Exploration** (`kind: exploration`) may be a labelled mock or a hand-staged demonstration. The
  Conductor's mock or demonstration is included. An exploration scene names the `question` that it explores. It never accepts a leaf, however it
  is labelled.
- **Acceptance** (`kind: acceptance`): a named entry point in the mod's proof script creates the scene. Its fields are
  `staged_by: script` and `entry_point: "<repo path>::<function or scene name>"`. If that entry point does not exist yet,
  file its implementation as a build item. Name that item in `entry_point_item` before the acceptance review is scheduled.
  The check refuses a hand or mock scene with `kind: acceptance`.
- **Interaction** (`kind: interaction`) joins two or more features (`features`: leaf ids). The acceptance property of the
  scene is the interaction of those features. Each feature still has its own acceptance scene. An interaction scene
  never substitutes for an acceptance scene.

## Each acceptance or interaction scene

```
{"id": "ladder_climb", "kind": "acceptance", "requirement": ["<leaf id>"], "staged_by": "script",
 "entry_point": "src/.../validation.py::scene_ladder_climb", "entry_point_item": "<item, if the entry point is missing>",
 "start": ["pit depth 3, walls unclimbable without a ladder (asserted)", "pawn can climb ladders"],
 "action": "order the pawn into the pit", "expect": "the pawn uses the ladder: its path crosses the ladder cell",
 "control": {"case": "the same pit with the ladder removed", "expect": "the order is refused: no path",
             "rules_out": "the pawn climbing the wall without the ladder"},
 "restore": "remove pit and ladder, restore terrain from the recorded snapshot", "hold": "immediate | owner_review"}
```

- **Start**: a known, asserted starting state that suits the scene. "Cleared and dry" is one recipe. That recipe is
  wrong for flooding, vegetation, obstruction, fire or integration behaviour.
- **Control**: the control passes when the expected rejection or absence occurs. The control must distinguish the
  intended mechanism from a plausible alternative explanation (`rules_out`). Removal of the object is not automatically
  a useful control. The positive case needs evidence that it used the mechanism.
- **Hold**: whether the scene ends at once or stays up for his review.
- **Recovery**: before a scene changes persistent state, the runner records how to restore that state. The command is
  `designer_stage.py scene-begin <dir> --scene <id> --recovery "<what to put back>"`. A normal exit restores the
  state and closes the entry (`scene-end`). An `owner_review` scene is held instead (`scene-hold --until "<when>"`).
  After an interrupted run, the open entry stays. The launcher then refuses every further run on the concept until
  the entry is restored or held.
- **Reset is housekeeping** (owner, 2026-11-17; `design/RimMandrake/standing_rulings.md` §Resetting a test scene). To
  reset or clean up a scene is the harness's job (save before, reload after). A reset is never a mod deliverable or a build
  item for the mod. A reset is never a coverage gap, and never a Problem or Polish finding. Write the `restore` line.
  Nobody judges that line.
- If the mod's script lacks a part (a start assertion, a control), the stage 0 audit lists the part. Stage 3 files the
  build item. You write no code.
- Each live-only bar (`live_only: true`), and each experience or walk leaf of an old tree off the offline tier,
  has at least one acceptance scene. A showcase never stands in for
  that scene.

The intent behind a scene is the approved requirement that the scene cites (`requirement`), or the `question` of an
exploration.

## The kind of a scene, in the test table

The rule: `design/RimMandrake/standing_rulings.md` §Live tests have three kinds. A stage-6 check with no tag is kind A.
The fields are on `tests.<id>` of `version/test_table.json`. The Stage 6 exit reads them
(`src/RimMandrake/rimflow/live_kinds.py`):

- `test_kind`: `"A"`, `"B"` or `"C"`.
- `tag_evidence`: an empty one is refused.
  - For B, write the things that spoil the run, what was tried to control each thing, and why that was not enough.
  - For C, write the symptom, how often it was seen in how many opportunities, and where the trace is.
- `budget`: the runs to spend on a kind B scene. Write a whole number, before the first run.
- `x_of_y`: `[X, Y]`. Use it only for a result that is random by design (a yield, a drop chance). Write it before the
  first run. A scene that ends short of X escalates to the Conductor. The Conductor decides if the mod needs X of Y, or
  if X was a guess. `x_of_y_calls` is the Conductor's record: do not write it.

A kind C scene is never in a bar's `decides` alone. Do not tag a new scene B or C on a guess: the tester tags it on
evidence.

## The cheapest scene that decides the bar

The rule: `design/RimMandrake/standing_rulings.md` §The cheapest test that decides the bar. The list goes from cheap to
dear:

1. an offline test;
2. a state read;
3. one spawned or held pawn and one order;
4. a staged event;
5. a scene with many pawns;
6. a raid.

A smaller mod list is cheaper than the full list.

- A scene that is not the cheapest carries `cheaper_why` (on `tests.<id>` of the test table). That field says why a
  cheaper, faster, simpler test cannot decide the same bar. Without that evidence, write the cheaper scene.
- Do not write a raid into a scene unless the mod's own function is about raiders. A hostile pawn that the scene spawns,
  holds or orders is not a raid.
- Raid scenes are paused. A scene that must stage a raid carries `stages_raid` (what it stages) in the test table. The
  bar of that scene stays open until the tools can hold a raid still. Each part of the bar that one ordered pawn can
  decide gets its own cheaper scene.

## The showcase set

A mod's face is an **ordered list of showcases**, not one first-judged scene. A showcase is a group of scenes from this
file that he judges as the mod's face. In `scenes.json`, beside `scenes`:

```
"showcases": [
 {"id": "moat", "scenes": ["<scene id>", ...], "exercises": ["<inventory id>", ...], "source": ["OWNER:<tsn>"],
  "decision": "<record.json decision id>"},
 {"id": "...", "scenes": [...], "exercises": [...], "overlap_why": {"<inventory id>": "why staging needs it"}}],
"coverage_rest": [{"capability": "<inventory id>", "by": ["<scene id or leaf id>"], "why": "why an ordinary check is cheaper"}]
```

- **The unit** is a record.json inventory capability.
  - The units are every built entry (`impl: present`, whatever its scope) and every entry in scope (`approved`,
    `opened_by_owner`, `opened_by_conductor`). A built entry ships until it is removed.
  - Only `coverage_rest` covers a built entry scoped `out` (its removal or absence check). A showcase never covers such
    an entry.
  - `exercises` names the capabilities that the showcase really uses in play, not those that the showcase merely has on
    the map.
- **Showcase 1 is the flagship he picked.** The first two bullets are the two routes to that pick.
  - His own pick: the showcase's `decision` names the record.json decision (speaker `owner`) that records his pick, with
    `"flagship": "<this showcase id>"`. The showcase's `source` shares that decision's `OWNER:<tsn>`.
  - Or the pick is a recorded delegated call, under the Evidence-for-Ask rule (designer.md,
    `RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME`). The call is an OWNER.jsonl event, per-ruling that
    item, about THIS concept. The event's why starts with `delegated: evidence-for-ask`. A decision records the event, with
    speaker `conductor`, `delegated: "evidence-for-ask"`, `"flagship": "<this showcase id>"` and source `CONDUCTOR:<tsn>`.
    The showcase's `source` shares that source. A decision that `answers` an ask names one in `record.asks` whose
    `evidence_against` is empty. (An ask that carries evidence waits for him.)
  - Once recorded, that pick is settled: never ask the same choice again. Changed owner input reopens work, as
    designer.md says. His root approval is not a pick, by either route.
  - With no pick recorded, take the obvious pick by that delegated call. The Conductor writes the event of the call. In
    that case, ask him at stage 2 only with concrete evidence against it, written in the ask's `evidence_against`.
  - Lock's first-touch certification is his or the Conductor window's act (owner 2026-11-19, RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS),
    never another agent's.
  - A mod whose only units are built but scoped out has no showcase. `coverage_rest` covers those units.
- **Each next showcase is chosen greedily.** Of the candidates, pick the one that newly exercises the most capabilities
  that no earlier showcase exercised. That showcase features ONLY very different functionality. What it shares with
  earlier showcases is the minimum needed to stage it.
  - The numbers are in `src/RimMandrake/rimflow/showcase_rules.json`. `max_overlap` is 0.25: the share of the showcase's
    exercised capabilities that earlier showcases already exercised. `min_new_after_first` is 3.
  - Both numbers were replayed against ten concepts' showcase sets on 2026-11-18 and kept. `status` in that file says
    what was measured.
  - Above the overlap limit, every shared capability carries its staging reason in `overlap_why`.
  - A scene he named that is not orthogonal stays a scene. Example: FlowWorks' pit trap and island bridges both reuse
    the moat's pits and drawbridges. Such a scene is a showcase only if it passes these rules, or its shared capabilities
    carry `overlap_why`.
- **Stop criterion: efficient coverage.** Add showcases until no candidate newly exercises at least
  `min_new_after_first` capabilities within the overlap limit. Then stop. List every capability left in
  `coverage_rest`. Each entry names the cheaper ordinary scene or leaf check that covers the capability (`by`: a scene
  id here or a tree leaf id), and `why`. Coverage is had when every unit is exercised by a showcase or
  listed in `coverage_rest`. No capability is silently uncovered.
- **Interactions stay.** Orthogonality chooses showcases. Orthogonality deletes no check. Three things remain, whatever they share
  with a showcase: the per-mod `walk` leaf, every leaf whose point IS an interaction, and every `interaction` scene.

What the program checks: `designer_stage.py showcases <dir>` prints it, and stage 3 and stage 5 refuse on it. The
command prints the new-coverage count and the overlap of each showcase. The checks are these:

- Showcase 1 must be bound to his recorded pick.
- A later showcase must newly exercise at least `min_new_after_first`.
- Greedy order: no later showcase offered more new capabilities at an earlier position.
- An overlap over the limit needs a staging reason for each shared capability.
- Each `coverage_rest` entry must name a real scene or leaf and a why.
- Every unit must be covered.

The program does not judge whether two showcases are "very different" in play. The stage 4 exam and his review judge that.

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation; the rules are in `designer.md`.
