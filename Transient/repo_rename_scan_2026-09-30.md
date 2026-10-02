# Repo rename scan, 2026-09-30

Old repo name `Rimworld` (lowercase w) vs game name `RimWorld` (not a finding). Symlink `D:\Luke\dev\Rimworld -> D:\Luke\dev\RimMandrake` made 2026-09-30 22:39. Nothing was fixed by this scan.

Patterns: `dev[/\\]+Rimworld`, `Lmandrake/Rimworld`, `Rimworld-wt`, `Luke-dev-Rimworld`, `Rimworld[/\\]`. Case-sensitive. Instrument: `git ls-files` (19,407 tracked files outside `infrastructure/artpipe/` and `Transient/`, both excluded) piped to `grep -I -n -E`. Sanity probes: `git grep -c RimMandrake CLAUDE.md` = 24; `~/.claude/skills` holds 40 symlinks; schtasks listed 285 tasks and 3 `dev\` tasks matched the probe.

## Repo tracked files: 1,178 hits in 573 files

| class | hits | meaning |
|---|---|---|
| BREAKS | 764 (443 files) | path in code/config/data that fails without the link |
| MISLEADS | 265 | prose in docs/skills naming old path |
| BENIGN | 149 | ledger `events.jsonl`, `handoffs/`, `items/closed/` (history, never edit) |

BREAKS split:

| group | hits / files | note |
|---|---|---|
| `.claude/` | 3 / 2 | hook docstring and selftest string, not executed paths |
| live tooling (`src/`, `skills/`, `infrastructure/`, `deployed/`) | 237 / 186 | below |
| `world/_*` one-off scripts | 416 / 242 | write-once scripts; low value |
| `design/**` manifests/scripts | 108 / 13 | `design/Jawa/mods/plant_sprites/manifest.json` 66, `design/Jawa/fauna/sprites/manifest_A.json` 21 |

Live-tooling BREAKS, grouped:
- ~70 csproj files carry `"%USERPROFILE%\.dotnet\dotnet.exe" build D:\Luke\dev\Rimworld\src\...` (PostBuild/comment build lines), e.g. `src/RimMandrake/FlowWorks/Source/RimMandrake_FlowWorks.csproj:25`, `src/RimMandrake/Oracle/Source/Oracle.csproj:13`, plus 11 `SelfTest/*.csproj` `run --project` lines.
- `src/RimMandrake/Utils/install_wt_seat_profiles.py:83,84,123,133` and `install_fleet_shortcut.py:53,54` (Windows Terminal profile generators; would regenerate the OLD path).
- `src/RimMandrake/Utils/claude_bounded.sh:91` (SLICE_SRC), `build_salvation_rid.py:37`, `worldmap_prefill.py:49`, `reload_check.py:35,36`, `planet_portrait.py:9,10`, `loadsweep/biome_load_proof.sh:33`, `rimbench/gl_sheet_run.sh:9`, `selftest_deployed_biome_refs.py:60,61`.
- `src/RimMandrake/bridgetools/*.py` (about 20 files, `sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")`), `bridgetools/crash_watch.sh:13`, `bridgetools/build.py:102`.
- `skills/validate_skills.py:16` (SRC path).
- `infrastructure/dashboards/hub/data/publish_ready.json` 16 `source` paths (generated).
- `infrastructure/output/pawn_flavor_phase2_census_gen.py:12,15` (Claude scratch slug `-mnt-d-Luke-dev-Rimworld`).
- `deployed/atmosphere_ring/ring_debris_gen.py:95,182`; 7 files under `src/RimStarWars/Armoury/_artsrc/desert_wraps_candidates_2026-09-09/work/`.
- Many `Utils/*.py` carry `Project: D:/Luke/dev/Rimworld/...` in a version-header comment (about 25): MISLEADS-grade, counted as BREAKS by extension.
- Stale internal: `src/RimMandrake/WreckedMachines/Source/RM_WreckedMachines.csproj:13` points into a dead `.claude\worktrees\agent-afc100cb85cd7f019`.

## ~/.claude (global): 0 hits
`settings.json`, `settings.local.json`, `CLAUDE.md`, `hooks/`, `skills/` all clean (repointed earlier). `~/.claude/projects/` has `-mnt-d-Luke-dev-RimMandrake` and NO stale `-mnt-d-Luke-dev-Rimworld`. `-mnt-g-My-Drive-Personal-Rimworld` is an unrelated Drive project. 0 symlinks anywhere with `-lname '*Rimworld*'` (`~` depth 3, `~/.claude/skills`, `D:\Luke\dev` depth 2) except the rename link itself.
- `C:\Users\Mandrake\.claude\CLAUDE.md:14` `file:///D:/Luke/dev/Rimworld/Utils/rimbench/scatter.py`: MISLEADS (the Windows-side global file; already wrong before the rename, since `Utils/` is under `src/RimMandrake/`).

## Lodestar / systemd / cron
- `systemd`: `/etc/systemd/system/lodestar-sync.service` runs `/home/mandrake/dev/Lodestar/bin/sync.py`: 0 hits. `~/.config/systemd/user` (hestia only): 0. `crontab -l`: none. The sweep itself does not need the link.
- BREAKS (Lodestar state):
  - `D:\Luke\dev\.lodestar\managed.json:33` `"rimmaster": "/home/mandrake/dev/Rimworld"` (the live path table; the registry row says `~/dev/RimMandrake`, so this file is stale or the sweep still resolves through the link).
  - `.lodestar/sync-status.json:354` same path (derived output; regenerates).
  - `Lodestar/loops/rimworld-twilight-floor.md:7` `repo: /mnt/d/Luke/dev/Rimworld`.
  - `Lodestar/journal/2026-09-30/rimworld-bench-bedazzle-handoff.md:6` and `journal/2026-10-01/...:6` `repo: /mnt/d/Luke/dev/Rimworld` (handoff wake reads this).
- MISLEADS/BENIGN (about 55 hits): `Lodestar/CLAUDE.md:223`, `bin/lifecycle.py:82`, `bin/lib/registry.py:24`, `bin/lib/skillclone.py:32`, `bin/lib/validate.py:64` (comments/docstrings naming the `home` override), `docs/SYNC_AGENT.md:187`, `loops/repo-lifecycle.md` (history), `sync/registry.md:63` (old names deliberately listed as aliases `RimMaster, Rimworld`), and `claude/snapshot|adopt|merge/` mirrored copies of CLAUDE.md and memory including a snapshot dir `claude/snapshot/archmagi/memory/-mnt-d-Luke-dev-Rimworld/` (mirror of a project dir that no longer exists).

## Windows scheduled tasks: 0 hits
285 tasks scanned; the three with `dev\` paths (`Custos SpaLogger`, `OllamaServe`, `WSL Keepalive` -> `D:\Luke\dev\claude-remote-control\scripts\wsl_keepalive.vbs`) do not mention Rimworld. The artpipe daemon is a WSL process started from in-repo scripts (any old path inside it falls under the repo hits above).

## Worktrees
- `git worktree list`: 0 entries with `Rimworld` (59 agent worktrees were repaired at rename time).
- `D:\Luke\dev\Rimworld-wt-sightblock`: an orphan directory containing only an `infrastructure/` folder, no `.git`, not a registered worktree. Delete candidate.
- `D:\Luke\dev\Rimworld_history.bundle` (260 MB): filename only, BENIGN.

## RimMaster
Not a typo and not an unrelated third repo: it is the repo's intermediate name.
- The GitHub repo was `Lmandrake/RimMaster` (`sync/registry.md:63` old-names column: `RimMaster, Rimworld, git@github.com:Lmandrake/RimMaster.git`), the Mac checkouts were `~/dev/RimMaster`, and this machine's checkout was `~/dev/Rimworld`. Lodestar's repo id is still `rimmaster` (`.git/config:25 id = rimmaster`) and the id deliberately stays.
- Chain: `Rimworld` (archmagi dir) / `RimMaster` (Mac dir + GitHub) -> `RimMandrake` (all, 2026-09-30, plans `rename-rimmaster-archmagi-20260930` and `rename-rimmaster-macs-20260930`; Macs unverified).
- Tracked residue: 32 hits in about 25 files, mostly history (handoffs, closed items, `design/NAMING_SCHEME_PLAN.md`). Live ones: `.bridge.eld:13` `:station RIMMASTER`, `.gitignore:1` comment, `.claude/hooks/selftest_block_forged_validation.py:47` `/Users/x/dev/RimMaster/` (test string, harmless). The Mac side may still resolve `~/dev/RimMaster`.
