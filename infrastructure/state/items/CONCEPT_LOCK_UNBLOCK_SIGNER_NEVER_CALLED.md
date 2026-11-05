## problem
Designer stage 5 (Lock) needs `concept_tree.py sign <dir> --by Arbiter`, which refuses unless RM_ROLE_UNIT is an
Arbiter role run (rm-role-arbiter-<n>). But no route launches an Arbiter run for a concept: `arbiter.md` never mentions
concept coverage signing, the Arbiter's launch is a structured claim-judging batch (`role_launch.py` STRUCTURED,
`slot_when: pending_work`), and `--concept` is refused for non stage-machine roles. So no concept can ever lock.
First hit: design/concepts/FlowWorks, run rm-role-designer-1793867400 (2026-11-05): gate refuses only on
"no Arbiter coverage signature"; showcase set accepted; exam.json passed (tree 572198fe, sheet 68f9946f).

## verify
- An Arbiter run can be started on a concept at stage 5 (pending-work kind or run-now with --concept), reads the
  frozen tree/sheet/exam/scenes, and runs `concept_tree.py sign`; `arbiter.md` says when and how.
- `concept_tree.py gate design/concepts/FlowWorks` passes after that run.
