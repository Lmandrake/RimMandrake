## spec
Owner pick 11 (2026-11-12, OWNER.jsonl tsn 1794524114165680240): fold the north-star frame judge into the pre-look scene
judge, leaving one item and one judge.

- Frame judge: `src/RimMandrake/Utils/northstar_driver/judge_cli.py`. It judges whether a frame shows what a must-show bar
  says the player sees. No FlowWorks bar has a judge (inventory `design/RimMandrake/validation_inventory_2026-11-12.md`
  row 114, UNMEASURED).
- Pre-look scene judge: `design/RimMandrake/scene_look_judge_brief.md`, two passes. First a fresh judge with an open
  question ("does anything look odd?"), then a different judge with the checklist.

### What to do
Make the must-show bar the pass-2 checklist input of the scene-look judge. Pass 1 stays open-question and blind to the bar.
Move whatever judge_cli.py does that the brief lacks into the brief's tooling: frame capture, the bar format and the
verdict record. Then delete judge_cli.py and its docs and fix every inbound reference. Check reachability first, and if
anything live calls judge_cli, keep it as the pass-2 entry and say so.

### Done when
There is one judge brief and one entry point. A must-show bar from one north-star run is judged through it, and
`grep -rn judge_cli` finds no orphan reference.
