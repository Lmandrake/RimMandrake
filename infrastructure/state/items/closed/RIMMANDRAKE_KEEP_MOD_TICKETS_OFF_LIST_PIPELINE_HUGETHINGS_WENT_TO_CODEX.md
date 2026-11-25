# RIMMANDRAKE_KEEP_MOD_TICKETS_OFF_LIST_PIPELINE_HUGETHINGS_WENT_TO_CODEX

## spec

A ticket that is one mod's work is not offered, launched or fed to Codex by the List Pipeline. One rule,
`src/RimMandrake/rimflow/mod_work.py` (`of`): a home `mod:<folder>`, or no home (or `unplaced`) and every repo path in
its title, check and prose inside one mod's folder (`src/<Tier>/<Mod>/`, `design/concepts/<Mod>/`). A path outside the
mod, or paths in two mods, keep a pipeline ticket in the List Pipeline. A home that cannot be read is not launched and
reads "could not look". Callers: `list_dispatch` (decision `mod_work`; no check runs), `list_pipeline.stage_of` (stage
`waiting`, "waits for the Maturation Pipeline run of <Mod>"), `maturation_nonmod.section`, and `list_home.py offer`
(the Codex lane's feed, per `roles/conductor.md`). The three HugeThings tickets the Codex lane started stay as they are.
Page: `design/specs/2026-11-23-list-dispatch/boundary.md` §a-mod-ticket-is-not-the-list-pipelines.

## verify

`python3 src/RimMandrake/rimflow/selftest_list_dispatch.py` ends `selftest_list_dispatch: PASS (0 fail)`. Seen red on
the parent's callers (4 FAIL) and on three planted faults (gather check skip, offer mod filter, stage_of branch).

## criteria

- The selftest `t_a_mod_ticket_is_not_the_list_pipelines` passes and covers: home `mod:X`; no home with paths inside
  `src/**/X/`; a pipeline ticket that names a mod as its example; an unreadable home.
- The pipeline tests for the changed files pass at `./publish`.
- The boundary page states the promise.
