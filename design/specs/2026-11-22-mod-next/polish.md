# Polish: mod_next (a record; nobody takes lines from it)

- `src/RimMandrake/Utils/ops_watch.py` `MATURATION_READING_MAX_AGE_S` (1800) restates `mod_next.READING_MAX_AGE_S` for
  the dead-tick alarm. Same number and danger today; it could import the one constant.
- The steward still writes `**Waiting on:**` and `**Next:**` lines in each journal. Since this page, no program reads
  them; they are history only.
- `maturation.gate_step` costs about a minute at the owner's walk (FlowWorks 64 s, measured 2026-11-22; most of it in
  `build_match.check_visit` -> `rerun_relation.relate`). `next_for(gate=False)` avoids it for the page and `pipe why`.
- `maturation_rescue.observe` and `ops_watch` read holds as `set(OH.load())` by key. The keys are already
  `mod_owner_hold.key`, so they agree with `OH.held`; not a second rule.
