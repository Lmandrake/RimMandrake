# Designer packet: Stage 4, the Cold Reader exam

Injected with `designer.md` whenever the concept is at stage 4, resumed or not. Design of record:
`design/RimMandrake/concept_agent_design_2026-11-01.md` §5. Skill `evaluation-independence` for the readers and judges.

## Procedure

1. **Freeze the input.** Record the current tree hash and sheet hash (`designer_stage.py status` shows the inputs; the
   exam must match them when the launcher checks it). If the tree, sheet, scenes or floor change, or an owner event on the
   item arrives, the launcher reopens the stages that depended on them and this exam is void.
2. **Scenarios, built by the Examiner**, a fresh agent that is not the tree's author: at least 10 concrete play
   situations, each with its expected verdict (`expect`: accept or reject, and why) and `expect_source` (the leaf id or
   `OWNER:<tsn>` the expectation comes from; never the Examiner's own taste). At least a third probe a core line's reject
   case. `designer_stage.py check` refuses a scenario with no id or text, two scenarios with the same id or the same text
   (case and spacing aside), and an `expect_source` that is neither a leaf of the tree (`leaf:<id>` or the bare id) nor
   one of his OWNER events. Freeze them: `scenarios_hash` is `concept_tree.sha(scenarios)`, written before any Reader sees them.
3. **Challenger**: a second fresh agent that writes the scenarios most likely to make a Reader accept what a core line
   rejects. Its scenarios join the set before the freeze, each marked `"by": "challenger"` (the Examiner's
   `"by": "examiner"`). `check` refuses an exam that names no `challenger`, a Challenger who is the author or the
   examiner, no scenario marked as the Challenger's, and a `challenger_misses` entry that is not one of its scenarios.
4. **Two Readers**: fresh agents that see only `sheet.md`, `tree.json` and the scenario text, never `expect`,
   `record.json`, `log.md` or your notes. Each says accept or reject per scenario, with the leaf it relied on. Land
   their answers in exam.json as `reader_verdicts`, keyed by each Reader's agent id: `{"<agent id>": {"s1": {"verdict":
   "reject", "leaf": "winch_side"}, ...}}`. That is where the read map comes from: without it no map is recorded and
   every later retake is whole.
   `designer_stage.py check` refuses an exam whose `readers` names fewer than two agents, one agent twice, a
   Reader with no agent id, a Designer run, a Reader whose own words declare a self-read or a role, or the author,
   examiner, challenger or open run; name everyone by agent id, author, examiner and challenger included, since the id
   is what it compares and an exam whose author, examiner or challenger names none is refused.
5. **Control**: one Reader run on a deliberately broken copy of the tree (a core leaf removed); it must miss what the
   real tree catches, or the scenarios do not discriminate. **The program makes the copy:** `designer_stage.py
   exam-control <dir> --leaf <id>` writes `exam_control/tree.json` and `exam_control/sheet.md` (the leaf gone, every line
   and list entry naming its id gone) and `exam_control/copy.json` (which leaf, from which tree, which phrases). Nobody edits that copy by hand: name any
   paraphrase of the removed rule to the program, `--strip "<phrase>"` (repeatable; below), then give the control Reader
   exactly that copy; it lands with `exam.json`. `designer_stage.py check` regenerates the copy from the current tree and
   the recorded phrases and refuses any difference, and
   refuses an exam whose `control` is absent, whose `broken_leaf` is not a leaf of the tree, whose `missed` is not true,
   whose `missed_ids` (the scenarios the control Reader got wrong) are empty, name no scenario, or include none sourced on
   the removed leaf, and whose copy is missing, was made from another tree, holds other leaves than the tree's minus that
   one, or still names its id in the tree or the sheet.
6. **Score**: a scenario is right when both Readers match `expect`. `accept_where_reject_core` counts any Reader accepting
   where a core line rejects. Pass: right ≥ 9/10 of the total, `accept_where_reject_core` = 0, every Challenger miss
   accounted for (the leaf fixed, or the miss shown not to be the tree's).
7. **On failure**: the misses name the leaves to rewrite; `return` to stage 3 with the decision named, or to stage 2 if a
   miss needs his answer. Never re-score the same scenarios against an edited tree without refreezing; a carry made
   by `exam_retake.py carry` (step 8) is not a re-score: it re-runs every scenario the edit touched and re-checks
   every carried answer against the current tree.
8. **Retake after a coverage repair** (stage 5 refused, stage 3 repaired, you are back here with a passed exam on
   disk): first run `python3 src/RimMandrake/rimflow/exam_retake.py plan design/concepts/<Mod>`. It prints one of four
   outcomes, each a different job:
   - **PARTIAL**: re-run only the scenarios it names, through two fresh Readers (step 4). The control Reader (step 5)
     reads the whole scenario set on a fresh `designer_stage.py exam-control` copy of the current tree, so its
     `missed_ids` can still include a scenario sourced on the removed leaf. Write their answers to one file: `readers`,
     `reader_verdicts` (step 4's shape, a leaf per answer), `inputs` {tree, sheet} as `status` shows them now,
     `scenarios_hash`, `control`, `accept_where_reject_core`, and `challenger_misses` for any retaken Challenger
     scenario a Reader got wrong (the old entry for a retaken scenario is dropped). Then `exam_retake.py carry
     design/concepts/<Mod> --fresh <file>` writes exam.json with every other answer carried forward and marked with
     the exam it came from.
   - **NONE_TOUCHED**: looked, and nothing any scenario read changed: retake nothing, but run `exam_retake.py carry
     design/concepts/<Mod> --fresh <file>` on a file holding `{}`. It restamps exam.json's inputs: a sheet edit no
     scenario reads still moves the sheet hash the gate checks, and the exam then fails its gate.
   - **WHOLE**: the map cannot tell (no map, a new leaf, the shared part changed, a leaf every scenario reads): steps
     1-6 in full.
   - **CANNOT_RUN**: the plan could not read an input, or `carry` refused the fresh answers (unreadable, or a field
     missing or stale): fix what it names and rerun the command that refused; never retake on it, and never read it
     as nothing touched.
   Once the exam passes, `exam_retake.py record design/concepts/<Mod>` writes `exam_reads.json`; land it with exam.json.

Charge every Examiner, Challenger, Reader and Control run: `designer_stage.py charge --kind helper`.
These helpers run under this Designer run's own allowance (`slot_rules.json` `role_runs`, five), counted on your own
session, never the Conductor's budget. A spawn refused `slots_full` means wait for one of yours to finish, then spawn:
it is a wait, never a reason to end the run blocked.
- **A control run must strip every mention of the removed leaf's rule, and the program does the stripping.** Removing a core leaf from `tree.json` and its sheet lines is not enough: a `## delegated` or `## pruning` clause naming the same check (e.g. 'new-game cleanup') still lets the control Reader reject, so the control does not discriminate. Name the phrase to the program: `designer_stage.py exam-control <dir> --leaf <id> --strip "new-game cleanup"` drops every sheet line and list entry holding it and turns any other text holding it into `(removed)` (case and spacing aside); a phrase found in a retained leaf's `id` or `experience` is refused. The copy is never edited by hand: `check` refuses a copy that differs from the one the program generates.

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

Or the tree carries `exam_waived` in his words on an OWNER event (the gate checks it); the Conductor cannot waive it.

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation; the rules are in `designer.md`.
