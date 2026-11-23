# Designer packet: Stage 4, the Cold Reader exam

The launcher injects this file with `designer.md` into each run at stage 4. A resumed run gets the file too. Design of
record: `design/RimMandrake/concept_agent_design_2026-11-01.md` §5. For the readers and judges, read the skill
`evaluation-independence`.
`designer_stage.py check` refuses many breaks of the rules below and names the fault. Each rule binds with or without
that check.

## Procedure

1. **Freeze the input.** Record the current tree hash and sheet hash. `designer_stage.py status` shows the inputs, and
   the launcher checks that the exam matches them. A change to the tree, sheet, scenes or floor voids this exam. A new
   owner event on the item also voids this exam. The launcher then reopens the stages that depended on the voiding
   change.
2. **Scenarios, built by the Examiner.** The Examiner is a fresh agent that is not the tree's author.
   - The Examiner writes at least 10 concrete play situations (scenarios).
   - Each scenario has an id, its text, its expected verdict (`expect`: accept or reject, and why) and
     `expect_source`.
   - The source is a leaf (`leaf:<id>` or the bare id) or an `OWNER:<tsn>` event. The source is never the Examiner's
     taste.
   - No two scenarios share an id or a text (case and spacing aside).
   - At least a third of the scenarios probe the reject case of a core line.
   - Freeze the scenarios: `scenarios_hash` is `concept_tree.sha(scenarios)`. Write it before any Reader sees them.
3. **Challenger.** The Challenger is a second fresh agent, neither the author nor the Examiner. Name it in
   `challenger`.
   - The Challenger writes the scenarios most likely to make a Reader accept what a core line rejects.
   - The Challenger's scenarios join the set before the freeze. Mark each one `"by": "challenger"`. Mark the
     Examiner's scenarios `"by": "examiner"`.
   - Each `challenger_misses` entry is one of the Challenger's scenarios.
4. **Two Readers.** A Reader is a fresh agent that sees only `sheet.md`, `tree.json` and the scenario text. A Reader
   never sees `expect`, `record.json`, `log.md` or your notes.
   - Each Reader says accept or reject for each scenario, with the leaf that it relied on.
   - Land their answers in exam.json as `reader_verdicts`, keyed by each Reader's agent id: `{"<agent id>": {"s1":
     {"verdict": "reject", "leaf": "winch_side"}, ...}}`.
   - The read map comes from these answers. The read map records which leaves each scenario read
     (`exam_retake.py`, written as `exam_reads.json` in step 8). Without the answers, no map is recorded, and every
     later retake is whole (step 8, **WHOLE**).
   - Name everyone by agent id, the author, examiner and challenger included, because `check` compares the ids.
   - Neither Reader is a Designer run, the author, the examiner, the challenger or the open run.
   - The two Readers are different agents. Neither Reader declares a self-read or a role in its own words (for example
     "the designer, self-read"). `check` refuses a Reader entry that names its own role.
5. **Control.** One Reader runs on a broken copy of the tree, with a core leaf removed. The control Reader must miss
   what the real tree catches. If the control Reader does not miss, the scenarios do not discriminate.
   - The program makes the copy. `designer_stage.py exam-control <dir> --leaf <id>` writes
     `exam_control/tree.json`, `exam_control/sheet.md` and `exam_control/copy.json` (which leaf, from which tree,
     which phrases).
   - The copy drops the leaf and every line and list entry that names its id.
   - **A control run must strip every mention of the removed leaf's rule, and the program does the stripping.**
   - A `## delegated` or `## pruning` clause can name the same check (e.g. 'new-game cleanup'). Then the control Reader
     still rejects, and the control does not discriminate.
   - Name each such paraphrase with `--strip "<phrase>"` (repeatable): `designer_stage.py exam-control <dir> --leaf
     <id> --strip "new-game cleanup"`.
   - The program drops each sheet line and list entry with the phrase. Other text with the phrase becomes `(removed)`
     (case and spacing aside).
   - The program refuses a phrase found in a kept leaf's `id` or `experience`.
   - Give the control Reader exactly that copy, and land the copy with `exam.json`. Never edit the copy by hand.
   - `check` regenerates the copy from the current tree and the recorded phrases, and refuses any difference.
   - Record `control` with `broken_leaf` (a leaf of the tree), `missed` true and `missed_ids`. The `missed_ids` are the
     scenarios that the control Reader got wrong. At least one of them is sourced on the removed leaf.
6. **Score.** A scenario is right when both Readers match `expect`. `accept_where_reject_core` counts each time a
   Reader accepts where a core line rejects. The exam passes when all three hold:
   - right ≥ 9/10 of the total;
   - `accept_where_reject_core` = 0;
   - every Challenger miss is accounted for (the leaf fixed, or the miss shown not to be the tree's).
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
   (step 8) is not a re-score. The carry re-runs every scenario that the edit touched. The carry also re-checks every
   carried answer against the current tree.
8. **Retake after a coverage repair.** This step applies when stage 5 refused, stage 3 repaired the refusal, and a
   passed exam is on disk. First run `python3 src/RimMandrake/rimflow/exam_retake.py plan design/concepts/<Mod>`. The
   plan prints one of four jobs:
   - **PARTIAL**: re-run only the scenarios that the plan names, through two fresh Readers (step 4).
     - The control Reader (step 5) reads the whole set on a fresh `designer_stage.py exam-control` copy of the current
       tree. So its `missed_ids` can still include a scenario sourced on the removed leaf.
     - Write their answers to one file. The file holds `readers`, `reader_verdicts` (step 4's shape),
       `scenarios_hash`, `control` and `accept_where_reject_core`.
     - Add `inputs` {tree, sheet} from `status` now.
     - Add `challenger_misses` for each retaken Challenger scenario that a Reader got wrong. The old entry for a
       retaken scenario is dropped.
     - Then `exam_retake.py carry design/concepts/<Mod> --fresh <file>` writes exam.json. Every other answer is carried
       forward and marked with the exam that it came from.
   - **NONE_TOUCHED**: nothing that any scenario read changed. Retake nothing. But run `exam_retake.py carry
     design/concepts/<Mod> --fresh <file>` on a file that holds `{}`. The carry restamps the inputs of exam.json. A
     sheet edit that no scenario reads still moves the sheet hash. The gate checks that hash. So without the restamp,
     the exam fails its gate.
   - **WHOLE**: the map cannot tell. The causes are no map, a new leaf, a changed shared part, or a leaf that every
     scenario reads. Do steps 1-6 in full.
   - **CANNOT_RUN**: the plan could not read an input, or `carry` refused the fresh answers. A refused answer file is
     unreadable, or has a missing or stale field. Fix what the message names, and rerun the command that refused.
     Never retake on CANNOT_RUN. Never read CANNOT_RUN as nothing touched.

   Once the exam passes, `exam_retake.py record design/concepts/<Mod>` writes `exam_reads.json`. Land it with
   exam.json.

Charge every Examiner, Challenger, Reader and Control run: `designer_stage.py charge --kind helper`. The helpers run on
your own session, under this Designer run's own allowance (`slot_rules.json` `role_runs`, five). The helpers never run
on the Conductor's budget. A spawn refused `slots_full` is a wait, never a reason to end the run blocked. Wait for a
helper to finish, then spawn.

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

Instead of an exam, the tree may carry `exam_waived`. The waiver is one of two things:

- his words on an OWNER event;
- the Conductor window's act. The act's event has speaker conductor and delegated "conductor-act", and its why names
  lost: and undo: (owner 2026-11-19).

The gate checks both kinds. No other agent waives the exam.

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation; the rules are in `designer.md`.
