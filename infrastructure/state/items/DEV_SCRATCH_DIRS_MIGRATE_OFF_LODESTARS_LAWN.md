# DEV_SCRATCH_DIRS_MIGRATE_OFF_LODESTARS_LAWN

Owner, 2026-10-19, verbatim: *"Clean up all of that. Get rid of old stuff. also check for a bunch of
strange dirs in /dev called _codexhome and _rmbuild etc. Do we really need all of that? What is it?
It's cluttering my dev dir, and that's a Lodestar maintained area. Not good."*

Inventory (sizes, mtimes, references, classification): `Transient/dev_underscore_dirs_inventory_2026-10-19.md` (pinned).
The DEAD dirs were deleted on 2026-10-19; what is left is in use by running daemons and tools
that have the path written into their code.

## Goal

Move every RimMandrake runtime dir out of `D:\Luke\dev\` (Lodestar's area) into the data root
`D:\ClaudeWork\rimmandrake` (`/mnt/d/ClaudeWork/rimmandrake`; Lodestar's machine-wide agent storage,
owner 2026-10-19: *"Find another storage place for yourself permanently and use it."*), resolved through
ONE path function, `src/RimMandrake/Utils/rmpaths.py` (`RM_DATA_ROOT`, else Lodestar's
`agent_storage.py rimmandrake`; no fallback), so that no code writes out `D:\Luke\dev\_*`.
Plan: `D:\ClaudeWork\rimmandrake\path_migration_for_foundry.md`.

## Status 2026-10-20 (FOUNDRY, night window)

DONE: rmpaths.py + guard `selftest_rmpaths.py`; ~80 code files and the instructing docs repointed; the six dirs
moved (`_artpipe`->`artpipe`, `_artstore`->`artstore`, `_rmscratch`->`scratch`, `_rmbuild`->`build`, `_obs`->`obs`,
`_rmdashboard`->`dashboard`); systemd units carry `rm-data-root.conf` drop-ins; Windows user env `RM_DATA_ROOT`
set; task "WSL Move Once" repointed. Dated design history keeps the old paths as history.
OPEN: the other non-project entries in `D:\Luke\dev` (worktrees `wt_live2`, `RimMandrake-wt-handoff`,
`RimMandrake-wt-livedeploy`; `Rimworld`, `Rimworld_history.bundle`, `reference`, `rimtools`, `govee_scan.ps1`) —
see the plan's last table; BENCH clone must pull (its units run pre-rmpaths code on env-var overrides).

## Dirs to move and the code that names them (grep 2026-10-19, foundry clone)

- `_artpipe` (artpiped queue state; `rm-artpiped.service` `Environment=ARTPIPE_STATE_DIR=/mnt/d/Luke/dev/_artpipe`
  plus its Description): ~33 references under `src/RimMandrake/Utils` (artpipe/, art/), 2 GimmeSomeSlack, 2 FlowWorks.
- `_artstore` (content-addressed art store): `src/RimMandrake/Utils/art/artledger.py`, `art/game_art.py`;
  docs `design/RimMandrake/art_ledger_design_2026-10-04.md`, `rich_screenshot_art_prereview.md`.
- `_rmscratch` (save backups, DRIVER_LOCK/BRIDGE_SHARED json, edge_gate profiles, codex staging):
  ~28 Utils, 19 GimmeSomeSlack, 10 FlowWorks, 2 rimflow, 2 bridgetools, 1 Pyrelands; skills telemetry,
  rimbridge/references, live-debugging-proof-harness, generating-images (scripts + references);
  `src/RimMandrake/Utils/art/facing_regen.py` (`codex_home_facing_regen`); ~15 design docs.
  ⛔ Holds `saves_backup_*`, `ported_mutator_saves`, `decisions_backup_*`: move, never delete.
- `_rmbuild` (winbuild.py staging, `WINBUILD_ROOT` env already exists — rebuildable cache):
  `src/RimMandrake/Utils/winbuild.py`, `selftest_winstage.py`, `suite_evidence.py`, `vv_shipped_matrix.py`,
  `telemetry/tcommon.py`, several selftests (`selftest_*_lint.py`, `selftest_flowworks_stock.py`,
  ExplosiveKnockback/KineticArms kernels), csproj HintPaths in FlowWorks, FlowWorks SelfTest, Pyrelands,
  EmpirePursuit, PyrelandsMechanics; skills rimbridge-companion, rimworld-deploy; design GIT_WORKFLOW.md,
  bridge_system.md and git-migration docs.
- `_obs` (bridge observatory run logs): `Utils/rimdrive/obs_events.py`, `rimdrive/session.py`,
  `modcheck/obs_summary.py`, `modcheck/live_queue/common.py`, `telemetry/tcommon.py`; design
  bridge_debugging_system.md, bridge_validation_observatory.md.
- `_rmdashboard` (RimPulse digests): `Utils/pulse/pulse.py` (`RM_PULSE_DIGESTS`).

## Owner decision still owed (do not move, delete or salvage without it)

- `_rm_old_git_2026-10` (4.2 GB, the pre-migration shared-tree `.git`) and `_rm_shared_tree_leftovers_2026-10`,
  both MOVED (not deleted) on 2026-10-19 to `D:\ClaudeWork\retired-trees\rimmandrake\`
  (a manifest; its tar is gone). `design/RimMandrake/git_migration_freeze_2026-10-02.md` says to keep them
  "until the owner says delete". A patch-id audit on 2026-10-19 found 14 refs (branches + 4 stashes)
  holding commits that are not on origin/main by patch, so deleting it may lose work. Ask him: salvage then delete, or delete.

## Done when

`ls -d /mnt/d/Luke/dev/_*` is empty, `grep -rn 'Luke/dev/_\|Luke\\\\dev\\\\_' src skills` finds nothing outside dated
design history, and artpiped plus one winbuild run work from the new root.
