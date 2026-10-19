# D:\Luke\dev\_* inventory and cleanup, 2026-10-19

Owner, verbatim: *"Clean up all of that. Get rid of old stuff. also check for a bunch of strange dirs in
/dev called _codexhome and _rmbuild etc. Do we really need all of that? What is it? It's cluttering my dev
dir, and that's a Lodestar maintained area. Not good."*

Method: `du -sh` plus the newest file mtime per dir; grep of the dir names across foundry `src/ skills/
infrastructure/ design/`, the `systemctl --user cat` output of the rm-* units, and Lodestar and Machinist
docs/bin/tools/knowledge; open handles from WSL `/proc/*/{cwd,fd}` and Windows `Win32_Process` command lines.
Lodestar `sync/registry.md` claims none of them.

Disk free before: `/` 758G, `D:` 2.0T (1.8T used). After: `/` 771G, `D:` 2.0T (1.7T used).

## Removed: 47 dirs on D:, plus 38 stale stages inside _rmbuild

| dir | size | newest | what it was | why it was safe to delete |
|---|---|---|---|---|
| `_codexhome_*` (21: fh, ladA/B, oe, on, rampC, rd_dalgo_n/s, rd_dome_e/n/s, rd_dome2_e/n/s, rd_ember_n, rd_hawk_4/5, rd_wasp_e/n, tallA/B) | ~0.4–0.55G each, ~8.9G total | 10-15/16 | per-job Codex CLI homes for hand-run image jobs. Each held a copy of `auth.json` | not used by any code (artpiped's worker homes live in the Windows profile, `.codex_workers/artpipe`); only reference is two old `.log` files under FlowWorks `art_source/Ladder/raw`; no open handles |
| `_codexhomes` (hosejoints_* homes) | 5.3G | 10-16 | the same thing, for the hose-joint art jobs | not referenced anywhere |
| `_rmbuild_*` (25 variants: B, C, bench*, fwfinal, liqcont_*, mapcontrols, ratchet1-3, sluice, susp, taps, wallclimb) | 1.7M–308M, ~1G total | 10-05..10-18 | throwaway winbuild staging made through a `WINBUILD_ROOT=` override | no code names them; can be rebuilt; no open handles |
| `_rmbuild/selftest_*` (38 of 62) | part of 19G | 10-10..10-18 | selftest stage dirs whose source clone no longer exists | `selftest_winstage.py` says a stage whose clone is gone is dead; hash checked against every live clone; kept anything under 6 h old |

**Generated art saved first:** of the 69 PNGs in the codex homes' `generated_images/`, 29 match the
`_artstore` or the repo byte for byte. The other 40 (52 MB) were copied to
`D:\Luke\dev\_rmscratch\codexhome_rescue_2026-10-19\` (with `MANIFEST.tsv`) before deletion.

## Kept: LIVE (code or a running daemon uses them; relocation is filed as `DEV_SCRATCH_DIRS_MIGRATE_OFF_LODESTARS_LAWN`)

| dir | size | newest | what it is | who uses it |
|---|---|---|---|---|
| `_artpipe` | 1.2G | 10-19 | the artpipe daemon's queue state | `rm-artpiped.service` (`ARTPIPE_STATE_DIR`), artpiped.py has it open now; ~37 code references |
| `_artstore` | 1.9G | 10-19 | content-addressed art store (sha256.png) | `art/artledger.py`, `art/game_art.py` |
| `_rmscratch` | **241G**, 850k files, 372 entries | 10-19 | save backups, DRIVER_LOCK/BRIDGE_SHARED json, Edge gate profiles (Edge running in it now), codex staging, build scratch | ~60 code references, skills, docs. Holds `saves_backup_*`, `ported_mutator_saves`, `decisions_backup_*`, so it was not pruned. Its many old subdirs (e.g. `silencetest/` build output) are the biggest remaining cleanup, and that needs its own pass, one subdir at a time |
| `_rmbuild` | 19G before the stage prune | 10-19 | winbuild.py staging (`WINBUILD_ROOT`) plus csproj HintPaths | can be rebuilt on demand; per-Mod stages and the live clones' selftest stages kept |
| `_obs` | 111M | 10-10 | bridge observatory run logs | `rimdrive/obs_events.py`, `rimdrive/session.py`, `modcheck/obs_summary.py` |
| `_rmdashboard` | 352K | 10-19 | RimPulse digests | `pulse/pulse.py` (`RM_PULSE_DIGESTS`), written at 06:00 today |

## Kept: the owner must decide (patch-level audit shows possibly-unique work)

| dir | size | newest | what it is | why kept |
|---|---|---|---|---|
| `_rm_old_git_2026-10` | 4.2G | 10-02 | the pre-migration shared-tree `.git` (133 branches, 4 stashes) | `design/RimMandrake/git_migration_freeze_2026-10-02.md`: "Keep … until the owner says delete". 14 refs (including `main`, `rescue/feverwood-92bd25209`, several worktree-agent branches, 3 stashes) hold commits whose patch-id is not on origin/main |
| `_rm_shared_tree_leftovers_2026-10` | 456K | 10-02 | `leftovers.manifest.tsv` only (its tar is already gone) | the same freeze ruling; it goes together with the old .git |

## Also removed outside D: (owner's list)

`~/rm/_foundry_dirty_backup_20261010{,b}`, `aside_20261007`, `ul_wip_backup`, `deploy_backup_20261016`,
`_quarantine`, and 14 loose Oct 5–10 files; `~/rm/scratch/BENCH` emptied (14G, 171 entries; its 6 git clones were
clean or held only rebuilt DLLs, and every commit was already on origin/main); `~/.seat-tmp/FOUNDRY/{hourly_*,tmp*,art-ledger-drift-*}`,
`BENCH/art-ledger-drift-*`, `cleanroot`, `yayo_dd`, `landtest`. Foundry branches deleted, with the tip each pointed at:
`backup/foundry-dhoggur-presync-93a444dc9` (4f6828445), `backup/foundry-pre-sync-20261011_132729-38f0431` (38f0431fe),
`backup/foundry-pre-sync-20261017_130030-c48c043` (c48c04321), `backup/foundry-pre-sync-20261017_133653-f5b3352` (f5b33524f),
`p3old` (48ee95acf). Their only patch-unique commits were rebuilt DLLs, plus the Dhoggur swell commit, which is on main as 3536bca79.
