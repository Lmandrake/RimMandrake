# Designer packet: Stage 4, the Cold Reader exam

Injected with `designer.md` whenever the concept is at stage 4, resumed or not. Design of record:
`design/RimMandrake/concept_agent_design_2026-11-01.md` §5. Skill `evaluation-independence` for the readers and judges.
`designer_stage.py check` refuses many breaks of the rules below and names the fault. Each rule binds with or without it.

## Procedure

1. **Freeze the input.** Record the current tree hash and sheet hash. `designer_stage.py status` shows the inputs, and
   the launcher checks that the exam matches them. A change to the tree, sheet, scenes or floor voids this exam. So does
   a new owner event on the item. The launcher then reopens the stages that depended on them.
2. **Scenarios, built by the Examiner**, a fresh agent that is not the tree's author. The Examiner writes at least 10
   concrete play situations. Each has an id, its text, its expected verdict (`expect`: accept or reject, and why) and
   `expect_source`. The source is a leaf (`leaf:<id>` or the bare id) or an `OWNER:<tsn>` event, not the Examiner's
   taste. No two scenarios share an id or a text (case and spacing aside). At least a third probe a core line's reject
   case. Freeze them: `scenarios_hash` is `concept_tree.sha(scenarios)`, written before any Reader sees them.
3. **Challenger**: a second fresh agent, neither the author nor the Examiner, named in `challenger`. The Challenger
   writes the scenarios most likely to make a Reader accept what a core line rejects. Its scenarios join the set before
   the freeze, each marked `"by": "challenger"` (the Examiner's `"by": "examiner"`). Each `challenger_misses` entry is
   one of its scenarios.
4. **Two Readers**: fresh agents that see only `sheet.md`, `tree.json` and the scenario text, never `expect`,
   `record.json`, `log.md` or your notes. Each says accept or reject per scenario, with the leaf it relied on. Land
   their answers in exam.json as `reader_verdicts`, keyed by each Reader's agent id: `{"<agent id>": {"s1": {"verdict":
   "reject", "leaf": "winch_side"}, ...}}`. The read map comes from these answers. Without them no map is recorded, and
   every later retake is whole. Name everyone by agent id, the author, examiner and challenger included, because
   `check` compares the ids. Neither Reader is a Designer run, the author, the examiner, the challenger or the open
   run. The two Readers are different agents, and neither declares a self-read or a role in its own words.
5. **Control**: one Reader runs on a broken copy of the tree, with a core leaf removed. The control Reader must miss
   what the real tree catches, or the scenarios do not discriminate. The program makes the copy.
   `designer_stage.py exam-control <dir> --leaf <id>` writes `exam_control/tree.json`, `exam_control/sheet.md` and
   `exam_control/copy.json` (which leaf, from which tree, which phrases). The copy drops the leaf and every line and
   list entry that names its id. **A control run must strip every mention of the removed leaf's rule, and the program
   does the stripping.** A `## delegated` or `## pruning` clause can name the same check (e.g. 'new-game cleanup').
   Then the control Reader still rejects, and the control does not discriminate. Name each paraphrase with
   `--strip "<phrase>"` (repeatable): `designer_stage.py exam-control <dir> --leaf <id> --strip "new-game cleanup"`.
   The program drops each sheet line and list entry with the phrase. Other text with the phrase becomes `(removed)`
   (case and spacing aside). The program refuses a phrase found in a kept leaf's `id` or `experience`. Give the control
   Reader exactly that copy, and land the copy with `exam.json`. Never edit the copy by hand. `check` regenerates the
   copy from the current tree and the recorded phrases, and refuses any difference. Record `control` with
   `broken_leaf` (a leaf of the tree), `missed` true and `missed_ids`. The `missed_ids` are the scenarios that the
   control Reader got wrong. At least one is sourced on the removed leaf.
