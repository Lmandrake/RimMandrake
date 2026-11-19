# RIMMANDRAKE_SETTLE_PARTIAL_IMPL_TWO_INVENTORY_ROWS_UNCOUNTED

## spec
`designer_stage.py showcases` refuses two concepts before counting any coverage (measured 2026-11-18 by the
SHOWCASE_RULES_TUNE_AWAITING_STAGE_THREE replay): `design/concepts/FlowWorks/record.json` inventory entry 28
(`inv_liquid_coating`) and `design/concepts/GimmeSomeSlack/record.json` entry 23
(`cords_join_stubs_on_position_and_slope`) both carry `impl: "partial"`, scope `opened_by_owner`; designer_stage.IMPL
allows only present / absent / unknown. Either `partial` is a real state the schema should admit (and coverage rules
say how a half-built capability is counted), or the two rows should say present/absent with a scope note. A
Designer-machinery question for the Designer / criteria fixer; FlowWorks and GimmeSomeSlack are not owner-held.

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/designer_stage.py showcases design/concepts/FlowWorks` and the same for
`design/concepts/GimmeSomeSlack` each exit 0 with a counted showcase table. Watched failing 2026-11-18 (both exit 1:
"record.json inventory entry N needs an id, impl (present/absent/unknown) and scope").

## criteria
- Both concepts' showcase sets are counted by `designer_stage.py showcases` (exit 0), with no change to any north-star bar.
