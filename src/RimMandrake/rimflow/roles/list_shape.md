# Workshop Pipeline: the Shape run, and its Work when the item is small

`list_dispatch.py` launches this brief (decision `shape`) on an open list item that has no outcome check and no route.
Page: `design/specs/2026-11-23-list-shape/boundary.md`. Plan: `design/specs/2026-11-22-coordination-every-agent-must-use/plan.md`
§Shape. The owner, 2026-11-23: "It would likely often be useful to have a single agent take an item through the non mod
pipeline though due to the smaller nature of the work than a mod." So one run shapes the item and, when it is small,
does the work with the same context. The text below the marker is the brief; `list_shape.brief_text` fills it.

<!-- BRIEF -->
Shape list item {item}, and do its work in this same run if it is small (the Workshop Pipeline's Shape stage).

Title: {title}
Why the lane sent it to Shape: {why_due}

The item has no outcome check. A program closes an item only when its check holds on origin/main, so the check that you
write is the judge of "done". Write a check that tests the NEED, not the paper. Example: for a study of wrongly routed
tickets, "the report exists" is the wrong check (the report existed and the tickets stayed wrong for three days); "the
tickets are routed correctly" is the right check.

Steps:
0. Start the item, before anything else:
   python3 src/RimMandrake/rimflow/cli.py start {item} --seat BENCH --why "Workshop Pipeline Shape run (list_dispatch.py)" --publish
1. Read it whole: the ITEM PACKET below, and the files that it names. Run python3 src/RimMandrake/rimflow/cli.py show {item}
   only for a part that the packet left out or could not read, or when this brief holds no packet.
2. Is it worth the touch (CLAUDE.md §Touching code has a cost)? If nobody would care, or other work already did it, or
   another item does it: drop it (`cli.py drop {item} --reason "not worth the touch: <why>" --seat BENCH --publish`) or
   close it with the sha of the work that did it. Then stop.
3. Split it into parts. Give each part ONE of these:
   - an outcome check that a program runs: `path-has:<repo path>::<text>`, `path-lacks:<repo path>::<text>`, or
     `cmd:<command>` (exit 0 when the need is met, 1 when it is not). Beside it, its fooled_by line: "what would pass
     this check and leave the need unmet?" A check with no fooled_by line is marked weak for the weekly audit.
   - a route, when the part is not yours to finish: {"who": one of {routes}, "ask": "<what is asked>", "resumes":
     "<what resumes the item>"}.
       judge: a taste call against written constraints. The maker never makes a taste call.
       owner: a question about what the owner wants, with its evidence, or one of his five acts.
       conductor: a choice between goals, or a looser bar.
       review: a look that only a sitting with the owner can give.
     Do not route a repair that our standing rules already allow. Do it.
   Each check must fail now (the step-1 gate refuses a check that is never seen failing). A part that is done already
   takes "holds_why": "<why>".
4. Write the split, with the size that you judge:
   python3 src/RimMandrake/rimflow/cli.py shape {item} --parts '<json list>' --size small --seat BENCH --why "Workshop Pipeline Shape run" --publish
   A refusal names the part and the repair. Repair the split and run the command again.
   - small (the default): you can do every part that has a check in this run. Go on to step 5.
   - large: the parts need more than one run's work, or different skills or models, or you need help. Write
     `--size large` and stop here. The lane gives the item its own Work runs.
5. Small: do the work. Run the item's check (step 4 printed it) until it holds:
   python3 src/RimMandrake/rimflow/list_effect.py check '<the item check>'
   Land with ./publish -m "{item}: <what>" <explicit paths>, then close:
   python3 src/RimMandrake/rimflow/cli.py close {item} --sha <published sha> --seat BENCH --why "Workshop Pipeline: the check holds at <sha>" --publish
   An operational item also takes its --live promise. A taste call inside the work goes to a judge route, never to you.
6. If you cannot finish, end with exactly one of these on the item:
   - a note whose text starts `LEFT OPEN:` and names the ONE next act that a second run would do. The lane gives the
     item at most one more run, and only on that note.
   - a dated wait (`cli.py wait {item} --until <YYYY-MM-DD> --reason "<who acts next and on what>"`) when the next act
     is someone else's.
   Do not file a new item for your own next step. A routed part keeps the item open: the party that answers it shapes
   the item again with `cli.py shape`.

An example of --parts:
[{"name": "rule_in_pages", "effect": "path-has:CLAUDE.md::<the rule's line>", "fooled_by": "the line is in a section that agents do not read", "route": null},
 {"name": "his_pick", "effect": null, "fooled_by": null, "route": {"who": "owner", "ask": "pick A or B (evidence: <paths>)", "resumes": "his card answer; then shape the item again"}}]

Authority: a Conductor instruction carries his authority (`--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`), never his quotation.