6. **Score**: a scenario is right when both Readers match `expect`. `accept_where_reject_core` counts any Reader
   accepting where a core line rejects. Pass: right ≥ 9/10 of the total, `accept_where_reject_core` = 0, every Challenger miss
   accounted for (the leaf fixed, or the miss shown not to be the tree's).
7. **On failure, mend it now, in this same run** (owner, 2026-11-20: *"allow it a chance to mend it during judgement
   while the context is fresh, even if it then gets blind judged again"*; `standing_rulings.md` §Touching code has a
   cost; if you see it, do it). The misses name the leaves to rewrite. You hold the tree, the misses and the reasons
   now. So do not end the run, and do not leave the repair to a later run:
   - `return` to stage 3 with the decision named. The `return` records the move and does not end your run.
   - Rewrite the leaves that the misses name. Change only what a miss names.
   - Take the exam again in this run by step 8 (`exam_retake.py plan`, then fresh Readers on what the edit touched).
     The Readers stay fresh agents that never saw the old answers. Their blind read is the check on your repair.
   - Only a miss that needs his answer returns to stage 2 and waits. Mend every other miss first.
   - A miss about wording that no player-facing experience turns on is polish: one line in `log.md`, no rewrite.
   Never re-score the same scenarios against an edited tree without refreezing. A carry by `exam_retake.py carry`
   (step 8) is not a re-score. The carry re-runs every scenario that the edit touched and re-checks every carried
   answer against the current tree.
8. **Retake after a coverage repair**: stage 5 refused, stage 3 repaired it, and a passed exam is on disk. First run
   `python3 src/RimMandrake/rimflow/exam_retake.py plan design/concepts/<Mod>`. The plan prints one of four jobs:
   - **PARTIAL**: re-run only the scenarios that the plan names, through two fresh Readers (step 4). The control Reader
     (step 5) reads the whole set on a fresh `designer_stage.py exam-control` copy of the current tree. So its
     `missed_ids` can still include a scenario sourced on the removed leaf. Write their answers to one file. The file
     holds `readers`, `reader_verdicts` (step 4's shape), `scenarios_hash`, `control` and `accept_where_reject_core`.
     Add `inputs` {tree, sheet} from `status` now. Add `challenger_misses` for each retaken Challenger scenario that a
     Reader got wrong (the old entry for a retaken scenario is dropped). Then `exam_retake.py carry design/concepts/<Mod>
     --fresh <file>` writes exam.json. Every other answer is carried forward and marked with the exam that it came from.
   - **NONE_TOUCHED**: nothing that any scenario read changed. Retake nothing, but run `exam_retake.py carry
     design/concepts/<Mod> --fresh <file>` on a file holding `{}`. The carry restamps the inputs of exam.json. A sheet
     edit that no scenario reads still moves the sheet hash. The gate checks that hash, so without the restamp the
     exam fails its gate.
   - **WHOLE**: the map cannot tell. Causes are no map, a new leaf, a changed shared part, or a leaf that every
     scenario reads. Do steps 1-6 in full.
   - **CANNOT_RUN**: the plan could not read an input, or `carry` refused the fresh answers. A refused answer file is
     unreadable, or has a missing or stale field. Fix what the message names and rerun the command that refused.
     Never retake on CANNOT_RUN, and never read it as nothing touched.
   Once the exam passes, `exam_retake.py record design/concepts/<Mod>` writes `exam_reads.json`. Land it with exam.json.

Charge every Examiner, Challenger, Reader and Control run: `designer_stage.py charge --kind helper`. The helpers run on
your own session, under this Designer run's own allowance (`slot_rules.json` `role_runs`, five), never the Conductor's
budget. A spawn refused `slots_full` is a wait, never a reason to end the run blocked: wait for a helper to finish, then spawn.

## exam.json

```
{"author": "<the tree's author run>", "examiner": "<a different agent>", "inputs": {"tree": "<tree hash>",
 "sheet": "<sheet sha256>"}, "scenarios": [{"id": "s1", "text": "...", "expect": "reject: ...",
 "expect_source": "leaf:winch_side", "by": "examiner"}, ...], "scenarios_hash": "...", "readers": ["...", "..."],
 "reader_verdicts": {"<reader agent id>": {"s1": {"verdict": "reject", "leaf": "winch_side"}, ...}, ...},
 "challenger": "<a fresh agent, by id>",
 "control": {"broken_leaf": "...", "missed": true, "missed_ids": ["s4", "s9"]}, "score": {"right": 10, "total": 10},
 "accept_where_reject_core": 0, "challenger_misses": [{"id": "s7", "accounted": "..."}]}
```

Instead of an exam, the tree may carry `exam_waived`: his words on an OWNER event, or the Conductor window's act. The
act's event has speaker conductor and delegated "conductor-act", and its why names lost: and undo: (owner 2026-11-19).
The gate checks both. No other agent waives the exam.

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation; the rules are in `designer.md`.
