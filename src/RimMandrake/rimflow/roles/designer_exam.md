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
   case. Freeze them: `scenarios_hash` is `concept_tree.sha(scenarios)`, written before any Reader sees them.
3. **Challenger**: a second fresh agent that writes the scenarios most likely to make a Reader accept what a core line
   rejects. Its scenarios join the set before the freeze.
4. **Two Readers**: fresh agents that see only `sheet.md`, `tree.json` and the scenario text, never `expect`,
   `record.json`, `log.md` or your notes. Each says accept or reject per scenario, with the leaf it relied on.
5. **Control**: one Reader run on a deliberately broken copy of the tree (a core leaf removed); it must miss what the
   real tree catches, or the scenarios do not discriminate.
6. **Score**: a scenario is right when both Readers match `expect`. `accept_where_reject_core` counts any Reader accepting
   where a core line rejects. Pass: right ≥ 9/10 of the total, `accept_where_reject_core` = 0, every Challenger miss
   accounted for (the leaf fixed, or the miss shown not to be the tree's).
7. **On failure**: the misses name the leaves to rewrite; `return` to stage 3 with the decision named, or to stage 2 if a
   miss needs his answer. Never re-score the same scenarios against an edited tree without refreezing.

Charge every Examiner, Challenger, Reader and Control run: `designer_stage.py charge --kind helper`.

## exam.json

```
{"author": "<the tree's author run>", "examiner": "<a different agent>", "inputs": {"tree": "<tree hash>",
 "sheet": "<sheet sha256>"}, "scenarios": [{"id": "s1", "text": "...", "expect": "reject: ...",
 "expect_source": "leaf:winch_side"}, ...], "scenarios_hash": "...", "readers": ["...", "..."],
 "control": {"broken_leaf": "...", "missed": true}, "score": {"right": 10, "total": 10},
 "accept_where_reject_core": 0, "challenger_misses": [{"id": "s7", "accounted": "..."}]}
```

Or the tree carries `exam_waived` in his words on an OWNER event (the gate checks it); the Conductor cannot waive it.

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation; the rules are in `designer.md`.
