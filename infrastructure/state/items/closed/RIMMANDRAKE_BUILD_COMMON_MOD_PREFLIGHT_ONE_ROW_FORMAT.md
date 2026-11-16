## spec
Plan `design/plans/2026-11-14-maturation-pipeline-build.md` slice 3 and `design/RimMandrake/maturation_pipeline.md` §9
("A common preflight that tags each refusal as build work or a spec fault"; open question 2 of plan §5). Grown from the
four throwaway preflights (`design/concepts/*/version/preflight*.py`, `version/advance_scripts/`): one program, one row
format, each refusal tagged "offline-build work" or "spec fault". Then the spine's preflight exit becomes "no
spec-fault refusal" and its `--steward-confirms` hand step goes away. Not the ticket preflight of
`design/specs/2026-11-12-ticket-preflight-before-any-token.md` (that one checks tickets, this one checks a mod version);
coordinate with `RIMMANDRAKE_GUARD_PIPELINE_DOORS_CHEAPLY_NO_CEREMONY`'s design before building. Found by the pipeline
sleeper census (`design/RimMandrake/pipeline_sleepers_census_2026-11-15.md`).

Acceptance test (the plan's, written at planning): `python3 src/RimMandrake/rimflow/selftest_mod_preflight.py`: run on
copies of the four mods it gives the same refusal ids as each mod's recorded `preflight.json` (measured on the base),
and planted faults (a missing def, a bar with no test, an unplaced held statement) are each refused. Watched failing on
464c69ccf0: the file does not exist (python exit 2).
