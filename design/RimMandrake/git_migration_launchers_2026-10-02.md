# Launcher migration to ext4 seat clones — 2026-10-02

Repoints every launcher/profile/autostart that starts a RimMandrake Claude seat:
BENCH → `/home/mandrake/rm/bench`, FOUNDRY → `/home/mandrake/rm/foundry`.
Plan: `design/RimMandrake/git_workflow_plan_2026-10-01.md` §2.1, §5. No running window was
touched; every change takes effect on the next launch.

## Inventory (what launches a RimMandrake Claude on Archmagi)

| launcher | where | was | now |
|---|---|---|---|
| WT profile `AGENT BENCH` | `C:\Users\Mandrake\AppData\Local\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json` | cd + script in `/mnt/d/Luke/dev/RimMandrake` | `cd /home/mandrake/rm/bench && export AGENT_SEAT=BENCH && /home/mandrake/rm/bench/src/RimMandrake/Utils/claude_bounded.sh …` (flags unchanged) |
| WT profile `AGENT FOUNDRY` | same | same | same shape, `/home/mandrake/rm/foundry` |
| WT profile `Server` | same | cwd + script on D:\ | cwd and script in `/home/mandrake/rm/bench` |
| WT profiles `HESTIA`, `EMERGENCY` | same | D:\ tree's script | script `/home/mandrake/rm/bench/src/RimMandrake/Utils/claude_bounded.sh`; cwd unchanged |
| WT profile `Artist` (artpipe daemon) | same | D:\ tree | **unchanged on purpose** — its queue state is tracked in the D:\ tree until Phase 5 moves it out (plan §2.3); repoint it then |
| `Start Agent Fleet.lnk` (Desktop + Startup) | `C:\Users\Mandrake\OneDrive\Desktop\`, `…\Start Menu\Programs\Startup\` | `D:\Luke\dev\Rimworld\…\launch_fleet.ps1` (junction alias) | `D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\launch_fleet.ps1` (real folder; Windows-side script, opens WT profiles by name, so the mirror is its right home) |
| `rc rescue` / `rc server` (`~/.local/bin/rc`, `rescue`) | `D:\Luke\dev\claude-remote-control\scripts\rc` | `/mnt/d/Luke/dev/Rimworld` | `/home/mandrake/rm/bench` |
| Scheduled tasks | `schtasks` | only `\WSL Keepalive` (`sleep infinity`, no repo cwd) | nothing to change |
| systemd user units | `~/.config/systemd/user/` | `claude-seats.slice`, `hestia.service` (Hestia tree) — no RimMandrake cwd; `lodestar-sync.timer` runs from `/home/mandrake` | nothing to change |
| Lodestar sweep target | `D:\Luke\dev\Lodestar\sync\registry.md` | `~/dev/RimMandrake` (Send off, Receive on) | Machine-paths override `RimMandrake | home | ~/rm/bench` — otherwise the gitless mirror would read as absent and `clone_step` would try to clone into it |
| Waypoint | `D:\Luke\dev\Waypoint\waypoints.md` | Mac row only | `RIMMASTER` archmagi row → `/home/mandrake/rm/bench` |
| Claude trust/settings | `~/.claude.json` projects map | only `/mnt/d/Luke/dev/RimMandrake` | its trust/MCP/`remoteControlSpawnMode` fields copied to both clone paths |
| `.claude/settings.local.json` (untracked) | D:\ tree | only there | copied into both clones |

## Repo code changes

- `src/RimMandrake/Utils/install_wt_seat_profiles.py` — per-seat clone homes (`SEAT_CLONES`), each seat runs
  its own clone's `claude_bounded.sh`, non-seat Claude tiles run BENCH's; re-run `--apply` reproduces the
  live profiles exactly (0 field diffs measured after apply).
- `src/RimMandrake/Utils/claude_bounded.sh` — `SLICE_SRC` was already derived from its own location upstream (`f610d7eac`, was
  hardcoded `/mnt/d/Luke/dev/Rimworld/…`).
- `src/RimMandrake/Utils/set_agent_window.sh` — repo-root walk tests `-e .git` (a worktree slot's `.git` is
  a file); it already derived its root from its own location.
- `src/RimMandrake/Utils/install_fleet_shortcut.py` — points at the real `D:\Luke\dev\RimMandrake` folder.

## Backups

Every machine file edited has `<file>.bak-2026-10-02` beside it: the WT `settings.json`, both
`Start Agent Fleet.lnk`, `~/.claude.json`, Lodestar `sync/registry.md`, Waypoint `waypoints.md`, and the four
claude-remote-control files.

## Left for the owner / later phases

- Close and reopen the fleet when ready (no window was restarted). The first BENCH/FOUNDRY launch in the
  new paths is the real test; memory dirs are already symlinked.
- `Artist` tile still runs in the D:\ tree — repoint when Phase 5 moves the artpipe queue out of git.
- `.claude/hooks/block_shared_tree_merge.py` still path-matches the D:\ tree — plan §5 hook work, not a launcher.
